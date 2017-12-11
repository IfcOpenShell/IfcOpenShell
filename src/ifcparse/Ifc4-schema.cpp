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

#ifdef USE_IFC4

#include "../ifcparse/IfcSchema.h"

using namespace IfcParse;
entity* IfcActionRequest_type = 0;
entity* IfcActor_type = 0;
entity* IfcActorRole_type = 0;
entity* IfcActuator_type = 0;
entity* IfcActuatorType_type = 0;
entity* IfcAddress_type = 0;
entity* IfcAdvancedBrep_type = 0;
entity* IfcAdvancedBrepWithVoids_type = 0;
entity* IfcAdvancedFace_type = 0;
entity* IfcAirTerminal_type = 0;
entity* IfcAirTerminalBox_type = 0;
entity* IfcAirTerminalBoxType_type = 0;
entity* IfcAirTerminalType_type = 0;
entity* IfcAirToAirHeatRecovery_type = 0;
entity* IfcAirToAirHeatRecoveryType_type = 0;
entity* IfcAlarm_type = 0;
entity* IfcAlarmType_type = 0;
entity* IfcAnnotation_type = 0;
entity* IfcAnnotationFillArea_type = 0;
entity* IfcApplication_type = 0;
entity* IfcAppliedValue_type = 0;
entity* IfcApproval_type = 0;
entity* IfcApprovalRelationship_type = 0;
entity* IfcArbitraryClosedProfileDef_type = 0;
entity* IfcArbitraryOpenProfileDef_type = 0;
entity* IfcArbitraryProfileDefWithVoids_type = 0;
entity* IfcAsset_type = 0;
entity* IfcAsymmetricIShapeProfileDef_type = 0;
entity* IfcAudioVisualAppliance_type = 0;
entity* IfcAudioVisualApplianceType_type = 0;
entity* IfcAxis1Placement_type = 0;
entity* IfcAxis2Placement2D_type = 0;
entity* IfcAxis2Placement3D_type = 0;
entity* IfcBSplineCurve_type = 0;
entity* IfcBSplineCurveWithKnots_type = 0;
entity* IfcBSplineSurface_type = 0;
entity* IfcBSplineSurfaceWithKnots_type = 0;
entity* IfcBeam_type = 0;
entity* IfcBeamStandardCase_type = 0;
entity* IfcBeamType_type = 0;
entity* IfcBlobTexture_type = 0;
entity* IfcBlock_type = 0;
entity* IfcBoiler_type = 0;
entity* IfcBoilerType_type = 0;
entity* IfcBooleanClippingResult_type = 0;
entity* IfcBooleanResult_type = 0;
entity* IfcBoundaryCondition_type = 0;
entity* IfcBoundaryCurve_type = 0;
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
entity* IfcBuildingElementPart_type = 0;
entity* IfcBuildingElementPartType_type = 0;
entity* IfcBuildingElementProxy_type = 0;
entity* IfcBuildingElementProxyType_type = 0;
entity* IfcBuildingElementType_type = 0;
entity* IfcBuildingStorey_type = 0;
entity* IfcBuildingSystem_type = 0;
entity* IfcBurner_type = 0;
entity* IfcBurnerType_type = 0;
entity* IfcCShapeProfileDef_type = 0;
entity* IfcCableCarrierFitting_type = 0;
entity* IfcCableCarrierFittingType_type = 0;
entity* IfcCableCarrierSegment_type = 0;
entity* IfcCableCarrierSegmentType_type = 0;
entity* IfcCableFitting_type = 0;
entity* IfcCableFittingType_type = 0;
entity* IfcCableSegment_type = 0;
entity* IfcCableSegmentType_type = 0;
entity* IfcCartesianPoint_type = 0;
entity* IfcCartesianPointList_type = 0;
entity* IfcCartesianPointList2D_type = 0;
entity* IfcCartesianPointList3D_type = 0;
entity* IfcCartesianTransformationOperator_type = 0;
entity* IfcCartesianTransformationOperator2D_type = 0;
entity* IfcCartesianTransformationOperator2DnonUniform_type = 0;
entity* IfcCartesianTransformationOperator3D_type = 0;
entity* IfcCartesianTransformationOperator3DnonUniform_type = 0;
entity* IfcCenterLineProfileDef_type = 0;
entity* IfcChiller_type = 0;
entity* IfcChillerType_type = 0;
entity* IfcChimney_type = 0;
entity* IfcChimneyType_type = 0;
entity* IfcCircle_type = 0;
entity* IfcCircleHollowProfileDef_type = 0;
entity* IfcCircleProfileDef_type = 0;
entity* IfcCivilElement_type = 0;
entity* IfcCivilElementType_type = 0;
entity* IfcClassification_type = 0;
entity* IfcClassificationReference_type = 0;
entity* IfcClosedShell_type = 0;
entity* IfcCoil_type = 0;
entity* IfcCoilType_type = 0;
entity* IfcColourRgb_type = 0;
entity* IfcColourRgbList_type = 0;
entity* IfcColourSpecification_type = 0;
entity* IfcColumn_type = 0;
entity* IfcColumnStandardCase_type = 0;
entity* IfcColumnType_type = 0;
entity* IfcCommunicationsAppliance_type = 0;
entity* IfcCommunicationsApplianceType_type = 0;
entity* IfcComplexProperty_type = 0;
entity* IfcComplexPropertyTemplate_type = 0;
entity* IfcCompositeCurve_type = 0;
entity* IfcCompositeCurveOnSurface_type = 0;
entity* IfcCompositeCurveSegment_type = 0;
entity* IfcCompositeProfileDef_type = 0;
entity* IfcCompressor_type = 0;
entity* IfcCompressorType_type = 0;
entity* IfcCondenser_type = 0;
entity* IfcCondenserType_type = 0;
entity* IfcConic_type = 0;
entity* IfcConnectedFaceSet_type = 0;
entity* IfcConnectionCurveGeometry_type = 0;
entity* IfcConnectionGeometry_type = 0;
entity* IfcConnectionPointEccentricity_type = 0;
entity* IfcConnectionPointGeometry_type = 0;
entity* IfcConnectionSurfaceGeometry_type = 0;
entity* IfcConnectionVolumeGeometry_type = 0;
entity* IfcConstraint_type = 0;
entity* IfcConstructionEquipmentResource_type = 0;
entity* IfcConstructionEquipmentResourceType_type = 0;
entity* IfcConstructionMaterialResource_type = 0;
entity* IfcConstructionMaterialResourceType_type = 0;
entity* IfcConstructionProductResource_type = 0;
entity* IfcConstructionProductResourceType_type = 0;
entity* IfcConstructionResource_type = 0;
entity* IfcConstructionResourceType_type = 0;
entity* IfcContext_type = 0;
entity* IfcContextDependentUnit_type = 0;
entity* IfcControl_type = 0;
entity* IfcController_type = 0;
entity* IfcControllerType_type = 0;
entity* IfcConversionBasedUnit_type = 0;
entity* IfcConversionBasedUnitWithOffset_type = 0;
entity* IfcCooledBeam_type = 0;
entity* IfcCooledBeamType_type = 0;
entity* IfcCoolingTower_type = 0;
entity* IfcCoolingTowerType_type = 0;
entity* IfcCoordinateOperation_type = 0;
entity* IfcCoordinateReferenceSystem_type = 0;
entity* IfcCostItem_type = 0;
entity* IfcCostSchedule_type = 0;
entity* IfcCostValue_type = 0;
entity* IfcCovering_type = 0;
entity* IfcCoveringType_type = 0;
entity* IfcCrewResource_type = 0;
entity* IfcCrewResourceType_type = 0;
entity* IfcCsgPrimitive3D_type = 0;
entity* IfcCsgSolid_type = 0;
entity* IfcCurrencyRelationship_type = 0;
entity* IfcCurtainWall_type = 0;
entity* IfcCurtainWallType_type = 0;
entity* IfcCurve_type = 0;
entity* IfcCurveBoundedPlane_type = 0;
entity* IfcCurveBoundedSurface_type = 0;
entity* IfcCurveStyle_type = 0;
entity* IfcCurveStyleFont_type = 0;
entity* IfcCurveStyleFontAndScaling_type = 0;
entity* IfcCurveStyleFontPattern_type = 0;
entity* IfcCylindricalSurface_type = 0;
entity* IfcDamper_type = 0;
entity* IfcDamperType_type = 0;
entity* IfcDerivedProfileDef_type = 0;
entity* IfcDerivedUnit_type = 0;
entity* IfcDerivedUnitElement_type = 0;
entity* IfcDimensionalExponents_type = 0;
entity* IfcDirection_type = 0;
entity* IfcDiscreteAccessory_type = 0;
entity* IfcDiscreteAccessoryType_type = 0;
entity* IfcDistributionChamberElement_type = 0;
entity* IfcDistributionChamberElementType_type = 0;
entity* IfcDistributionCircuit_type = 0;
entity* IfcDistributionControlElement_type = 0;
entity* IfcDistributionControlElementType_type = 0;
entity* IfcDistributionElement_type = 0;
entity* IfcDistributionElementType_type = 0;
entity* IfcDistributionFlowElement_type = 0;
entity* IfcDistributionFlowElementType_type = 0;
entity* IfcDistributionPort_type = 0;
entity* IfcDistributionSystem_type = 0;
entity* IfcDocumentInformation_type = 0;
entity* IfcDocumentInformationRelationship_type = 0;
entity* IfcDocumentReference_type = 0;
entity* IfcDoor_type = 0;
entity* IfcDoorLiningProperties_type = 0;
entity* IfcDoorPanelProperties_type = 0;
entity* IfcDoorStandardCase_type = 0;
entity* IfcDoorStyle_type = 0;
entity* IfcDoorType_type = 0;
entity* IfcDraughtingPreDefinedColour_type = 0;
entity* IfcDraughtingPreDefinedCurveFont_type = 0;
entity* IfcDuctFitting_type = 0;
entity* IfcDuctFittingType_type = 0;
entity* IfcDuctSegment_type = 0;
entity* IfcDuctSegmentType_type = 0;
entity* IfcDuctSilencer_type = 0;
entity* IfcDuctSilencerType_type = 0;
entity* IfcEdge_type = 0;
entity* IfcEdgeCurve_type = 0;
entity* IfcEdgeLoop_type = 0;
entity* IfcElectricAppliance_type = 0;
entity* IfcElectricApplianceType_type = 0;
entity* IfcElectricDistributionBoard_type = 0;
entity* IfcElectricDistributionBoardType_type = 0;
entity* IfcElectricFlowStorageDevice_type = 0;
entity* IfcElectricFlowStorageDeviceType_type = 0;
entity* IfcElectricGenerator_type = 0;
entity* IfcElectricGeneratorType_type = 0;
entity* IfcElectricMotor_type = 0;
entity* IfcElectricMotorType_type = 0;
entity* IfcElectricTimeControl_type = 0;
entity* IfcElectricTimeControlType_type = 0;
entity* IfcElement_type = 0;
entity* IfcElementAssembly_type = 0;
entity* IfcElementAssemblyType_type = 0;
entity* IfcElementComponent_type = 0;
entity* IfcElementComponentType_type = 0;
entity* IfcElementQuantity_type = 0;
entity* IfcElementType_type = 0;
entity* IfcElementarySurface_type = 0;
entity* IfcEllipse_type = 0;
entity* IfcEllipseProfileDef_type = 0;
entity* IfcEnergyConversionDevice_type = 0;
entity* IfcEnergyConversionDeviceType_type = 0;
entity* IfcEngine_type = 0;
entity* IfcEngineType_type = 0;
entity* IfcEvaporativeCooler_type = 0;
entity* IfcEvaporativeCoolerType_type = 0;
entity* IfcEvaporator_type = 0;
entity* IfcEvaporatorType_type = 0;
entity* IfcEvent_type = 0;
entity* IfcEventTime_type = 0;
entity* IfcEventType_type = 0;
entity* IfcExtendedProperties_type = 0;
entity* IfcExternalInformation_type = 0;
entity* IfcExternalReference_type = 0;
entity* IfcExternalReferenceRelationship_type = 0;
entity* IfcExternalSpatialElement_type = 0;
entity* IfcExternalSpatialStructureElement_type = 0;
entity* IfcExternallyDefinedHatchStyle_type = 0;
entity* IfcExternallyDefinedSurfaceStyle_type = 0;
entity* IfcExternallyDefinedTextFont_type = 0;
entity* IfcExtrudedAreaSolid_type = 0;
entity* IfcExtrudedAreaSolidTapered_type = 0;
entity* IfcFace_type = 0;
entity* IfcFaceBasedSurfaceModel_type = 0;
entity* IfcFaceBound_type = 0;
entity* IfcFaceOuterBound_type = 0;
entity* IfcFaceSurface_type = 0;
entity* IfcFacetedBrep_type = 0;
entity* IfcFacetedBrepWithVoids_type = 0;
entity* IfcFailureConnectionCondition_type = 0;
entity* IfcFan_type = 0;
entity* IfcFanType_type = 0;
entity* IfcFastener_type = 0;
entity* IfcFastenerType_type = 0;
entity* IfcFeatureElement_type = 0;
entity* IfcFeatureElementAddition_type = 0;
entity* IfcFeatureElementSubtraction_type = 0;
entity* IfcFillAreaStyle_type = 0;
entity* IfcFillAreaStyleHatching_type = 0;
entity* IfcFillAreaStyleTiles_type = 0;
entity* IfcFilter_type = 0;
entity* IfcFilterType_type = 0;
entity* IfcFireSuppressionTerminal_type = 0;
entity* IfcFireSuppressionTerminalType_type = 0;
entity* IfcFixedReferenceSweptAreaSolid_type = 0;
entity* IfcFlowController_type = 0;
entity* IfcFlowControllerType_type = 0;
entity* IfcFlowFitting_type = 0;
entity* IfcFlowFittingType_type = 0;
entity* IfcFlowInstrument_type = 0;
entity* IfcFlowInstrumentType_type = 0;
entity* IfcFlowMeter_type = 0;
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
entity* IfcFooting_type = 0;
entity* IfcFootingType_type = 0;
entity* IfcFurnishingElement_type = 0;
entity* IfcFurnishingElementType_type = 0;
entity* IfcFurniture_type = 0;
entity* IfcFurnitureType_type = 0;
entity* IfcGeographicElement_type = 0;
entity* IfcGeographicElementType_type = 0;
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
entity* IfcHeatExchanger_type = 0;
entity* IfcHeatExchangerType_type = 0;
entity* IfcHumidifier_type = 0;
entity* IfcHumidifierType_type = 0;
entity* IfcIShapeProfileDef_type = 0;
entity* IfcImageTexture_type = 0;
entity* IfcIndexedColourMap_type = 0;
entity* IfcIndexedPolyCurve_type = 0;
entity* IfcIndexedTextureMap_type = 0;
entity* IfcIndexedTriangleTextureMap_type = 0;
entity* IfcInterceptor_type = 0;
entity* IfcInterceptorType_type = 0;
entity* IfcInventory_type = 0;
entity* IfcIrregularTimeSeries_type = 0;
entity* IfcIrregularTimeSeriesValue_type = 0;
entity* IfcJunctionBox_type = 0;
entity* IfcJunctionBoxType_type = 0;
entity* IfcLShapeProfileDef_type = 0;
entity* IfcLaborResource_type = 0;
entity* IfcLaborResourceType_type = 0;
entity* IfcLagTime_type = 0;
entity* IfcLamp_type = 0;
entity* IfcLampType_type = 0;
entity* IfcLibraryInformation_type = 0;
entity* IfcLibraryReference_type = 0;
entity* IfcLightDistributionData_type = 0;
entity* IfcLightFixture_type = 0;
entity* IfcLightFixtureType_type = 0;
entity* IfcLightIntensityDistribution_type = 0;
entity* IfcLightSource_type = 0;
entity* IfcLightSourceAmbient_type = 0;
entity* IfcLightSourceDirectional_type = 0;
entity* IfcLightSourceGoniometric_type = 0;
entity* IfcLightSourcePositional_type = 0;
entity* IfcLightSourceSpot_type = 0;
entity* IfcLine_type = 0;
entity* IfcLocalPlacement_type = 0;
entity* IfcLoop_type = 0;
entity* IfcManifoldSolidBrep_type = 0;
entity* IfcMapConversion_type = 0;
entity* IfcMappedItem_type = 0;
entity* IfcMaterial_type = 0;
entity* IfcMaterialClassificationRelationship_type = 0;
entity* IfcMaterialConstituent_type = 0;
entity* IfcMaterialConstituentSet_type = 0;
entity* IfcMaterialDefinition_type = 0;
entity* IfcMaterialDefinitionRepresentation_type = 0;
entity* IfcMaterialLayer_type = 0;
entity* IfcMaterialLayerSet_type = 0;
entity* IfcMaterialLayerSetUsage_type = 0;
entity* IfcMaterialLayerWithOffsets_type = 0;
entity* IfcMaterialList_type = 0;
entity* IfcMaterialProfile_type = 0;
entity* IfcMaterialProfileSet_type = 0;
entity* IfcMaterialProfileSetUsage_type = 0;
entity* IfcMaterialProfileSetUsageTapering_type = 0;
entity* IfcMaterialProfileWithOffsets_type = 0;
entity* IfcMaterialProperties_type = 0;
entity* IfcMaterialRelationship_type = 0;
entity* IfcMaterialUsageDefinition_type = 0;
entity* IfcMeasureWithUnit_type = 0;
entity* IfcMechanicalFastener_type = 0;
entity* IfcMechanicalFastenerType_type = 0;
entity* IfcMedicalDevice_type = 0;
entity* IfcMedicalDeviceType_type = 0;
entity* IfcMember_type = 0;
entity* IfcMemberStandardCase_type = 0;
entity* IfcMemberType_type = 0;
entity* IfcMetric_type = 0;
entity* IfcMirroredProfileDef_type = 0;
entity* IfcMonetaryUnit_type = 0;
entity* IfcMotorConnection_type = 0;
entity* IfcMotorConnectionType_type = 0;
entity* IfcNamedUnit_type = 0;
entity* IfcObject_type = 0;
entity* IfcObjectDefinition_type = 0;
entity* IfcObjectPlacement_type = 0;
entity* IfcObjective_type = 0;
entity* IfcOccupant_type = 0;
entity* IfcOffsetCurve2D_type = 0;
entity* IfcOffsetCurve3D_type = 0;
entity* IfcOpenShell_type = 0;
entity* IfcOpeningElement_type = 0;
entity* IfcOpeningStandardCase_type = 0;
entity* IfcOrganization_type = 0;
entity* IfcOrganizationRelationship_type = 0;
entity* IfcOrientedEdge_type = 0;
entity* IfcOuterBoundaryCurve_type = 0;
entity* IfcOutlet_type = 0;
entity* IfcOutletType_type = 0;
entity* IfcOwnerHistory_type = 0;
entity* IfcParameterizedProfileDef_type = 0;
entity* IfcPath_type = 0;
entity* IfcPcurve_type = 0;
entity* IfcPerformanceHistory_type = 0;
entity* IfcPermeableCoveringProperties_type = 0;
entity* IfcPermit_type = 0;
entity* IfcPerson_type = 0;
entity* IfcPersonAndOrganization_type = 0;
entity* IfcPhysicalComplexQuantity_type = 0;
entity* IfcPhysicalQuantity_type = 0;
entity* IfcPhysicalSimpleQuantity_type = 0;
entity* IfcPile_type = 0;
entity* IfcPileType_type = 0;
entity* IfcPipeFitting_type = 0;
entity* IfcPipeFittingType_type = 0;
entity* IfcPipeSegment_type = 0;
entity* IfcPipeSegmentType_type = 0;
entity* IfcPixelTexture_type = 0;
entity* IfcPlacement_type = 0;
entity* IfcPlanarBox_type = 0;
entity* IfcPlanarExtent_type = 0;
entity* IfcPlane_type = 0;
entity* IfcPlate_type = 0;
entity* IfcPlateStandardCase_type = 0;
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
entity* IfcPreDefinedItem_type = 0;
entity* IfcPreDefinedProperties_type = 0;
entity* IfcPreDefinedPropertySet_type = 0;
entity* IfcPreDefinedTextFont_type = 0;
entity* IfcPresentationItem_type = 0;
entity* IfcPresentationLayerAssignment_type = 0;
entity* IfcPresentationLayerWithStyle_type = 0;
entity* IfcPresentationStyle_type = 0;
entity* IfcPresentationStyleAssignment_type = 0;
entity* IfcProcedure_type = 0;
entity* IfcProcedureType_type = 0;
entity* IfcProcess_type = 0;
entity* IfcProduct_type = 0;
entity* IfcProductDefinitionShape_type = 0;
entity* IfcProductRepresentation_type = 0;
entity* IfcProfileDef_type = 0;
entity* IfcProfileProperties_type = 0;
entity* IfcProject_type = 0;
entity* IfcProjectLibrary_type = 0;
entity* IfcProjectOrder_type = 0;
entity* IfcProjectedCRS_type = 0;
entity* IfcProjectionElement_type = 0;
entity* IfcProperty_type = 0;
entity* IfcPropertyAbstraction_type = 0;
entity* IfcPropertyBoundedValue_type = 0;
entity* IfcPropertyDefinition_type = 0;
entity* IfcPropertyDependencyRelationship_type = 0;
entity* IfcPropertyEnumeratedValue_type = 0;
entity* IfcPropertyEnumeration_type = 0;
entity* IfcPropertyListValue_type = 0;
entity* IfcPropertyReferenceValue_type = 0;
entity* IfcPropertySet_type = 0;
entity* IfcPropertySetDefinition_type = 0;
entity* IfcPropertySetTemplate_type = 0;
entity* IfcPropertySingleValue_type = 0;
entity* IfcPropertyTableValue_type = 0;
entity* IfcPropertyTemplate_type = 0;
entity* IfcPropertyTemplateDefinition_type = 0;
entity* IfcProtectiveDevice_type = 0;
entity* IfcProtectiveDeviceTrippingUnit_type = 0;
entity* IfcProtectiveDeviceTrippingUnitType_type = 0;
entity* IfcProtectiveDeviceType_type = 0;
entity* IfcProxy_type = 0;
entity* IfcPump_type = 0;
entity* IfcPumpType_type = 0;
entity* IfcQuantityArea_type = 0;
entity* IfcQuantityCount_type = 0;
entity* IfcQuantityLength_type = 0;
entity* IfcQuantitySet_type = 0;
entity* IfcQuantityTime_type = 0;
entity* IfcQuantityVolume_type = 0;
entity* IfcQuantityWeight_type = 0;
entity* IfcRailing_type = 0;
entity* IfcRailingType_type = 0;
entity* IfcRamp_type = 0;
entity* IfcRampFlight_type = 0;
entity* IfcRampFlightType_type = 0;
entity* IfcRampType_type = 0;
entity* IfcRationalBSplineCurveWithKnots_type = 0;
entity* IfcRationalBSplineSurfaceWithKnots_type = 0;
entity* IfcRectangleHollowProfileDef_type = 0;
entity* IfcRectangleProfileDef_type = 0;
entity* IfcRectangularPyramid_type = 0;
entity* IfcRectangularTrimmedSurface_type = 0;
entity* IfcRecurrencePattern_type = 0;
entity* IfcReference_type = 0;
entity* IfcRegularTimeSeries_type = 0;
entity* IfcReinforcementBarProperties_type = 0;
entity* IfcReinforcementDefinitionProperties_type = 0;
entity* IfcReinforcingBar_type = 0;
entity* IfcReinforcingBarType_type = 0;
entity* IfcReinforcingElement_type = 0;
entity* IfcReinforcingElementType_type = 0;
entity* IfcReinforcingMesh_type = 0;
entity* IfcReinforcingMeshType_type = 0;
entity* IfcRelAggregates_type = 0;
entity* IfcRelAssigns_type = 0;
entity* IfcRelAssignsToActor_type = 0;
entity* IfcRelAssignsToControl_type = 0;
entity* IfcRelAssignsToGroup_type = 0;
entity* IfcRelAssignsToGroupByFactor_type = 0;
entity* IfcRelAssignsToProcess_type = 0;
entity* IfcRelAssignsToProduct_type = 0;
entity* IfcRelAssignsToResource_type = 0;
entity* IfcRelAssociates_type = 0;
entity* IfcRelAssociatesApproval_type = 0;
entity* IfcRelAssociatesClassification_type = 0;
entity* IfcRelAssociatesConstraint_type = 0;
entity* IfcRelAssociatesDocument_type = 0;
entity* IfcRelAssociatesLibrary_type = 0;
entity* IfcRelAssociatesMaterial_type = 0;
entity* IfcRelConnects_type = 0;
entity* IfcRelConnectsElements_type = 0;
entity* IfcRelConnectsPathElements_type = 0;
entity* IfcRelConnectsPortToElement_type = 0;
entity* IfcRelConnectsPorts_type = 0;
entity* IfcRelConnectsStructuralActivity_type = 0;
entity* IfcRelConnectsStructuralMember_type = 0;
entity* IfcRelConnectsWithEccentricity_type = 0;
entity* IfcRelConnectsWithRealizingElements_type = 0;
entity* IfcRelContainedInSpatialStructure_type = 0;
entity* IfcRelCoversBldgElements_type = 0;
entity* IfcRelCoversSpaces_type = 0;
entity* IfcRelDeclares_type = 0;
entity* IfcRelDecomposes_type = 0;
entity* IfcRelDefines_type = 0;
entity* IfcRelDefinesByObject_type = 0;
entity* IfcRelDefinesByProperties_type = 0;
entity* IfcRelDefinesByTemplate_type = 0;
entity* IfcRelDefinesByType_type = 0;
entity* IfcRelFillsElement_type = 0;
entity* IfcRelFlowControlElements_type = 0;
entity* IfcRelInterferesElements_type = 0;
entity* IfcRelNests_type = 0;
entity* IfcRelProjectsElement_type = 0;
entity* IfcRelReferencedInSpatialStructure_type = 0;
entity* IfcRelSequence_type = 0;
entity* IfcRelServicesBuildings_type = 0;
entity* IfcRelSpaceBoundary_type = 0;
entity* IfcRelSpaceBoundary1stLevel_type = 0;
entity* IfcRelSpaceBoundary2ndLevel_type = 0;
entity* IfcRelVoidsElement_type = 0;
entity* IfcRelationship_type = 0;
entity* IfcReparametrisedCompositeCurveSegment_type = 0;
entity* IfcRepresentation_type = 0;
entity* IfcRepresentationContext_type = 0;
entity* IfcRepresentationItem_type = 0;
entity* IfcRepresentationMap_type = 0;
entity* IfcResource_type = 0;
entity* IfcResourceApprovalRelationship_type = 0;
entity* IfcResourceConstraintRelationship_type = 0;
entity* IfcResourceLevelRelationship_type = 0;
entity* IfcResourceTime_type = 0;
entity* IfcRevolvedAreaSolid_type = 0;
entity* IfcRevolvedAreaSolidTapered_type = 0;
entity* IfcRightCircularCone_type = 0;
entity* IfcRightCircularCylinder_type = 0;
entity* IfcRoof_type = 0;
entity* IfcRoofType_type = 0;
entity* IfcRoot_type = 0;
entity* IfcRoundedRectangleProfileDef_type = 0;
entity* IfcSIUnit_type = 0;
entity* IfcSanitaryTerminal_type = 0;
entity* IfcSanitaryTerminalType_type = 0;
entity* IfcSchedulingTime_type = 0;
entity* IfcSectionProperties_type = 0;
entity* IfcSectionReinforcementProperties_type = 0;
entity* IfcSectionedSpine_type = 0;
entity* IfcSensor_type = 0;
entity* IfcSensorType_type = 0;
entity* IfcShadingDevice_type = 0;
entity* IfcShadingDeviceType_type = 0;
entity* IfcShapeAspect_type = 0;
entity* IfcShapeModel_type = 0;
entity* IfcShapeRepresentation_type = 0;
entity* IfcShellBasedSurfaceModel_type = 0;
entity* IfcSimpleProperty_type = 0;
entity* IfcSimplePropertyTemplate_type = 0;
entity* IfcSite_type = 0;
entity* IfcSlab_type = 0;
entity* IfcSlabElementedCase_type = 0;
entity* IfcSlabStandardCase_type = 0;
entity* IfcSlabType_type = 0;
entity* IfcSlippageConnectionCondition_type = 0;
entity* IfcSolarDevice_type = 0;
entity* IfcSolarDeviceType_type = 0;
entity* IfcSolidModel_type = 0;
entity* IfcSpace_type = 0;
entity* IfcSpaceHeater_type = 0;
entity* IfcSpaceHeaterType_type = 0;
entity* IfcSpaceType_type = 0;
entity* IfcSpatialElement_type = 0;
entity* IfcSpatialElementType_type = 0;
entity* IfcSpatialStructureElement_type = 0;
entity* IfcSpatialStructureElementType_type = 0;
entity* IfcSpatialZone_type = 0;
entity* IfcSpatialZoneType_type = 0;
entity* IfcSphere_type = 0;
entity* IfcStackTerminal_type = 0;
entity* IfcStackTerminalType_type = 0;
entity* IfcStair_type = 0;
entity* IfcStairFlight_type = 0;
entity* IfcStairFlightType_type = 0;
entity* IfcStairType_type = 0;
entity* IfcStructuralAction_type = 0;
entity* IfcStructuralActivity_type = 0;
entity* IfcStructuralAnalysisModel_type = 0;
entity* IfcStructuralConnection_type = 0;
entity* IfcStructuralConnectionCondition_type = 0;
entity* IfcStructuralCurveAction_type = 0;
entity* IfcStructuralCurveConnection_type = 0;
entity* IfcStructuralCurveMember_type = 0;
entity* IfcStructuralCurveMemberVarying_type = 0;
entity* IfcStructuralCurveReaction_type = 0;
entity* IfcStructuralItem_type = 0;
entity* IfcStructuralLinearAction_type = 0;
entity* IfcStructuralLoad_type = 0;
entity* IfcStructuralLoadCase_type = 0;
entity* IfcStructuralLoadConfiguration_type = 0;
entity* IfcStructuralLoadGroup_type = 0;
entity* IfcStructuralLoadLinearForce_type = 0;
entity* IfcStructuralLoadOrResult_type = 0;
entity* IfcStructuralLoadPlanarForce_type = 0;
entity* IfcStructuralLoadSingleDisplacement_type = 0;
entity* IfcStructuralLoadSingleDisplacementDistortion_type = 0;
entity* IfcStructuralLoadSingleForce_type = 0;
entity* IfcStructuralLoadSingleForceWarping_type = 0;
entity* IfcStructuralLoadStatic_type = 0;
entity* IfcStructuralLoadTemperature_type = 0;
entity* IfcStructuralMember_type = 0;
entity* IfcStructuralPlanarAction_type = 0;
entity* IfcStructuralPointAction_type = 0;
entity* IfcStructuralPointConnection_type = 0;
entity* IfcStructuralPointReaction_type = 0;
entity* IfcStructuralReaction_type = 0;
entity* IfcStructuralResultGroup_type = 0;
entity* IfcStructuralSurfaceAction_type = 0;
entity* IfcStructuralSurfaceConnection_type = 0;
entity* IfcStructuralSurfaceMember_type = 0;
entity* IfcStructuralSurfaceMemberVarying_type = 0;
entity* IfcStructuralSurfaceReaction_type = 0;
entity* IfcStyleModel_type = 0;
entity* IfcStyledItem_type = 0;
entity* IfcStyledRepresentation_type = 0;
entity* IfcSubContractResource_type = 0;
entity* IfcSubContractResourceType_type = 0;
entity* IfcSubedge_type = 0;
entity* IfcSurface_type = 0;
entity* IfcSurfaceCurveSweptAreaSolid_type = 0;
entity* IfcSurfaceFeature_type = 0;
entity* IfcSurfaceOfLinearExtrusion_type = 0;
entity* IfcSurfaceOfRevolution_type = 0;
entity* IfcSurfaceReinforcementArea_type = 0;
entity* IfcSurfaceStyle_type = 0;
entity* IfcSurfaceStyleLighting_type = 0;
entity* IfcSurfaceStyleRefraction_type = 0;
entity* IfcSurfaceStyleRendering_type = 0;
entity* IfcSurfaceStyleShading_type = 0;
entity* IfcSurfaceStyleWithTextures_type = 0;
entity* IfcSurfaceTexture_type = 0;
entity* IfcSweptAreaSolid_type = 0;
entity* IfcSweptDiskSolid_type = 0;
entity* IfcSweptDiskSolidPolygonal_type = 0;
entity* IfcSweptSurface_type = 0;
entity* IfcSwitchingDevice_type = 0;
entity* IfcSwitchingDeviceType_type = 0;
entity* IfcSystem_type = 0;
entity* IfcSystemFurnitureElement_type = 0;
entity* IfcSystemFurnitureElementType_type = 0;
entity* IfcTShapeProfileDef_type = 0;
entity* IfcTable_type = 0;
entity* IfcTableColumn_type = 0;
entity* IfcTableRow_type = 0;
entity* IfcTank_type = 0;
entity* IfcTankType_type = 0;
entity* IfcTask_type = 0;
entity* IfcTaskTime_type = 0;
entity* IfcTaskTimeRecurring_type = 0;
entity* IfcTaskType_type = 0;
entity* IfcTelecomAddress_type = 0;
entity* IfcTendon_type = 0;
entity* IfcTendonAnchor_type = 0;
entity* IfcTendonAnchorType_type = 0;
entity* IfcTendonType_type = 0;
entity* IfcTessellatedFaceSet_type = 0;
entity* IfcTessellatedItem_type = 0;
entity* IfcTextLiteral_type = 0;
entity* IfcTextLiteralWithExtent_type = 0;
entity* IfcTextStyle_type = 0;
entity* IfcTextStyleFontModel_type = 0;
entity* IfcTextStyleForDefinedFont_type = 0;
entity* IfcTextStyleTextModel_type = 0;
entity* IfcTextureCoordinate_type = 0;
entity* IfcTextureCoordinateGenerator_type = 0;
entity* IfcTextureMap_type = 0;
entity* IfcTextureVertex_type = 0;
entity* IfcTextureVertexList_type = 0;
entity* IfcTimePeriod_type = 0;
entity* IfcTimeSeries_type = 0;
entity* IfcTimeSeriesValue_type = 0;
entity* IfcTopologicalRepresentationItem_type = 0;
entity* IfcTopologyRepresentation_type = 0;
entity* IfcTransformer_type = 0;
entity* IfcTransformerType_type = 0;
entity* IfcTransportElement_type = 0;
entity* IfcTransportElementType_type = 0;
entity* IfcTrapeziumProfileDef_type = 0;
entity* IfcTriangulatedFaceSet_type = 0;
entity* IfcTrimmedCurve_type = 0;
entity* IfcTubeBundle_type = 0;
entity* IfcTubeBundleType_type = 0;
entity* IfcTypeObject_type = 0;
entity* IfcTypeProcess_type = 0;
entity* IfcTypeProduct_type = 0;
entity* IfcTypeResource_type = 0;
entity* IfcUShapeProfileDef_type = 0;
entity* IfcUnitAssignment_type = 0;
entity* IfcUnitaryControlElement_type = 0;
entity* IfcUnitaryControlElementType_type = 0;
entity* IfcUnitaryEquipment_type = 0;
entity* IfcUnitaryEquipmentType_type = 0;
entity* IfcValve_type = 0;
entity* IfcValveType_type = 0;
entity* IfcVector_type = 0;
entity* IfcVertex_type = 0;
entity* IfcVertexLoop_type = 0;
entity* IfcVertexPoint_type = 0;
entity* IfcVibrationIsolator_type = 0;
entity* IfcVibrationIsolatorType_type = 0;
entity* IfcVirtualElement_type = 0;
entity* IfcVirtualGridIntersection_type = 0;
entity* IfcVoidingFeature_type = 0;
entity* IfcWall_type = 0;
entity* IfcWallElementedCase_type = 0;
entity* IfcWallStandardCase_type = 0;
entity* IfcWallType_type = 0;
entity* IfcWasteTerminal_type = 0;
entity* IfcWasteTerminalType_type = 0;
entity* IfcWindow_type = 0;
entity* IfcWindowLiningProperties_type = 0;
entity* IfcWindowPanelProperties_type = 0;
entity* IfcWindowStandardCase_type = 0;
entity* IfcWindowStyle_type = 0;
entity* IfcWindowType_type = 0;
entity* IfcWorkCalendar_type = 0;
entity* IfcWorkControl_type = 0;
entity* IfcWorkPlan_type = 0;
entity* IfcWorkSchedule_type = 0;
entity* IfcWorkTime_type = 0;
entity* IfcZShapeProfileDef_type = 0;
entity* IfcZone_type = 0;
type_declaration* IfcAbsorbedDoseMeasure_type = 0;
type_declaration* IfcAccelerationMeasure_type = 0;
type_declaration* IfcAmountOfSubstanceMeasure_type = 0;
type_declaration* IfcAngularVelocityMeasure_type = 0;
type_declaration* IfcArcIndex_type = 0;
type_declaration* IfcAreaDensityMeasure_type = 0;
type_declaration* IfcAreaMeasure_type = 0;
type_declaration* IfcBinary_type = 0;
type_declaration* IfcBoolean_type = 0;
type_declaration* IfcBoxAlignment_type = 0;
type_declaration* IfcCardinalPointReference_type = 0;
type_declaration* IfcComplexNumber_type = 0;
type_declaration* IfcCompoundPlaneAngleMeasure_type = 0;
type_declaration* IfcContextDependentMeasure_type = 0;
type_declaration* IfcCountMeasure_type = 0;
type_declaration* IfcCurvatureMeasure_type = 0;
type_declaration* IfcDate_type = 0;
type_declaration* IfcDateTime_type = 0;
type_declaration* IfcDayInMonthNumber_type = 0;
type_declaration* IfcDayInWeekNumber_type = 0;
type_declaration* IfcDescriptiveMeasure_type = 0;
type_declaration* IfcDimensionCount_type = 0;
type_declaration* IfcDoseEquivalentMeasure_type = 0;
type_declaration* IfcDuration_type = 0;
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
type_declaration* IfcIdentifier_type = 0;
type_declaration* IfcIlluminanceMeasure_type = 0;
type_declaration* IfcInductanceMeasure_type = 0;
type_declaration* IfcInteger_type = 0;
type_declaration* IfcIntegerCountRateMeasure_type = 0;
type_declaration* IfcIonConcentrationMeasure_type = 0;
type_declaration* IfcIsothermalMoistureCapacityMeasure_type = 0;
type_declaration* IfcKinematicViscosityMeasure_type = 0;
type_declaration* IfcLabel_type = 0;
type_declaration* IfcLanguageId_type = 0;
type_declaration* IfcLengthMeasure_type = 0;
type_declaration* IfcLineIndex_type = 0;
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
type_declaration* IfcModulusOfElasticityMeasure_type = 0;
type_declaration* IfcModulusOfLinearSubgradeReactionMeasure_type = 0;
type_declaration* IfcModulusOfRotationalSubgradeReactionMeasure_type = 0;
type_declaration* IfcModulusOfSubgradeReactionMeasure_type = 0;
type_declaration* IfcMoistureDiffusivityMeasure_type = 0;
type_declaration* IfcMolecularWeightMeasure_type = 0;
type_declaration* IfcMomentOfInertiaMeasure_type = 0;
type_declaration* IfcMonetaryMeasure_type = 0;
type_declaration* IfcMonthInYearNumber_type = 0;
type_declaration* IfcNonNegativeLengthMeasure_type = 0;
type_declaration* IfcNormalisedRatioMeasure_type = 0;
type_declaration* IfcNumericMeasure_type = 0;
type_declaration* IfcPHMeasure_type = 0;
type_declaration* IfcParameterValue_type = 0;
type_declaration* IfcPlanarForceMeasure_type = 0;
type_declaration* IfcPlaneAngleMeasure_type = 0;
type_declaration* IfcPositiveInteger_type = 0;
type_declaration* IfcPositiveLengthMeasure_type = 0;
type_declaration* IfcPositivePlaneAngleMeasure_type = 0;
type_declaration* IfcPositiveRatioMeasure_type = 0;
type_declaration* IfcPowerMeasure_type = 0;
type_declaration* IfcPresentableText_type = 0;
type_declaration* IfcPressureMeasure_type = 0;
type_declaration* IfcPropertySetDefinitionSet_type = 0;
type_declaration* IfcRadioActivityMeasure_type = 0;
type_declaration* IfcRatioMeasure_type = 0;
type_declaration* IfcReal_type = 0;
type_declaration* IfcRotationalFrequencyMeasure_type = 0;
type_declaration* IfcRotationalMassMeasure_type = 0;
type_declaration* IfcRotationalStiffnessMeasure_type = 0;
type_declaration* IfcSectionModulusMeasure_type = 0;
type_declaration* IfcSectionalAreaIntegralMeasure_type = 0;
type_declaration* IfcShearModulusMeasure_type = 0;
type_declaration* IfcSolidAngleMeasure_type = 0;
type_declaration* IfcSoundPowerLevelMeasure_type = 0;
type_declaration* IfcSoundPowerMeasure_type = 0;
type_declaration* IfcSoundPressureLevelMeasure_type = 0;
type_declaration* IfcSoundPressureMeasure_type = 0;
type_declaration* IfcSpecificHeatCapacityMeasure_type = 0;
type_declaration* IfcSpecularExponent_type = 0;
type_declaration* IfcSpecularRoughness_type = 0;
type_declaration* IfcStrippedOptional_type = 0;
type_declaration* IfcTemperatureGradientMeasure_type = 0;
type_declaration* IfcTemperatureRateOfChangeMeasure_type = 0;
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
type_declaration* IfcTime_type = 0;
type_declaration* IfcTimeMeasure_type = 0;
type_declaration* IfcTimeStamp_type = 0;
type_declaration* IfcTorqueMeasure_type = 0;
type_declaration* IfcURIReference_type = 0;
type_declaration* IfcVaporPermeabilityMeasure_type = 0;
type_declaration* IfcVolumeMeasure_type = 0;
type_declaration* IfcVolumetricFlowRateMeasure_type = 0;
type_declaration* IfcWarpingConstantMeasure_type = 0;
type_declaration* IfcWarpingMomentMeasure_type = 0;
select_type* IfcActorSelect_type = 0;
select_type* IfcAppliedValueSelect_type = 0;
select_type* IfcAxis2Placement_type = 0;
select_type* IfcBendingParameterSelect_type = 0;
select_type* IfcBooleanOperand_type = 0;
select_type* IfcClassificationReferenceSelect_type = 0;
select_type* IfcClassificationSelect_type = 0;
select_type* IfcColour_type = 0;
select_type* IfcColourOrFactor_type = 0;
select_type* IfcCoordinateReferenceSystemSelect_type = 0;
select_type* IfcCsgSelect_type = 0;
select_type* IfcCurveFontOrScaledCurveFontSelect_type = 0;
select_type* IfcCurveOnSurface_type = 0;
select_type* IfcCurveOrEdgeCurve_type = 0;
select_type* IfcCurveStyleFontSelect_type = 0;
select_type* IfcDefinitionSelect_type = 0;
select_type* IfcDerivedMeasureValue_type = 0;
select_type* IfcDocumentSelect_type = 0;
select_type* IfcFillStyleSelect_type = 0;
select_type* IfcGeometricSetSelect_type = 0;
select_type* IfcGridPlacementDirectionSelect_type = 0;
select_type* IfcHatchLineDistanceSelect_type = 0;
select_type* IfcLayeredItem_type = 0;
select_type* IfcLibrarySelect_type = 0;
select_type* IfcLightDistributionDataSourceSelect_type = 0;
select_type* IfcMaterialSelect_type = 0;
select_type* IfcMeasureValue_type = 0;
select_type* IfcMetricValueSelect_type = 0;
select_type* IfcModulusOfRotationalSubgradeReactionSelect_type = 0;
select_type* IfcModulusOfSubgradeReactionSelect_type = 0;
select_type* IfcModulusOfTranslationalSubgradeReactionSelect_type = 0;
select_type* IfcObjectReferenceSelect_type = 0;
select_type* IfcPointOrVertexPoint_type = 0;
select_type* IfcPresentationStyleSelect_type = 0;
select_type* IfcProcessSelect_type = 0;
select_type* IfcProductRepresentationSelect_type = 0;
select_type* IfcProductSelect_type = 0;
select_type* IfcPropertySetDefinitionSelect_type = 0;
select_type* IfcResourceObjectSelect_type = 0;
select_type* IfcResourceSelect_type = 0;
select_type* IfcRotationalStiffnessSelect_type = 0;
select_type* IfcSegmentIndexSelect_type = 0;
select_type* IfcShell_type = 0;
select_type* IfcSimpleValue_type = 0;
select_type* IfcSizeSelect_type = 0;
select_type* IfcSolidOrShell_type = 0;
select_type* IfcSpaceBoundarySelect_type = 0;
select_type* IfcSpecularHighlightSelect_type = 0;
select_type* IfcStructuralActivityAssignmentSelect_type = 0;
select_type* IfcStyleAssignmentSelect_type = 0;
select_type* IfcSurfaceOrFaceSurface_type = 0;
select_type* IfcSurfaceStyleElementSelect_type = 0;
select_type* IfcTextFontSelect_type = 0;
select_type* IfcTimeOrRatioSelect_type = 0;
select_type* IfcTranslationalStiffnessSelect_type = 0;
select_type* IfcTrimmingSelect_type = 0;
select_type* IfcUnit_type = 0;
select_type* IfcValue_type = 0;
select_type* IfcVectorOrDirection_type = 0;
select_type* IfcWarpingStiffnessSelect_type = 0;
enumeration_type* IfcActionRequestTypeEnum_type = 0;
enumeration_type* IfcActionSourceTypeEnum_type = 0;
enumeration_type* IfcActionTypeEnum_type = 0;
enumeration_type* IfcActuatorTypeEnum_type = 0;
enumeration_type* IfcAddressTypeEnum_type = 0;
enumeration_type* IfcAirTerminalBoxTypeEnum_type = 0;
enumeration_type* IfcAirTerminalTypeEnum_type = 0;
enumeration_type* IfcAirToAirHeatRecoveryTypeEnum_type = 0;
enumeration_type* IfcAlarmTypeEnum_type = 0;
enumeration_type* IfcAnalysisModelTypeEnum_type = 0;
enumeration_type* IfcAnalysisTheoryTypeEnum_type = 0;
enumeration_type* IfcArithmeticOperatorEnum_type = 0;
enumeration_type* IfcAssemblyPlaceEnum_type = 0;
enumeration_type* IfcAudioVisualApplianceTypeEnum_type = 0;
enumeration_type* IfcBSplineCurveForm_type = 0;
enumeration_type* IfcBSplineSurfaceForm_type = 0;
enumeration_type* IfcBeamTypeEnum_type = 0;
enumeration_type* IfcBenchmarkEnum_type = 0;
enumeration_type* IfcBoilerTypeEnum_type = 0;
enumeration_type* IfcBooleanOperator_type = 0;
enumeration_type* IfcBuildingElementPartTypeEnum_type = 0;
enumeration_type* IfcBuildingElementProxyTypeEnum_type = 0;
enumeration_type* IfcBuildingSystemTypeEnum_type = 0;
enumeration_type* IfcBurnerTypeEnum_type = 0;
enumeration_type* IfcCableCarrierFittingTypeEnum_type = 0;
enumeration_type* IfcCableCarrierSegmentTypeEnum_type = 0;
enumeration_type* IfcCableFittingTypeEnum_type = 0;
enumeration_type* IfcCableSegmentTypeEnum_type = 0;
enumeration_type* IfcChangeActionEnum_type = 0;
enumeration_type* IfcChillerTypeEnum_type = 0;
enumeration_type* IfcChimneyTypeEnum_type = 0;
enumeration_type* IfcCoilTypeEnum_type = 0;
enumeration_type* IfcColumnTypeEnum_type = 0;
enumeration_type* IfcCommunicationsApplianceTypeEnum_type = 0;
enumeration_type* IfcComplexPropertyTemplateTypeEnum_type = 0;
enumeration_type* IfcCompressorTypeEnum_type = 0;
enumeration_type* IfcCondenserTypeEnum_type = 0;
enumeration_type* IfcConnectionTypeEnum_type = 0;
enumeration_type* IfcConstraintEnum_type = 0;
enumeration_type* IfcConstructionEquipmentResourceTypeEnum_type = 0;
enumeration_type* IfcConstructionMaterialResourceTypeEnum_type = 0;
enumeration_type* IfcConstructionProductResourceTypeEnum_type = 0;
enumeration_type* IfcControllerTypeEnum_type = 0;
enumeration_type* IfcCooledBeamTypeEnum_type = 0;
enumeration_type* IfcCoolingTowerTypeEnum_type = 0;
enumeration_type* IfcCostItemTypeEnum_type = 0;
enumeration_type* IfcCostScheduleTypeEnum_type = 0;
enumeration_type* IfcCoveringTypeEnum_type = 0;
enumeration_type* IfcCrewResourceTypeEnum_type = 0;
enumeration_type* IfcCurtainWallTypeEnum_type = 0;
enumeration_type* IfcCurveInterpolationEnum_type = 0;
enumeration_type* IfcDamperTypeEnum_type = 0;
enumeration_type* IfcDataOriginEnum_type = 0;
enumeration_type* IfcDerivedUnitEnum_type = 0;
enumeration_type* IfcDirectionSenseEnum_type = 0;
enumeration_type* IfcDiscreteAccessoryTypeEnum_type = 0;
enumeration_type* IfcDistributionChamberElementTypeEnum_type = 0;
enumeration_type* IfcDistributionPortTypeEnum_type = 0;
enumeration_type* IfcDistributionSystemEnum_type = 0;
enumeration_type* IfcDocumentConfidentialityEnum_type = 0;
enumeration_type* IfcDocumentStatusEnum_type = 0;
enumeration_type* IfcDoorPanelOperationEnum_type = 0;
enumeration_type* IfcDoorPanelPositionEnum_type = 0;
enumeration_type* IfcDoorStyleConstructionEnum_type = 0;
enumeration_type* IfcDoorStyleOperationEnum_type = 0;
enumeration_type* IfcDoorTypeEnum_type = 0;
enumeration_type* IfcDoorTypeOperationEnum_type = 0;
enumeration_type* IfcDuctFittingTypeEnum_type = 0;
enumeration_type* IfcDuctSegmentTypeEnum_type = 0;
enumeration_type* IfcDuctSilencerTypeEnum_type = 0;
enumeration_type* IfcElectricApplianceTypeEnum_type = 0;
enumeration_type* IfcElectricDistributionBoardTypeEnum_type = 0;
enumeration_type* IfcElectricFlowStorageDeviceTypeEnum_type = 0;
enumeration_type* IfcElectricGeneratorTypeEnum_type = 0;
enumeration_type* IfcElectricMotorTypeEnum_type = 0;
enumeration_type* IfcElectricTimeControlTypeEnum_type = 0;
enumeration_type* IfcElementAssemblyTypeEnum_type = 0;
enumeration_type* IfcElementCompositionEnum_type = 0;
enumeration_type* IfcEngineTypeEnum_type = 0;
enumeration_type* IfcEvaporativeCoolerTypeEnum_type = 0;
enumeration_type* IfcEvaporatorTypeEnum_type = 0;
enumeration_type* IfcEventTriggerTypeEnum_type = 0;
enumeration_type* IfcEventTypeEnum_type = 0;
enumeration_type* IfcExternalSpatialElementTypeEnum_type = 0;
enumeration_type* IfcFanTypeEnum_type = 0;
enumeration_type* IfcFastenerTypeEnum_type = 0;
enumeration_type* IfcFilterTypeEnum_type = 0;
enumeration_type* IfcFireSuppressionTerminalTypeEnum_type = 0;
enumeration_type* IfcFlowDirectionEnum_type = 0;
enumeration_type* IfcFlowInstrumentTypeEnum_type = 0;
enumeration_type* IfcFlowMeterTypeEnum_type = 0;
enumeration_type* IfcFootingTypeEnum_type = 0;
enumeration_type* IfcFurnitureTypeEnum_type = 0;
enumeration_type* IfcGeographicElementTypeEnum_type = 0;
enumeration_type* IfcGeometricProjectionEnum_type = 0;
enumeration_type* IfcGlobalOrLocalEnum_type = 0;
enumeration_type* IfcGridTypeEnum_type = 0;
enumeration_type* IfcHeatExchangerTypeEnum_type = 0;
enumeration_type* IfcHumidifierTypeEnum_type = 0;
enumeration_type* IfcInterceptorTypeEnum_type = 0;
enumeration_type* IfcInternalOrExternalEnum_type = 0;
enumeration_type* IfcInventoryTypeEnum_type = 0;
enumeration_type* IfcJunctionBoxTypeEnum_type = 0;
enumeration_type* IfcKnotType_type = 0;
enumeration_type* IfcLaborResourceTypeEnum_type = 0;
enumeration_type* IfcLampTypeEnum_type = 0;
enumeration_type* IfcLayerSetDirectionEnum_type = 0;
enumeration_type* IfcLightDistributionCurveEnum_type = 0;
enumeration_type* IfcLightEmissionSourceEnum_type = 0;
enumeration_type* IfcLightFixtureTypeEnum_type = 0;
enumeration_type* IfcLoadGroupTypeEnum_type = 0;
enumeration_type* IfcLogicalOperatorEnum_type = 0;
enumeration_type* IfcMechanicalFastenerTypeEnum_type = 0;
enumeration_type* IfcMedicalDeviceTypeEnum_type = 0;
enumeration_type* IfcMemberTypeEnum_type = 0;
enumeration_type* IfcMotorConnectionTypeEnum_type = 0;
enumeration_type* IfcNullStyle_type = 0;
enumeration_type* IfcObjectTypeEnum_type = 0;
enumeration_type* IfcObjectiveEnum_type = 0;
enumeration_type* IfcOccupantTypeEnum_type = 0;
enumeration_type* IfcOpeningElementTypeEnum_type = 0;
enumeration_type* IfcOutletTypeEnum_type = 0;
enumeration_type* IfcPerformanceHistoryTypeEnum_type = 0;
enumeration_type* IfcPermeableCoveringOperationEnum_type = 0;
enumeration_type* IfcPermitTypeEnum_type = 0;
enumeration_type* IfcPhysicalOrVirtualEnum_type = 0;
enumeration_type* IfcPileConstructionEnum_type = 0;
enumeration_type* IfcPileTypeEnum_type = 0;
enumeration_type* IfcPipeFittingTypeEnum_type = 0;
enumeration_type* IfcPipeSegmentTypeEnum_type = 0;
enumeration_type* IfcPlateTypeEnum_type = 0;
enumeration_type* IfcProcedureTypeEnum_type = 0;
enumeration_type* IfcProfileTypeEnum_type = 0;
enumeration_type* IfcProjectOrderTypeEnum_type = 0;
enumeration_type* IfcProjectedOrTrueLengthEnum_type = 0;
enumeration_type* IfcProjectionElementTypeEnum_type = 0;
enumeration_type* IfcPropertySetTemplateTypeEnum_type = 0;
enumeration_type* IfcProtectiveDeviceTrippingUnitTypeEnum_type = 0;
enumeration_type* IfcProtectiveDeviceTypeEnum_type = 0;
enumeration_type* IfcPumpTypeEnum_type = 0;
enumeration_type* IfcRailingTypeEnum_type = 0;
enumeration_type* IfcRampFlightTypeEnum_type = 0;
enumeration_type* IfcRampTypeEnum_type = 0;
enumeration_type* IfcRecurrenceTypeEnum_type = 0;
enumeration_type* IfcReflectanceMethodEnum_type = 0;
enumeration_type* IfcReinforcingBarRoleEnum_type = 0;
enumeration_type* IfcReinforcingBarSurfaceEnum_type = 0;
enumeration_type* IfcReinforcingBarTypeEnum_type = 0;
enumeration_type* IfcReinforcingMeshTypeEnum_type = 0;
enumeration_type* IfcRoleEnum_type = 0;
enumeration_type* IfcRoofTypeEnum_type = 0;
enumeration_type* IfcSIPrefix_type = 0;
enumeration_type* IfcSIUnitName_type = 0;
enumeration_type* IfcSanitaryTerminalTypeEnum_type = 0;
enumeration_type* IfcSectionTypeEnum_type = 0;
enumeration_type* IfcSensorTypeEnum_type = 0;
enumeration_type* IfcSequenceEnum_type = 0;
enumeration_type* IfcShadingDeviceTypeEnum_type = 0;
enumeration_type* IfcSimplePropertyTemplateTypeEnum_type = 0;
enumeration_type* IfcSlabTypeEnum_type = 0;
enumeration_type* IfcSolarDeviceTypeEnum_type = 0;
enumeration_type* IfcSpaceHeaterTypeEnum_type = 0;
enumeration_type* IfcSpaceTypeEnum_type = 0;
enumeration_type* IfcSpatialZoneTypeEnum_type = 0;
enumeration_type* IfcStackTerminalTypeEnum_type = 0;
enumeration_type* IfcStairFlightTypeEnum_type = 0;
enumeration_type* IfcStairTypeEnum_type = 0;
enumeration_type* IfcStateEnum_type = 0;
enumeration_type* IfcStructuralCurveActivityTypeEnum_type = 0;
enumeration_type* IfcStructuralCurveMemberTypeEnum_type = 0;
enumeration_type* IfcStructuralSurfaceActivityTypeEnum_type = 0;
enumeration_type* IfcStructuralSurfaceMemberTypeEnum_type = 0;
enumeration_type* IfcSubContractResourceTypeEnum_type = 0;
enumeration_type* IfcSurfaceFeatureTypeEnum_type = 0;
enumeration_type* IfcSurfaceSide_type = 0;
enumeration_type* IfcSwitchingDeviceTypeEnum_type = 0;
enumeration_type* IfcSystemFurnitureElementTypeEnum_type = 0;
enumeration_type* IfcTankTypeEnum_type = 0;
enumeration_type* IfcTaskDurationEnum_type = 0;
enumeration_type* IfcTaskTypeEnum_type = 0;
enumeration_type* IfcTendonAnchorTypeEnum_type = 0;
enumeration_type* IfcTendonTypeEnum_type = 0;
enumeration_type* IfcTextPath_type = 0;
enumeration_type* IfcTimeSeriesDataTypeEnum_type = 0;
enumeration_type* IfcTransformerTypeEnum_type = 0;
enumeration_type* IfcTransitionCode_type = 0;
enumeration_type* IfcTransportElementTypeEnum_type = 0;
enumeration_type* IfcTrimmingPreference_type = 0;
enumeration_type* IfcTubeBundleTypeEnum_type = 0;
enumeration_type* IfcUnitEnum_type = 0;
enumeration_type* IfcUnitaryControlElementTypeEnum_type = 0;
enumeration_type* IfcUnitaryEquipmentTypeEnum_type = 0;
enumeration_type* IfcValveTypeEnum_type = 0;
enumeration_type* IfcVibrationIsolatorTypeEnum_type = 0;
enumeration_type* IfcVoidingFeatureTypeEnum_type = 0;
enumeration_type* IfcWallTypeEnum_type = 0;
enumeration_type* IfcWasteTerminalTypeEnum_type = 0;
enumeration_type* IfcWindowPanelOperationEnum_type = 0;
enumeration_type* IfcWindowPanelPositionEnum_type = 0;
enumeration_type* IfcWindowStyleConstructionEnum_type = 0;
enumeration_type* IfcWindowStyleOperationEnum_type = 0;
enumeration_type* IfcWindowTypeEnum_type = 0;
enumeration_type* IfcWindowTypePartitioningEnum_type = 0;
enumeration_type* IfcWorkCalendarTypeEnum_type = 0;
enumeration_type* IfcWorkPlanTypeEnum_type = 0;
enumeration_type* IfcWorkScheduleTypeEnum_type = 0;

#ifdef _MSC_VER
#pragma optimize("", off)
#endif
        
schema_definition* populate_schema() {
    IfcAbsorbedDoseMeasure_type = new type_declaration(IfcSchema::Type::IfcAbsorbedDoseMeasure, new simple_type(simple_type::real_type));
    IfcAccelerationMeasure_type = new type_declaration(IfcSchema::Type::IfcAccelerationMeasure, new simple_type(simple_type::real_type));
    IfcAmountOfSubstanceMeasure_type = new type_declaration(IfcSchema::Type::IfcAmountOfSubstanceMeasure, new simple_type(simple_type::real_type));
    IfcAngularVelocityMeasure_type = new type_declaration(IfcSchema::Type::IfcAngularVelocityMeasure, new simple_type(simple_type::real_type));
    IfcArcIndex_type = new type_declaration(IfcSchema::Type::IfcArcIndex, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IfcPositiveInteger_type)));
    IfcAreaDensityMeasure_type = new type_declaration(IfcSchema::Type::IfcAreaDensityMeasure, new simple_type(simple_type::real_type));
    IfcAreaMeasure_type = new type_declaration(IfcSchema::Type::IfcAreaMeasure, new simple_type(simple_type::real_type));
    IfcBinary_type = new type_declaration(IfcSchema::Type::IfcBinary, new simple_type(simple_type::binary_type));
    IfcBoolean_type = new type_declaration(IfcSchema::Type::IfcBoolean, new simple_type(simple_type::boolean_type));
    IfcCardinalPointReference_type = new type_declaration(IfcSchema::Type::IfcCardinalPointReference, new simple_type(simple_type::integer_type));
    IfcComplexNumber_type = new type_declaration(IfcSchema::Type::IfcComplexNumber, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IfcCompoundPlaneAngleMeasure_type = new type_declaration(IfcSchema::Type::IfcCompoundPlaneAngleMeasure, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
    IfcContextDependentMeasure_type = new type_declaration(IfcSchema::Type::IfcContextDependentMeasure, new simple_type(simple_type::real_type));
    IfcCountMeasure_type = new type_declaration(IfcSchema::Type::IfcCountMeasure, new simple_type(simple_type::number_type));
    IfcCurvatureMeasure_type = new type_declaration(IfcSchema::Type::IfcCurvatureMeasure, new simple_type(simple_type::real_type));
    IfcDate_type = new type_declaration(IfcSchema::Type::IfcDate, new simple_type(simple_type::string_type));
    IfcDateTime_type = new type_declaration(IfcSchema::Type::IfcDateTime, new simple_type(simple_type::string_type));
    IfcDayInMonthNumber_type = new type_declaration(IfcSchema::Type::IfcDayInMonthNumber, new simple_type(simple_type::integer_type));
    IfcDayInWeekNumber_type = new type_declaration(IfcSchema::Type::IfcDayInWeekNumber, new simple_type(simple_type::integer_type));
    IfcDescriptiveMeasure_type = new type_declaration(IfcSchema::Type::IfcDescriptiveMeasure, new simple_type(simple_type::string_type));
    IfcDimensionCount_type = new type_declaration(IfcSchema::Type::IfcDimensionCount, new simple_type(simple_type::integer_type));
    IfcDoseEquivalentMeasure_type = new type_declaration(IfcSchema::Type::IfcDoseEquivalentMeasure, new simple_type(simple_type::real_type));
    IfcDuration_type = new type_declaration(IfcSchema::Type::IfcDuration, new simple_type(simple_type::string_type));
    IfcDynamicViscosityMeasure_type = new type_declaration(IfcSchema::Type::IfcDynamicViscosityMeasure, new simple_type(simple_type::real_type));
    IfcElectricCapacitanceMeasure_type = new type_declaration(IfcSchema::Type::IfcElectricCapacitanceMeasure, new simple_type(simple_type::real_type));
    IfcElectricChargeMeasure_type = new type_declaration(IfcSchema::Type::IfcElectricChargeMeasure, new simple_type(simple_type::real_type));
    IfcElectricConductanceMeasure_type = new type_declaration(IfcSchema::Type::IfcElectricConductanceMeasure, new simple_type(simple_type::real_type));
    IfcElectricCurrentMeasure_type = new type_declaration(IfcSchema::Type::IfcElectricCurrentMeasure, new simple_type(simple_type::real_type));
    IfcElectricResistanceMeasure_type = new type_declaration(IfcSchema::Type::IfcElectricResistanceMeasure, new simple_type(simple_type::real_type));
    IfcElectricVoltageMeasure_type = new type_declaration(IfcSchema::Type::IfcElectricVoltageMeasure, new simple_type(simple_type::real_type));
    IfcEnergyMeasure_type = new type_declaration(IfcSchema::Type::IfcEnergyMeasure, new simple_type(simple_type::real_type));
    IfcFontStyle_type = new type_declaration(IfcSchema::Type::IfcFontStyle, new simple_type(simple_type::string_type));
    IfcFontVariant_type = new type_declaration(IfcSchema::Type::IfcFontVariant, new simple_type(simple_type::string_type));
    IfcFontWeight_type = new type_declaration(IfcSchema::Type::IfcFontWeight, new simple_type(simple_type::string_type));
    IfcForceMeasure_type = new type_declaration(IfcSchema::Type::IfcForceMeasure, new simple_type(simple_type::real_type));
    IfcFrequencyMeasure_type = new type_declaration(IfcSchema::Type::IfcFrequencyMeasure, new simple_type(simple_type::real_type));
    IfcGloballyUniqueId_type = new type_declaration(IfcSchema::Type::IfcGloballyUniqueId, new simple_type(simple_type::string_type));
    IfcHeatFluxDensityMeasure_type = new type_declaration(IfcSchema::Type::IfcHeatFluxDensityMeasure, new simple_type(simple_type::real_type));
    IfcHeatingValueMeasure_type = new type_declaration(IfcSchema::Type::IfcHeatingValueMeasure, new simple_type(simple_type::real_type));
    IfcIdentifier_type = new type_declaration(IfcSchema::Type::IfcIdentifier, new simple_type(simple_type::string_type));
    IfcIlluminanceMeasure_type = new type_declaration(IfcSchema::Type::IfcIlluminanceMeasure, new simple_type(simple_type::real_type));
    IfcInductanceMeasure_type = new type_declaration(IfcSchema::Type::IfcInductanceMeasure, new simple_type(simple_type::real_type));
    IfcInteger_type = new type_declaration(IfcSchema::Type::IfcInteger, new simple_type(simple_type::integer_type));
    IfcIntegerCountRateMeasure_type = new type_declaration(IfcSchema::Type::IfcIntegerCountRateMeasure, new simple_type(simple_type::integer_type));
    IfcIonConcentrationMeasure_type = new type_declaration(IfcSchema::Type::IfcIonConcentrationMeasure, new simple_type(simple_type::real_type));
    IfcIsothermalMoistureCapacityMeasure_type = new type_declaration(IfcSchema::Type::IfcIsothermalMoistureCapacityMeasure, new simple_type(simple_type::real_type));
    IfcKinematicViscosityMeasure_type = new type_declaration(IfcSchema::Type::IfcKinematicViscosityMeasure, new simple_type(simple_type::real_type));
    IfcLabel_type = new type_declaration(IfcSchema::Type::IfcLabel, new simple_type(simple_type::string_type));
    IfcLanguageId_type = new type_declaration(IfcSchema::Type::IfcLanguageId, new named_type(IfcIdentifier_type));
    IfcLengthMeasure_type = new type_declaration(IfcSchema::Type::IfcLengthMeasure, new simple_type(simple_type::real_type));
    IfcLineIndex_type = new type_declaration(IfcSchema::Type::IfcLineIndex, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcPositiveInteger_type)));
    IfcLinearForceMeasure_type = new type_declaration(IfcSchema::Type::IfcLinearForceMeasure, new simple_type(simple_type::real_type));
    IfcLinearMomentMeasure_type = new type_declaration(IfcSchema::Type::IfcLinearMomentMeasure, new simple_type(simple_type::real_type));
    IfcLinearStiffnessMeasure_type = new type_declaration(IfcSchema::Type::IfcLinearStiffnessMeasure, new simple_type(simple_type::real_type));
    IfcLinearVelocityMeasure_type = new type_declaration(IfcSchema::Type::IfcLinearVelocityMeasure, new simple_type(simple_type::real_type));
    IfcLogical_type = new type_declaration(IfcSchema::Type::IfcLogical, new simple_type(simple_type::logical_type));
    IfcLuminousFluxMeasure_type = new type_declaration(IfcSchema::Type::IfcLuminousFluxMeasure, new simple_type(simple_type::real_type));
    IfcLuminousIntensityDistributionMeasure_type = new type_declaration(IfcSchema::Type::IfcLuminousIntensityDistributionMeasure, new simple_type(simple_type::real_type));
    IfcLuminousIntensityMeasure_type = new type_declaration(IfcSchema::Type::IfcLuminousIntensityMeasure, new simple_type(simple_type::real_type));
    IfcMagneticFluxDensityMeasure_type = new type_declaration(IfcSchema::Type::IfcMagneticFluxDensityMeasure, new simple_type(simple_type::real_type));
    IfcMagneticFluxMeasure_type = new type_declaration(IfcSchema::Type::IfcMagneticFluxMeasure, new simple_type(simple_type::real_type));
    IfcMassDensityMeasure_type = new type_declaration(IfcSchema::Type::IfcMassDensityMeasure, new simple_type(simple_type::real_type));
    IfcMassFlowRateMeasure_type = new type_declaration(IfcSchema::Type::IfcMassFlowRateMeasure, new simple_type(simple_type::real_type));
    IfcMassMeasure_type = new type_declaration(IfcSchema::Type::IfcMassMeasure, new simple_type(simple_type::real_type));
    IfcMassPerLengthMeasure_type = new type_declaration(IfcSchema::Type::IfcMassPerLengthMeasure, new simple_type(simple_type::real_type));
    IfcModulusOfElasticityMeasure_type = new type_declaration(IfcSchema::Type::IfcModulusOfElasticityMeasure, new simple_type(simple_type::real_type));
    IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration(IfcSchema::Type::IfcModulusOfLinearSubgradeReactionMeasure, new simple_type(simple_type::real_type));
    IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration(IfcSchema::Type::IfcModulusOfRotationalSubgradeReactionMeasure, new simple_type(simple_type::real_type));
    IfcModulusOfSubgradeReactionMeasure_type = new type_declaration(IfcSchema::Type::IfcModulusOfSubgradeReactionMeasure, new simple_type(simple_type::real_type));
    IfcMoistureDiffusivityMeasure_type = new type_declaration(IfcSchema::Type::IfcMoistureDiffusivityMeasure, new simple_type(simple_type::real_type));
    IfcMolecularWeightMeasure_type = new type_declaration(IfcSchema::Type::IfcMolecularWeightMeasure, new simple_type(simple_type::real_type));
    IfcMomentOfInertiaMeasure_type = new type_declaration(IfcSchema::Type::IfcMomentOfInertiaMeasure, new simple_type(simple_type::real_type));
    IfcMonetaryMeasure_type = new type_declaration(IfcSchema::Type::IfcMonetaryMeasure, new simple_type(simple_type::real_type));
    IfcMonthInYearNumber_type = new type_declaration(IfcSchema::Type::IfcMonthInYearNumber, new simple_type(simple_type::integer_type));
    IfcNonNegativeLengthMeasure_type = new type_declaration(IfcSchema::Type::IfcNonNegativeLengthMeasure, new named_type(IfcLengthMeasure_type));
    IfcNumericMeasure_type = new type_declaration(IfcSchema::Type::IfcNumericMeasure, new simple_type(simple_type::number_type));
    IfcPHMeasure_type = new type_declaration(IfcSchema::Type::IfcPHMeasure, new simple_type(simple_type::real_type));
    IfcParameterValue_type = new type_declaration(IfcSchema::Type::IfcParameterValue, new simple_type(simple_type::real_type));
    IfcPlanarForceMeasure_type = new type_declaration(IfcSchema::Type::IfcPlanarForceMeasure, new simple_type(simple_type::real_type));
    IfcPlaneAngleMeasure_type = new type_declaration(IfcSchema::Type::IfcPlaneAngleMeasure, new simple_type(simple_type::real_type));
    IfcPositiveInteger_type = new type_declaration(IfcSchema::Type::IfcPositiveInteger, new named_type(IfcInteger_type));
    IfcPositiveLengthMeasure_type = new type_declaration(IfcSchema::Type::IfcPositiveLengthMeasure, new named_type(IfcLengthMeasure_type));
    IfcPositivePlaneAngleMeasure_type = new type_declaration(IfcSchema::Type::IfcPositivePlaneAngleMeasure, new named_type(IfcPlaneAngleMeasure_type));
    IfcPowerMeasure_type = new type_declaration(IfcSchema::Type::IfcPowerMeasure, new simple_type(simple_type::real_type));
    IfcPresentableText_type = new type_declaration(IfcSchema::Type::IfcPresentableText, new simple_type(simple_type::string_type));
    IfcPressureMeasure_type = new type_declaration(IfcSchema::Type::IfcPressureMeasure, new simple_type(simple_type::real_type));
    IfcPropertySetDefinitionSet_type = new type_declaration(IfcSchema::Type::IfcPropertySetDefinitionSet, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPropertySetDefinition_type)));
    IfcRadioActivityMeasure_type = new type_declaration(IfcSchema::Type::IfcRadioActivityMeasure, new simple_type(simple_type::real_type));
    IfcRatioMeasure_type = new type_declaration(IfcSchema::Type::IfcRatioMeasure, new simple_type(simple_type::real_type));
    IfcReal_type = new type_declaration(IfcSchema::Type::IfcReal, new simple_type(simple_type::real_type));
    IfcRotationalFrequencyMeasure_type = new type_declaration(IfcSchema::Type::IfcRotationalFrequencyMeasure, new simple_type(simple_type::real_type));
    IfcRotationalMassMeasure_type = new type_declaration(IfcSchema::Type::IfcRotationalMassMeasure, new simple_type(simple_type::real_type));
    IfcRotationalStiffnessMeasure_type = new type_declaration(IfcSchema::Type::IfcRotationalStiffnessMeasure, new simple_type(simple_type::real_type));
    IfcSectionModulusMeasure_type = new type_declaration(IfcSchema::Type::IfcSectionModulusMeasure, new simple_type(simple_type::real_type));
    IfcSectionalAreaIntegralMeasure_type = new type_declaration(IfcSchema::Type::IfcSectionalAreaIntegralMeasure, new simple_type(simple_type::real_type));
    IfcShearModulusMeasure_type = new type_declaration(IfcSchema::Type::IfcShearModulusMeasure, new simple_type(simple_type::real_type));
    IfcSolidAngleMeasure_type = new type_declaration(IfcSchema::Type::IfcSolidAngleMeasure, new simple_type(simple_type::real_type));
    IfcSoundPowerLevelMeasure_type = new type_declaration(IfcSchema::Type::IfcSoundPowerLevelMeasure, new simple_type(simple_type::real_type));
    IfcSoundPowerMeasure_type = new type_declaration(IfcSchema::Type::IfcSoundPowerMeasure, new simple_type(simple_type::real_type));
    IfcSoundPressureLevelMeasure_type = new type_declaration(IfcSchema::Type::IfcSoundPressureLevelMeasure, new simple_type(simple_type::real_type));
    IfcSoundPressureMeasure_type = new type_declaration(IfcSchema::Type::IfcSoundPressureMeasure, new simple_type(simple_type::real_type));
    IfcSpecificHeatCapacityMeasure_type = new type_declaration(IfcSchema::Type::IfcSpecificHeatCapacityMeasure, new simple_type(simple_type::real_type));
    IfcSpecularExponent_type = new type_declaration(IfcSchema::Type::IfcSpecularExponent, new simple_type(simple_type::real_type));
    IfcSpecularRoughness_type = new type_declaration(IfcSchema::Type::IfcSpecularRoughness, new simple_type(simple_type::real_type));
    IfcStrippedOptional_type = new type_declaration(IfcSchema::Type::IfcStrippedOptional, new simple_type(simple_type::boolean_type));
    IfcTemperatureGradientMeasure_type = new type_declaration(IfcSchema::Type::IfcTemperatureGradientMeasure, new simple_type(simple_type::real_type));
    IfcTemperatureRateOfChangeMeasure_type = new type_declaration(IfcSchema::Type::IfcTemperatureRateOfChangeMeasure, new simple_type(simple_type::real_type));
    IfcText_type = new type_declaration(IfcSchema::Type::IfcText, new simple_type(simple_type::string_type));
    IfcTextAlignment_type = new type_declaration(IfcSchema::Type::IfcTextAlignment, new simple_type(simple_type::string_type));
    IfcTextDecoration_type = new type_declaration(IfcSchema::Type::IfcTextDecoration, new simple_type(simple_type::string_type));
    IfcTextFontName_type = new type_declaration(IfcSchema::Type::IfcTextFontName, new simple_type(simple_type::string_type));
    IfcTextTransformation_type = new type_declaration(IfcSchema::Type::IfcTextTransformation, new simple_type(simple_type::string_type));
    IfcThermalAdmittanceMeasure_type = new type_declaration(IfcSchema::Type::IfcThermalAdmittanceMeasure, new simple_type(simple_type::real_type));
    IfcThermalConductivityMeasure_type = new type_declaration(IfcSchema::Type::IfcThermalConductivityMeasure, new simple_type(simple_type::real_type));
    IfcThermalExpansionCoefficientMeasure_type = new type_declaration(IfcSchema::Type::IfcThermalExpansionCoefficientMeasure, new simple_type(simple_type::real_type));
    IfcThermalResistanceMeasure_type = new type_declaration(IfcSchema::Type::IfcThermalResistanceMeasure, new simple_type(simple_type::real_type));
    IfcThermalTransmittanceMeasure_type = new type_declaration(IfcSchema::Type::IfcThermalTransmittanceMeasure, new simple_type(simple_type::real_type));
    IfcThermodynamicTemperatureMeasure_type = new type_declaration(IfcSchema::Type::IfcThermodynamicTemperatureMeasure, new simple_type(simple_type::real_type));
    IfcTime_type = new type_declaration(IfcSchema::Type::IfcTime, new simple_type(simple_type::string_type));
    IfcTimeMeasure_type = new type_declaration(IfcSchema::Type::IfcTimeMeasure, new simple_type(simple_type::real_type));
    IfcTimeStamp_type = new type_declaration(IfcSchema::Type::IfcTimeStamp, new simple_type(simple_type::integer_type));
    IfcTorqueMeasure_type = new type_declaration(IfcSchema::Type::IfcTorqueMeasure, new simple_type(simple_type::real_type));
    IfcURIReference_type = new type_declaration(IfcSchema::Type::IfcURIReference, new simple_type(simple_type::string_type));
    IfcVaporPermeabilityMeasure_type = new type_declaration(IfcSchema::Type::IfcVaporPermeabilityMeasure, new simple_type(simple_type::real_type));
    IfcVolumeMeasure_type = new type_declaration(IfcSchema::Type::IfcVolumeMeasure, new simple_type(simple_type::real_type));
    IfcVolumetricFlowRateMeasure_type = new type_declaration(IfcSchema::Type::IfcVolumetricFlowRateMeasure, new simple_type(simple_type::real_type));
    IfcWarpingConstantMeasure_type = new type_declaration(IfcSchema::Type::IfcWarpingConstantMeasure, new simple_type(simple_type::real_type));
    IfcWarpingMomentMeasure_type = new type_declaration(IfcSchema::Type::IfcWarpingMomentMeasure, new simple_type(simple_type::real_type));
    IfcBoxAlignment_type = new type_declaration(IfcSchema::Type::IfcBoxAlignment, new named_type(IfcLabel_type));
    IfcNormalisedRatioMeasure_type = new type_declaration(IfcSchema::Type::IfcNormalisedRatioMeasure, new named_type(IfcRatioMeasure_type));
    IfcPositiveRatioMeasure_type = new type_declaration(IfcSchema::Type::IfcPositiveRatioMeasure, new named_type(IfcRatioMeasure_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("EMAIL");
        items.push_back("FAX");
        items.push_back("NOTDEFINED");
        items.push_back("PHONE");
        items.push_back("POST");
        items.push_back("USERDEFINED");
        items.push_back("VERBAL");
        IfcActionRequestTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcActionRequestTypeEnum, items);
    }
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
        IfcActionSourceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcActionSourceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IfcActionTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcActionTypeEnum, items);
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
        IfcActuatorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcActuatorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IfcAddressTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcAddressTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IfcAirTerminalBoxTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcAirTerminalBoxTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("DIFFUSER");
        items.push_back("GRILLE");
        items.push_back("LOUVRE");
        items.push_back("NOTDEFINED");
        items.push_back("REGISTER");
        items.push_back("USERDEFINED");
        IfcAirTerminalTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcAirTerminalTypeEnum, items);
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
        IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcAirToAirHeatRecoveryTypeEnum, items);
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
        IfcAlarmTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcAlarmTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IfcAnalysisModelTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcAnalysisModelTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IfcAnalysisTheoryTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcAnalysisTheoryTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IfcArithmeticOperatorEnum_type = new enumeration_type(IfcSchema::Type::IfcArithmeticOperatorEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IfcAssemblyPlaceEnum_type = new enumeration_type(IfcSchema::Type::IfcAssemblyPlaceEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(13);
        items.push_back("AMPLIFIER");
        items.push_back("CAMERA");
        items.push_back("DISPLAY");
        items.push_back("MICROPHONE");
        items.push_back("NOTDEFINED");
        items.push_back("PLAYER");
        items.push_back("PROJECTOR");
        items.push_back("RECEIVER");
        items.push_back("SPEAKER");
        items.push_back("SWITCHER");
        items.push_back("TELEPHONE");
        items.push_back("TUNER");
        items.push_back("USERDEFINED");
        IfcAudioVisualApplianceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcAudioVisualApplianceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IfcBSplineCurveForm_type = new enumeration_type(IfcSchema::Type::IfcBSplineCurveForm, items);
    }
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("CONICAL_SURF");
        items.push_back("CYLINDRICAL_SURF");
        items.push_back("GENERALISED_CONE");
        items.push_back("PLANE_SURF");
        items.push_back("QUADRIC_SURF");
        items.push_back("RULED_SURF");
        items.push_back("SPHERICAL_SURF");
        items.push_back("SURF_OF_LINEAR_EXTRUSION");
        items.push_back("SURF_OF_REVOLUTION");
        items.push_back("TOROIDAL_SURF");
        items.push_back("UNSPECIFIED");
        IfcBSplineSurfaceForm_type = new enumeration_type(IfcSchema::Type::IfcBSplineSurfaceForm, items);
    }
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("BEAM");
        items.push_back("HOLLOWCORE");
        items.push_back("JOIST");
        items.push_back("LINTEL");
        items.push_back("NOTDEFINED");
        items.push_back("SPANDREL");
        items.push_back("T_BEAM");
        items.push_back("USERDEFINED");
        IfcBeamTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcBeamTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("EQUALTO");
        items.push_back("GREATERTHAN");
        items.push_back("GREATERTHANOREQUALTO");
        items.push_back("INCLUDEDIN");
        items.push_back("INCLUDES");
        items.push_back("LESSTHAN");
        items.push_back("LESSTHANOREQUALTO");
        items.push_back("NOTEQUALTO");
        items.push_back("NOTINCLUDEDIN");
        items.push_back("NOTINCLUDES");
        IfcBenchmarkEnum_type = new enumeration_type(IfcSchema::Type::IfcBenchmarkEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IfcBoilerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcBoilerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IfcBooleanOperator_type = new enumeration_type(IfcSchema::Type::IfcBooleanOperator, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("INSULATION");
        items.push_back("NOTDEFINED");
        items.push_back("PRECASTPANEL");
        items.push_back("USERDEFINED");
        IfcBuildingElementPartTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcBuildingElementPartTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("PARTIAL");
        items.push_back("PROVISIONFORVOID");
        items.push_back("USERDEFINED");
        IfcBuildingElementProxyTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcBuildingElementProxyTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("FENESTRATION");
        items.push_back("FOUNDATION");
        items.push_back("LOADBEARING");
        items.push_back("NOTDEFINED");
        items.push_back("OUTERSHELL");
        items.push_back("SHADING");
        items.push_back("TRANSPORT");
        items.push_back("USERDEFINED");
        IfcBuildingSystemTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcBuildingSystemTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcBurnerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcBurnerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IfcCableCarrierFittingTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCableCarrierFittingTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCableCarrierSegmentTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCableCarrierSegmentTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CONNECTOR");
        items.push_back("ENTRY");
        items.push_back("EXIT");
        items.push_back("JUNCTION");
        items.push_back("NOTDEFINED");
        items.push_back("TRANSITION");
        items.push_back("USERDEFINED");
        IfcCableFittingTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCableFittingTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BUSBARSEGMENT");
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("CORESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCableSegmentTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCableSegmentTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("NOCHANGE");
        items.push_back("NOTDEFINED");
        IfcChangeActionEnum_type = new enumeration_type(IfcSchema::Type::IfcChangeActionEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IfcChillerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcChillerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcChimneyTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcChimneyTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("DXCOOLINGCOIL");
        items.push_back("ELECTRICHEATINGCOIL");
        items.push_back("GASHEATINGCOIL");
        items.push_back("HYDRONICCOIL");
        items.push_back("NOTDEFINED");
        items.push_back("STEAMHEATINGCOIL");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLINGCOIL");
        items.push_back("WATERHEATINGCOIL");
        IfcCoilTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCoilTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("PILASTER");
        items.push_back("USERDEFINED");
        IfcColumnTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcColumnTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(14);
        items.push_back("ANTENNA");
        items.push_back("COMPUTER");
        items.push_back("FAX");
        items.push_back("GATEWAY");
        items.push_back("MODEM");
        items.push_back("NETWORKAPPLIANCE");
        items.push_back("NETWORKBRIDGE");
        items.push_back("NETWORKHUB");
        items.push_back("NOTDEFINED");
        items.push_back("PRINTER");
        items.push_back("REPEATER");
        items.push_back("ROUTER");
        items.push_back("SCANNER");
        items.push_back("USERDEFINED");
        IfcCommunicationsApplianceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCommunicationsApplianceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("P_COMPLEX");
        items.push_back("Q_COMPLEX");
        IfcComplexPropertyTemplateTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcComplexPropertyTemplateTypeEnum, items);
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
        IfcCompressorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCompressorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("AIRCOOLED");
        items.push_back("EVAPORATIVECOOLED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        items.push_back("WATERCOOLEDBRAZEDPLATE");
        items.push_back("WATERCOOLEDSHELLCOIL");
        items.push_back("WATERCOOLEDSHELLTUBE");
        items.push_back("WATERCOOLEDTUBEINTUBE");
        IfcCondenserTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCondenserTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IfcConnectionTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcConnectionTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IfcConstraintEnum_type = new enumeration_type(IfcSchema::Type::IfcConstraintEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("DEMOLISHING");
        items.push_back("EARTHMOVING");
        items.push_back("ERECTING");
        items.push_back("HEATING");
        items.push_back("LIGHTING");
        items.push_back("NOTDEFINED");
        items.push_back("PAVING");
        items.push_back("PUMPING");
        items.push_back("TRANSPORTING");
        items.push_back("USERDEFINED");
        IfcConstructionEquipmentResourceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcConstructionEquipmentResourceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("AGGREGATES");
        items.push_back("CONCRETE");
        items.push_back("DRYWALL");
        items.push_back("FUEL");
        items.push_back("GYPSUM");
        items.push_back("MASONRY");
        items.push_back("METAL");
        items.push_back("NOTDEFINED");
        items.push_back("PLASTIC");
        items.push_back("USERDEFINED");
        items.push_back("WOOD");
        IfcConstructionMaterialResourceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcConstructionMaterialResourceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ASSEMBLY");
        items.push_back("FORMWORK");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcConstructionProductResourceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcConstructionProductResourceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("FLOATING");
        items.push_back("MULTIPOSITION");
        items.push_back("NOTDEFINED");
        items.push_back("PROGRAMMABLE");
        items.push_back("PROPORTIONAL");
        items.push_back("TWOPOSITION");
        items.push_back("USERDEFINED");
        IfcControllerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcControllerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IfcCooledBeamTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCooledBeamTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCoolingTowerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCoolingTowerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCostItemTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCostItemTypeEnum, items);
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
        IfcCostScheduleTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCostScheduleTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(12);
        items.push_back("CEILING");
        items.push_back("CLADDING");
        items.push_back("FLOORING");
        items.push_back("INSULATION");
        items.push_back("MEMBRANE");
        items.push_back("MOLDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOFING");
        items.push_back("SKIRTINGBOARD");
        items.push_back("SLEEVING");
        items.push_back("USERDEFINED");
        items.push_back("WRAPPING");
        IfcCoveringTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCoveringTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IfcCrewResourceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCrewResourceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCurtainWallTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcCurtainWallTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LINEAR");
        items.push_back("LOG_LINEAR");
        items.push_back("LOG_LOG");
        items.push_back("NOTDEFINED");
        IfcCurveInterpolationEnum_type = new enumeration_type(IfcSchema::Type::IfcCurveInterpolationEnum, items);
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
        IfcDamperTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcDamperTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IfcDataOriginEnum_type = new enumeration_type(IfcSchema::Type::IfcDataOriginEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(53);
        items.push_back("ACCELERATIONUNIT");
        items.push_back("ANGULARVELOCITYUNIT");
        items.push_back("AREADENSITYUNIT");
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
        items.push_back("SOUNDPOWERLEVELUNIT");
        items.push_back("SOUNDPOWERUNIT");
        items.push_back("SOUNDPRESSURELEVELUNIT");
        items.push_back("SOUNDPRESSUREUNIT");
        items.push_back("SPECIFICHEATCAPACITYUNIT");
        items.push_back("TEMPERATUREGRADIENTUNIT");
        items.push_back("TEMPERATURERATEOFCHANGEUNIT");
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
        IfcDerivedUnitEnum_type = new enumeration_type(IfcSchema::Type::IfcDerivedUnitEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IfcDirectionSenseEnum_type = new enumeration_type(IfcSchema::Type::IfcDirectionSenseEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ANCHORPLATE");
        items.push_back("BRACKET");
        items.push_back("NOTDEFINED");
        items.push_back("SHOE");
        items.push_back("USERDEFINED");
        IfcDiscreteAccessoryTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcDiscreteAccessoryTypeEnum, items);
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
        IfcDistributionChamberElementTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcDistributionChamberElementTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLE");
        items.push_back("CABLECARRIER");
        items.push_back("DUCT");
        items.push_back("NOTDEFINED");
        items.push_back("PIPE");
        items.push_back("USERDEFINED");
        IfcDistributionPortTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcDistributionPortTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(44);
        items.push_back("AIRCONDITIONING");
        items.push_back("AUDIOVISUAL");
        items.push_back("CHEMICAL");
        items.push_back("CHILLEDWATER");
        items.push_back("COMMUNICATION");
        items.push_back("COMPRESSEDAIR");
        items.push_back("CONDENSERWATER");
        items.push_back("CONTROL");
        items.push_back("CONVEYING");
        items.push_back("DATA");
        items.push_back("DISPOSAL");
        items.push_back("DOMESTICCOLDWATER");
        items.push_back("DOMESTICHOTWATER");
        items.push_back("DRAINAGE");
        items.push_back("EARTHING");
        items.push_back("ELECTRICAL");
        items.push_back("ELECTROACOUSTIC");
        items.push_back("EXHAUST");
        items.push_back("FIREPROTECTION");
        items.push_back("FUEL");
        items.push_back("GAS");
        items.push_back("HAZARDOUS");
        items.push_back("HEATING");
        items.push_back("LIGHTING");
        items.push_back("LIGHTNINGPROTECTION");
        items.push_back("MUNICIPALSOLIDWASTE");
        items.push_back("NOTDEFINED");
        items.push_back("OIL");
        items.push_back("OPERATIONAL");
        items.push_back("POWERGENERATION");
        items.push_back("RAINWATER");
        items.push_back("REFRIGERATION");
        items.push_back("SECURITY");
        items.push_back("SEWAGE");
        items.push_back("SIGNAL");
        items.push_back("STORMWATER");
        items.push_back("TELEPHONE");
        items.push_back("TV");
        items.push_back("USERDEFINED");
        items.push_back("VACUUM");
        items.push_back("VENT");
        items.push_back("VENTILATION");
        items.push_back("WASTEWATER");
        items.push_back("WATERSUPPLY");
        IfcDistributionSystemEnum_type = new enumeration_type(IfcSchema::Type::IfcDistributionSystemEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IfcDocumentConfidentialityEnum_type = new enumeration_type(IfcSchema::Type::IfcDocumentConfidentialityEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IfcDocumentStatusEnum_type = new enumeration_type(IfcSchema::Type::IfcDocumentStatusEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("DOUBLE_ACTING");
        items.push_back("FIXEDPANEL");
        items.push_back("FOLDING");
        items.push_back("NOTDEFINED");
        items.push_back("REVOLVING");
        items.push_back("ROLLINGUP");
        items.push_back("SLIDING");
        items.push_back("SWINGING");
        items.push_back("USERDEFINED");
        IfcDoorPanelOperationEnum_type = new enumeration_type(IfcSchema::Type::IfcDoorPanelOperationEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IfcDoorPanelPositionEnum_type = new enumeration_type(IfcSchema::Type::IfcDoorPanelPositionEnum, items);
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
        IfcDoorStyleConstructionEnum_type = new enumeration_type(IfcSchema::Type::IfcDoorStyleConstructionEnum, items);
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
        IfcDoorStyleOperationEnum_type = new enumeration_type(IfcSchema::Type::IfcDoorStyleOperationEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DOOR");
        items.push_back("GATE");
        items.push_back("NOTDEFINED");
        items.push_back("TRAPDOOR");
        items.push_back("USERDEFINED");
        IfcDoorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcDoorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(20);
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
        items.push_back("SWING_FIXED_LEFT");
        items.push_back("SWING_FIXED_RIGHT");
        items.push_back("USERDEFINED");
        IfcDoorTypeOperationEnum_type = new enumeration_type(IfcSchema::Type::IfcDoorTypeOperationEnum, items);
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
        IfcDuctFittingTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcDuctFittingTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IfcDuctSegmentTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcDuctSegmentTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IfcDuctSilencerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcDuctSilencerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(18);
        items.push_back("DISHWASHER");
        items.push_back("ELECTRICCOOKER");
        items.push_back("FREESTANDINGELECTRICHEATER");
        items.push_back("FREESTANDINGFAN");
        items.push_back("FREESTANDINGWATERCOOLER");
        items.push_back("FREESTANDINGWATERHEATER");
        items.push_back("FREEZER");
        items.push_back("FRIDGE_FREEZER");
        items.push_back("HANDDRYER");
        items.push_back("KITCHENMACHINE");
        items.push_back("MICROWAVE");
        items.push_back("NOTDEFINED");
        items.push_back("PHOTOCOPIER");
        items.push_back("REFRIGERATOR");
        items.push_back("TUMBLEDRYER");
        items.push_back("USERDEFINED");
        items.push_back("VENDINGMACHINE");
        items.push_back("WASHINGMACHINE");
        IfcElectricApplianceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcElectricApplianceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONSUMERUNIT");
        items.push_back("DISTRIBUTIONBOARD");
        items.push_back("MOTORCONTROLCENTRE");
        items.push_back("NOTDEFINED");
        items.push_back("SWITCHBOARD");
        items.push_back("USERDEFINED");
        IfcElectricDistributionBoardTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcElectricDistributionBoardTypeEnum, items);
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
        IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcElectricFlowStorageDeviceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CHP");
        items.push_back("ENGINEGENERATOR");
        items.push_back("NOTDEFINED");
        items.push_back("STANDALONE");
        items.push_back("USERDEFINED");
        IfcElectricGeneratorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcElectricGeneratorTypeEnum, items);
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
        IfcElectricMotorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcElectricMotorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IfcElectricTimeControlTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcElectricTimeControlTypeEnum, items);
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
        IfcElementAssemblyTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcElementAssemblyTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IfcElementCompositionEnum_type = new enumeration_type(IfcSchema::Type::IfcElementCompositionEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("EXTERNALCOMBUSTION");
        items.push_back("INTERNALCOMBUSTION");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcEngineTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcEngineTypeEnum, items);
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
        IfcEvaporativeCoolerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcEvaporativeCoolerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("DIRECTEXPANSION");
        items.push_back("DIRECTEXPANSIONBRAZEDPLATE");
        items.push_back("DIRECTEXPANSIONSHELLANDTUBE");
        items.push_back("DIRECTEXPANSIONTUBEINTUBE");
        items.push_back("FLOODEDSHELLANDTUBE");
        items.push_back("NOTDEFINED");
        items.push_back("SHELLANDCOIL");
        items.push_back("USERDEFINED");
        IfcEvaporatorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcEvaporatorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EVENTCOMPLEX");
        items.push_back("EVENTMESSAGE");
        items.push_back("EVENTRULE");
        items.push_back("EVENTTIME");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcEventTriggerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcEventTriggerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ENDEVENT");
        items.push_back("INTERMEDIATEEVENT");
        items.push_back("NOTDEFINED");
        items.push_back("STARTEVENT");
        items.push_back("USERDEFINED");
        IfcEventTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcEventTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("NOTDEFIEND");
        items.push_back("USERDEFINED");
        IfcExternalSpatialElementTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcExternalSpatialElementTypeEnum, items);
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
        IfcFanTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcFanTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GLUE");
        items.push_back("MORTAR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WELD");
        IfcFastenerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcFastenerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("AIRPARTICLEFILTER");
        items.push_back("COMPRESSEDAIRFILTER");
        items.push_back("NOTDEFINED");
        items.push_back("ODORFILTER");
        items.push_back("OILFILTER");
        items.push_back("STRAINER");
        items.push_back("USERDEFINED");
        items.push_back("WATERFILTER");
        IfcFilterTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcFilterTypeEnum, items);
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
        IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcFireSuppressionTerminalTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IfcFlowDirectionEnum_type = new enumeration_type(IfcSchema::Type::IfcFlowDirectionEnum, items);
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
        IfcFlowInstrumentTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcFlowInstrumentTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ENERGYMETER");
        items.push_back("GASMETER");
        items.push_back("NOTDEFINED");
        items.push_back("OILMETER");
        items.push_back("USERDEFINED");
        items.push_back("WATERMETER");
        IfcFlowMeterTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcFlowMeterTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CAISSON_FOUNDATION");
        items.push_back("FOOTING_BEAM");
        items.push_back("NOTDEFINED");
        items.push_back("PAD_FOOTING");
        items.push_back("PILE_CAP");
        items.push_back("STRIP_FOOTING");
        items.push_back("USERDEFINED");
        IfcFootingTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcFootingTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("BED");
        items.push_back("CHAIR");
        items.push_back("DESK");
        items.push_back("FILECABINET");
        items.push_back("NOTDEFINED");
        items.push_back("SHELF");
        items.push_back("SOFA");
        items.push_back("TABLE");
        items.push_back("USERDEFINED");
        IfcFurnitureTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcFurnitureTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("TERRAIN");
        items.push_back("USERDEFINED");
        IfcGeographicElementTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcGeographicElementTypeEnum, items);
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
        IfcGeometricProjectionEnum_type = new enumeration_type(IfcSchema::Type::IfcGeometricProjectionEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IfcGlobalOrLocalEnum_type = new enumeration_type(IfcSchema::Type::IfcGlobalOrLocalEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("IRREGULAR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIAL");
        items.push_back("RECTANGULAR");
        items.push_back("TRIANGULAR");
        items.push_back("USERDEFINED");
        IfcGridTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcGridTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IfcHeatExchangerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcHeatExchangerTypeEnum, items);
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
        IfcHumidifierTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcHumidifierTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CYCLONIC");
        items.push_back("GREASE");
        items.push_back("NOTDEFINED");
        items.push_back("OIL");
        items.push_back("PETROL");
        items.push_back("USERDEFINED");
        IfcInterceptorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcInterceptorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IfcInternalOrExternalEnum_type = new enumeration_type(IfcSchema::Type::IfcInternalOrExternalEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IfcInventoryTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcInventoryTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DATA");
        items.push_back("NOTDEFINED");
        items.push_back("POWER");
        items.push_back("USERDEFINED");
        IfcJunctionBoxTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcJunctionBoxTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("PIECEWISE_BEZIER_KNOTS");
        items.push_back("QUASI_UNIFORM_KNOTS");
        items.push_back("UNIFORM_KNOTS");
        items.push_back("UNSPECIFIED");
        IfcKnotType_type = new enumeration_type(IfcSchema::Type::IfcKnotType, items);
    }
    {
        std::vector<std::string> items; items.reserve(21);
        items.push_back("ADMINISTRATION");
        items.push_back("CARPENTRY");
        items.push_back("CLEANING");
        items.push_back("CONCRETE");
        items.push_back("DRYWALL");
        items.push_back("ELECTRIC");
        items.push_back("FINISHING");
        items.push_back("FLOORING");
        items.push_back("GENERAL");
        items.push_back("HVAC");
        items.push_back("LANDSCAPING");
        items.push_back("MASONRY");
        items.push_back("NOTDEFINED");
        items.push_back("PAINTING");
        items.push_back("PAVING");
        items.push_back("PLUMBING");
        items.push_back("ROOFING");
        items.push_back("SITEGRADING");
        items.push_back("STEELWORK");
        items.push_back("SURVEYING");
        items.push_back("USERDEFINED");
        IfcLaborResourceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcLaborResourceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("COMPACTFLUORESCENT");
        items.push_back("FLUORESCENT");
        items.push_back("HALOGEN");
        items.push_back("HIGHPRESSUREMERCURY");
        items.push_back("HIGHPRESSURESODIUM");
        items.push_back("LED");
        items.push_back("METALHALIDE");
        items.push_back("NOTDEFINED");
        items.push_back("OLED");
        items.push_back("TUNGSTENFILAMENT");
        items.push_back("USERDEFINED");
        IfcLampTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcLampTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IfcLayerSetDirectionEnum_type = new enumeration_type(IfcSchema::Type::IfcLayerSetDirectionEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IfcLightDistributionCurveEnum_type = new enumeration_type(IfcSchema::Type::IfcLightDistributionCurveEnum, items);
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
        IfcLightEmissionSourceEnum_type = new enumeration_type(IfcSchema::Type::IfcLightEmissionSourceEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("SECURITYLIGHTING");
        items.push_back("USERDEFINED");
        IfcLightFixtureTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcLightFixtureTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcLoadGroupTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcLoadGroupTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALNOTAND");
        items.push_back("LOGICALNOTOR");
        items.push_back("LOGICALOR");
        items.push_back("LOGICALXOR");
        IfcLogicalOperatorEnum_type = new enumeration_type(IfcSchema::Type::IfcLogicalOperatorEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(12);
        items.push_back("ANCHORBOLT");
        items.push_back("BOLT");
        items.push_back("DOWEL");
        items.push_back("NAIL");
        items.push_back("NAILPLATE");
        items.push_back("NOTDEFINED");
        items.push_back("RIVET");
        items.push_back("SCREW");
        items.push_back("SHEARCONNECTOR");
        items.push_back("STAPLE");
        items.push_back("STUDSHEARCONNECTOR");
        items.push_back("USERDEFINED");
        IfcMechanicalFastenerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcMechanicalFastenerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("AIRSTATION");
        items.push_back("FEEDAIRUNIT");
        items.push_back("NOTDEFINED");
        items.push_back("OXYGENGENERATOR");
        items.push_back("OXYGENPLANT");
        items.push_back("USERDEFINED");
        items.push_back("VACUUMSTATION");
        IfcMedicalDeviceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcMedicalDeviceTypeEnum, items);
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
        IfcMemberTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcMemberTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcMotorConnectionTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcMotorConnectionTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IfcNullStyle_type = new enumeration_type(IfcSchema::Type::IfcNullStyle, items);
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
        IfcObjectTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcObjectTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(13);
        items.push_back("CODECOMPLIANCE");
        items.push_back("CODEWAIVER");
        items.push_back("DESIGNINTENT");
        items.push_back("EXTERNAL");
        items.push_back("HEALTHANDSAFETY");
        items.push_back("MERGECONFLICT");
        items.push_back("MODELVIEW");
        items.push_back("NOTDEFINED");
        items.push_back("PARAMETER");
        items.push_back("REQUIREMENT");
        items.push_back("SPECIFICATION");
        items.push_back("TRIGGERCONDITION");
        items.push_back("USERDEFINED");
        IfcObjectiveEnum_type = new enumeration_type(IfcSchema::Type::IfcObjectiveEnum, items);
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
        IfcOccupantTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcOccupantTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OPENING");
        items.push_back("RECESS");
        items.push_back("USERDEFINED");
        IfcOpeningElementTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcOpeningElementTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("AUDIOVISUALOUTLET");
        items.push_back("COMMUNICATIONSOUTLET");
        items.push_back("DATAOUTLET");
        items.push_back("NOTDEFINED");
        items.push_back("POWEROUTLET");
        items.push_back("TELEPHONEOUTLET");
        items.push_back("USERDEFINED");
        IfcOutletTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcOutletTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcPerformanceHistoryTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcPerformanceHistoryTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IfcPermeableCoveringOperationEnum_type = new enumeration_type(IfcSchema::Type::IfcPermeableCoveringOperationEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACCESS");
        items.push_back("BUILDING");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IfcPermitTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcPermitTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IfcPhysicalOrVirtualEnum_type = new enumeration_type(IfcSchema::Type::IfcPhysicalOrVirtualEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IfcPileConstructionEnum_type = new enumeration_type(IfcSchema::Type::IfcPileConstructionEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("BORED");
        items.push_back("COHESION");
        items.push_back("DRIVEN");
        items.push_back("FRICTION");
        items.push_back("JETGROUTING");
        items.push_back("NOTDEFINED");
        items.push_back("SUPPORT");
        items.push_back("USERDEFINED");
        IfcPileTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcPileTypeEnum, items);
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
        IfcPipeFittingTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcPipeFittingTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CULVERT");
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("GUTTER");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("SPOOL");
        items.push_back("USERDEFINED");
        IfcPipeSegmentTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcPipeSegmentTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CURTAIN_PANEL");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("USERDEFINED");
        IfcPlateTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcPlateTypeEnum, items);
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
        IfcProcedureTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcProcedureTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IfcProfileTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcProfileTypeEnum, items);
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
        IfcProjectOrderTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcProjectOrderTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IfcProjectedOrTrueLengthEnum_type = new enumeration_type(IfcSchema::Type::IfcProjectedOrTrueLengthEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcProjectionElementTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcProjectionElementTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("NOTDEFINED");
        items.push_back("PSET_OCCURRENCEDRIVEN");
        items.push_back("PSET_PERFORMANCEDRIVEN");
        items.push_back("PSET_TYPEDRIVENONLY");
        items.push_back("PSET_TYPEDRIVENOVERRIDE");
        items.push_back("QTO_OCCURRENCEDRIVEN");
        items.push_back("QTO_TYPEDRIVENONLY");
        items.push_back("QTO_TYPEDRIVENOVERRIDE");
        IfcPropertySetTemplateTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcPropertySetTemplateTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ELECTROMAGNETIC");
        items.push_back("ELECTRONIC");
        items.push_back("NOTDEFINED");
        items.push_back("RESIDUALCURRENT");
        items.push_back("THERMAL");
        items.push_back("USERDEFINED");
        IfcProtectiveDeviceTrippingUnitTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcProtectiveDeviceTrippingUnitTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("CIRCUITBREAKER");
        items.push_back("EARTHINGSWITCH");
        items.push_back("EARTHLEAKAGECIRCUITBREAKER");
        items.push_back("FUSEDISCONNECTOR");
        items.push_back("NOTDEFINED");
        items.push_back("RESIDUALCURRENTCIRCUITBREAKER");
        items.push_back("RESIDUALCURRENTSWITCH");
        items.push_back("USERDEFINED");
        items.push_back("VARISTOR");
        IfcProtectiveDeviceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcProtectiveDeviceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("CIRCULATOR");
        items.push_back("ENDSUCTION");
        items.push_back("NOTDEFINED");
        items.push_back("SPLITCASE");
        items.push_back("SUBMERSIBLEPUMP");
        items.push_back("SUMPPUMP");
        items.push_back("USERDEFINED");
        items.push_back("VERTICALINLINE");
        items.push_back("VERTICALTURBINE");
        IfcPumpTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcPumpTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcRailingTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcRailingTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IfcRampFlightTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcRampFlightTypeEnum, items);
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
        IfcRampTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcRampTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("BY_DAY_COUNT");
        items.push_back("BY_WEEKDAY_COUNT");
        items.push_back("DAILY");
        items.push_back("MONTHLY_BY_DAY_OF_MONTH");
        items.push_back("MONTHLY_BY_POSITION");
        items.push_back("WEEKLY");
        items.push_back("YEARLY_BY_DAY_OF_MONTH");
        items.push_back("YEARLY_BY_POSITION");
        IfcRecurrenceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcRecurrenceTypeEnum, items);
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
        IfcReflectanceMethodEnum_type = new enumeration_type(IfcSchema::Type::IfcReflectanceMethodEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("ANCHORING");
        items.push_back("EDGE");
        items.push_back("LIGATURE");
        items.push_back("MAIN");
        items.push_back("NOTDEFINED");
        items.push_back("PUNCHING");
        items.push_back("RING");
        items.push_back("SHEAR");
        items.push_back("STUD");
        items.push_back("USERDEFINED");
        IfcReinforcingBarRoleEnum_type = new enumeration_type(IfcSchema::Type::IfcReinforcingBarRoleEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IfcReinforcingBarSurfaceEnum_type = new enumeration_type(IfcSchema::Type::IfcReinforcingBarSurfaceEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("ANCHORING");
        items.push_back("EDGE");
        items.push_back("LIGATURE");
        items.push_back("MAIN");
        items.push_back("NOTDEFINED");
        items.push_back("PUNCHING");
        items.push_back("RING");
        items.push_back("SHEAR");
        items.push_back("STUD");
        items.push_back("USERDEFINED");
        IfcReinforcingBarTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcReinforcingBarTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcReinforcingMeshTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcReinforcingMeshTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(23);
        items.push_back("ARCHITECT");
        items.push_back("BUILDINGOPERATOR");
        items.push_back("BUILDINGOWNER");
        items.push_back("CIVILENGINEER");
        items.push_back("CLIENT");
        items.push_back("COMMISSIONINGENGINEER");
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
        IfcRoleEnum_type = new enumeration_type(IfcSchema::Type::IfcRoleEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(15);
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
        items.push_back("USERDEFINED");
        IfcRoofTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcRoofTypeEnum, items);
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
        IfcSIPrefix_type = new enumeration_type(IfcSchema::Type::IfcSIPrefix, items);
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
        IfcSIUnitName_type = new enumeration_type(IfcSchema::Type::IfcSIUnitName, items);
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
        IfcSanitaryTerminalTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSanitaryTerminalTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IfcSectionTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSectionTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(25);
        items.push_back("CO2SENSOR");
        items.push_back("CONDUCTANCESENSOR");
        items.push_back("CONTACTSENSOR");
        items.push_back("FIRESENSOR");
        items.push_back("FLOWSENSOR");
        items.push_back("FROSTSENSOR");
        items.push_back("GASSENSOR");
        items.push_back("HEATSENSOR");
        items.push_back("HUMIDITYSENSOR");
        items.push_back("IDENTIFIERSENSOR");
        items.push_back("IONCONCENTRATIONSENSOR");
        items.push_back("LEVELSENSOR");
        items.push_back("LIGHTSENSOR");
        items.push_back("MOISTURESENSOR");
        items.push_back("MOVEMENTSENSOR");
        items.push_back("NOTDEFINED");
        items.push_back("PHSENSOR");
        items.push_back("PRESSURESENSOR");
        items.push_back("RADIATIONSENSOR");
        items.push_back("RADIOACTIVITYSENSOR");
        items.push_back("SMOKESENSOR");
        items.push_back("SOUNDSENSOR");
        items.push_back("TEMPERATURESENSOR");
        items.push_back("USERDEFINED");
        items.push_back("WINDSENSOR");
        IfcSensorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSensorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        items.push_back("USERDEFINED");
        IfcSequenceEnum_type = new enumeration_type(IfcSchema::Type::IfcSequenceEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AWNING");
        items.push_back("JALOUSIE");
        items.push_back("NOTDEFINED");
        items.push_back("SHUTTER");
        items.push_back("USERDEFINED");
        IfcShadingDeviceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcShadingDeviceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(12);
        items.push_back("P_BOUNDEDVALUE");
        items.push_back("P_ENUMERATEDVALUE");
        items.push_back("P_LISTVALUE");
        items.push_back("P_REFERENCEVALUE");
        items.push_back("P_SINGLEVALUE");
        items.push_back("P_TABLEVALUE");
        items.push_back("Q_AREA");
        items.push_back("Q_COUNT");
        items.push_back("Q_LENGTH");
        items.push_back("Q_TIME");
        items.push_back("Q_VOLUME");
        items.push_back("Q_WEIGHT");
        IfcSimplePropertyTemplateTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSimplePropertyTemplateTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOF");
        items.push_back("USERDEFINED");
        IfcSlabTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSlabTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SOLARCOLLECTOR");
        items.push_back("SOLARPANEL");
        items.push_back("USERDEFINED");
        IfcSolarDeviceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSolarDeviceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONVECTOR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIATOR");
        items.push_back("USERDEFINED");
        IfcSpaceHeaterTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSpaceHeaterTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("EXTERNAL");
        items.push_back("GFA");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        items.push_back("PARKING");
        items.push_back("SPACE");
        items.push_back("USERDEFINED");
        IfcSpaceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSpaceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("CONSTRUCTION");
        items.push_back("FIRESAFETY");
        items.push_back("LIGHTING");
        items.push_back("NOTDEFINED");
        items.push_back("OCCUPANCY");
        items.push_back("SECURITY");
        items.push_back("THERMAL");
        items.push_back("TRANSPORT");
        items.push_back("USERDEFINED");
        items.push_back("VENTILATION");
        IfcSpatialZoneTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSpatialZoneTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IfcStackTerminalTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcStackTerminalTypeEnum, items);
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
        IfcStairFlightTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcStairFlightTypeEnum, items);
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
        IfcStairTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcStairTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IfcStateEnum_type = new enumeration_type(IfcSchema::Type::IfcStateEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("CONST");
        items.push_back("DISCRETE");
        items.push_back("EQUIDISTANT");
        items.push_back("LINEAR");
        items.push_back("NOTDEFINED");
        items.push_back("PARABOLA");
        items.push_back("POLYGONAL");
        items.push_back("SINUS");
        items.push_back("USERDEFINED");
        IfcStructuralCurveActivityTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcStructuralCurveActivityTypeEnum, items);
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
        IfcStructuralCurveMemberTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcStructuralCurveMemberTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BILINEAR");
        items.push_back("CONST");
        items.push_back("DISCRETE");
        items.push_back("ISOCONTOUR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcStructuralSurfaceActivityTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcStructuralSurfaceActivityTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IfcStructuralSurfaceMemberTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcStructuralSurfaceMemberTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASE");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IfcSubContractResourceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSubContractResourceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MARK");
        items.push_back("NOTDEFINED");
        items.push_back("TAG");
        items.push_back("TREATMENT");
        items.push_back("USERDEFINED");
        IfcSurfaceFeatureTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSurfaceFeatureTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IfcSurfaceSide_type = new enumeration_type(IfcSchema::Type::IfcSurfaceSide, items);
    }
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("CONTACTOR");
        items.push_back("DIMMERSWITCH");
        items.push_back("EMERGENCYSTOP");
        items.push_back("KEYPAD");
        items.push_back("MOMENTARYSWITCH");
        items.push_back("NOTDEFINED");
        items.push_back("SELECTORSWITCH");
        items.push_back("STARTER");
        items.push_back("SWITCHDISCONNECTOR");
        items.push_back("TOGGLESWITCH");
        items.push_back("USERDEFINED");
        IfcSwitchingDeviceTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSwitchingDeviceTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PANEL");
        items.push_back("USERDEFINED");
        items.push_back("WORKSURFACE");
        IfcSystemFurnitureElementTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcSystemFurnitureElementTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("BASIN");
        items.push_back("BREAKPRESSURE");
        items.push_back("EXPANSION");
        items.push_back("FEEDANDEXPANSION");
        items.push_back("NOTDEFINED");
        items.push_back("PRESSUREVESSEL");
        items.push_back("STORAGE");
        items.push_back("USERDEFINED");
        items.push_back("VESSEL");
        IfcTankTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcTankTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ELAPSEDTIME");
        items.push_back("NOTDEFINED");
        items.push_back("WORKTIME");
        IfcTaskDurationEnum_type = new enumeration_type(IfcSchema::Type::IfcTaskDurationEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(14);
        items.push_back("ATTENDANCE");
        items.push_back("CONSTRUCTION");
        items.push_back("DEMOLITION");
        items.push_back("DISMANTLE");
        items.push_back("DISPOSAL");
        items.push_back("INSTALLATION");
        items.push_back("LOGISTIC");
        items.push_back("MAINTENANCE");
        items.push_back("MOVE");
        items.push_back("NOTDEFINED");
        items.push_back("OPERATION");
        items.push_back("REMOVAL");
        items.push_back("RENOVATION");
        items.push_back("USERDEFINED");
        IfcTaskTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcTaskTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COUPLER");
        items.push_back("FIXED_END");
        items.push_back("NOTDEFINED");
        items.push_back("TENSIONING_END");
        items.push_back("USERDEFINED");
        IfcTendonAnchorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcTendonAnchorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IfcTendonTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcTendonTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IfcTextPath_type = new enumeration_type(IfcSchema::Type::IfcTextPath, items);
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
        IfcTimeSeriesDataTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcTimeSeriesDataTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CURRENT");
        items.push_back("FREQUENCY");
        items.push_back("INVERTER");
        items.push_back("NOTDEFINED");
        items.push_back("RECTIFIER");
        items.push_back("USERDEFINED");
        items.push_back("VOLTAGE");
        IfcTransformerTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcTransformerTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IfcTransitionCode_type = new enumeration_type(IfcSchema::Type::IfcTransitionCode, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CRANEWAY");
        items.push_back("ELEVATOR");
        items.push_back("ESCALATOR");
        items.push_back("LIFTINGGEAR");
        items.push_back("MOVINGWALKWAY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcTransportElementTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcTransportElementTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IfcTrimmingPreference_type = new enumeration_type(IfcSchema::Type::IfcTrimmingPreference, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcTubeBundleTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcTubeBundleTypeEnum, items);
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
        IfcUnitEnum_type = new enumeration_type(IfcSchema::Type::IfcUnitEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("ALARMPANEL");
        items.push_back("CONTROLPANEL");
        items.push_back("GASDETECTIONPANEL");
        items.push_back("HUMIDISTAT");
        items.push_back("INDICATORPANEL");
        items.push_back("MIMICPANEL");
        items.push_back("NOTDEFINED");
        items.push_back("THERMOSTAT");
        items.push_back("USERDEFINED");
        items.push_back("WEATHERSTATION");
        IfcUnitaryControlElementTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcUnitaryControlElementTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("AIRCONDITIONINGUNIT");
        items.push_back("AIRHANDLER");
        items.push_back("DEHUMIDIFIER");
        items.push_back("NOTDEFINED");
        items.push_back("ROOFTOPUNIT");
        items.push_back("SPLITSYSTEM");
        items.push_back("USERDEFINED");
        IfcUnitaryEquipmentTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcUnitaryEquipmentTypeEnum, items);
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
        IfcValveTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcValveTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IfcVibrationIsolatorTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcVibrationIsolatorTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("CHAMFER");
        items.push_back("CUTOUT");
        items.push_back("EDGE");
        items.push_back("HOLE");
        items.push_back("MITER");
        items.push_back("NOTCH");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcVoidingFeatureTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcVoidingFeatureTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("ELEMENTEDWALL");
        items.push_back("MOVABLE");
        items.push_back("NOTDEFINED");
        items.push_back("PARAPET");
        items.push_back("PARTITIONING");
        items.push_back("PLUMBINGWALL");
        items.push_back("POLYGONAL");
        items.push_back("SHEAR");
        items.push_back("SOLIDWALL");
        items.push_back("STANDARD");
        items.push_back("USERDEFINED");
        IfcWallTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcWallTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("FLOORTRAP");
        items.push_back("FLOORWASTE");
        items.push_back("GULLYSUMP");
        items.push_back("GULLYTRAP");
        items.push_back("NOTDEFINED");
        items.push_back("ROOFDRAIN");
        items.push_back("USERDEFINED");
        items.push_back("WASTEDISPOSALUNIT");
        items.push_back("WASTETRAP");
        IfcWasteTerminalTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcWasteTerminalTypeEnum, items);
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
        IfcWindowPanelOperationEnum_type = new enumeration_type(IfcSchema::Type::IfcWindowPanelOperationEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IfcWindowPanelPositionEnum_type = new enumeration_type(IfcSchema::Type::IfcWindowPanelPositionEnum, items);
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
        IfcWindowStyleConstructionEnum_type = new enumeration_type(IfcSchema::Type::IfcWindowStyleConstructionEnum, items);
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
        IfcWindowStyleOperationEnum_type = new enumeration_type(IfcSchema::Type::IfcWindowStyleOperationEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LIGHTDOME");
        items.push_back("NOTDEFINED");
        items.push_back("SKYLIGHT");
        items.push_back("USERDEFINED");
        items.push_back("WINDOW");
        IfcWindowTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcWindowTypeEnum, items);
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
        IfcWindowTypePartitioningEnum_type = new enumeration_type(IfcSchema::Type::IfcWindowTypePartitioningEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FIRSTSHIFT");
        items.push_back("NOTDEFINED");
        items.push_back("SECONDSHIFT");
        items.push_back("THIRDSHIFT");
        items.push_back("USERDEFINED");
        IfcWorkCalendarTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcWorkCalendarTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IfcWorkPlanTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcWorkPlanTypeEnum, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IfcWorkScheduleTypeEnum_type = new enumeration_type(IfcSchema::Type::IfcWorkScheduleTypeEnum, items);
    }
    IfcActorRole_type = new entity(IfcSchema::Type::IfcActorRole, 0);
    IfcAddress_type = new entity(IfcSchema::Type::IfcAddress, 0);
    IfcApplication_type = new entity(IfcSchema::Type::IfcApplication, 0);
    IfcAppliedValue_type = new entity(IfcSchema::Type::IfcAppliedValue, 0);
    IfcApproval_type = new entity(IfcSchema::Type::IfcApproval, 0);
    IfcBoundaryCondition_type = new entity(IfcSchema::Type::IfcBoundaryCondition, 0);
    IfcBoundaryEdgeCondition_type = new entity(IfcSchema::Type::IfcBoundaryEdgeCondition, IfcBoundaryCondition_type);
    IfcBoundaryFaceCondition_type = new entity(IfcSchema::Type::IfcBoundaryFaceCondition, IfcBoundaryCondition_type);
    IfcBoundaryNodeCondition_type = new entity(IfcSchema::Type::IfcBoundaryNodeCondition, IfcBoundaryCondition_type);
    IfcBoundaryNodeConditionWarping_type = new entity(IfcSchema::Type::IfcBoundaryNodeConditionWarping, IfcBoundaryNodeCondition_type);
    IfcConnectionGeometry_type = new entity(IfcSchema::Type::IfcConnectionGeometry, 0);
    IfcConnectionPointGeometry_type = new entity(IfcSchema::Type::IfcConnectionPointGeometry, IfcConnectionGeometry_type);
    IfcConnectionSurfaceGeometry_type = new entity(IfcSchema::Type::IfcConnectionSurfaceGeometry, IfcConnectionGeometry_type);
    IfcConnectionVolumeGeometry_type = new entity(IfcSchema::Type::IfcConnectionVolumeGeometry, IfcConnectionGeometry_type);
    IfcConstraint_type = new entity(IfcSchema::Type::IfcConstraint, 0);
    IfcCoordinateOperation_type = new entity(IfcSchema::Type::IfcCoordinateOperation, 0);
    IfcCoordinateReferenceSystem_type = new entity(IfcSchema::Type::IfcCoordinateReferenceSystem, 0);
    IfcCostValue_type = new entity(IfcSchema::Type::IfcCostValue, IfcAppliedValue_type);
    IfcDerivedUnit_type = new entity(IfcSchema::Type::IfcDerivedUnit, 0);
    IfcDerivedUnitElement_type = new entity(IfcSchema::Type::IfcDerivedUnitElement, 0);
    IfcDimensionalExponents_type = new entity(IfcSchema::Type::IfcDimensionalExponents, 0);
    IfcExternalInformation_type = new entity(IfcSchema::Type::IfcExternalInformation, 0);
    IfcExternalReference_type = new entity(IfcSchema::Type::IfcExternalReference, 0);
    IfcExternallyDefinedHatchStyle_type = new entity(IfcSchema::Type::IfcExternallyDefinedHatchStyle, IfcExternalReference_type);
    IfcExternallyDefinedSurfaceStyle_type = new entity(IfcSchema::Type::IfcExternallyDefinedSurfaceStyle, IfcExternalReference_type);
    IfcExternallyDefinedTextFont_type = new entity(IfcSchema::Type::IfcExternallyDefinedTextFont, IfcExternalReference_type);
    IfcGridAxis_type = new entity(IfcSchema::Type::IfcGridAxis, 0);
    IfcIrregularTimeSeriesValue_type = new entity(IfcSchema::Type::IfcIrregularTimeSeriesValue, 0);
    IfcLibraryInformation_type = new entity(IfcSchema::Type::IfcLibraryInformation, IfcExternalInformation_type);
    IfcLibraryReference_type = new entity(IfcSchema::Type::IfcLibraryReference, IfcExternalReference_type);
    IfcLightDistributionData_type = new entity(IfcSchema::Type::IfcLightDistributionData, 0);
    IfcLightIntensityDistribution_type = new entity(IfcSchema::Type::IfcLightIntensityDistribution, 0);
    IfcMapConversion_type = new entity(IfcSchema::Type::IfcMapConversion, IfcCoordinateOperation_type);
    IfcMaterialClassificationRelationship_type = new entity(IfcSchema::Type::IfcMaterialClassificationRelationship, 0);
    IfcMaterialDefinition_type = new entity(IfcSchema::Type::IfcMaterialDefinition, 0);
    IfcMaterialLayer_type = new entity(IfcSchema::Type::IfcMaterialLayer, IfcMaterialDefinition_type);
    IfcMaterialLayerSet_type = new entity(IfcSchema::Type::IfcMaterialLayerSet, IfcMaterialDefinition_type);
    IfcMaterialLayerWithOffsets_type = new entity(IfcSchema::Type::IfcMaterialLayerWithOffsets, IfcMaterialLayer_type);
    IfcMaterialList_type = new entity(IfcSchema::Type::IfcMaterialList, 0);
    IfcMaterialProfile_type = new entity(IfcSchema::Type::IfcMaterialProfile, IfcMaterialDefinition_type);
    IfcMaterialProfileSet_type = new entity(IfcSchema::Type::IfcMaterialProfileSet, IfcMaterialDefinition_type);
    IfcMaterialProfileWithOffsets_type = new entity(IfcSchema::Type::IfcMaterialProfileWithOffsets, IfcMaterialProfile_type);
    IfcMaterialUsageDefinition_type = new entity(IfcSchema::Type::IfcMaterialUsageDefinition, 0);
    IfcMeasureWithUnit_type = new entity(IfcSchema::Type::IfcMeasureWithUnit, 0);
    IfcMetric_type = new entity(IfcSchema::Type::IfcMetric, IfcConstraint_type);
    IfcMonetaryUnit_type = new entity(IfcSchema::Type::IfcMonetaryUnit, 0);
    IfcNamedUnit_type = new entity(IfcSchema::Type::IfcNamedUnit, 0);
    IfcObjectPlacement_type = new entity(IfcSchema::Type::IfcObjectPlacement, 0);
    IfcObjective_type = new entity(IfcSchema::Type::IfcObjective, IfcConstraint_type);
    IfcOrganization_type = new entity(IfcSchema::Type::IfcOrganization, 0);
    IfcOwnerHistory_type = new entity(IfcSchema::Type::IfcOwnerHistory, 0);
    IfcPerson_type = new entity(IfcSchema::Type::IfcPerson, 0);
    IfcPersonAndOrganization_type = new entity(IfcSchema::Type::IfcPersonAndOrganization, 0);
    IfcPhysicalQuantity_type = new entity(IfcSchema::Type::IfcPhysicalQuantity, 0);
    IfcPhysicalSimpleQuantity_type = new entity(IfcSchema::Type::IfcPhysicalSimpleQuantity, IfcPhysicalQuantity_type);
    IfcPostalAddress_type = new entity(IfcSchema::Type::IfcPostalAddress, IfcAddress_type);
    IfcPresentationItem_type = new entity(IfcSchema::Type::IfcPresentationItem, 0);
    IfcPresentationLayerAssignment_type = new entity(IfcSchema::Type::IfcPresentationLayerAssignment, 0);
    IfcPresentationLayerWithStyle_type = new entity(IfcSchema::Type::IfcPresentationLayerWithStyle, IfcPresentationLayerAssignment_type);
    IfcPresentationStyle_type = new entity(IfcSchema::Type::IfcPresentationStyle, 0);
    IfcPresentationStyleAssignment_type = new entity(IfcSchema::Type::IfcPresentationStyleAssignment, 0);
    IfcProductRepresentation_type = new entity(IfcSchema::Type::IfcProductRepresentation, 0);
    IfcProfileDef_type = new entity(IfcSchema::Type::IfcProfileDef, 0);
    IfcProjectedCRS_type = new entity(IfcSchema::Type::IfcProjectedCRS, IfcCoordinateReferenceSystem_type);
    IfcPropertyAbstraction_type = new entity(IfcSchema::Type::IfcPropertyAbstraction, 0);
    IfcPropertyEnumeration_type = new entity(IfcSchema::Type::IfcPropertyEnumeration, IfcPropertyAbstraction_type);
    IfcQuantityArea_type = new entity(IfcSchema::Type::IfcQuantityArea, IfcPhysicalSimpleQuantity_type);
    IfcQuantityCount_type = new entity(IfcSchema::Type::IfcQuantityCount, IfcPhysicalSimpleQuantity_type);
    IfcQuantityLength_type = new entity(IfcSchema::Type::IfcQuantityLength, IfcPhysicalSimpleQuantity_type);
    IfcQuantityTime_type = new entity(IfcSchema::Type::IfcQuantityTime, IfcPhysicalSimpleQuantity_type);
    IfcQuantityVolume_type = new entity(IfcSchema::Type::IfcQuantityVolume, IfcPhysicalSimpleQuantity_type);
    IfcQuantityWeight_type = new entity(IfcSchema::Type::IfcQuantityWeight, IfcPhysicalSimpleQuantity_type);
    IfcRecurrencePattern_type = new entity(IfcSchema::Type::IfcRecurrencePattern, 0);
    IfcReference_type = new entity(IfcSchema::Type::IfcReference, 0);
    IfcRepresentation_type = new entity(IfcSchema::Type::IfcRepresentation, 0);
    IfcRepresentationContext_type = new entity(IfcSchema::Type::IfcRepresentationContext, 0);
    IfcRepresentationItem_type = new entity(IfcSchema::Type::IfcRepresentationItem, 0);
    IfcRepresentationMap_type = new entity(IfcSchema::Type::IfcRepresentationMap, 0);
    IfcResourceLevelRelationship_type = new entity(IfcSchema::Type::IfcResourceLevelRelationship, 0);
    IfcRoot_type = new entity(IfcSchema::Type::IfcRoot, 0);
    IfcSIUnit_type = new entity(IfcSchema::Type::IfcSIUnit, IfcNamedUnit_type);
    IfcSchedulingTime_type = new entity(IfcSchema::Type::IfcSchedulingTime, 0);
    IfcShapeAspect_type = new entity(IfcSchema::Type::IfcShapeAspect, 0);
    IfcShapeModel_type = new entity(IfcSchema::Type::IfcShapeModel, IfcRepresentation_type);
    IfcShapeRepresentation_type = new entity(IfcSchema::Type::IfcShapeRepresentation, IfcShapeModel_type);
    IfcStructuralConnectionCondition_type = new entity(IfcSchema::Type::IfcStructuralConnectionCondition, 0);
    IfcStructuralLoad_type = new entity(IfcSchema::Type::IfcStructuralLoad, 0);
    IfcStructuralLoadConfiguration_type = new entity(IfcSchema::Type::IfcStructuralLoadConfiguration, IfcStructuralLoad_type);
    IfcStructuralLoadOrResult_type = new entity(IfcSchema::Type::IfcStructuralLoadOrResult, IfcStructuralLoad_type);
    IfcStructuralLoadStatic_type = new entity(IfcSchema::Type::IfcStructuralLoadStatic, IfcStructuralLoadOrResult_type);
    IfcStructuralLoadTemperature_type = new entity(IfcSchema::Type::IfcStructuralLoadTemperature, IfcStructuralLoadStatic_type);
    IfcStyleModel_type = new entity(IfcSchema::Type::IfcStyleModel, IfcRepresentation_type);
    IfcStyledItem_type = new entity(IfcSchema::Type::IfcStyledItem, IfcRepresentationItem_type);
    IfcStyledRepresentation_type = new entity(IfcSchema::Type::IfcStyledRepresentation, IfcStyleModel_type);
    IfcSurfaceReinforcementArea_type = new entity(IfcSchema::Type::IfcSurfaceReinforcementArea, IfcStructuralLoadOrResult_type);
    IfcSurfaceStyle_type = new entity(IfcSchema::Type::IfcSurfaceStyle, IfcPresentationStyle_type);
    IfcSurfaceStyleLighting_type = new entity(IfcSchema::Type::IfcSurfaceStyleLighting, IfcPresentationItem_type);
    IfcSurfaceStyleRefraction_type = new entity(IfcSchema::Type::IfcSurfaceStyleRefraction, IfcPresentationItem_type);
    IfcSurfaceStyleShading_type = new entity(IfcSchema::Type::IfcSurfaceStyleShading, IfcPresentationItem_type);
    IfcSurfaceStyleWithTextures_type = new entity(IfcSchema::Type::IfcSurfaceStyleWithTextures, IfcPresentationItem_type);
    IfcSurfaceTexture_type = new entity(IfcSchema::Type::IfcSurfaceTexture, IfcPresentationItem_type);
    IfcTable_type = new entity(IfcSchema::Type::IfcTable, 0);
    IfcTableColumn_type = new entity(IfcSchema::Type::IfcTableColumn, 0);
    IfcTableRow_type = new entity(IfcSchema::Type::IfcTableRow, 0);
    IfcTaskTime_type = new entity(IfcSchema::Type::IfcTaskTime, IfcSchedulingTime_type);
    IfcTaskTimeRecurring_type = new entity(IfcSchema::Type::IfcTaskTimeRecurring, IfcTaskTime_type);
    IfcTelecomAddress_type = new entity(IfcSchema::Type::IfcTelecomAddress, IfcAddress_type);
    IfcTextStyle_type = new entity(IfcSchema::Type::IfcTextStyle, IfcPresentationStyle_type);
    IfcTextStyleForDefinedFont_type = new entity(IfcSchema::Type::IfcTextStyleForDefinedFont, IfcPresentationItem_type);
    IfcTextStyleTextModel_type = new entity(IfcSchema::Type::IfcTextStyleTextModel, IfcPresentationItem_type);
    IfcTextureCoordinate_type = new entity(IfcSchema::Type::IfcTextureCoordinate, IfcPresentationItem_type);
    IfcTextureCoordinateGenerator_type = new entity(IfcSchema::Type::IfcTextureCoordinateGenerator, IfcTextureCoordinate_type);
    IfcTextureMap_type = new entity(IfcSchema::Type::IfcTextureMap, IfcTextureCoordinate_type);
    IfcTextureVertex_type = new entity(IfcSchema::Type::IfcTextureVertex, IfcPresentationItem_type);
    IfcTextureVertexList_type = new entity(IfcSchema::Type::IfcTextureVertexList, IfcPresentationItem_type);
    IfcTimePeriod_type = new entity(IfcSchema::Type::IfcTimePeriod, 0);
    IfcTimeSeries_type = new entity(IfcSchema::Type::IfcTimeSeries, 0);
    IfcTimeSeriesValue_type = new entity(IfcSchema::Type::IfcTimeSeriesValue, 0);
    IfcTopologicalRepresentationItem_type = new entity(IfcSchema::Type::IfcTopologicalRepresentationItem, IfcRepresentationItem_type);
    IfcTopologyRepresentation_type = new entity(IfcSchema::Type::IfcTopologyRepresentation, IfcShapeModel_type);
    IfcUnitAssignment_type = new entity(IfcSchema::Type::IfcUnitAssignment, 0);
    IfcVertex_type = new entity(IfcSchema::Type::IfcVertex, IfcTopologicalRepresentationItem_type);
    IfcVertexPoint_type = new entity(IfcSchema::Type::IfcVertexPoint, IfcVertex_type);
    IfcVirtualGridIntersection_type = new entity(IfcSchema::Type::IfcVirtualGridIntersection, 0);
    IfcWorkTime_type = new entity(IfcSchema::Type::IfcWorkTime, IfcSchedulingTime_type);
    IfcApprovalRelationship_type = new entity(IfcSchema::Type::IfcApprovalRelationship, IfcResourceLevelRelationship_type);
    IfcArbitraryClosedProfileDef_type = new entity(IfcSchema::Type::IfcArbitraryClosedProfileDef, IfcProfileDef_type);
    IfcArbitraryOpenProfileDef_type = new entity(IfcSchema::Type::IfcArbitraryOpenProfileDef, IfcProfileDef_type);
    IfcArbitraryProfileDefWithVoids_type = new entity(IfcSchema::Type::IfcArbitraryProfileDefWithVoids, IfcArbitraryClosedProfileDef_type);
    IfcBlobTexture_type = new entity(IfcSchema::Type::IfcBlobTexture, IfcSurfaceTexture_type);
    IfcCenterLineProfileDef_type = new entity(IfcSchema::Type::IfcCenterLineProfileDef, IfcArbitraryOpenProfileDef_type);
    IfcClassification_type = new entity(IfcSchema::Type::IfcClassification, IfcExternalInformation_type);
    IfcClassificationReference_type = new entity(IfcSchema::Type::IfcClassificationReference, IfcExternalReference_type);
    IfcColourRgbList_type = new entity(IfcSchema::Type::IfcColourRgbList, IfcPresentationItem_type);
    IfcColourSpecification_type = new entity(IfcSchema::Type::IfcColourSpecification, IfcPresentationItem_type);
    IfcCompositeProfileDef_type = new entity(IfcSchema::Type::IfcCompositeProfileDef, IfcProfileDef_type);
    IfcConnectedFaceSet_type = new entity(IfcSchema::Type::IfcConnectedFaceSet, IfcTopologicalRepresentationItem_type);
    IfcConnectionCurveGeometry_type = new entity(IfcSchema::Type::IfcConnectionCurveGeometry, IfcConnectionGeometry_type);
    IfcConnectionPointEccentricity_type = new entity(IfcSchema::Type::IfcConnectionPointEccentricity, IfcConnectionPointGeometry_type);
    IfcContextDependentUnit_type = new entity(IfcSchema::Type::IfcContextDependentUnit, IfcNamedUnit_type);
    IfcConversionBasedUnit_type = new entity(IfcSchema::Type::IfcConversionBasedUnit, IfcNamedUnit_type);
    IfcConversionBasedUnitWithOffset_type = new entity(IfcSchema::Type::IfcConversionBasedUnitWithOffset, IfcConversionBasedUnit_type);
    IfcCurrencyRelationship_type = new entity(IfcSchema::Type::IfcCurrencyRelationship, IfcResourceLevelRelationship_type);
    IfcCurveStyle_type = new entity(IfcSchema::Type::IfcCurveStyle, IfcPresentationStyle_type);
    IfcCurveStyleFont_type = new entity(IfcSchema::Type::IfcCurveStyleFont, IfcPresentationItem_type);
    IfcCurveStyleFontAndScaling_type = new entity(IfcSchema::Type::IfcCurveStyleFontAndScaling, IfcPresentationItem_type);
    IfcCurveStyleFontPattern_type = new entity(IfcSchema::Type::IfcCurveStyleFontPattern, IfcPresentationItem_type);
    IfcDerivedProfileDef_type = new entity(IfcSchema::Type::IfcDerivedProfileDef, IfcProfileDef_type);
    IfcDocumentInformation_type = new entity(IfcSchema::Type::IfcDocumentInformation, IfcExternalInformation_type);
    IfcDocumentInformationRelationship_type = new entity(IfcSchema::Type::IfcDocumentInformationRelationship, IfcResourceLevelRelationship_type);
    IfcDocumentReference_type = new entity(IfcSchema::Type::IfcDocumentReference, IfcExternalReference_type);
    IfcEdge_type = new entity(IfcSchema::Type::IfcEdge, IfcTopologicalRepresentationItem_type);
    IfcEdgeCurve_type = new entity(IfcSchema::Type::IfcEdgeCurve, IfcEdge_type);
    IfcEventTime_type = new entity(IfcSchema::Type::IfcEventTime, IfcSchedulingTime_type);
    IfcExtendedProperties_type = new entity(IfcSchema::Type::IfcExtendedProperties, IfcPropertyAbstraction_type);
    IfcExternalReferenceRelationship_type = new entity(IfcSchema::Type::IfcExternalReferenceRelationship, IfcResourceLevelRelationship_type);
    IfcFace_type = new entity(IfcSchema::Type::IfcFace, IfcTopologicalRepresentationItem_type);
    IfcFaceBound_type = new entity(IfcSchema::Type::IfcFaceBound, IfcTopologicalRepresentationItem_type);
    IfcFaceOuterBound_type = new entity(IfcSchema::Type::IfcFaceOuterBound, IfcFaceBound_type);
    IfcFaceSurface_type = new entity(IfcSchema::Type::IfcFaceSurface, IfcFace_type);
    IfcFailureConnectionCondition_type = new entity(IfcSchema::Type::IfcFailureConnectionCondition, IfcStructuralConnectionCondition_type);
    IfcFillAreaStyle_type = new entity(IfcSchema::Type::IfcFillAreaStyle, IfcPresentationStyle_type);
    IfcGeometricRepresentationContext_type = new entity(IfcSchema::Type::IfcGeometricRepresentationContext, IfcRepresentationContext_type);
    IfcGeometricRepresentationItem_type = new entity(IfcSchema::Type::IfcGeometricRepresentationItem, IfcRepresentationItem_type);
    IfcGeometricRepresentationSubContext_type = new entity(IfcSchema::Type::IfcGeometricRepresentationSubContext, IfcGeometricRepresentationContext_type);
    IfcGeometricSet_type = new entity(IfcSchema::Type::IfcGeometricSet, IfcGeometricRepresentationItem_type);
    IfcGridPlacement_type = new entity(IfcSchema::Type::IfcGridPlacement, IfcObjectPlacement_type);
    IfcHalfSpaceSolid_type = new entity(IfcSchema::Type::IfcHalfSpaceSolid, IfcGeometricRepresentationItem_type);
    IfcImageTexture_type = new entity(IfcSchema::Type::IfcImageTexture, IfcSurfaceTexture_type);
    IfcIndexedColourMap_type = new entity(IfcSchema::Type::IfcIndexedColourMap, IfcPresentationItem_type);
    IfcIndexedTextureMap_type = new entity(IfcSchema::Type::IfcIndexedTextureMap, IfcTextureCoordinate_type);
    IfcIndexedTriangleTextureMap_type = new entity(IfcSchema::Type::IfcIndexedTriangleTextureMap, IfcIndexedTextureMap_type);
    IfcIrregularTimeSeries_type = new entity(IfcSchema::Type::IfcIrregularTimeSeries, IfcTimeSeries_type);
    IfcLagTime_type = new entity(IfcSchema::Type::IfcLagTime, IfcSchedulingTime_type);
    IfcLightSource_type = new entity(IfcSchema::Type::IfcLightSource, IfcGeometricRepresentationItem_type);
    IfcLightSourceAmbient_type = new entity(IfcSchema::Type::IfcLightSourceAmbient, IfcLightSource_type);
    IfcLightSourceDirectional_type = new entity(IfcSchema::Type::IfcLightSourceDirectional, IfcLightSource_type);
    IfcLightSourceGoniometric_type = new entity(IfcSchema::Type::IfcLightSourceGoniometric, IfcLightSource_type);
    IfcLightSourcePositional_type = new entity(IfcSchema::Type::IfcLightSourcePositional, IfcLightSource_type);
    IfcLightSourceSpot_type = new entity(IfcSchema::Type::IfcLightSourceSpot, IfcLightSourcePositional_type);
    IfcLocalPlacement_type = new entity(IfcSchema::Type::IfcLocalPlacement, IfcObjectPlacement_type);
    IfcLoop_type = new entity(IfcSchema::Type::IfcLoop, IfcTopologicalRepresentationItem_type);
    IfcMappedItem_type = new entity(IfcSchema::Type::IfcMappedItem, IfcRepresentationItem_type);
    IfcMaterial_type = new entity(IfcSchema::Type::IfcMaterial, IfcMaterialDefinition_type);
    IfcMaterialConstituent_type = new entity(IfcSchema::Type::IfcMaterialConstituent, IfcMaterialDefinition_type);
    IfcMaterialConstituentSet_type = new entity(IfcSchema::Type::IfcMaterialConstituentSet, IfcMaterialDefinition_type);
    IfcMaterialDefinitionRepresentation_type = new entity(IfcSchema::Type::IfcMaterialDefinitionRepresentation, IfcProductRepresentation_type);
    IfcMaterialLayerSetUsage_type = new entity(IfcSchema::Type::IfcMaterialLayerSetUsage, IfcMaterialUsageDefinition_type);
    IfcMaterialProfileSetUsage_type = new entity(IfcSchema::Type::IfcMaterialProfileSetUsage, IfcMaterialUsageDefinition_type);
    IfcMaterialProfileSetUsageTapering_type = new entity(IfcSchema::Type::IfcMaterialProfileSetUsageTapering, IfcMaterialProfileSetUsage_type);
    IfcMaterialProperties_type = new entity(IfcSchema::Type::IfcMaterialProperties, IfcExtendedProperties_type);
    IfcMaterialRelationship_type = new entity(IfcSchema::Type::IfcMaterialRelationship, IfcResourceLevelRelationship_type);
    IfcMirroredProfileDef_type = new entity(IfcSchema::Type::IfcMirroredProfileDef, IfcDerivedProfileDef_type);
    IfcObjectDefinition_type = new entity(IfcSchema::Type::IfcObjectDefinition, IfcRoot_type);
    IfcOpenShell_type = new entity(IfcSchema::Type::IfcOpenShell, IfcConnectedFaceSet_type);
    IfcOrganizationRelationship_type = new entity(IfcSchema::Type::IfcOrganizationRelationship, IfcResourceLevelRelationship_type);
    IfcOrientedEdge_type = new entity(IfcSchema::Type::IfcOrientedEdge, IfcEdge_type);
    IfcParameterizedProfileDef_type = new entity(IfcSchema::Type::IfcParameterizedProfileDef, IfcProfileDef_type);
    IfcPath_type = new entity(IfcSchema::Type::IfcPath, IfcTopologicalRepresentationItem_type);
    IfcPhysicalComplexQuantity_type = new entity(IfcSchema::Type::IfcPhysicalComplexQuantity, IfcPhysicalQuantity_type);
    IfcPixelTexture_type = new entity(IfcSchema::Type::IfcPixelTexture, IfcSurfaceTexture_type);
    IfcPlacement_type = new entity(IfcSchema::Type::IfcPlacement, IfcGeometricRepresentationItem_type);
    IfcPlanarExtent_type = new entity(IfcSchema::Type::IfcPlanarExtent, IfcGeometricRepresentationItem_type);
    IfcPoint_type = new entity(IfcSchema::Type::IfcPoint, IfcGeometricRepresentationItem_type);
    IfcPointOnCurve_type = new entity(IfcSchema::Type::IfcPointOnCurve, IfcPoint_type);
    IfcPointOnSurface_type = new entity(IfcSchema::Type::IfcPointOnSurface, IfcPoint_type);
    IfcPolyLoop_type = new entity(IfcSchema::Type::IfcPolyLoop, IfcLoop_type);
    IfcPolygonalBoundedHalfSpace_type = new entity(IfcSchema::Type::IfcPolygonalBoundedHalfSpace, IfcHalfSpaceSolid_type);
    IfcPreDefinedItem_type = new entity(IfcSchema::Type::IfcPreDefinedItem, IfcPresentationItem_type);
    IfcPreDefinedProperties_type = new entity(IfcSchema::Type::IfcPreDefinedProperties, IfcPropertyAbstraction_type);
    IfcPreDefinedTextFont_type = new entity(IfcSchema::Type::IfcPreDefinedTextFont, IfcPreDefinedItem_type);
    IfcProductDefinitionShape_type = new entity(IfcSchema::Type::IfcProductDefinitionShape, IfcProductRepresentation_type);
    IfcProfileProperties_type = new entity(IfcSchema::Type::IfcProfileProperties, IfcExtendedProperties_type);
    IfcProperty_type = new entity(IfcSchema::Type::IfcProperty, IfcPropertyAbstraction_type);
    IfcPropertyDefinition_type = new entity(IfcSchema::Type::IfcPropertyDefinition, IfcRoot_type);
    IfcPropertyDependencyRelationship_type = new entity(IfcSchema::Type::IfcPropertyDependencyRelationship, IfcResourceLevelRelationship_type);
    IfcPropertySetDefinition_type = new entity(IfcSchema::Type::IfcPropertySetDefinition, IfcPropertyDefinition_type);
    IfcPropertyTemplateDefinition_type = new entity(IfcSchema::Type::IfcPropertyTemplateDefinition, IfcPropertyDefinition_type);
    IfcQuantitySet_type = new entity(IfcSchema::Type::IfcQuantitySet, IfcPropertySetDefinition_type);
    IfcRectangleProfileDef_type = new entity(IfcSchema::Type::IfcRectangleProfileDef, IfcParameterizedProfileDef_type);
    IfcRegularTimeSeries_type = new entity(IfcSchema::Type::IfcRegularTimeSeries, IfcTimeSeries_type);
    IfcReinforcementBarProperties_type = new entity(IfcSchema::Type::IfcReinforcementBarProperties, IfcPreDefinedProperties_type);
    IfcRelationship_type = new entity(IfcSchema::Type::IfcRelationship, IfcRoot_type);
    IfcResourceApprovalRelationship_type = new entity(IfcSchema::Type::IfcResourceApprovalRelationship, IfcResourceLevelRelationship_type);
    IfcResourceConstraintRelationship_type = new entity(IfcSchema::Type::IfcResourceConstraintRelationship, IfcResourceLevelRelationship_type);
    IfcResourceTime_type = new entity(IfcSchema::Type::IfcResourceTime, IfcSchedulingTime_type);
    IfcRoundedRectangleProfileDef_type = new entity(IfcSchema::Type::IfcRoundedRectangleProfileDef, IfcRectangleProfileDef_type);
    IfcSectionProperties_type = new entity(IfcSchema::Type::IfcSectionProperties, IfcPreDefinedProperties_type);
    IfcSectionReinforcementProperties_type = new entity(IfcSchema::Type::IfcSectionReinforcementProperties, IfcPreDefinedProperties_type);
    IfcSectionedSpine_type = new entity(IfcSchema::Type::IfcSectionedSpine, IfcGeometricRepresentationItem_type);
    IfcShellBasedSurfaceModel_type = new entity(IfcSchema::Type::IfcShellBasedSurfaceModel, IfcGeometricRepresentationItem_type);
    IfcSimpleProperty_type = new entity(IfcSchema::Type::IfcSimpleProperty, IfcProperty_type);
    IfcSlippageConnectionCondition_type = new entity(IfcSchema::Type::IfcSlippageConnectionCondition, IfcStructuralConnectionCondition_type);
    IfcSolidModel_type = new entity(IfcSchema::Type::IfcSolidModel, IfcGeometricRepresentationItem_type);
    IfcStructuralLoadLinearForce_type = new entity(IfcSchema::Type::IfcStructuralLoadLinearForce, IfcStructuralLoadStatic_type);
    IfcStructuralLoadPlanarForce_type = new entity(IfcSchema::Type::IfcStructuralLoadPlanarForce, IfcStructuralLoadStatic_type);
    IfcStructuralLoadSingleDisplacement_type = new entity(IfcSchema::Type::IfcStructuralLoadSingleDisplacement, IfcStructuralLoadStatic_type);
    IfcStructuralLoadSingleDisplacementDistortion_type = new entity(IfcSchema::Type::IfcStructuralLoadSingleDisplacementDistortion, IfcStructuralLoadSingleDisplacement_type);
    IfcStructuralLoadSingleForce_type = new entity(IfcSchema::Type::IfcStructuralLoadSingleForce, IfcStructuralLoadStatic_type);
    IfcStructuralLoadSingleForceWarping_type = new entity(IfcSchema::Type::IfcStructuralLoadSingleForceWarping, IfcStructuralLoadSingleForce_type);
    IfcSubedge_type = new entity(IfcSchema::Type::IfcSubedge, IfcEdge_type);
    IfcSurface_type = new entity(IfcSchema::Type::IfcSurface, IfcGeometricRepresentationItem_type);
    IfcSurfaceStyleRendering_type = new entity(IfcSchema::Type::IfcSurfaceStyleRendering, IfcSurfaceStyleShading_type);
    IfcSweptAreaSolid_type = new entity(IfcSchema::Type::IfcSweptAreaSolid, IfcSolidModel_type);
    IfcSweptDiskSolid_type = new entity(IfcSchema::Type::IfcSweptDiskSolid, IfcSolidModel_type);
    IfcSweptDiskSolidPolygonal_type = new entity(IfcSchema::Type::IfcSweptDiskSolidPolygonal, IfcSweptDiskSolid_type);
    IfcSweptSurface_type = new entity(IfcSchema::Type::IfcSweptSurface, IfcSurface_type);
    IfcTShapeProfileDef_type = new entity(IfcSchema::Type::IfcTShapeProfileDef, IfcParameterizedProfileDef_type);
    IfcTessellatedItem_type = new entity(IfcSchema::Type::IfcTessellatedItem, IfcGeometricRepresentationItem_type);
    IfcTextLiteral_type = new entity(IfcSchema::Type::IfcTextLiteral, IfcGeometricRepresentationItem_type);
    IfcTextLiteralWithExtent_type = new entity(IfcSchema::Type::IfcTextLiteralWithExtent, IfcTextLiteral_type);
    IfcTextStyleFontModel_type = new entity(IfcSchema::Type::IfcTextStyleFontModel, IfcPreDefinedTextFont_type);
    IfcTrapeziumProfileDef_type = new entity(IfcSchema::Type::IfcTrapeziumProfileDef, IfcParameterizedProfileDef_type);
    IfcTypeObject_type = new entity(IfcSchema::Type::IfcTypeObject, IfcObjectDefinition_type);
    IfcTypeProcess_type = new entity(IfcSchema::Type::IfcTypeProcess, IfcTypeObject_type);
    IfcTypeProduct_type = new entity(IfcSchema::Type::IfcTypeProduct, IfcTypeObject_type);
    IfcTypeResource_type = new entity(IfcSchema::Type::IfcTypeResource, IfcTypeObject_type);
    IfcUShapeProfileDef_type = new entity(IfcSchema::Type::IfcUShapeProfileDef, IfcParameterizedProfileDef_type);
    IfcVector_type = new entity(IfcSchema::Type::IfcVector, IfcGeometricRepresentationItem_type);
    IfcVertexLoop_type = new entity(IfcSchema::Type::IfcVertexLoop, IfcLoop_type);
    IfcWindowStyle_type = new entity(IfcSchema::Type::IfcWindowStyle, IfcTypeProduct_type);
    IfcZShapeProfileDef_type = new entity(IfcSchema::Type::IfcZShapeProfileDef, IfcParameterizedProfileDef_type);
    IfcAdvancedFace_type = new entity(IfcSchema::Type::IfcAdvancedFace, IfcFaceSurface_type);
    IfcAnnotationFillArea_type = new entity(IfcSchema::Type::IfcAnnotationFillArea, IfcGeometricRepresentationItem_type);
    IfcAsymmetricIShapeProfileDef_type = new entity(IfcSchema::Type::IfcAsymmetricIShapeProfileDef, IfcParameterizedProfileDef_type);
    IfcAxis1Placement_type = new entity(IfcSchema::Type::IfcAxis1Placement, IfcPlacement_type);
    IfcAxis2Placement2D_type = new entity(IfcSchema::Type::IfcAxis2Placement2D, IfcPlacement_type);
    IfcAxis2Placement3D_type = new entity(IfcSchema::Type::IfcAxis2Placement3D, IfcPlacement_type);
    IfcBooleanResult_type = new entity(IfcSchema::Type::IfcBooleanResult, IfcGeometricRepresentationItem_type);
    IfcBoundedSurface_type = new entity(IfcSchema::Type::IfcBoundedSurface, IfcSurface_type);
    IfcBoundingBox_type = new entity(IfcSchema::Type::IfcBoundingBox, IfcGeometricRepresentationItem_type);
    IfcBoxedHalfSpace_type = new entity(IfcSchema::Type::IfcBoxedHalfSpace, IfcHalfSpaceSolid_type);
    IfcCShapeProfileDef_type = new entity(IfcSchema::Type::IfcCShapeProfileDef, IfcParameterizedProfileDef_type);
    IfcCartesianPoint_type = new entity(IfcSchema::Type::IfcCartesianPoint, IfcPoint_type);
    IfcCartesianPointList_type = new entity(IfcSchema::Type::IfcCartesianPointList, IfcGeometricRepresentationItem_type);
    IfcCartesianPointList2D_type = new entity(IfcSchema::Type::IfcCartesianPointList2D, IfcCartesianPointList_type);
    IfcCartesianPointList3D_type = new entity(IfcSchema::Type::IfcCartesianPointList3D, IfcCartesianPointList_type);
    IfcCartesianTransformationOperator_type = new entity(IfcSchema::Type::IfcCartesianTransformationOperator, IfcGeometricRepresentationItem_type);
    IfcCartesianTransformationOperator2D_type = new entity(IfcSchema::Type::IfcCartesianTransformationOperator2D, IfcCartesianTransformationOperator_type);
    IfcCartesianTransformationOperator2DnonUniform_type = new entity(IfcSchema::Type::IfcCartesianTransformationOperator2DnonUniform, IfcCartesianTransformationOperator2D_type);
    IfcCartesianTransformationOperator3D_type = new entity(IfcSchema::Type::IfcCartesianTransformationOperator3D, IfcCartesianTransformationOperator_type);
    IfcCartesianTransformationOperator3DnonUniform_type = new entity(IfcSchema::Type::IfcCartesianTransformationOperator3DnonUniform, IfcCartesianTransformationOperator3D_type);
    IfcCircleProfileDef_type = new entity(IfcSchema::Type::IfcCircleProfileDef, IfcParameterizedProfileDef_type);
    IfcClosedShell_type = new entity(IfcSchema::Type::IfcClosedShell, IfcConnectedFaceSet_type);
    IfcColourRgb_type = new entity(IfcSchema::Type::IfcColourRgb, IfcColourSpecification_type);
    IfcComplexProperty_type = new entity(IfcSchema::Type::IfcComplexProperty, IfcProperty_type);
    IfcCompositeCurveSegment_type = new entity(IfcSchema::Type::IfcCompositeCurveSegment, IfcGeometricRepresentationItem_type);
    IfcConstructionResourceType_type = new entity(IfcSchema::Type::IfcConstructionResourceType, IfcTypeResource_type);
    IfcContext_type = new entity(IfcSchema::Type::IfcContext, IfcObjectDefinition_type);
    IfcCrewResourceType_type = new entity(IfcSchema::Type::IfcCrewResourceType, IfcConstructionResourceType_type);
    IfcCsgPrimitive3D_type = new entity(IfcSchema::Type::IfcCsgPrimitive3D, IfcGeometricRepresentationItem_type);
    IfcCsgSolid_type = new entity(IfcSchema::Type::IfcCsgSolid, IfcSolidModel_type);
    IfcCurve_type = new entity(IfcSchema::Type::IfcCurve, IfcGeometricRepresentationItem_type);
    IfcCurveBoundedPlane_type = new entity(IfcSchema::Type::IfcCurveBoundedPlane, IfcBoundedSurface_type);
    IfcCurveBoundedSurface_type = new entity(IfcSchema::Type::IfcCurveBoundedSurface, IfcBoundedSurface_type);
    IfcDirection_type = new entity(IfcSchema::Type::IfcDirection, IfcGeometricRepresentationItem_type);
    IfcDoorStyle_type = new entity(IfcSchema::Type::IfcDoorStyle, IfcTypeProduct_type);
    IfcEdgeLoop_type = new entity(IfcSchema::Type::IfcEdgeLoop, IfcLoop_type);
    IfcElementQuantity_type = new entity(IfcSchema::Type::IfcElementQuantity, IfcQuantitySet_type);
    IfcElementType_type = new entity(IfcSchema::Type::IfcElementType, IfcTypeProduct_type);
    IfcElementarySurface_type = new entity(IfcSchema::Type::IfcElementarySurface, IfcSurface_type);
    IfcEllipseProfileDef_type = new entity(IfcSchema::Type::IfcEllipseProfileDef, IfcParameterizedProfileDef_type);
    IfcEventType_type = new entity(IfcSchema::Type::IfcEventType, IfcTypeProcess_type);
    IfcExtrudedAreaSolid_type = new entity(IfcSchema::Type::IfcExtrudedAreaSolid, IfcSweptAreaSolid_type);
    IfcExtrudedAreaSolidTapered_type = new entity(IfcSchema::Type::IfcExtrudedAreaSolidTapered, IfcExtrudedAreaSolid_type);
    IfcFaceBasedSurfaceModel_type = new entity(IfcSchema::Type::IfcFaceBasedSurfaceModel, IfcGeometricRepresentationItem_type);
    IfcFillAreaStyleHatching_type = new entity(IfcSchema::Type::IfcFillAreaStyleHatching, IfcGeometricRepresentationItem_type);
    IfcFillAreaStyleTiles_type = new entity(IfcSchema::Type::IfcFillAreaStyleTiles, IfcGeometricRepresentationItem_type);
    IfcFixedReferenceSweptAreaSolid_type = new entity(IfcSchema::Type::IfcFixedReferenceSweptAreaSolid, IfcSweptAreaSolid_type);
    IfcFurnishingElementType_type = new entity(IfcSchema::Type::IfcFurnishingElementType, IfcElementType_type);
    IfcFurnitureType_type = new entity(IfcSchema::Type::IfcFurnitureType, IfcFurnishingElementType_type);
    IfcGeographicElementType_type = new entity(IfcSchema::Type::IfcGeographicElementType, IfcElementType_type);
    IfcGeometricCurveSet_type = new entity(IfcSchema::Type::IfcGeometricCurveSet, IfcGeometricSet_type);
    IfcIShapeProfileDef_type = new entity(IfcSchema::Type::IfcIShapeProfileDef, IfcParameterizedProfileDef_type);
    IfcLShapeProfileDef_type = new entity(IfcSchema::Type::IfcLShapeProfileDef, IfcParameterizedProfileDef_type);
    IfcLaborResourceType_type = new entity(IfcSchema::Type::IfcLaborResourceType, IfcConstructionResourceType_type);
    IfcLine_type = new entity(IfcSchema::Type::IfcLine, IfcCurve_type);
    IfcManifoldSolidBrep_type = new entity(IfcSchema::Type::IfcManifoldSolidBrep, IfcSolidModel_type);
    IfcObject_type = new entity(IfcSchema::Type::IfcObject, IfcObjectDefinition_type);
    IfcOffsetCurve2D_type = new entity(IfcSchema::Type::IfcOffsetCurve2D, IfcCurve_type);
    IfcOffsetCurve3D_type = new entity(IfcSchema::Type::IfcOffsetCurve3D, IfcCurve_type);
    IfcPcurve_type = new entity(IfcSchema::Type::IfcPcurve, IfcCurve_type);
    IfcPlanarBox_type = new entity(IfcSchema::Type::IfcPlanarBox, IfcPlanarExtent_type);
    IfcPlane_type = new entity(IfcSchema::Type::IfcPlane, IfcElementarySurface_type);
    IfcPreDefinedColour_type = new entity(IfcSchema::Type::IfcPreDefinedColour, IfcPreDefinedItem_type);
    IfcPreDefinedCurveFont_type = new entity(IfcSchema::Type::IfcPreDefinedCurveFont, IfcPreDefinedItem_type);
    IfcPreDefinedPropertySet_type = new entity(IfcSchema::Type::IfcPreDefinedPropertySet, IfcPropertySetDefinition_type);
    IfcProcedureType_type = new entity(IfcSchema::Type::IfcProcedureType, IfcTypeProcess_type);
    IfcProcess_type = new entity(IfcSchema::Type::IfcProcess, IfcObject_type);
    IfcProduct_type = new entity(IfcSchema::Type::IfcProduct, IfcObject_type);
    IfcProject_type = new entity(IfcSchema::Type::IfcProject, IfcContext_type);
    IfcProjectLibrary_type = new entity(IfcSchema::Type::IfcProjectLibrary, IfcContext_type);
    IfcPropertyBoundedValue_type = new entity(IfcSchema::Type::IfcPropertyBoundedValue, IfcSimpleProperty_type);
    IfcPropertyEnumeratedValue_type = new entity(IfcSchema::Type::IfcPropertyEnumeratedValue, IfcSimpleProperty_type);
    IfcPropertyListValue_type = new entity(IfcSchema::Type::IfcPropertyListValue, IfcSimpleProperty_type);
    IfcPropertyReferenceValue_type = new entity(IfcSchema::Type::IfcPropertyReferenceValue, IfcSimpleProperty_type);
    IfcPropertySet_type = new entity(IfcSchema::Type::IfcPropertySet, IfcPropertySetDefinition_type);
    IfcPropertySetTemplate_type = new entity(IfcSchema::Type::IfcPropertySetTemplate, IfcPropertyTemplateDefinition_type);
    IfcPropertySingleValue_type = new entity(IfcSchema::Type::IfcPropertySingleValue, IfcSimpleProperty_type);
    IfcPropertyTableValue_type = new entity(IfcSchema::Type::IfcPropertyTableValue, IfcSimpleProperty_type);
    IfcPropertyTemplate_type = new entity(IfcSchema::Type::IfcPropertyTemplate, IfcPropertyTemplateDefinition_type);
    IfcProxy_type = new entity(IfcSchema::Type::IfcProxy, IfcProduct_type);
    IfcRectangleHollowProfileDef_type = new entity(IfcSchema::Type::IfcRectangleHollowProfileDef, IfcRectangleProfileDef_type);
    IfcRectangularPyramid_type = new entity(IfcSchema::Type::IfcRectangularPyramid, IfcCsgPrimitive3D_type);
    IfcRectangularTrimmedSurface_type = new entity(IfcSchema::Type::IfcRectangularTrimmedSurface, IfcBoundedSurface_type);
    IfcReinforcementDefinitionProperties_type = new entity(IfcSchema::Type::IfcReinforcementDefinitionProperties, IfcPreDefinedPropertySet_type);
    IfcRelAssigns_type = new entity(IfcSchema::Type::IfcRelAssigns, IfcRelationship_type);
    IfcRelAssignsToActor_type = new entity(IfcSchema::Type::IfcRelAssignsToActor, IfcRelAssigns_type);
    IfcRelAssignsToControl_type = new entity(IfcSchema::Type::IfcRelAssignsToControl, IfcRelAssigns_type);
    IfcRelAssignsToGroup_type = new entity(IfcSchema::Type::IfcRelAssignsToGroup, IfcRelAssigns_type);
    IfcRelAssignsToGroupByFactor_type = new entity(IfcSchema::Type::IfcRelAssignsToGroupByFactor, IfcRelAssignsToGroup_type);
    IfcRelAssignsToProcess_type = new entity(IfcSchema::Type::IfcRelAssignsToProcess, IfcRelAssigns_type);
    IfcRelAssignsToProduct_type = new entity(IfcSchema::Type::IfcRelAssignsToProduct, IfcRelAssigns_type);
    IfcRelAssignsToResource_type = new entity(IfcSchema::Type::IfcRelAssignsToResource, IfcRelAssigns_type);
    IfcRelAssociates_type = new entity(IfcSchema::Type::IfcRelAssociates, IfcRelationship_type);
    IfcRelAssociatesApproval_type = new entity(IfcSchema::Type::IfcRelAssociatesApproval, IfcRelAssociates_type);
    IfcRelAssociatesClassification_type = new entity(IfcSchema::Type::IfcRelAssociatesClassification, IfcRelAssociates_type);
    IfcRelAssociatesConstraint_type = new entity(IfcSchema::Type::IfcRelAssociatesConstraint, IfcRelAssociates_type);
    IfcRelAssociatesDocument_type = new entity(IfcSchema::Type::IfcRelAssociatesDocument, IfcRelAssociates_type);
    IfcRelAssociatesLibrary_type = new entity(IfcSchema::Type::IfcRelAssociatesLibrary, IfcRelAssociates_type);
    IfcRelAssociatesMaterial_type = new entity(IfcSchema::Type::IfcRelAssociatesMaterial, IfcRelAssociates_type);
    IfcRelConnects_type = new entity(IfcSchema::Type::IfcRelConnects, IfcRelationship_type);
    IfcRelConnectsElements_type = new entity(IfcSchema::Type::IfcRelConnectsElements, IfcRelConnects_type);
    IfcRelConnectsPathElements_type = new entity(IfcSchema::Type::IfcRelConnectsPathElements, IfcRelConnectsElements_type);
    IfcRelConnectsPortToElement_type = new entity(IfcSchema::Type::IfcRelConnectsPortToElement, IfcRelConnects_type);
    IfcRelConnectsPorts_type = new entity(IfcSchema::Type::IfcRelConnectsPorts, IfcRelConnects_type);
    IfcRelConnectsStructuralActivity_type = new entity(IfcSchema::Type::IfcRelConnectsStructuralActivity, IfcRelConnects_type);
    IfcRelConnectsStructuralMember_type = new entity(IfcSchema::Type::IfcRelConnectsStructuralMember, IfcRelConnects_type);
    IfcRelConnectsWithEccentricity_type = new entity(IfcSchema::Type::IfcRelConnectsWithEccentricity, IfcRelConnectsStructuralMember_type);
    IfcRelConnectsWithRealizingElements_type = new entity(IfcSchema::Type::IfcRelConnectsWithRealizingElements, IfcRelConnectsElements_type);
    IfcRelContainedInSpatialStructure_type = new entity(IfcSchema::Type::IfcRelContainedInSpatialStructure, IfcRelConnects_type);
    IfcRelCoversBldgElements_type = new entity(IfcSchema::Type::IfcRelCoversBldgElements, IfcRelConnects_type);
    IfcRelCoversSpaces_type = new entity(IfcSchema::Type::IfcRelCoversSpaces, IfcRelConnects_type);
    IfcRelDeclares_type = new entity(IfcSchema::Type::IfcRelDeclares, IfcRelationship_type);
    IfcRelDecomposes_type = new entity(IfcSchema::Type::IfcRelDecomposes, IfcRelationship_type);
    IfcRelDefines_type = new entity(IfcSchema::Type::IfcRelDefines, IfcRelationship_type);
    IfcRelDefinesByObject_type = new entity(IfcSchema::Type::IfcRelDefinesByObject, IfcRelDefines_type);
    IfcRelDefinesByProperties_type = new entity(IfcSchema::Type::IfcRelDefinesByProperties, IfcRelDefines_type);
    IfcRelDefinesByTemplate_type = new entity(IfcSchema::Type::IfcRelDefinesByTemplate, IfcRelDefines_type);
    IfcRelDefinesByType_type = new entity(IfcSchema::Type::IfcRelDefinesByType, IfcRelDefines_type);
    IfcRelFillsElement_type = new entity(IfcSchema::Type::IfcRelFillsElement, IfcRelConnects_type);
    IfcRelFlowControlElements_type = new entity(IfcSchema::Type::IfcRelFlowControlElements, IfcRelConnects_type);
    IfcRelInterferesElements_type = new entity(IfcSchema::Type::IfcRelInterferesElements, IfcRelConnects_type);
    IfcRelNests_type = new entity(IfcSchema::Type::IfcRelNests, IfcRelDecomposes_type);
    IfcRelProjectsElement_type = new entity(IfcSchema::Type::IfcRelProjectsElement, IfcRelDecomposes_type);
    IfcRelReferencedInSpatialStructure_type = new entity(IfcSchema::Type::IfcRelReferencedInSpatialStructure, IfcRelConnects_type);
    IfcRelSequence_type = new entity(IfcSchema::Type::IfcRelSequence, IfcRelConnects_type);
    IfcRelServicesBuildings_type = new entity(IfcSchema::Type::IfcRelServicesBuildings, IfcRelConnects_type);
    IfcRelSpaceBoundary_type = new entity(IfcSchema::Type::IfcRelSpaceBoundary, IfcRelConnects_type);
    IfcRelSpaceBoundary1stLevel_type = new entity(IfcSchema::Type::IfcRelSpaceBoundary1stLevel, IfcRelSpaceBoundary_type);
    IfcRelSpaceBoundary2ndLevel_type = new entity(IfcSchema::Type::IfcRelSpaceBoundary2ndLevel, IfcRelSpaceBoundary1stLevel_type);
    IfcRelVoidsElement_type = new entity(IfcSchema::Type::IfcRelVoidsElement, IfcRelDecomposes_type);
    IfcReparametrisedCompositeCurveSegment_type = new entity(IfcSchema::Type::IfcReparametrisedCompositeCurveSegment, IfcCompositeCurveSegment_type);
    IfcResource_type = new entity(IfcSchema::Type::IfcResource, IfcObject_type);
    IfcRevolvedAreaSolid_type = new entity(IfcSchema::Type::IfcRevolvedAreaSolid, IfcSweptAreaSolid_type);
    IfcRevolvedAreaSolidTapered_type = new entity(IfcSchema::Type::IfcRevolvedAreaSolidTapered, IfcRevolvedAreaSolid_type);
    IfcRightCircularCone_type = new entity(IfcSchema::Type::IfcRightCircularCone, IfcCsgPrimitive3D_type);
    IfcRightCircularCylinder_type = new entity(IfcSchema::Type::IfcRightCircularCylinder, IfcCsgPrimitive3D_type);
    IfcSimplePropertyTemplate_type = new entity(IfcSchema::Type::IfcSimplePropertyTemplate, IfcPropertyTemplate_type);
    IfcSpatialElement_type = new entity(IfcSchema::Type::IfcSpatialElement, IfcProduct_type);
    IfcSpatialElementType_type = new entity(IfcSchema::Type::IfcSpatialElementType, IfcTypeProduct_type);
    IfcSpatialStructureElement_type = new entity(IfcSchema::Type::IfcSpatialStructureElement, IfcSpatialElement_type);
    IfcSpatialStructureElementType_type = new entity(IfcSchema::Type::IfcSpatialStructureElementType, IfcSpatialElementType_type);
    IfcSpatialZone_type = new entity(IfcSchema::Type::IfcSpatialZone, IfcSpatialElement_type);
    IfcSpatialZoneType_type = new entity(IfcSchema::Type::IfcSpatialZoneType, IfcSpatialElementType_type);
    IfcSphere_type = new entity(IfcSchema::Type::IfcSphere, IfcCsgPrimitive3D_type);
    IfcStructuralActivity_type = new entity(IfcSchema::Type::IfcStructuralActivity, IfcProduct_type);
    IfcStructuralItem_type = new entity(IfcSchema::Type::IfcStructuralItem, IfcProduct_type);
    IfcStructuralMember_type = new entity(IfcSchema::Type::IfcStructuralMember, IfcStructuralItem_type);
    IfcStructuralReaction_type = new entity(IfcSchema::Type::IfcStructuralReaction, IfcStructuralActivity_type);
    IfcStructuralSurfaceMember_type = new entity(IfcSchema::Type::IfcStructuralSurfaceMember, IfcStructuralMember_type);
    IfcStructuralSurfaceMemberVarying_type = new entity(IfcSchema::Type::IfcStructuralSurfaceMemberVarying, IfcStructuralSurfaceMember_type);
    IfcStructuralSurfaceReaction_type = new entity(IfcSchema::Type::IfcStructuralSurfaceReaction, IfcStructuralReaction_type);
    IfcSubContractResourceType_type = new entity(IfcSchema::Type::IfcSubContractResourceType, IfcConstructionResourceType_type);
    IfcSurfaceCurveSweptAreaSolid_type = new entity(IfcSchema::Type::IfcSurfaceCurveSweptAreaSolid, IfcSweptAreaSolid_type);
    IfcSurfaceOfLinearExtrusion_type = new entity(IfcSchema::Type::IfcSurfaceOfLinearExtrusion, IfcSweptSurface_type);
    IfcSurfaceOfRevolution_type = new entity(IfcSchema::Type::IfcSurfaceOfRevolution, IfcSweptSurface_type);
    IfcSystemFurnitureElementType_type = new entity(IfcSchema::Type::IfcSystemFurnitureElementType, IfcFurnishingElementType_type);
    IfcTask_type = new entity(IfcSchema::Type::IfcTask, IfcProcess_type);
    IfcTaskType_type = new entity(IfcSchema::Type::IfcTaskType, IfcTypeProcess_type);
    IfcTessellatedFaceSet_type = new entity(IfcSchema::Type::IfcTessellatedFaceSet, IfcTessellatedItem_type);
    IfcTransportElementType_type = new entity(IfcSchema::Type::IfcTransportElementType, IfcElementType_type);
    IfcTriangulatedFaceSet_type = new entity(IfcSchema::Type::IfcTriangulatedFaceSet, IfcTessellatedFaceSet_type);
    IfcWindowLiningProperties_type = new entity(IfcSchema::Type::IfcWindowLiningProperties, IfcPreDefinedPropertySet_type);
    IfcWindowPanelProperties_type = new entity(IfcSchema::Type::IfcWindowPanelProperties, IfcPreDefinedPropertySet_type);
    IfcActor_type = new entity(IfcSchema::Type::IfcActor, IfcObject_type);
    IfcAdvancedBrep_type = new entity(IfcSchema::Type::IfcAdvancedBrep, IfcManifoldSolidBrep_type);
    IfcAdvancedBrepWithVoids_type = new entity(IfcSchema::Type::IfcAdvancedBrepWithVoids, IfcAdvancedBrep_type);
    IfcAnnotation_type = new entity(IfcSchema::Type::IfcAnnotation, IfcProduct_type);
    IfcBSplineSurface_type = new entity(IfcSchema::Type::IfcBSplineSurface, IfcBoundedSurface_type);
    IfcBSplineSurfaceWithKnots_type = new entity(IfcSchema::Type::IfcBSplineSurfaceWithKnots, IfcBSplineSurface_type);
    IfcBlock_type = new entity(IfcSchema::Type::IfcBlock, IfcCsgPrimitive3D_type);
    IfcBooleanClippingResult_type = new entity(IfcSchema::Type::IfcBooleanClippingResult, IfcBooleanResult_type);
    IfcBoundedCurve_type = new entity(IfcSchema::Type::IfcBoundedCurve, IfcCurve_type);
    IfcBuilding_type = new entity(IfcSchema::Type::IfcBuilding, IfcSpatialStructureElement_type);
    IfcBuildingElementType_type = new entity(IfcSchema::Type::IfcBuildingElementType, IfcElementType_type);
    IfcBuildingStorey_type = new entity(IfcSchema::Type::IfcBuildingStorey, IfcSpatialStructureElement_type);
    IfcChimneyType_type = new entity(IfcSchema::Type::IfcChimneyType, IfcBuildingElementType_type);
    IfcCircleHollowProfileDef_type = new entity(IfcSchema::Type::IfcCircleHollowProfileDef, IfcCircleProfileDef_type);
    IfcCivilElementType_type = new entity(IfcSchema::Type::IfcCivilElementType, IfcElementType_type);
    IfcColumnType_type = new entity(IfcSchema::Type::IfcColumnType, IfcBuildingElementType_type);
    IfcComplexPropertyTemplate_type = new entity(IfcSchema::Type::IfcComplexPropertyTemplate, IfcPropertyTemplate_type);
    IfcCompositeCurve_type = new entity(IfcSchema::Type::IfcCompositeCurve, IfcBoundedCurve_type);
    IfcCompositeCurveOnSurface_type = new entity(IfcSchema::Type::IfcCompositeCurveOnSurface, IfcCompositeCurve_type);
    IfcConic_type = new entity(IfcSchema::Type::IfcConic, IfcCurve_type);
    IfcConstructionEquipmentResourceType_type = new entity(IfcSchema::Type::IfcConstructionEquipmentResourceType, IfcConstructionResourceType_type);
    IfcConstructionMaterialResourceType_type = new entity(IfcSchema::Type::IfcConstructionMaterialResourceType, IfcConstructionResourceType_type);
    IfcConstructionProductResourceType_type = new entity(IfcSchema::Type::IfcConstructionProductResourceType, IfcConstructionResourceType_type);
    IfcConstructionResource_type = new entity(IfcSchema::Type::IfcConstructionResource, IfcResource_type);
    IfcControl_type = new entity(IfcSchema::Type::IfcControl, IfcObject_type);
    IfcCostItem_type = new entity(IfcSchema::Type::IfcCostItem, IfcControl_type);
    IfcCostSchedule_type = new entity(IfcSchema::Type::IfcCostSchedule, IfcControl_type);
    IfcCoveringType_type = new entity(IfcSchema::Type::IfcCoveringType, IfcBuildingElementType_type);
    IfcCrewResource_type = new entity(IfcSchema::Type::IfcCrewResource, IfcConstructionResource_type);
    IfcCurtainWallType_type = new entity(IfcSchema::Type::IfcCurtainWallType, IfcBuildingElementType_type);
    IfcCylindricalSurface_type = new entity(IfcSchema::Type::IfcCylindricalSurface, IfcElementarySurface_type);
    IfcDistributionElementType_type = new entity(IfcSchema::Type::IfcDistributionElementType, IfcElementType_type);
    IfcDistributionFlowElementType_type = new entity(IfcSchema::Type::IfcDistributionFlowElementType, IfcDistributionElementType_type);
    IfcDoorLiningProperties_type = new entity(IfcSchema::Type::IfcDoorLiningProperties, IfcPreDefinedPropertySet_type);
    IfcDoorPanelProperties_type = new entity(IfcSchema::Type::IfcDoorPanelProperties, IfcPreDefinedPropertySet_type);
    IfcDoorType_type = new entity(IfcSchema::Type::IfcDoorType, IfcBuildingElementType_type);
    IfcDraughtingPreDefinedColour_type = new entity(IfcSchema::Type::IfcDraughtingPreDefinedColour, IfcPreDefinedColour_type);
    IfcDraughtingPreDefinedCurveFont_type = new entity(IfcSchema::Type::IfcDraughtingPreDefinedCurveFont, IfcPreDefinedCurveFont_type);
    IfcElement_type = new entity(IfcSchema::Type::IfcElement, IfcProduct_type);
    IfcElementAssembly_type = new entity(IfcSchema::Type::IfcElementAssembly, IfcElement_type);
    IfcElementAssemblyType_type = new entity(IfcSchema::Type::IfcElementAssemblyType, IfcElementType_type);
    IfcElementComponent_type = new entity(IfcSchema::Type::IfcElementComponent, IfcElement_type);
    IfcElementComponentType_type = new entity(IfcSchema::Type::IfcElementComponentType, IfcElementType_type);
    IfcEllipse_type = new entity(IfcSchema::Type::IfcEllipse, IfcConic_type);
    IfcEnergyConversionDeviceType_type = new entity(IfcSchema::Type::IfcEnergyConversionDeviceType, IfcDistributionFlowElementType_type);
    IfcEngineType_type = new entity(IfcSchema::Type::IfcEngineType, IfcEnergyConversionDeviceType_type);
    IfcEvaporativeCoolerType_type = new entity(IfcSchema::Type::IfcEvaporativeCoolerType, IfcEnergyConversionDeviceType_type);
    IfcEvaporatorType_type = new entity(IfcSchema::Type::IfcEvaporatorType, IfcEnergyConversionDeviceType_type);
    IfcEvent_type = new entity(IfcSchema::Type::IfcEvent, IfcProcess_type);
    IfcExternalSpatialStructureElement_type = new entity(IfcSchema::Type::IfcExternalSpatialStructureElement, IfcSpatialElement_type);
    IfcFacetedBrep_type = new entity(IfcSchema::Type::IfcFacetedBrep, IfcManifoldSolidBrep_type);
    IfcFacetedBrepWithVoids_type = new entity(IfcSchema::Type::IfcFacetedBrepWithVoids, IfcFacetedBrep_type);
    IfcFastener_type = new entity(IfcSchema::Type::IfcFastener, IfcElementComponent_type);
    IfcFastenerType_type = new entity(IfcSchema::Type::IfcFastenerType, IfcElementComponentType_type);
    IfcFeatureElement_type = new entity(IfcSchema::Type::IfcFeatureElement, IfcElement_type);
    IfcFeatureElementAddition_type = new entity(IfcSchema::Type::IfcFeatureElementAddition, IfcFeatureElement_type);
    IfcFeatureElementSubtraction_type = new entity(IfcSchema::Type::IfcFeatureElementSubtraction, IfcFeatureElement_type);
    IfcFlowControllerType_type = new entity(IfcSchema::Type::IfcFlowControllerType, IfcDistributionFlowElementType_type);
    IfcFlowFittingType_type = new entity(IfcSchema::Type::IfcFlowFittingType, IfcDistributionFlowElementType_type);
    IfcFlowMeterType_type = new entity(IfcSchema::Type::IfcFlowMeterType, IfcFlowControllerType_type);
    IfcFlowMovingDeviceType_type = new entity(IfcSchema::Type::IfcFlowMovingDeviceType, IfcDistributionFlowElementType_type);
    IfcFlowSegmentType_type = new entity(IfcSchema::Type::IfcFlowSegmentType, IfcDistributionFlowElementType_type);
    IfcFlowStorageDeviceType_type = new entity(IfcSchema::Type::IfcFlowStorageDeviceType, IfcDistributionFlowElementType_type);
    IfcFlowTerminalType_type = new entity(IfcSchema::Type::IfcFlowTerminalType, IfcDistributionFlowElementType_type);
    IfcFlowTreatmentDeviceType_type = new entity(IfcSchema::Type::IfcFlowTreatmentDeviceType, IfcDistributionFlowElementType_type);
    IfcFootingType_type = new entity(IfcSchema::Type::IfcFootingType, IfcBuildingElementType_type);
    IfcFurnishingElement_type = new entity(IfcSchema::Type::IfcFurnishingElement, IfcElement_type);
    IfcFurniture_type = new entity(IfcSchema::Type::IfcFurniture, IfcFurnishingElement_type);
    IfcGeographicElement_type = new entity(IfcSchema::Type::IfcGeographicElement, IfcElement_type);
    IfcGrid_type = new entity(IfcSchema::Type::IfcGrid, IfcProduct_type);
    IfcGroup_type = new entity(IfcSchema::Type::IfcGroup, IfcObject_type);
    IfcHeatExchangerType_type = new entity(IfcSchema::Type::IfcHeatExchangerType, IfcEnergyConversionDeviceType_type);
    IfcHumidifierType_type = new entity(IfcSchema::Type::IfcHumidifierType, IfcEnergyConversionDeviceType_type);
    IfcIndexedPolyCurve_type = new entity(IfcSchema::Type::IfcIndexedPolyCurve, IfcBoundedCurve_type);
    IfcInterceptorType_type = new entity(IfcSchema::Type::IfcInterceptorType, IfcFlowTreatmentDeviceType_type);
    IfcInventory_type = new entity(IfcSchema::Type::IfcInventory, IfcGroup_type);
    IfcJunctionBoxType_type = new entity(IfcSchema::Type::IfcJunctionBoxType, IfcFlowFittingType_type);
    IfcLaborResource_type = new entity(IfcSchema::Type::IfcLaborResource, IfcConstructionResource_type);
    IfcLampType_type = new entity(IfcSchema::Type::IfcLampType, IfcFlowTerminalType_type);
    IfcLightFixtureType_type = new entity(IfcSchema::Type::IfcLightFixtureType, IfcFlowTerminalType_type);
    IfcMechanicalFastener_type = new entity(IfcSchema::Type::IfcMechanicalFastener, IfcElementComponent_type);
    IfcMechanicalFastenerType_type = new entity(IfcSchema::Type::IfcMechanicalFastenerType, IfcElementComponentType_type);
    IfcMedicalDeviceType_type = new entity(IfcSchema::Type::IfcMedicalDeviceType, IfcFlowTerminalType_type);
    IfcMemberType_type = new entity(IfcSchema::Type::IfcMemberType, IfcBuildingElementType_type);
    IfcMotorConnectionType_type = new entity(IfcSchema::Type::IfcMotorConnectionType, IfcEnergyConversionDeviceType_type);
    IfcOccupant_type = new entity(IfcSchema::Type::IfcOccupant, IfcActor_type);
    IfcOpeningElement_type = new entity(IfcSchema::Type::IfcOpeningElement, IfcFeatureElementSubtraction_type);
    IfcOpeningStandardCase_type = new entity(IfcSchema::Type::IfcOpeningStandardCase, IfcOpeningElement_type);
    IfcOutletType_type = new entity(IfcSchema::Type::IfcOutletType, IfcFlowTerminalType_type);
    IfcPerformanceHistory_type = new entity(IfcSchema::Type::IfcPerformanceHistory, IfcControl_type);
    IfcPermeableCoveringProperties_type = new entity(IfcSchema::Type::IfcPermeableCoveringProperties, IfcPreDefinedPropertySet_type);
    IfcPermit_type = new entity(IfcSchema::Type::IfcPermit, IfcControl_type);
    IfcPileType_type = new entity(IfcSchema::Type::IfcPileType, IfcBuildingElementType_type);
    IfcPipeFittingType_type = new entity(IfcSchema::Type::IfcPipeFittingType, IfcFlowFittingType_type);
    IfcPipeSegmentType_type = new entity(IfcSchema::Type::IfcPipeSegmentType, IfcFlowSegmentType_type);
    IfcPlateType_type = new entity(IfcSchema::Type::IfcPlateType, IfcBuildingElementType_type);
    IfcPolyline_type = new entity(IfcSchema::Type::IfcPolyline, IfcBoundedCurve_type);
    IfcPort_type = new entity(IfcSchema::Type::IfcPort, IfcProduct_type);
    IfcProcedure_type = new entity(IfcSchema::Type::IfcProcedure, IfcProcess_type);
    IfcProjectOrder_type = new entity(IfcSchema::Type::IfcProjectOrder, IfcControl_type);
    IfcProjectionElement_type = new entity(IfcSchema::Type::IfcProjectionElement, IfcFeatureElementAddition_type);
    IfcProtectiveDeviceType_type = new entity(IfcSchema::Type::IfcProtectiveDeviceType, IfcFlowControllerType_type);
    IfcPumpType_type = new entity(IfcSchema::Type::IfcPumpType, IfcFlowMovingDeviceType_type);
    IfcRailingType_type = new entity(IfcSchema::Type::IfcRailingType, IfcBuildingElementType_type);
    IfcRampFlightType_type = new entity(IfcSchema::Type::IfcRampFlightType, IfcBuildingElementType_type);
    IfcRampType_type = new entity(IfcSchema::Type::IfcRampType, IfcBuildingElementType_type);
    IfcRationalBSplineSurfaceWithKnots_type = new entity(IfcSchema::Type::IfcRationalBSplineSurfaceWithKnots, IfcBSplineSurfaceWithKnots_type);
    IfcReinforcingElement_type = new entity(IfcSchema::Type::IfcReinforcingElement, IfcElementComponent_type);
    IfcReinforcingElementType_type = new entity(IfcSchema::Type::IfcReinforcingElementType, IfcElementComponentType_type);
    IfcReinforcingMesh_type = new entity(IfcSchema::Type::IfcReinforcingMesh, IfcReinforcingElement_type);
    IfcReinforcingMeshType_type = new entity(IfcSchema::Type::IfcReinforcingMeshType, IfcReinforcingElementType_type);
    IfcRelAggregates_type = new entity(IfcSchema::Type::IfcRelAggregates, IfcRelDecomposes_type);
    IfcRoofType_type = new entity(IfcSchema::Type::IfcRoofType, IfcBuildingElementType_type);
    IfcSanitaryTerminalType_type = new entity(IfcSchema::Type::IfcSanitaryTerminalType, IfcFlowTerminalType_type);
    IfcShadingDeviceType_type = new entity(IfcSchema::Type::IfcShadingDeviceType, IfcBuildingElementType_type);
    IfcSite_type = new entity(IfcSchema::Type::IfcSite, IfcSpatialStructureElement_type);
    IfcSlabType_type = new entity(IfcSchema::Type::IfcSlabType, IfcBuildingElementType_type);
    IfcSolarDeviceType_type = new entity(IfcSchema::Type::IfcSolarDeviceType, IfcEnergyConversionDeviceType_type);
    IfcSpace_type = new entity(IfcSchema::Type::IfcSpace, IfcSpatialStructureElement_type);
    IfcSpaceHeaterType_type = new entity(IfcSchema::Type::IfcSpaceHeaterType, IfcFlowTerminalType_type);
    IfcSpaceType_type = new entity(IfcSchema::Type::IfcSpaceType, IfcSpatialStructureElementType_type);
    IfcStackTerminalType_type = new entity(IfcSchema::Type::IfcStackTerminalType, IfcFlowTerminalType_type);
    IfcStairFlightType_type = new entity(IfcSchema::Type::IfcStairFlightType, IfcBuildingElementType_type);
    IfcStairType_type = new entity(IfcSchema::Type::IfcStairType, IfcBuildingElementType_type);
    IfcStructuralAction_type = new entity(IfcSchema::Type::IfcStructuralAction, IfcStructuralActivity_type);
    IfcStructuralConnection_type = new entity(IfcSchema::Type::IfcStructuralConnection, IfcStructuralItem_type);
    IfcStructuralCurveAction_type = new entity(IfcSchema::Type::IfcStructuralCurveAction, IfcStructuralAction_type);
    IfcStructuralCurveConnection_type = new entity(IfcSchema::Type::IfcStructuralCurveConnection, IfcStructuralConnection_type);
    IfcStructuralCurveMember_type = new entity(IfcSchema::Type::IfcStructuralCurveMember, IfcStructuralMember_type);
    IfcStructuralCurveMemberVarying_type = new entity(IfcSchema::Type::IfcStructuralCurveMemberVarying, IfcStructuralCurveMember_type);
    IfcStructuralCurveReaction_type = new entity(IfcSchema::Type::IfcStructuralCurveReaction, IfcStructuralReaction_type);
    IfcStructuralLinearAction_type = new entity(IfcSchema::Type::IfcStructuralLinearAction, IfcStructuralCurveAction_type);
    IfcStructuralLoadGroup_type = new entity(IfcSchema::Type::IfcStructuralLoadGroup, IfcGroup_type);
    IfcStructuralPointAction_type = new entity(IfcSchema::Type::IfcStructuralPointAction, IfcStructuralAction_type);
    IfcStructuralPointConnection_type = new entity(IfcSchema::Type::IfcStructuralPointConnection, IfcStructuralConnection_type);
    IfcStructuralPointReaction_type = new entity(IfcSchema::Type::IfcStructuralPointReaction, IfcStructuralReaction_type);
    IfcStructuralResultGroup_type = new entity(IfcSchema::Type::IfcStructuralResultGroup, IfcGroup_type);
    IfcStructuralSurfaceAction_type = new entity(IfcSchema::Type::IfcStructuralSurfaceAction, IfcStructuralAction_type);
    IfcStructuralSurfaceConnection_type = new entity(IfcSchema::Type::IfcStructuralSurfaceConnection, IfcStructuralConnection_type);
    IfcSubContractResource_type = new entity(IfcSchema::Type::IfcSubContractResource, IfcConstructionResource_type);
    IfcSurfaceFeature_type = new entity(IfcSchema::Type::IfcSurfaceFeature, IfcFeatureElement_type);
    IfcSwitchingDeviceType_type = new entity(IfcSchema::Type::IfcSwitchingDeviceType, IfcFlowControllerType_type);
    IfcSystem_type = new entity(IfcSchema::Type::IfcSystem, IfcGroup_type);
    IfcSystemFurnitureElement_type = new entity(IfcSchema::Type::IfcSystemFurnitureElement, IfcFurnishingElement_type);
    IfcTankType_type = new entity(IfcSchema::Type::IfcTankType, IfcFlowStorageDeviceType_type);
    IfcTendon_type = new entity(IfcSchema::Type::IfcTendon, IfcReinforcingElement_type);
    IfcTendonAnchor_type = new entity(IfcSchema::Type::IfcTendonAnchor, IfcReinforcingElement_type);
    IfcTendonAnchorType_type = new entity(IfcSchema::Type::IfcTendonAnchorType, IfcReinforcingElementType_type);
    IfcTendonType_type = new entity(IfcSchema::Type::IfcTendonType, IfcReinforcingElementType_type);
    IfcTransformerType_type = new entity(IfcSchema::Type::IfcTransformerType, IfcEnergyConversionDeviceType_type);
    IfcTransportElement_type = new entity(IfcSchema::Type::IfcTransportElement, IfcElement_type);
    IfcTrimmedCurve_type = new entity(IfcSchema::Type::IfcTrimmedCurve, IfcBoundedCurve_type);
    IfcTubeBundleType_type = new entity(IfcSchema::Type::IfcTubeBundleType, IfcEnergyConversionDeviceType_type);
    IfcUnitaryEquipmentType_type = new entity(IfcSchema::Type::IfcUnitaryEquipmentType, IfcEnergyConversionDeviceType_type);
    IfcValveType_type = new entity(IfcSchema::Type::IfcValveType, IfcFlowControllerType_type);
    IfcVibrationIsolator_type = new entity(IfcSchema::Type::IfcVibrationIsolator, IfcElementComponent_type);
    IfcVibrationIsolatorType_type = new entity(IfcSchema::Type::IfcVibrationIsolatorType, IfcElementComponentType_type);
    IfcVirtualElement_type = new entity(IfcSchema::Type::IfcVirtualElement, IfcElement_type);
    IfcVoidingFeature_type = new entity(IfcSchema::Type::IfcVoidingFeature, IfcFeatureElementSubtraction_type);
    IfcWallType_type = new entity(IfcSchema::Type::IfcWallType, IfcBuildingElementType_type);
    IfcWasteTerminalType_type = new entity(IfcSchema::Type::IfcWasteTerminalType, IfcFlowTerminalType_type);
    IfcWindowType_type = new entity(IfcSchema::Type::IfcWindowType, IfcBuildingElementType_type);
    IfcWorkCalendar_type = new entity(IfcSchema::Type::IfcWorkCalendar, IfcControl_type);
    IfcWorkControl_type = new entity(IfcSchema::Type::IfcWorkControl, IfcControl_type);
    IfcWorkPlan_type = new entity(IfcSchema::Type::IfcWorkPlan, IfcWorkControl_type);
    IfcWorkSchedule_type = new entity(IfcSchema::Type::IfcWorkSchedule, IfcWorkControl_type);
    IfcZone_type = new entity(IfcSchema::Type::IfcZone, IfcSystem_type);
    IfcActionRequest_type = new entity(IfcSchema::Type::IfcActionRequest, IfcControl_type);
    IfcAirTerminalBoxType_type = new entity(IfcSchema::Type::IfcAirTerminalBoxType, IfcFlowControllerType_type);
    IfcAirTerminalType_type = new entity(IfcSchema::Type::IfcAirTerminalType, IfcFlowTerminalType_type);
    IfcAirToAirHeatRecoveryType_type = new entity(IfcSchema::Type::IfcAirToAirHeatRecoveryType, IfcEnergyConversionDeviceType_type);
    IfcAsset_type = new entity(IfcSchema::Type::IfcAsset, IfcGroup_type);
    IfcAudioVisualApplianceType_type = new entity(IfcSchema::Type::IfcAudioVisualApplianceType, IfcFlowTerminalType_type);
    IfcBSplineCurve_type = new entity(IfcSchema::Type::IfcBSplineCurve, IfcBoundedCurve_type);
    IfcBSplineCurveWithKnots_type = new entity(IfcSchema::Type::IfcBSplineCurveWithKnots, IfcBSplineCurve_type);
    IfcBeamType_type = new entity(IfcSchema::Type::IfcBeamType, IfcBuildingElementType_type);
    IfcBoilerType_type = new entity(IfcSchema::Type::IfcBoilerType, IfcEnergyConversionDeviceType_type);
    IfcBoundaryCurve_type = new entity(IfcSchema::Type::IfcBoundaryCurve, IfcCompositeCurveOnSurface_type);
    IfcBuildingElement_type = new entity(IfcSchema::Type::IfcBuildingElement, IfcElement_type);
    IfcBuildingElementPart_type = new entity(IfcSchema::Type::IfcBuildingElementPart, IfcElementComponent_type);
    IfcBuildingElementPartType_type = new entity(IfcSchema::Type::IfcBuildingElementPartType, IfcElementComponentType_type);
    IfcBuildingElementProxy_type = new entity(IfcSchema::Type::IfcBuildingElementProxy, IfcBuildingElement_type);
    IfcBuildingElementProxyType_type = new entity(IfcSchema::Type::IfcBuildingElementProxyType, IfcBuildingElementType_type);
    IfcBuildingSystem_type = new entity(IfcSchema::Type::IfcBuildingSystem, IfcSystem_type);
    IfcBurnerType_type = new entity(IfcSchema::Type::IfcBurnerType, IfcEnergyConversionDeviceType_type);
    IfcCableCarrierFittingType_type = new entity(IfcSchema::Type::IfcCableCarrierFittingType, IfcFlowFittingType_type);
    IfcCableCarrierSegmentType_type = new entity(IfcSchema::Type::IfcCableCarrierSegmentType, IfcFlowSegmentType_type);
    IfcCableFittingType_type = new entity(IfcSchema::Type::IfcCableFittingType, IfcFlowFittingType_type);
    IfcCableSegmentType_type = new entity(IfcSchema::Type::IfcCableSegmentType, IfcFlowSegmentType_type);
    IfcChillerType_type = new entity(IfcSchema::Type::IfcChillerType, IfcEnergyConversionDeviceType_type);
    IfcChimney_type = new entity(IfcSchema::Type::IfcChimney, IfcBuildingElement_type);
    IfcCircle_type = new entity(IfcSchema::Type::IfcCircle, IfcConic_type);
    IfcCivilElement_type = new entity(IfcSchema::Type::IfcCivilElement, IfcElement_type);
    IfcCoilType_type = new entity(IfcSchema::Type::IfcCoilType, IfcEnergyConversionDeviceType_type);
    IfcColumn_type = new entity(IfcSchema::Type::IfcColumn, IfcBuildingElement_type);
    IfcColumnStandardCase_type = new entity(IfcSchema::Type::IfcColumnStandardCase, IfcColumn_type);
    IfcCommunicationsApplianceType_type = new entity(IfcSchema::Type::IfcCommunicationsApplianceType, IfcFlowTerminalType_type);
    IfcCompressorType_type = new entity(IfcSchema::Type::IfcCompressorType, IfcFlowMovingDeviceType_type);
    IfcCondenserType_type = new entity(IfcSchema::Type::IfcCondenserType, IfcEnergyConversionDeviceType_type);
    IfcConstructionEquipmentResource_type = new entity(IfcSchema::Type::IfcConstructionEquipmentResource, IfcConstructionResource_type);
    IfcConstructionMaterialResource_type = new entity(IfcSchema::Type::IfcConstructionMaterialResource, IfcConstructionResource_type);
    IfcConstructionProductResource_type = new entity(IfcSchema::Type::IfcConstructionProductResource, IfcConstructionResource_type);
    IfcCooledBeamType_type = new entity(IfcSchema::Type::IfcCooledBeamType, IfcEnergyConversionDeviceType_type);
    IfcCoolingTowerType_type = new entity(IfcSchema::Type::IfcCoolingTowerType, IfcEnergyConversionDeviceType_type);
    IfcCovering_type = new entity(IfcSchema::Type::IfcCovering, IfcBuildingElement_type);
    IfcCurtainWall_type = new entity(IfcSchema::Type::IfcCurtainWall, IfcBuildingElement_type);
    IfcDamperType_type = new entity(IfcSchema::Type::IfcDamperType, IfcFlowControllerType_type);
    IfcDiscreteAccessory_type = new entity(IfcSchema::Type::IfcDiscreteAccessory, IfcElementComponent_type);
    IfcDiscreteAccessoryType_type = new entity(IfcSchema::Type::IfcDiscreteAccessoryType, IfcElementComponentType_type);
    IfcDistributionChamberElementType_type = new entity(IfcSchema::Type::IfcDistributionChamberElementType, IfcDistributionFlowElementType_type);
    IfcDistributionControlElementType_type = new entity(IfcSchema::Type::IfcDistributionControlElementType, IfcDistributionElementType_type);
    IfcDistributionElement_type = new entity(IfcSchema::Type::IfcDistributionElement, IfcElement_type);
    IfcDistributionFlowElement_type = new entity(IfcSchema::Type::IfcDistributionFlowElement, IfcDistributionElement_type);
    IfcDistributionPort_type = new entity(IfcSchema::Type::IfcDistributionPort, IfcPort_type);
    IfcDistributionSystem_type = new entity(IfcSchema::Type::IfcDistributionSystem, IfcSystem_type);
    IfcDoor_type = new entity(IfcSchema::Type::IfcDoor, IfcBuildingElement_type);
    IfcDoorStandardCase_type = new entity(IfcSchema::Type::IfcDoorStandardCase, IfcDoor_type);
    IfcDuctFittingType_type = new entity(IfcSchema::Type::IfcDuctFittingType, IfcFlowFittingType_type);
    IfcDuctSegmentType_type = new entity(IfcSchema::Type::IfcDuctSegmentType, IfcFlowSegmentType_type);
    IfcDuctSilencerType_type = new entity(IfcSchema::Type::IfcDuctSilencerType, IfcFlowTreatmentDeviceType_type);
    IfcElectricApplianceType_type = new entity(IfcSchema::Type::IfcElectricApplianceType, IfcFlowTerminalType_type);
    IfcElectricDistributionBoardType_type = new entity(IfcSchema::Type::IfcElectricDistributionBoardType, IfcFlowControllerType_type);
    IfcElectricFlowStorageDeviceType_type = new entity(IfcSchema::Type::IfcElectricFlowStorageDeviceType, IfcFlowStorageDeviceType_type);
    IfcElectricGeneratorType_type = new entity(IfcSchema::Type::IfcElectricGeneratorType, IfcEnergyConversionDeviceType_type);
    IfcElectricMotorType_type = new entity(IfcSchema::Type::IfcElectricMotorType, IfcEnergyConversionDeviceType_type);
    IfcElectricTimeControlType_type = new entity(IfcSchema::Type::IfcElectricTimeControlType, IfcFlowControllerType_type);
    IfcEnergyConversionDevice_type = new entity(IfcSchema::Type::IfcEnergyConversionDevice, IfcDistributionFlowElement_type);
    IfcEngine_type = new entity(IfcSchema::Type::IfcEngine, IfcEnergyConversionDevice_type);
    IfcEvaporativeCooler_type = new entity(IfcSchema::Type::IfcEvaporativeCooler, IfcEnergyConversionDevice_type);
    IfcEvaporator_type = new entity(IfcSchema::Type::IfcEvaporator, IfcEnergyConversionDevice_type);
    IfcExternalSpatialElement_type = new entity(IfcSchema::Type::IfcExternalSpatialElement, IfcExternalSpatialStructureElement_type);
    IfcFanType_type = new entity(IfcSchema::Type::IfcFanType, IfcFlowMovingDeviceType_type);
    IfcFilterType_type = new entity(IfcSchema::Type::IfcFilterType, IfcFlowTreatmentDeviceType_type);
    IfcFireSuppressionTerminalType_type = new entity(IfcSchema::Type::IfcFireSuppressionTerminalType, IfcFlowTerminalType_type);
    IfcFlowController_type = new entity(IfcSchema::Type::IfcFlowController, IfcDistributionFlowElement_type);
    IfcFlowFitting_type = new entity(IfcSchema::Type::IfcFlowFitting, IfcDistributionFlowElement_type);
    IfcFlowInstrumentType_type = new entity(IfcSchema::Type::IfcFlowInstrumentType, IfcDistributionControlElementType_type);
    IfcFlowMeter_type = new entity(IfcSchema::Type::IfcFlowMeter, IfcFlowController_type);
    IfcFlowMovingDevice_type = new entity(IfcSchema::Type::IfcFlowMovingDevice, IfcDistributionFlowElement_type);
    IfcFlowSegment_type = new entity(IfcSchema::Type::IfcFlowSegment, IfcDistributionFlowElement_type);
    IfcFlowStorageDevice_type = new entity(IfcSchema::Type::IfcFlowStorageDevice, IfcDistributionFlowElement_type);
    IfcFlowTerminal_type = new entity(IfcSchema::Type::IfcFlowTerminal, IfcDistributionFlowElement_type);
    IfcFlowTreatmentDevice_type = new entity(IfcSchema::Type::IfcFlowTreatmentDevice, IfcDistributionFlowElement_type);
    IfcFooting_type = new entity(IfcSchema::Type::IfcFooting, IfcBuildingElement_type);
    IfcHeatExchanger_type = new entity(IfcSchema::Type::IfcHeatExchanger, IfcEnergyConversionDevice_type);
    IfcHumidifier_type = new entity(IfcSchema::Type::IfcHumidifier, IfcEnergyConversionDevice_type);
    IfcInterceptor_type = new entity(IfcSchema::Type::IfcInterceptor, IfcFlowTreatmentDevice_type);
    IfcJunctionBox_type = new entity(IfcSchema::Type::IfcJunctionBox, IfcFlowFitting_type);
    IfcLamp_type = new entity(IfcSchema::Type::IfcLamp, IfcFlowTerminal_type);
    IfcLightFixture_type = new entity(IfcSchema::Type::IfcLightFixture, IfcFlowTerminal_type);
    IfcMedicalDevice_type = new entity(IfcSchema::Type::IfcMedicalDevice, IfcFlowTerminal_type);
    IfcMember_type = new entity(IfcSchema::Type::IfcMember, IfcBuildingElement_type);
    IfcMemberStandardCase_type = new entity(IfcSchema::Type::IfcMemberStandardCase, IfcMember_type);
    IfcMotorConnection_type = new entity(IfcSchema::Type::IfcMotorConnection, IfcEnergyConversionDevice_type);
    IfcOuterBoundaryCurve_type = new entity(IfcSchema::Type::IfcOuterBoundaryCurve, IfcBoundaryCurve_type);
    IfcOutlet_type = new entity(IfcSchema::Type::IfcOutlet, IfcFlowTerminal_type);
    IfcPile_type = new entity(IfcSchema::Type::IfcPile, IfcBuildingElement_type);
    IfcPipeFitting_type = new entity(IfcSchema::Type::IfcPipeFitting, IfcFlowFitting_type);
    IfcPipeSegment_type = new entity(IfcSchema::Type::IfcPipeSegment, IfcFlowSegment_type);
    IfcPlate_type = new entity(IfcSchema::Type::IfcPlate, IfcBuildingElement_type);
    IfcPlateStandardCase_type = new entity(IfcSchema::Type::IfcPlateStandardCase, IfcPlate_type);
    IfcProtectiveDevice_type = new entity(IfcSchema::Type::IfcProtectiveDevice, IfcFlowController_type);
    IfcProtectiveDeviceTrippingUnitType_type = new entity(IfcSchema::Type::IfcProtectiveDeviceTrippingUnitType, IfcDistributionControlElementType_type);
    IfcPump_type = new entity(IfcSchema::Type::IfcPump, IfcFlowMovingDevice_type);
    IfcRailing_type = new entity(IfcSchema::Type::IfcRailing, IfcBuildingElement_type);
    IfcRamp_type = new entity(IfcSchema::Type::IfcRamp, IfcBuildingElement_type);
    IfcRampFlight_type = new entity(IfcSchema::Type::IfcRampFlight, IfcBuildingElement_type);
    IfcRationalBSplineCurveWithKnots_type = new entity(IfcSchema::Type::IfcRationalBSplineCurveWithKnots, IfcBSplineCurveWithKnots_type);
    IfcReinforcingBar_type = new entity(IfcSchema::Type::IfcReinforcingBar, IfcReinforcingElement_type);
    IfcReinforcingBarType_type = new entity(IfcSchema::Type::IfcReinforcingBarType, IfcReinforcingElementType_type);
    IfcRoof_type = new entity(IfcSchema::Type::IfcRoof, IfcBuildingElement_type);
    IfcSanitaryTerminal_type = new entity(IfcSchema::Type::IfcSanitaryTerminal, IfcFlowTerminal_type);
    IfcSensorType_type = new entity(IfcSchema::Type::IfcSensorType, IfcDistributionControlElementType_type);
    IfcShadingDevice_type = new entity(IfcSchema::Type::IfcShadingDevice, IfcBuildingElement_type);
    IfcSlab_type = new entity(IfcSchema::Type::IfcSlab, IfcBuildingElement_type);
    IfcSlabElementedCase_type = new entity(IfcSchema::Type::IfcSlabElementedCase, IfcSlab_type);
    IfcSlabStandardCase_type = new entity(IfcSchema::Type::IfcSlabStandardCase, IfcSlab_type);
    IfcSolarDevice_type = new entity(IfcSchema::Type::IfcSolarDevice, IfcEnergyConversionDevice_type);
    IfcSpaceHeater_type = new entity(IfcSchema::Type::IfcSpaceHeater, IfcFlowTerminal_type);
    IfcStackTerminal_type = new entity(IfcSchema::Type::IfcStackTerminal, IfcFlowTerminal_type);
    IfcStair_type = new entity(IfcSchema::Type::IfcStair, IfcBuildingElement_type);
    IfcStairFlight_type = new entity(IfcSchema::Type::IfcStairFlight, IfcBuildingElement_type);
    IfcStructuralAnalysisModel_type = new entity(IfcSchema::Type::IfcStructuralAnalysisModel, IfcSystem_type);
    IfcStructuralLoadCase_type = new entity(IfcSchema::Type::IfcStructuralLoadCase, IfcStructuralLoadGroup_type);
    IfcStructuralPlanarAction_type = new entity(IfcSchema::Type::IfcStructuralPlanarAction, IfcStructuralSurfaceAction_type);
    IfcSwitchingDevice_type = new entity(IfcSchema::Type::IfcSwitchingDevice, IfcFlowController_type);
    IfcTank_type = new entity(IfcSchema::Type::IfcTank, IfcFlowStorageDevice_type);
    IfcTransformer_type = new entity(IfcSchema::Type::IfcTransformer, IfcEnergyConversionDevice_type);
    IfcTubeBundle_type = new entity(IfcSchema::Type::IfcTubeBundle, IfcEnergyConversionDevice_type);
    IfcUnitaryControlElementType_type = new entity(IfcSchema::Type::IfcUnitaryControlElementType, IfcDistributionControlElementType_type);
    IfcUnitaryEquipment_type = new entity(IfcSchema::Type::IfcUnitaryEquipment, IfcEnergyConversionDevice_type);
    IfcValve_type = new entity(IfcSchema::Type::IfcValve, IfcFlowController_type);
    IfcWall_type = new entity(IfcSchema::Type::IfcWall, IfcBuildingElement_type);
    IfcWallElementedCase_type = new entity(IfcSchema::Type::IfcWallElementedCase, IfcWall_type);
    IfcWallStandardCase_type = new entity(IfcSchema::Type::IfcWallStandardCase, IfcWall_type);
    IfcWasteTerminal_type = new entity(IfcSchema::Type::IfcWasteTerminal, IfcFlowTerminal_type);
    IfcWindow_type = new entity(IfcSchema::Type::IfcWindow, IfcBuildingElement_type);
    IfcWindowStandardCase_type = new entity(IfcSchema::Type::IfcWindowStandardCase, IfcWindow_type);
    IfcActuatorType_type = new entity(IfcSchema::Type::IfcActuatorType, IfcDistributionControlElementType_type);
    IfcAirTerminal_type = new entity(IfcSchema::Type::IfcAirTerminal, IfcFlowTerminal_type);
    IfcAirTerminalBox_type = new entity(IfcSchema::Type::IfcAirTerminalBox, IfcFlowController_type);
    IfcAirToAirHeatRecovery_type = new entity(IfcSchema::Type::IfcAirToAirHeatRecovery, IfcEnergyConversionDevice_type);
    IfcAlarmType_type = new entity(IfcSchema::Type::IfcAlarmType, IfcDistributionControlElementType_type);
    IfcAudioVisualAppliance_type = new entity(IfcSchema::Type::IfcAudioVisualAppliance, IfcFlowTerminal_type);
    IfcBeam_type = new entity(IfcSchema::Type::IfcBeam, IfcBuildingElement_type);
    IfcBeamStandardCase_type = new entity(IfcSchema::Type::IfcBeamStandardCase, IfcBeam_type);
    IfcBoiler_type = new entity(IfcSchema::Type::IfcBoiler, IfcEnergyConversionDevice_type);
    IfcBurner_type = new entity(IfcSchema::Type::IfcBurner, IfcEnergyConversionDevice_type);
    IfcCableCarrierFitting_type = new entity(IfcSchema::Type::IfcCableCarrierFitting, IfcFlowFitting_type);
    IfcCableCarrierSegment_type = new entity(IfcSchema::Type::IfcCableCarrierSegment, IfcFlowSegment_type);
    IfcCableFitting_type = new entity(IfcSchema::Type::IfcCableFitting, IfcFlowFitting_type);
    IfcCableSegment_type = new entity(IfcSchema::Type::IfcCableSegment, IfcFlowSegment_type);
    IfcChiller_type = new entity(IfcSchema::Type::IfcChiller, IfcEnergyConversionDevice_type);
    IfcCoil_type = new entity(IfcSchema::Type::IfcCoil, IfcEnergyConversionDevice_type);
    IfcCommunicationsAppliance_type = new entity(IfcSchema::Type::IfcCommunicationsAppliance, IfcFlowTerminal_type);
    IfcCompressor_type = new entity(IfcSchema::Type::IfcCompressor, IfcFlowMovingDevice_type);
    IfcCondenser_type = new entity(IfcSchema::Type::IfcCondenser, IfcEnergyConversionDevice_type);
    IfcControllerType_type = new entity(IfcSchema::Type::IfcControllerType, IfcDistributionControlElementType_type);
    IfcCooledBeam_type = new entity(IfcSchema::Type::IfcCooledBeam, IfcEnergyConversionDevice_type);
    IfcCoolingTower_type = new entity(IfcSchema::Type::IfcCoolingTower, IfcEnergyConversionDevice_type);
    IfcDamper_type = new entity(IfcSchema::Type::IfcDamper, IfcFlowController_type);
    IfcDistributionChamberElement_type = new entity(IfcSchema::Type::IfcDistributionChamberElement, IfcDistributionFlowElement_type);
    IfcDistributionCircuit_type = new entity(IfcSchema::Type::IfcDistributionCircuit, IfcDistributionSystem_type);
    IfcDistributionControlElement_type = new entity(IfcSchema::Type::IfcDistributionControlElement, IfcDistributionElement_type);
    IfcDuctFitting_type = new entity(IfcSchema::Type::IfcDuctFitting, IfcFlowFitting_type);
    IfcDuctSegment_type = new entity(IfcSchema::Type::IfcDuctSegment, IfcFlowSegment_type);
    IfcDuctSilencer_type = new entity(IfcSchema::Type::IfcDuctSilencer, IfcFlowTreatmentDevice_type);
    IfcElectricAppliance_type = new entity(IfcSchema::Type::IfcElectricAppliance, IfcFlowTerminal_type);
    IfcElectricDistributionBoard_type = new entity(IfcSchema::Type::IfcElectricDistributionBoard, IfcFlowController_type);
    IfcElectricFlowStorageDevice_type = new entity(IfcSchema::Type::IfcElectricFlowStorageDevice, IfcFlowStorageDevice_type);
    IfcElectricGenerator_type = new entity(IfcSchema::Type::IfcElectricGenerator, IfcEnergyConversionDevice_type);
    IfcElectricMotor_type = new entity(IfcSchema::Type::IfcElectricMotor, IfcEnergyConversionDevice_type);
    IfcElectricTimeControl_type = new entity(IfcSchema::Type::IfcElectricTimeControl, IfcFlowController_type);
    IfcFan_type = new entity(IfcSchema::Type::IfcFan, IfcFlowMovingDevice_type);
    IfcFilter_type = new entity(IfcSchema::Type::IfcFilter, IfcFlowTreatmentDevice_type);
    IfcFireSuppressionTerminal_type = new entity(IfcSchema::Type::IfcFireSuppressionTerminal, IfcFlowTerminal_type);
    IfcFlowInstrument_type = new entity(IfcSchema::Type::IfcFlowInstrument, IfcDistributionControlElement_type);
    IfcProtectiveDeviceTrippingUnit_type = new entity(IfcSchema::Type::IfcProtectiveDeviceTrippingUnit, IfcDistributionControlElement_type);
    IfcSensor_type = new entity(IfcSchema::Type::IfcSensor, IfcDistributionControlElement_type);
    IfcUnitaryControlElement_type = new entity(IfcSchema::Type::IfcUnitaryControlElement, IfcDistributionControlElement_type);
    IfcActuator_type = new entity(IfcSchema::Type::IfcActuator, IfcDistributionControlElement_type);
    IfcAlarm_type = new entity(IfcSchema::Type::IfcAlarm, IfcDistributionControlElement_type);
    IfcController_type = new entity(IfcSchema::Type::IfcController, IfcDistributionControlElement_type);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcOrganization_type);
        items.push_back(IfcPerson_type);
        items.push_back(IfcPersonAndOrganization_type);
        IfcActorSelect_type = new select_type(IfcSchema::Type::IfcActorSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcAxis2Placement2D_type);
        items.push_back(IfcAxis2Placement3D_type);
        IfcAxis2Placement_type = new select_type(IfcSchema::Type::IfcAxis2Placement, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcLengthMeasure_type);
        items.push_back(IfcPlaneAngleMeasure_type);
        IfcBendingParameterSelect_type = new select_type(IfcSchema::Type::IfcBendingParameterSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IfcBooleanResult_type);
        items.push_back(IfcCsgPrimitive3D_type);
        items.push_back(IfcHalfSpaceSolid_type);
        items.push_back(IfcSolidModel_type);
        IfcBooleanOperand_type = new select_type(IfcSchema::Type::IfcBooleanOperand, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcClassification_type);
        items.push_back(IfcClassificationReference_type);
        IfcClassificationReferenceSelect_type = new select_type(IfcSchema::Type::IfcClassificationReferenceSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcClassification_type);
        items.push_back(IfcClassificationReference_type);
        IfcClassificationSelect_type = new select_type(IfcSchema::Type::IfcClassificationSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcColourSpecification_type);
        items.push_back(IfcPreDefinedColour_type);
        IfcColour_type = new select_type(IfcSchema::Type::IfcColour, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcColourRgb_type);
        items.push_back(IfcNormalisedRatioMeasure_type);
        IfcColourOrFactor_type = new select_type(IfcSchema::Type::IfcColourOrFactor, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCoordinateReferenceSystem_type);
        items.push_back(IfcGeometricRepresentationContext_type);
        IfcCoordinateReferenceSystemSelect_type = new select_type(IfcSchema::Type::IfcCoordinateReferenceSystemSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBooleanResult_type);
        items.push_back(IfcCsgPrimitive3D_type);
        IfcCsgSelect_type = new select_type(IfcSchema::Type::IfcCsgSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCompositeCurveOnSurface_type);
        items.push_back(IfcPcurve_type);
        IfcCurveOnSurface_type = new select_type(IfcSchema::Type::IfcCurveOnSurface, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoundedCurve_type);
        items.push_back(IfcEdgeCurve_type);
        IfcCurveOrEdgeCurve_type = new select_type(IfcSchema::Type::IfcCurveOrEdgeCurve, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCurveStyleFont_type);
        items.push_back(IfcPreDefinedCurveFont_type);
        IfcCurveStyleFontSelect_type = new select_type(IfcSchema::Type::IfcCurveStyleFontSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcObjectDefinition_type);
        items.push_back(IfcPropertyDefinition_type);
        IfcDefinitionSelect_type = new select_type(IfcSchema::Type::IfcDefinitionSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(71);
        items.push_back(IfcAbsorbedDoseMeasure_type);
        items.push_back(IfcAccelerationMeasure_type);
        items.push_back(IfcAngularVelocityMeasure_type);
        items.push_back(IfcAreaDensityMeasure_type);
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
        items.push_back(IfcSoundPowerLevelMeasure_type);
        items.push_back(IfcSoundPowerMeasure_type);
        items.push_back(IfcSoundPressureLevelMeasure_type);
        items.push_back(IfcSoundPressureMeasure_type);
        items.push_back(IfcSpecificHeatCapacityMeasure_type);
        items.push_back(IfcTemperatureGradientMeasure_type);
        items.push_back(IfcTemperatureRateOfChangeMeasure_type);
        items.push_back(IfcThermalAdmittanceMeasure_type);
        items.push_back(IfcThermalConductivityMeasure_type);
        items.push_back(IfcThermalExpansionCoefficientMeasure_type);
        items.push_back(IfcThermalResistanceMeasure_type);
        items.push_back(IfcThermalTransmittanceMeasure_type);
        items.push_back(IfcTorqueMeasure_type);
        items.push_back(IfcVaporPermeabilityMeasure_type);
        items.push_back(IfcVolumetricFlowRateMeasure_type);
        items.push_back(IfcWarpingConstantMeasure_type);
        items.push_back(IfcWarpingMomentMeasure_type);
        IfcDerivedMeasureValue_type = new select_type(IfcSchema::Type::IfcDerivedMeasureValue, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDocumentInformation_type);
        items.push_back(IfcDocumentReference_type);
        IfcDocumentSelect_type = new select_type(IfcSchema::Type::IfcDocumentSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IfcColour_type);
        items.push_back(IfcExternallyDefinedHatchStyle_type);
        items.push_back(IfcFillAreaStyleHatching_type);
        items.push_back(IfcFillAreaStyleTiles_type);
        IfcFillStyleSelect_type = new select_type(IfcSchema::Type::IfcFillStyleSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcCurve_type);
        items.push_back(IfcPoint_type);
        items.push_back(IfcSurface_type);
        IfcGeometricSetSelect_type = new select_type(IfcSchema::Type::IfcGeometricSetSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDirection_type);
        items.push_back(IfcVirtualGridIntersection_type);
        IfcGridPlacementDirectionSelect_type = new select_type(IfcSchema::Type::IfcGridPlacementDirectionSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcPositiveLengthMeasure_type);
        items.push_back(IfcVector_type);
        IfcHatchLineDistanceSelect_type = new select_type(IfcSchema::Type::IfcHatchLineDistanceSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcRepresentation_type);
        items.push_back(IfcRepresentationItem_type);
        IfcLayeredItem_type = new select_type(IfcSchema::Type::IfcLayeredItem, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcLibraryInformation_type);
        items.push_back(IfcLibraryReference_type);
        IfcLibrarySelect_type = new select_type(IfcSchema::Type::IfcLibrarySelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternalReference_type);
        items.push_back(IfcLightIntensityDistribution_type);
        IfcLightDistributionDataSourceSelect_type = new select_type(IfcSchema::Type::IfcLightDistributionDataSourceSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcMaterialDefinition_type);
        items.push_back(IfcMaterialList_type);
        items.push_back(IfcMaterialUsageDefinition_type);
        IfcMaterialSelect_type = new select_type(IfcSchema::Type::IfcMaterialSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(23);
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
        items.push_back(IfcNonNegativeLengthMeasure_type);
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
        IfcMeasureValue_type = new select_type(IfcSchema::Type::IfcMeasureValue, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcModulusOfRotationalSubgradeReactionMeasure_type);
        IfcModulusOfRotationalSubgradeReactionSelect_type = new select_type(IfcSchema::Type::IfcModulusOfRotationalSubgradeReactionSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcModulusOfSubgradeReactionMeasure_type);
        IfcModulusOfSubgradeReactionSelect_type = new select_type(IfcSchema::Type::IfcModulusOfSubgradeReactionSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcModulusOfLinearSubgradeReactionMeasure_type);
        IfcModulusOfTranslationalSubgradeReactionSelect_type = new select_type(IfcSchema::Type::IfcModulusOfTranslationalSubgradeReactionSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(9);
        items.push_back(IfcAddress_type);
        items.push_back(IfcAppliedValue_type);
        items.push_back(IfcExternalReference_type);
        items.push_back(IfcMaterialDefinition_type);
        items.push_back(IfcOrganization_type);
        items.push_back(IfcPerson_type);
        items.push_back(IfcPersonAndOrganization_type);
        items.push_back(IfcTable_type);
        items.push_back(IfcTimeSeries_type);
        IfcObjectReferenceSelect_type = new select_type(IfcSchema::Type::IfcObjectReferenceSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcPoint_type);
        items.push_back(IfcVertexPoint_type);
        IfcPointOrVertexPoint_type = new select_type(IfcSchema::Type::IfcPointOrVertexPoint, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IfcCurveStyle_type);
        items.push_back(IfcFillAreaStyle_type);
        items.push_back(IfcNullStyle_type);
        items.push_back(IfcSurfaceStyle_type);
        items.push_back(IfcTextStyle_type);
        IfcPresentationStyleSelect_type = new select_type(IfcSchema::Type::IfcPresentationStyleSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcProcess_type);
        items.push_back(IfcTypeProcess_type);
        IfcProcessSelect_type = new select_type(IfcSchema::Type::IfcProcessSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcProductDefinitionShape_type);
        items.push_back(IfcRepresentationMap_type);
        IfcProductRepresentationSelect_type = new select_type(IfcSchema::Type::IfcProductRepresentationSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcProduct_type);
        items.push_back(IfcTypeProduct_type);
        IfcProductSelect_type = new select_type(IfcSchema::Type::IfcProductSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcPropertySetDefinition_type);
        items.push_back(IfcPropertySetDefinitionSet_type);
        IfcPropertySetDefinitionSelect_type = new select_type(IfcSchema::Type::IfcPropertySetDefinitionSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(16);
        items.push_back(IfcActorRole_type);
        items.push_back(IfcAppliedValue_type);
        items.push_back(IfcApproval_type);
        items.push_back(IfcConstraint_type);
        items.push_back(IfcContextDependentUnit_type);
        items.push_back(IfcConversionBasedUnit_type);
        items.push_back(IfcExternalInformation_type);
        items.push_back(IfcExternalReference_type);
        items.push_back(IfcMaterialDefinition_type);
        items.push_back(IfcOrganization_type);
        items.push_back(IfcPerson_type);
        items.push_back(IfcPersonAndOrganization_type);
        items.push_back(IfcPhysicalQuantity_type);
        items.push_back(IfcProfileDef_type);
        items.push_back(IfcPropertyAbstraction_type);
        items.push_back(IfcTimeSeries_type);
        IfcResourceObjectSelect_type = new select_type(IfcSchema::Type::IfcResourceObjectSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcResource_type);
        items.push_back(IfcTypeResource_type);
        IfcResourceSelect_type = new select_type(IfcSchema::Type::IfcResourceSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcRotationalStiffnessMeasure_type);
        IfcRotationalStiffnessSelect_type = new select_type(IfcSchema::Type::IfcRotationalStiffnessSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcArcIndex_type);
        items.push_back(IfcLineIndex_type);
        IfcSegmentIndexSelect_type = new select_type(IfcSchema::Type::IfcSegmentIndexSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcClosedShell_type);
        items.push_back(IfcOpenShell_type);
        IfcShell_type = new select_type(IfcSchema::Type::IfcShell, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(13);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcDate_type);
        items.push_back(IfcDateTime_type);
        items.push_back(IfcDuration_type);
        items.push_back(IfcIdentifier_type);
        items.push_back(IfcInteger_type);
        items.push_back(IfcLabel_type);
        items.push_back(IfcLogical_type);
        items.push_back(IfcPositiveInteger_type);
        items.push_back(IfcReal_type);
        items.push_back(IfcText_type);
        items.push_back(IfcTime_type);
        items.push_back(IfcTimeStamp_type);
        IfcSimpleValue_type = new select_type(IfcSchema::Type::IfcSimpleValue, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IfcDescriptiveMeasure_type);
        items.push_back(IfcLengthMeasure_type);
        items.push_back(IfcNormalisedRatioMeasure_type);
        items.push_back(IfcPositiveLengthMeasure_type);
        items.push_back(IfcPositiveRatioMeasure_type);
        items.push_back(IfcRatioMeasure_type);
        IfcSizeSelect_type = new select_type(IfcSchema::Type::IfcSizeSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcClosedShell_type);
        items.push_back(IfcSolidModel_type);
        IfcSolidOrShell_type = new select_type(IfcSchema::Type::IfcSolidOrShell, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternalSpatialElement_type);
        items.push_back(IfcSpace_type);
        IfcSpaceBoundarySelect_type = new select_type(IfcSchema::Type::IfcSpaceBoundarySelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcSpecularExponent_type);
        items.push_back(IfcSpecularRoughness_type);
        IfcSpecularHighlightSelect_type = new select_type(IfcSchema::Type::IfcSpecularHighlightSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcElement_type);
        items.push_back(IfcStructuralItem_type);
        IfcStructuralActivityAssignmentSelect_type = new select_type(IfcSchema::Type::IfcStructuralActivityAssignmentSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcPresentationStyle_type);
        items.push_back(IfcPresentationStyleAssignment_type);
        IfcStyleAssignmentSelect_type = new select_type(IfcSchema::Type::IfcStyleAssignmentSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcFaceBasedSurfaceModel_type);
        items.push_back(IfcFaceSurface_type);
        items.push_back(IfcSurface_type);
        IfcSurfaceOrFaceSurface_type = new select_type(IfcSchema::Type::IfcSurfaceOrFaceSurface, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IfcExternallyDefinedSurfaceStyle_type);
        items.push_back(IfcSurfaceStyleLighting_type);
        items.push_back(IfcSurfaceStyleRefraction_type);
        items.push_back(IfcSurfaceStyleShading_type);
        items.push_back(IfcSurfaceStyleWithTextures_type);
        IfcSurfaceStyleElementSelect_type = new select_type(IfcSchema::Type::IfcSurfaceStyleElementSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternallyDefinedTextFont_type);
        items.push_back(IfcPreDefinedTextFont_type);
        IfcTextFontSelect_type = new select_type(IfcSchema::Type::IfcTextFontSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDuration_type);
        items.push_back(IfcRatioMeasure_type);
        IfcTimeOrRatioSelect_type = new select_type(IfcSchema::Type::IfcTimeOrRatioSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcLinearStiffnessMeasure_type);
        IfcTranslationalStiffnessSelect_type = new select_type(IfcSchema::Type::IfcTranslationalStiffnessSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCartesianPoint_type);
        items.push_back(IfcParameterValue_type);
        IfcTrimmingSelect_type = new select_type(IfcSchema::Type::IfcTrimmingSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcDerivedUnit_type);
        items.push_back(IfcMonetaryUnit_type);
        items.push_back(IfcNamedUnit_type);
        IfcUnit_type = new select_type(IfcSchema::Type::IfcUnit, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcDerivedMeasureValue_type);
        items.push_back(IfcMeasureValue_type);
        items.push_back(IfcSimpleValue_type);
        IfcValue_type = new select_type(IfcSchema::Type::IfcValue, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDirection_type);
        items.push_back(IfcVector_type);
        IfcVectorOrDirection_type = new select_type(IfcSchema::Type::IfcVectorOrDirection, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcWarpingMomentMeasure_type);
        IfcWarpingStiffnessSelect_type = new select_type(IfcSchema::Type::IfcWarpingStiffnessSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcMeasureWithUnit_type);
        items.push_back(IfcReference_type);
        items.push_back(IfcValue_type);
        IfcAppliedValueSelect_type = new select_type(IfcSchema::Type::IfcAppliedValueSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCurveStyleFontAndScaling_type);
        items.push_back(IfcCurveStyleFontSelect_type);
        IfcCurveFontOrScaledCurveFontSelect_type = new select_type(IfcSchema::Type::IfcCurveFontOrScaledCurveFontSelect, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IfcAppliedValue_type);
        items.push_back(IfcMeasureWithUnit_type);
        items.push_back(IfcReference_type);
        items.push_back(IfcTable_type);
        items.push_back(IfcTimeSeries_type);
        items.push_back(IfcValue_type);
        IfcMetricValueSelect_type = new select_type(IfcSchema::Type::IfcMetricValueSelect, items);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcActionRequestTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcActuatorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcActuator_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcAdvancedBrep_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcClosedShell_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcAdvancedBrepWithVoids_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAdvancedFace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAirTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAirTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAirTerminalBoxTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAirTerminalBox_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAirToAirHeatRecoveryTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAirToAirHeatRecovery_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAlarmTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAlarm_type->set_attributes(attributes, derived);
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
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAnnotation_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("AppliedValue", new named_type(IfcAppliedValueSelect_type), true));
        attributes.push_back(new entity::attribute("UnitBasis", new named_type(IfcMeasureWithUnit_type), true));
        attributes.push_back(new entity::attribute("ApplicableDate", new named_type(IfcDate_type), true));
        attributes.push_back(new entity::attribute("FixedUntilDate", new named_type(IfcDate_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Condition", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ArithmeticOperator", new named_type(IfcArithmeticOperatorEnum_type), true));
        attributes.push_back(new entity::attribute("Components", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcAppliedValue_type)), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAppliedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("Identifier", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("TimeOfApproval", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Level", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Qualifier", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("RequestingApproval", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("GivingApproval", new named_type(IfcActorSelect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcApproval_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IfcApproval_type), false));
        attributes.push_back(new entity::attribute("RelatedApprovals", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcApproval_type)), false));
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
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("OriginalValue", new named_type(IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("CurrentValue", new named_type(IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("TotalReplacementCost", new named_type(IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("Owner", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("User", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("ResponsiblePerson", new named_type(IfcPerson_type), true));
        attributes.push_back(new entity::attribute("IncorporationDate", new named_type(IfcDate_type), true));
        attributes.push_back(new entity::attribute("DepreciatedValue", new named_type(IfcCostValue_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAsset_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::attribute("BottomFlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("OverallDepth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BottomFlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BottomFlangeFilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopFlangeThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeFilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BottomFlangeEdgeRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BottomFlangeSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeEdgeRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAsymmetricIShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAudioVisualApplianceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAudioVisualAppliance_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAudioVisualApplianceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAudioVisualApplianceType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("Degree", new named_type(IfcInteger_type), false));
        attributes.push_back(new entity::attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcCartesianPoint_type)), false));
        attributes.push_back(new entity::attribute("CurveForm", new named_type(IfcBSplineCurveForm_type), false));
        attributes.push_back(new entity::attribute("ClosedCurve", new named_type(IfcLogical_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IfcLogical_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBSplineCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("KnotMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("Knots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcParameterValue_type)), false));
        attributes.push_back(new entity::attribute("KnotSpec", new named_type(IfcKnotType_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBSplineCurveWithKnots_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("UDegree", new named_type(IfcInteger_type), false));
        attributes.push_back(new entity::attribute("VDegree", new named_type(IfcInteger_type), false));
        attributes.push_back(new entity::attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcCartesianPoint_type))), false));
        attributes.push_back(new entity::attribute("SurfaceForm", new named_type(IfcBSplineSurfaceForm_type), false));
        attributes.push_back(new entity::attribute("UClosed", new named_type(IfcLogical_type), false));
        attributes.push_back(new entity::attribute("VClosed", new named_type(IfcLogical_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IfcLogical_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBSplineSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("UMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("VMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("UKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcParameterValue_type)), false));
        attributes.push_back(new entity::attribute("VKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcParameterValue_type)), false));
        attributes.push_back(new entity::attribute("KnotSpec", new named_type(IfcKnotType_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBSplineSurfaceWithKnots_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBeamTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBeam_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBeamStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBeamTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBeamType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RasterFormat", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("RasterCode", new named_type(IfcBinary_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBoilerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoiler_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcBoundaryCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TranslationalStiffnessByLengthX", new named_type(IfcModulusOfTranslationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessByLengthY", new named_type(IfcModulusOfTranslationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessByLengthZ", new named_type(IfcModulusOfTranslationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthX", new named_type(IfcModulusOfRotationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthY", new named_type(IfcModulusOfRotationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthZ", new named_type(IfcModulusOfRotationalSubgradeReactionSelect_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoundaryEdgeCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TranslationalStiffnessByAreaX", new named_type(IfcModulusOfSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessByAreaY", new named_type(IfcModulusOfSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessByAreaZ", new named_type(IfcModulusOfSubgradeReactionSelect_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoundaryFaceCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TranslationalStiffnessX", new named_type(IfcTranslationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessY", new named_type(IfcTranslationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessZ", new named_type(IfcTranslationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessX", new named_type(IfcRotationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessY", new named_type(IfcRotationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessZ", new named_type(IfcRotationalStiffnessSelect_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoundaryNodeCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WarpingStiffness", new named_type(IfcWarpingStiffnessSelect_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBuildingElementPartTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingElementPart_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBuildingElementPartTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingElementPartType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBuildingElementProxyTypeEnum_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBuildingSystemTypeEnum_type), true));
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBurnerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBurner_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBurnerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBurnerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Width", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Girth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InternalFilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableCarrierFittingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableCarrierFitting_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableCarrierSegmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableCarrierSegment_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableFittingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableFitting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableSegmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcCartesianPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcCartesianPointList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IfcLengthMeasure_type))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcCartesianPointList2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IfcLengthMeasure_type))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcCartesianPointList3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Axis1", new named_type(IfcDirection_type), true));
        attributes.push_back(new entity::attribute("Axis2", new named_type(IfcDirection_type), true));
        attributes.push_back(new entity::attribute("LocalOrigin", new named_type(IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Scale", new named_type(IfcReal_type), true));
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
        attributes.push_back(new entity::attribute("Scale2", new named_type(IfcReal_type), true));
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
        attributes.push_back(new entity::attribute("Scale2", new named_type(IfcReal_type), true));
        attributes.push_back(new entity::attribute("Scale3", new named_type(IfcReal_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcChillerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcChiller_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcChimneyTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcChimney_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcChimneyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcChimneyType_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCivilElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCivilElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Source", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Edition", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("EditionDate", new named_type(IfcDate_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Location", new named_type(IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("ReferenceTokens", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcIdentifier_type)), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcClassification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ReferencedSource", new named_type(IfcClassificationReferenceSelect_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Sort", new named_type(IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCoilTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCoil_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("ColourList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IfcNormalisedRatioMeasure_type))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcColourRgbList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcColourSpecification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcColumnTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcColumn_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcColumnStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcColumnTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcColumnType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCommunicationsApplianceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCommunicationsAppliance_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCommunicationsApplianceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCommunicationsApplianceType_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("TemplateType", new named_type(IfcComplexPropertyTemplateTypeEnum_type), true));
        attributes.push_back(new entity::attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPropertyTemplate_type)), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcComplexPropertyTemplate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcCompositeCurveSegment_type)), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IfcLogical_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcCompositeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcCompositeCurveOnSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Transition", new named_type(IfcTransitionCode_type), false));
        attributes.push_back(new entity::attribute("SameSense", new named_type(IfcBoolean_type), false));
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCompressorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCompressor_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCondenserTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCondenser_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCondenserTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCondenserType_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SurfaceOnRelatingElement", new named_type(IfcSurfaceOrFaceSurface_type), false));
        attributes.push_back(new entity::attribute("SurfaceOnRelatedElement", new named_type(IfcSurfaceOrFaceSurface_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcConnectionSurfaceGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VolumeOnRelatingElement", new named_type(IfcSolidOrShell_type), false));
        attributes.push_back(new entity::attribute("VolumeOnRelatedElement", new named_type(IfcSolidOrShell_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcConnectionVolumeGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ConstraintGrade", new named_type(IfcConstraintEnum_type), false));
        attributes.push_back(new entity::attribute("ConstraintSource", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CreatingActor", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("CreationTime", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("UserDefinedGrade", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstraint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcConstructionEquipmentResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionEquipmentResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcConstructionEquipmentResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionEquipmentResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcConstructionMaterialResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionMaterialResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcConstructionMaterialResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionMaterialResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcConstructionProductResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionProductResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcConstructionProductResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionProductResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Usage", new named_type(IfcResourceTime_type), true));
        attributes.push_back(new entity::attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcAppliedValue_type)), true));
        attributes.push_back(new entity::attribute("BaseQuantity", new named_type(IfcPhysicalQuantity_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcAppliedValue_type)), true));
        attributes.push_back(new entity::attribute("BaseQuantity", new named_type(IfcPhysicalQuantity_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ObjectType", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Phase", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("RepresentationContexts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcRepresentationContext_type)), true));
        attributes.push_back(new entity::attribute("UnitsInContext", new named_type(IfcUnitAssignment_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcContextDependentUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcControllerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcController_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("ConversionOffset", new named_type(IfcReal_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConversionBasedUnitWithOffset_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCooledBeamTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCooledBeam_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCoolingTowerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCoolingTower_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCoolingTowerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCoolingTowerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SourceCRS", new named_type(IfcCoordinateReferenceSystemSelect_type), false));
        attributes.push_back(new entity::attribute("TargetCRS", new named_type(IfcCoordinateReferenceSystem_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcCoordinateOperation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("GeodeticDatum", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("VerticalDatum", new named_type(IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCoordinateReferenceSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCostItemTypeEnum_type), true));
        attributes.push_back(new entity::attribute("CostValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcCostValue_type)), true));
        attributes.push_back(new entity::attribute("CostQuantities", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcPhysicalQuantity_type)), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCostItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCostScheduleTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("SubmittedOn", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("UpdateDate", new named_type(IfcDateTime_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCostSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCrewResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCrewResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCrewResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCrewResourceType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("RateDateTime", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("RateSource", new named_type(IfcLibraryInformation_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCurrencyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCurtainWallTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IfcSurface_type), false));
        attributes.push_back(new entity::attribute("Boundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcBoundaryCurve_type)), false));
        attributes.push_back(new entity::attribute("ImplicitOuter", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCurveBoundedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("CurveFont", new named_type(IfcCurveFontOrScaledCurveFontSelect_type), true));
        attributes.push_back(new entity::attribute("CurveWidth", new named_type(IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("CurveColour", new named_type(IfcColour_type), true));
        attributes.push_back(new entity::attribute("ModelOrDraughting", new named_type(IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcCylindricalSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDamperTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDamper_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDamperTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDamperType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("DirectionRatios", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IfcReal_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcDirection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDiscreteAccessoryTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDiscreteAccessory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDiscreteAccessoryTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDiscreteAccessoryType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDistributionChamberElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionCircuit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("FlowDirection", new named_type(IfcFlowDirectionEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDistributionPortTypeEnum_type), true));
        attributes.push_back(new entity::attribute("SystemType", new named_type(IfcDistributionSystemEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionPort_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDistributionSystemEnum_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Location", new named_type(IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("IntendedUse", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Scope", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Revision", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DocumentOwner", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("Editors", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcActorSelect_type)), true));
        attributes.push_back(new entity::attribute("CreationTime", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("LastRevisionTime", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ElectronicFormat", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("ValidFrom", new named_type(IfcDate_type), true));
        attributes.push_back(new entity::attribute("ValidUntil", new named_type(IfcDate_type), true));
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
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDocumentInformationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ReferencedDocument", new named_type(IfcDocumentInformation_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDocumentReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDoorTypeEnum_type), true));
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcDoorTypeOperationEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedOperationType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDoor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(13);
        attributes.push_back(new entity::attribute("LiningDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningThickness", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdThickness", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomThickness", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomOffset", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningOffset", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdOffset", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CasingThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CasingDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IfcShapeAspect_type), true));
        attributes.push_back(new entity::attribute("LiningToPanelOffsetX", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningToPanelOffsetY", new named_type(IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDoorStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcDoorStyleOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IfcDoorStyleConstructionEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new named_type(IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Sizeable", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDoorStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDoorTypeEnum_type), false));
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcDoorTypeOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new named_type(IfcBoolean_type), true));
        attributes.push_back(new entity::attribute("UserDefinedOperationType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDoorType_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDuctFittingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDuctFitting_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDuctSegmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDuctSegment_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDuctSilencerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDuctSilencer_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("SameSense", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEdgeCurve_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricApplianceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricAppliance_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricApplianceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricApplianceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricDistributionBoardTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricDistributionBoard_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricDistributionBoardTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricDistributionBoardType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricFlowStorageDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricFlowStorageDevice_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricGeneratorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricGenerator_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricMotorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricMotor_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricTimeControlTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricTimeControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricTimeControlTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricTimeControlType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElementAssemblyTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElementAssembly_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElementAssemblyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElementAssemblyType_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEngineTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEngine_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEngineTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEngineType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEvaporativeCoolerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEvaporativeCooler_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEvaporatorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEvaporator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEvaporatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEvaporatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEventTypeEnum_type), true));
        attributes.push_back(new entity::attribute("EventTriggerType", new named_type(IfcEventTriggerTypeEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedEventTriggerType", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("EventOccurenceTime", new named_type(IfcEventTime_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEvent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ActualDate", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("EarlyDate", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("LateDate", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ScheduleDate", new named_type(IfcDateTime_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEventTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEventTypeEnum_type), false));
        attributes.push_back(new entity::attribute("EventTriggerType", new named_type(IfcEventTriggerTypeEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedEventTriggerType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEventType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Properties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExtendedProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcExternalInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Location", new named_type(IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternalReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingReference", new named_type(IfcExternalReference_type), false));
        attributes.push_back(new entity::attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcResourceObjectSelect_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternalReferenceRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcExternalSpatialElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternalSpatialElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternalSpatialStructureElement_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("EndSweptArea", new named_type(IfcProfileDef_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExtrudedAreaSolidTapered_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("Orientation", new named_type(IfcBoolean_type), false));
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
        attributes.push_back(new entity::attribute("SameSense", new named_type(IfcBoolean_type), false));
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFanTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFan_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFanTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFanType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFastenerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFastener_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFastenerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("FillStyles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcFillStyleSelect_type)), false));
        attributes.push_back(new entity::attribute("ModelorDraughting", new named_type(IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TilingPattern", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IfcVector_type)), false));
        attributes.push_back(new entity::attribute("Tiles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcStyledItem_type)), false));
        attributes.push_back(new entity::attribute("TilingScale", new named_type(IfcPositiveRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFillAreaStyleTiles_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFilterTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFilter_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFireSuppressionTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFireSuppressionTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFireSuppressionTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFireSuppressionTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("FixedReference", new named_type(IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFixedReferenceSweptAreaSolid_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFlowInstrumentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowInstrument_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFlowMeterTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowMeter_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFootingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFooting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFootingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFootingType_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFurnitureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFurniture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AssemblyPlace", new named_type(IfcAssemblyPlaceEnum_type), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFurnitureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFurnitureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcGeographicElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGeographicElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcGeographicElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGeographicElementType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("Precision", new named_type(IfcReal_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("UAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("VAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("WAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcGridAxis_type)), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcGridTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("PlacementRefDirection", new named_type(IfcGridPlacementDirectionSelect_type), true));
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
        attributes.push_back(new entity::attribute("AgreementFlag", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcHalfSpaceSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcHeatExchangerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcHeatExchanger_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcHumidifierTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcHumidifier_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcHumidifierTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcHumidifierType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("OverallDepth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeEdgeRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcIShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("URLReference", new named_type(IfcURIReference_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcImageTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("MappedTo", new named_type(IfcTessellatedFaceSet_type), false));
        attributes.push_back(new entity::attribute("Opacity", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Colours", new named_type(IfcColourRgbList_type), false));
        attributes.push_back(new entity::attribute("ColourIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcPositiveInteger_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcIndexedColourMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Points", new named_type(IfcCartesianPointList_type), false));
        attributes.push_back(new entity::attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcSegmentIndexSelect_type)), true));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcIndexedPolyCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MappedTo", new named_type(IfcTessellatedFaceSet_type), false));
        attributes.push_back(new entity::attribute("TexCoords", new named_type(IfcTextureVertexList_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcIndexedTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TexCoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IfcPositiveInteger_type))), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcIndexedTriangleTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcInterceptorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcInterceptor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcInterceptorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcInterceptorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcInventoryTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Jurisdiction", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("ResponsiblePersons", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPerson_type)), true));
        attributes.push_back(new entity::attribute("LastUpdateDate", new named_type(IfcDate_type), true));
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
        attributes.push_back(new entity::attribute("TimeStamp", new named_type(IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcIrregularTimeSeriesValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcJunctionBoxTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcJunctionBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcJunctionBoxTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcJunctionBoxType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Width", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Thickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LegSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcLaborResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLaborResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcLaborResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLaborResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LagValue", new named_type(IfcTimeOrRatioSelect_type), false));
        attributes.push_back(new entity::attribute("DurationType", new named_type(IfcTaskDurationEnum_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLagTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcLampTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLamp_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcLampTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLampType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Version", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Publisher", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("VersionDate", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("Location", new named_type(IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLibraryInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Language", new named_type(IfcLanguageId_type), true));
        attributes.push_back(new entity::attribute("ReferencedLibrary", new named_type(IfcLibraryInformation_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcLightFixtureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightFixture_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PlacementRelTo", new named_type(IfcObjectPlacement_type), true));
        attributes.push_back(new entity::attribute("RelativePlacement", new named_type(IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcLocalPlacement_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Eastings", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Northings", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("OrthogonalHeight", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("XAxisAbscissa", new named_type(IfcReal_type), true));
        attributes.push_back(new entity::attribute("XAxisOrdinate", new named_type(IfcReal_type), true));
        attributes.push_back(new entity::attribute("Scale", new named_type(IfcReal_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMapConversion_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterial_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MaterialClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcClassificationSelect_type)), false));
        attributes.push_back(new entity::attribute("ClassifiedMaterial", new named_type(IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcMaterialClassificationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Material", new named_type(IfcMaterial_type), false));
        attributes.push_back(new entity::attribute("Fraction", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialConstituent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("MaterialConstituents", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcMaterialConstituent_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialConstituentSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcMaterialDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RepresentedMaterial", new named_type(IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialDefinitionRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Material", new named_type(IfcMaterial_type), true));
        attributes.push_back(new entity::attribute("LayerThickness", new named_type(IfcNonNegativeLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("IsVentilated", new named_type(IfcLogical_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Priority", new named_type(IfcInteger_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialLayer_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MaterialLayers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcMaterialLayer_type)), false));
        attributes.push_back(new entity::attribute("LayerSetName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialLayerSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ForLayerSet", new named_type(IfcMaterialLayerSet_type), false));
        attributes.push_back(new entity::attribute("LayerSetDirection", new named_type(IfcLayerSetDirectionEnum_type), false));
        attributes.push_back(new entity::attribute("DirectionSense", new named_type(IfcDirectionSenseEnum_type), false));
        attributes.push_back(new entity::attribute("OffsetFromReferenceLine", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ReferenceExtent", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialLayerSetUsage_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OffsetDirection", new named_type(IfcLayerSetDirectionEnum_type), false));
        attributes.push_back(new entity::attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialLayerWithOffsets_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Materials", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcMaterial_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcMaterialList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Material", new named_type(IfcMaterial_type), true));
        attributes.push_back(new entity::attribute("Profile", new named_type(IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Priority", new named_type(IfcInteger_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialProfile_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("MaterialProfiles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcMaterialProfile_type)), false));
        attributes.push_back(new entity::attribute("CompositeProfile", new named_type(IfcCompositeProfileDef_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialProfileSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ForProfileSet", new named_type(IfcMaterialProfileSet_type), false));
        attributes.push_back(new entity::attribute("CardinalPoint", new named_type(IfcCardinalPointReference_type), true));
        attributes.push_back(new entity::attribute("ReferenceExtent", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialProfileSetUsage_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ForProfileEndSet", new named_type(IfcMaterialProfileSet_type), false));
        attributes.push_back(new entity::attribute("CardinalEndPoint", new named_type(IfcCardinalPointReference_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialProfileSetUsageTapering_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialProfileWithOffsets_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Material", new named_type(IfcMaterialDefinition_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingMaterial", new named_type(IfcMaterial_type), false));
        attributes.push_back(new entity::attribute("RelatedMaterials", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcMaterial_type)), false));
        attributes.push_back(new entity::attribute("Expression", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcMaterialUsageDefinition_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalLength", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMechanicalFastenerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMechanicalFastener_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMechanicalFastenerTypeEnum_type), false));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalLength", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMechanicalFastenerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMedicalDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMedicalDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMedicalDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMedicalDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMemberTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMemberStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMemberTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMemberType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Benchmark", new named_type(IfcBenchmarkEnum_type), false));
        attributes.push_back(new entity::attribute("ValueSource", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DataValue", new named_type(IfcMetricValueSelect_type), true));
        attributes.push_back(new entity::attribute("ReferencePath", new named_type(IfcReference_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMetric_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(false);
        IfcMirroredProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Currency", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcMonetaryUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMotorConnectionTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMotorConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMotorConnectionTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMotorConnectionType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("BenchmarkValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcConstraint_type)), true));
        attributes.push_back(new entity::attribute("LogicalAggregator", new named_type(IfcLogicalOperatorEnum_type), true));
        attributes.push_back(new entity::attribute("ObjectiveQualifier", new named_type(IfcObjectiveEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedQualifier", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcObjective_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcOccupantTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOccupant_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Distance", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IfcLogical_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOffsetCurve2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Distance", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IfcLogical_type), false));
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOffsetCurve3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcOpenShell_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcOpeningElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOpeningElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOpeningStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcActorRole_type)), true));
        attributes.push_back(new entity::attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcAddress_type)), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOrganization_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingOrganization", new named_type(IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("RelatedOrganizations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcOrganization_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOrganizationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeElement", new named_type(IfcEdge_type), false));
        attributes.push_back(new entity::attribute("Orientation", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false);
        IfcOrientedEdge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcOuterBoundaryCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcOutletTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOutlet_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("ChangeAction", new named_type(IfcChangeActionEnum_type), true));
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
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement2D_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IfcSurface_type), false));
        attributes.push_back(new entity::attribute("ReferenceCurve", new named_type(IfcCurve_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcPcurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LifeCyclePhase", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPerformanceHistoryTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPermitTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPermit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPileTypeEnum_type), true));
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IfcPileConstructionEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPile_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPileTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPileType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPipeFittingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPipeFitting_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPipeSegmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPipeSegment_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("Pixel", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcBinary_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPlateTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPlate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPlateStandardCase_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcPreDefinedProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPreDefinedPropertySet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcPresentationItem_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("LayerOn", new named_type(IfcLogical_type), false));
        attributes.push_back(new entity::attribute("LayerFrozen", new named_type(IfcLogical_type), false));
        attributes.push_back(new entity::attribute("LayerBlocked", new named_type(IfcLogical_type), false));
        attributes.push_back(new entity::attribute("LayerStyles", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IfcPresentationStyle_type)), false));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProcedureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProcedure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProcedureTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProcedureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProfileType", new named_type(IfcProfileTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ProfileName", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ProfileDefinition", new named_type(IfcProfileDef_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProjectLibrary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProjectOrderTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProjectOrder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MapProjection", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("MapZone", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("MapUnit", new named_type(IfcNamedUnit_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProjectedCRS_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProjectionElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcPropertyAbstraction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("UpperBoundValue", new named_type(IfcValue_type), true));
        attributes.push_back(new entity::attribute("LowerBoundValue", new named_type(IfcValue_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        attributes.push_back(new entity::attribute("SetPointValue", new named_type(IfcValue_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyBoundedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("DependingProperty", new named_type(IfcProperty_type), false));
        attributes.push_back(new entity::attribute("DependantProperty", new named_type(IfcProperty_type), false));
        attributes.push_back(new entity::attribute("Expression", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyDependencyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), true));
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
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyListValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("PropertyReference", new named_type(IfcObjectReferenceSelect_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TemplateType", new named_type(IfcPropertySetTemplateTypeEnum_type), true));
        attributes.push_back(new entity::attribute("ApplicableEntity", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPropertyTemplate_type)), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertySetTemplate_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("DefiningValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), true));
        attributes.push_back(new entity::attribute("DefinedValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), true));
        attributes.push_back(new entity::attribute("Expression", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("DefiningUnit", new named_type(IfcUnit_type), true));
        attributes.push_back(new entity::attribute("DefinedUnit", new named_type(IfcUnit_type), true));
        attributes.push_back(new entity::attribute("CurveInterpolation", new named_type(IfcCurveInterpolationEnum_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyTableValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyTemplate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyTemplateDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProtectiveDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProtectiveDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProtectiveDeviceTrippingUnitTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProtectiveDeviceTrippingUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProtectiveDeviceTrippingUnitTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProtectiveDeviceTrippingUnitType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPumpTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPump_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPumpTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPumpType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AreaValue", new named_type(IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityArea_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CountValue", new named_type(IfcCountMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityCount_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LengthValue", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityLength_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantitySet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TimeValue", new named_type(IfcTimeMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VolumeValue", new named_type(IfcVolumeMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityVolume_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("WeightValue", new named_type(IfcMassMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityWeight_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcRampTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRamp_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcRampFlightTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcRampTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRampType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcReal_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRationalBSplineCurveWithKnots_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcReal_type))), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRationalBSplineSurfaceWithKnots_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InnerFilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OuterFilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
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
        attributes.push_back(new entity::attribute("Usense", new named_type(IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Vsense", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRectangularTrimmedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("RecurrenceType", new named_type(IfcRecurrenceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("DayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDayInMonthNumber_type)), true));
        attributes.push_back(new entity::attribute("WeekdayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDayInWeekNumber_type)), true));
        attributes.push_back(new entity::attribute("MonthComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcMonthInYearNumber_type)), true));
        attributes.push_back(new entity::attribute("Position", new named_type(IfcInteger_type), true));
        attributes.push_back(new entity::attribute("Interval", new named_type(IfcInteger_type), true));
        attributes.push_back(new entity::attribute("Occurrences", new named_type(IfcInteger_type), true));
        attributes.push_back(new entity::attribute("TimePeriods", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcTimePeriod_type)), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRecurrencePattern_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("TypeIdentifier", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("AttributeIdentifier", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("InstanceName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ListPositions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcInteger_type)), true));
        attributes.push_back(new entity::attribute("InnerReference", new named_type(IfcReference_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReference_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("BarLength", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcReinforcingBarTypeEnum_type), true));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IfcReinforcingBarSurfaceEnum_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingBar_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcReinforcingBarTypeEnum_type), false));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("BarLength", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IfcReinforcingBarSurfaceEnum_type), true));
        attributes.push_back(new entity::attribute("BendingShapeCode", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcBendingParameterSelect_type)), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingBarType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SteelGrade", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("MeshLength", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MeshWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarNominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarNominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarCrossSectionArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarCrossSectionArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarSpacing", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarSpacing", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcReinforcingMeshTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingMesh_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(11);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcReinforcingMeshTypeEnum_type), false));
        attributes.push_back(new entity::attribute("MeshLength", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MeshWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarNominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarNominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarCrossSectionArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarCrossSectionArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarSpacing", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarSpacing", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BendingShapeCode", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcBendingParameterSelect_type)), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingMeshType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingObject", new named_type(IfcObjectDefinition_type), false));
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcObjectDefinition_type)), false));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Factor", new named_type(IfcRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToGroupByFactor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingProcess", new named_type(IfcProcessSelect_type), false));
        attributes.push_back(new entity::attribute("QuantityInProcess", new named_type(IfcMeasureWithUnit_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToProcess_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingProduct", new named_type(IfcProductSelect_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingResource", new named_type(IfcResourceSelect_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDefinitionSelect_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociates_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("RelatingClassification", new named_type(IfcClassificationSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesClassification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Intent", new named_type(IfcLabel_type), true));
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
        attributes.push_back(new entity::attribute("RelatingPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("RelatedPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("RelatedConnectionType", new named_type(IfcConnectionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("RelatingConnectionType", new named_type(IfcConnectionTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsPathElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingPort", new named_type(IfcPort_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IfcDistributionElement_type), false));
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
        attributes.push_back(new entity::attribute("RelatingStructure", new named_type(IfcSpatialElement_type), false));
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
        attributes.push_back(new entity::attribute("RelatingSpace", new named_type(IfcSpace_type), false));
        attributes.push_back(new entity::attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcCovering_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelCoversSpaces_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingContext", new named_type(IfcContext_type), false));
        attributes.push_back(new entity::attribute("RelatedDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDefinitionSelect_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDeclares_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDecomposes_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDefines_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcObject_type)), false));
        attributes.push_back(new entity::attribute("RelatingObject", new named_type(IfcObject_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDefinesByObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcObjectDefinition_type)), false));
        attributes.push_back(new entity::attribute("RelatingPropertyDefinition", new named_type(IfcPropertySetDefinitionSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDefinesByProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPropertySetDefinition_type)), false));
        attributes.push_back(new entity::attribute("RelatingTemplate", new named_type(IfcPropertySetTemplate_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDefinesByTemplate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcObject_type)), false));
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
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IfcElement_type), false));
        attributes.push_back(new entity::attribute("InterferenceGeometry", new named_type(IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("InterferenceType", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("ImpliedOrder", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelInterferesElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingObject", new named_type(IfcObjectDefinition_type), false));
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcObjectDefinition_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelNests_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("RelatingStructure", new named_type(IfcSpatialElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelReferencedInSpatialStructure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingProcess", new named_type(IfcProcess_type), false));
        attributes.push_back(new entity::attribute("RelatedProcess", new named_type(IfcProcess_type), false));
        attributes.push_back(new entity::attribute("TimeLag", new named_type(IfcLagTime_type), true));
        attributes.push_back(new entity::attribute("SequenceType", new named_type(IfcSequenceEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedSequenceType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelSequence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingSystem", new named_type(IfcSystem_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcSpatialElement_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelServicesBuildings_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingSpace", new named_type(IfcSpaceBoundarySelect_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildingElement", new named_type(IfcElement_type), false));
        attributes.push_back(new entity::attribute("ConnectionGeometry", new named_type(IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("PhysicalOrVirtualBoundary", new named_type(IfcPhysicalOrVirtualEnum_type), false));
        attributes.push_back(new entity::attribute("InternalOrExternalBoundary", new named_type(IfcInternalOrExternalEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelSpaceBoundary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ParentBoundary", new named_type(IfcRelSpaceBoundary1stLevel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelSpaceBoundary1stLevel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CorrespondingBoundary", new named_type(IfcRelSpaceBoundary2ndLevel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelSpaceBoundary2ndLevel_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ParamLength", new named_type(IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReparametrisedCompositeCurveSegment_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcResourceObjectSelect_type)), false));
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IfcApproval_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcResourceApprovalRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcResourceObjectSelect_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcResourceConstraintRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcResourceLevelRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(15);
        attributes.push_back(new entity::attribute("ScheduleWork", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("ScheduleUsage", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ScheduleStart", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ScheduleFinish", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ScheduleContour", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LevelingDelay", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("IsOverAllocated", new named_type(IfcBoolean_type), true));
        attributes.push_back(new entity::attribute("StatusTime", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ActualWork", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("ActualUsage", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ActualStart", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ActualFinish", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("RemainingWork", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("RemainingUsage", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Completion", new named_type(IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcResourceTime_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EndSweptArea", new named_type(IfcProfileDef_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRevolvedAreaSolidTapered_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcRoofTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRoof_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcRoofTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRoofType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("GlobalId", new named_type(IfcGloballyUniqueId_type), false));
        attributes.push_back(new entity::attribute("OwnerHistory", new named_type(IfcOwnerHistory_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRoot_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSanitaryTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSanitaryTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSanitaryTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSanitaryTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DataOrigin", new named_type(IfcDataOriginEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedDataOrigin", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSchedulingTime_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSensorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSensor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSensorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSensorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcShadingDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcShadingDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcShadingDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcShadingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ShapeRepresentations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcShapeModel_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ProductDefinitional", new named_type(IfcLogical_type), false));
        attributes.push_back(new entity::attribute("PartOfProductDefinitionShape", new named_type(IfcProductRepresentationSelect_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("TemplateType", new named_type(IfcSimplePropertyTemplateTypeEnum_type), true));
        attributes.push_back(new entity::attribute("PrimaryMeasureType", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("SecondaryMeasureType", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Enumerators", new named_type(IfcPropertyEnumeration_type), true));
        attributes.push_back(new entity::attribute("PrimaryUnit", new named_type(IfcUnit_type), true));
        attributes.push_back(new entity::attribute("SecondaryUnit", new named_type(IfcUnit_type), true));
        attributes.push_back(new entity::attribute("Expression", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("AccessState", new named_type(IfcStateEnum_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSimplePropertyTemplate_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSlabElementedCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSlabStandardCase_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSolarDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSolarDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSolarDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSolarDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcSolidModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSpaceTypeEnum_type), true));
        attributes.push_back(new entity::attribute("ElevationWithFlooring", new named_type(IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSpaceHeaterTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpaceHeater_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSpaceHeaterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpaceHeaterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSpaceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpaceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpatialElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ElementType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpatialElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CompositionType", new named_type(IfcElementCompositionEnum_type), true));
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSpatialZoneTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpatialZone_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSpatialZoneTypeEnum_type), false));
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpatialZoneType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStackTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStackTerminal_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStairTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStair_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("NumberOfRisers", new named_type(IfcInteger_type), true));
        attributes.push_back(new entity::attribute("NumberOfTreads", new named_type(IfcInteger_type), true));
        attributes.push_back(new entity::attribute("RiserHeight", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TreadLength", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStairFlightTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStairTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStairType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("DestabilizingLoad", new named_type(IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAnalysisModelTypeEnum_type), false));
        attributes.push_back(new entity::attribute("OrientationOf2DPlane", new named_type(IfcAxis2Placement3D_type), true));
        attributes.push_back(new entity::attribute("LoadedBy", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcStructuralLoadGroup_type)), true));
        attributes.push_back(new entity::attribute("HasResults", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcStructuralResultGroup_type)), true));
        attributes.push_back(new entity::attribute("SharedPlacement", new named_type(IfcObjectPlacement_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProjectedOrTrue", new named_type(IfcProjectedOrTrueLengthEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStructuralCurveActivityTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralCurveAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Axis", new named_type(IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralCurveConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStructuralCurveMemberTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Axis", new named_type(IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralCurveMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralCurveMemberVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStructuralCurveActivityTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralCurveReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLinearAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcStructuralLoad_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SelfWeightCoefficients", new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IfcRatioMeasure_type)), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcStructuralLoadOrResult_type)), false));
        attributes.push_back(new entity::attribute("Locations", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IfcLengthMeasure_type))), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadConfiguration_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcStructuralLoadOrResult_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("DeltaTConstant", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("DeltaTY", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("DeltaTZ", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPlanarAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPointAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ConditionCoordinateSystem", new named_type(IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPointConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPointReaction_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("IsLinear", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralResultGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProjectedOrTrue", new named_type(IfcProjectedOrTrueLengthEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStructuralSurfaceActivityTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSurfaceAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSurfaceConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStructuralSurfaceMemberTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Thickness", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSurfaceMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSurfaceMemberVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStructuralSurfaceActivityTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSurfaceReaction_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcStyleAssignmentSelect_type)), false));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSubContractResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSubContractResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSubContractResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSubContractResourceType_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("StartParam", new named_type(IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("ReferenceSurface", new named_type(IfcSurface_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceCurveSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSurfaceFeatureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceFeature_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SurfaceReinforcement1", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IfcLengthMeasure_type)), true));
        attributes.push_back(new entity::attribute("SurfaceReinforcement2", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IfcLengthMeasure_type)), true));
        attributes.push_back(new entity::attribute("ShearReinforcement", new named_type(IfcRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceReinforcementArea_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SurfaceColour", new named_type(IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("Transparency", new named_type(IfcNormalisedRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RepeatS", new named_type(IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("RepeatT", new named_type(IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Mode", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("TextureTransform", new named_type(IfcCartesianTransformationOperator2D_type), true));
        attributes.push_back(new entity::attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcIdentifier_type)), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SweptArea", new named_type(IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InnerRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IfcParameterValue_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSweptDiskSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSweptDiskSolidPolygonal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SweptCurve", new named_type(IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcSweptSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSwitchingDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSwitchingDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSwitchingDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSwitchingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSystemFurnitureElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSystemFurnitureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSystemFurnitureElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSystemFurnitureElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeEdgeRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("WebEdgeRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("WebSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Rows", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcTableRow_type)), true));
        attributes.push_back(new entity::attribute("Columns", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcTableColumn_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTable_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Identifier", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        attributes.push_back(new entity::attribute("ReferencePath", new named_type(IfcReference_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTableColumn_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RowCells", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), true));
        attributes.push_back(new entity::attribute("IsHeading", new named_type(IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcTableRow_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTankTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTank_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTankTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTankType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("WorkMethod", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("IsMilestone", new named_type(IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Priority", new named_type(IfcInteger_type), true));
        attributes.push_back(new entity::attribute("TaskTime", new named_type(IfcTaskTime_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTaskTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTask_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new entity::attribute("DurationType", new named_type(IfcTaskDurationEnum_type), true));
        attributes.push_back(new entity::attribute("ScheduleDuration", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("ScheduleStart", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ScheduleFinish", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("EarlyStart", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("EarlyFinish", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("LateStart", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("LateFinish", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("FreeFloat", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("TotalFloat", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("IsCritical", new named_type(IfcBoolean_type), true));
        attributes.push_back(new entity::attribute("StatusTime", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ActualDuration", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("ActualStart", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ActualFinish", new named_type(IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("RemainingTime", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("Completion", new named_type(IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTaskTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Recurrence", new named_type(IfcRecurrencePattern_type), false));
        std::vector<bool> derived; derived.reserve(21);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTaskTimeRecurring_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTaskTypeEnum_type), false));
        attributes.push_back(new entity::attribute("WorkMethod", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTaskType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TelephoneNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("FacsimileNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PagerNumber", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ElectronicMailAddresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("WWWHomePageURL", new named_type(IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("MessagingIDs", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcURIReference_type)), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTelecomAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTendonTypeEnum_type), true));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IfcAreaMeasure_type), true));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTendonAnchorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTendonAnchor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTendonAnchorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTendonAnchorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTendonTypeEnum_type), false));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("SheethDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTendonType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Coordinates", new named_type(IfcCartesianPointList3D_type), false));
        attributes.push_back(new entity::attribute("Normals", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IfcParameterValue_type))), true));
        attributes.push_back(new entity::attribute("Closed", new named_type(IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTessellatedFaceSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcTessellatedItem_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("TextCharacterAppearance", new named_type(IfcTextStyleForDefinedFont_type), true));
        attributes.push_back(new entity::attribute("TextStyle", new named_type(IfcTextStyleTextModel_type), true));
        attributes.push_back(new entity::attribute("TextFontStyle", new named_type(IfcTextFontSelect_type), false));
        attributes.push_back(new entity::attribute("ModelOrDraughting", new named_type(IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTextStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("FontFamily", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcTextFontName_type)), false));
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Maps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcSurfaceTexture_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcTextureCoordinate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Mode", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcReal_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTextureCoordinateGenerator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Vertices", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IfcTextureVertex_type)), false));
        attributes.push_back(new entity::attribute("MappedTo", new named_type(IfcFace_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TexCoordsList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IfcParameterValue_type))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcTextureVertexList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("StartTime", new named_type(IfcTime_type), false));
        attributes.push_back(new entity::attribute("EndTime", new named_type(IfcTime_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcTimePeriod_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("StartTime", new named_type(IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("EndTime", new named_type(IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("TimeSeriesDataType", new named_type(IfcTimeSeriesDataTypeEnum_type), false));
        attributes.push_back(new entity::attribute("DataOrigin", new named_type(IfcDataOriginEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedDataOrigin", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTimeSeries_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTransformerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTransformer_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTransformerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTransformerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTransportElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IfcPositiveInteger_type))), false));
        attributes.push_back(new entity::attribute("NormalIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IfcPositiveInteger_type))), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTriangulatedFaceSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Trim1", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IfcTrimmingSelect_type)), false));
        attributes.push_back(new entity::attribute("Trim2", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IfcTrimmingSelect_type)), false));
        attributes.push_back(new entity::attribute("SenseAgreement", new named_type(IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("MasterRepresentation", new named_type(IfcTrimmingPreference_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTrimmedCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTubeBundleTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTubeBundle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTubeBundleTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTubeBundleType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ApplicableOccurrence", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("HasPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPropertySetDefinition_type)), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTypeObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ProcessType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTypeProcess_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Identification", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ResourceType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTypeResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcUnitaryControlElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcUnitaryControlElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcUnitaryControlElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcUnitaryControlElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcUnitaryEquipmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcUnitaryEquipment_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcValveTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcValve_type->set_attributes(attributes, derived);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcVibrationIsolatorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcVibrationIsolator_type->set_attributes(attributes, derived);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcVoidingFeatureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcVoidingFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWallTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWall_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWallElementedCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWasteTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWasteTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWasteTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWasteTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWindowTypeEnum_type), true));
        attributes.push_back(new entity::attribute("PartitioningType", new named_type(IfcWindowTypePartitioningEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPartitioningType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWindow_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::attribute("LiningDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningThickness", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomThickness", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MullionThickness", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FirstTransomOffset", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SecondTransomOffset", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("FirstMullionOffset", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SecondMullionOffset", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IfcShapeAspect_type), true));
        attributes.push_back(new entity::attribute("LiningOffset", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningToPanelOffsetX", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningToPanelOffsetY", new named_type(IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
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
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWindowStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IfcWindowStyleConstructionEnum_type), false));
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcWindowStyleOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new named_type(IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Sizeable", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWindowStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWindowTypeEnum_type), false));
        attributes.push_back(new entity::attribute("PartitioningType", new named_type(IfcWindowTypePartitioningEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new named_type(IfcBoolean_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPartitioningType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWindowType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("WorkingTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcWorkTime_type)), true));
        attributes.push_back(new entity::attribute("ExceptionTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcWorkTime_type)), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWorkCalendarTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWorkCalendar_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("CreationDate", new named_type(IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("Creators", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPerson_type)), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Duration", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("TotalFloat", new named_type(IfcDuration_type), true));
        attributes.push_back(new entity::attribute("StartTime", new named_type(IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("FinishTime", new named_type(IfcDateTime_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWorkControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWorkPlanTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWorkPlan_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWorkScheduleTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWorkSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RecurrencePattern", new named_type(IfcRecurrencePattern_type), true));
        attributes.push_back(new entity::attribute("Start", new named_type(IfcDate_type), true));
        attributes.push_back(new entity::attribute("Finish", new named_type(IfcDate_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWorkTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IfcNonNegativeLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcZShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcZone_type->set_attributes(attributes, derived);
    }

    std::vector<const declaration*> declarations; declarations.reserve(1165);
    declarations.push_back(IfcAbsorbedDoseMeasure_type);
    declarations.push_back(IfcAccelerationMeasure_type);
    declarations.push_back(IfcAmountOfSubstanceMeasure_type);
    declarations.push_back(IfcAngularVelocityMeasure_type);
    declarations.push_back(IfcArcIndex_type);
    declarations.push_back(IfcAreaDensityMeasure_type);
    declarations.push_back(IfcAreaMeasure_type);
    declarations.push_back(IfcBinary_type);
    declarations.push_back(IfcBoolean_type);
    declarations.push_back(IfcCardinalPointReference_type);
    declarations.push_back(IfcComplexNumber_type);
    declarations.push_back(IfcCompoundPlaneAngleMeasure_type);
    declarations.push_back(IfcContextDependentMeasure_type);
    declarations.push_back(IfcCountMeasure_type);
    declarations.push_back(IfcCurvatureMeasure_type);
    declarations.push_back(IfcDate_type);
    declarations.push_back(IfcDateTime_type);
    declarations.push_back(IfcDayInMonthNumber_type);
    declarations.push_back(IfcDayInWeekNumber_type);
    declarations.push_back(IfcDescriptiveMeasure_type);
    declarations.push_back(IfcDimensionCount_type);
    declarations.push_back(IfcDoseEquivalentMeasure_type);
    declarations.push_back(IfcDuration_type);
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
    declarations.push_back(IfcIdentifier_type);
    declarations.push_back(IfcIlluminanceMeasure_type);
    declarations.push_back(IfcInductanceMeasure_type);
    declarations.push_back(IfcInteger_type);
    declarations.push_back(IfcIntegerCountRateMeasure_type);
    declarations.push_back(IfcIonConcentrationMeasure_type);
    declarations.push_back(IfcIsothermalMoistureCapacityMeasure_type);
    declarations.push_back(IfcKinematicViscosityMeasure_type);
    declarations.push_back(IfcLabel_type);
    declarations.push_back(IfcLanguageId_type);
    declarations.push_back(IfcLengthMeasure_type);
    declarations.push_back(IfcLineIndex_type);
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
    declarations.push_back(IfcModulusOfElasticityMeasure_type);
    declarations.push_back(IfcModulusOfLinearSubgradeReactionMeasure_type);
    declarations.push_back(IfcModulusOfRotationalSubgradeReactionMeasure_type);
    declarations.push_back(IfcModulusOfSubgradeReactionMeasure_type);
    declarations.push_back(IfcMoistureDiffusivityMeasure_type);
    declarations.push_back(IfcMolecularWeightMeasure_type);
    declarations.push_back(IfcMomentOfInertiaMeasure_type);
    declarations.push_back(IfcMonetaryMeasure_type);
    declarations.push_back(IfcMonthInYearNumber_type);
    declarations.push_back(IfcNonNegativeLengthMeasure_type);
    declarations.push_back(IfcNumericMeasure_type);
    declarations.push_back(IfcPHMeasure_type);
    declarations.push_back(IfcParameterValue_type);
    declarations.push_back(IfcPlanarForceMeasure_type);
    declarations.push_back(IfcPlaneAngleMeasure_type);
    declarations.push_back(IfcPositiveInteger_type);
    declarations.push_back(IfcPositiveLengthMeasure_type);
    declarations.push_back(IfcPositivePlaneAngleMeasure_type);
    declarations.push_back(IfcPowerMeasure_type);
    declarations.push_back(IfcPresentableText_type);
    declarations.push_back(IfcPressureMeasure_type);
    declarations.push_back(IfcPropertySetDefinitionSet_type);
    declarations.push_back(IfcRadioActivityMeasure_type);
    declarations.push_back(IfcRatioMeasure_type);
    declarations.push_back(IfcReal_type);
    declarations.push_back(IfcRotationalFrequencyMeasure_type);
    declarations.push_back(IfcRotationalMassMeasure_type);
    declarations.push_back(IfcRotationalStiffnessMeasure_type);
    declarations.push_back(IfcSectionModulusMeasure_type);
    declarations.push_back(IfcSectionalAreaIntegralMeasure_type);
    declarations.push_back(IfcShearModulusMeasure_type);
    declarations.push_back(IfcSolidAngleMeasure_type);
    declarations.push_back(IfcSoundPowerLevelMeasure_type);
    declarations.push_back(IfcSoundPowerMeasure_type);
    declarations.push_back(IfcSoundPressureLevelMeasure_type);
    declarations.push_back(IfcSoundPressureMeasure_type);
    declarations.push_back(IfcSpecificHeatCapacityMeasure_type);
    declarations.push_back(IfcSpecularExponent_type);
    declarations.push_back(IfcSpecularRoughness_type);
    declarations.push_back(IfcStrippedOptional_type);
    declarations.push_back(IfcTemperatureGradientMeasure_type);
    declarations.push_back(IfcTemperatureRateOfChangeMeasure_type);
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
    declarations.push_back(IfcTime_type);
    declarations.push_back(IfcTimeMeasure_type);
    declarations.push_back(IfcTimeStamp_type);
    declarations.push_back(IfcTorqueMeasure_type);
    declarations.push_back(IfcURIReference_type);
    declarations.push_back(IfcVaporPermeabilityMeasure_type);
    declarations.push_back(IfcVolumeMeasure_type);
    declarations.push_back(IfcVolumetricFlowRateMeasure_type);
    declarations.push_back(IfcWarpingConstantMeasure_type);
    declarations.push_back(IfcWarpingMomentMeasure_type);
    declarations.push_back(IfcBoxAlignment_type);
    declarations.push_back(IfcNormalisedRatioMeasure_type);
    declarations.push_back(IfcPositiveRatioMeasure_type);
    declarations.push_back(IfcActionRequestTypeEnum_type);
    declarations.push_back(IfcActionSourceTypeEnum_type);
    declarations.push_back(IfcActionTypeEnum_type);
    declarations.push_back(IfcActuatorTypeEnum_type);
    declarations.push_back(IfcAddressTypeEnum_type);
    declarations.push_back(IfcAirTerminalBoxTypeEnum_type);
    declarations.push_back(IfcAirTerminalTypeEnum_type);
    declarations.push_back(IfcAirToAirHeatRecoveryTypeEnum_type);
    declarations.push_back(IfcAlarmTypeEnum_type);
    declarations.push_back(IfcAnalysisModelTypeEnum_type);
    declarations.push_back(IfcAnalysisTheoryTypeEnum_type);
    declarations.push_back(IfcArithmeticOperatorEnum_type);
    declarations.push_back(IfcAssemblyPlaceEnum_type);
    declarations.push_back(IfcAudioVisualApplianceTypeEnum_type);
    declarations.push_back(IfcBSplineCurveForm_type);
    declarations.push_back(IfcBSplineSurfaceForm_type);
    declarations.push_back(IfcBeamTypeEnum_type);
    declarations.push_back(IfcBenchmarkEnum_type);
    declarations.push_back(IfcBoilerTypeEnum_type);
    declarations.push_back(IfcBooleanOperator_type);
    declarations.push_back(IfcBuildingElementPartTypeEnum_type);
    declarations.push_back(IfcBuildingElementProxyTypeEnum_type);
    declarations.push_back(IfcBuildingSystemTypeEnum_type);
    declarations.push_back(IfcBurnerTypeEnum_type);
    declarations.push_back(IfcCableCarrierFittingTypeEnum_type);
    declarations.push_back(IfcCableCarrierSegmentTypeEnum_type);
    declarations.push_back(IfcCableFittingTypeEnum_type);
    declarations.push_back(IfcCableSegmentTypeEnum_type);
    declarations.push_back(IfcChangeActionEnum_type);
    declarations.push_back(IfcChillerTypeEnum_type);
    declarations.push_back(IfcChimneyTypeEnum_type);
    declarations.push_back(IfcCoilTypeEnum_type);
    declarations.push_back(IfcColumnTypeEnum_type);
    declarations.push_back(IfcCommunicationsApplianceTypeEnum_type);
    declarations.push_back(IfcComplexPropertyTemplateTypeEnum_type);
    declarations.push_back(IfcCompressorTypeEnum_type);
    declarations.push_back(IfcCondenserTypeEnum_type);
    declarations.push_back(IfcConnectionTypeEnum_type);
    declarations.push_back(IfcConstraintEnum_type);
    declarations.push_back(IfcConstructionEquipmentResourceTypeEnum_type);
    declarations.push_back(IfcConstructionMaterialResourceTypeEnum_type);
    declarations.push_back(IfcConstructionProductResourceTypeEnum_type);
    declarations.push_back(IfcControllerTypeEnum_type);
    declarations.push_back(IfcCooledBeamTypeEnum_type);
    declarations.push_back(IfcCoolingTowerTypeEnum_type);
    declarations.push_back(IfcCostItemTypeEnum_type);
    declarations.push_back(IfcCostScheduleTypeEnum_type);
    declarations.push_back(IfcCoveringTypeEnum_type);
    declarations.push_back(IfcCrewResourceTypeEnum_type);
    declarations.push_back(IfcCurtainWallTypeEnum_type);
    declarations.push_back(IfcCurveInterpolationEnum_type);
    declarations.push_back(IfcDamperTypeEnum_type);
    declarations.push_back(IfcDataOriginEnum_type);
    declarations.push_back(IfcDerivedUnitEnum_type);
    declarations.push_back(IfcDirectionSenseEnum_type);
    declarations.push_back(IfcDiscreteAccessoryTypeEnum_type);
    declarations.push_back(IfcDistributionChamberElementTypeEnum_type);
    declarations.push_back(IfcDistributionPortTypeEnum_type);
    declarations.push_back(IfcDistributionSystemEnum_type);
    declarations.push_back(IfcDocumentConfidentialityEnum_type);
    declarations.push_back(IfcDocumentStatusEnum_type);
    declarations.push_back(IfcDoorPanelOperationEnum_type);
    declarations.push_back(IfcDoorPanelPositionEnum_type);
    declarations.push_back(IfcDoorStyleConstructionEnum_type);
    declarations.push_back(IfcDoorStyleOperationEnum_type);
    declarations.push_back(IfcDoorTypeEnum_type);
    declarations.push_back(IfcDoorTypeOperationEnum_type);
    declarations.push_back(IfcDuctFittingTypeEnum_type);
    declarations.push_back(IfcDuctSegmentTypeEnum_type);
    declarations.push_back(IfcDuctSilencerTypeEnum_type);
    declarations.push_back(IfcElectricApplianceTypeEnum_type);
    declarations.push_back(IfcElectricDistributionBoardTypeEnum_type);
    declarations.push_back(IfcElectricFlowStorageDeviceTypeEnum_type);
    declarations.push_back(IfcElectricGeneratorTypeEnum_type);
    declarations.push_back(IfcElectricMotorTypeEnum_type);
    declarations.push_back(IfcElectricTimeControlTypeEnum_type);
    declarations.push_back(IfcElementAssemblyTypeEnum_type);
    declarations.push_back(IfcElementCompositionEnum_type);
    declarations.push_back(IfcEngineTypeEnum_type);
    declarations.push_back(IfcEvaporativeCoolerTypeEnum_type);
    declarations.push_back(IfcEvaporatorTypeEnum_type);
    declarations.push_back(IfcEventTriggerTypeEnum_type);
    declarations.push_back(IfcEventTypeEnum_type);
    declarations.push_back(IfcExternalSpatialElementTypeEnum_type);
    declarations.push_back(IfcFanTypeEnum_type);
    declarations.push_back(IfcFastenerTypeEnum_type);
    declarations.push_back(IfcFilterTypeEnum_type);
    declarations.push_back(IfcFireSuppressionTerminalTypeEnum_type);
    declarations.push_back(IfcFlowDirectionEnum_type);
    declarations.push_back(IfcFlowInstrumentTypeEnum_type);
    declarations.push_back(IfcFlowMeterTypeEnum_type);
    declarations.push_back(IfcFootingTypeEnum_type);
    declarations.push_back(IfcFurnitureTypeEnum_type);
    declarations.push_back(IfcGeographicElementTypeEnum_type);
    declarations.push_back(IfcGeometricProjectionEnum_type);
    declarations.push_back(IfcGlobalOrLocalEnum_type);
    declarations.push_back(IfcGridTypeEnum_type);
    declarations.push_back(IfcHeatExchangerTypeEnum_type);
    declarations.push_back(IfcHumidifierTypeEnum_type);
    declarations.push_back(IfcInterceptorTypeEnum_type);
    declarations.push_back(IfcInternalOrExternalEnum_type);
    declarations.push_back(IfcInventoryTypeEnum_type);
    declarations.push_back(IfcJunctionBoxTypeEnum_type);
    declarations.push_back(IfcKnotType_type);
    declarations.push_back(IfcLaborResourceTypeEnum_type);
    declarations.push_back(IfcLampTypeEnum_type);
    declarations.push_back(IfcLayerSetDirectionEnum_type);
    declarations.push_back(IfcLightDistributionCurveEnum_type);
    declarations.push_back(IfcLightEmissionSourceEnum_type);
    declarations.push_back(IfcLightFixtureTypeEnum_type);
    declarations.push_back(IfcLoadGroupTypeEnum_type);
    declarations.push_back(IfcLogicalOperatorEnum_type);
    declarations.push_back(IfcMechanicalFastenerTypeEnum_type);
    declarations.push_back(IfcMedicalDeviceTypeEnum_type);
    declarations.push_back(IfcMemberTypeEnum_type);
    declarations.push_back(IfcMotorConnectionTypeEnum_type);
    declarations.push_back(IfcNullStyle_type);
    declarations.push_back(IfcObjectTypeEnum_type);
    declarations.push_back(IfcObjectiveEnum_type);
    declarations.push_back(IfcOccupantTypeEnum_type);
    declarations.push_back(IfcOpeningElementTypeEnum_type);
    declarations.push_back(IfcOutletTypeEnum_type);
    declarations.push_back(IfcPerformanceHistoryTypeEnum_type);
    declarations.push_back(IfcPermeableCoveringOperationEnum_type);
    declarations.push_back(IfcPermitTypeEnum_type);
    declarations.push_back(IfcPhysicalOrVirtualEnum_type);
    declarations.push_back(IfcPileConstructionEnum_type);
    declarations.push_back(IfcPileTypeEnum_type);
    declarations.push_back(IfcPipeFittingTypeEnum_type);
    declarations.push_back(IfcPipeSegmentTypeEnum_type);
    declarations.push_back(IfcPlateTypeEnum_type);
    declarations.push_back(IfcProcedureTypeEnum_type);
    declarations.push_back(IfcProfileTypeEnum_type);
    declarations.push_back(IfcProjectOrderTypeEnum_type);
    declarations.push_back(IfcProjectedOrTrueLengthEnum_type);
    declarations.push_back(IfcProjectionElementTypeEnum_type);
    declarations.push_back(IfcPropertySetTemplateTypeEnum_type);
    declarations.push_back(IfcProtectiveDeviceTrippingUnitTypeEnum_type);
    declarations.push_back(IfcProtectiveDeviceTypeEnum_type);
    declarations.push_back(IfcPumpTypeEnum_type);
    declarations.push_back(IfcRailingTypeEnum_type);
    declarations.push_back(IfcRampFlightTypeEnum_type);
    declarations.push_back(IfcRampTypeEnum_type);
    declarations.push_back(IfcRecurrenceTypeEnum_type);
    declarations.push_back(IfcReflectanceMethodEnum_type);
    declarations.push_back(IfcReinforcingBarRoleEnum_type);
    declarations.push_back(IfcReinforcingBarSurfaceEnum_type);
    declarations.push_back(IfcReinforcingBarTypeEnum_type);
    declarations.push_back(IfcReinforcingMeshTypeEnum_type);
    declarations.push_back(IfcRoleEnum_type);
    declarations.push_back(IfcRoofTypeEnum_type);
    declarations.push_back(IfcSIPrefix_type);
    declarations.push_back(IfcSIUnitName_type);
    declarations.push_back(IfcSanitaryTerminalTypeEnum_type);
    declarations.push_back(IfcSectionTypeEnum_type);
    declarations.push_back(IfcSensorTypeEnum_type);
    declarations.push_back(IfcSequenceEnum_type);
    declarations.push_back(IfcShadingDeviceTypeEnum_type);
    declarations.push_back(IfcSimplePropertyTemplateTypeEnum_type);
    declarations.push_back(IfcSlabTypeEnum_type);
    declarations.push_back(IfcSolarDeviceTypeEnum_type);
    declarations.push_back(IfcSpaceHeaterTypeEnum_type);
    declarations.push_back(IfcSpaceTypeEnum_type);
    declarations.push_back(IfcSpatialZoneTypeEnum_type);
    declarations.push_back(IfcStackTerminalTypeEnum_type);
    declarations.push_back(IfcStairFlightTypeEnum_type);
    declarations.push_back(IfcStairTypeEnum_type);
    declarations.push_back(IfcStateEnum_type);
    declarations.push_back(IfcStructuralCurveActivityTypeEnum_type);
    declarations.push_back(IfcStructuralCurveMemberTypeEnum_type);
    declarations.push_back(IfcStructuralSurfaceActivityTypeEnum_type);
    declarations.push_back(IfcStructuralSurfaceMemberTypeEnum_type);
    declarations.push_back(IfcSubContractResourceTypeEnum_type);
    declarations.push_back(IfcSurfaceFeatureTypeEnum_type);
    declarations.push_back(IfcSurfaceSide_type);
    declarations.push_back(IfcSwitchingDeviceTypeEnum_type);
    declarations.push_back(IfcSystemFurnitureElementTypeEnum_type);
    declarations.push_back(IfcTankTypeEnum_type);
    declarations.push_back(IfcTaskDurationEnum_type);
    declarations.push_back(IfcTaskTypeEnum_type);
    declarations.push_back(IfcTendonAnchorTypeEnum_type);
    declarations.push_back(IfcTendonTypeEnum_type);
    declarations.push_back(IfcTextPath_type);
    declarations.push_back(IfcTimeSeriesDataTypeEnum_type);
    declarations.push_back(IfcTransformerTypeEnum_type);
    declarations.push_back(IfcTransitionCode_type);
    declarations.push_back(IfcTransportElementTypeEnum_type);
    declarations.push_back(IfcTrimmingPreference_type);
    declarations.push_back(IfcTubeBundleTypeEnum_type);
    declarations.push_back(IfcUnitEnum_type);
    declarations.push_back(IfcUnitaryControlElementTypeEnum_type);
    declarations.push_back(IfcUnitaryEquipmentTypeEnum_type);
    declarations.push_back(IfcValveTypeEnum_type);
    declarations.push_back(IfcVibrationIsolatorTypeEnum_type);
    declarations.push_back(IfcVoidingFeatureTypeEnum_type);
    declarations.push_back(IfcWallTypeEnum_type);
    declarations.push_back(IfcWasteTerminalTypeEnum_type);
    declarations.push_back(IfcWindowPanelOperationEnum_type);
    declarations.push_back(IfcWindowPanelPositionEnum_type);
    declarations.push_back(IfcWindowStyleConstructionEnum_type);
    declarations.push_back(IfcWindowStyleOperationEnum_type);
    declarations.push_back(IfcWindowTypeEnum_type);
    declarations.push_back(IfcWindowTypePartitioningEnum_type);
    declarations.push_back(IfcWorkCalendarTypeEnum_type);
    declarations.push_back(IfcWorkPlanTypeEnum_type);
    declarations.push_back(IfcWorkScheduleTypeEnum_type);
    declarations.push_back(IfcActorRole_type);
    declarations.push_back(IfcAddress_type);
    declarations.push_back(IfcApplication_type);
    declarations.push_back(IfcAppliedValue_type);
    declarations.push_back(IfcApproval_type);
    declarations.push_back(IfcBoundaryCondition_type);
    declarations.push_back(IfcBoundaryEdgeCondition_type);
    declarations.push_back(IfcBoundaryFaceCondition_type);
    declarations.push_back(IfcBoundaryNodeCondition_type);
    declarations.push_back(IfcBoundaryNodeConditionWarping_type);
    declarations.push_back(IfcConnectionGeometry_type);
    declarations.push_back(IfcConnectionPointGeometry_type);
    declarations.push_back(IfcConnectionSurfaceGeometry_type);
    declarations.push_back(IfcConnectionVolumeGeometry_type);
    declarations.push_back(IfcConstraint_type);
    declarations.push_back(IfcCoordinateOperation_type);
    declarations.push_back(IfcCoordinateReferenceSystem_type);
    declarations.push_back(IfcCostValue_type);
    declarations.push_back(IfcDerivedUnit_type);
    declarations.push_back(IfcDerivedUnitElement_type);
    declarations.push_back(IfcDimensionalExponents_type);
    declarations.push_back(IfcExternalInformation_type);
    declarations.push_back(IfcExternalReference_type);
    declarations.push_back(IfcExternallyDefinedHatchStyle_type);
    declarations.push_back(IfcExternallyDefinedSurfaceStyle_type);
    declarations.push_back(IfcExternallyDefinedTextFont_type);
    declarations.push_back(IfcGridAxis_type);
    declarations.push_back(IfcIrregularTimeSeriesValue_type);
    declarations.push_back(IfcLibraryInformation_type);
    declarations.push_back(IfcLibraryReference_type);
    declarations.push_back(IfcLightDistributionData_type);
    declarations.push_back(IfcLightIntensityDistribution_type);
    declarations.push_back(IfcMapConversion_type);
    declarations.push_back(IfcMaterialClassificationRelationship_type);
    declarations.push_back(IfcMaterialDefinition_type);
    declarations.push_back(IfcMaterialLayer_type);
    declarations.push_back(IfcMaterialLayerSet_type);
    declarations.push_back(IfcMaterialLayerWithOffsets_type);
    declarations.push_back(IfcMaterialList_type);
    declarations.push_back(IfcMaterialProfile_type);
    declarations.push_back(IfcMaterialProfileSet_type);
    declarations.push_back(IfcMaterialProfileWithOffsets_type);
    declarations.push_back(IfcMaterialUsageDefinition_type);
    declarations.push_back(IfcMeasureWithUnit_type);
    declarations.push_back(IfcMetric_type);
    declarations.push_back(IfcMonetaryUnit_type);
    declarations.push_back(IfcNamedUnit_type);
    declarations.push_back(IfcObjectPlacement_type);
    declarations.push_back(IfcObjective_type);
    declarations.push_back(IfcOrganization_type);
    declarations.push_back(IfcOwnerHistory_type);
    declarations.push_back(IfcPerson_type);
    declarations.push_back(IfcPersonAndOrganization_type);
    declarations.push_back(IfcPhysicalQuantity_type);
    declarations.push_back(IfcPhysicalSimpleQuantity_type);
    declarations.push_back(IfcPostalAddress_type);
    declarations.push_back(IfcPresentationItem_type);
    declarations.push_back(IfcPresentationLayerAssignment_type);
    declarations.push_back(IfcPresentationLayerWithStyle_type);
    declarations.push_back(IfcPresentationStyle_type);
    declarations.push_back(IfcPresentationStyleAssignment_type);
    declarations.push_back(IfcProductRepresentation_type);
    declarations.push_back(IfcProfileDef_type);
    declarations.push_back(IfcProjectedCRS_type);
    declarations.push_back(IfcPropertyAbstraction_type);
    declarations.push_back(IfcPropertyEnumeration_type);
    declarations.push_back(IfcQuantityArea_type);
    declarations.push_back(IfcQuantityCount_type);
    declarations.push_back(IfcQuantityLength_type);
    declarations.push_back(IfcQuantityTime_type);
    declarations.push_back(IfcQuantityVolume_type);
    declarations.push_back(IfcQuantityWeight_type);
    declarations.push_back(IfcRecurrencePattern_type);
    declarations.push_back(IfcReference_type);
    declarations.push_back(IfcRepresentation_type);
    declarations.push_back(IfcRepresentationContext_type);
    declarations.push_back(IfcRepresentationItem_type);
    declarations.push_back(IfcRepresentationMap_type);
    declarations.push_back(IfcResourceLevelRelationship_type);
    declarations.push_back(IfcRoot_type);
    declarations.push_back(IfcSIUnit_type);
    declarations.push_back(IfcSchedulingTime_type);
    declarations.push_back(IfcShapeAspect_type);
    declarations.push_back(IfcShapeModel_type);
    declarations.push_back(IfcShapeRepresentation_type);
    declarations.push_back(IfcStructuralConnectionCondition_type);
    declarations.push_back(IfcStructuralLoad_type);
    declarations.push_back(IfcStructuralLoadConfiguration_type);
    declarations.push_back(IfcStructuralLoadOrResult_type);
    declarations.push_back(IfcStructuralLoadStatic_type);
    declarations.push_back(IfcStructuralLoadTemperature_type);
    declarations.push_back(IfcStyleModel_type);
    declarations.push_back(IfcStyledItem_type);
    declarations.push_back(IfcStyledRepresentation_type);
    declarations.push_back(IfcSurfaceReinforcementArea_type);
    declarations.push_back(IfcSurfaceStyle_type);
    declarations.push_back(IfcSurfaceStyleLighting_type);
    declarations.push_back(IfcSurfaceStyleRefraction_type);
    declarations.push_back(IfcSurfaceStyleShading_type);
    declarations.push_back(IfcSurfaceStyleWithTextures_type);
    declarations.push_back(IfcSurfaceTexture_type);
    declarations.push_back(IfcTable_type);
    declarations.push_back(IfcTableColumn_type);
    declarations.push_back(IfcTableRow_type);
    declarations.push_back(IfcTaskTime_type);
    declarations.push_back(IfcTaskTimeRecurring_type);
    declarations.push_back(IfcTelecomAddress_type);
    declarations.push_back(IfcTextStyle_type);
    declarations.push_back(IfcTextStyleForDefinedFont_type);
    declarations.push_back(IfcTextStyleTextModel_type);
    declarations.push_back(IfcTextureCoordinate_type);
    declarations.push_back(IfcTextureCoordinateGenerator_type);
    declarations.push_back(IfcTextureMap_type);
    declarations.push_back(IfcTextureVertex_type);
    declarations.push_back(IfcTextureVertexList_type);
    declarations.push_back(IfcTimePeriod_type);
    declarations.push_back(IfcTimeSeries_type);
    declarations.push_back(IfcTimeSeriesValue_type);
    declarations.push_back(IfcTopologicalRepresentationItem_type);
    declarations.push_back(IfcTopologyRepresentation_type);
    declarations.push_back(IfcUnitAssignment_type);
    declarations.push_back(IfcVertex_type);
    declarations.push_back(IfcVertexPoint_type);
    declarations.push_back(IfcVirtualGridIntersection_type);
    declarations.push_back(IfcWorkTime_type);
    declarations.push_back(IfcApprovalRelationship_type);
    declarations.push_back(IfcArbitraryClosedProfileDef_type);
    declarations.push_back(IfcArbitraryOpenProfileDef_type);
    declarations.push_back(IfcArbitraryProfileDefWithVoids_type);
    declarations.push_back(IfcBlobTexture_type);
    declarations.push_back(IfcCenterLineProfileDef_type);
    declarations.push_back(IfcClassification_type);
    declarations.push_back(IfcClassificationReference_type);
    declarations.push_back(IfcColourRgbList_type);
    declarations.push_back(IfcColourSpecification_type);
    declarations.push_back(IfcCompositeProfileDef_type);
    declarations.push_back(IfcConnectedFaceSet_type);
    declarations.push_back(IfcConnectionCurveGeometry_type);
    declarations.push_back(IfcConnectionPointEccentricity_type);
    declarations.push_back(IfcContextDependentUnit_type);
    declarations.push_back(IfcConversionBasedUnit_type);
    declarations.push_back(IfcConversionBasedUnitWithOffset_type);
    declarations.push_back(IfcCurrencyRelationship_type);
    declarations.push_back(IfcCurveStyle_type);
    declarations.push_back(IfcCurveStyleFont_type);
    declarations.push_back(IfcCurveStyleFontAndScaling_type);
    declarations.push_back(IfcCurveStyleFontPattern_type);
    declarations.push_back(IfcDerivedProfileDef_type);
    declarations.push_back(IfcDocumentInformation_type);
    declarations.push_back(IfcDocumentInformationRelationship_type);
    declarations.push_back(IfcDocumentReference_type);
    declarations.push_back(IfcEdge_type);
    declarations.push_back(IfcEdgeCurve_type);
    declarations.push_back(IfcEventTime_type);
    declarations.push_back(IfcExtendedProperties_type);
    declarations.push_back(IfcExternalReferenceRelationship_type);
    declarations.push_back(IfcFace_type);
    declarations.push_back(IfcFaceBound_type);
    declarations.push_back(IfcFaceOuterBound_type);
    declarations.push_back(IfcFaceSurface_type);
    declarations.push_back(IfcFailureConnectionCondition_type);
    declarations.push_back(IfcFillAreaStyle_type);
    declarations.push_back(IfcGeometricRepresentationContext_type);
    declarations.push_back(IfcGeometricRepresentationItem_type);
    declarations.push_back(IfcGeometricRepresentationSubContext_type);
    declarations.push_back(IfcGeometricSet_type);
    declarations.push_back(IfcGridPlacement_type);
    declarations.push_back(IfcHalfSpaceSolid_type);
    declarations.push_back(IfcImageTexture_type);
    declarations.push_back(IfcIndexedColourMap_type);
    declarations.push_back(IfcIndexedTextureMap_type);
    declarations.push_back(IfcIndexedTriangleTextureMap_type);
    declarations.push_back(IfcIrregularTimeSeries_type);
    declarations.push_back(IfcLagTime_type);
    declarations.push_back(IfcLightSource_type);
    declarations.push_back(IfcLightSourceAmbient_type);
    declarations.push_back(IfcLightSourceDirectional_type);
    declarations.push_back(IfcLightSourceGoniometric_type);
    declarations.push_back(IfcLightSourcePositional_type);
    declarations.push_back(IfcLightSourceSpot_type);
    declarations.push_back(IfcLocalPlacement_type);
    declarations.push_back(IfcLoop_type);
    declarations.push_back(IfcMappedItem_type);
    declarations.push_back(IfcMaterial_type);
    declarations.push_back(IfcMaterialConstituent_type);
    declarations.push_back(IfcMaterialConstituentSet_type);
    declarations.push_back(IfcMaterialDefinitionRepresentation_type);
    declarations.push_back(IfcMaterialLayerSetUsage_type);
    declarations.push_back(IfcMaterialProfileSetUsage_type);
    declarations.push_back(IfcMaterialProfileSetUsageTapering_type);
    declarations.push_back(IfcMaterialProperties_type);
    declarations.push_back(IfcMaterialRelationship_type);
    declarations.push_back(IfcMirroredProfileDef_type);
    declarations.push_back(IfcObjectDefinition_type);
    declarations.push_back(IfcOpenShell_type);
    declarations.push_back(IfcOrganizationRelationship_type);
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
    declarations.push_back(IfcPreDefinedItem_type);
    declarations.push_back(IfcPreDefinedProperties_type);
    declarations.push_back(IfcPreDefinedTextFont_type);
    declarations.push_back(IfcProductDefinitionShape_type);
    declarations.push_back(IfcProfileProperties_type);
    declarations.push_back(IfcProperty_type);
    declarations.push_back(IfcPropertyDefinition_type);
    declarations.push_back(IfcPropertyDependencyRelationship_type);
    declarations.push_back(IfcPropertySetDefinition_type);
    declarations.push_back(IfcPropertyTemplateDefinition_type);
    declarations.push_back(IfcQuantitySet_type);
    declarations.push_back(IfcRectangleProfileDef_type);
    declarations.push_back(IfcRegularTimeSeries_type);
    declarations.push_back(IfcReinforcementBarProperties_type);
    declarations.push_back(IfcRelationship_type);
    declarations.push_back(IfcResourceApprovalRelationship_type);
    declarations.push_back(IfcResourceConstraintRelationship_type);
    declarations.push_back(IfcResourceTime_type);
    declarations.push_back(IfcRoundedRectangleProfileDef_type);
    declarations.push_back(IfcSectionProperties_type);
    declarations.push_back(IfcSectionReinforcementProperties_type);
    declarations.push_back(IfcSectionedSpine_type);
    declarations.push_back(IfcShellBasedSurfaceModel_type);
    declarations.push_back(IfcSimpleProperty_type);
    declarations.push_back(IfcSlippageConnectionCondition_type);
    declarations.push_back(IfcSolidModel_type);
    declarations.push_back(IfcStructuralLoadLinearForce_type);
    declarations.push_back(IfcStructuralLoadPlanarForce_type);
    declarations.push_back(IfcStructuralLoadSingleDisplacement_type);
    declarations.push_back(IfcStructuralLoadSingleDisplacementDistortion_type);
    declarations.push_back(IfcStructuralLoadSingleForce_type);
    declarations.push_back(IfcStructuralLoadSingleForceWarping_type);
    declarations.push_back(IfcSubedge_type);
    declarations.push_back(IfcSurface_type);
    declarations.push_back(IfcSurfaceStyleRendering_type);
    declarations.push_back(IfcSweptAreaSolid_type);
    declarations.push_back(IfcSweptDiskSolid_type);
    declarations.push_back(IfcSweptDiskSolidPolygonal_type);
    declarations.push_back(IfcSweptSurface_type);
    declarations.push_back(IfcTShapeProfileDef_type);
    declarations.push_back(IfcTessellatedItem_type);
    declarations.push_back(IfcTextLiteral_type);
    declarations.push_back(IfcTextLiteralWithExtent_type);
    declarations.push_back(IfcTextStyleFontModel_type);
    declarations.push_back(IfcTrapeziumProfileDef_type);
    declarations.push_back(IfcTypeObject_type);
    declarations.push_back(IfcTypeProcess_type);
    declarations.push_back(IfcTypeProduct_type);
    declarations.push_back(IfcTypeResource_type);
    declarations.push_back(IfcUShapeProfileDef_type);
    declarations.push_back(IfcVector_type);
    declarations.push_back(IfcVertexLoop_type);
    declarations.push_back(IfcWindowStyle_type);
    declarations.push_back(IfcZShapeProfileDef_type);
    declarations.push_back(IfcAdvancedFace_type);
    declarations.push_back(IfcAnnotationFillArea_type);
    declarations.push_back(IfcAsymmetricIShapeProfileDef_type);
    declarations.push_back(IfcAxis1Placement_type);
    declarations.push_back(IfcAxis2Placement2D_type);
    declarations.push_back(IfcAxis2Placement3D_type);
    declarations.push_back(IfcBooleanResult_type);
    declarations.push_back(IfcBoundedSurface_type);
    declarations.push_back(IfcBoundingBox_type);
    declarations.push_back(IfcBoxedHalfSpace_type);
    declarations.push_back(IfcCShapeProfileDef_type);
    declarations.push_back(IfcCartesianPoint_type);
    declarations.push_back(IfcCartesianPointList_type);
    declarations.push_back(IfcCartesianPointList2D_type);
    declarations.push_back(IfcCartesianPointList3D_type);
    declarations.push_back(IfcCartesianTransformationOperator_type);
    declarations.push_back(IfcCartesianTransformationOperator2D_type);
    declarations.push_back(IfcCartesianTransformationOperator2DnonUniform_type);
    declarations.push_back(IfcCartesianTransformationOperator3D_type);
    declarations.push_back(IfcCartesianTransformationOperator3DnonUniform_type);
    declarations.push_back(IfcCircleProfileDef_type);
    declarations.push_back(IfcClosedShell_type);
    declarations.push_back(IfcColourRgb_type);
    declarations.push_back(IfcComplexProperty_type);
    declarations.push_back(IfcCompositeCurveSegment_type);
    declarations.push_back(IfcConstructionResourceType_type);
    declarations.push_back(IfcContext_type);
    declarations.push_back(IfcCrewResourceType_type);
    declarations.push_back(IfcCsgPrimitive3D_type);
    declarations.push_back(IfcCsgSolid_type);
    declarations.push_back(IfcCurve_type);
    declarations.push_back(IfcCurveBoundedPlane_type);
    declarations.push_back(IfcCurveBoundedSurface_type);
    declarations.push_back(IfcDirection_type);
    declarations.push_back(IfcDoorStyle_type);
    declarations.push_back(IfcEdgeLoop_type);
    declarations.push_back(IfcElementQuantity_type);
    declarations.push_back(IfcElementType_type);
    declarations.push_back(IfcElementarySurface_type);
    declarations.push_back(IfcEllipseProfileDef_type);
    declarations.push_back(IfcEventType_type);
    declarations.push_back(IfcExtrudedAreaSolid_type);
    declarations.push_back(IfcExtrudedAreaSolidTapered_type);
    declarations.push_back(IfcFaceBasedSurfaceModel_type);
    declarations.push_back(IfcFillAreaStyleHatching_type);
    declarations.push_back(IfcFillAreaStyleTiles_type);
    declarations.push_back(IfcFixedReferenceSweptAreaSolid_type);
    declarations.push_back(IfcFurnishingElementType_type);
    declarations.push_back(IfcFurnitureType_type);
    declarations.push_back(IfcGeographicElementType_type);
    declarations.push_back(IfcGeometricCurveSet_type);
    declarations.push_back(IfcIShapeProfileDef_type);
    declarations.push_back(IfcLShapeProfileDef_type);
    declarations.push_back(IfcLaborResourceType_type);
    declarations.push_back(IfcLine_type);
    declarations.push_back(IfcManifoldSolidBrep_type);
    declarations.push_back(IfcObject_type);
    declarations.push_back(IfcOffsetCurve2D_type);
    declarations.push_back(IfcOffsetCurve3D_type);
    declarations.push_back(IfcPcurve_type);
    declarations.push_back(IfcPlanarBox_type);
    declarations.push_back(IfcPlane_type);
    declarations.push_back(IfcPreDefinedColour_type);
    declarations.push_back(IfcPreDefinedCurveFont_type);
    declarations.push_back(IfcPreDefinedPropertySet_type);
    declarations.push_back(IfcProcedureType_type);
    declarations.push_back(IfcProcess_type);
    declarations.push_back(IfcProduct_type);
    declarations.push_back(IfcProject_type);
    declarations.push_back(IfcProjectLibrary_type);
    declarations.push_back(IfcPropertyBoundedValue_type);
    declarations.push_back(IfcPropertyEnumeratedValue_type);
    declarations.push_back(IfcPropertyListValue_type);
    declarations.push_back(IfcPropertyReferenceValue_type);
    declarations.push_back(IfcPropertySet_type);
    declarations.push_back(IfcPropertySetTemplate_type);
    declarations.push_back(IfcPropertySingleValue_type);
    declarations.push_back(IfcPropertyTableValue_type);
    declarations.push_back(IfcPropertyTemplate_type);
    declarations.push_back(IfcProxy_type);
    declarations.push_back(IfcRectangleHollowProfileDef_type);
    declarations.push_back(IfcRectangularPyramid_type);
    declarations.push_back(IfcRectangularTrimmedSurface_type);
    declarations.push_back(IfcReinforcementDefinitionProperties_type);
    declarations.push_back(IfcRelAssigns_type);
    declarations.push_back(IfcRelAssignsToActor_type);
    declarations.push_back(IfcRelAssignsToControl_type);
    declarations.push_back(IfcRelAssignsToGroup_type);
    declarations.push_back(IfcRelAssignsToGroupByFactor_type);
    declarations.push_back(IfcRelAssignsToProcess_type);
    declarations.push_back(IfcRelAssignsToProduct_type);
    declarations.push_back(IfcRelAssignsToResource_type);
    declarations.push_back(IfcRelAssociates_type);
    declarations.push_back(IfcRelAssociatesApproval_type);
    declarations.push_back(IfcRelAssociatesClassification_type);
    declarations.push_back(IfcRelAssociatesConstraint_type);
    declarations.push_back(IfcRelAssociatesDocument_type);
    declarations.push_back(IfcRelAssociatesLibrary_type);
    declarations.push_back(IfcRelAssociatesMaterial_type);
    declarations.push_back(IfcRelConnects_type);
    declarations.push_back(IfcRelConnectsElements_type);
    declarations.push_back(IfcRelConnectsPathElements_type);
    declarations.push_back(IfcRelConnectsPortToElement_type);
    declarations.push_back(IfcRelConnectsPorts_type);
    declarations.push_back(IfcRelConnectsStructuralActivity_type);
    declarations.push_back(IfcRelConnectsStructuralMember_type);
    declarations.push_back(IfcRelConnectsWithEccentricity_type);
    declarations.push_back(IfcRelConnectsWithRealizingElements_type);
    declarations.push_back(IfcRelContainedInSpatialStructure_type);
    declarations.push_back(IfcRelCoversBldgElements_type);
    declarations.push_back(IfcRelCoversSpaces_type);
    declarations.push_back(IfcRelDeclares_type);
    declarations.push_back(IfcRelDecomposes_type);
    declarations.push_back(IfcRelDefines_type);
    declarations.push_back(IfcRelDefinesByObject_type);
    declarations.push_back(IfcRelDefinesByProperties_type);
    declarations.push_back(IfcRelDefinesByTemplate_type);
    declarations.push_back(IfcRelDefinesByType_type);
    declarations.push_back(IfcRelFillsElement_type);
    declarations.push_back(IfcRelFlowControlElements_type);
    declarations.push_back(IfcRelInterferesElements_type);
    declarations.push_back(IfcRelNests_type);
    declarations.push_back(IfcRelProjectsElement_type);
    declarations.push_back(IfcRelReferencedInSpatialStructure_type);
    declarations.push_back(IfcRelSequence_type);
    declarations.push_back(IfcRelServicesBuildings_type);
    declarations.push_back(IfcRelSpaceBoundary_type);
    declarations.push_back(IfcRelSpaceBoundary1stLevel_type);
    declarations.push_back(IfcRelSpaceBoundary2ndLevel_type);
    declarations.push_back(IfcRelVoidsElement_type);
    declarations.push_back(IfcReparametrisedCompositeCurveSegment_type);
    declarations.push_back(IfcResource_type);
    declarations.push_back(IfcRevolvedAreaSolid_type);
    declarations.push_back(IfcRevolvedAreaSolidTapered_type);
    declarations.push_back(IfcRightCircularCone_type);
    declarations.push_back(IfcRightCircularCylinder_type);
    declarations.push_back(IfcSimplePropertyTemplate_type);
    declarations.push_back(IfcSpatialElement_type);
    declarations.push_back(IfcSpatialElementType_type);
    declarations.push_back(IfcSpatialStructureElement_type);
    declarations.push_back(IfcSpatialStructureElementType_type);
    declarations.push_back(IfcSpatialZone_type);
    declarations.push_back(IfcSpatialZoneType_type);
    declarations.push_back(IfcSphere_type);
    declarations.push_back(IfcStructuralActivity_type);
    declarations.push_back(IfcStructuralItem_type);
    declarations.push_back(IfcStructuralMember_type);
    declarations.push_back(IfcStructuralReaction_type);
    declarations.push_back(IfcStructuralSurfaceMember_type);
    declarations.push_back(IfcStructuralSurfaceMemberVarying_type);
    declarations.push_back(IfcStructuralSurfaceReaction_type);
    declarations.push_back(IfcSubContractResourceType_type);
    declarations.push_back(IfcSurfaceCurveSweptAreaSolid_type);
    declarations.push_back(IfcSurfaceOfLinearExtrusion_type);
    declarations.push_back(IfcSurfaceOfRevolution_type);
    declarations.push_back(IfcSystemFurnitureElementType_type);
    declarations.push_back(IfcTask_type);
    declarations.push_back(IfcTaskType_type);
    declarations.push_back(IfcTessellatedFaceSet_type);
    declarations.push_back(IfcTransportElementType_type);
    declarations.push_back(IfcTriangulatedFaceSet_type);
    declarations.push_back(IfcWindowLiningProperties_type);
    declarations.push_back(IfcWindowPanelProperties_type);
    declarations.push_back(IfcActor_type);
    declarations.push_back(IfcAdvancedBrep_type);
    declarations.push_back(IfcAdvancedBrepWithVoids_type);
    declarations.push_back(IfcAnnotation_type);
    declarations.push_back(IfcBSplineSurface_type);
    declarations.push_back(IfcBSplineSurfaceWithKnots_type);
    declarations.push_back(IfcBlock_type);
    declarations.push_back(IfcBooleanClippingResult_type);
    declarations.push_back(IfcBoundedCurve_type);
    declarations.push_back(IfcBuilding_type);
    declarations.push_back(IfcBuildingElementType_type);
    declarations.push_back(IfcBuildingStorey_type);
    declarations.push_back(IfcChimneyType_type);
    declarations.push_back(IfcCircleHollowProfileDef_type);
    declarations.push_back(IfcCivilElementType_type);
    declarations.push_back(IfcColumnType_type);
    declarations.push_back(IfcComplexPropertyTemplate_type);
    declarations.push_back(IfcCompositeCurve_type);
    declarations.push_back(IfcCompositeCurveOnSurface_type);
    declarations.push_back(IfcConic_type);
    declarations.push_back(IfcConstructionEquipmentResourceType_type);
    declarations.push_back(IfcConstructionMaterialResourceType_type);
    declarations.push_back(IfcConstructionProductResourceType_type);
    declarations.push_back(IfcConstructionResource_type);
    declarations.push_back(IfcControl_type);
    declarations.push_back(IfcCostItem_type);
    declarations.push_back(IfcCostSchedule_type);
    declarations.push_back(IfcCoveringType_type);
    declarations.push_back(IfcCrewResource_type);
    declarations.push_back(IfcCurtainWallType_type);
    declarations.push_back(IfcCylindricalSurface_type);
    declarations.push_back(IfcDistributionElementType_type);
    declarations.push_back(IfcDistributionFlowElementType_type);
    declarations.push_back(IfcDoorLiningProperties_type);
    declarations.push_back(IfcDoorPanelProperties_type);
    declarations.push_back(IfcDoorType_type);
    declarations.push_back(IfcDraughtingPreDefinedColour_type);
    declarations.push_back(IfcDraughtingPreDefinedCurveFont_type);
    declarations.push_back(IfcElement_type);
    declarations.push_back(IfcElementAssembly_type);
    declarations.push_back(IfcElementAssemblyType_type);
    declarations.push_back(IfcElementComponent_type);
    declarations.push_back(IfcElementComponentType_type);
    declarations.push_back(IfcEllipse_type);
    declarations.push_back(IfcEnergyConversionDeviceType_type);
    declarations.push_back(IfcEngineType_type);
    declarations.push_back(IfcEvaporativeCoolerType_type);
    declarations.push_back(IfcEvaporatorType_type);
    declarations.push_back(IfcEvent_type);
    declarations.push_back(IfcExternalSpatialStructureElement_type);
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
    declarations.push_back(IfcFootingType_type);
    declarations.push_back(IfcFurnishingElement_type);
    declarations.push_back(IfcFurniture_type);
    declarations.push_back(IfcGeographicElement_type);
    declarations.push_back(IfcGrid_type);
    declarations.push_back(IfcGroup_type);
    declarations.push_back(IfcHeatExchangerType_type);
    declarations.push_back(IfcHumidifierType_type);
    declarations.push_back(IfcIndexedPolyCurve_type);
    declarations.push_back(IfcInterceptorType_type);
    declarations.push_back(IfcInventory_type);
    declarations.push_back(IfcJunctionBoxType_type);
    declarations.push_back(IfcLaborResource_type);
    declarations.push_back(IfcLampType_type);
    declarations.push_back(IfcLightFixtureType_type);
    declarations.push_back(IfcMechanicalFastener_type);
    declarations.push_back(IfcMechanicalFastenerType_type);
    declarations.push_back(IfcMedicalDeviceType_type);
    declarations.push_back(IfcMemberType_type);
    declarations.push_back(IfcMotorConnectionType_type);
    declarations.push_back(IfcOccupant_type);
    declarations.push_back(IfcOpeningElement_type);
    declarations.push_back(IfcOpeningStandardCase_type);
    declarations.push_back(IfcOutletType_type);
    declarations.push_back(IfcPerformanceHistory_type);
    declarations.push_back(IfcPermeableCoveringProperties_type);
    declarations.push_back(IfcPermit_type);
    declarations.push_back(IfcPileType_type);
    declarations.push_back(IfcPipeFittingType_type);
    declarations.push_back(IfcPipeSegmentType_type);
    declarations.push_back(IfcPlateType_type);
    declarations.push_back(IfcPolyline_type);
    declarations.push_back(IfcPort_type);
    declarations.push_back(IfcProcedure_type);
    declarations.push_back(IfcProjectOrder_type);
    declarations.push_back(IfcProjectionElement_type);
    declarations.push_back(IfcProtectiveDeviceType_type);
    declarations.push_back(IfcPumpType_type);
    declarations.push_back(IfcRailingType_type);
    declarations.push_back(IfcRampFlightType_type);
    declarations.push_back(IfcRampType_type);
    declarations.push_back(IfcRationalBSplineSurfaceWithKnots_type);
    declarations.push_back(IfcReinforcingElement_type);
    declarations.push_back(IfcReinforcingElementType_type);
    declarations.push_back(IfcReinforcingMesh_type);
    declarations.push_back(IfcReinforcingMeshType_type);
    declarations.push_back(IfcRelAggregates_type);
    declarations.push_back(IfcRoofType_type);
    declarations.push_back(IfcSanitaryTerminalType_type);
    declarations.push_back(IfcShadingDeviceType_type);
    declarations.push_back(IfcSite_type);
    declarations.push_back(IfcSlabType_type);
    declarations.push_back(IfcSolarDeviceType_type);
    declarations.push_back(IfcSpace_type);
    declarations.push_back(IfcSpaceHeaterType_type);
    declarations.push_back(IfcSpaceType_type);
    declarations.push_back(IfcStackTerminalType_type);
    declarations.push_back(IfcStairFlightType_type);
    declarations.push_back(IfcStairType_type);
    declarations.push_back(IfcStructuralAction_type);
    declarations.push_back(IfcStructuralConnection_type);
    declarations.push_back(IfcStructuralCurveAction_type);
    declarations.push_back(IfcStructuralCurveConnection_type);
    declarations.push_back(IfcStructuralCurveMember_type);
    declarations.push_back(IfcStructuralCurveMemberVarying_type);
    declarations.push_back(IfcStructuralCurveReaction_type);
    declarations.push_back(IfcStructuralLinearAction_type);
    declarations.push_back(IfcStructuralLoadGroup_type);
    declarations.push_back(IfcStructuralPointAction_type);
    declarations.push_back(IfcStructuralPointConnection_type);
    declarations.push_back(IfcStructuralPointReaction_type);
    declarations.push_back(IfcStructuralResultGroup_type);
    declarations.push_back(IfcStructuralSurfaceAction_type);
    declarations.push_back(IfcStructuralSurfaceConnection_type);
    declarations.push_back(IfcSubContractResource_type);
    declarations.push_back(IfcSurfaceFeature_type);
    declarations.push_back(IfcSwitchingDeviceType_type);
    declarations.push_back(IfcSystem_type);
    declarations.push_back(IfcSystemFurnitureElement_type);
    declarations.push_back(IfcTankType_type);
    declarations.push_back(IfcTendon_type);
    declarations.push_back(IfcTendonAnchor_type);
    declarations.push_back(IfcTendonAnchorType_type);
    declarations.push_back(IfcTendonType_type);
    declarations.push_back(IfcTransformerType_type);
    declarations.push_back(IfcTransportElement_type);
    declarations.push_back(IfcTrimmedCurve_type);
    declarations.push_back(IfcTubeBundleType_type);
    declarations.push_back(IfcUnitaryEquipmentType_type);
    declarations.push_back(IfcValveType_type);
    declarations.push_back(IfcVibrationIsolator_type);
    declarations.push_back(IfcVibrationIsolatorType_type);
    declarations.push_back(IfcVirtualElement_type);
    declarations.push_back(IfcVoidingFeature_type);
    declarations.push_back(IfcWallType_type);
    declarations.push_back(IfcWasteTerminalType_type);
    declarations.push_back(IfcWindowType_type);
    declarations.push_back(IfcWorkCalendar_type);
    declarations.push_back(IfcWorkControl_type);
    declarations.push_back(IfcWorkPlan_type);
    declarations.push_back(IfcWorkSchedule_type);
    declarations.push_back(IfcZone_type);
    declarations.push_back(IfcActionRequest_type);
    declarations.push_back(IfcAirTerminalBoxType_type);
    declarations.push_back(IfcAirTerminalType_type);
    declarations.push_back(IfcAirToAirHeatRecoveryType_type);
    declarations.push_back(IfcAsset_type);
    declarations.push_back(IfcAudioVisualApplianceType_type);
    declarations.push_back(IfcBSplineCurve_type);
    declarations.push_back(IfcBSplineCurveWithKnots_type);
    declarations.push_back(IfcBeamType_type);
    declarations.push_back(IfcBoilerType_type);
    declarations.push_back(IfcBoundaryCurve_type);
    declarations.push_back(IfcBuildingElement_type);
    declarations.push_back(IfcBuildingElementPart_type);
    declarations.push_back(IfcBuildingElementPartType_type);
    declarations.push_back(IfcBuildingElementProxy_type);
    declarations.push_back(IfcBuildingElementProxyType_type);
    declarations.push_back(IfcBuildingSystem_type);
    declarations.push_back(IfcBurnerType_type);
    declarations.push_back(IfcCableCarrierFittingType_type);
    declarations.push_back(IfcCableCarrierSegmentType_type);
    declarations.push_back(IfcCableFittingType_type);
    declarations.push_back(IfcCableSegmentType_type);
    declarations.push_back(IfcChillerType_type);
    declarations.push_back(IfcChimney_type);
    declarations.push_back(IfcCircle_type);
    declarations.push_back(IfcCivilElement_type);
    declarations.push_back(IfcCoilType_type);
    declarations.push_back(IfcColumn_type);
    declarations.push_back(IfcColumnStandardCase_type);
    declarations.push_back(IfcCommunicationsApplianceType_type);
    declarations.push_back(IfcCompressorType_type);
    declarations.push_back(IfcCondenserType_type);
    declarations.push_back(IfcConstructionEquipmentResource_type);
    declarations.push_back(IfcConstructionMaterialResource_type);
    declarations.push_back(IfcConstructionProductResource_type);
    declarations.push_back(IfcCooledBeamType_type);
    declarations.push_back(IfcCoolingTowerType_type);
    declarations.push_back(IfcCovering_type);
    declarations.push_back(IfcCurtainWall_type);
    declarations.push_back(IfcDamperType_type);
    declarations.push_back(IfcDiscreteAccessory_type);
    declarations.push_back(IfcDiscreteAccessoryType_type);
    declarations.push_back(IfcDistributionChamberElementType_type);
    declarations.push_back(IfcDistributionControlElementType_type);
    declarations.push_back(IfcDistributionElement_type);
    declarations.push_back(IfcDistributionFlowElement_type);
    declarations.push_back(IfcDistributionPort_type);
    declarations.push_back(IfcDistributionSystem_type);
    declarations.push_back(IfcDoor_type);
    declarations.push_back(IfcDoorStandardCase_type);
    declarations.push_back(IfcDuctFittingType_type);
    declarations.push_back(IfcDuctSegmentType_type);
    declarations.push_back(IfcDuctSilencerType_type);
    declarations.push_back(IfcElectricApplianceType_type);
    declarations.push_back(IfcElectricDistributionBoardType_type);
    declarations.push_back(IfcElectricFlowStorageDeviceType_type);
    declarations.push_back(IfcElectricGeneratorType_type);
    declarations.push_back(IfcElectricMotorType_type);
    declarations.push_back(IfcElectricTimeControlType_type);
    declarations.push_back(IfcEnergyConversionDevice_type);
    declarations.push_back(IfcEngine_type);
    declarations.push_back(IfcEvaporativeCooler_type);
    declarations.push_back(IfcEvaporator_type);
    declarations.push_back(IfcExternalSpatialElement_type);
    declarations.push_back(IfcFanType_type);
    declarations.push_back(IfcFilterType_type);
    declarations.push_back(IfcFireSuppressionTerminalType_type);
    declarations.push_back(IfcFlowController_type);
    declarations.push_back(IfcFlowFitting_type);
    declarations.push_back(IfcFlowInstrumentType_type);
    declarations.push_back(IfcFlowMeter_type);
    declarations.push_back(IfcFlowMovingDevice_type);
    declarations.push_back(IfcFlowSegment_type);
    declarations.push_back(IfcFlowStorageDevice_type);
    declarations.push_back(IfcFlowTerminal_type);
    declarations.push_back(IfcFlowTreatmentDevice_type);
    declarations.push_back(IfcFooting_type);
    declarations.push_back(IfcHeatExchanger_type);
    declarations.push_back(IfcHumidifier_type);
    declarations.push_back(IfcInterceptor_type);
    declarations.push_back(IfcJunctionBox_type);
    declarations.push_back(IfcLamp_type);
    declarations.push_back(IfcLightFixture_type);
    declarations.push_back(IfcMedicalDevice_type);
    declarations.push_back(IfcMember_type);
    declarations.push_back(IfcMemberStandardCase_type);
    declarations.push_back(IfcMotorConnection_type);
    declarations.push_back(IfcOuterBoundaryCurve_type);
    declarations.push_back(IfcOutlet_type);
    declarations.push_back(IfcPile_type);
    declarations.push_back(IfcPipeFitting_type);
    declarations.push_back(IfcPipeSegment_type);
    declarations.push_back(IfcPlate_type);
    declarations.push_back(IfcPlateStandardCase_type);
    declarations.push_back(IfcProtectiveDevice_type);
    declarations.push_back(IfcProtectiveDeviceTrippingUnitType_type);
    declarations.push_back(IfcPump_type);
    declarations.push_back(IfcRailing_type);
    declarations.push_back(IfcRamp_type);
    declarations.push_back(IfcRampFlight_type);
    declarations.push_back(IfcRationalBSplineCurveWithKnots_type);
    declarations.push_back(IfcReinforcingBar_type);
    declarations.push_back(IfcReinforcingBarType_type);
    declarations.push_back(IfcRoof_type);
    declarations.push_back(IfcSanitaryTerminal_type);
    declarations.push_back(IfcSensorType_type);
    declarations.push_back(IfcShadingDevice_type);
    declarations.push_back(IfcSlab_type);
    declarations.push_back(IfcSlabElementedCase_type);
    declarations.push_back(IfcSlabStandardCase_type);
    declarations.push_back(IfcSolarDevice_type);
    declarations.push_back(IfcSpaceHeater_type);
    declarations.push_back(IfcStackTerminal_type);
    declarations.push_back(IfcStair_type);
    declarations.push_back(IfcStairFlight_type);
    declarations.push_back(IfcStructuralAnalysisModel_type);
    declarations.push_back(IfcStructuralLoadCase_type);
    declarations.push_back(IfcStructuralPlanarAction_type);
    declarations.push_back(IfcSwitchingDevice_type);
    declarations.push_back(IfcTank_type);
    declarations.push_back(IfcTransformer_type);
    declarations.push_back(IfcTubeBundle_type);
    declarations.push_back(IfcUnitaryControlElementType_type);
    declarations.push_back(IfcUnitaryEquipment_type);
    declarations.push_back(IfcValve_type);
    declarations.push_back(IfcWall_type);
    declarations.push_back(IfcWallElementedCase_type);
    declarations.push_back(IfcWallStandardCase_type);
    declarations.push_back(IfcWasteTerminal_type);
    declarations.push_back(IfcWindow_type);
    declarations.push_back(IfcWindowStandardCase_type);
    declarations.push_back(IfcActuatorType_type);
    declarations.push_back(IfcAirTerminal_type);
    declarations.push_back(IfcAirTerminalBox_type);
    declarations.push_back(IfcAirToAirHeatRecovery_type);
    declarations.push_back(IfcAlarmType_type);
    declarations.push_back(IfcAudioVisualAppliance_type);
    declarations.push_back(IfcBeam_type);
    declarations.push_back(IfcBeamStandardCase_type);
    declarations.push_back(IfcBoiler_type);
    declarations.push_back(IfcBurner_type);
    declarations.push_back(IfcCableCarrierFitting_type);
    declarations.push_back(IfcCableCarrierSegment_type);
    declarations.push_back(IfcCableFitting_type);
    declarations.push_back(IfcCableSegment_type);
    declarations.push_back(IfcChiller_type);
    declarations.push_back(IfcCoil_type);
    declarations.push_back(IfcCommunicationsAppliance_type);
    declarations.push_back(IfcCompressor_type);
    declarations.push_back(IfcCondenser_type);
    declarations.push_back(IfcControllerType_type);
    declarations.push_back(IfcCooledBeam_type);
    declarations.push_back(IfcCoolingTower_type);
    declarations.push_back(IfcDamper_type);
    declarations.push_back(IfcDistributionChamberElement_type);
    declarations.push_back(IfcDistributionCircuit_type);
    declarations.push_back(IfcDistributionControlElement_type);
    declarations.push_back(IfcDuctFitting_type);
    declarations.push_back(IfcDuctSegment_type);
    declarations.push_back(IfcDuctSilencer_type);
    declarations.push_back(IfcElectricAppliance_type);
    declarations.push_back(IfcElectricDistributionBoard_type);
    declarations.push_back(IfcElectricFlowStorageDevice_type);
    declarations.push_back(IfcElectricGenerator_type);
    declarations.push_back(IfcElectricMotor_type);
    declarations.push_back(IfcElectricTimeControl_type);
    declarations.push_back(IfcFan_type);
    declarations.push_back(IfcFilter_type);
    declarations.push_back(IfcFireSuppressionTerminal_type);
    declarations.push_back(IfcFlowInstrument_type);
    declarations.push_back(IfcProtectiveDeviceTrippingUnit_type);
    declarations.push_back(IfcSensor_type);
    declarations.push_back(IfcUnitaryControlElement_type);
    declarations.push_back(IfcActuator_type);
    declarations.push_back(IfcAlarm_type);
    declarations.push_back(IfcController_type);
    declarations.push_back(IfcActorSelect_type);
    declarations.push_back(IfcAxis2Placement_type);
    declarations.push_back(IfcBendingParameterSelect_type);
    declarations.push_back(IfcBooleanOperand_type);
    declarations.push_back(IfcClassificationReferenceSelect_type);
    declarations.push_back(IfcClassificationSelect_type);
    declarations.push_back(IfcColour_type);
    declarations.push_back(IfcColourOrFactor_type);
    declarations.push_back(IfcCoordinateReferenceSystemSelect_type);
    declarations.push_back(IfcCsgSelect_type);
    declarations.push_back(IfcCurveOnSurface_type);
    declarations.push_back(IfcCurveOrEdgeCurve_type);
    declarations.push_back(IfcCurveStyleFontSelect_type);
    declarations.push_back(IfcDefinitionSelect_type);
    declarations.push_back(IfcDerivedMeasureValue_type);
    declarations.push_back(IfcDocumentSelect_type);
    declarations.push_back(IfcFillStyleSelect_type);
    declarations.push_back(IfcGeometricSetSelect_type);
    declarations.push_back(IfcGridPlacementDirectionSelect_type);
    declarations.push_back(IfcHatchLineDistanceSelect_type);
    declarations.push_back(IfcLayeredItem_type);
    declarations.push_back(IfcLibrarySelect_type);
    declarations.push_back(IfcLightDistributionDataSourceSelect_type);
    declarations.push_back(IfcMaterialSelect_type);
    declarations.push_back(IfcMeasureValue_type);
    declarations.push_back(IfcModulusOfRotationalSubgradeReactionSelect_type);
    declarations.push_back(IfcModulusOfSubgradeReactionSelect_type);
    declarations.push_back(IfcModulusOfTranslationalSubgradeReactionSelect_type);
    declarations.push_back(IfcObjectReferenceSelect_type);
    declarations.push_back(IfcPointOrVertexPoint_type);
    declarations.push_back(IfcPresentationStyleSelect_type);
    declarations.push_back(IfcProcessSelect_type);
    declarations.push_back(IfcProductRepresentationSelect_type);
    declarations.push_back(IfcProductSelect_type);
    declarations.push_back(IfcPropertySetDefinitionSelect_type);
    declarations.push_back(IfcResourceObjectSelect_type);
    declarations.push_back(IfcResourceSelect_type);
    declarations.push_back(IfcRotationalStiffnessSelect_type);
    declarations.push_back(IfcSegmentIndexSelect_type);
    declarations.push_back(IfcShell_type);
    declarations.push_back(IfcSimpleValue_type);
    declarations.push_back(IfcSizeSelect_type);
    declarations.push_back(IfcSolidOrShell_type);
    declarations.push_back(IfcSpaceBoundarySelect_type);
    declarations.push_back(IfcSpecularHighlightSelect_type);
    declarations.push_back(IfcStructuralActivityAssignmentSelect_type);
    declarations.push_back(IfcStyleAssignmentSelect_type);
    declarations.push_back(IfcSurfaceOrFaceSurface_type);
    declarations.push_back(IfcSurfaceStyleElementSelect_type);
    declarations.push_back(IfcTextFontSelect_type);
    declarations.push_back(IfcTimeOrRatioSelect_type);
    declarations.push_back(IfcTranslationalStiffnessSelect_type);
    declarations.push_back(IfcTrimmingSelect_type);
    declarations.push_back(IfcUnit_type);
    declarations.push_back(IfcValue_type);
    declarations.push_back(IfcVectorOrDirection_type);
    declarations.push_back(IfcWarpingStiffnessSelect_type);
    declarations.push_back(IfcAppliedValueSelect_type);
    declarations.push_back(IfcCurveFontOrScaledCurveFontSelect_type);
    declarations.push_back(IfcMetricValueSelect_type);
    return new schema_definition("IFC4", declarations, true);
}


#ifdef _MSC_VER
#pragma optimize("", on)
#endif
        
const schema_definition& get_schema() {

    static const schema_definition* s = populate_schema();
    return *s;
}

#endif
