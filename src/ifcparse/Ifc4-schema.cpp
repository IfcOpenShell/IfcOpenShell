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

#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/Ifc4.h"

using namespace IfcParse;

entity* IFC4_IfcActionRequest_type = 0;
entity* IFC4_IfcActor_type = 0;
entity* IFC4_IfcActorRole_type = 0;
entity* IFC4_IfcActuator_type = 0;
entity* IFC4_IfcActuatorType_type = 0;
entity* IFC4_IfcAddress_type = 0;
entity* IFC4_IfcAdvancedBrep_type = 0;
entity* IFC4_IfcAdvancedBrepWithVoids_type = 0;
entity* IFC4_IfcAdvancedFace_type = 0;
entity* IFC4_IfcAirTerminal_type = 0;
entity* IFC4_IfcAirTerminalBox_type = 0;
entity* IFC4_IfcAirTerminalBoxType_type = 0;
entity* IFC4_IfcAirTerminalType_type = 0;
entity* IFC4_IfcAirToAirHeatRecovery_type = 0;
entity* IFC4_IfcAirToAirHeatRecoveryType_type = 0;
entity* IFC4_IfcAlarm_type = 0;
entity* IFC4_IfcAlarmType_type = 0;
entity* IFC4_IfcAnnotation_type = 0;
entity* IFC4_IfcAnnotationFillArea_type = 0;
entity* IFC4_IfcApplication_type = 0;
entity* IFC4_IfcAppliedValue_type = 0;
entity* IFC4_IfcApproval_type = 0;
entity* IFC4_IfcApprovalRelationship_type = 0;
entity* IFC4_IfcArbitraryClosedProfileDef_type = 0;
entity* IFC4_IfcArbitraryOpenProfileDef_type = 0;
entity* IFC4_IfcArbitraryProfileDefWithVoids_type = 0;
entity* IFC4_IfcAsset_type = 0;
entity* IFC4_IfcAsymmetricIShapeProfileDef_type = 0;
entity* IFC4_IfcAudioVisualAppliance_type = 0;
entity* IFC4_IfcAudioVisualApplianceType_type = 0;
entity* IFC4_IfcAxis1Placement_type = 0;
entity* IFC4_IfcAxis2Placement2D_type = 0;
entity* IFC4_IfcAxis2Placement3D_type = 0;
entity* IFC4_IfcBSplineCurve_type = 0;
entity* IFC4_IfcBSplineCurveWithKnots_type = 0;
entity* IFC4_IfcBSplineSurface_type = 0;
entity* IFC4_IfcBSplineSurfaceWithKnots_type = 0;
entity* IFC4_IfcBeam_type = 0;
entity* IFC4_IfcBeamStandardCase_type = 0;
entity* IFC4_IfcBeamType_type = 0;
entity* IFC4_IfcBlobTexture_type = 0;
entity* IFC4_IfcBlock_type = 0;
entity* IFC4_IfcBoiler_type = 0;
entity* IFC4_IfcBoilerType_type = 0;
entity* IFC4_IfcBooleanClippingResult_type = 0;
entity* IFC4_IfcBooleanResult_type = 0;
entity* IFC4_IfcBoundaryCondition_type = 0;
entity* IFC4_IfcBoundaryCurve_type = 0;
entity* IFC4_IfcBoundaryEdgeCondition_type = 0;
entity* IFC4_IfcBoundaryFaceCondition_type = 0;
entity* IFC4_IfcBoundaryNodeCondition_type = 0;
entity* IFC4_IfcBoundaryNodeConditionWarping_type = 0;
entity* IFC4_IfcBoundedCurve_type = 0;
entity* IFC4_IfcBoundedSurface_type = 0;
entity* IFC4_IfcBoundingBox_type = 0;
entity* IFC4_IfcBoxedHalfSpace_type = 0;
entity* IFC4_IfcBuilding_type = 0;
entity* IFC4_IfcBuildingElement_type = 0;
entity* IFC4_IfcBuildingElementPart_type = 0;
entity* IFC4_IfcBuildingElementPartType_type = 0;
entity* IFC4_IfcBuildingElementProxy_type = 0;
entity* IFC4_IfcBuildingElementProxyType_type = 0;
entity* IFC4_IfcBuildingElementType_type = 0;
entity* IFC4_IfcBuildingStorey_type = 0;
entity* IFC4_IfcBuildingSystem_type = 0;
entity* IFC4_IfcBurner_type = 0;
entity* IFC4_IfcBurnerType_type = 0;
entity* IFC4_IfcCShapeProfileDef_type = 0;
entity* IFC4_IfcCableCarrierFitting_type = 0;
entity* IFC4_IfcCableCarrierFittingType_type = 0;
entity* IFC4_IfcCableCarrierSegment_type = 0;
entity* IFC4_IfcCableCarrierSegmentType_type = 0;
entity* IFC4_IfcCableFitting_type = 0;
entity* IFC4_IfcCableFittingType_type = 0;
entity* IFC4_IfcCableSegment_type = 0;
entity* IFC4_IfcCableSegmentType_type = 0;
entity* IFC4_IfcCartesianPoint_type = 0;
entity* IFC4_IfcCartesianPointList_type = 0;
entity* IFC4_IfcCartesianPointList2D_type = 0;
entity* IFC4_IfcCartesianPointList3D_type = 0;
entity* IFC4_IfcCartesianTransformationOperator_type = 0;
entity* IFC4_IfcCartesianTransformationOperator2D_type = 0;
entity* IFC4_IfcCartesianTransformationOperator2DnonUniform_type = 0;
entity* IFC4_IfcCartesianTransformationOperator3D_type = 0;
entity* IFC4_IfcCartesianTransformationOperator3DnonUniform_type = 0;
entity* IFC4_IfcCenterLineProfileDef_type = 0;
entity* IFC4_IfcChiller_type = 0;
entity* IFC4_IfcChillerType_type = 0;
entity* IFC4_IfcChimney_type = 0;
entity* IFC4_IfcChimneyType_type = 0;
entity* IFC4_IfcCircle_type = 0;
entity* IFC4_IfcCircleHollowProfileDef_type = 0;
entity* IFC4_IfcCircleProfileDef_type = 0;
entity* IFC4_IfcCivilElement_type = 0;
entity* IFC4_IfcCivilElementType_type = 0;
entity* IFC4_IfcClassification_type = 0;
entity* IFC4_IfcClassificationReference_type = 0;
entity* IFC4_IfcClosedShell_type = 0;
entity* IFC4_IfcCoil_type = 0;
entity* IFC4_IfcCoilType_type = 0;
entity* IFC4_IfcColourRgb_type = 0;
entity* IFC4_IfcColourRgbList_type = 0;
entity* IFC4_IfcColourSpecification_type = 0;
entity* IFC4_IfcColumn_type = 0;
entity* IFC4_IfcColumnStandardCase_type = 0;
entity* IFC4_IfcColumnType_type = 0;
entity* IFC4_IfcCommunicationsAppliance_type = 0;
entity* IFC4_IfcCommunicationsApplianceType_type = 0;
entity* IFC4_IfcComplexProperty_type = 0;
entity* IFC4_IfcComplexPropertyTemplate_type = 0;
entity* IFC4_IfcCompositeCurve_type = 0;
entity* IFC4_IfcCompositeCurveOnSurface_type = 0;
entity* IFC4_IfcCompositeCurveSegment_type = 0;
entity* IFC4_IfcCompositeProfileDef_type = 0;
entity* IFC4_IfcCompressor_type = 0;
entity* IFC4_IfcCompressorType_type = 0;
entity* IFC4_IfcCondenser_type = 0;
entity* IFC4_IfcCondenserType_type = 0;
entity* IFC4_IfcConic_type = 0;
entity* IFC4_IfcConnectedFaceSet_type = 0;
entity* IFC4_IfcConnectionCurveGeometry_type = 0;
entity* IFC4_IfcConnectionGeometry_type = 0;
entity* IFC4_IfcConnectionPointEccentricity_type = 0;
entity* IFC4_IfcConnectionPointGeometry_type = 0;
entity* IFC4_IfcConnectionSurfaceGeometry_type = 0;
entity* IFC4_IfcConnectionVolumeGeometry_type = 0;
entity* IFC4_IfcConstraint_type = 0;
entity* IFC4_IfcConstructionEquipmentResource_type = 0;
entity* IFC4_IfcConstructionEquipmentResourceType_type = 0;
entity* IFC4_IfcConstructionMaterialResource_type = 0;
entity* IFC4_IfcConstructionMaterialResourceType_type = 0;
entity* IFC4_IfcConstructionProductResource_type = 0;
entity* IFC4_IfcConstructionProductResourceType_type = 0;
entity* IFC4_IfcConstructionResource_type = 0;
entity* IFC4_IfcConstructionResourceType_type = 0;
entity* IFC4_IfcContext_type = 0;
entity* IFC4_IfcContextDependentUnit_type = 0;
entity* IFC4_IfcControl_type = 0;
entity* IFC4_IfcController_type = 0;
entity* IFC4_IfcControllerType_type = 0;
entity* IFC4_IfcConversionBasedUnit_type = 0;
entity* IFC4_IfcConversionBasedUnitWithOffset_type = 0;
entity* IFC4_IfcCooledBeam_type = 0;
entity* IFC4_IfcCooledBeamType_type = 0;
entity* IFC4_IfcCoolingTower_type = 0;
entity* IFC4_IfcCoolingTowerType_type = 0;
entity* IFC4_IfcCoordinateOperation_type = 0;
entity* IFC4_IfcCoordinateReferenceSystem_type = 0;
entity* IFC4_IfcCostItem_type = 0;
entity* IFC4_IfcCostSchedule_type = 0;
entity* IFC4_IfcCostValue_type = 0;
entity* IFC4_IfcCovering_type = 0;
entity* IFC4_IfcCoveringType_type = 0;
entity* IFC4_IfcCrewResource_type = 0;
entity* IFC4_IfcCrewResourceType_type = 0;
entity* IFC4_IfcCsgPrimitive3D_type = 0;
entity* IFC4_IfcCsgSolid_type = 0;
entity* IFC4_IfcCurrencyRelationship_type = 0;
entity* IFC4_IfcCurtainWall_type = 0;
entity* IFC4_IfcCurtainWallType_type = 0;
entity* IFC4_IfcCurve_type = 0;
entity* IFC4_IfcCurveBoundedPlane_type = 0;
entity* IFC4_IfcCurveBoundedSurface_type = 0;
entity* IFC4_IfcCurveStyle_type = 0;
entity* IFC4_IfcCurveStyleFont_type = 0;
entity* IFC4_IfcCurveStyleFontAndScaling_type = 0;
entity* IFC4_IfcCurveStyleFontPattern_type = 0;
entity* IFC4_IfcCylindricalSurface_type = 0;
entity* IFC4_IfcDamper_type = 0;
entity* IFC4_IfcDamperType_type = 0;
entity* IFC4_IfcDerivedProfileDef_type = 0;
entity* IFC4_IfcDerivedUnit_type = 0;
entity* IFC4_IfcDerivedUnitElement_type = 0;
entity* IFC4_IfcDimensionalExponents_type = 0;
entity* IFC4_IfcDirection_type = 0;
entity* IFC4_IfcDiscreteAccessory_type = 0;
entity* IFC4_IfcDiscreteAccessoryType_type = 0;
entity* IFC4_IfcDistributionChamberElement_type = 0;
entity* IFC4_IfcDistributionChamberElementType_type = 0;
entity* IFC4_IfcDistributionCircuit_type = 0;
entity* IFC4_IfcDistributionControlElement_type = 0;
entity* IFC4_IfcDistributionControlElementType_type = 0;
entity* IFC4_IfcDistributionElement_type = 0;
entity* IFC4_IfcDistributionElementType_type = 0;
entity* IFC4_IfcDistributionFlowElement_type = 0;
entity* IFC4_IfcDistributionFlowElementType_type = 0;
entity* IFC4_IfcDistributionPort_type = 0;
entity* IFC4_IfcDistributionSystem_type = 0;
entity* IFC4_IfcDocumentInformation_type = 0;
entity* IFC4_IfcDocumentInformationRelationship_type = 0;
entity* IFC4_IfcDocumentReference_type = 0;
entity* IFC4_IfcDoor_type = 0;
entity* IFC4_IfcDoorLiningProperties_type = 0;
entity* IFC4_IfcDoorPanelProperties_type = 0;
entity* IFC4_IfcDoorStandardCase_type = 0;
entity* IFC4_IfcDoorStyle_type = 0;
entity* IFC4_IfcDoorType_type = 0;
entity* IFC4_IfcDraughtingPreDefinedColour_type = 0;
entity* IFC4_IfcDraughtingPreDefinedCurveFont_type = 0;
entity* IFC4_IfcDuctFitting_type = 0;
entity* IFC4_IfcDuctFittingType_type = 0;
entity* IFC4_IfcDuctSegment_type = 0;
entity* IFC4_IfcDuctSegmentType_type = 0;
entity* IFC4_IfcDuctSilencer_type = 0;
entity* IFC4_IfcDuctSilencerType_type = 0;
entity* IFC4_IfcEdge_type = 0;
entity* IFC4_IfcEdgeCurve_type = 0;
entity* IFC4_IfcEdgeLoop_type = 0;
entity* IFC4_IfcElectricAppliance_type = 0;
entity* IFC4_IfcElectricApplianceType_type = 0;
entity* IFC4_IfcElectricDistributionBoard_type = 0;
entity* IFC4_IfcElectricDistributionBoardType_type = 0;
entity* IFC4_IfcElectricFlowStorageDevice_type = 0;
entity* IFC4_IfcElectricFlowStorageDeviceType_type = 0;
entity* IFC4_IfcElectricGenerator_type = 0;
entity* IFC4_IfcElectricGeneratorType_type = 0;
entity* IFC4_IfcElectricMotor_type = 0;
entity* IFC4_IfcElectricMotorType_type = 0;
entity* IFC4_IfcElectricTimeControl_type = 0;
entity* IFC4_IfcElectricTimeControlType_type = 0;
entity* IFC4_IfcElement_type = 0;
entity* IFC4_IfcElementAssembly_type = 0;
entity* IFC4_IfcElementAssemblyType_type = 0;
entity* IFC4_IfcElementComponent_type = 0;
entity* IFC4_IfcElementComponentType_type = 0;
entity* IFC4_IfcElementQuantity_type = 0;
entity* IFC4_IfcElementType_type = 0;
entity* IFC4_IfcElementarySurface_type = 0;
entity* IFC4_IfcEllipse_type = 0;
entity* IFC4_IfcEllipseProfileDef_type = 0;
entity* IFC4_IfcEnergyConversionDevice_type = 0;
entity* IFC4_IfcEnergyConversionDeviceType_type = 0;
entity* IFC4_IfcEngine_type = 0;
entity* IFC4_IfcEngineType_type = 0;
entity* IFC4_IfcEvaporativeCooler_type = 0;
entity* IFC4_IfcEvaporativeCoolerType_type = 0;
entity* IFC4_IfcEvaporator_type = 0;
entity* IFC4_IfcEvaporatorType_type = 0;
entity* IFC4_IfcEvent_type = 0;
entity* IFC4_IfcEventTime_type = 0;
entity* IFC4_IfcEventType_type = 0;
entity* IFC4_IfcExtendedProperties_type = 0;
entity* IFC4_IfcExternalInformation_type = 0;
entity* IFC4_IfcExternalReference_type = 0;
entity* IFC4_IfcExternalReferenceRelationship_type = 0;
entity* IFC4_IfcExternalSpatialElement_type = 0;
entity* IFC4_IfcExternalSpatialStructureElement_type = 0;
entity* IFC4_IfcExternallyDefinedHatchStyle_type = 0;
entity* IFC4_IfcExternallyDefinedSurfaceStyle_type = 0;
entity* IFC4_IfcExternallyDefinedTextFont_type = 0;
entity* IFC4_IfcExtrudedAreaSolid_type = 0;
entity* IFC4_IfcExtrudedAreaSolidTapered_type = 0;
entity* IFC4_IfcFace_type = 0;
entity* IFC4_IfcFaceBasedSurfaceModel_type = 0;
entity* IFC4_IfcFaceBound_type = 0;
entity* IFC4_IfcFaceOuterBound_type = 0;
entity* IFC4_IfcFaceSurface_type = 0;
entity* IFC4_IfcFacetedBrep_type = 0;
entity* IFC4_IfcFacetedBrepWithVoids_type = 0;
entity* IFC4_IfcFailureConnectionCondition_type = 0;
entity* IFC4_IfcFan_type = 0;
entity* IFC4_IfcFanType_type = 0;
entity* IFC4_IfcFastener_type = 0;
entity* IFC4_IfcFastenerType_type = 0;
entity* IFC4_IfcFeatureElement_type = 0;
entity* IFC4_IfcFeatureElementAddition_type = 0;
entity* IFC4_IfcFeatureElementSubtraction_type = 0;
entity* IFC4_IfcFillAreaStyle_type = 0;
entity* IFC4_IfcFillAreaStyleHatching_type = 0;
entity* IFC4_IfcFillAreaStyleTiles_type = 0;
entity* IFC4_IfcFilter_type = 0;
entity* IFC4_IfcFilterType_type = 0;
entity* IFC4_IfcFireSuppressionTerminal_type = 0;
entity* IFC4_IfcFireSuppressionTerminalType_type = 0;
entity* IFC4_IfcFixedReferenceSweptAreaSolid_type = 0;
entity* IFC4_IfcFlowController_type = 0;
entity* IFC4_IfcFlowControllerType_type = 0;
entity* IFC4_IfcFlowFitting_type = 0;
entity* IFC4_IfcFlowFittingType_type = 0;
entity* IFC4_IfcFlowInstrument_type = 0;
entity* IFC4_IfcFlowInstrumentType_type = 0;
entity* IFC4_IfcFlowMeter_type = 0;
entity* IFC4_IfcFlowMeterType_type = 0;
entity* IFC4_IfcFlowMovingDevice_type = 0;
entity* IFC4_IfcFlowMovingDeviceType_type = 0;
entity* IFC4_IfcFlowSegment_type = 0;
entity* IFC4_IfcFlowSegmentType_type = 0;
entity* IFC4_IfcFlowStorageDevice_type = 0;
entity* IFC4_IfcFlowStorageDeviceType_type = 0;
entity* IFC4_IfcFlowTerminal_type = 0;
entity* IFC4_IfcFlowTerminalType_type = 0;
entity* IFC4_IfcFlowTreatmentDevice_type = 0;
entity* IFC4_IfcFlowTreatmentDeviceType_type = 0;
entity* IFC4_IfcFooting_type = 0;
entity* IFC4_IfcFootingType_type = 0;
entity* IFC4_IfcFurnishingElement_type = 0;
entity* IFC4_IfcFurnishingElementType_type = 0;
entity* IFC4_IfcFurniture_type = 0;
entity* IFC4_IfcFurnitureType_type = 0;
entity* IFC4_IfcGeographicElement_type = 0;
entity* IFC4_IfcGeographicElementType_type = 0;
entity* IFC4_IfcGeometricCurveSet_type = 0;
entity* IFC4_IfcGeometricRepresentationContext_type = 0;
entity* IFC4_IfcGeometricRepresentationItem_type = 0;
entity* IFC4_IfcGeometricRepresentationSubContext_type = 0;
entity* IFC4_IfcGeometricSet_type = 0;
entity* IFC4_IfcGrid_type = 0;
entity* IFC4_IfcGridAxis_type = 0;
entity* IFC4_IfcGridPlacement_type = 0;
entity* IFC4_IfcGroup_type = 0;
entity* IFC4_IfcHalfSpaceSolid_type = 0;
entity* IFC4_IfcHeatExchanger_type = 0;
entity* IFC4_IfcHeatExchangerType_type = 0;
entity* IFC4_IfcHumidifier_type = 0;
entity* IFC4_IfcHumidifierType_type = 0;
entity* IFC4_IfcIShapeProfileDef_type = 0;
entity* IFC4_IfcImageTexture_type = 0;
entity* IFC4_IfcIndexedColourMap_type = 0;
entity* IFC4_IfcIndexedPolyCurve_type = 0;
entity* IFC4_IfcIndexedTextureMap_type = 0;
entity* IFC4_IfcIndexedTriangleTextureMap_type = 0;
entity* IFC4_IfcInterceptor_type = 0;
entity* IFC4_IfcInterceptorType_type = 0;
entity* IFC4_IfcInventory_type = 0;
entity* IFC4_IfcIrregularTimeSeries_type = 0;
entity* IFC4_IfcIrregularTimeSeriesValue_type = 0;
entity* IFC4_IfcJunctionBox_type = 0;
entity* IFC4_IfcJunctionBoxType_type = 0;
entity* IFC4_IfcLShapeProfileDef_type = 0;
entity* IFC4_IfcLaborResource_type = 0;
entity* IFC4_IfcLaborResourceType_type = 0;
entity* IFC4_IfcLagTime_type = 0;
entity* IFC4_IfcLamp_type = 0;
entity* IFC4_IfcLampType_type = 0;
entity* IFC4_IfcLibraryInformation_type = 0;
entity* IFC4_IfcLibraryReference_type = 0;
entity* IFC4_IfcLightDistributionData_type = 0;
entity* IFC4_IfcLightFixture_type = 0;
entity* IFC4_IfcLightFixtureType_type = 0;
entity* IFC4_IfcLightIntensityDistribution_type = 0;
entity* IFC4_IfcLightSource_type = 0;
entity* IFC4_IfcLightSourceAmbient_type = 0;
entity* IFC4_IfcLightSourceDirectional_type = 0;
entity* IFC4_IfcLightSourceGoniometric_type = 0;
entity* IFC4_IfcLightSourcePositional_type = 0;
entity* IFC4_IfcLightSourceSpot_type = 0;
entity* IFC4_IfcLine_type = 0;
entity* IFC4_IfcLocalPlacement_type = 0;
entity* IFC4_IfcLoop_type = 0;
entity* IFC4_IfcManifoldSolidBrep_type = 0;
entity* IFC4_IfcMapConversion_type = 0;
entity* IFC4_IfcMappedItem_type = 0;
entity* IFC4_IfcMaterial_type = 0;
entity* IFC4_IfcMaterialClassificationRelationship_type = 0;
entity* IFC4_IfcMaterialConstituent_type = 0;
entity* IFC4_IfcMaterialConstituentSet_type = 0;
entity* IFC4_IfcMaterialDefinition_type = 0;
entity* IFC4_IfcMaterialDefinitionRepresentation_type = 0;
entity* IFC4_IfcMaterialLayer_type = 0;
entity* IFC4_IfcMaterialLayerSet_type = 0;
entity* IFC4_IfcMaterialLayerSetUsage_type = 0;
entity* IFC4_IfcMaterialLayerWithOffsets_type = 0;
entity* IFC4_IfcMaterialList_type = 0;
entity* IFC4_IfcMaterialProfile_type = 0;
entity* IFC4_IfcMaterialProfileSet_type = 0;
entity* IFC4_IfcMaterialProfileSetUsage_type = 0;
entity* IFC4_IfcMaterialProfileSetUsageTapering_type = 0;
entity* IFC4_IfcMaterialProfileWithOffsets_type = 0;
entity* IFC4_IfcMaterialProperties_type = 0;
entity* IFC4_IfcMaterialRelationship_type = 0;
entity* IFC4_IfcMaterialUsageDefinition_type = 0;
entity* IFC4_IfcMeasureWithUnit_type = 0;
entity* IFC4_IfcMechanicalFastener_type = 0;
entity* IFC4_IfcMechanicalFastenerType_type = 0;
entity* IFC4_IfcMedicalDevice_type = 0;
entity* IFC4_IfcMedicalDeviceType_type = 0;
entity* IFC4_IfcMember_type = 0;
entity* IFC4_IfcMemberStandardCase_type = 0;
entity* IFC4_IfcMemberType_type = 0;
entity* IFC4_IfcMetric_type = 0;
entity* IFC4_IfcMirroredProfileDef_type = 0;
entity* IFC4_IfcMonetaryUnit_type = 0;
entity* IFC4_IfcMotorConnection_type = 0;
entity* IFC4_IfcMotorConnectionType_type = 0;
entity* IFC4_IfcNamedUnit_type = 0;
entity* IFC4_IfcObject_type = 0;
entity* IFC4_IfcObjectDefinition_type = 0;
entity* IFC4_IfcObjectPlacement_type = 0;
entity* IFC4_IfcObjective_type = 0;
entity* IFC4_IfcOccupant_type = 0;
entity* IFC4_IfcOffsetCurve2D_type = 0;
entity* IFC4_IfcOffsetCurve3D_type = 0;
entity* IFC4_IfcOpenShell_type = 0;
entity* IFC4_IfcOpeningElement_type = 0;
entity* IFC4_IfcOpeningStandardCase_type = 0;
entity* IFC4_IfcOrganization_type = 0;
entity* IFC4_IfcOrganizationRelationship_type = 0;
entity* IFC4_IfcOrientedEdge_type = 0;
entity* IFC4_IfcOuterBoundaryCurve_type = 0;
entity* IFC4_IfcOutlet_type = 0;
entity* IFC4_IfcOutletType_type = 0;
entity* IFC4_IfcOwnerHistory_type = 0;
entity* IFC4_IfcParameterizedProfileDef_type = 0;
entity* IFC4_IfcPath_type = 0;
entity* IFC4_IfcPcurve_type = 0;
entity* IFC4_IfcPerformanceHistory_type = 0;
entity* IFC4_IfcPermeableCoveringProperties_type = 0;
entity* IFC4_IfcPermit_type = 0;
entity* IFC4_IfcPerson_type = 0;
entity* IFC4_IfcPersonAndOrganization_type = 0;
entity* IFC4_IfcPhysicalComplexQuantity_type = 0;
entity* IFC4_IfcPhysicalQuantity_type = 0;
entity* IFC4_IfcPhysicalSimpleQuantity_type = 0;
entity* IFC4_IfcPile_type = 0;
entity* IFC4_IfcPileType_type = 0;
entity* IFC4_IfcPipeFitting_type = 0;
entity* IFC4_IfcPipeFittingType_type = 0;
entity* IFC4_IfcPipeSegment_type = 0;
entity* IFC4_IfcPipeSegmentType_type = 0;
entity* IFC4_IfcPixelTexture_type = 0;
entity* IFC4_IfcPlacement_type = 0;
entity* IFC4_IfcPlanarBox_type = 0;
entity* IFC4_IfcPlanarExtent_type = 0;
entity* IFC4_IfcPlane_type = 0;
entity* IFC4_IfcPlate_type = 0;
entity* IFC4_IfcPlateStandardCase_type = 0;
entity* IFC4_IfcPlateType_type = 0;
entity* IFC4_IfcPoint_type = 0;
entity* IFC4_IfcPointOnCurve_type = 0;
entity* IFC4_IfcPointOnSurface_type = 0;
entity* IFC4_IfcPolyLoop_type = 0;
entity* IFC4_IfcPolygonalBoundedHalfSpace_type = 0;
entity* IFC4_IfcPolyline_type = 0;
entity* IFC4_IfcPort_type = 0;
entity* IFC4_IfcPostalAddress_type = 0;
entity* IFC4_IfcPreDefinedColour_type = 0;
entity* IFC4_IfcPreDefinedCurveFont_type = 0;
entity* IFC4_IfcPreDefinedItem_type = 0;
entity* IFC4_IfcPreDefinedProperties_type = 0;
entity* IFC4_IfcPreDefinedPropertySet_type = 0;
entity* IFC4_IfcPreDefinedTextFont_type = 0;
entity* IFC4_IfcPresentationItem_type = 0;
entity* IFC4_IfcPresentationLayerAssignment_type = 0;
entity* IFC4_IfcPresentationLayerWithStyle_type = 0;
entity* IFC4_IfcPresentationStyle_type = 0;
entity* IFC4_IfcPresentationStyleAssignment_type = 0;
entity* IFC4_IfcProcedure_type = 0;
entity* IFC4_IfcProcedureType_type = 0;
entity* IFC4_IfcProcess_type = 0;
entity* IFC4_IfcProduct_type = 0;
entity* IFC4_IfcProductDefinitionShape_type = 0;
entity* IFC4_IfcProductRepresentation_type = 0;
entity* IFC4_IfcProfileDef_type = 0;
entity* IFC4_IfcProfileProperties_type = 0;
entity* IFC4_IfcProject_type = 0;
entity* IFC4_IfcProjectLibrary_type = 0;
entity* IFC4_IfcProjectOrder_type = 0;
entity* IFC4_IfcProjectedCRS_type = 0;
entity* IFC4_IfcProjectionElement_type = 0;
entity* IFC4_IfcProperty_type = 0;
entity* IFC4_IfcPropertyAbstraction_type = 0;
entity* IFC4_IfcPropertyBoundedValue_type = 0;
entity* IFC4_IfcPropertyDefinition_type = 0;
entity* IFC4_IfcPropertyDependencyRelationship_type = 0;
entity* IFC4_IfcPropertyEnumeratedValue_type = 0;
entity* IFC4_IfcPropertyEnumeration_type = 0;
entity* IFC4_IfcPropertyListValue_type = 0;
entity* IFC4_IfcPropertyReferenceValue_type = 0;
entity* IFC4_IfcPropertySet_type = 0;
entity* IFC4_IfcPropertySetDefinition_type = 0;
entity* IFC4_IfcPropertySetTemplate_type = 0;
entity* IFC4_IfcPropertySingleValue_type = 0;
entity* IFC4_IfcPropertyTableValue_type = 0;
entity* IFC4_IfcPropertyTemplate_type = 0;
entity* IFC4_IfcPropertyTemplateDefinition_type = 0;
entity* IFC4_IfcProtectiveDevice_type = 0;
entity* IFC4_IfcProtectiveDeviceTrippingUnit_type = 0;
entity* IFC4_IfcProtectiveDeviceTrippingUnitType_type = 0;
entity* IFC4_IfcProtectiveDeviceType_type = 0;
entity* IFC4_IfcProxy_type = 0;
entity* IFC4_IfcPump_type = 0;
entity* IFC4_IfcPumpType_type = 0;
entity* IFC4_IfcQuantityArea_type = 0;
entity* IFC4_IfcQuantityCount_type = 0;
entity* IFC4_IfcQuantityLength_type = 0;
entity* IFC4_IfcQuantitySet_type = 0;
entity* IFC4_IfcQuantityTime_type = 0;
entity* IFC4_IfcQuantityVolume_type = 0;
entity* IFC4_IfcQuantityWeight_type = 0;
entity* IFC4_IfcRailing_type = 0;
entity* IFC4_IfcRailingType_type = 0;
entity* IFC4_IfcRamp_type = 0;
entity* IFC4_IfcRampFlight_type = 0;
entity* IFC4_IfcRampFlightType_type = 0;
entity* IFC4_IfcRampType_type = 0;
entity* IFC4_IfcRationalBSplineCurveWithKnots_type = 0;
entity* IFC4_IfcRationalBSplineSurfaceWithKnots_type = 0;
entity* IFC4_IfcRectangleHollowProfileDef_type = 0;
entity* IFC4_IfcRectangleProfileDef_type = 0;
entity* IFC4_IfcRectangularPyramid_type = 0;
entity* IFC4_IfcRectangularTrimmedSurface_type = 0;
entity* IFC4_IfcRecurrencePattern_type = 0;
entity* IFC4_IfcReference_type = 0;
entity* IFC4_IfcRegularTimeSeries_type = 0;
entity* IFC4_IfcReinforcementBarProperties_type = 0;
entity* IFC4_IfcReinforcementDefinitionProperties_type = 0;
entity* IFC4_IfcReinforcingBar_type = 0;
entity* IFC4_IfcReinforcingBarType_type = 0;
entity* IFC4_IfcReinforcingElement_type = 0;
entity* IFC4_IfcReinforcingElementType_type = 0;
entity* IFC4_IfcReinforcingMesh_type = 0;
entity* IFC4_IfcReinforcingMeshType_type = 0;
entity* IFC4_IfcRelAggregates_type = 0;
entity* IFC4_IfcRelAssigns_type = 0;
entity* IFC4_IfcRelAssignsToActor_type = 0;
entity* IFC4_IfcRelAssignsToControl_type = 0;
entity* IFC4_IfcRelAssignsToGroup_type = 0;
entity* IFC4_IfcRelAssignsToGroupByFactor_type = 0;
entity* IFC4_IfcRelAssignsToProcess_type = 0;
entity* IFC4_IfcRelAssignsToProduct_type = 0;
entity* IFC4_IfcRelAssignsToResource_type = 0;
entity* IFC4_IfcRelAssociates_type = 0;
entity* IFC4_IfcRelAssociatesApproval_type = 0;
entity* IFC4_IfcRelAssociatesClassification_type = 0;
entity* IFC4_IfcRelAssociatesConstraint_type = 0;
entity* IFC4_IfcRelAssociatesDocument_type = 0;
entity* IFC4_IfcRelAssociatesLibrary_type = 0;
entity* IFC4_IfcRelAssociatesMaterial_type = 0;
entity* IFC4_IfcRelConnects_type = 0;
entity* IFC4_IfcRelConnectsElements_type = 0;
entity* IFC4_IfcRelConnectsPathElements_type = 0;
entity* IFC4_IfcRelConnectsPortToElement_type = 0;
entity* IFC4_IfcRelConnectsPorts_type = 0;
entity* IFC4_IfcRelConnectsStructuralActivity_type = 0;
entity* IFC4_IfcRelConnectsStructuralMember_type = 0;
entity* IFC4_IfcRelConnectsWithEccentricity_type = 0;
entity* IFC4_IfcRelConnectsWithRealizingElements_type = 0;
entity* IFC4_IfcRelContainedInSpatialStructure_type = 0;
entity* IFC4_IfcRelCoversBldgElements_type = 0;
entity* IFC4_IfcRelCoversSpaces_type = 0;
entity* IFC4_IfcRelDeclares_type = 0;
entity* IFC4_IfcRelDecomposes_type = 0;
entity* IFC4_IfcRelDefines_type = 0;
entity* IFC4_IfcRelDefinesByObject_type = 0;
entity* IFC4_IfcRelDefinesByProperties_type = 0;
entity* IFC4_IfcRelDefinesByTemplate_type = 0;
entity* IFC4_IfcRelDefinesByType_type = 0;
entity* IFC4_IfcRelFillsElement_type = 0;
entity* IFC4_IfcRelFlowControlElements_type = 0;
entity* IFC4_IfcRelInterferesElements_type = 0;
entity* IFC4_IfcRelNests_type = 0;
entity* IFC4_IfcRelProjectsElement_type = 0;
entity* IFC4_IfcRelReferencedInSpatialStructure_type = 0;
entity* IFC4_IfcRelSequence_type = 0;
entity* IFC4_IfcRelServicesBuildings_type = 0;
entity* IFC4_IfcRelSpaceBoundary_type = 0;
entity* IFC4_IfcRelSpaceBoundary1stLevel_type = 0;
entity* IFC4_IfcRelSpaceBoundary2ndLevel_type = 0;
entity* IFC4_IfcRelVoidsElement_type = 0;
entity* IFC4_IfcRelationship_type = 0;
entity* IFC4_IfcReparametrisedCompositeCurveSegment_type = 0;
entity* IFC4_IfcRepresentation_type = 0;
entity* IFC4_IfcRepresentationContext_type = 0;
entity* IFC4_IfcRepresentationItem_type = 0;
entity* IFC4_IfcRepresentationMap_type = 0;
entity* IFC4_IfcResource_type = 0;
entity* IFC4_IfcResourceApprovalRelationship_type = 0;
entity* IFC4_IfcResourceConstraintRelationship_type = 0;
entity* IFC4_IfcResourceLevelRelationship_type = 0;
entity* IFC4_IfcResourceTime_type = 0;
entity* IFC4_IfcRevolvedAreaSolid_type = 0;
entity* IFC4_IfcRevolvedAreaSolidTapered_type = 0;
entity* IFC4_IfcRightCircularCone_type = 0;
entity* IFC4_IfcRightCircularCylinder_type = 0;
entity* IFC4_IfcRoof_type = 0;
entity* IFC4_IfcRoofType_type = 0;
entity* IFC4_IfcRoot_type = 0;
entity* IFC4_IfcRoundedRectangleProfileDef_type = 0;
entity* IFC4_IfcSIUnit_type = 0;
entity* IFC4_IfcSanitaryTerminal_type = 0;
entity* IFC4_IfcSanitaryTerminalType_type = 0;
entity* IFC4_IfcSchedulingTime_type = 0;
entity* IFC4_IfcSectionProperties_type = 0;
entity* IFC4_IfcSectionReinforcementProperties_type = 0;
entity* IFC4_IfcSectionedSpine_type = 0;
entity* IFC4_IfcSensor_type = 0;
entity* IFC4_IfcSensorType_type = 0;
entity* IFC4_IfcShadingDevice_type = 0;
entity* IFC4_IfcShadingDeviceType_type = 0;
entity* IFC4_IfcShapeAspect_type = 0;
entity* IFC4_IfcShapeModel_type = 0;
entity* IFC4_IfcShapeRepresentation_type = 0;
entity* IFC4_IfcShellBasedSurfaceModel_type = 0;
entity* IFC4_IfcSimpleProperty_type = 0;
entity* IFC4_IfcSimplePropertyTemplate_type = 0;
entity* IFC4_IfcSite_type = 0;
entity* IFC4_IfcSlab_type = 0;
entity* IFC4_IfcSlabElementedCase_type = 0;
entity* IFC4_IfcSlabStandardCase_type = 0;
entity* IFC4_IfcSlabType_type = 0;
entity* IFC4_IfcSlippageConnectionCondition_type = 0;
entity* IFC4_IfcSolarDevice_type = 0;
entity* IFC4_IfcSolarDeviceType_type = 0;
entity* IFC4_IfcSolidModel_type = 0;
entity* IFC4_IfcSpace_type = 0;
entity* IFC4_IfcSpaceHeater_type = 0;
entity* IFC4_IfcSpaceHeaterType_type = 0;
entity* IFC4_IfcSpaceType_type = 0;
entity* IFC4_IfcSpatialElement_type = 0;
entity* IFC4_IfcSpatialElementType_type = 0;
entity* IFC4_IfcSpatialStructureElement_type = 0;
entity* IFC4_IfcSpatialStructureElementType_type = 0;
entity* IFC4_IfcSpatialZone_type = 0;
entity* IFC4_IfcSpatialZoneType_type = 0;
entity* IFC4_IfcSphere_type = 0;
entity* IFC4_IfcStackTerminal_type = 0;
entity* IFC4_IfcStackTerminalType_type = 0;
entity* IFC4_IfcStair_type = 0;
entity* IFC4_IfcStairFlight_type = 0;
entity* IFC4_IfcStairFlightType_type = 0;
entity* IFC4_IfcStairType_type = 0;
entity* IFC4_IfcStructuralAction_type = 0;
entity* IFC4_IfcStructuralActivity_type = 0;
entity* IFC4_IfcStructuralAnalysisModel_type = 0;
entity* IFC4_IfcStructuralConnection_type = 0;
entity* IFC4_IfcStructuralConnectionCondition_type = 0;
entity* IFC4_IfcStructuralCurveAction_type = 0;
entity* IFC4_IfcStructuralCurveConnection_type = 0;
entity* IFC4_IfcStructuralCurveMember_type = 0;
entity* IFC4_IfcStructuralCurveMemberVarying_type = 0;
entity* IFC4_IfcStructuralCurveReaction_type = 0;
entity* IFC4_IfcStructuralItem_type = 0;
entity* IFC4_IfcStructuralLinearAction_type = 0;
entity* IFC4_IfcStructuralLoad_type = 0;
entity* IFC4_IfcStructuralLoadCase_type = 0;
entity* IFC4_IfcStructuralLoadConfiguration_type = 0;
entity* IFC4_IfcStructuralLoadGroup_type = 0;
entity* IFC4_IfcStructuralLoadLinearForce_type = 0;
entity* IFC4_IfcStructuralLoadOrResult_type = 0;
entity* IFC4_IfcStructuralLoadPlanarForce_type = 0;
entity* IFC4_IfcStructuralLoadSingleDisplacement_type = 0;
entity* IFC4_IfcStructuralLoadSingleDisplacementDistortion_type = 0;
entity* IFC4_IfcStructuralLoadSingleForce_type = 0;
entity* IFC4_IfcStructuralLoadSingleForceWarping_type = 0;
entity* IFC4_IfcStructuralLoadStatic_type = 0;
entity* IFC4_IfcStructuralLoadTemperature_type = 0;
entity* IFC4_IfcStructuralMember_type = 0;
entity* IFC4_IfcStructuralPlanarAction_type = 0;
entity* IFC4_IfcStructuralPointAction_type = 0;
entity* IFC4_IfcStructuralPointConnection_type = 0;
entity* IFC4_IfcStructuralPointReaction_type = 0;
entity* IFC4_IfcStructuralReaction_type = 0;
entity* IFC4_IfcStructuralResultGroup_type = 0;
entity* IFC4_IfcStructuralSurfaceAction_type = 0;
entity* IFC4_IfcStructuralSurfaceConnection_type = 0;
entity* IFC4_IfcStructuralSurfaceMember_type = 0;
entity* IFC4_IfcStructuralSurfaceMemberVarying_type = 0;
entity* IFC4_IfcStructuralSurfaceReaction_type = 0;
entity* IFC4_IfcStyleModel_type = 0;
entity* IFC4_IfcStyledItem_type = 0;
entity* IFC4_IfcStyledRepresentation_type = 0;
entity* IFC4_IfcSubContractResource_type = 0;
entity* IFC4_IfcSubContractResourceType_type = 0;
entity* IFC4_IfcSubedge_type = 0;
entity* IFC4_IfcSurface_type = 0;
entity* IFC4_IfcSurfaceCurveSweptAreaSolid_type = 0;
entity* IFC4_IfcSurfaceFeature_type = 0;
entity* IFC4_IfcSurfaceOfLinearExtrusion_type = 0;
entity* IFC4_IfcSurfaceOfRevolution_type = 0;
entity* IFC4_IfcSurfaceReinforcementArea_type = 0;
entity* IFC4_IfcSurfaceStyle_type = 0;
entity* IFC4_IfcSurfaceStyleLighting_type = 0;
entity* IFC4_IfcSurfaceStyleRefraction_type = 0;
entity* IFC4_IfcSurfaceStyleRendering_type = 0;
entity* IFC4_IfcSurfaceStyleShading_type = 0;
entity* IFC4_IfcSurfaceStyleWithTextures_type = 0;
entity* IFC4_IfcSurfaceTexture_type = 0;
entity* IFC4_IfcSweptAreaSolid_type = 0;
entity* IFC4_IfcSweptDiskSolid_type = 0;
entity* IFC4_IfcSweptDiskSolidPolygonal_type = 0;
entity* IFC4_IfcSweptSurface_type = 0;
entity* IFC4_IfcSwitchingDevice_type = 0;
entity* IFC4_IfcSwitchingDeviceType_type = 0;
entity* IFC4_IfcSystem_type = 0;
entity* IFC4_IfcSystemFurnitureElement_type = 0;
entity* IFC4_IfcSystemFurnitureElementType_type = 0;
entity* IFC4_IfcTShapeProfileDef_type = 0;
entity* IFC4_IfcTable_type = 0;
entity* IFC4_IfcTableColumn_type = 0;
entity* IFC4_IfcTableRow_type = 0;
entity* IFC4_IfcTank_type = 0;
entity* IFC4_IfcTankType_type = 0;
entity* IFC4_IfcTask_type = 0;
entity* IFC4_IfcTaskTime_type = 0;
entity* IFC4_IfcTaskTimeRecurring_type = 0;
entity* IFC4_IfcTaskType_type = 0;
entity* IFC4_IfcTelecomAddress_type = 0;
entity* IFC4_IfcTendon_type = 0;
entity* IFC4_IfcTendonAnchor_type = 0;
entity* IFC4_IfcTendonAnchorType_type = 0;
entity* IFC4_IfcTendonType_type = 0;
entity* IFC4_IfcTessellatedFaceSet_type = 0;
entity* IFC4_IfcTessellatedItem_type = 0;
entity* IFC4_IfcTextLiteral_type = 0;
entity* IFC4_IfcTextLiteralWithExtent_type = 0;
entity* IFC4_IfcTextStyle_type = 0;
entity* IFC4_IfcTextStyleFontModel_type = 0;
entity* IFC4_IfcTextStyleForDefinedFont_type = 0;
entity* IFC4_IfcTextStyleTextModel_type = 0;
entity* IFC4_IfcTextureCoordinate_type = 0;
entity* IFC4_IfcTextureCoordinateGenerator_type = 0;
entity* IFC4_IfcTextureMap_type = 0;
entity* IFC4_IfcTextureVertex_type = 0;
entity* IFC4_IfcTextureVertexList_type = 0;
entity* IFC4_IfcTimePeriod_type = 0;
entity* IFC4_IfcTimeSeries_type = 0;
entity* IFC4_IfcTimeSeriesValue_type = 0;
entity* IFC4_IfcTopologicalRepresentationItem_type = 0;
entity* IFC4_IfcTopologyRepresentation_type = 0;
entity* IFC4_IfcTransformer_type = 0;
entity* IFC4_IfcTransformerType_type = 0;
entity* IFC4_IfcTransportElement_type = 0;
entity* IFC4_IfcTransportElementType_type = 0;
entity* IFC4_IfcTrapeziumProfileDef_type = 0;
entity* IFC4_IfcTriangulatedFaceSet_type = 0;
entity* IFC4_IfcTrimmedCurve_type = 0;
entity* IFC4_IfcTubeBundle_type = 0;
entity* IFC4_IfcTubeBundleType_type = 0;
entity* IFC4_IfcTypeObject_type = 0;
entity* IFC4_IfcTypeProcess_type = 0;
entity* IFC4_IfcTypeProduct_type = 0;
entity* IFC4_IfcTypeResource_type = 0;
entity* IFC4_IfcUShapeProfileDef_type = 0;
entity* IFC4_IfcUnitAssignment_type = 0;
entity* IFC4_IfcUnitaryControlElement_type = 0;
entity* IFC4_IfcUnitaryControlElementType_type = 0;
entity* IFC4_IfcUnitaryEquipment_type = 0;
entity* IFC4_IfcUnitaryEquipmentType_type = 0;
entity* IFC4_IfcValve_type = 0;
entity* IFC4_IfcValveType_type = 0;
entity* IFC4_IfcVector_type = 0;
entity* IFC4_IfcVertex_type = 0;
entity* IFC4_IfcVertexLoop_type = 0;
entity* IFC4_IfcVertexPoint_type = 0;
entity* IFC4_IfcVibrationIsolator_type = 0;
entity* IFC4_IfcVibrationIsolatorType_type = 0;
entity* IFC4_IfcVirtualElement_type = 0;
entity* IFC4_IfcVirtualGridIntersection_type = 0;
entity* IFC4_IfcVoidingFeature_type = 0;
entity* IFC4_IfcWall_type = 0;
entity* IFC4_IfcWallElementedCase_type = 0;
entity* IFC4_IfcWallStandardCase_type = 0;
entity* IFC4_IfcWallType_type = 0;
entity* IFC4_IfcWasteTerminal_type = 0;
entity* IFC4_IfcWasteTerminalType_type = 0;
entity* IFC4_IfcWindow_type = 0;
entity* IFC4_IfcWindowLiningProperties_type = 0;
entity* IFC4_IfcWindowPanelProperties_type = 0;
entity* IFC4_IfcWindowStandardCase_type = 0;
entity* IFC4_IfcWindowStyle_type = 0;
entity* IFC4_IfcWindowType_type = 0;
entity* IFC4_IfcWorkCalendar_type = 0;
entity* IFC4_IfcWorkControl_type = 0;
entity* IFC4_IfcWorkPlan_type = 0;
entity* IFC4_IfcWorkSchedule_type = 0;
entity* IFC4_IfcWorkTime_type = 0;
entity* IFC4_IfcZShapeProfileDef_type = 0;
entity* IFC4_IfcZone_type = 0;
type_declaration* IFC4_IfcAbsorbedDoseMeasure_type = 0;
type_declaration* IFC4_IfcAccelerationMeasure_type = 0;
type_declaration* IFC4_IfcAmountOfSubstanceMeasure_type = 0;
type_declaration* IFC4_IfcAngularVelocityMeasure_type = 0;
type_declaration* IFC4_IfcArcIndex_type = 0;
type_declaration* IFC4_IfcAreaDensityMeasure_type = 0;
type_declaration* IFC4_IfcAreaMeasure_type = 0;
type_declaration* IFC4_IfcBinary_type = 0;
type_declaration* IFC4_IfcBoolean_type = 0;
type_declaration* IFC4_IfcBoxAlignment_type = 0;
type_declaration* IFC4_IfcCardinalPointReference_type = 0;
type_declaration* IFC4_IfcComplexNumber_type = 0;
type_declaration* IFC4_IfcCompoundPlaneAngleMeasure_type = 0;
type_declaration* IFC4_IfcContextDependentMeasure_type = 0;
type_declaration* IFC4_IfcCountMeasure_type = 0;
type_declaration* IFC4_IfcCurvatureMeasure_type = 0;
type_declaration* IFC4_IfcDate_type = 0;
type_declaration* IFC4_IfcDateTime_type = 0;
type_declaration* IFC4_IfcDayInMonthNumber_type = 0;
type_declaration* IFC4_IfcDayInWeekNumber_type = 0;
type_declaration* IFC4_IfcDescriptiveMeasure_type = 0;
type_declaration* IFC4_IfcDimensionCount_type = 0;
type_declaration* IFC4_IfcDoseEquivalentMeasure_type = 0;
type_declaration* IFC4_IfcDuration_type = 0;
type_declaration* IFC4_IfcDynamicViscosityMeasure_type = 0;
type_declaration* IFC4_IfcElectricCapacitanceMeasure_type = 0;
type_declaration* IFC4_IfcElectricChargeMeasure_type = 0;
type_declaration* IFC4_IfcElectricConductanceMeasure_type = 0;
type_declaration* IFC4_IfcElectricCurrentMeasure_type = 0;
type_declaration* IFC4_IfcElectricResistanceMeasure_type = 0;
type_declaration* IFC4_IfcElectricVoltageMeasure_type = 0;
type_declaration* IFC4_IfcEnergyMeasure_type = 0;
type_declaration* IFC4_IfcFontStyle_type = 0;
type_declaration* IFC4_IfcFontVariant_type = 0;
type_declaration* IFC4_IfcFontWeight_type = 0;
type_declaration* IFC4_IfcForceMeasure_type = 0;
type_declaration* IFC4_IfcFrequencyMeasure_type = 0;
type_declaration* IFC4_IfcGloballyUniqueId_type = 0;
type_declaration* IFC4_IfcHeatFluxDensityMeasure_type = 0;
type_declaration* IFC4_IfcHeatingValueMeasure_type = 0;
type_declaration* IFC4_IfcIdentifier_type = 0;
type_declaration* IFC4_IfcIlluminanceMeasure_type = 0;
type_declaration* IFC4_IfcInductanceMeasure_type = 0;
type_declaration* IFC4_IfcInteger_type = 0;
type_declaration* IFC4_IfcIntegerCountRateMeasure_type = 0;
type_declaration* IFC4_IfcIonConcentrationMeasure_type = 0;
type_declaration* IFC4_IfcIsothermalMoistureCapacityMeasure_type = 0;
type_declaration* IFC4_IfcKinematicViscosityMeasure_type = 0;
type_declaration* IFC4_IfcLabel_type = 0;
type_declaration* IFC4_IfcLanguageId_type = 0;
type_declaration* IFC4_IfcLengthMeasure_type = 0;
type_declaration* IFC4_IfcLineIndex_type = 0;
type_declaration* IFC4_IfcLinearForceMeasure_type = 0;
type_declaration* IFC4_IfcLinearMomentMeasure_type = 0;
type_declaration* IFC4_IfcLinearStiffnessMeasure_type = 0;
type_declaration* IFC4_IfcLinearVelocityMeasure_type = 0;
type_declaration* IFC4_IfcLogical_type = 0;
type_declaration* IFC4_IfcLuminousFluxMeasure_type = 0;
type_declaration* IFC4_IfcLuminousIntensityDistributionMeasure_type = 0;
type_declaration* IFC4_IfcLuminousIntensityMeasure_type = 0;
type_declaration* IFC4_IfcMagneticFluxDensityMeasure_type = 0;
type_declaration* IFC4_IfcMagneticFluxMeasure_type = 0;
type_declaration* IFC4_IfcMassDensityMeasure_type = 0;
type_declaration* IFC4_IfcMassFlowRateMeasure_type = 0;
type_declaration* IFC4_IfcMassMeasure_type = 0;
type_declaration* IFC4_IfcMassPerLengthMeasure_type = 0;
type_declaration* IFC4_IfcModulusOfElasticityMeasure_type = 0;
type_declaration* IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type = 0;
type_declaration* IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type = 0;
type_declaration* IFC4_IfcModulusOfSubgradeReactionMeasure_type = 0;
type_declaration* IFC4_IfcMoistureDiffusivityMeasure_type = 0;
type_declaration* IFC4_IfcMolecularWeightMeasure_type = 0;
type_declaration* IFC4_IfcMomentOfInertiaMeasure_type = 0;
type_declaration* IFC4_IfcMonetaryMeasure_type = 0;
type_declaration* IFC4_IfcMonthInYearNumber_type = 0;
type_declaration* IFC4_IfcNonNegativeLengthMeasure_type = 0;
type_declaration* IFC4_IfcNormalisedRatioMeasure_type = 0;
type_declaration* IFC4_IfcNumericMeasure_type = 0;
type_declaration* IFC4_IfcPHMeasure_type = 0;
type_declaration* IFC4_IfcParameterValue_type = 0;
type_declaration* IFC4_IfcPlanarForceMeasure_type = 0;
type_declaration* IFC4_IfcPlaneAngleMeasure_type = 0;
type_declaration* IFC4_IfcPositiveInteger_type = 0;
type_declaration* IFC4_IfcPositiveLengthMeasure_type = 0;
type_declaration* IFC4_IfcPositivePlaneAngleMeasure_type = 0;
type_declaration* IFC4_IfcPositiveRatioMeasure_type = 0;
type_declaration* IFC4_IfcPowerMeasure_type = 0;
type_declaration* IFC4_IfcPresentableText_type = 0;
type_declaration* IFC4_IfcPressureMeasure_type = 0;
type_declaration* IFC4_IfcPropertySetDefinitionSet_type = 0;
type_declaration* IFC4_IfcRadioActivityMeasure_type = 0;
type_declaration* IFC4_IfcRatioMeasure_type = 0;
type_declaration* IFC4_IfcReal_type = 0;
type_declaration* IFC4_IfcRotationalFrequencyMeasure_type = 0;
type_declaration* IFC4_IfcRotationalMassMeasure_type = 0;
type_declaration* IFC4_IfcRotationalStiffnessMeasure_type = 0;
type_declaration* IFC4_IfcSectionModulusMeasure_type = 0;
type_declaration* IFC4_IfcSectionalAreaIntegralMeasure_type = 0;
type_declaration* IFC4_IfcShearModulusMeasure_type = 0;
type_declaration* IFC4_IfcSolidAngleMeasure_type = 0;
type_declaration* IFC4_IfcSoundPowerLevelMeasure_type = 0;
type_declaration* IFC4_IfcSoundPowerMeasure_type = 0;
type_declaration* IFC4_IfcSoundPressureLevelMeasure_type = 0;
type_declaration* IFC4_IfcSoundPressureMeasure_type = 0;
type_declaration* IFC4_IfcSpecificHeatCapacityMeasure_type = 0;
type_declaration* IFC4_IfcSpecularExponent_type = 0;
type_declaration* IFC4_IfcSpecularRoughness_type = 0;
type_declaration* IFC4_IfcStrippedOptional_type = 0;
type_declaration* IFC4_IfcTemperatureGradientMeasure_type = 0;
type_declaration* IFC4_IfcTemperatureRateOfChangeMeasure_type = 0;
type_declaration* IFC4_IfcText_type = 0;
type_declaration* IFC4_IfcTextAlignment_type = 0;
type_declaration* IFC4_IfcTextDecoration_type = 0;
type_declaration* IFC4_IfcTextFontName_type = 0;
type_declaration* IFC4_IfcTextTransformation_type = 0;
type_declaration* IFC4_IfcThermalAdmittanceMeasure_type = 0;
type_declaration* IFC4_IfcThermalConductivityMeasure_type = 0;
type_declaration* IFC4_IfcThermalExpansionCoefficientMeasure_type = 0;
type_declaration* IFC4_IfcThermalResistanceMeasure_type = 0;
type_declaration* IFC4_IfcThermalTransmittanceMeasure_type = 0;
type_declaration* IFC4_IfcThermodynamicTemperatureMeasure_type = 0;
type_declaration* IFC4_IfcTime_type = 0;
type_declaration* IFC4_IfcTimeMeasure_type = 0;
type_declaration* IFC4_IfcTimeStamp_type = 0;
type_declaration* IFC4_IfcTorqueMeasure_type = 0;
type_declaration* IFC4_IfcURIReference_type = 0;
type_declaration* IFC4_IfcVaporPermeabilityMeasure_type = 0;
type_declaration* IFC4_IfcVolumeMeasure_type = 0;
type_declaration* IFC4_IfcVolumetricFlowRateMeasure_type = 0;
type_declaration* IFC4_IfcWarpingConstantMeasure_type = 0;
type_declaration* IFC4_IfcWarpingMomentMeasure_type = 0;
select_type* IFC4_IfcActorSelect_type = 0;
select_type* IFC4_IfcAppliedValueSelect_type = 0;
select_type* IFC4_IfcAxis2Placement_type = 0;
select_type* IFC4_IfcBendingParameterSelect_type = 0;
select_type* IFC4_IfcBooleanOperand_type = 0;
select_type* IFC4_IfcClassificationReferenceSelect_type = 0;
select_type* IFC4_IfcClassificationSelect_type = 0;
select_type* IFC4_IfcColour_type = 0;
select_type* IFC4_IfcColourOrFactor_type = 0;
select_type* IFC4_IfcCoordinateReferenceSystemSelect_type = 0;
select_type* IFC4_IfcCsgSelect_type = 0;
select_type* IFC4_IfcCurveFontOrScaledCurveFontSelect_type = 0;
select_type* IFC4_IfcCurveOnSurface_type = 0;
select_type* IFC4_IfcCurveOrEdgeCurve_type = 0;
select_type* IFC4_IfcCurveStyleFontSelect_type = 0;
select_type* IFC4_IfcDefinitionSelect_type = 0;
select_type* IFC4_IfcDerivedMeasureValue_type = 0;
select_type* IFC4_IfcDocumentSelect_type = 0;
select_type* IFC4_IfcFillStyleSelect_type = 0;
select_type* IFC4_IfcGeometricSetSelect_type = 0;
select_type* IFC4_IfcGridPlacementDirectionSelect_type = 0;
select_type* IFC4_IfcHatchLineDistanceSelect_type = 0;
select_type* IFC4_IfcLayeredItem_type = 0;
select_type* IFC4_IfcLibrarySelect_type = 0;
select_type* IFC4_IfcLightDistributionDataSourceSelect_type = 0;
select_type* IFC4_IfcMaterialSelect_type = 0;
select_type* IFC4_IfcMeasureValue_type = 0;
select_type* IFC4_IfcMetricValueSelect_type = 0;
select_type* IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type = 0;
select_type* IFC4_IfcModulusOfSubgradeReactionSelect_type = 0;
select_type* IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type = 0;
select_type* IFC4_IfcObjectReferenceSelect_type = 0;
select_type* IFC4_IfcPointOrVertexPoint_type = 0;
select_type* IFC4_IfcPresentationStyleSelect_type = 0;
select_type* IFC4_IfcProcessSelect_type = 0;
select_type* IFC4_IfcProductRepresentationSelect_type = 0;
select_type* IFC4_IfcProductSelect_type = 0;
select_type* IFC4_IfcPropertySetDefinitionSelect_type = 0;
select_type* IFC4_IfcResourceObjectSelect_type = 0;
select_type* IFC4_IfcResourceSelect_type = 0;
select_type* IFC4_IfcRotationalStiffnessSelect_type = 0;
select_type* IFC4_IfcSegmentIndexSelect_type = 0;
select_type* IFC4_IfcShell_type = 0;
select_type* IFC4_IfcSimpleValue_type = 0;
select_type* IFC4_IfcSizeSelect_type = 0;
select_type* IFC4_IfcSolidOrShell_type = 0;
select_type* IFC4_IfcSpaceBoundarySelect_type = 0;
select_type* IFC4_IfcSpecularHighlightSelect_type = 0;
select_type* IFC4_IfcStructuralActivityAssignmentSelect_type = 0;
select_type* IFC4_IfcStyleAssignmentSelect_type = 0;
select_type* IFC4_IfcSurfaceOrFaceSurface_type = 0;
select_type* IFC4_IfcSurfaceStyleElementSelect_type = 0;
select_type* IFC4_IfcTextFontSelect_type = 0;
select_type* IFC4_IfcTimeOrRatioSelect_type = 0;
select_type* IFC4_IfcTranslationalStiffnessSelect_type = 0;
select_type* IFC4_IfcTrimmingSelect_type = 0;
select_type* IFC4_IfcUnit_type = 0;
select_type* IFC4_IfcValue_type = 0;
select_type* IFC4_IfcVectorOrDirection_type = 0;
select_type* IFC4_IfcWarpingStiffnessSelect_type = 0;
enumeration_type* IFC4_IfcActionRequestTypeEnum_type = 0;
enumeration_type* IFC4_IfcActionSourceTypeEnum_type = 0;
enumeration_type* IFC4_IfcActionTypeEnum_type = 0;
enumeration_type* IFC4_IfcActuatorTypeEnum_type = 0;
enumeration_type* IFC4_IfcAddressTypeEnum_type = 0;
enumeration_type* IFC4_IfcAirTerminalBoxTypeEnum_type = 0;
enumeration_type* IFC4_IfcAirTerminalTypeEnum_type = 0;
enumeration_type* IFC4_IfcAirToAirHeatRecoveryTypeEnum_type = 0;
enumeration_type* IFC4_IfcAlarmTypeEnum_type = 0;
enumeration_type* IFC4_IfcAnalysisModelTypeEnum_type = 0;
enumeration_type* IFC4_IfcAnalysisTheoryTypeEnum_type = 0;
enumeration_type* IFC4_IfcArithmeticOperatorEnum_type = 0;
enumeration_type* IFC4_IfcAssemblyPlaceEnum_type = 0;
enumeration_type* IFC4_IfcAudioVisualApplianceTypeEnum_type = 0;
enumeration_type* IFC4_IfcBSplineCurveForm_type = 0;
enumeration_type* IFC4_IfcBSplineSurfaceForm_type = 0;
enumeration_type* IFC4_IfcBeamTypeEnum_type = 0;
enumeration_type* IFC4_IfcBenchmarkEnum_type = 0;
enumeration_type* IFC4_IfcBoilerTypeEnum_type = 0;
enumeration_type* IFC4_IfcBooleanOperator_type = 0;
enumeration_type* IFC4_IfcBuildingElementPartTypeEnum_type = 0;
enumeration_type* IFC4_IfcBuildingElementProxyTypeEnum_type = 0;
enumeration_type* IFC4_IfcBuildingSystemTypeEnum_type = 0;
enumeration_type* IFC4_IfcBurnerTypeEnum_type = 0;
enumeration_type* IFC4_IfcCableCarrierFittingTypeEnum_type = 0;
enumeration_type* IFC4_IfcCableCarrierSegmentTypeEnum_type = 0;
enumeration_type* IFC4_IfcCableFittingTypeEnum_type = 0;
enumeration_type* IFC4_IfcCableSegmentTypeEnum_type = 0;
enumeration_type* IFC4_IfcChangeActionEnum_type = 0;
enumeration_type* IFC4_IfcChillerTypeEnum_type = 0;
enumeration_type* IFC4_IfcChimneyTypeEnum_type = 0;
enumeration_type* IFC4_IfcCoilTypeEnum_type = 0;
enumeration_type* IFC4_IfcColumnTypeEnum_type = 0;
enumeration_type* IFC4_IfcCommunicationsApplianceTypeEnum_type = 0;
enumeration_type* IFC4_IfcComplexPropertyTemplateTypeEnum_type = 0;
enumeration_type* IFC4_IfcCompressorTypeEnum_type = 0;
enumeration_type* IFC4_IfcCondenserTypeEnum_type = 0;
enumeration_type* IFC4_IfcConnectionTypeEnum_type = 0;
enumeration_type* IFC4_IfcConstraintEnum_type = 0;
enumeration_type* IFC4_IfcConstructionEquipmentResourceTypeEnum_type = 0;
enumeration_type* IFC4_IfcConstructionMaterialResourceTypeEnum_type = 0;
enumeration_type* IFC4_IfcConstructionProductResourceTypeEnum_type = 0;
enumeration_type* IFC4_IfcControllerTypeEnum_type = 0;
enumeration_type* IFC4_IfcCooledBeamTypeEnum_type = 0;
enumeration_type* IFC4_IfcCoolingTowerTypeEnum_type = 0;
enumeration_type* IFC4_IfcCostItemTypeEnum_type = 0;
enumeration_type* IFC4_IfcCostScheduleTypeEnum_type = 0;
enumeration_type* IFC4_IfcCoveringTypeEnum_type = 0;
enumeration_type* IFC4_IfcCrewResourceTypeEnum_type = 0;
enumeration_type* IFC4_IfcCurtainWallTypeEnum_type = 0;
enumeration_type* IFC4_IfcCurveInterpolationEnum_type = 0;
enumeration_type* IFC4_IfcDamperTypeEnum_type = 0;
enumeration_type* IFC4_IfcDataOriginEnum_type = 0;
enumeration_type* IFC4_IfcDerivedUnitEnum_type = 0;
enumeration_type* IFC4_IfcDirectionSenseEnum_type = 0;
enumeration_type* IFC4_IfcDiscreteAccessoryTypeEnum_type = 0;
enumeration_type* IFC4_IfcDistributionChamberElementTypeEnum_type = 0;
enumeration_type* IFC4_IfcDistributionPortTypeEnum_type = 0;
enumeration_type* IFC4_IfcDistributionSystemEnum_type = 0;
enumeration_type* IFC4_IfcDocumentConfidentialityEnum_type = 0;
enumeration_type* IFC4_IfcDocumentStatusEnum_type = 0;
enumeration_type* IFC4_IfcDoorPanelOperationEnum_type = 0;
enumeration_type* IFC4_IfcDoorPanelPositionEnum_type = 0;
enumeration_type* IFC4_IfcDoorStyleConstructionEnum_type = 0;
enumeration_type* IFC4_IfcDoorStyleOperationEnum_type = 0;
enumeration_type* IFC4_IfcDoorTypeEnum_type = 0;
enumeration_type* IFC4_IfcDoorTypeOperationEnum_type = 0;
enumeration_type* IFC4_IfcDuctFittingTypeEnum_type = 0;
enumeration_type* IFC4_IfcDuctSegmentTypeEnum_type = 0;
enumeration_type* IFC4_IfcDuctSilencerTypeEnum_type = 0;
enumeration_type* IFC4_IfcElectricApplianceTypeEnum_type = 0;
enumeration_type* IFC4_IfcElectricDistributionBoardTypeEnum_type = 0;
enumeration_type* IFC4_IfcElectricFlowStorageDeviceTypeEnum_type = 0;
enumeration_type* IFC4_IfcElectricGeneratorTypeEnum_type = 0;
enumeration_type* IFC4_IfcElectricMotorTypeEnum_type = 0;
enumeration_type* IFC4_IfcElectricTimeControlTypeEnum_type = 0;
enumeration_type* IFC4_IfcElementAssemblyTypeEnum_type = 0;
enumeration_type* IFC4_IfcElementCompositionEnum_type = 0;
enumeration_type* IFC4_IfcEngineTypeEnum_type = 0;
enumeration_type* IFC4_IfcEvaporativeCoolerTypeEnum_type = 0;
enumeration_type* IFC4_IfcEvaporatorTypeEnum_type = 0;
enumeration_type* IFC4_IfcEventTriggerTypeEnum_type = 0;
enumeration_type* IFC4_IfcEventTypeEnum_type = 0;
enumeration_type* IFC4_IfcExternalSpatialElementTypeEnum_type = 0;
enumeration_type* IFC4_IfcFanTypeEnum_type = 0;
enumeration_type* IFC4_IfcFastenerTypeEnum_type = 0;
enumeration_type* IFC4_IfcFilterTypeEnum_type = 0;
enumeration_type* IFC4_IfcFireSuppressionTerminalTypeEnum_type = 0;
enumeration_type* IFC4_IfcFlowDirectionEnum_type = 0;
enumeration_type* IFC4_IfcFlowInstrumentTypeEnum_type = 0;
enumeration_type* IFC4_IfcFlowMeterTypeEnum_type = 0;
enumeration_type* IFC4_IfcFootingTypeEnum_type = 0;
enumeration_type* IFC4_IfcFurnitureTypeEnum_type = 0;
enumeration_type* IFC4_IfcGeographicElementTypeEnum_type = 0;
enumeration_type* IFC4_IfcGeometricProjectionEnum_type = 0;
enumeration_type* IFC4_IfcGlobalOrLocalEnum_type = 0;
enumeration_type* IFC4_IfcGridTypeEnum_type = 0;
enumeration_type* IFC4_IfcHeatExchangerTypeEnum_type = 0;
enumeration_type* IFC4_IfcHumidifierTypeEnum_type = 0;
enumeration_type* IFC4_IfcInterceptorTypeEnum_type = 0;
enumeration_type* IFC4_IfcInternalOrExternalEnum_type = 0;
enumeration_type* IFC4_IfcInventoryTypeEnum_type = 0;
enumeration_type* IFC4_IfcJunctionBoxTypeEnum_type = 0;
enumeration_type* IFC4_IfcKnotType_type = 0;
enumeration_type* IFC4_IfcLaborResourceTypeEnum_type = 0;
enumeration_type* IFC4_IfcLampTypeEnum_type = 0;
enumeration_type* IFC4_IfcLayerSetDirectionEnum_type = 0;
enumeration_type* IFC4_IfcLightDistributionCurveEnum_type = 0;
enumeration_type* IFC4_IfcLightEmissionSourceEnum_type = 0;
enumeration_type* IFC4_IfcLightFixtureTypeEnum_type = 0;
enumeration_type* IFC4_IfcLoadGroupTypeEnum_type = 0;
enumeration_type* IFC4_IfcLogicalOperatorEnum_type = 0;
enumeration_type* IFC4_IfcMechanicalFastenerTypeEnum_type = 0;
enumeration_type* IFC4_IfcMedicalDeviceTypeEnum_type = 0;
enumeration_type* IFC4_IfcMemberTypeEnum_type = 0;
enumeration_type* IFC4_IfcMotorConnectionTypeEnum_type = 0;
enumeration_type* IFC4_IfcNullStyle_type = 0;
enumeration_type* IFC4_IfcObjectTypeEnum_type = 0;
enumeration_type* IFC4_IfcObjectiveEnum_type = 0;
enumeration_type* IFC4_IfcOccupantTypeEnum_type = 0;
enumeration_type* IFC4_IfcOpeningElementTypeEnum_type = 0;
enumeration_type* IFC4_IfcOutletTypeEnum_type = 0;
enumeration_type* IFC4_IfcPerformanceHistoryTypeEnum_type = 0;
enumeration_type* IFC4_IfcPermeableCoveringOperationEnum_type = 0;
enumeration_type* IFC4_IfcPermitTypeEnum_type = 0;
enumeration_type* IFC4_IfcPhysicalOrVirtualEnum_type = 0;
enumeration_type* IFC4_IfcPileConstructionEnum_type = 0;
enumeration_type* IFC4_IfcPileTypeEnum_type = 0;
enumeration_type* IFC4_IfcPipeFittingTypeEnum_type = 0;
enumeration_type* IFC4_IfcPipeSegmentTypeEnum_type = 0;
enumeration_type* IFC4_IfcPlateTypeEnum_type = 0;
enumeration_type* IFC4_IfcProcedureTypeEnum_type = 0;
enumeration_type* IFC4_IfcProfileTypeEnum_type = 0;
enumeration_type* IFC4_IfcProjectOrderTypeEnum_type = 0;
enumeration_type* IFC4_IfcProjectedOrTrueLengthEnum_type = 0;
enumeration_type* IFC4_IfcProjectionElementTypeEnum_type = 0;
enumeration_type* IFC4_IfcPropertySetTemplateTypeEnum_type = 0;
enumeration_type* IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type = 0;
enumeration_type* IFC4_IfcProtectiveDeviceTypeEnum_type = 0;
enumeration_type* IFC4_IfcPumpTypeEnum_type = 0;
enumeration_type* IFC4_IfcRailingTypeEnum_type = 0;
enumeration_type* IFC4_IfcRampFlightTypeEnum_type = 0;
enumeration_type* IFC4_IfcRampTypeEnum_type = 0;
enumeration_type* IFC4_IfcRecurrenceTypeEnum_type = 0;
enumeration_type* IFC4_IfcReflectanceMethodEnum_type = 0;
enumeration_type* IFC4_IfcReinforcingBarRoleEnum_type = 0;
enumeration_type* IFC4_IfcReinforcingBarSurfaceEnum_type = 0;
enumeration_type* IFC4_IfcReinforcingBarTypeEnum_type = 0;
enumeration_type* IFC4_IfcReinforcingMeshTypeEnum_type = 0;
enumeration_type* IFC4_IfcRoleEnum_type = 0;
enumeration_type* IFC4_IfcRoofTypeEnum_type = 0;
enumeration_type* IFC4_IfcSIPrefix_type = 0;
enumeration_type* IFC4_IfcSIUnitName_type = 0;
enumeration_type* IFC4_IfcSanitaryTerminalTypeEnum_type = 0;
enumeration_type* IFC4_IfcSectionTypeEnum_type = 0;
enumeration_type* IFC4_IfcSensorTypeEnum_type = 0;
enumeration_type* IFC4_IfcSequenceEnum_type = 0;
enumeration_type* IFC4_IfcShadingDeviceTypeEnum_type = 0;
enumeration_type* IFC4_IfcSimplePropertyTemplateTypeEnum_type = 0;
enumeration_type* IFC4_IfcSlabTypeEnum_type = 0;
enumeration_type* IFC4_IfcSolarDeviceTypeEnum_type = 0;
enumeration_type* IFC4_IfcSpaceHeaterTypeEnum_type = 0;
enumeration_type* IFC4_IfcSpaceTypeEnum_type = 0;
enumeration_type* IFC4_IfcSpatialZoneTypeEnum_type = 0;
enumeration_type* IFC4_IfcStackTerminalTypeEnum_type = 0;
enumeration_type* IFC4_IfcStairFlightTypeEnum_type = 0;
enumeration_type* IFC4_IfcStairTypeEnum_type = 0;
enumeration_type* IFC4_IfcStateEnum_type = 0;
enumeration_type* IFC4_IfcStructuralCurveActivityTypeEnum_type = 0;
enumeration_type* IFC4_IfcStructuralCurveMemberTypeEnum_type = 0;
enumeration_type* IFC4_IfcStructuralSurfaceActivityTypeEnum_type = 0;
enumeration_type* IFC4_IfcStructuralSurfaceMemberTypeEnum_type = 0;
enumeration_type* IFC4_IfcSubContractResourceTypeEnum_type = 0;
enumeration_type* IFC4_IfcSurfaceFeatureTypeEnum_type = 0;
enumeration_type* IFC4_IfcSurfaceSide_type = 0;
enumeration_type* IFC4_IfcSwitchingDeviceTypeEnum_type = 0;
enumeration_type* IFC4_IfcSystemFurnitureElementTypeEnum_type = 0;
enumeration_type* IFC4_IfcTankTypeEnum_type = 0;
enumeration_type* IFC4_IfcTaskDurationEnum_type = 0;
enumeration_type* IFC4_IfcTaskTypeEnum_type = 0;
enumeration_type* IFC4_IfcTendonAnchorTypeEnum_type = 0;
enumeration_type* IFC4_IfcTendonTypeEnum_type = 0;
enumeration_type* IFC4_IfcTextPath_type = 0;
enumeration_type* IFC4_IfcTimeSeriesDataTypeEnum_type = 0;
enumeration_type* IFC4_IfcTransformerTypeEnum_type = 0;
enumeration_type* IFC4_IfcTransitionCode_type = 0;
enumeration_type* IFC4_IfcTransportElementTypeEnum_type = 0;
enumeration_type* IFC4_IfcTrimmingPreference_type = 0;
enumeration_type* IFC4_IfcTubeBundleTypeEnum_type = 0;
enumeration_type* IFC4_IfcUnitEnum_type = 0;
enumeration_type* IFC4_IfcUnitaryControlElementTypeEnum_type = 0;
enumeration_type* IFC4_IfcUnitaryEquipmentTypeEnum_type = 0;
enumeration_type* IFC4_IfcValveTypeEnum_type = 0;
enumeration_type* IFC4_IfcVibrationIsolatorTypeEnum_type = 0;
enumeration_type* IFC4_IfcVoidingFeatureTypeEnum_type = 0;
enumeration_type* IFC4_IfcWallTypeEnum_type = 0;
enumeration_type* IFC4_IfcWasteTerminalTypeEnum_type = 0;
enumeration_type* IFC4_IfcWindowPanelOperationEnum_type = 0;
enumeration_type* IFC4_IfcWindowPanelPositionEnum_type = 0;
enumeration_type* IFC4_IfcWindowStyleConstructionEnum_type = 0;
enumeration_type* IFC4_IfcWindowStyleOperationEnum_type = 0;
enumeration_type* IFC4_IfcWindowTypeEnum_type = 0;
enumeration_type* IFC4_IfcWindowTypePartitioningEnum_type = 0;
enumeration_type* IFC4_IfcWorkCalendarTypeEnum_type = 0;
enumeration_type* IFC4_IfcWorkPlanTypeEnum_type = 0;
enumeration_type* IFC4_IfcWorkScheduleTypeEnum_type = 0;

class IFC4_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        switch(data->type()->index_in_schema()) {
            case 0: return new ::Ifc4::IfcAbsorbedDoseMeasure(data);
            case 1: return new ::Ifc4::IfcAccelerationMeasure(data);
            case 2: return new ::Ifc4::IfcActionRequest(data);
            case 6: return new ::Ifc4::IfcActor(data);
            case 7: return new ::Ifc4::IfcActorRole(data);
            case 9: return new ::Ifc4::IfcActuator(data);
            case 10: return new ::Ifc4::IfcActuatorType(data);
            case 12: return new ::Ifc4::IfcAddress(data);
            case 14: return new ::Ifc4::IfcAdvancedBrep(data);
            case 15: return new ::Ifc4::IfcAdvancedBrepWithVoids(data);
            case 16: return new ::Ifc4::IfcAdvancedFace(data);
            case 17: return new ::Ifc4::IfcAirTerminal(data);
            case 18: return new ::Ifc4::IfcAirTerminalBox(data);
            case 19: return new ::Ifc4::IfcAirTerminalBoxType(data);
            case 21: return new ::Ifc4::IfcAirTerminalType(data);
            case 23: return new ::Ifc4::IfcAirToAirHeatRecovery(data);
            case 24: return new ::Ifc4::IfcAirToAirHeatRecoveryType(data);
            case 26: return new ::Ifc4::IfcAlarm(data);
            case 27: return new ::Ifc4::IfcAlarmType(data);
            case 29: return new ::Ifc4::IfcAmountOfSubstanceMeasure(data);
            case 32: return new ::Ifc4::IfcAngularVelocityMeasure(data);
            case 33: return new ::Ifc4::IfcAnnotation(data);
            case 34: return new ::Ifc4::IfcAnnotationFillArea(data);
            case 35: return new ::Ifc4::IfcApplication(data);
            case 36: return new ::Ifc4::IfcAppliedValue(data);
            case 38: return new ::Ifc4::IfcApproval(data);
            case 39: return new ::Ifc4::IfcApprovalRelationship(data);
            case 40: return new ::Ifc4::IfcArbitraryClosedProfileDef(data);
            case 41: return new ::Ifc4::IfcArbitraryOpenProfileDef(data);
            case 42: return new ::Ifc4::IfcArbitraryProfileDefWithVoids(data);
            case 43: return new ::Ifc4::IfcArcIndex(data);
            case 44: return new ::Ifc4::IfcAreaDensityMeasure(data);
            case 45: return new ::Ifc4::IfcAreaMeasure(data);
            case 48: return new ::Ifc4::IfcAsset(data);
            case 49: return new ::Ifc4::IfcAsymmetricIShapeProfileDef(data);
            case 50: return new ::Ifc4::IfcAudioVisualAppliance(data);
            case 51: return new ::Ifc4::IfcAudioVisualApplianceType(data);
            case 53: return new ::Ifc4::IfcAxis1Placement(data);
            case 55: return new ::Ifc4::IfcAxis2Placement2D(data);
            case 56: return new ::Ifc4::IfcAxis2Placement3D(data);
            case 57: return new ::Ifc4::IfcBeam(data);
            case 58: return new ::Ifc4::IfcBeamStandardCase(data);
            case 59: return new ::Ifc4::IfcBeamType(data);
            case 63: return new ::Ifc4::IfcBinary(data);
            case 64: return new ::Ifc4::IfcBlobTexture(data);
            case 65: return new ::Ifc4::IfcBlock(data);
            case 66: return new ::Ifc4::IfcBoiler(data);
            case 67: return new ::Ifc4::IfcBoilerType(data);
            case 69: return new ::Ifc4::IfcBoolean(data);
            case 70: return new ::Ifc4::IfcBooleanClippingResult(data);
            case 73: return new ::Ifc4::IfcBooleanResult(data);
            case 74: return new ::Ifc4::IfcBoundaryCondition(data);
            case 75: return new ::Ifc4::IfcBoundaryCurve(data);
            case 76: return new ::Ifc4::IfcBoundaryEdgeCondition(data);
            case 77: return new ::Ifc4::IfcBoundaryFaceCondition(data);
            case 78: return new ::Ifc4::IfcBoundaryNodeCondition(data);
            case 79: return new ::Ifc4::IfcBoundaryNodeConditionWarping(data);
            case 80: return new ::Ifc4::IfcBoundedCurve(data);
            case 81: return new ::Ifc4::IfcBoundedSurface(data);
            case 82: return new ::Ifc4::IfcBoundingBox(data);
            case 83: return new ::Ifc4::IfcBoxAlignment(data);
            case 84: return new ::Ifc4::IfcBoxedHalfSpace(data);
            case 85: return new ::Ifc4::IfcBSplineCurve(data);
            case 87: return new ::Ifc4::IfcBSplineCurveWithKnots(data);
            case 88: return new ::Ifc4::IfcBSplineSurface(data);
            case 90: return new ::Ifc4::IfcBSplineSurfaceWithKnots(data);
            case 91: return new ::Ifc4::IfcBuilding(data);
            case 92: return new ::Ifc4::IfcBuildingElement(data);
            case 93: return new ::Ifc4::IfcBuildingElementPart(data);
            case 94: return new ::Ifc4::IfcBuildingElementPartType(data);
            case 96: return new ::Ifc4::IfcBuildingElementProxy(data);
            case 97: return new ::Ifc4::IfcBuildingElementProxyType(data);
            case 99: return new ::Ifc4::IfcBuildingElementType(data);
            case 100: return new ::Ifc4::IfcBuildingStorey(data);
            case 101: return new ::Ifc4::IfcBuildingSystem(data);
            case 103: return new ::Ifc4::IfcBurner(data);
            case 104: return new ::Ifc4::IfcBurnerType(data);
            case 106: return new ::Ifc4::IfcCableCarrierFitting(data);
            case 107: return new ::Ifc4::IfcCableCarrierFittingType(data);
            case 109: return new ::Ifc4::IfcCableCarrierSegment(data);
            case 110: return new ::Ifc4::IfcCableCarrierSegmentType(data);
            case 112: return new ::Ifc4::IfcCableFitting(data);
            case 113: return new ::Ifc4::IfcCableFittingType(data);
            case 115: return new ::Ifc4::IfcCableSegment(data);
            case 116: return new ::Ifc4::IfcCableSegmentType(data);
            case 118: return new ::Ifc4::IfcCardinalPointReference(data);
            case 119: return new ::Ifc4::IfcCartesianPoint(data);
            case 120: return new ::Ifc4::IfcCartesianPointList(data);
            case 121: return new ::Ifc4::IfcCartesianPointList2D(data);
            case 122: return new ::Ifc4::IfcCartesianPointList3D(data);
            case 123: return new ::Ifc4::IfcCartesianTransformationOperator(data);
            case 124: return new ::Ifc4::IfcCartesianTransformationOperator2D(data);
            case 125: return new ::Ifc4::IfcCartesianTransformationOperator2DnonUniform(data);
            case 126: return new ::Ifc4::IfcCartesianTransformationOperator3D(data);
            case 127: return new ::Ifc4::IfcCartesianTransformationOperator3DnonUniform(data);
            case 128: return new ::Ifc4::IfcCenterLineProfileDef(data);
            case 130: return new ::Ifc4::IfcChiller(data);
            case 131: return new ::Ifc4::IfcChillerType(data);
            case 133: return new ::Ifc4::IfcChimney(data);
            case 134: return new ::Ifc4::IfcChimneyType(data);
            case 136: return new ::Ifc4::IfcCircle(data);
            case 137: return new ::Ifc4::IfcCircleHollowProfileDef(data);
            case 138: return new ::Ifc4::IfcCircleProfileDef(data);
            case 139: return new ::Ifc4::IfcCivilElement(data);
            case 140: return new ::Ifc4::IfcCivilElementType(data);
            case 141: return new ::Ifc4::IfcClassification(data);
            case 142: return new ::Ifc4::IfcClassificationReference(data);
            case 145: return new ::Ifc4::IfcClosedShell(data);
            case 146: return new ::Ifc4::IfcCoil(data);
            case 147: return new ::Ifc4::IfcCoilType(data);
            case 151: return new ::Ifc4::IfcColourRgb(data);
            case 152: return new ::Ifc4::IfcColourRgbList(data);
            case 153: return new ::Ifc4::IfcColourSpecification(data);
            case 154: return new ::Ifc4::IfcColumn(data);
            case 155: return new ::Ifc4::IfcColumnStandardCase(data);
            case 156: return new ::Ifc4::IfcColumnType(data);
            case 158: return new ::Ifc4::IfcCommunicationsAppliance(data);
            case 159: return new ::Ifc4::IfcCommunicationsApplianceType(data);
            case 161: return new ::Ifc4::IfcComplexNumber(data);
            case 162: return new ::Ifc4::IfcComplexProperty(data);
            case 163: return new ::Ifc4::IfcComplexPropertyTemplate(data);
            case 165: return new ::Ifc4::IfcCompositeCurve(data);
            case 166: return new ::Ifc4::IfcCompositeCurveOnSurface(data);
            case 167: return new ::Ifc4::IfcCompositeCurveSegment(data);
            case 168: return new ::Ifc4::IfcCompositeProfileDef(data);
            case 169: return new ::Ifc4::IfcCompoundPlaneAngleMeasure(data);
            case 170: return new ::Ifc4::IfcCompressor(data);
            case 171: return new ::Ifc4::IfcCompressorType(data);
            case 173: return new ::Ifc4::IfcCondenser(data);
            case 174: return new ::Ifc4::IfcCondenserType(data);
            case 176: return new ::Ifc4::IfcConic(data);
            case 177: return new ::Ifc4::IfcConnectedFaceSet(data);
            case 178: return new ::Ifc4::IfcConnectionCurveGeometry(data);
            case 179: return new ::Ifc4::IfcConnectionGeometry(data);
            case 180: return new ::Ifc4::IfcConnectionPointEccentricity(data);
            case 181: return new ::Ifc4::IfcConnectionPointGeometry(data);
            case 182: return new ::Ifc4::IfcConnectionSurfaceGeometry(data);
            case 184: return new ::Ifc4::IfcConnectionVolumeGeometry(data);
            case 185: return new ::Ifc4::IfcConstraint(data);
            case 187: return new ::Ifc4::IfcConstructionEquipmentResource(data);
            case 188: return new ::Ifc4::IfcConstructionEquipmentResourceType(data);
            case 190: return new ::Ifc4::IfcConstructionMaterialResource(data);
            case 191: return new ::Ifc4::IfcConstructionMaterialResourceType(data);
            case 193: return new ::Ifc4::IfcConstructionProductResource(data);
            case 194: return new ::Ifc4::IfcConstructionProductResourceType(data);
            case 196: return new ::Ifc4::IfcConstructionResource(data);
            case 197: return new ::Ifc4::IfcConstructionResourceType(data);
            case 198: return new ::Ifc4::IfcContext(data);
            case 199: return new ::Ifc4::IfcContextDependentMeasure(data);
            case 200: return new ::Ifc4::IfcContextDependentUnit(data);
            case 201: return new ::Ifc4::IfcControl(data);
            case 202: return new ::Ifc4::IfcController(data);
            case 203: return new ::Ifc4::IfcControllerType(data);
            case 205: return new ::Ifc4::IfcConversionBasedUnit(data);
            case 206: return new ::Ifc4::IfcConversionBasedUnitWithOffset(data);
            case 207: return new ::Ifc4::IfcCooledBeam(data);
            case 208: return new ::Ifc4::IfcCooledBeamType(data);
            case 210: return new ::Ifc4::IfcCoolingTower(data);
            case 211: return new ::Ifc4::IfcCoolingTowerType(data);
            case 213: return new ::Ifc4::IfcCoordinateOperation(data);
            case 214: return new ::Ifc4::IfcCoordinateReferenceSystem(data);
            case 216: return new ::Ifc4::IfcCostItem(data);
            case 218: return new ::Ifc4::IfcCostSchedule(data);
            case 220: return new ::Ifc4::IfcCostValue(data);
            case 221: return new ::Ifc4::IfcCountMeasure(data);
            case 222: return new ::Ifc4::IfcCovering(data);
            case 223: return new ::Ifc4::IfcCoveringType(data);
            case 225: return new ::Ifc4::IfcCrewResource(data);
            case 226: return new ::Ifc4::IfcCrewResourceType(data);
            case 228: return new ::Ifc4::IfcCsgPrimitive3D(data);
            case 230: return new ::Ifc4::IfcCsgSolid(data);
            case 231: return new ::Ifc4::IfcCShapeProfileDef(data);
            case 232: return new ::Ifc4::IfcCurrencyRelationship(data);
            case 233: return new ::Ifc4::IfcCurtainWall(data);
            case 234: return new ::Ifc4::IfcCurtainWallType(data);
            case 236: return new ::Ifc4::IfcCurvatureMeasure(data);
            case 237: return new ::Ifc4::IfcCurve(data);
            case 238: return new ::Ifc4::IfcCurveBoundedPlane(data);
            case 239: return new ::Ifc4::IfcCurveBoundedSurface(data);
            case 244: return new ::Ifc4::IfcCurveStyle(data);
            case 245: return new ::Ifc4::IfcCurveStyleFont(data);
            case 246: return new ::Ifc4::IfcCurveStyleFontAndScaling(data);
            case 247: return new ::Ifc4::IfcCurveStyleFontPattern(data);
            case 249: return new ::Ifc4::IfcCylindricalSurface(data);
            case 250: return new ::Ifc4::IfcDamper(data);
            case 251: return new ::Ifc4::IfcDamperType(data);
            case 254: return new ::Ifc4::IfcDate(data);
            case 255: return new ::Ifc4::IfcDateTime(data);
            case 256: return new ::Ifc4::IfcDayInMonthNumber(data);
            case 257: return new ::Ifc4::IfcDayInWeekNumber(data);
            case 260: return new ::Ifc4::IfcDerivedProfileDef(data);
            case 261: return new ::Ifc4::IfcDerivedUnit(data);
            case 262: return new ::Ifc4::IfcDerivedUnitElement(data);
            case 264: return new ::Ifc4::IfcDescriptiveMeasure(data);
            case 265: return new ::Ifc4::IfcDimensionalExponents(data);
            case 266: return new ::Ifc4::IfcDimensionCount(data);
            case 267: return new ::Ifc4::IfcDirection(data);
            case 269: return new ::Ifc4::IfcDiscreteAccessory(data);
            case 270: return new ::Ifc4::IfcDiscreteAccessoryType(data);
            case 272: return new ::Ifc4::IfcDistributionChamberElement(data);
            case 273: return new ::Ifc4::IfcDistributionChamberElementType(data);
            case 275: return new ::Ifc4::IfcDistributionCircuit(data);
            case 276: return new ::Ifc4::IfcDistributionControlElement(data);
            case 277: return new ::Ifc4::IfcDistributionControlElementType(data);
            case 278: return new ::Ifc4::IfcDistributionElement(data);
            case 279: return new ::Ifc4::IfcDistributionElementType(data);
            case 280: return new ::Ifc4::IfcDistributionFlowElement(data);
            case 281: return new ::Ifc4::IfcDistributionFlowElementType(data);
            case 282: return new ::Ifc4::IfcDistributionPort(data);
            case 284: return new ::Ifc4::IfcDistributionSystem(data);
            case 287: return new ::Ifc4::IfcDocumentInformation(data);
            case 288: return new ::Ifc4::IfcDocumentInformationRelationship(data);
            case 289: return new ::Ifc4::IfcDocumentReference(data);
            case 292: return new ::Ifc4::IfcDoor(data);
            case 293: return new ::Ifc4::IfcDoorLiningProperties(data);
            case 296: return new ::Ifc4::IfcDoorPanelProperties(data);
            case 297: return new ::Ifc4::IfcDoorStandardCase(data);
            case 298: return new ::Ifc4::IfcDoorStyle(data);
            case 301: return new ::Ifc4::IfcDoorType(data);
            case 304: return new ::Ifc4::IfcDoseEquivalentMeasure(data);
            case 305: return new ::Ifc4::IfcDraughtingPreDefinedColour(data);
            case 306: return new ::Ifc4::IfcDraughtingPreDefinedCurveFont(data);
            case 307: return new ::Ifc4::IfcDuctFitting(data);
            case 308: return new ::Ifc4::IfcDuctFittingType(data);
            case 310: return new ::Ifc4::IfcDuctSegment(data);
            case 311: return new ::Ifc4::IfcDuctSegmentType(data);
            case 313: return new ::Ifc4::IfcDuctSilencer(data);
            case 314: return new ::Ifc4::IfcDuctSilencerType(data);
            case 316: return new ::Ifc4::IfcDuration(data);
            case 317: return new ::Ifc4::IfcDynamicViscosityMeasure(data);
            case 318: return new ::Ifc4::IfcEdge(data);
            case 319: return new ::Ifc4::IfcEdgeCurve(data);
            case 320: return new ::Ifc4::IfcEdgeLoop(data);
            case 321: return new ::Ifc4::IfcElectricAppliance(data);
            case 322: return new ::Ifc4::IfcElectricApplianceType(data);
            case 324: return new ::Ifc4::IfcElectricCapacitanceMeasure(data);
            case 325: return new ::Ifc4::IfcElectricChargeMeasure(data);
            case 326: return new ::Ifc4::IfcElectricConductanceMeasure(data);
            case 327: return new ::Ifc4::IfcElectricCurrentMeasure(data);
            case 328: return new ::Ifc4::IfcElectricDistributionBoard(data);
            case 329: return new ::Ifc4::IfcElectricDistributionBoardType(data);
            case 331: return new ::Ifc4::IfcElectricFlowStorageDevice(data);
            case 332: return new ::Ifc4::IfcElectricFlowStorageDeviceType(data);
            case 334: return new ::Ifc4::IfcElectricGenerator(data);
            case 335: return new ::Ifc4::IfcElectricGeneratorType(data);
            case 337: return new ::Ifc4::IfcElectricMotor(data);
            case 338: return new ::Ifc4::IfcElectricMotorType(data);
            case 340: return new ::Ifc4::IfcElectricResistanceMeasure(data);
            case 341: return new ::Ifc4::IfcElectricTimeControl(data);
            case 342: return new ::Ifc4::IfcElectricTimeControlType(data);
            case 344: return new ::Ifc4::IfcElectricVoltageMeasure(data);
            case 345: return new ::Ifc4::IfcElement(data);
            case 346: return new ::Ifc4::IfcElementarySurface(data);
            case 347: return new ::Ifc4::IfcElementAssembly(data);
            case 348: return new ::Ifc4::IfcElementAssemblyType(data);
            case 350: return new ::Ifc4::IfcElementComponent(data);
            case 351: return new ::Ifc4::IfcElementComponentType(data);
            case 353: return new ::Ifc4::IfcElementQuantity(data);
            case 354: return new ::Ifc4::IfcElementType(data);
            case 355: return new ::Ifc4::IfcEllipse(data);
            case 356: return new ::Ifc4::IfcEllipseProfileDef(data);
            case 357: return new ::Ifc4::IfcEnergyConversionDevice(data);
            case 358: return new ::Ifc4::IfcEnergyConversionDeviceType(data);
            case 359: return new ::Ifc4::IfcEnergyMeasure(data);
            case 360: return new ::Ifc4::IfcEngine(data);
            case 361: return new ::Ifc4::IfcEngineType(data);
            case 363: return new ::Ifc4::IfcEvaporativeCooler(data);
            case 364: return new ::Ifc4::IfcEvaporativeCoolerType(data);
            case 366: return new ::Ifc4::IfcEvaporator(data);
            case 367: return new ::Ifc4::IfcEvaporatorType(data);
            case 369: return new ::Ifc4::IfcEvent(data);
            case 370: return new ::Ifc4::IfcEventTime(data);
            case 372: return new ::Ifc4::IfcEventType(data);
            case 374: return new ::Ifc4::IfcExtendedProperties(data);
            case 375: return new ::Ifc4::IfcExternalInformation(data);
            case 376: return new ::Ifc4::IfcExternallyDefinedHatchStyle(data);
            case 377: return new ::Ifc4::IfcExternallyDefinedSurfaceStyle(data);
            case 378: return new ::Ifc4::IfcExternallyDefinedTextFont(data);
            case 379: return new ::Ifc4::IfcExternalReference(data);
            case 380: return new ::Ifc4::IfcExternalReferenceRelationship(data);
            case 381: return new ::Ifc4::IfcExternalSpatialElement(data);
            case 383: return new ::Ifc4::IfcExternalSpatialStructureElement(data);
            case 384: return new ::Ifc4::IfcExtrudedAreaSolid(data);
            case 385: return new ::Ifc4::IfcExtrudedAreaSolidTapered(data);
            case 386: return new ::Ifc4::IfcFace(data);
            case 387: return new ::Ifc4::IfcFaceBasedSurfaceModel(data);
            case 388: return new ::Ifc4::IfcFaceBound(data);
            case 389: return new ::Ifc4::IfcFaceOuterBound(data);
            case 390: return new ::Ifc4::IfcFaceSurface(data);
            case 391: return new ::Ifc4::IfcFacetedBrep(data);
            case 392: return new ::Ifc4::IfcFacetedBrepWithVoids(data);
            case 393: return new ::Ifc4::IfcFailureConnectionCondition(data);
            case 394: return new ::Ifc4::IfcFan(data);
            case 395: return new ::Ifc4::IfcFanType(data);
            case 397: return new ::Ifc4::IfcFastener(data);
            case 398: return new ::Ifc4::IfcFastenerType(data);
            case 400: return new ::Ifc4::IfcFeatureElement(data);
            case 401: return new ::Ifc4::IfcFeatureElementAddition(data);
            case 402: return new ::Ifc4::IfcFeatureElementSubtraction(data);
            case 403: return new ::Ifc4::IfcFillAreaStyle(data);
            case 404: return new ::Ifc4::IfcFillAreaStyleHatching(data);
            case 405: return new ::Ifc4::IfcFillAreaStyleTiles(data);
            case 407: return new ::Ifc4::IfcFilter(data);
            case 408: return new ::Ifc4::IfcFilterType(data);
            case 410: return new ::Ifc4::IfcFireSuppressionTerminal(data);
            case 411: return new ::Ifc4::IfcFireSuppressionTerminalType(data);
            case 413: return new ::Ifc4::IfcFixedReferenceSweptAreaSolid(data);
            case 414: return new ::Ifc4::IfcFlowController(data);
            case 415: return new ::Ifc4::IfcFlowControllerType(data);
            case 417: return new ::Ifc4::IfcFlowFitting(data);
            case 418: return new ::Ifc4::IfcFlowFittingType(data);
            case 419: return new ::Ifc4::IfcFlowInstrument(data);
            case 420: return new ::Ifc4::IfcFlowInstrumentType(data);
            case 422: return new ::Ifc4::IfcFlowMeter(data);
            case 423: return new ::Ifc4::IfcFlowMeterType(data);
            case 425: return new ::Ifc4::IfcFlowMovingDevice(data);
            case 426: return new ::Ifc4::IfcFlowMovingDeviceType(data);
            case 427: return new ::Ifc4::IfcFlowSegment(data);
            case 428: return new ::Ifc4::IfcFlowSegmentType(data);
            case 429: return new ::Ifc4::IfcFlowStorageDevice(data);
            case 430: return new ::Ifc4::IfcFlowStorageDeviceType(data);
            case 431: return new ::Ifc4::IfcFlowTerminal(data);
            case 432: return new ::Ifc4::IfcFlowTerminalType(data);
            case 433: return new ::Ifc4::IfcFlowTreatmentDevice(data);
            case 434: return new ::Ifc4::IfcFlowTreatmentDeviceType(data);
            case 435: return new ::Ifc4::IfcFontStyle(data);
            case 436: return new ::Ifc4::IfcFontVariant(data);
            case 437: return new ::Ifc4::IfcFontWeight(data);
            case 438: return new ::Ifc4::IfcFooting(data);
            case 439: return new ::Ifc4::IfcFootingType(data);
            case 441: return new ::Ifc4::IfcForceMeasure(data);
            case 442: return new ::Ifc4::IfcFrequencyMeasure(data);
            case 443: return new ::Ifc4::IfcFurnishingElement(data);
            case 444: return new ::Ifc4::IfcFurnishingElementType(data);
            case 445: return new ::Ifc4::IfcFurniture(data);
            case 446: return new ::Ifc4::IfcFurnitureType(data);
            case 448: return new ::Ifc4::IfcGeographicElement(data);
            case 449: return new ::Ifc4::IfcGeographicElementType(data);
            case 451: return new ::Ifc4::IfcGeometricCurveSet(data);
            case 453: return new ::Ifc4::IfcGeometricRepresentationContext(data);
            case 454: return new ::Ifc4::IfcGeometricRepresentationItem(data);
            case 455: return new ::Ifc4::IfcGeometricRepresentationSubContext(data);
            case 456: return new ::Ifc4::IfcGeometricSet(data);
            case 458: return new ::Ifc4::IfcGloballyUniqueId(data);
            case 460: return new ::Ifc4::IfcGrid(data);
            case 461: return new ::Ifc4::IfcGridAxis(data);
            case 462: return new ::Ifc4::IfcGridPlacement(data);
            case 465: return new ::Ifc4::IfcGroup(data);
            case 466: return new ::Ifc4::IfcHalfSpaceSolid(data);
            case 468: return new ::Ifc4::IfcHeatExchanger(data);
            case 469: return new ::Ifc4::IfcHeatExchangerType(data);
            case 471: return new ::Ifc4::IfcHeatFluxDensityMeasure(data);
            case 472: return new ::Ifc4::IfcHeatingValueMeasure(data);
            case 473: return new ::Ifc4::IfcHumidifier(data);
            case 474: return new ::Ifc4::IfcHumidifierType(data);
            case 476: return new ::Ifc4::IfcIdentifier(data);
            case 477: return new ::Ifc4::IfcIlluminanceMeasure(data);
            case 478: return new ::Ifc4::IfcImageTexture(data);
            case 479: return new ::Ifc4::IfcIndexedColourMap(data);
            case 480: return new ::Ifc4::IfcIndexedPolyCurve(data);
            case 481: return new ::Ifc4::IfcIndexedTextureMap(data);
            case 482: return new ::Ifc4::IfcIndexedTriangleTextureMap(data);
            case 483: return new ::Ifc4::IfcInductanceMeasure(data);
            case 484: return new ::Ifc4::IfcInteger(data);
            case 485: return new ::Ifc4::IfcIntegerCountRateMeasure(data);
            case 486: return new ::Ifc4::IfcInterceptor(data);
            case 487: return new ::Ifc4::IfcInterceptorType(data);
            case 490: return new ::Ifc4::IfcInventory(data);
            case 492: return new ::Ifc4::IfcIonConcentrationMeasure(data);
            case 493: return new ::Ifc4::IfcIrregularTimeSeries(data);
            case 494: return new ::Ifc4::IfcIrregularTimeSeriesValue(data);
            case 495: return new ::Ifc4::IfcIShapeProfileDef(data);
            case 496: return new ::Ifc4::IfcIsothermalMoistureCapacityMeasure(data);
            case 497: return new ::Ifc4::IfcJunctionBox(data);
            case 498: return new ::Ifc4::IfcJunctionBoxType(data);
            case 500: return new ::Ifc4::IfcKinematicViscosityMeasure(data);
            case 502: return new ::Ifc4::IfcLabel(data);
            case 503: return new ::Ifc4::IfcLaborResource(data);
            case 504: return new ::Ifc4::IfcLaborResourceType(data);
            case 506: return new ::Ifc4::IfcLagTime(data);
            case 507: return new ::Ifc4::IfcLamp(data);
            case 508: return new ::Ifc4::IfcLampType(data);
            case 510: return new ::Ifc4::IfcLanguageId(data);
            case 513: return new ::Ifc4::IfcLengthMeasure(data);
            case 514: return new ::Ifc4::IfcLibraryInformation(data);
            case 515: return new ::Ifc4::IfcLibraryReference(data);
            case 518: return new ::Ifc4::IfcLightDistributionData(data);
            case 521: return new ::Ifc4::IfcLightFixture(data);
            case 522: return new ::Ifc4::IfcLightFixtureType(data);
            case 524: return new ::Ifc4::IfcLightIntensityDistribution(data);
            case 525: return new ::Ifc4::IfcLightSource(data);
            case 526: return new ::Ifc4::IfcLightSourceAmbient(data);
            case 527: return new ::Ifc4::IfcLightSourceDirectional(data);
            case 528: return new ::Ifc4::IfcLightSourceGoniometric(data);
            case 529: return new ::Ifc4::IfcLightSourcePositional(data);
            case 530: return new ::Ifc4::IfcLightSourceSpot(data);
            case 531: return new ::Ifc4::IfcLine(data);
            case 532: return new ::Ifc4::IfcLinearForceMeasure(data);
            case 533: return new ::Ifc4::IfcLinearMomentMeasure(data);
            case 534: return new ::Ifc4::IfcLinearStiffnessMeasure(data);
            case 535: return new ::Ifc4::IfcLinearVelocityMeasure(data);
            case 536: return new ::Ifc4::IfcLineIndex(data);
            case 538: return new ::Ifc4::IfcLocalPlacement(data);
            case 539: return new ::Ifc4::IfcLogical(data);
            case 541: return new ::Ifc4::IfcLoop(data);
            case 542: return new ::Ifc4::IfcLShapeProfileDef(data);
            case 543: return new ::Ifc4::IfcLuminousFluxMeasure(data);
            case 544: return new ::Ifc4::IfcLuminousIntensityDistributionMeasure(data);
            case 545: return new ::Ifc4::IfcLuminousIntensityMeasure(data);
            case 546: return new ::Ifc4::IfcMagneticFluxDensityMeasure(data);
            case 547: return new ::Ifc4::IfcMagneticFluxMeasure(data);
            case 548: return new ::Ifc4::IfcManifoldSolidBrep(data);
            case 549: return new ::Ifc4::IfcMapConversion(data);
            case 550: return new ::Ifc4::IfcMappedItem(data);
            case 551: return new ::Ifc4::IfcMassDensityMeasure(data);
            case 552: return new ::Ifc4::IfcMassFlowRateMeasure(data);
            case 553: return new ::Ifc4::IfcMassMeasure(data);
            case 554: return new ::Ifc4::IfcMassPerLengthMeasure(data);
            case 555: return new ::Ifc4::IfcMaterial(data);
            case 556: return new ::Ifc4::IfcMaterialClassificationRelationship(data);
            case 557: return new ::Ifc4::IfcMaterialConstituent(data);
            case 558: return new ::Ifc4::IfcMaterialConstituentSet(data);
            case 559: return new ::Ifc4::IfcMaterialDefinition(data);
            case 560: return new ::Ifc4::IfcMaterialDefinitionRepresentation(data);
            case 561: return new ::Ifc4::IfcMaterialLayer(data);
            case 562: return new ::Ifc4::IfcMaterialLayerSet(data);
            case 563: return new ::Ifc4::IfcMaterialLayerSetUsage(data);
            case 564: return new ::Ifc4::IfcMaterialLayerWithOffsets(data);
            case 565: return new ::Ifc4::IfcMaterialList(data);
            case 566: return new ::Ifc4::IfcMaterialProfile(data);
            case 567: return new ::Ifc4::IfcMaterialProfileSet(data);
            case 568: return new ::Ifc4::IfcMaterialProfileSetUsage(data);
            case 569: return new ::Ifc4::IfcMaterialProfileSetUsageTapering(data);
            case 570: return new ::Ifc4::IfcMaterialProfileWithOffsets(data);
            case 571: return new ::Ifc4::IfcMaterialProperties(data);
            case 572: return new ::Ifc4::IfcMaterialRelationship(data);
            case 574: return new ::Ifc4::IfcMaterialUsageDefinition(data);
            case 576: return new ::Ifc4::IfcMeasureWithUnit(data);
            case 577: return new ::Ifc4::IfcMechanicalFastener(data);
            case 578: return new ::Ifc4::IfcMechanicalFastenerType(data);
            case 580: return new ::Ifc4::IfcMedicalDevice(data);
            case 581: return new ::Ifc4::IfcMedicalDeviceType(data);
            case 583: return new ::Ifc4::IfcMember(data);
            case 584: return new ::Ifc4::IfcMemberStandardCase(data);
            case 585: return new ::Ifc4::IfcMemberType(data);
            case 587: return new ::Ifc4::IfcMetric(data);
            case 589: return new ::Ifc4::IfcMirroredProfileDef(data);
            case 590: return new ::Ifc4::IfcModulusOfElasticityMeasure(data);
            case 591: return new ::Ifc4::IfcModulusOfLinearSubgradeReactionMeasure(data);
            case 592: return new ::Ifc4::IfcModulusOfRotationalSubgradeReactionMeasure(data);
            case 594: return new ::Ifc4::IfcModulusOfSubgradeReactionMeasure(data);
            case 597: return new ::Ifc4::IfcMoistureDiffusivityMeasure(data);
            case 598: return new ::Ifc4::IfcMolecularWeightMeasure(data);
            case 599: return new ::Ifc4::IfcMomentOfInertiaMeasure(data);
            case 600: return new ::Ifc4::IfcMonetaryMeasure(data);
            case 601: return new ::Ifc4::IfcMonetaryUnit(data);
            case 602: return new ::Ifc4::IfcMonthInYearNumber(data);
            case 603: return new ::Ifc4::IfcMotorConnection(data);
            case 604: return new ::Ifc4::IfcMotorConnectionType(data);
            case 606: return new ::Ifc4::IfcNamedUnit(data);
            case 607: return new ::Ifc4::IfcNonNegativeLengthMeasure(data);
            case 608: return new ::Ifc4::IfcNormalisedRatioMeasure(data);
            case 610: return new ::Ifc4::IfcNumericMeasure(data);
            case 611: return new ::Ifc4::IfcObject(data);
            case 612: return new ::Ifc4::IfcObjectDefinition(data);
            case 613: return new ::Ifc4::IfcObjective(data);
            case 615: return new ::Ifc4::IfcObjectPlacement(data);
            case 618: return new ::Ifc4::IfcOccupant(data);
            case 620: return new ::Ifc4::IfcOffsetCurve2D(data);
            case 621: return new ::Ifc4::IfcOffsetCurve3D(data);
            case 622: return new ::Ifc4::IfcOpeningElement(data);
            case 624: return new ::Ifc4::IfcOpeningStandardCase(data);
            case 625: return new ::Ifc4::IfcOpenShell(data);
            case 626: return new ::Ifc4::IfcOrganization(data);
            case 627: return new ::Ifc4::IfcOrganizationRelationship(data);
            case 628: return new ::Ifc4::IfcOrientedEdge(data);
            case 629: return new ::Ifc4::IfcOuterBoundaryCurve(data);
            case 630: return new ::Ifc4::IfcOutlet(data);
            case 631: return new ::Ifc4::IfcOutletType(data);
            case 633: return new ::Ifc4::IfcOwnerHistory(data);
            case 634: return new ::Ifc4::IfcParameterizedProfileDef(data);
            case 635: return new ::Ifc4::IfcParameterValue(data);
            case 636: return new ::Ifc4::IfcPath(data);
            case 637: return new ::Ifc4::IfcPcurve(data);
            case 638: return new ::Ifc4::IfcPerformanceHistory(data);
            case 641: return new ::Ifc4::IfcPermeableCoveringProperties(data);
            case 642: return new ::Ifc4::IfcPermit(data);
            case 644: return new ::Ifc4::IfcPerson(data);
            case 645: return new ::Ifc4::IfcPersonAndOrganization(data);
            case 646: return new ::Ifc4::IfcPHMeasure(data);
            case 647: return new ::Ifc4::IfcPhysicalComplexQuantity(data);
            case 649: return new ::Ifc4::IfcPhysicalQuantity(data);
            case 650: return new ::Ifc4::IfcPhysicalSimpleQuantity(data);
            case 651: return new ::Ifc4::IfcPile(data);
            case 653: return new ::Ifc4::IfcPileType(data);
            case 655: return new ::Ifc4::IfcPipeFitting(data);
            case 656: return new ::Ifc4::IfcPipeFittingType(data);
            case 658: return new ::Ifc4::IfcPipeSegment(data);
            case 659: return new ::Ifc4::IfcPipeSegmentType(data);
            case 661: return new ::Ifc4::IfcPixelTexture(data);
            case 662: return new ::Ifc4::IfcPlacement(data);
            case 663: return new ::Ifc4::IfcPlanarBox(data);
            case 664: return new ::Ifc4::IfcPlanarExtent(data);
            case 665: return new ::Ifc4::IfcPlanarForceMeasure(data);
            case 666: return new ::Ifc4::IfcPlane(data);
            case 667: return new ::Ifc4::IfcPlaneAngleMeasure(data);
            case 668: return new ::Ifc4::IfcPlate(data);
            case 669: return new ::Ifc4::IfcPlateStandardCase(data);
            case 670: return new ::Ifc4::IfcPlateType(data);
            case 672: return new ::Ifc4::IfcPoint(data);
            case 673: return new ::Ifc4::IfcPointOnCurve(data);
            case 674: return new ::Ifc4::IfcPointOnSurface(data);
            case 676: return new ::Ifc4::IfcPolygonalBoundedHalfSpace(data);
            case 677: return new ::Ifc4::IfcPolyline(data);
            case 678: return new ::Ifc4::IfcPolyLoop(data);
            case 679: return new ::Ifc4::IfcPort(data);
            case 680: return new ::Ifc4::IfcPositiveInteger(data);
            case 681: return new ::Ifc4::IfcPositiveLengthMeasure(data);
            case 682: return new ::Ifc4::IfcPositivePlaneAngleMeasure(data);
            case 683: return new ::Ifc4::IfcPositiveRatioMeasure(data);
            case 684: return new ::Ifc4::IfcPostalAddress(data);
            case 685: return new ::Ifc4::IfcPowerMeasure(data);
            case 686: return new ::Ifc4::IfcPreDefinedColour(data);
            case 687: return new ::Ifc4::IfcPreDefinedCurveFont(data);
            case 688: return new ::Ifc4::IfcPreDefinedItem(data);
            case 689: return new ::Ifc4::IfcPreDefinedProperties(data);
            case 690: return new ::Ifc4::IfcPreDefinedPropertySet(data);
            case 691: return new ::Ifc4::IfcPreDefinedTextFont(data);
            case 692: return new ::Ifc4::IfcPresentableText(data);
            case 693: return new ::Ifc4::IfcPresentationItem(data);
            case 694: return new ::Ifc4::IfcPresentationLayerAssignment(data);
            case 695: return new ::Ifc4::IfcPresentationLayerWithStyle(data);
            case 696: return new ::Ifc4::IfcPresentationStyle(data);
            case 697: return new ::Ifc4::IfcPresentationStyleAssignment(data);
            case 699: return new ::Ifc4::IfcPressureMeasure(data);
            case 700: return new ::Ifc4::IfcProcedure(data);
            case 701: return new ::Ifc4::IfcProcedureType(data);
            case 703: return new ::Ifc4::IfcProcess(data);
            case 705: return new ::Ifc4::IfcProduct(data);
            case 706: return new ::Ifc4::IfcProductDefinitionShape(data);
            case 707: return new ::Ifc4::IfcProductRepresentation(data);
            case 710: return new ::Ifc4::IfcProfileDef(data);
            case 711: return new ::Ifc4::IfcProfileProperties(data);
            case 713: return new ::Ifc4::IfcProject(data);
            case 714: return new ::Ifc4::IfcProjectedCRS(data);
            case 716: return new ::Ifc4::IfcProjectionElement(data);
            case 718: return new ::Ifc4::IfcProjectLibrary(data);
            case 719: return new ::Ifc4::IfcProjectOrder(data);
            case 721: return new ::Ifc4::IfcProperty(data);
            case 722: return new ::Ifc4::IfcPropertyAbstraction(data);
            case 723: return new ::Ifc4::IfcPropertyBoundedValue(data);
            case 724: return new ::Ifc4::IfcPropertyDefinition(data);
            case 725: return new ::Ifc4::IfcPropertyDependencyRelationship(data);
            case 726: return new ::Ifc4::IfcPropertyEnumeratedValue(data);
            case 727: return new ::Ifc4::IfcPropertyEnumeration(data);
            case 728: return new ::Ifc4::IfcPropertyListValue(data);
            case 729: return new ::Ifc4::IfcPropertyReferenceValue(data);
            case 730: return new ::Ifc4::IfcPropertySet(data);
            case 731: return new ::Ifc4::IfcPropertySetDefinition(data);
            case 733: return new ::Ifc4::IfcPropertySetDefinitionSet(data);
            case 734: return new ::Ifc4::IfcPropertySetTemplate(data);
            case 736: return new ::Ifc4::IfcPropertySingleValue(data);
            case 737: return new ::Ifc4::IfcPropertyTableValue(data);
            case 738: return new ::Ifc4::IfcPropertyTemplate(data);
            case 739: return new ::Ifc4::IfcPropertyTemplateDefinition(data);
            case 740: return new ::Ifc4::IfcProtectiveDevice(data);
            case 741: return new ::Ifc4::IfcProtectiveDeviceTrippingUnit(data);
            case 742: return new ::Ifc4::IfcProtectiveDeviceTrippingUnitType(data);
            case 744: return new ::Ifc4::IfcProtectiveDeviceType(data);
            case 746: return new ::Ifc4::IfcProxy(data);
            case 747: return new ::Ifc4::IfcPump(data);
            case 748: return new ::Ifc4::IfcPumpType(data);
            case 750: return new ::Ifc4::IfcQuantityArea(data);
            case 751: return new ::Ifc4::IfcQuantityCount(data);
            case 752: return new ::Ifc4::IfcQuantityLength(data);
            case 753: return new ::Ifc4::IfcQuantitySet(data);
            case 754: return new ::Ifc4::IfcQuantityTime(data);
            case 755: return new ::Ifc4::IfcQuantityVolume(data);
            case 756: return new ::Ifc4::IfcQuantityWeight(data);
            case 757: return new ::Ifc4::IfcRadioActivityMeasure(data);
            case 758: return new ::Ifc4::IfcRailing(data);
            case 759: return new ::Ifc4::IfcRailingType(data);
            case 761: return new ::Ifc4::IfcRamp(data);
            case 762: return new ::Ifc4::IfcRampFlight(data);
            case 763: return new ::Ifc4::IfcRampFlightType(data);
            case 765: return new ::Ifc4::IfcRampType(data);
            case 767: return new ::Ifc4::IfcRatioMeasure(data);
            case 768: return new ::Ifc4::IfcRationalBSplineCurveWithKnots(data);
            case 769: return new ::Ifc4::IfcRationalBSplineSurfaceWithKnots(data);
            case 770: return new ::Ifc4::IfcReal(data);
            case 771: return new ::Ifc4::IfcRectangleHollowProfileDef(data);
            case 772: return new ::Ifc4::IfcRectangleProfileDef(data);
            case 773: return new ::Ifc4::IfcRectangularPyramid(data);
            case 774: return new ::Ifc4::IfcRectangularTrimmedSurface(data);
            case 775: return new ::Ifc4::IfcRecurrencePattern(data);
            case 777: return new ::Ifc4::IfcReference(data);
            case 779: return new ::Ifc4::IfcRegularTimeSeries(data);
            case 780: return new ::Ifc4::IfcReinforcementBarProperties(data);
            case 781: return new ::Ifc4::IfcReinforcementDefinitionProperties(data);
            case 782: return new ::Ifc4::IfcReinforcingBar(data);
            case 785: return new ::Ifc4::IfcReinforcingBarType(data);
            case 787: return new ::Ifc4::IfcReinforcingElement(data);
            case 788: return new ::Ifc4::IfcReinforcingElementType(data);
            case 789: return new ::Ifc4::IfcReinforcingMesh(data);
            case 790: return new ::Ifc4::IfcReinforcingMeshType(data);
            case 792: return new ::Ifc4::IfcRelAggregates(data);
            case 793: return new ::Ifc4::IfcRelAssigns(data);
            case 794: return new ::Ifc4::IfcRelAssignsToActor(data);
            case 795: return new ::Ifc4::IfcRelAssignsToControl(data);
            case 796: return new ::Ifc4::IfcRelAssignsToGroup(data);
            case 797: return new ::Ifc4::IfcRelAssignsToGroupByFactor(data);
            case 798: return new ::Ifc4::IfcRelAssignsToProcess(data);
            case 799: return new ::Ifc4::IfcRelAssignsToProduct(data);
            case 800: return new ::Ifc4::IfcRelAssignsToResource(data);
            case 801: return new ::Ifc4::IfcRelAssociates(data);
            case 802: return new ::Ifc4::IfcRelAssociatesApproval(data);
            case 803: return new ::Ifc4::IfcRelAssociatesClassification(data);
            case 804: return new ::Ifc4::IfcRelAssociatesConstraint(data);
            case 805: return new ::Ifc4::IfcRelAssociatesDocument(data);
            case 806: return new ::Ifc4::IfcRelAssociatesLibrary(data);
            case 807: return new ::Ifc4::IfcRelAssociatesMaterial(data);
            case 808: return new ::Ifc4::IfcRelationship(data);
            case 809: return new ::Ifc4::IfcRelConnects(data);
            case 810: return new ::Ifc4::IfcRelConnectsElements(data);
            case 811: return new ::Ifc4::IfcRelConnectsPathElements(data);
            case 812: return new ::Ifc4::IfcRelConnectsPorts(data);
            case 813: return new ::Ifc4::IfcRelConnectsPortToElement(data);
            case 814: return new ::Ifc4::IfcRelConnectsStructuralActivity(data);
            case 815: return new ::Ifc4::IfcRelConnectsStructuralMember(data);
            case 816: return new ::Ifc4::IfcRelConnectsWithEccentricity(data);
            case 817: return new ::Ifc4::IfcRelConnectsWithRealizingElements(data);
            case 818: return new ::Ifc4::IfcRelContainedInSpatialStructure(data);
            case 819: return new ::Ifc4::IfcRelCoversBldgElements(data);
            case 820: return new ::Ifc4::IfcRelCoversSpaces(data);
            case 821: return new ::Ifc4::IfcRelDeclares(data);
            case 822: return new ::Ifc4::IfcRelDecomposes(data);
            case 823: return new ::Ifc4::IfcRelDefines(data);
            case 824: return new ::Ifc4::IfcRelDefinesByObject(data);
            case 825: return new ::Ifc4::IfcRelDefinesByProperties(data);
            case 826: return new ::Ifc4::IfcRelDefinesByTemplate(data);
            case 827: return new ::Ifc4::IfcRelDefinesByType(data);
            case 828: return new ::Ifc4::IfcRelFillsElement(data);
            case 829: return new ::Ifc4::IfcRelFlowControlElements(data);
            case 830: return new ::Ifc4::IfcRelInterferesElements(data);
            case 831: return new ::Ifc4::IfcRelNests(data);
            case 832: return new ::Ifc4::IfcRelProjectsElement(data);
            case 833: return new ::Ifc4::IfcRelReferencedInSpatialStructure(data);
            case 834: return new ::Ifc4::IfcRelSequence(data);
            case 835: return new ::Ifc4::IfcRelServicesBuildings(data);
            case 836: return new ::Ifc4::IfcRelSpaceBoundary(data);
            case 837: return new ::Ifc4::IfcRelSpaceBoundary1stLevel(data);
            case 838: return new ::Ifc4::IfcRelSpaceBoundary2ndLevel(data);
            case 839: return new ::Ifc4::IfcRelVoidsElement(data);
            case 840: return new ::Ifc4::IfcReparametrisedCompositeCurveSegment(data);
            case 841: return new ::Ifc4::IfcRepresentation(data);
            case 842: return new ::Ifc4::IfcRepresentationContext(data);
            case 843: return new ::Ifc4::IfcRepresentationItem(data);
            case 844: return new ::Ifc4::IfcRepresentationMap(data);
            case 845: return new ::Ifc4::IfcResource(data);
            case 846: return new ::Ifc4::IfcResourceApprovalRelationship(data);
            case 847: return new ::Ifc4::IfcResourceConstraintRelationship(data);
            case 848: return new ::Ifc4::IfcResourceLevelRelationship(data);
            case 851: return new ::Ifc4::IfcResourceTime(data);
            case 852: return new ::Ifc4::IfcRevolvedAreaSolid(data);
            case 853: return new ::Ifc4::IfcRevolvedAreaSolidTapered(data);
            case 854: return new ::Ifc4::IfcRightCircularCone(data);
            case 855: return new ::Ifc4::IfcRightCircularCylinder(data);
            case 857: return new ::Ifc4::IfcRoof(data);
            case 858: return new ::Ifc4::IfcRoofType(data);
            case 860: return new ::Ifc4::IfcRoot(data);
            case 861: return new ::Ifc4::IfcRotationalFrequencyMeasure(data);
            case 862: return new ::Ifc4::IfcRotationalMassMeasure(data);
            case 863: return new ::Ifc4::IfcRotationalStiffnessMeasure(data);
            case 865: return new ::Ifc4::IfcRoundedRectangleProfileDef(data);
            case 866: return new ::Ifc4::IfcSanitaryTerminal(data);
            case 867: return new ::Ifc4::IfcSanitaryTerminalType(data);
            case 869: return new ::Ifc4::IfcSchedulingTime(data);
            case 870: return new ::Ifc4::IfcSectionalAreaIntegralMeasure(data);
            case 871: return new ::Ifc4::IfcSectionedSpine(data);
            case 872: return new ::Ifc4::IfcSectionModulusMeasure(data);
            case 873: return new ::Ifc4::IfcSectionProperties(data);
            case 874: return new ::Ifc4::IfcSectionReinforcementProperties(data);
            case 877: return new ::Ifc4::IfcSensor(data);
            case 878: return new ::Ifc4::IfcSensorType(data);
            case 881: return new ::Ifc4::IfcShadingDevice(data);
            case 882: return new ::Ifc4::IfcShadingDeviceType(data);
            case 884: return new ::Ifc4::IfcShapeAspect(data);
            case 885: return new ::Ifc4::IfcShapeModel(data);
            case 886: return new ::Ifc4::IfcShapeRepresentation(data);
            case 887: return new ::Ifc4::IfcShearModulusMeasure(data);
            case 889: return new ::Ifc4::IfcShellBasedSurfaceModel(data);
            case 890: return new ::Ifc4::IfcSimpleProperty(data);
            case 891: return new ::Ifc4::IfcSimplePropertyTemplate(data);
            case 895: return new ::Ifc4::IfcSite(data);
            case 896: return new ::Ifc4::IfcSIUnit(data);
            case 899: return new ::Ifc4::IfcSlab(data);
            case 900: return new ::Ifc4::IfcSlabElementedCase(data);
            case 901: return new ::Ifc4::IfcSlabStandardCase(data);
            case 902: return new ::Ifc4::IfcSlabType(data);
            case 904: return new ::Ifc4::IfcSlippageConnectionCondition(data);
            case 905: return new ::Ifc4::IfcSolarDevice(data);
            case 906: return new ::Ifc4::IfcSolarDeviceType(data);
            case 908: return new ::Ifc4::IfcSolidAngleMeasure(data);
            case 909: return new ::Ifc4::IfcSolidModel(data);
            case 911: return new ::Ifc4::IfcSoundPowerLevelMeasure(data);
            case 912: return new ::Ifc4::IfcSoundPowerMeasure(data);
            case 913: return new ::Ifc4::IfcSoundPressureLevelMeasure(data);
            case 914: return new ::Ifc4::IfcSoundPressureMeasure(data);
            case 915: return new ::Ifc4::IfcSpace(data);
            case 917: return new ::Ifc4::IfcSpaceHeater(data);
            case 918: return new ::Ifc4::IfcSpaceHeaterType(data);
            case 920: return new ::Ifc4::IfcSpaceType(data);
            case 922: return new ::Ifc4::IfcSpatialElement(data);
            case 923: return new ::Ifc4::IfcSpatialElementType(data);
            case 924: return new ::Ifc4::IfcSpatialStructureElement(data);
            case 925: return new ::Ifc4::IfcSpatialStructureElementType(data);
            case 926: return new ::Ifc4::IfcSpatialZone(data);
            case 927: return new ::Ifc4::IfcSpatialZoneType(data);
            case 929: return new ::Ifc4::IfcSpecificHeatCapacityMeasure(data);
            case 930: return new ::Ifc4::IfcSpecularExponent(data);
            case 932: return new ::Ifc4::IfcSpecularRoughness(data);
            case 933: return new ::Ifc4::IfcSphere(data);
            case 934: return new ::Ifc4::IfcStackTerminal(data);
            case 935: return new ::Ifc4::IfcStackTerminalType(data);
            case 937: return new ::Ifc4::IfcStair(data);
            case 938: return new ::Ifc4::IfcStairFlight(data);
            case 939: return new ::Ifc4::IfcStairFlightType(data);
            case 941: return new ::Ifc4::IfcStairType(data);
            case 944: return new ::Ifc4::IfcStrippedOptional(data);
            case 945: return new ::Ifc4::IfcStructuralAction(data);
            case 946: return new ::Ifc4::IfcStructuralActivity(data);
            case 948: return new ::Ifc4::IfcStructuralAnalysisModel(data);
            case 949: return new ::Ifc4::IfcStructuralConnection(data);
            case 950: return new ::Ifc4::IfcStructuralConnectionCondition(data);
            case 951: return new ::Ifc4::IfcStructuralCurveAction(data);
            case 953: return new ::Ifc4::IfcStructuralCurveConnection(data);
            case 954: return new ::Ifc4::IfcStructuralCurveMember(data);
            case 956: return new ::Ifc4::IfcStructuralCurveMemberVarying(data);
            case 957: return new ::Ifc4::IfcStructuralCurveReaction(data);
            case 958: return new ::Ifc4::IfcStructuralItem(data);
            case 959: return new ::Ifc4::IfcStructuralLinearAction(data);
            case 960: return new ::Ifc4::IfcStructuralLoad(data);
            case 961: return new ::Ifc4::IfcStructuralLoadCase(data);
            case 962: return new ::Ifc4::IfcStructuralLoadConfiguration(data);
            case 963: return new ::Ifc4::IfcStructuralLoadGroup(data);
            case 964: return new ::Ifc4::IfcStructuralLoadLinearForce(data);
            case 965: return new ::Ifc4::IfcStructuralLoadOrResult(data);
            case 966: return new ::Ifc4::IfcStructuralLoadPlanarForce(data);
            case 967: return new ::Ifc4::IfcStructuralLoadSingleDisplacement(data);
            case 968: return new ::Ifc4::IfcStructuralLoadSingleDisplacementDistortion(data);
            case 969: return new ::Ifc4::IfcStructuralLoadSingleForce(data);
            case 970: return new ::Ifc4::IfcStructuralLoadSingleForceWarping(data);
            case 971: return new ::Ifc4::IfcStructuralLoadStatic(data);
            case 972: return new ::Ifc4::IfcStructuralLoadTemperature(data);
            case 973: return new ::Ifc4::IfcStructuralMember(data);
            case 974: return new ::Ifc4::IfcStructuralPlanarAction(data);
            case 975: return new ::Ifc4::IfcStructuralPointAction(data);
            case 976: return new ::Ifc4::IfcStructuralPointConnection(data);
            case 977: return new ::Ifc4::IfcStructuralPointReaction(data);
            case 978: return new ::Ifc4::IfcStructuralReaction(data);
            case 979: return new ::Ifc4::IfcStructuralResultGroup(data);
            case 980: return new ::Ifc4::IfcStructuralSurfaceAction(data);
            case 982: return new ::Ifc4::IfcStructuralSurfaceConnection(data);
            case 983: return new ::Ifc4::IfcStructuralSurfaceMember(data);
            case 985: return new ::Ifc4::IfcStructuralSurfaceMemberVarying(data);
            case 986: return new ::Ifc4::IfcStructuralSurfaceReaction(data);
            case 988: return new ::Ifc4::IfcStyledItem(data);
            case 989: return new ::Ifc4::IfcStyledRepresentation(data);
            case 990: return new ::Ifc4::IfcStyleModel(data);
            case 991: return new ::Ifc4::IfcSubContractResource(data);
            case 992: return new ::Ifc4::IfcSubContractResourceType(data);
            case 994: return new ::Ifc4::IfcSubedge(data);
            case 995: return new ::Ifc4::IfcSurface(data);
            case 996: return new ::Ifc4::IfcSurfaceCurveSweptAreaSolid(data);
            case 997: return new ::Ifc4::IfcSurfaceFeature(data);
            case 999: return new ::Ifc4::IfcSurfaceOfLinearExtrusion(data);
            case 1000: return new ::Ifc4::IfcSurfaceOfRevolution(data);
            case 1002: return new ::Ifc4::IfcSurfaceReinforcementArea(data);
            case 1004: return new ::Ifc4::IfcSurfaceStyle(data);
            case 1006: return new ::Ifc4::IfcSurfaceStyleLighting(data);
            case 1007: return new ::Ifc4::IfcSurfaceStyleRefraction(data);
            case 1008: return new ::Ifc4::IfcSurfaceStyleRendering(data);
            case 1009: return new ::Ifc4::IfcSurfaceStyleShading(data);
            case 1010: return new ::Ifc4::IfcSurfaceStyleWithTextures(data);
            case 1011: return new ::Ifc4::IfcSurfaceTexture(data);
            case 1012: return new ::Ifc4::IfcSweptAreaSolid(data);
            case 1013: return new ::Ifc4::IfcSweptDiskSolid(data);
            case 1014: return new ::Ifc4::IfcSweptDiskSolidPolygonal(data);
            case 1015: return new ::Ifc4::IfcSweptSurface(data);
            case 1016: return new ::Ifc4::IfcSwitchingDevice(data);
            case 1017: return new ::Ifc4::IfcSwitchingDeviceType(data);
            case 1019: return new ::Ifc4::IfcSystem(data);
            case 1020: return new ::Ifc4::IfcSystemFurnitureElement(data);
            case 1021: return new ::Ifc4::IfcSystemFurnitureElementType(data);
            case 1023: return new ::Ifc4::IfcTable(data);
            case 1024: return new ::Ifc4::IfcTableColumn(data);
            case 1025: return new ::Ifc4::IfcTableRow(data);
            case 1026: return new ::Ifc4::IfcTank(data);
            case 1027: return new ::Ifc4::IfcTankType(data);
            case 1029: return new ::Ifc4::IfcTask(data);
            case 1031: return new ::Ifc4::IfcTaskTime(data);
            case 1032: return new ::Ifc4::IfcTaskTimeRecurring(data);
            case 1033: return new ::Ifc4::IfcTaskType(data);
            case 1035: return new ::Ifc4::IfcTelecomAddress(data);
            case 1036: return new ::Ifc4::IfcTemperatureGradientMeasure(data);
            case 1037: return new ::Ifc4::IfcTemperatureRateOfChangeMeasure(data);
            case 1038: return new ::Ifc4::IfcTendon(data);
            case 1039: return new ::Ifc4::IfcTendonAnchor(data);
            case 1040: return new ::Ifc4::IfcTendonAnchorType(data);
            case 1042: return new ::Ifc4::IfcTendonType(data);
            case 1044: return new ::Ifc4::IfcTessellatedFaceSet(data);
            case 1045: return new ::Ifc4::IfcTessellatedItem(data);
            case 1046: return new ::Ifc4::IfcText(data);
            case 1047: return new ::Ifc4::IfcTextAlignment(data);
            case 1048: return new ::Ifc4::IfcTextDecoration(data);
            case 1049: return new ::Ifc4::IfcTextFontName(data);
            case 1051: return new ::Ifc4::IfcTextLiteral(data);
            case 1052: return new ::Ifc4::IfcTextLiteralWithExtent(data);
            case 1054: return new ::Ifc4::IfcTextStyle(data);
            case 1055: return new ::Ifc4::IfcTextStyleFontModel(data);
            case 1056: return new ::Ifc4::IfcTextStyleForDefinedFont(data);
            case 1057: return new ::Ifc4::IfcTextStyleTextModel(data);
            case 1058: return new ::Ifc4::IfcTextTransformation(data);
            case 1059: return new ::Ifc4::IfcTextureCoordinate(data);
            case 1060: return new ::Ifc4::IfcTextureCoordinateGenerator(data);
            case 1061: return new ::Ifc4::IfcTextureMap(data);
            case 1062: return new ::Ifc4::IfcTextureVertex(data);
            case 1063: return new ::Ifc4::IfcTextureVertexList(data);
            case 1064: return new ::Ifc4::IfcThermalAdmittanceMeasure(data);
            case 1065: return new ::Ifc4::IfcThermalConductivityMeasure(data);
            case 1066: return new ::Ifc4::IfcThermalExpansionCoefficientMeasure(data);
            case 1067: return new ::Ifc4::IfcThermalResistanceMeasure(data);
            case 1068: return new ::Ifc4::IfcThermalTransmittanceMeasure(data);
            case 1069: return new ::Ifc4::IfcThermodynamicTemperatureMeasure(data);
            case 1070: return new ::Ifc4::IfcTime(data);
            case 1071: return new ::Ifc4::IfcTimeMeasure(data);
            case 1073: return new ::Ifc4::IfcTimePeriod(data);
            case 1074: return new ::Ifc4::IfcTimeSeries(data);
            case 1076: return new ::Ifc4::IfcTimeSeriesValue(data);
            case 1077: return new ::Ifc4::IfcTimeStamp(data);
            case 1078: return new ::Ifc4::IfcTopologicalRepresentationItem(data);
            case 1079: return new ::Ifc4::IfcTopologyRepresentation(data);
            case 1080: return new ::Ifc4::IfcTorqueMeasure(data);
            case 1081: return new ::Ifc4::IfcTransformer(data);
            case 1082: return new ::Ifc4::IfcTransformerType(data);
            case 1086: return new ::Ifc4::IfcTransportElement(data);
            case 1087: return new ::Ifc4::IfcTransportElementType(data);
            case 1089: return new ::Ifc4::IfcTrapeziumProfileDef(data);
            case 1090: return new ::Ifc4::IfcTriangulatedFaceSet(data);
            case 1091: return new ::Ifc4::IfcTrimmedCurve(data);
            case 1094: return new ::Ifc4::IfcTShapeProfileDef(data);
            case 1095: return new ::Ifc4::IfcTubeBundle(data);
            case 1096: return new ::Ifc4::IfcTubeBundleType(data);
            case 1098: return new ::Ifc4::IfcTypeObject(data);
            case 1099: return new ::Ifc4::IfcTypeProcess(data);
            case 1100: return new ::Ifc4::IfcTypeProduct(data);
            case 1101: return new ::Ifc4::IfcTypeResource(data);
            case 1103: return new ::Ifc4::IfcUnitaryControlElement(data);
            case 1104: return new ::Ifc4::IfcUnitaryControlElementType(data);
            case 1106: return new ::Ifc4::IfcUnitaryEquipment(data);
            case 1107: return new ::Ifc4::IfcUnitaryEquipmentType(data);
            case 1109: return new ::Ifc4::IfcUnitAssignment(data);
            case 1111: return new ::Ifc4::IfcURIReference(data);
            case 1112: return new ::Ifc4::IfcUShapeProfileDef(data);
            case 1114: return new ::Ifc4::IfcValve(data);
            case 1115: return new ::Ifc4::IfcValveType(data);
            case 1117: return new ::Ifc4::IfcVaporPermeabilityMeasure(data);
            case 1118: return new ::Ifc4::IfcVector(data);
            case 1120: return new ::Ifc4::IfcVertex(data);
            case 1121: return new ::Ifc4::IfcVertexLoop(data);
            case 1122: return new ::Ifc4::IfcVertexPoint(data);
            case 1123: return new ::Ifc4::IfcVibrationIsolator(data);
            case 1124: return new ::Ifc4::IfcVibrationIsolatorType(data);
            case 1126: return new ::Ifc4::IfcVirtualElement(data);
            case 1127: return new ::Ifc4::IfcVirtualGridIntersection(data);
            case 1128: return new ::Ifc4::IfcVoidingFeature(data);
            case 1130: return new ::Ifc4::IfcVolumeMeasure(data);
            case 1131: return new ::Ifc4::IfcVolumetricFlowRateMeasure(data);
            case 1132: return new ::Ifc4::IfcWall(data);
            case 1133: return new ::Ifc4::IfcWallElementedCase(data);
            case 1134: return new ::Ifc4::IfcWallStandardCase(data);
            case 1135: return new ::Ifc4::IfcWallType(data);
            case 1137: return new ::Ifc4::IfcWarpingConstantMeasure(data);
            case 1138: return new ::Ifc4::IfcWarpingMomentMeasure(data);
            case 1140: return new ::Ifc4::IfcWasteTerminal(data);
            case 1141: return new ::Ifc4::IfcWasteTerminalType(data);
            case 1143: return new ::Ifc4::IfcWindow(data);
            case 1144: return new ::Ifc4::IfcWindowLiningProperties(data);
            case 1147: return new ::Ifc4::IfcWindowPanelProperties(data);
            case 1148: return new ::Ifc4::IfcWindowStandardCase(data);
            case 1149: return new ::Ifc4::IfcWindowStyle(data);
            case 1152: return new ::Ifc4::IfcWindowType(data);
            case 1155: return new ::Ifc4::IfcWorkCalendar(data);
            case 1157: return new ::Ifc4::IfcWorkControl(data);
            case 1158: return new ::Ifc4::IfcWorkPlan(data);
            case 1160: return new ::Ifc4::IfcWorkSchedule(data);
            case 1162: return new ::Ifc4::IfcWorkTime(data);
            case 1163: return new ::Ifc4::IfcZone(data);
            case 1164: return new ::Ifc4::IfcZShapeProfileDef(data);
            default: throw IfcParse::IfcException(data->type()->name() + " cannot be instantiated");
        }

    }
};


#ifdef _MSC_VER
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC4_populate_schema() {
    IFC4_IfcAbsorbedDoseMeasure_type = new type_declaration("IfcAbsorbedDoseMeasure", 0, new simple_type(simple_type::real_type));
    IFC4_IfcAccelerationMeasure_type = new type_declaration("IfcAccelerationMeasure", 1, new simple_type(simple_type::real_type));
    IFC4_IfcAmountOfSubstanceMeasure_type = new type_declaration("IfcAmountOfSubstanceMeasure", 29, new simple_type(simple_type::real_type));
    IFC4_IfcAngularVelocityMeasure_type = new type_declaration("IfcAngularVelocityMeasure", 32, new simple_type(simple_type::real_type));
    IFC4_IfcArcIndex_type = new type_declaration("IfcArcIndex", 43, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcPositiveInteger_type)));
    IFC4_IfcAreaDensityMeasure_type = new type_declaration("IfcAreaDensityMeasure", 44, new simple_type(simple_type::real_type));
    IFC4_IfcAreaMeasure_type = new type_declaration("IfcAreaMeasure", 45, new simple_type(simple_type::real_type));
    IFC4_IfcBinary_type = new type_declaration("IfcBinary", 63, new simple_type(simple_type::binary_type));
    IFC4_IfcBoolean_type = new type_declaration("IfcBoolean", 69, new simple_type(simple_type::boolean_type));
    IFC4_IfcCardinalPointReference_type = new type_declaration("IfcCardinalPointReference", 118, new simple_type(simple_type::integer_type));
    IFC4_IfcComplexNumber_type = new type_declaration("IfcComplexNumber", 161, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IFC4_IfcCompoundPlaneAngleMeasure_type = new type_declaration("IfcCompoundPlaneAngleMeasure", 169, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
    IFC4_IfcContextDependentMeasure_type = new type_declaration("IfcContextDependentMeasure", 199, new simple_type(simple_type::real_type));
    IFC4_IfcCountMeasure_type = new type_declaration("IfcCountMeasure", 221, new simple_type(simple_type::number_type));
    IFC4_IfcCurvatureMeasure_type = new type_declaration("IfcCurvatureMeasure", 236, new simple_type(simple_type::real_type));
    IFC4_IfcDate_type = new type_declaration("IfcDate", 254, new simple_type(simple_type::string_type));
    IFC4_IfcDateTime_type = new type_declaration("IfcDateTime", 255, new simple_type(simple_type::string_type));
    IFC4_IfcDayInMonthNumber_type = new type_declaration("IfcDayInMonthNumber", 256, new simple_type(simple_type::integer_type));
    IFC4_IfcDayInWeekNumber_type = new type_declaration("IfcDayInWeekNumber", 257, new simple_type(simple_type::integer_type));
    IFC4_IfcDescriptiveMeasure_type = new type_declaration("IfcDescriptiveMeasure", 264, new simple_type(simple_type::string_type));
    IFC4_IfcDimensionCount_type = new type_declaration("IfcDimensionCount", 266, new simple_type(simple_type::integer_type));
    IFC4_IfcDoseEquivalentMeasure_type = new type_declaration("IfcDoseEquivalentMeasure", 304, new simple_type(simple_type::real_type));
    IFC4_IfcDuration_type = new type_declaration("IfcDuration", 316, new simple_type(simple_type::string_type));
    IFC4_IfcDynamicViscosityMeasure_type = new type_declaration("IfcDynamicViscosityMeasure", 317, new simple_type(simple_type::real_type));
    IFC4_IfcElectricCapacitanceMeasure_type = new type_declaration("IfcElectricCapacitanceMeasure", 324, new simple_type(simple_type::real_type));
    IFC4_IfcElectricChargeMeasure_type = new type_declaration("IfcElectricChargeMeasure", 325, new simple_type(simple_type::real_type));
    IFC4_IfcElectricConductanceMeasure_type = new type_declaration("IfcElectricConductanceMeasure", 326, new simple_type(simple_type::real_type));
    IFC4_IfcElectricCurrentMeasure_type = new type_declaration("IfcElectricCurrentMeasure", 327, new simple_type(simple_type::real_type));
    IFC4_IfcElectricResistanceMeasure_type = new type_declaration("IfcElectricResistanceMeasure", 340, new simple_type(simple_type::real_type));
    IFC4_IfcElectricVoltageMeasure_type = new type_declaration("IfcElectricVoltageMeasure", 344, new simple_type(simple_type::real_type));
    IFC4_IfcEnergyMeasure_type = new type_declaration("IfcEnergyMeasure", 359, new simple_type(simple_type::real_type));
    IFC4_IfcFontStyle_type = new type_declaration("IfcFontStyle", 435, new simple_type(simple_type::string_type));
    IFC4_IfcFontVariant_type = new type_declaration("IfcFontVariant", 436, new simple_type(simple_type::string_type));
    IFC4_IfcFontWeight_type = new type_declaration("IfcFontWeight", 437, new simple_type(simple_type::string_type));
    IFC4_IfcForceMeasure_type = new type_declaration("IfcForceMeasure", 441, new simple_type(simple_type::real_type));
    IFC4_IfcFrequencyMeasure_type = new type_declaration("IfcFrequencyMeasure", 442, new simple_type(simple_type::real_type));
    IFC4_IfcGloballyUniqueId_type = new type_declaration("IfcGloballyUniqueId", 458, new simple_type(simple_type::string_type));
    IFC4_IfcHeatFluxDensityMeasure_type = new type_declaration("IfcHeatFluxDensityMeasure", 471, new simple_type(simple_type::real_type));
    IFC4_IfcHeatingValueMeasure_type = new type_declaration("IfcHeatingValueMeasure", 472, new simple_type(simple_type::real_type));
    IFC4_IfcIdentifier_type = new type_declaration("IfcIdentifier", 476, new simple_type(simple_type::string_type));
    IFC4_IfcIlluminanceMeasure_type = new type_declaration("IfcIlluminanceMeasure", 477, new simple_type(simple_type::real_type));
    IFC4_IfcInductanceMeasure_type = new type_declaration("IfcInductanceMeasure", 483, new simple_type(simple_type::real_type));
    IFC4_IfcInteger_type = new type_declaration("IfcInteger", 484, new simple_type(simple_type::integer_type));
    IFC4_IfcIntegerCountRateMeasure_type = new type_declaration("IfcIntegerCountRateMeasure", 485, new simple_type(simple_type::integer_type));
    IFC4_IfcIonConcentrationMeasure_type = new type_declaration("IfcIonConcentrationMeasure", 492, new simple_type(simple_type::real_type));
    IFC4_IfcIsothermalMoistureCapacityMeasure_type = new type_declaration("IfcIsothermalMoistureCapacityMeasure", 496, new simple_type(simple_type::real_type));
    IFC4_IfcKinematicViscosityMeasure_type = new type_declaration("IfcKinematicViscosityMeasure", 500, new simple_type(simple_type::real_type));
    IFC4_IfcLabel_type = new type_declaration("IfcLabel", 502, new simple_type(simple_type::string_type));
    IFC4_IfcLanguageId_type = new type_declaration("IfcLanguageId", 510, new named_type(IFC4_IfcIdentifier_type));
    IFC4_IfcLengthMeasure_type = new type_declaration("IfcLengthMeasure", 513, new simple_type(simple_type::real_type));
    IFC4_IfcLineIndex_type = new type_declaration("IfcLineIndex", 536, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcPositiveInteger_type)));
    IFC4_IfcLinearForceMeasure_type = new type_declaration("IfcLinearForceMeasure", 532, new simple_type(simple_type::real_type));
    IFC4_IfcLinearMomentMeasure_type = new type_declaration("IfcLinearMomentMeasure", 533, new simple_type(simple_type::real_type));
    IFC4_IfcLinearStiffnessMeasure_type = new type_declaration("IfcLinearStiffnessMeasure", 534, new simple_type(simple_type::real_type));
    IFC4_IfcLinearVelocityMeasure_type = new type_declaration("IfcLinearVelocityMeasure", 535, new simple_type(simple_type::real_type));
    IFC4_IfcLogical_type = new type_declaration("IfcLogical", 539, new simple_type(simple_type::logical_type));
    IFC4_IfcLuminousFluxMeasure_type = new type_declaration("IfcLuminousFluxMeasure", 543, new simple_type(simple_type::real_type));
    IFC4_IfcLuminousIntensityDistributionMeasure_type = new type_declaration("IfcLuminousIntensityDistributionMeasure", 544, new simple_type(simple_type::real_type));
    IFC4_IfcLuminousIntensityMeasure_type = new type_declaration("IfcLuminousIntensityMeasure", 545, new simple_type(simple_type::real_type));
    IFC4_IfcMagneticFluxDensityMeasure_type = new type_declaration("IfcMagneticFluxDensityMeasure", 546, new simple_type(simple_type::real_type));
    IFC4_IfcMagneticFluxMeasure_type = new type_declaration("IfcMagneticFluxMeasure", 547, new simple_type(simple_type::real_type));
    IFC4_IfcMassDensityMeasure_type = new type_declaration("IfcMassDensityMeasure", 551, new simple_type(simple_type::real_type));
    IFC4_IfcMassFlowRateMeasure_type = new type_declaration("IfcMassFlowRateMeasure", 552, new simple_type(simple_type::real_type));
    IFC4_IfcMassMeasure_type = new type_declaration("IfcMassMeasure", 553, new simple_type(simple_type::real_type));
    IFC4_IfcMassPerLengthMeasure_type = new type_declaration("IfcMassPerLengthMeasure", 554, new simple_type(simple_type::real_type));
    IFC4_IfcModulusOfElasticityMeasure_type = new type_declaration("IfcModulusOfElasticityMeasure", 590, new simple_type(simple_type::real_type));
    IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfLinearSubgradeReactionMeasure", 591, new simple_type(simple_type::real_type));
    IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfRotationalSubgradeReactionMeasure", 592, new simple_type(simple_type::real_type));
    IFC4_IfcModulusOfSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfSubgradeReactionMeasure", 594, new simple_type(simple_type::real_type));
    IFC4_IfcMoistureDiffusivityMeasure_type = new type_declaration("IfcMoistureDiffusivityMeasure", 597, new simple_type(simple_type::real_type));
    IFC4_IfcMolecularWeightMeasure_type = new type_declaration("IfcMolecularWeightMeasure", 598, new simple_type(simple_type::real_type));
    IFC4_IfcMomentOfInertiaMeasure_type = new type_declaration("IfcMomentOfInertiaMeasure", 599, new simple_type(simple_type::real_type));
    IFC4_IfcMonetaryMeasure_type = new type_declaration("IfcMonetaryMeasure", 600, new simple_type(simple_type::real_type));
    IFC4_IfcMonthInYearNumber_type = new type_declaration("IfcMonthInYearNumber", 602, new simple_type(simple_type::integer_type));
    IFC4_IfcNonNegativeLengthMeasure_type = new type_declaration("IfcNonNegativeLengthMeasure", 607, new named_type(IFC4_IfcLengthMeasure_type));
    IFC4_IfcNumericMeasure_type = new type_declaration("IfcNumericMeasure", 610, new simple_type(simple_type::number_type));
    IFC4_IfcPHMeasure_type = new type_declaration("IfcPHMeasure", 646, new simple_type(simple_type::real_type));
    IFC4_IfcParameterValue_type = new type_declaration("IfcParameterValue", 635, new simple_type(simple_type::real_type));
    IFC4_IfcPlanarForceMeasure_type = new type_declaration("IfcPlanarForceMeasure", 665, new simple_type(simple_type::real_type));
    IFC4_IfcPlaneAngleMeasure_type = new type_declaration("IfcPlaneAngleMeasure", 667, new simple_type(simple_type::real_type));
    IFC4_IfcPositiveInteger_type = new type_declaration("IfcPositiveInteger", 680, new named_type(IFC4_IfcInteger_type));
    IFC4_IfcPositiveLengthMeasure_type = new type_declaration("IfcPositiveLengthMeasure", 681, new named_type(IFC4_IfcLengthMeasure_type));
    IFC4_IfcPositivePlaneAngleMeasure_type = new type_declaration("IfcPositivePlaneAngleMeasure", 682, new named_type(IFC4_IfcPlaneAngleMeasure_type));
    IFC4_IfcPowerMeasure_type = new type_declaration("IfcPowerMeasure", 685, new simple_type(simple_type::real_type));
    IFC4_IfcPresentableText_type = new type_declaration("IfcPresentableText", 692, new simple_type(simple_type::string_type));
    IFC4_IfcPressureMeasure_type = new type_declaration("IfcPressureMeasure", 699, new simple_type(simple_type::real_type));
    IFC4_IfcPropertySetDefinitionSet_type = new type_declaration("IfcPropertySetDefinitionSet", 733, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertySetDefinition_type)));
    IFC4_IfcRadioActivityMeasure_type = new type_declaration("IfcRadioActivityMeasure", 757, new simple_type(simple_type::real_type));
    IFC4_IfcRatioMeasure_type = new type_declaration("IfcRatioMeasure", 767, new simple_type(simple_type::real_type));
    IFC4_IfcReal_type = new type_declaration("IfcReal", 770, new simple_type(simple_type::real_type));
    IFC4_IfcRotationalFrequencyMeasure_type = new type_declaration("IfcRotationalFrequencyMeasure", 861, new simple_type(simple_type::real_type));
    IFC4_IfcRotationalMassMeasure_type = new type_declaration("IfcRotationalMassMeasure", 862, new simple_type(simple_type::real_type));
    IFC4_IfcRotationalStiffnessMeasure_type = new type_declaration("IfcRotationalStiffnessMeasure", 863, new simple_type(simple_type::real_type));
    IFC4_IfcSectionModulusMeasure_type = new type_declaration("IfcSectionModulusMeasure", 872, new simple_type(simple_type::real_type));
    IFC4_IfcSectionalAreaIntegralMeasure_type = new type_declaration("IfcSectionalAreaIntegralMeasure", 870, new simple_type(simple_type::real_type));
    IFC4_IfcShearModulusMeasure_type = new type_declaration("IfcShearModulusMeasure", 887, new simple_type(simple_type::real_type));
    IFC4_IfcSolidAngleMeasure_type = new type_declaration("IfcSolidAngleMeasure", 908, new simple_type(simple_type::real_type));
    IFC4_IfcSoundPowerLevelMeasure_type = new type_declaration("IfcSoundPowerLevelMeasure", 911, new simple_type(simple_type::real_type));
    IFC4_IfcSoundPowerMeasure_type = new type_declaration("IfcSoundPowerMeasure", 912, new simple_type(simple_type::real_type));
    IFC4_IfcSoundPressureLevelMeasure_type = new type_declaration("IfcSoundPressureLevelMeasure", 913, new simple_type(simple_type::real_type));
    IFC4_IfcSoundPressureMeasure_type = new type_declaration("IfcSoundPressureMeasure", 914, new simple_type(simple_type::real_type));
    IFC4_IfcSpecificHeatCapacityMeasure_type = new type_declaration("IfcSpecificHeatCapacityMeasure", 929, new simple_type(simple_type::real_type));
    IFC4_IfcSpecularExponent_type = new type_declaration("IfcSpecularExponent", 930, new simple_type(simple_type::real_type));
    IFC4_IfcSpecularRoughness_type = new type_declaration("IfcSpecularRoughness", 932, new simple_type(simple_type::real_type));
    IFC4_IfcStrippedOptional_type = new type_declaration("IfcStrippedOptional", 944, new simple_type(simple_type::boolean_type));
    IFC4_IfcTemperatureGradientMeasure_type = new type_declaration("IfcTemperatureGradientMeasure", 1036, new simple_type(simple_type::real_type));
    IFC4_IfcTemperatureRateOfChangeMeasure_type = new type_declaration("IfcTemperatureRateOfChangeMeasure", 1037, new simple_type(simple_type::real_type));
    IFC4_IfcText_type = new type_declaration("IfcText", 1046, new simple_type(simple_type::string_type));
    IFC4_IfcTextAlignment_type = new type_declaration("IfcTextAlignment", 1047, new simple_type(simple_type::string_type));
    IFC4_IfcTextDecoration_type = new type_declaration("IfcTextDecoration", 1048, new simple_type(simple_type::string_type));
    IFC4_IfcTextFontName_type = new type_declaration("IfcTextFontName", 1049, new simple_type(simple_type::string_type));
    IFC4_IfcTextTransformation_type = new type_declaration("IfcTextTransformation", 1058, new simple_type(simple_type::string_type));
    IFC4_IfcThermalAdmittanceMeasure_type = new type_declaration("IfcThermalAdmittanceMeasure", 1064, new simple_type(simple_type::real_type));
    IFC4_IfcThermalConductivityMeasure_type = new type_declaration("IfcThermalConductivityMeasure", 1065, new simple_type(simple_type::real_type));
    IFC4_IfcThermalExpansionCoefficientMeasure_type = new type_declaration("IfcThermalExpansionCoefficientMeasure", 1066, new simple_type(simple_type::real_type));
    IFC4_IfcThermalResistanceMeasure_type = new type_declaration("IfcThermalResistanceMeasure", 1067, new simple_type(simple_type::real_type));
    IFC4_IfcThermalTransmittanceMeasure_type = new type_declaration("IfcThermalTransmittanceMeasure", 1068, new simple_type(simple_type::real_type));
    IFC4_IfcThermodynamicTemperatureMeasure_type = new type_declaration("IfcThermodynamicTemperatureMeasure", 1069, new simple_type(simple_type::real_type));
    IFC4_IfcTime_type = new type_declaration("IfcTime", 1070, new simple_type(simple_type::string_type));
    IFC4_IfcTimeMeasure_type = new type_declaration("IfcTimeMeasure", 1071, new simple_type(simple_type::real_type));
    IFC4_IfcTimeStamp_type = new type_declaration("IfcTimeStamp", 1077, new simple_type(simple_type::integer_type));
    IFC4_IfcTorqueMeasure_type = new type_declaration("IfcTorqueMeasure", 1080, new simple_type(simple_type::real_type));
    IFC4_IfcURIReference_type = new type_declaration("IfcURIReference", 1111, new simple_type(simple_type::string_type));
    IFC4_IfcVaporPermeabilityMeasure_type = new type_declaration("IfcVaporPermeabilityMeasure", 1117, new simple_type(simple_type::real_type));
    IFC4_IfcVolumeMeasure_type = new type_declaration("IfcVolumeMeasure", 1130, new simple_type(simple_type::real_type));
    IFC4_IfcVolumetricFlowRateMeasure_type = new type_declaration("IfcVolumetricFlowRateMeasure", 1131, new simple_type(simple_type::real_type));
    IFC4_IfcWarpingConstantMeasure_type = new type_declaration("IfcWarpingConstantMeasure", 1137, new simple_type(simple_type::real_type));
    IFC4_IfcWarpingMomentMeasure_type = new type_declaration("IfcWarpingMomentMeasure", 1138, new simple_type(simple_type::real_type));
    IFC4_IfcBoxAlignment_type = new type_declaration("IfcBoxAlignment", 83, new named_type(IFC4_IfcLabel_type));
    IFC4_IfcNormalisedRatioMeasure_type = new type_declaration("IfcNormalisedRatioMeasure", 608, new named_type(IFC4_IfcRatioMeasure_type));
    IFC4_IfcPositiveRatioMeasure_type = new type_declaration("IfcPositiveRatioMeasure", 683, new named_type(IFC4_IfcRatioMeasure_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("EMAIL");
        items.push_back("FAX");
        items.push_back("NOTDEFINED");
        items.push_back("PHONE");
        items.push_back("POST");
        items.push_back("USERDEFINED");
        items.push_back("VERBAL");
        IFC4_IfcActionRequestTypeEnum_type = new enumeration_type("IfcActionRequestTypeEnum", 3, items);
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
        IFC4_IfcActionSourceTypeEnum_type = new enumeration_type("IfcActionSourceTypeEnum", 4, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IFC4_IfcActionTypeEnum_type = new enumeration_type("IfcActionTypeEnum", 5, items);
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
        IFC4_IfcActuatorTypeEnum_type = new enumeration_type("IfcActuatorTypeEnum", 11, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC4_IfcAddressTypeEnum_type = new enumeration_type("IfcAddressTypeEnum", 13, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IFC4_IfcAirTerminalBoxTypeEnum_type = new enumeration_type("IfcAirTerminalBoxTypeEnum", 20, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("DIFFUSER");
        items.push_back("GRILLE");
        items.push_back("LOUVRE");
        items.push_back("NOTDEFINED");
        items.push_back("REGISTER");
        items.push_back("USERDEFINED");
        IFC4_IfcAirTerminalTypeEnum_type = new enumeration_type("IfcAirTerminalTypeEnum", 22, items);
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
        IFC4_IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type("IfcAirToAirHeatRecoveryTypeEnum", 25, items);
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
        IFC4_IfcAlarmTypeEnum_type = new enumeration_type("IfcAlarmTypeEnum", 28, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IFC4_IfcAnalysisModelTypeEnum_type = new enumeration_type("IfcAnalysisModelTypeEnum", 30, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IFC4_IfcAnalysisTheoryTypeEnum_type = new enumeration_type("IfcAnalysisTheoryTypeEnum", 31, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IFC4_IfcArithmeticOperatorEnum_type = new enumeration_type("IfcArithmeticOperatorEnum", 46, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IFC4_IfcAssemblyPlaceEnum_type = new enumeration_type("IfcAssemblyPlaceEnum", 47, items);
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
        IFC4_IfcAudioVisualApplianceTypeEnum_type = new enumeration_type("IfcAudioVisualApplianceTypeEnum", 52, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IFC4_IfcBSplineCurveForm_type = new enumeration_type("IfcBSplineCurveForm", 86, items);
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
        IFC4_IfcBSplineSurfaceForm_type = new enumeration_type("IfcBSplineSurfaceForm", 89, items);
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
        IFC4_IfcBeamTypeEnum_type = new enumeration_type("IfcBeamTypeEnum", 60, items);
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
        IFC4_IfcBenchmarkEnum_type = new enumeration_type("IfcBenchmarkEnum", 61, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IFC4_IfcBoilerTypeEnum_type = new enumeration_type("IfcBoilerTypeEnum", 68, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IFC4_IfcBooleanOperator_type = new enumeration_type("IfcBooleanOperator", 72, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("INSULATION");
        items.push_back("NOTDEFINED");
        items.push_back("PRECASTPANEL");
        items.push_back("USERDEFINED");
        IFC4_IfcBuildingElementPartTypeEnum_type = new enumeration_type("IfcBuildingElementPartTypeEnum", 95, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("PARTIAL");
        items.push_back("PROVISIONFORVOID");
        items.push_back("USERDEFINED");
        IFC4_IfcBuildingElementProxyTypeEnum_type = new enumeration_type("IfcBuildingElementProxyTypeEnum", 98, items);
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
        IFC4_IfcBuildingSystemTypeEnum_type = new enumeration_type("IfcBuildingSystemTypeEnum", 102, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcBurnerTypeEnum_type = new enumeration_type("IfcBurnerTypeEnum", 105, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IFC4_IfcCableCarrierFittingTypeEnum_type = new enumeration_type("IfcCableCarrierFittingTypeEnum", 108, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcCableCarrierSegmentTypeEnum_type = new enumeration_type("IfcCableCarrierSegmentTypeEnum", 111, items);
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
        IFC4_IfcCableFittingTypeEnum_type = new enumeration_type("IfcCableFittingTypeEnum", 114, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BUSBARSEGMENT");
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("CORESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcCableSegmentTypeEnum_type = new enumeration_type("IfcCableSegmentTypeEnum", 117, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("NOCHANGE");
        items.push_back("NOTDEFINED");
        IFC4_IfcChangeActionEnum_type = new enumeration_type("IfcChangeActionEnum", 129, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IFC4_IfcChillerTypeEnum_type = new enumeration_type("IfcChillerTypeEnum", 132, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcChimneyTypeEnum_type = new enumeration_type("IfcChimneyTypeEnum", 135, items);
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
        IFC4_IfcCoilTypeEnum_type = new enumeration_type("IfcCoilTypeEnum", 148, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("PILASTER");
        items.push_back("USERDEFINED");
        IFC4_IfcColumnTypeEnum_type = new enumeration_type("IfcColumnTypeEnum", 157, items);
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
        IFC4_IfcCommunicationsApplianceTypeEnum_type = new enumeration_type("IfcCommunicationsApplianceTypeEnum", 160, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("P_COMPLEX");
        items.push_back("Q_COMPLEX");
        IFC4_IfcComplexPropertyTemplateTypeEnum_type = new enumeration_type("IfcComplexPropertyTemplateTypeEnum", 164, items);
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
        IFC4_IfcCompressorTypeEnum_type = new enumeration_type("IfcCompressorTypeEnum", 172, items);
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
        IFC4_IfcCondenserTypeEnum_type = new enumeration_type("IfcCondenserTypeEnum", 175, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IFC4_IfcConnectionTypeEnum_type = new enumeration_type("IfcConnectionTypeEnum", 183, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IFC4_IfcConstraintEnum_type = new enumeration_type("IfcConstraintEnum", 186, items);
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
        IFC4_IfcConstructionEquipmentResourceTypeEnum_type = new enumeration_type("IfcConstructionEquipmentResourceTypeEnum", 189, items);
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
        IFC4_IfcConstructionMaterialResourceTypeEnum_type = new enumeration_type("IfcConstructionMaterialResourceTypeEnum", 192, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ASSEMBLY");
        items.push_back("FORMWORK");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcConstructionProductResourceTypeEnum_type = new enumeration_type("IfcConstructionProductResourceTypeEnum", 195, items);
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
        IFC4_IfcControllerTypeEnum_type = new enumeration_type("IfcControllerTypeEnum", 204, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IFC4_IfcCooledBeamTypeEnum_type = new enumeration_type("IfcCooledBeamTypeEnum", 209, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcCoolingTowerTypeEnum_type = new enumeration_type("IfcCoolingTowerTypeEnum", 212, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcCostItemTypeEnum_type = new enumeration_type("IfcCostItemTypeEnum", 217, items);
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
        IFC4_IfcCostScheduleTypeEnum_type = new enumeration_type("IfcCostScheduleTypeEnum", 219, items);
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
        IFC4_IfcCoveringTypeEnum_type = new enumeration_type("IfcCoveringTypeEnum", 224, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC4_IfcCrewResourceTypeEnum_type = new enumeration_type("IfcCrewResourceTypeEnum", 227, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcCurtainWallTypeEnum_type = new enumeration_type("IfcCurtainWallTypeEnum", 235, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LINEAR");
        items.push_back("LOG_LINEAR");
        items.push_back("LOG_LOG");
        items.push_back("NOTDEFINED");
        IFC4_IfcCurveInterpolationEnum_type = new enumeration_type("IfcCurveInterpolationEnum", 241, items);
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
        IFC4_IfcDamperTypeEnum_type = new enumeration_type("IfcDamperTypeEnum", 252, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IFC4_IfcDataOriginEnum_type = new enumeration_type("IfcDataOriginEnum", 253, items);
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
        IFC4_IfcDerivedUnitEnum_type = new enumeration_type("IfcDerivedUnitEnum", 263, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC4_IfcDirectionSenseEnum_type = new enumeration_type("IfcDirectionSenseEnum", 268, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ANCHORPLATE");
        items.push_back("BRACKET");
        items.push_back("NOTDEFINED");
        items.push_back("SHOE");
        items.push_back("USERDEFINED");
        IFC4_IfcDiscreteAccessoryTypeEnum_type = new enumeration_type("IfcDiscreteAccessoryTypeEnum", 271, items);
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
        IFC4_IfcDistributionChamberElementTypeEnum_type = new enumeration_type("IfcDistributionChamberElementTypeEnum", 274, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLE");
        items.push_back("CABLECARRIER");
        items.push_back("DUCT");
        items.push_back("NOTDEFINED");
        items.push_back("PIPE");
        items.push_back("USERDEFINED");
        IFC4_IfcDistributionPortTypeEnum_type = new enumeration_type("IfcDistributionPortTypeEnum", 283, items);
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
        IFC4_IfcDistributionSystemEnum_type = new enumeration_type("IfcDistributionSystemEnum", 285, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IFC4_IfcDocumentConfidentialityEnum_type = new enumeration_type("IfcDocumentConfidentialityEnum", 286, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IFC4_IfcDocumentStatusEnum_type = new enumeration_type("IfcDocumentStatusEnum", 291, items);
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
        IFC4_IfcDoorPanelOperationEnum_type = new enumeration_type("IfcDoorPanelOperationEnum", 294, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IFC4_IfcDoorPanelPositionEnum_type = new enumeration_type("IfcDoorPanelPositionEnum", 295, items);
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
        IFC4_IfcDoorStyleConstructionEnum_type = new enumeration_type("IfcDoorStyleConstructionEnum", 299, items);
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
        IFC4_IfcDoorStyleOperationEnum_type = new enumeration_type("IfcDoorStyleOperationEnum", 300, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DOOR");
        items.push_back("GATE");
        items.push_back("NOTDEFINED");
        items.push_back("TRAPDOOR");
        items.push_back("USERDEFINED");
        IFC4_IfcDoorTypeEnum_type = new enumeration_type("IfcDoorTypeEnum", 302, items);
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
        IFC4_IfcDoorTypeOperationEnum_type = new enumeration_type("IfcDoorTypeOperationEnum", 303, items);
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
        IFC4_IfcDuctFittingTypeEnum_type = new enumeration_type("IfcDuctFittingTypeEnum", 309, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IFC4_IfcDuctSegmentTypeEnum_type = new enumeration_type("IfcDuctSegmentTypeEnum", 312, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IFC4_IfcDuctSilencerTypeEnum_type = new enumeration_type("IfcDuctSilencerTypeEnum", 315, items);
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
        IFC4_IfcElectricApplianceTypeEnum_type = new enumeration_type("IfcElectricApplianceTypeEnum", 323, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONSUMERUNIT");
        items.push_back("DISTRIBUTIONBOARD");
        items.push_back("MOTORCONTROLCENTRE");
        items.push_back("NOTDEFINED");
        items.push_back("SWITCHBOARD");
        items.push_back("USERDEFINED");
        IFC4_IfcElectricDistributionBoardTypeEnum_type = new enumeration_type("IfcElectricDistributionBoardTypeEnum", 330, items);
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
        IFC4_IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type("IfcElectricFlowStorageDeviceTypeEnum", 333, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CHP");
        items.push_back("ENGINEGENERATOR");
        items.push_back("NOTDEFINED");
        items.push_back("STANDALONE");
        items.push_back("USERDEFINED");
        IFC4_IfcElectricGeneratorTypeEnum_type = new enumeration_type("IfcElectricGeneratorTypeEnum", 336, items);
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
        IFC4_IfcElectricMotorTypeEnum_type = new enumeration_type("IfcElectricMotorTypeEnum", 339, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IFC4_IfcElectricTimeControlTypeEnum_type = new enumeration_type("IfcElectricTimeControlTypeEnum", 343, items);
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
        IFC4_IfcElementAssemblyTypeEnum_type = new enumeration_type("IfcElementAssemblyTypeEnum", 349, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IFC4_IfcElementCompositionEnum_type = new enumeration_type("IfcElementCompositionEnum", 352, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("EXTERNALCOMBUSTION");
        items.push_back("INTERNALCOMBUSTION");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcEngineTypeEnum_type = new enumeration_type("IfcEngineTypeEnum", 362, items);
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
        IFC4_IfcEvaporativeCoolerTypeEnum_type = new enumeration_type("IfcEvaporativeCoolerTypeEnum", 365, items);
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
        IFC4_IfcEvaporatorTypeEnum_type = new enumeration_type("IfcEvaporatorTypeEnum", 368, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EVENTCOMPLEX");
        items.push_back("EVENTMESSAGE");
        items.push_back("EVENTRULE");
        items.push_back("EVENTTIME");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcEventTriggerTypeEnum_type = new enumeration_type("IfcEventTriggerTypeEnum", 371, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ENDEVENT");
        items.push_back("INTERMEDIATEEVENT");
        items.push_back("NOTDEFINED");
        items.push_back("STARTEVENT");
        items.push_back("USERDEFINED");
        IFC4_IfcEventTypeEnum_type = new enumeration_type("IfcEventTypeEnum", 373, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("NOTDEFIEND");
        items.push_back("USERDEFINED");
        IFC4_IfcExternalSpatialElementTypeEnum_type = new enumeration_type("IfcExternalSpatialElementTypeEnum", 382, items);
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
        IFC4_IfcFanTypeEnum_type = new enumeration_type("IfcFanTypeEnum", 396, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GLUE");
        items.push_back("MORTAR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WELD");
        IFC4_IfcFastenerTypeEnum_type = new enumeration_type("IfcFastenerTypeEnum", 399, items);
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
        IFC4_IfcFilterTypeEnum_type = new enumeration_type("IfcFilterTypeEnum", 409, items);
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
        IFC4_IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type("IfcFireSuppressionTerminalTypeEnum", 412, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IFC4_IfcFlowDirectionEnum_type = new enumeration_type("IfcFlowDirectionEnum", 416, items);
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
        IFC4_IfcFlowInstrumentTypeEnum_type = new enumeration_type("IfcFlowInstrumentTypeEnum", 421, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ENERGYMETER");
        items.push_back("GASMETER");
        items.push_back("NOTDEFINED");
        items.push_back("OILMETER");
        items.push_back("USERDEFINED");
        items.push_back("WATERMETER");
        IFC4_IfcFlowMeterTypeEnum_type = new enumeration_type("IfcFlowMeterTypeEnum", 424, items);
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
        IFC4_IfcFootingTypeEnum_type = new enumeration_type("IfcFootingTypeEnum", 440, items);
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
        IFC4_IfcFurnitureTypeEnum_type = new enumeration_type("IfcFurnitureTypeEnum", 447, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("TERRAIN");
        items.push_back("USERDEFINED");
        IFC4_IfcGeographicElementTypeEnum_type = new enumeration_type("IfcGeographicElementTypeEnum", 450, items);
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
        IFC4_IfcGeometricProjectionEnum_type = new enumeration_type("IfcGeometricProjectionEnum", 452, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IFC4_IfcGlobalOrLocalEnum_type = new enumeration_type("IfcGlobalOrLocalEnum", 459, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("IRREGULAR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIAL");
        items.push_back("RECTANGULAR");
        items.push_back("TRIANGULAR");
        items.push_back("USERDEFINED");
        IFC4_IfcGridTypeEnum_type = new enumeration_type("IfcGridTypeEnum", 464, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IFC4_IfcHeatExchangerTypeEnum_type = new enumeration_type("IfcHeatExchangerTypeEnum", 470, items);
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
        IFC4_IfcHumidifierTypeEnum_type = new enumeration_type("IfcHumidifierTypeEnum", 475, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CYCLONIC");
        items.push_back("GREASE");
        items.push_back("NOTDEFINED");
        items.push_back("OIL");
        items.push_back("PETROL");
        items.push_back("USERDEFINED");
        IFC4_IfcInterceptorTypeEnum_type = new enumeration_type("IfcInterceptorTypeEnum", 488, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IFC4_IfcInternalOrExternalEnum_type = new enumeration_type("IfcInternalOrExternalEnum", 489, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IFC4_IfcInventoryTypeEnum_type = new enumeration_type("IfcInventoryTypeEnum", 491, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DATA");
        items.push_back("NOTDEFINED");
        items.push_back("POWER");
        items.push_back("USERDEFINED");
        IFC4_IfcJunctionBoxTypeEnum_type = new enumeration_type("IfcJunctionBoxTypeEnum", 499, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("PIECEWISE_BEZIER_KNOTS");
        items.push_back("QUASI_UNIFORM_KNOTS");
        items.push_back("UNIFORM_KNOTS");
        items.push_back("UNSPECIFIED");
        IFC4_IfcKnotType_type = new enumeration_type("IfcKnotType", 501, items);
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
        IFC4_IfcLaborResourceTypeEnum_type = new enumeration_type("IfcLaborResourceTypeEnum", 505, items);
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
        IFC4_IfcLampTypeEnum_type = new enumeration_type("IfcLampTypeEnum", 509, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IFC4_IfcLayerSetDirectionEnum_type = new enumeration_type("IfcLayerSetDirectionEnum", 512, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IFC4_IfcLightDistributionCurveEnum_type = new enumeration_type("IfcLightDistributionCurveEnum", 517, items);
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
        IFC4_IfcLightEmissionSourceEnum_type = new enumeration_type("IfcLightEmissionSourceEnum", 520, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("SECURITYLIGHTING");
        items.push_back("USERDEFINED");
        IFC4_IfcLightFixtureTypeEnum_type = new enumeration_type("IfcLightFixtureTypeEnum", 523, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcLoadGroupTypeEnum_type = new enumeration_type("IfcLoadGroupTypeEnum", 537, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALNOTAND");
        items.push_back("LOGICALNOTOR");
        items.push_back("LOGICALOR");
        items.push_back("LOGICALXOR");
        IFC4_IfcLogicalOperatorEnum_type = new enumeration_type("IfcLogicalOperatorEnum", 540, items);
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
        IFC4_IfcMechanicalFastenerTypeEnum_type = new enumeration_type("IfcMechanicalFastenerTypeEnum", 579, items);
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
        IFC4_IfcMedicalDeviceTypeEnum_type = new enumeration_type("IfcMedicalDeviceTypeEnum", 582, items);
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
        IFC4_IfcMemberTypeEnum_type = new enumeration_type("IfcMemberTypeEnum", 586, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcMotorConnectionTypeEnum_type = new enumeration_type("IfcMotorConnectionTypeEnum", 605, items);
    }
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IFC4_IfcNullStyle_type = new enumeration_type("IfcNullStyle", 609, items);
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
        IFC4_IfcObjectTypeEnum_type = new enumeration_type("IfcObjectTypeEnum", 617, items);
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
        IFC4_IfcObjectiveEnum_type = new enumeration_type("IfcObjectiveEnum", 614, items);
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
        IFC4_IfcOccupantTypeEnum_type = new enumeration_type("IfcOccupantTypeEnum", 619, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OPENING");
        items.push_back("RECESS");
        items.push_back("USERDEFINED");
        IFC4_IfcOpeningElementTypeEnum_type = new enumeration_type("IfcOpeningElementTypeEnum", 623, items);
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
        IFC4_IfcOutletTypeEnum_type = new enumeration_type("IfcOutletTypeEnum", 632, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcPerformanceHistoryTypeEnum_type = new enumeration_type("IfcPerformanceHistoryTypeEnum", 639, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IFC4_IfcPermeableCoveringOperationEnum_type = new enumeration_type("IfcPermeableCoveringOperationEnum", 640, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACCESS");
        items.push_back("BUILDING");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IFC4_IfcPermitTypeEnum_type = new enumeration_type("IfcPermitTypeEnum", 643, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IFC4_IfcPhysicalOrVirtualEnum_type = new enumeration_type("IfcPhysicalOrVirtualEnum", 648, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IFC4_IfcPileConstructionEnum_type = new enumeration_type("IfcPileConstructionEnum", 652, items);
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
        IFC4_IfcPileTypeEnum_type = new enumeration_type("IfcPileTypeEnum", 654, items);
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
        IFC4_IfcPipeFittingTypeEnum_type = new enumeration_type("IfcPipeFittingTypeEnum", 657, items);
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
        IFC4_IfcPipeSegmentTypeEnum_type = new enumeration_type("IfcPipeSegmentTypeEnum", 660, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CURTAIN_PANEL");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("USERDEFINED");
        IFC4_IfcPlateTypeEnum_type = new enumeration_type("IfcPlateTypeEnum", 671, items);
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
        IFC4_IfcProcedureTypeEnum_type = new enumeration_type("IfcProcedureTypeEnum", 702, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IFC4_IfcProfileTypeEnum_type = new enumeration_type("IfcProfileTypeEnum", 712, items);
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
        IFC4_IfcProjectOrderTypeEnum_type = new enumeration_type("IfcProjectOrderTypeEnum", 720, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IFC4_IfcProjectedOrTrueLengthEnum_type = new enumeration_type("IfcProjectedOrTrueLengthEnum", 715, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcProjectionElementTypeEnum_type = new enumeration_type("IfcProjectionElementTypeEnum", 717, items);
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
        IFC4_IfcPropertySetTemplateTypeEnum_type = new enumeration_type("IfcPropertySetTemplateTypeEnum", 735, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ELECTROMAGNETIC");
        items.push_back("ELECTRONIC");
        items.push_back("NOTDEFINED");
        items.push_back("RESIDUALCURRENT");
        items.push_back("THERMAL");
        items.push_back("USERDEFINED");
        IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type = new enumeration_type("IfcProtectiveDeviceTrippingUnitTypeEnum", 743, items);
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
        IFC4_IfcProtectiveDeviceTypeEnum_type = new enumeration_type("IfcProtectiveDeviceTypeEnum", 745, items);
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
        IFC4_IfcPumpTypeEnum_type = new enumeration_type("IfcPumpTypeEnum", 749, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcRailingTypeEnum_type = new enumeration_type("IfcRailingTypeEnum", 760, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IFC4_IfcRampFlightTypeEnum_type = new enumeration_type("IfcRampFlightTypeEnum", 764, items);
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
        IFC4_IfcRampTypeEnum_type = new enumeration_type("IfcRampTypeEnum", 766, items);
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
        IFC4_IfcRecurrenceTypeEnum_type = new enumeration_type("IfcRecurrenceTypeEnum", 776, items);
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
        IFC4_IfcReflectanceMethodEnum_type = new enumeration_type("IfcReflectanceMethodEnum", 778, items);
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
        IFC4_IfcReinforcingBarRoleEnum_type = new enumeration_type("IfcReinforcingBarRoleEnum", 783, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IFC4_IfcReinforcingBarSurfaceEnum_type = new enumeration_type("IfcReinforcingBarSurfaceEnum", 784, items);
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
        IFC4_IfcReinforcingBarTypeEnum_type = new enumeration_type("IfcReinforcingBarTypeEnum", 786, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcReinforcingMeshTypeEnum_type = new enumeration_type("IfcReinforcingMeshTypeEnum", 791, items);
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
        IFC4_IfcRoleEnum_type = new enumeration_type("IfcRoleEnum", 856, items);
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
        IFC4_IfcRoofTypeEnum_type = new enumeration_type("IfcRoofTypeEnum", 859, items);
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
        IFC4_IfcSIPrefix_type = new enumeration_type("IfcSIPrefix", 894, items);
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
        IFC4_IfcSIUnitName_type = new enumeration_type("IfcSIUnitName", 897, items);
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
        IFC4_IfcSanitaryTerminalTypeEnum_type = new enumeration_type("IfcSanitaryTerminalTypeEnum", 868, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IFC4_IfcSectionTypeEnum_type = new enumeration_type("IfcSectionTypeEnum", 875, items);
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
        IFC4_IfcSensorTypeEnum_type = new enumeration_type("IfcSensorTypeEnum", 879, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        items.push_back("USERDEFINED");
        IFC4_IfcSequenceEnum_type = new enumeration_type("IfcSequenceEnum", 880, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AWNING");
        items.push_back("JALOUSIE");
        items.push_back("NOTDEFINED");
        items.push_back("SHUTTER");
        items.push_back("USERDEFINED");
        IFC4_IfcShadingDeviceTypeEnum_type = new enumeration_type("IfcShadingDeviceTypeEnum", 883, items);
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
        IFC4_IfcSimplePropertyTemplateTypeEnum_type = new enumeration_type("IfcSimplePropertyTemplateTypeEnum", 892, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOF");
        items.push_back("USERDEFINED");
        IFC4_IfcSlabTypeEnum_type = new enumeration_type("IfcSlabTypeEnum", 903, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SOLARCOLLECTOR");
        items.push_back("SOLARPANEL");
        items.push_back("USERDEFINED");
        IFC4_IfcSolarDeviceTypeEnum_type = new enumeration_type("IfcSolarDeviceTypeEnum", 907, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONVECTOR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIATOR");
        items.push_back("USERDEFINED");
        IFC4_IfcSpaceHeaterTypeEnum_type = new enumeration_type("IfcSpaceHeaterTypeEnum", 919, items);
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
        IFC4_IfcSpaceTypeEnum_type = new enumeration_type("IfcSpaceTypeEnum", 921, items);
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
        IFC4_IfcSpatialZoneTypeEnum_type = new enumeration_type("IfcSpatialZoneTypeEnum", 928, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IFC4_IfcStackTerminalTypeEnum_type = new enumeration_type("IfcStackTerminalTypeEnum", 936, items);
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
        IFC4_IfcStairFlightTypeEnum_type = new enumeration_type("IfcStairFlightTypeEnum", 940, items);
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
        IFC4_IfcStairTypeEnum_type = new enumeration_type("IfcStairTypeEnum", 942, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IFC4_IfcStateEnum_type = new enumeration_type("IfcStateEnum", 943, items);
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
        IFC4_IfcStructuralCurveActivityTypeEnum_type = new enumeration_type("IfcStructuralCurveActivityTypeEnum", 952, items);
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
        IFC4_IfcStructuralCurveMemberTypeEnum_type = new enumeration_type("IfcStructuralCurveMemberTypeEnum", 955, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BILINEAR");
        items.push_back("CONST");
        items.push_back("DISCRETE");
        items.push_back("ISOCONTOUR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcStructuralSurfaceActivityTypeEnum_type = new enumeration_type("IfcStructuralSurfaceActivityTypeEnum", 981, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IFC4_IfcStructuralSurfaceMemberTypeEnum_type = new enumeration_type("IfcStructuralSurfaceMemberTypeEnum", 984, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASE");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IFC4_IfcSubContractResourceTypeEnum_type = new enumeration_type("IfcSubContractResourceTypeEnum", 993, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MARK");
        items.push_back("NOTDEFINED");
        items.push_back("TAG");
        items.push_back("TREATMENT");
        items.push_back("USERDEFINED");
        IFC4_IfcSurfaceFeatureTypeEnum_type = new enumeration_type("IfcSurfaceFeatureTypeEnum", 998, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC4_IfcSurfaceSide_type = new enumeration_type("IfcSurfaceSide", 1003, items);
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
        IFC4_IfcSwitchingDeviceTypeEnum_type = new enumeration_type("IfcSwitchingDeviceTypeEnum", 1018, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PANEL");
        items.push_back("USERDEFINED");
        items.push_back("WORKSURFACE");
        IFC4_IfcSystemFurnitureElementTypeEnum_type = new enumeration_type("IfcSystemFurnitureElementTypeEnum", 1022, items);
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
        IFC4_IfcTankTypeEnum_type = new enumeration_type("IfcTankTypeEnum", 1028, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ELAPSEDTIME");
        items.push_back("NOTDEFINED");
        items.push_back("WORKTIME");
        IFC4_IfcTaskDurationEnum_type = new enumeration_type("IfcTaskDurationEnum", 1030, items);
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
        IFC4_IfcTaskTypeEnum_type = new enumeration_type("IfcTaskTypeEnum", 1034, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COUPLER");
        items.push_back("FIXED_END");
        items.push_back("NOTDEFINED");
        items.push_back("TENSIONING_END");
        items.push_back("USERDEFINED");
        IFC4_IfcTendonAnchorTypeEnum_type = new enumeration_type("IfcTendonAnchorTypeEnum", 1041, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IFC4_IfcTendonTypeEnum_type = new enumeration_type("IfcTendonTypeEnum", 1043, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IFC4_IfcTextPath_type = new enumeration_type("IfcTextPath", 1053, items);
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
        IFC4_IfcTimeSeriesDataTypeEnum_type = new enumeration_type("IfcTimeSeriesDataTypeEnum", 1075, items);
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
        IFC4_IfcTransformerTypeEnum_type = new enumeration_type("IfcTransformerTypeEnum", 1083, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IFC4_IfcTransitionCode_type = new enumeration_type("IfcTransitionCode", 1084, items);
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
        IFC4_IfcTransportElementTypeEnum_type = new enumeration_type("IfcTransportElementTypeEnum", 1088, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IFC4_IfcTrimmingPreference_type = new enumeration_type("IfcTrimmingPreference", 1092, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_IfcTubeBundleTypeEnum_type = new enumeration_type("IfcTubeBundleTypeEnum", 1097, items);
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
        IFC4_IfcUnitEnum_type = new enumeration_type("IfcUnitEnum", 1110, items);
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
        IFC4_IfcUnitaryControlElementTypeEnum_type = new enumeration_type("IfcUnitaryControlElementTypeEnum", 1105, items);
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
        IFC4_IfcUnitaryEquipmentTypeEnum_type = new enumeration_type("IfcUnitaryEquipmentTypeEnum", 1108, items);
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
        IFC4_IfcValveTypeEnum_type = new enumeration_type("IfcValveTypeEnum", 1116, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IFC4_IfcVibrationIsolatorTypeEnum_type = new enumeration_type("IfcVibrationIsolatorTypeEnum", 1125, items);
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
        IFC4_IfcVoidingFeatureTypeEnum_type = new enumeration_type("IfcVoidingFeatureTypeEnum", 1129, items);
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
        IFC4_IfcWallTypeEnum_type = new enumeration_type("IfcWallTypeEnum", 1136, items);
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
        IFC4_IfcWasteTerminalTypeEnum_type = new enumeration_type("IfcWasteTerminalTypeEnum", 1142, items);
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
        IFC4_IfcWindowPanelOperationEnum_type = new enumeration_type("IfcWindowPanelOperationEnum", 1145, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IFC4_IfcWindowPanelPositionEnum_type = new enumeration_type("IfcWindowPanelPositionEnum", 1146, items);
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
        IFC4_IfcWindowStyleConstructionEnum_type = new enumeration_type("IfcWindowStyleConstructionEnum", 1150, items);
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
        IFC4_IfcWindowStyleOperationEnum_type = new enumeration_type("IfcWindowStyleOperationEnum", 1151, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LIGHTDOME");
        items.push_back("NOTDEFINED");
        items.push_back("SKYLIGHT");
        items.push_back("USERDEFINED");
        items.push_back("WINDOW");
        IFC4_IfcWindowTypeEnum_type = new enumeration_type("IfcWindowTypeEnum", 1153, items);
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
        IFC4_IfcWindowTypePartitioningEnum_type = new enumeration_type("IfcWindowTypePartitioningEnum", 1154, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FIRSTSHIFT");
        items.push_back("NOTDEFINED");
        items.push_back("SECONDSHIFT");
        items.push_back("THIRDSHIFT");
        items.push_back("USERDEFINED");
        IFC4_IfcWorkCalendarTypeEnum_type = new enumeration_type("IfcWorkCalendarTypeEnum", 1156, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC4_IfcWorkPlanTypeEnum_type = new enumeration_type("IfcWorkPlanTypeEnum", 1159, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC4_IfcWorkScheduleTypeEnum_type = new enumeration_type("IfcWorkScheduleTypeEnum", 1161, items);
    }
    IFC4_IfcActorRole_type = new entity("IfcActorRole", 7, 0);
    IFC4_IfcAddress_type = new entity("IfcAddress", 12, 0);
    IFC4_IfcApplication_type = new entity("IfcApplication", 35, 0);
    IFC4_IfcAppliedValue_type = new entity("IfcAppliedValue", 36, 0);
    IFC4_IfcApproval_type = new entity("IfcApproval", 38, 0);
    IFC4_IfcBoundaryCondition_type = new entity("IfcBoundaryCondition", 74, 0);
    IFC4_IfcBoundaryEdgeCondition_type = new entity("IfcBoundaryEdgeCondition", 76, IFC4_IfcBoundaryCondition_type);
    IFC4_IfcBoundaryFaceCondition_type = new entity("IfcBoundaryFaceCondition", 77, IFC4_IfcBoundaryCondition_type);
    IFC4_IfcBoundaryNodeCondition_type = new entity("IfcBoundaryNodeCondition", 78, IFC4_IfcBoundaryCondition_type);
    IFC4_IfcBoundaryNodeConditionWarping_type = new entity("IfcBoundaryNodeConditionWarping", 79, IFC4_IfcBoundaryNodeCondition_type);
    IFC4_IfcConnectionGeometry_type = new entity("IfcConnectionGeometry", 179, 0);
    IFC4_IfcConnectionPointGeometry_type = new entity("IfcConnectionPointGeometry", 181, IFC4_IfcConnectionGeometry_type);
    IFC4_IfcConnectionSurfaceGeometry_type = new entity("IfcConnectionSurfaceGeometry", 182, IFC4_IfcConnectionGeometry_type);
    IFC4_IfcConnectionVolumeGeometry_type = new entity("IfcConnectionVolumeGeometry", 184, IFC4_IfcConnectionGeometry_type);
    IFC4_IfcConstraint_type = new entity("IfcConstraint", 185, 0);
    IFC4_IfcCoordinateOperation_type = new entity("IfcCoordinateOperation", 213, 0);
    IFC4_IfcCoordinateReferenceSystem_type = new entity("IfcCoordinateReferenceSystem", 214, 0);
    IFC4_IfcCostValue_type = new entity("IfcCostValue", 220, IFC4_IfcAppliedValue_type);
    IFC4_IfcDerivedUnit_type = new entity("IfcDerivedUnit", 261, 0);
    IFC4_IfcDerivedUnitElement_type = new entity("IfcDerivedUnitElement", 262, 0);
    IFC4_IfcDimensionalExponents_type = new entity("IfcDimensionalExponents", 265, 0);
    IFC4_IfcExternalInformation_type = new entity("IfcExternalInformation", 375, 0);
    IFC4_IfcExternalReference_type = new entity("IfcExternalReference", 379, 0);
    IFC4_IfcExternallyDefinedHatchStyle_type = new entity("IfcExternallyDefinedHatchStyle", 376, IFC4_IfcExternalReference_type);
    IFC4_IfcExternallyDefinedSurfaceStyle_type = new entity("IfcExternallyDefinedSurfaceStyle", 377, IFC4_IfcExternalReference_type);
    IFC4_IfcExternallyDefinedTextFont_type = new entity("IfcExternallyDefinedTextFont", 378, IFC4_IfcExternalReference_type);
    IFC4_IfcGridAxis_type = new entity("IfcGridAxis", 461, 0);
    IFC4_IfcIrregularTimeSeriesValue_type = new entity("IfcIrregularTimeSeriesValue", 494, 0);
    IFC4_IfcLibraryInformation_type = new entity("IfcLibraryInformation", 514, IFC4_IfcExternalInformation_type);
    IFC4_IfcLibraryReference_type = new entity("IfcLibraryReference", 515, IFC4_IfcExternalReference_type);
    IFC4_IfcLightDistributionData_type = new entity("IfcLightDistributionData", 518, 0);
    IFC4_IfcLightIntensityDistribution_type = new entity("IfcLightIntensityDistribution", 524, 0);
    IFC4_IfcMapConversion_type = new entity("IfcMapConversion", 549, IFC4_IfcCoordinateOperation_type);
    IFC4_IfcMaterialClassificationRelationship_type = new entity("IfcMaterialClassificationRelationship", 556, 0);
    IFC4_IfcMaterialDefinition_type = new entity("IfcMaterialDefinition", 559, 0);
    IFC4_IfcMaterialLayer_type = new entity("IfcMaterialLayer", 561, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialLayerSet_type = new entity("IfcMaterialLayerSet", 562, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialLayerWithOffsets_type = new entity("IfcMaterialLayerWithOffsets", 564, IFC4_IfcMaterialLayer_type);
    IFC4_IfcMaterialList_type = new entity("IfcMaterialList", 565, 0);
    IFC4_IfcMaterialProfile_type = new entity("IfcMaterialProfile", 566, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialProfileSet_type = new entity("IfcMaterialProfileSet", 567, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialProfileWithOffsets_type = new entity("IfcMaterialProfileWithOffsets", 570, IFC4_IfcMaterialProfile_type);
    IFC4_IfcMaterialUsageDefinition_type = new entity("IfcMaterialUsageDefinition", 574, 0);
    IFC4_IfcMeasureWithUnit_type = new entity("IfcMeasureWithUnit", 576, 0);
    IFC4_IfcMetric_type = new entity("IfcMetric", 587, IFC4_IfcConstraint_type);
    IFC4_IfcMonetaryUnit_type = new entity("IfcMonetaryUnit", 601, 0);
    IFC4_IfcNamedUnit_type = new entity("IfcNamedUnit", 606, 0);
    IFC4_IfcObjectPlacement_type = new entity("IfcObjectPlacement", 615, 0);
    IFC4_IfcObjective_type = new entity("IfcObjective", 613, IFC4_IfcConstraint_type);
    IFC4_IfcOrganization_type = new entity("IfcOrganization", 626, 0);
    IFC4_IfcOwnerHistory_type = new entity("IfcOwnerHistory", 633, 0);
    IFC4_IfcPerson_type = new entity("IfcPerson", 644, 0);
    IFC4_IfcPersonAndOrganization_type = new entity("IfcPersonAndOrganization", 645, 0);
    IFC4_IfcPhysicalQuantity_type = new entity("IfcPhysicalQuantity", 649, 0);
    IFC4_IfcPhysicalSimpleQuantity_type = new entity("IfcPhysicalSimpleQuantity", 650, IFC4_IfcPhysicalQuantity_type);
    IFC4_IfcPostalAddress_type = new entity("IfcPostalAddress", 684, IFC4_IfcAddress_type);
    IFC4_IfcPresentationItem_type = new entity("IfcPresentationItem", 693, 0);
    IFC4_IfcPresentationLayerAssignment_type = new entity("IfcPresentationLayerAssignment", 694, 0);
    IFC4_IfcPresentationLayerWithStyle_type = new entity("IfcPresentationLayerWithStyle", 695, IFC4_IfcPresentationLayerAssignment_type);
    IFC4_IfcPresentationStyle_type = new entity("IfcPresentationStyle", 696, 0);
    IFC4_IfcPresentationStyleAssignment_type = new entity("IfcPresentationStyleAssignment", 697, 0);
    IFC4_IfcProductRepresentation_type = new entity("IfcProductRepresentation", 707, 0);
    IFC4_IfcProfileDef_type = new entity("IfcProfileDef", 710, 0);
    IFC4_IfcProjectedCRS_type = new entity("IfcProjectedCRS", 714, IFC4_IfcCoordinateReferenceSystem_type);
    IFC4_IfcPropertyAbstraction_type = new entity("IfcPropertyAbstraction", 722, 0);
    IFC4_IfcPropertyEnumeration_type = new entity("IfcPropertyEnumeration", 727, IFC4_IfcPropertyAbstraction_type);
    IFC4_IfcQuantityArea_type = new entity("IfcQuantityArea", 750, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityCount_type = new entity("IfcQuantityCount", 751, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityLength_type = new entity("IfcQuantityLength", 752, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityTime_type = new entity("IfcQuantityTime", 754, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityVolume_type = new entity("IfcQuantityVolume", 755, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityWeight_type = new entity("IfcQuantityWeight", 756, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcRecurrencePattern_type = new entity("IfcRecurrencePattern", 775, 0);
    IFC4_IfcReference_type = new entity("IfcReference", 777, 0);
    IFC4_IfcRepresentation_type = new entity("IfcRepresentation", 841, 0);
    IFC4_IfcRepresentationContext_type = new entity("IfcRepresentationContext", 842, 0);
    IFC4_IfcRepresentationItem_type = new entity("IfcRepresentationItem", 843, 0);
    IFC4_IfcRepresentationMap_type = new entity("IfcRepresentationMap", 844, 0);
    IFC4_IfcResourceLevelRelationship_type = new entity("IfcResourceLevelRelationship", 848, 0);
    IFC4_IfcRoot_type = new entity("IfcRoot", 860, 0);
    IFC4_IfcSIUnit_type = new entity("IfcSIUnit", 896, IFC4_IfcNamedUnit_type);
    IFC4_IfcSchedulingTime_type = new entity("IfcSchedulingTime", 869, 0);
    IFC4_IfcShapeAspect_type = new entity("IfcShapeAspect", 884, 0);
    IFC4_IfcShapeModel_type = new entity("IfcShapeModel", 885, IFC4_IfcRepresentation_type);
    IFC4_IfcShapeRepresentation_type = new entity("IfcShapeRepresentation", 886, IFC4_IfcShapeModel_type);
    IFC4_IfcStructuralConnectionCondition_type = new entity("IfcStructuralConnectionCondition", 950, 0);
    IFC4_IfcStructuralLoad_type = new entity("IfcStructuralLoad", 960, 0);
    IFC4_IfcStructuralLoadConfiguration_type = new entity("IfcStructuralLoadConfiguration", 962, IFC4_IfcStructuralLoad_type);
    IFC4_IfcStructuralLoadOrResult_type = new entity("IfcStructuralLoadOrResult", 965, IFC4_IfcStructuralLoad_type);
    IFC4_IfcStructuralLoadStatic_type = new entity("IfcStructuralLoadStatic", 971, IFC4_IfcStructuralLoadOrResult_type);
    IFC4_IfcStructuralLoadTemperature_type = new entity("IfcStructuralLoadTemperature", 972, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStyleModel_type = new entity("IfcStyleModel", 990, IFC4_IfcRepresentation_type);
    IFC4_IfcStyledItem_type = new entity("IfcStyledItem", 988, IFC4_IfcRepresentationItem_type);
    IFC4_IfcStyledRepresentation_type = new entity("IfcStyledRepresentation", 989, IFC4_IfcStyleModel_type);
    IFC4_IfcSurfaceReinforcementArea_type = new entity("IfcSurfaceReinforcementArea", 1002, IFC4_IfcStructuralLoadOrResult_type);
    IFC4_IfcSurfaceStyle_type = new entity("IfcSurfaceStyle", 1004, IFC4_IfcPresentationStyle_type);
    IFC4_IfcSurfaceStyleLighting_type = new entity("IfcSurfaceStyleLighting", 1006, IFC4_IfcPresentationItem_type);
    IFC4_IfcSurfaceStyleRefraction_type = new entity("IfcSurfaceStyleRefraction", 1007, IFC4_IfcPresentationItem_type);
    IFC4_IfcSurfaceStyleShading_type = new entity("IfcSurfaceStyleShading", 1009, IFC4_IfcPresentationItem_type);
    IFC4_IfcSurfaceStyleWithTextures_type = new entity("IfcSurfaceStyleWithTextures", 1010, IFC4_IfcPresentationItem_type);
    IFC4_IfcSurfaceTexture_type = new entity("IfcSurfaceTexture", 1011, IFC4_IfcPresentationItem_type);
    IFC4_IfcTable_type = new entity("IfcTable", 1023, 0);
    IFC4_IfcTableColumn_type = new entity("IfcTableColumn", 1024, 0);
    IFC4_IfcTableRow_type = new entity("IfcTableRow", 1025, 0);
    IFC4_IfcTaskTime_type = new entity("IfcTaskTime", 1031, IFC4_IfcSchedulingTime_type);
    IFC4_IfcTaskTimeRecurring_type = new entity("IfcTaskTimeRecurring", 1032, IFC4_IfcTaskTime_type);
    IFC4_IfcTelecomAddress_type = new entity("IfcTelecomAddress", 1035, IFC4_IfcAddress_type);
    IFC4_IfcTextStyle_type = new entity("IfcTextStyle", 1054, IFC4_IfcPresentationStyle_type);
    IFC4_IfcTextStyleForDefinedFont_type = new entity("IfcTextStyleForDefinedFont", 1056, IFC4_IfcPresentationItem_type);
    IFC4_IfcTextStyleTextModel_type = new entity("IfcTextStyleTextModel", 1057, IFC4_IfcPresentationItem_type);
    IFC4_IfcTextureCoordinate_type = new entity("IfcTextureCoordinate", 1059, IFC4_IfcPresentationItem_type);
    IFC4_IfcTextureCoordinateGenerator_type = new entity("IfcTextureCoordinateGenerator", 1060, IFC4_IfcTextureCoordinate_type);
    IFC4_IfcTextureMap_type = new entity("IfcTextureMap", 1061, IFC4_IfcTextureCoordinate_type);
    IFC4_IfcTextureVertex_type = new entity("IfcTextureVertex", 1062, IFC4_IfcPresentationItem_type);
    IFC4_IfcTextureVertexList_type = new entity("IfcTextureVertexList", 1063, IFC4_IfcPresentationItem_type);
    IFC4_IfcTimePeriod_type = new entity("IfcTimePeriod", 1073, 0);
    IFC4_IfcTimeSeries_type = new entity("IfcTimeSeries", 1074, 0);
    IFC4_IfcTimeSeriesValue_type = new entity("IfcTimeSeriesValue", 1076, 0);
    IFC4_IfcTopologicalRepresentationItem_type = new entity("IfcTopologicalRepresentationItem", 1078, IFC4_IfcRepresentationItem_type);
    IFC4_IfcTopologyRepresentation_type = new entity("IfcTopologyRepresentation", 1079, IFC4_IfcShapeModel_type);
    IFC4_IfcUnitAssignment_type = new entity("IfcUnitAssignment", 1109, 0);
    IFC4_IfcVertex_type = new entity("IfcVertex", 1120, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcVertexPoint_type = new entity("IfcVertexPoint", 1122, IFC4_IfcVertex_type);
    IFC4_IfcVirtualGridIntersection_type = new entity("IfcVirtualGridIntersection", 1127, 0);
    IFC4_IfcWorkTime_type = new entity("IfcWorkTime", 1162, IFC4_IfcSchedulingTime_type);
    IFC4_IfcApprovalRelationship_type = new entity("IfcApprovalRelationship", 39, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcArbitraryClosedProfileDef_type = new entity("IfcArbitraryClosedProfileDef", 40, IFC4_IfcProfileDef_type);
    IFC4_IfcArbitraryOpenProfileDef_type = new entity("IfcArbitraryOpenProfileDef", 41, IFC4_IfcProfileDef_type);
    IFC4_IfcArbitraryProfileDefWithVoids_type = new entity("IfcArbitraryProfileDefWithVoids", 42, IFC4_IfcArbitraryClosedProfileDef_type);
    IFC4_IfcBlobTexture_type = new entity("IfcBlobTexture", 64, IFC4_IfcSurfaceTexture_type);
    IFC4_IfcCenterLineProfileDef_type = new entity("IfcCenterLineProfileDef", 128, IFC4_IfcArbitraryOpenProfileDef_type);
    IFC4_IfcClassification_type = new entity("IfcClassification", 141, IFC4_IfcExternalInformation_type);
    IFC4_IfcClassificationReference_type = new entity("IfcClassificationReference", 142, IFC4_IfcExternalReference_type);
    IFC4_IfcColourRgbList_type = new entity("IfcColourRgbList", 152, IFC4_IfcPresentationItem_type);
    IFC4_IfcColourSpecification_type = new entity("IfcColourSpecification", 153, IFC4_IfcPresentationItem_type);
    IFC4_IfcCompositeProfileDef_type = new entity("IfcCompositeProfileDef", 168, IFC4_IfcProfileDef_type);
    IFC4_IfcConnectedFaceSet_type = new entity("IfcConnectedFaceSet", 177, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcConnectionCurveGeometry_type = new entity("IfcConnectionCurveGeometry", 178, IFC4_IfcConnectionGeometry_type);
    IFC4_IfcConnectionPointEccentricity_type = new entity("IfcConnectionPointEccentricity", 180, IFC4_IfcConnectionPointGeometry_type);
    IFC4_IfcContextDependentUnit_type = new entity("IfcContextDependentUnit", 200, IFC4_IfcNamedUnit_type);
    IFC4_IfcConversionBasedUnit_type = new entity("IfcConversionBasedUnit", 205, IFC4_IfcNamedUnit_type);
    IFC4_IfcConversionBasedUnitWithOffset_type = new entity("IfcConversionBasedUnitWithOffset", 206, IFC4_IfcConversionBasedUnit_type);
    IFC4_IfcCurrencyRelationship_type = new entity("IfcCurrencyRelationship", 232, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcCurveStyle_type = new entity("IfcCurveStyle", 244, IFC4_IfcPresentationStyle_type);
    IFC4_IfcCurveStyleFont_type = new entity("IfcCurveStyleFont", 245, IFC4_IfcPresentationItem_type);
    IFC4_IfcCurveStyleFontAndScaling_type = new entity("IfcCurveStyleFontAndScaling", 246, IFC4_IfcPresentationItem_type);
    IFC4_IfcCurveStyleFontPattern_type = new entity("IfcCurveStyleFontPattern", 247, IFC4_IfcPresentationItem_type);
    IFC4_IfcDerivedProfileDef_type = new entity("IfcDerivedProfileDef", 260, IFC4_IfcProfileDef_type);
    IFC4_IfcDocumentInformation_type = new entity("IfcDocumentInformation", 287, IFC4_IfcExternalInformation_type);
    IFC4_IfcDocumentInformationRelationship_type = new entity("IfcDocumentInformationRelationship", 288, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcDocumentReference_type = new entity("IfcDocumentReference", 289, IFC4_IfcExternalReference_type);
    IFC4_IfcEdge_type = new entity("IfcEdge", 318, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcEdgeCurve_type = new entity("IfcEdgeCurve", 319, IFC4_IfcEdge_type);
    IFC4_IfcEventTime_type = new entity("IfcEventTime", 370, IFC4_IfcSchedulingTime_type);
    IFC4_IfcExtendedProperties_type = new entity("IfcExtendedProperties", 374, IFC4_IfcPropertyAbstraction_type);
    IFC4_IfcExternalReferenceRelationship_type = new entity("IfcExternalReferenceRelationship", 380, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcFace_type = new entity("IfcFace", 386, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcFaceBound_type = new entity("IfcFaceBound", 388, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcFaceOuterBound_type = new entity("IfcFaceOuterBound", 389, IFC4_IfcFaceBound_type);
    IFC4_IfcFaceSurface_type = new entity("IfcFaceSurface", 390, IFC4_IfcFace_type);
    IFC4_IfcFailureConnectionCondition_type = new entity("IfcFailureConnectionCondition", 393, IFC4_IfcStructuralConnectionCondition_type);
    IFC4_IfcFillAreaStyle_type = new entity("IfcFillAreaStyle", 403, IFC4_IfcPresentationStyle_type);
    IFC4_IfcGeometricRepresentationContext_type = new entity("IfcGeometricRepresentationContext", 453, IFC4_IfcRepresentationContext_type);
    IFC4_IfcGeometricRepresentationItem_type = new entity("IfcGeometricRepresentationItem", 454, IFC4_IfcRepresentationItem_type);
    IFC4_IfcGeometricRepresentationSubContext_type = new entity("IfcGeometricRepresentationSubContext", 455, IFC4_IfcGeometricRepresentationContext_type);
    IFC4_IfcGeometricSet_type = new entity("IfcGeometricSet", 456, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcGridPlacement_type = new entity("IfcGridPlacement", 462, IFC4_IfcObjectPlacement_type);
    IFC4_IfcHalfSpaceSolid_type = new entity("IfcHalfSpaceSolid", 466, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcImageTexture_type = new entity("IfcImageTexture", 478, IFC4_IfcSurfaceTexture_type);
    IFC4_IfcIndexedColourMap_type = new entity("IfcIndexedColourMap", 479, IFC4_IfcPresentationItem_type);
    IFC4_IfcIndexedTextureMap_type = new entity("IfcIndexedTextureMap", 481, IFC4_IfcTextureCoordinate_type);
    IFC4_IfcIndexedTriangleTextureMap_type = new entity("IfcIndexedTriangleTextureMap", 482, IFC4_IfcIndexedTextureMap_type);
    IFC4_IfcIrregularTimeSeries_type = new entity("IfcIrregularTimeSeries", 493, IFC4_IfcTimeSeries_type);
    IFC4_IfcLagTime_type = new entity("IfcLagTime", 506, IFC4_IfcSchedulingTime_type);
    IFC4_IfcLightSource_type = new entity("IfcLightSource", 525, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcLightSourceAmbient_type = new entity("IfcLightSourceAmbient", 526, IFC4_IfcLightSource_type);
    IFC4_IfcLightSourceDirectional_type = new entity("IfcLightSourceDirectional", 527, IFC4_IfcLightSource_type);
    IFC4_IfcLightSourceGoniometric_type = new entity("IfcLightSourceGoniometric", 528, IFC4_IfcLightSource_type);
    IFC4_IfcLightSourcePositional_type = new entity("IfcLightSourcePositional", 529, IFC4_IfcLightSource_type);
    IFC4_IfcLightSourceSpot_type = new entity("IfcLightSourceSpot", 530, IFC4_IfcLightSourcePositional_type);
    IFC4_IfcLocalPlacement_type = new entity("IfcLocalPlacement", 538, IFC4_IfcObjectPlacement_type);
    IFC4_IfcLoop_type = new entity("IfcLoop", 541, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcMappedItem_type = new entity("IfcMappedItem", 550, IFC4_IfcRepresentationItem_type);
    IFC4_IfcMaterial_type = new entity("IfcMaterial", 555, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialConstituent_type = new entity("IfcMaterialConstituent", 557, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialConstituentSet_type = new entity("IfcMaterialConstituentSet", 558, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialDefinitionRepresentation_type = new entity("IfcMaterialDefinitionRepresentation", 560, IFC4_IfcProductRepresentation_type);
    IFC4_IfcMaterialLayerSetUsage_type = new entity("IfcMaterialLayerSetUsage", 563, IFC4_IfcMaterialUsageDefinition_type);
    IFC4_IfcMaterialProfileSetUsage_type = new entity("IfcMaterialProfileSetUsage", 568, IFC4_IfcMaterialUsageDefinition_type);
    IFC4_IfcMaterialProfileSetUsageTapering_type = new entity("IfcMaterialProfileSetUsageTapering", 569, IFC4_IfcMaterialProfileSetUsage_type);
    IFC4_IfcMaterialProperties_type = new entity("IfcMaterialProperties", 571, IFC4_IfcExtendedProperties_type);
    IFC4_IfcMaterialRelationship_type = new entity("IfcMaterialRelationship", 572, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcMirroredProfileDef_type = new entity("IfcMirroredProfileDef", 589, IFC4_IfcDerivedProfileDef_type);
    IFC4_IfcObjectDefinition_type = new entity("IfcObjectDefinition", 612, IFC4_IfcRoot_type);
    IFC4_IfcOpenShell_type = new entity("IfcOpenShell", 625, IFC4_IfcConnectedFaceSet_type);
    IFC4_IfcOrganizationRelationship_type = new entity("IfcOrganizationRelationship", 627, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcOrientedEdge_type = new entity("IfcOrientedEdge", 628, IFC4_IfcEdge_type);
    IFC4_IfcParameterizedProfileDef_type = new entity("IfcParameterizedProfileDef", 634, IFC4_IfcProfileDef_type);
    IFC4_IfcPath_type = new entity("IfcPath", 636, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcPhysicalComplexQuantity_type = new entity("IfcPhysicalComplexQuantity", 647, IFC4_IfcPhysicalQuantity_type);
    IFC4_IfcPixelTexture_type = new entity("IfcPixelTexture", 661, IFC4_IfcSurfaceTexture_type);
    IFC4_IfcPlacement_type = new entity("IfcPlacement", 662, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcPlanarExtent_type = new entity("IfcPlanarExtent", 664, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcPoint_type = new entity("IfcPoint", 672, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcPointOnCurve_type = new entity("IfcPointOnCurve", 673, IFC4_IfcPoint_type);
    IFC4_IfcPointOnSurface_type = new entity("IfcPointOnSurface", 674, IFC4_IfcPoint_type);
    IFC4_IfcPolyLoop_type = new entity("IfcPolyLoop", 678, IFC4_IfcLoop_type);
    IFC4_IfcPolygonalBoundedHalfSpace_type = new entity("IfcPolygonalBoundedHalfSpace", 676, IFC4_IfcHalfSpaceSolid_type);
    IFC4_IfcPreDefinedItem_type = new entity("IfcPreDefinedItem", 688, IFC4_IfcPresentationItem_type);
    IFC4_IfcPreDefinedProperties_type = new entity("IfcPreDefinedProperties", 689, IFC4_IfcPropertyAbstraction_type);
    IFC4_IfcPreDefinedTextFont_type = new entity("IfcPreDefinedTextFont", 691, IFC4_IfcPreDefinedItem_type);
    IFC4_IfcProductDefinitionShape_type = new entity("IfcProductDefinitionShape", 706, IFC4_IfcProductRepresentation_type);
    IFC4_IfcProfileProperties_type = new entity("IfcProfileProperties", 711, IFC4_IfcExtendedProperties_type);
    IFC4_IfcProperty_type = new entity("IfcProperty", 721, IFC4_IfcPropertyAbstraction_type);
    IFC4_IfcPropertyDefinition_type = new entity("IfcPropertyDefinition", 724, IFC4_IfcRoot_type);
    IFC4_IfcPropertyDependencyRelationship_type = new entity("IfcPropertyDependencyRelationship", 725, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcPropertySetDefinition_type = new entity("IfcPropertySetDefinition", 731, IFC4_IfcPropertyDefinition_type);
    IFC4_IfcPropertyTemplateDefinition_type = new entity("IfcPropertyTemplateDefinition", 739, IFC4_IfcPropertyDefinition_type);
    IFC4_IfcQuantitySet_type = new entity("IfcQuantitySet", 753, IFC4_IfcPropertySetDefinition_type);
    IFC4_IfcRectangleProfileDef_type = new entity("IfcRectangleProfileDef", 772, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcRegularTimeSeries_type = new entity("IfcRegularTimeSeries", 779, IFC4_IfcTimeSeries_type);
    IFC4_IfcReinforcementBarProperties_type = new entity("IfcReinforcementBarProperties", 780, IFC4_IfcPreDefinedProperties_type);
    IFC4_IfcRelationship_type = new entity("IfcRelationship", 808, IFC4_IfcRoot_type);
    IFC4_IfcResourceApprovalRelationship_type = new entity("IfcResourceApprovalRelationship", 846, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcResourceConstraintRelationship_type = new entity("IfcResourceConstraintRelationship", 847, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcResourceTime_type = new entity("IfcResourceTime", 851, IFC4_IfcSchedulingTime_type);
    IFC4_IfcRoundedRectangleProfileDef_type = new entity("IfcRoundedRectangleProfileDef", 865, IFC4_IfcRectangleProfileDef_type);
    IFC4_IfcSectionProperties_type = new entity("IfcSectionProperties", 873, IFC4_IfcPreDefinedProperties_type);
    IFC4_IfcSectionReinforcementProperties_type = new entity("IfcSectionReinforcementProperties", 874, IFC4_IfcPreDefinedProperties_type);
    IFC4_IfcSectionedSpine_type = new entity("IfcSectionedSpine", 871, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcShellBasedSurfaceModel_type = new entity("IfcShellBasedSurfaceModel", 889, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcSimpleProperty_type = new entity("IfcSimpleProperty", 890, IFC4_IfcProperty_type);
    IFC4_IfcSlippageConnectionCondition_type = new entity("IfcSlippageConnectionCondition", 904, IFC4_IfcStructuralConnectionCondition_type);
    IFC4_IfcSolidModel_type = new entity("IfcSolidModel", 909, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcStructuralLoadLinearForce_type = new entity("IfcStructuralLoadLinearForce", 964, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStructuralLoadPlanarForce_type = new entity("IfcStructuralLoadPlanarForce", 966, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStructuralLoadSingleDisplacement_type = new entity("IfcStructuralLoadSingleDisplacement", 967, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStructuralLoadSingleDisplacementDistortion_type = new entity("IfcStructuralLoadSingleDisplacementDistortion", 968, IFC4_IfcStructuralLoadSingleDisplacement_type);
    IFC4_IfcStructuralLoadSingleForce_type = new entity("IfcStructuralLoadSingleForce", 969, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStructuralLoadSingleForceWarping_type = new entity("IfcStructuralLoadSingleForceWarping", 970, IFC4_IfcStructuralLoadSingleForce_type);
    IFC4_IfcSubedge_type = new entity("IfcSubedge", 994, IFC4_IfcEdge_type);
    IFC4_IfcSurface_type = new entity("IfcSurface", 995, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcSurfaceStyleRendering_type = new entity("IfcSurfaceStyleRendering", 1008, IFC4_IfcSurfaceStyleShading_type);
    IFC4_IfcSweptAreaSolid_type = new entity("IfcSweptAreaSolid", 1012, IFC4_IfcSolidModel_type);
    IFC4_IfcSweptDiskSolid_type = new entity("IfcSweptDiskSolid", 1013, IFC4_IfcSolidModel_type);
    IFC4_IfcSweptDiskSolidPolygonal_type = new entity("IfcSweptDiskSolidPolygonal", 1014, IFC4_IfcSweptDiskSolid_type);
    IFC4_IfcSweptSurface_type = new entity("IfcSweptSurface", 1015, IFC4_IfcSurface_type);
    IFC4_IfcTShapeProfileDef_type = new entity("IfcTShapeProfileDef", 1094, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcTessellatedItem_type = new entity("IfcTessellatedItem", 1045, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcTextLiteral_type = new entity("IfcTextLiteral", 1051, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcTextLiteralWithExtent_type = new entity("IfcTextLiteralWithExtent", 1052, IFC4_IfcTextLiteral_type);
    IFC4_IfcTextStyleFontModel_type = new entity("IfcTextStyleFontModel", 1055, IFC4_IfcPreDefinedTextFont_type);
    IFC4_IfcTrapeziumProfileDef_type = new entity("IfcTrapeziumProfileDef", 1089, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcTypeObject_type = new entity("IfcTypeObject", 1098, IFC4_IfcObjectDefinition_type);
    IFC4_IfcTypeProcess_type = new entity("IfcTypeProcess", 1099, IFC4_IfcTypeObject_type);
    IFC4_IfcTypeProduct_type = new entity("IfcTypeProduct", 1100, IFC4_IfcTypeObject_type);
    IFC4_IfcTypeResource_type = new entity("IfcTypeResource", 1101, IFC4_IfcTypeObject_type);
    IFC4_IfcUShapeProfileDef_type = new entity("IfcUShapeProfileDef", 1112, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcVector_type = new entity("IfcVector", 1118, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcVertexLoop_type = new entity("IfcVertexLoop", 1121, IFC4_IfcLoop_type);
    IFC4_IfcWindowStyle_type = new entity("IfcWindowStyle", 1149, IFC4_IfcTypeProduct_type);
    IFC4_IfcZShapeProfileDef_type = new entity("IfcZShapeProfileDef", 1164, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcAdvancedFace_type = new entity("IfcAdvancedFace", 16, IFC4_IfcFaceSurface_type);
    IFC4_IfcAnnotationFillArea_type = new entity("IfcAnnotationFillArea", 34, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcAsymmetricIShapeProfileDef_type = new entity("IfcAsymmetricIShapeProfileDef", 49, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcAxis1Placement_type = new entity("IfcAxis1Placement", 53, IFC4_IfcPlacement_type);
    IFC4_IfcAxis2Placement2D_type = new entity("IfcAxis2Placement2D", 55, IFC4_IfcPlacement_type);
    IFC4_IfcAxis2Placement3D_type = new entity("IfcAxis2Placement3D", 56, IFC4_IfcPlacement_type);
    IFC4_IfcBooleanResult_type = new entity("IfcBooleanResult", 73, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcBoundedSurface_type = new entity("IfcBoundedSurface", 81, IFC4_IfcSurface_type);
    IFC4_IfcBoundingBox_type = new entity("IfcBoundingBox", 82, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcBoxedHalfSpace_type = new entity("IfcBoxedHalfSpace", 84, IFC4_IfcHalfSpaceSolid_type);
    IFC4_IfcCShapeProfileDef_type = new entity("IfcCShapeProfileDef", 231, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcCartesianPoint_type = new entity("IfcCartesianPoint", 119, IFC4_IfcPoint_type);
    IFC4_IfcCartesianPointList_type = new entity("IfcCartesianPointList", 120, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcCartesianPointList2D_type = new entity("IfcCartesianPointList2D", 121, IFC4_IfcCartesianPointList_type);
    IFC4_IfcCartesianPointList3D_type = new entity("IfcCartesianPointList3D", 122, IFC4_IfcCartesianPointList_type);
    IFC4_IfcCartesianTransformationOperator_type = new entity("IfcCartesianTransformationOperator", 123, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcCartesianTransformationOperator2D_type = new entity("IfcCartesianTransformationOperator2D", 124, IFC4_IfcCartesianTransformationOperator_type);
    IFC4_IfcCartesianTransformationOperator2DnonUniform_type = new entity("IfcCartesianTransformationOperator2DnonUniform", 125, IFC4_IfcCartesianTransformationOperator2D_type);
    IFC4_IfcCartesianTransformationOperator3D_type = new entity("IfcCartesianTransformationOperator3D", 126, IFC4_IfcCartesianTransformationOperator_type);
    IFC4_IfcCartesianTransformationOperator3DnonUniform_type = new entity("IfcCartesianTransformationOperator3DnonUniform", 127, IFC4_IfcCartesianTransformationOperator3D_type);
    IFC4_IfcCircleProfileDef_type = new entity("IfcCircleProfileDef", 138, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcClosedShell_type = new entity("IfcClosedShell", 145, IFC4_IfcConnectedFaceSet_type);
    IFC4_IfcColourRgb_type = new entity("IfcColourRgb", 151, IFC4_IfcColourSpecification_type);
    IFC4_IfcComplexProperty_type = new entity("IfcComplexProperty", 162, IFC4_IfcProperty_type);
    IFC4_IfcCompositeCurveSegment_type = new entity("IfcCompositeCurveSegment", 167, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcConstructionResourceType_type = new entity("IfcConstructionResourceType", 197, IFC4_IfcTypeResource_type);
    IFC4_IfcContext_type = new entity("IfcContext", 198, IFC4_IfcObjectDefinition_type);
    IFC4_IfcCrewResourceType_type = new entity("IfcCrewResourceType", 226, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcCsgPrimitive3D_type = new entity("IfcCsgPrimitive3D", 228, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcCsgSolid_type = new entity("IfcCsgSolid", 230, IFC4_IfcSolidModel_type);
    IFC4_IfcCurve_type = new entity("IfcCurve", 237, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcCurveBoundedPlane_type = new entity("IfcCurveBoundedPlane", 238, IFC4_IfcBoundedSurface_type);
    IFC4_IfcCurveBoundedSurface_type = new entity("IfcCurveBoundedSurface", 239, IFC4_IfcBoundedSurface_type);
    IFC4_IfcDirection_type = new entity("IfcDirection", 267, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcDoorStyle_type = new entity("IfcDoorStyle", 298, IFC4_IfcTypeProduct_type);
    IFC4_IfcEdgeLoop_type = new entity("IfcEdgeLoop", 320, IFC4_IfcLoop_type);
    IFC4_IfcElementQuantity_type = new entity("IfcElementQuantity", 353, IFC4_IfcQuantitySet_type);
    IFC4_IfcElementType_type = new entity("IfcElementType", 354, IFC4_IfcTypeProduct_type);
    IFC4_IfcElementarySurface_type = new entity("IfcElementarySurface", 346, IFC4_IfcSurface_type);
    IFC4_IfcEllipseProfileDef_type = new entity("IfcEllipseProfileDef", 356, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcEventType_type = new entity("IfcEventType", 372, IFC4_IfcTypeProcess_type);
    IFC4_IfcExtrudedAreaSolid_type = new entity("IfcExtrudedAreaSolid", 384, IFC4_IfcSweptAreaSolid_type);
    IFC4_IfcExtrudedAreaSolidTapered_type = new entity("IfcExtrudedAreaSolidTapered", 385, IFC4_IfcExtrudedAreaSolid_type);
    IFC4_IfcFaceBasedSurfaceModel_type = new entity("IfcFaceBasedSurfaceModel", 387, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcFillAreaStyleHatching_type = new entity("IfcFillAreaStyleHatching", 404, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcFillAreaStyleTiles_type = new entity("IfcFillAreaStyleTiles", 405, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcFixedReferenceSweptAreaSolid_type = new entity("IfcFixedReferenceSweptAreaSolid", 413, IFC4_IfcSweptAreaSolid_type);
    IFC4_IfcFurnishingElementType_type = new entity("IfcFurnishingElementType", 444, IFC4_IfcElementType_type);
    IFC4_IfcFurnitureType_type = new entity("IfcFurnitureType", 446, IFC4_IfcFurnishingElementType_type);
    IFC4_IfcGeographicElementType_type = new entity("IfcGeographicElementType", 449, IFC4_IfcElementType_type);
    IFC4_IfcGeometricCurveSet_type = new entity("IfcGeometricCurveSet", 451, IFC4_IfcGeometricSet_type);
    IFC4_IfcIShapeProfileDef_type = new entity("IfcIShapeProfileDef", 495, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcLShapeProfileDef_type = new entity("IfcLShapeProfileDef", 542, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcLaborResourceType_type = new entity("IfcLaborResourceType", 504, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcLine_type = new entity("IfcLine", 531, IFC4_IfcCurve_type);
    IFC4_IfcManifoldSolidBrep_type = new entity("IfcManifoldSolidBrep", 548, IFC4_IfcSolidModel_type);
    IFC4_IfcObject_type = new entity("IfcObject", 611, IFC4_IfcObjectDefinition_type);
    IFC4_IfcOffsetCurve2D_type = new entity("IfcOffsetCurve2D", 620, IFC4_IfcCurve_type);
    IFC4_IfcOffsetCurve3D_type = new entity("IfcOffsetCurve3D", 621, IFC4_IfcCurve_type);
    IFC4_IfcPcurve_type = new entity("IfcPcurve", 637, IFC4_IfcCurve_type);
    IFC4_IfcPlanarBox_type = new entity("IfcPlanarBox", 663, IFC4_IfcPlanarExtent_type);
    IFC4_IfcPlane_type = new entity("IfcPlane", 666, IFC4_IfcElementarySurface_type);
    IFC4_IfcPreDefinedColour_type = new entity("IfcPreDefinedColour", 686, IFC4_IfcPreDefinedItem_type);
    IFC4_IfcPreDefinedCurveFont_type = new entity("IfcPreDefinedCurveFont", 687, IFC4_IfcPreDefinedItem_type);
    IFC4_IfcPreDefinedPropertySet_type = new entity("IfcPreDefinedPropertySet", 690, IFC4_IfcPropertySetDefinition_type);
    IFC4_IfcProcedureType_type = new entity("IfcProcedureType", 701, IFC4_IfcTypeProcess_type);
    IFC4_IfcProcess_type = new entity("IfcProcess", 703, IFC4_IfcObject_type);
    IFC4_IfcProduct_type = new entity("IfcProduct", 705, IFC4_IfcObject_type);
    IFC4_IfcProject_type = new entity("IfcProject", 713, IFC4_IfcContext_type);
    IFC4_IfcProjectLibrary_type = new entity("IfcProjectLibrary", 718, IFC4_IfcContext_type);
    IFC4_IfcPropertyBoundedValue_type = new entity("IfcPropertyBoundedValue", 723, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyEnumeratedValue_type = new entity("IfcPropertyEnumeratedValue", 726, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyListValue_type = new entity("IfcPropertyListValue", 728, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyReferenceValue_type = new entity("IfcPropertyReferenceValue", 729, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertySet_type = new entity("IfcPropertySet", 730, IFC4_IfcPropertySetDefinition_type);
    IFC4_IfcPropertySetTemplate_type = new entity("IfcPropertySetTemplate", 734, IFC4_IfcPropertyTemplateDefinition_type);
    IFC4_IfcPropertySingleValue_type = new entity("IfcPropertySingleValue", 736, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyTableValue_type = new entity("IfcPropertyTableValue", 737, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyTemplate_type = new entity("IfcPropertyTemplate", 738, IFC4_IfcPropertyTemplateDefinition_type);
    IFC4_IfcProxy_type = new entity("IfcProxy", 746, IFC4_IfcProduct_type);
    IFC4_IfcRectangleHollowProfileDef_type = new entity("IfcRectangleHollowProfileDef", 771, IFC4_IfcRectangleProfileDef_type);
    IFC4_IfcRectangularPyramid_type = new entity("IfcRectangularPyramid", 773, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcRectangularTrimmedSurface_type = new entity("IfcRectangularTrimmedSurface", 774, IFC4_IfcBoundedSurface_type);
    IFC4_IfcReinforcementDefinitionProperties_type = new entity("IfcReinforcementDefinitionProperties", 781, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcRelAssigns_type = new entity("IfcRelAssigns", 793, IFC4_IfcRelationship_type);
    IFC4_IfcRelAssignsToActor_type = new entity("IfcRelAssignsToActor", 794, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToControl_type = new entity("IfcRelAssignsToControl", 795, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToGroup_type = new entity("IfcRelAssignsToGroup", 796, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToGroupByFactor_type = new entity("IfcRelAssignsToGroupByFactor", 797, IFC4_IfcRelAssignsToGroup_type);
    IFC4_IfcRelAssignsToProcess_type = new entity("IfcRelAssignsToProcess", 798, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToProduct_type = new entity("IfcRelAssignsToProduct", 799, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToResource_type = new entity("IfcRelAssignsToResource", 800, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssociates_type = new entity("IfcRelAssociates", 801, IFC4_IfcRelationship_type);
    IFC4_IfcRelAssociatesApproval_type = new entity("IfcRelAssociatesApproval", 802, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesClassification_type = new entity("IfcRelAssociatesClassification", 803, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesConstraint_type = new entity("IfcRelAssociatesConstraint", 804, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesDocument_type = new entity("IfcRelAssociatesDocument", 805, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesLibrary_type = new entity("IfcRelAssociatesLibrary", 806, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesMaterial_type = new entity("IfcRelAssociatesMaterial", 807, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelConnects_type = new entity("IfcRelConnects", 809, IFC4_IfcRelationship_type);
    IFC4_IfcRelConnectsElements_type = new entity("IfcRelConnectsElements", 810, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsPathElements_type = new entity("IfcRelConnectsPathElements", 811, IFC4_IfcRelConnectsElements_type);
    IFC4_IfcRelConnectsPortToElement_type = new entity("IfcRelConnectsPortToElement", 813, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsPorts_type = new entity("IfcRelConnectsPorts", 812, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsStructuralActivity_type = new entity("IfcRelConnectsStructuralActivity", 814, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsStructuralMember_type = new entity("IfcRelConnectsStructuralMember", 815, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsWithEccentricity_type = new entity("IfcRelConnectsWithEccentricity", 816, IFC4_IfcRelConnectsStructuralMember_type);
    IFC4_IfcRelConnectsWithRealizingElements_type = new entity("IfcRelConnectsWithRealizingElements", 817, IFC4_IfcRelConnectsElements_type);
    IFC4_IfcRelContainedInSpatialStructure_type = new entity("IfcRelContainedInSpatialStructure", 818, IFC4_IfcRelConnects_type);
    IFC4_IfcRelCoversBldgElements_type = new entity("IfcRelCoversBldgElements", 819, IFC4_IfcRelConnects_type);
    IFC4_IfcRelCoversSpaces_type = new entity("IfcRelCoversSpaces", 820, IFC4_IfcRelConnects_type);
    IFC4_IfcRelDeclares_type = new entity("IfcRelDeclares", 821, IFC4_IfcRelationship_type);
    IFC4_IfcRelDecomposes_type = new entity("IfcRelDecomposes", 822, IFC4_IfcRelationship_type);
    IFC4_IfcRelDefines_type = new entity("IfcRelDefines", 823, IFC4_IfcRelationship_type);
    IFC4_IfcRelDefinesByObject_type = new entity("IfcRelDefinesByObject", 824, IFC4_IfcRelDefines_type);
    IFC4_IfcRelDefinesByProperties_type = new entity("IfcRelDefinesByProperties", 825, IFC4_IfcRelDefines_type);
    IFC4_IfcRelDefinesByTemplate_type = new entity("IfcRelDefinesByTemplate", 826, IFC4_IfcRelDefines_type);
    IFC4_IfcRelDefinesByType_type = new entity("IfcRelDefinesByType", 827, IFC4_IfcRelDefines_type);
    IFC4_IfcRelFillsElement_type = new entity("IfcRelFillsElement", 828, IFC4_IfcRelConnects_type);
    IFC4_IfcRelFlowControlElements_type = new entity("IfcRelFlowControlElements", 829, IFC4_IfcRelConnects_type);
    IFC4_IfcRelInterferesElements_type = new entity("IfcRelInterferesElements", 830, IFC4_IfcRelConnects_type);
    IFC4_IfcRelNests_type = new entity("IfcRelNests", 831, IFC4_IfcRelDecomposes_type);
    IFC4_IfcRelProjectsElement_type = new entity("IfcRelProjectsElement", 832, IFC4_IfcRelDecomposes_type);
    IFC4_IfcRelReferencedInSpatialStructure_type = new entity("IfcRelReferencedInSpatialStructure", 833, IFC4_IfcRelConnects_type);
    IFC4_IfcRelSequence_type = new entity("IfcRelSequence", 834, IFC4_IfcRelConnects_type);
    IFC4_IfcRelServicesBuildings_type = new entity("IfcRelServicesBuildings", 835, IFC4_IfcRelConnects_type);
    IFC4_IfcRelSpaceBoundary_type = new entity("IfcRelSpaceBoundary", 836, IFC4_IfcRelConnects_type);
    IFC4_IfcRelSpaceBoundary1stLevel_type = new entity("IfcRelSpaceBoundary1stLevel", 837, IFC4_IfcRelSpaceBoundary_type);
    IFC4_IfcRelSpaceBoundary2ndLevel_type = new entity("IfcRelSpaceBoundary2ndLevel", 838, IFC4_IfcRelSpaceBoundary1stLevel_type);
    IFC4_IfcRelVoidsElement_type = new entity("IfcRelVoidsElement", 839, IFC4_IfcRelDecomposes_type);
    IFC4_IfcReparametrisedCompositeCurveSegment_type = new entity("IfcReparametrisedCompositeCurveSegment", 840, IFC4_IfcCompositeCurveSegment_type);
    IFC4_IfcResource_type = new entity("IfcResource", 845, IFC4_IfcObject_type);
    IFC4_IfcRevolvedAreaSolid_type = new entity("IfcRevolvedAreaSolid", 852, IFC4_IfcSweptAreaSolid_type);
    IFC4_IfcRevolvedAreaSolidTapered_type = new entity("IfcRevolvedAreaSolidTapered", 853, IFC4_IfcRevolvedAreaSolid_type);
    IFC4_IfcRightCircularCone_type = new entity("IfcRightCircularCone", 854, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcRightCircularCylinder_type = new entity("IfcRightCircularCylinder", 855, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcSimplePropertyTemplate_type = new entity("IfcSimplePropertyTemplate", 891, IFC4_IfcPropertyTemplate_type);
    IFC4_IfcSpatialElement_type = new entity("IfcSpatialElement", 922, IFC4_IfcProduct_type);
    IFC4_IfcSpatialElementType_type = new entity("IfcSpatialElementType", 923, IFC4_IfcTypeProduct_type);
    IFC4_IfcSpatialStructureElement_type = new entity("IfcSpatialStructureElement", 924, IFC4_IfcSpatialElement_type);
    IFC4_IfcSpatialStructureElementType_type = new entity("IfcSpatialStructureElementType", 925, IFC4_IfcSpatialElementType_type);
    IFC4_IfcSpatialZone_type = new entity("IfcSpatialZone", 926, IFC4_IfcSpatialElement_type);
    IFC4_IfcSpatialZoneType_type = new entity("IfcSpatialZoneType", 927, IFC4_IfcSpatialElementType_type);
    IFC4_IfcSphere_type = new entity("IfcSphere", 933, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcStructuralActivity_type = new entity("IfcStructuralActivity", 946, IFC4_IfcProduct_type);
    IFC4_IfcStructuralItem_type = new entity("IfcStructuralItem", 958, IFC4_IfcProduct_type);
    IFC4_IfcStructuralMember_type = new entity("IfcStructuralMember", 973, IFC4_IfcStructuralItem_type);
    IFC4_IfcStructuralReaction_type = new entity("IfcStructuralReaction", 978, IFC4_IfcStructuralActivity_type);
    IFC4_IfcStructuralSurfaceMember_type = new entity("IfcStructuralSurfaceMember", 983, IFC4_IfcStructuralMember_type);
    IFC4_IfcStructuralSurfaceMemberVarying_type = new entity("IfcStructuralSurfaceMemberVarying", 985, IFC4_IfcStructuralSurfaceMember_type);
    IFC4_IfcStructuralSurfaceReaction_type = new entity("IfcStructuralSurfaceReaction", 986, IFC4_IfcStructuralReaction_type);
    IFC4_IfcSubContractResourceType_type = new entity("IfcSubContractResourceType", 992, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcSurfaceCurveSweptAreaSolid_type = new entity("IfcSurfaceCurveSweptAreaSolid", 996, IFC4_IfcSweptAreaSolid_type);
    IFC4_IfcSurfaceOfLinearExtrusion_type = new entity("IfcSurfaceOfLinearExtrusion", 999, IFC4_IfcSweptSurface_type);
    IFC4_IfcSurfaceOfRevolution_type = new entity("IfcSurfaceOfRevolution", 1000, IFC4_IfcSweptSurface_type);
    IFC4_IfcSystemFurnitureElementType_type = new entity("IfcSystemFurnitureElementType", 1021, IFC4_IfcFurnishingElementType_type);
    IFC4_IfcTask_type = new entity("IfcTask", 1029, IFC4_IfcProcess_type);
    IFC4_IfcTaskType_type = new entity("IfcTaskType", 1033, IFC4_IfcTypeProcess_type);
    IFC4_IfcTessellatedFaceSet_type = new entity("IfcTessellatedFaceSet", 1044, IFC4_IfcTessellatedItem_type);
    IFC4_IfcTransportElementType_type = new entity("IfcTransportElementType", 1087, IFC4_IfcElementType_type);
    IFC4_IfcTriangulatedFaceSet_type = new entity("IfcTriangulatedFaceSet", 1090, IFC4_IfcTessellatedFaceSet_type);
    IFC4_IfcWindowLiningProperties_type = new entity("IfcWindowLiningProperties", 1144, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcWindowPanelProperties_type = new entity("IfcWindowPanelProperties", 1147, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcActor_type = new entity("IfcActor", 6, IFC4_IfcObject_type);
    IFC4_IfcAdvancedBrep_type = new entity("IfcAdvancedBrep", 14, IFC4_IfcManifoldSolidBrep_type);
    IFC4_IfcAdvancedBrepWithVoids_type = new entity("IfcAdvancedBrepWithVoids", 15, IFC4_IfcAdvancedBrep_type);
    IFC4_IfcAnnotation_type = new entity("IfcAnnotation", 33, IFC4_IfcProduct_type);
    IFC4_IfcBSplineSurface_type = new entity("IfcBSplineSurface", 88, IFC4_IfcBoundedSurface_type);
    IFC4_IfcBSplineSurfaceWithKnots_type = new entity("IfcBSplineSurfaceWithKnots", 90, IFC4_IfcBSplineSurface_type);
    IFC4_IfcBlock_type = new entity("IfcBlock", 65, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcBooleanClippingResult_type = new entity("IfcBooleanClippingResult", 70, IFC4_IfcBooleanResult_type);
    IFC4_IfcBoundedCurve_type = new entity("IfcBoundedCurve", 80, IFC4_IfcCurve_type);
    IFC4_IfcBuilding_type = new entity("IfcBuilding", 91, IFC4_IfcSpatialStructureElement_type);
    IFC4_IfcBuildingElementType_type = new entity("IfcBuildingElementType", 99, IFC4_IfcElementType_type);
    IFC4_IfcBuildingStorey_type = new entity("IfcBuildingStorey", 100, IFC4_IfcSpatialStructureElement_type);
    IFC4_IfcChimneyType_type = new entity("IfcChimneyType", 134, IFC4_IfcBuildingElementType_type);
    IFC4_IfcCircleHollowProfileDef_type = new entity("IfcCircleHollowProfileDef", 137, IFC4_IfcCircleProfileDef_type);
    IFC4_IfcCivilElementType_type = new entity("IfcCivilElementType", 140, IFC4_IfcElementType_type);
    IFC4_IfcColumnType_type = new entity("IfcColumnType", 156, IFC4_IfcBuildingElementType_type);
    IFC4_IfcComplexPropertyTemplate_type = new entity("IfcComplexPropertyTemplate", 163, IFC4_IfcPropertyTemplate_type);
    IFC4_IfcCompositeCurve_type = new entity("IfcCompositeCurve", 165, IFC4_IfcBoundedCurve_type);
    IFC4_IfcCompositeCurveOnSurface_type = new entity("IfcCompositeCurveOnSurface", 166, IFC4_IfcCompositeCurve_type);
    IFC4_IfcConic_type = new entity("IfcConic", 176, IFC4_IfcCurve_type);
    IFC4_IfcConstructionEquipmentResourceType_type = new entity("IfcConstructionEquipmentResourceType", 188, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcConstructionMaterialResourceType_type = new entity("IfcConstructionMaterialResourceType", 191, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcConstructionProductResourceType_type = new entity("IfcConstructionProductResourceType", 194, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcConstructionResource_type = new entity("IfcConstructionResource", 196, IFC4_IfcResource_type);
    IFC4_IfcControl_type = new entity("IfcControl", 201, IFC4_IfcObject_type);
    IFC4_IfcCostItem_type = new entity("IfcCostItem", 216, IFC4_IfcControl_type);
    IFC4_IfcCostSchedule_type = new entity("IfcCostSchedule", 218, IFC4_IfcControl_type);
    IFC4_IfcCoveringType_type = new entity("IfcCoveringType", 223, IFC4_IfcBuildingElementType_type);
    IFC4_IfcCrewResource_type = new entity("IfcCrewResource", 225, IFC4_IfcConstructionResource_type);
    IFC4_IfcCurtainWallType_type = new entity("IfcCurtainWallType", 234, IFC4_IfcBuildingElementType_type);
    IFC4_IfcCylindricalSurface_type = new entity("IfcCylindricalSurface", 249, IFC4_IfcElementarySurface_type);
    IFC4_IfcDistributionElementType_type = new entity("IfcDistributionElementType", 279, IFC4_IfcElementType_type);
    IFC4_IfcDistributionFlowElementType_type = new entity("IfcDistributionFlowElementType", 281, IFC4_IfcDistributionElementType_type);
    IFC4_IfcDoorLiningProperties_type = new entity("IfcDoorLiningProperties", 293, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcDoorPanelProperties_type = new entity("IfcDoorPanelProperties", 296, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcDoorType_type = new entity("IfcDoorType", 301, IFC4_IfcBuildingElementType_type);
    IFC4_IfcDraughtingPreDefinedColour_type = new entity("IfcDraughtingPreDefinedColour", 305, IFC4_IfcPreDefinedColour_type);
    IFC4_IfcDraughtingPreDefinedCurveFont_type = new entity("IfcDraughtingPreDefinedCurveFont", 306, IFC4_IfcPreDefinedCurveFont_type);
    IFC4_IfcElement_type = new entity("IfcElement", 345, IFC4_IfcProduct_type);
    IFC4_IfcElementAssembly_type = new entity("IfcElementAssembly", 347, IFC4_IfcElement_type);
    IFC4_IfcElementAssemblyType_type = new entity("IfcElementAssemblyType", 348, IFC4_IfcElementType_type);
    IFC4_IfcElementComponent_type = new entity("IfcElementComponent", 350, IFC4_IfcElement_type);
    IFC4_IfcElementComponentType_type = new entity("IfcElementComponentType", 351, IFC4_IfcElementType_type);
    IFC4_IfcEllipse_type = new entity("IfcEllipse", 355, IFC4_IfcConic_type);
    IFC4_IfcEnergyConversionDeviceType_type = new entity("IfcEnergyConversionDeviceType", 358, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcEngineType_type = new entity("IfcEngineType", 361, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcEvaporativeCoolerType_type = new entity("IfcEvaporativeCoolerType", 364, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcEvaporatorType_type = new entity("IfcEvaporatorType", 367, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcEvent_type = new entity("IfcEvent", 369, IFC4_IfcProcess_type);
    IFC4_IfcExternalSpatialStructureElement_type = new entity("IfcExternalSpatialStructureElement", 383, IFC4_IfcSpatialElement_type);
    IFC4_IfcFacetedBrep_type = new entity("IfcFacetedBrep", 391, IFC4_IfcManifoldSolidBrep_type);
    IFC4_IfcFacetedBrepWithVoids_type = new entity("IfcFacetedBrepWithVoids", 392, IFC4_IfcFacetedBrep_type);
    IFC4_IfcFastener_type = new entity("IfcFastener", 397, IFC4_IfcElementComponent_type);
    IFC4_IfcFastenerType_type = new entity("IfcFastenerType", 398, IFC4_IfcElementComponentType_type);
    IFC4_IfcFeatureElement_type = new entity("IfcFeatureElement", 400, IFC4_IfcElement_type);
    IFC4_IfcFeatureElementAddition_type = new entity("IfcFeatureElementAddition", 401, IFC4_IfcFeatureElement_type);
    IFC4_IfcFeatureElementSubtraction_type = new entity("IfcFeatureElementSubtraction", 402, IFC4_IfcFeatureElement_type);
    IFC4_IfcFlowControllerType_type = new entity("IfcFlowControllerType", 415, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowFittingType_type = new entity("IfcFlowFittingType", 418, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowMeterType_type = new entity("IfcFlowMeterType", 423, IFC4_IfcFlowControllerType_type);
    IFC4_IfcFlowMovingDeviceType_type = new entity("IfcFlowMovingDeviceType", 426, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowSegmentType_type = new entity("IfcFlowSegmentType", 428, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowStorageDeviceType_type = new entity("IfcFlowStorageDeviceType", 430, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowTerminalType_type = new entity("IfcFlowTerminalType", 432, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowTreatmentDeviceType_type = new entity("IfcFlowTreatmentDeviceType", 434, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFootingType_type = new entity("IfcFootingType", 439, IFC4_IfcBuildingElementType_type);
    IFC4_IfcFurnishingElement_type = new entity("IfcFurnishingElement", 443, IFC4_IfcElement_type);
    IFC4_IfcFurniture_type = new entity("IfcFurniture", 445, IFC4_IfcFurnishingElement_type);
    IFC4_IfcGeographicElement_type = new entity("IfcGeographicElement", 448, IFC4_IfcElement_type);
    IFC4_IfcGrid_type = new entity("IfcGrid", 460, IFC4_IfcProduct_type);
    IFC4_IfcGroup_type = new entity("IfcGroup", 465, IFC4_IfcObject_type);
    IFC4_IfcHeatExchangerType_type = new entity("IfcHeatExchangerType", 469, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcHumidifierType_type = new entity("IfcHumidifierType", 474, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcIndexedPolyCurve_type = new entity("IfcIndexedPolyCurve", 480, IFC4_IfcBoundedCurve_type);
    IFC4_IfcInterceptorType_type = new entity("IfcInterceptorType", 487, IFC4_IfcFlowTreatmentDeviceType_type);
    IFC4_IfcInventory_type = new entity("IfcInventory", 490, IFC4_IfcGroup_type);
    IFC4_IfcJunctionBoxType_type = new entity("IfcJunctionBoxType", 498, IFC4_IfcFlowFittingType_type);
    IFC4_IfcLaborResource_type = new entity("IfcLaborResource", 503, IFC4_IfcConstructionResource_type);
    IFC4_IfcLampType_type = new entity("IfcLampType", 508, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcLightFixtureType_type = new entity("IfcLightFixtureType", 522, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcMechanicalFastener_type = new entity("IfcMechanicalFastener", 577, IFC4_IfcElementComponent_type);
    IFC4_IfcMechanicalFastenerType_type = new entity("IfcMechanicalFastenerType", 578, IFC4_IfcElementComponentType_type);
    IFC4_IfcMedicalDeviceType_type = new entity("IfcMedicalDeviceType", 581, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcMemberType_type = new entity("IfcMemberType", 585, IFC4_IfcBuildingElementType_type);
    IFC4_IfcMotorConnectionType_type = new entity("IfcMotorConnectionType", 604, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcOccupant_type = new entity("IfcOccupant", 618, IFC4_IfcActor_type);
    IFC4_IfcOpeningElement_type = new entity("IfcOpeningElement", 622, IFC4_IfcFeatureElementSubtraction_type);
    IFC4_IfcOpeningStandardCase_type = new entity("IfcOpeningStandardCase", 624, IFC4_IfcOpeningElement_type);
    IFC4_IfcOutletType_type = new entity("IfcOutletType", 631, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcPerformanceHistory_type = new entity("IfcPerformanceHistory", 638, IFC4_IfcControl_type);
    IFC4_IfcPermeableCoveringProperties_type = new entity("IfcPermeableCoveringProperties", 641, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcPermit_type = new entity("IfcPermit", 642, IFC4_IfcControl_type);
    IFC4_IfcPileType_type = new entity("IfcPileType", 653, IFC4_IfcBuildingElementType_type);
    IFC4_IfcPipeFittingType_type = new entity("IfcPipeFittingType", 656, IFC4_IfcFlowFittingType_type);
    IFC4_IfcPipeSegmentType_type = new entity("IfcPipeSegmentType", 659, IFC4_IfcFlowSegmentType_type);
    IFC4_IfcPlateType_type = new entity("IfcPlateType", 670, IFC4_IfcBuildingElementType_type);
    IFC4_IfcPolyline_type = new entity("IfcPolyline", 677, IFC4_IfcBoundedCurve_type);
    IFC4_IfcPort_type = new entity("IfcPort", 679, IFC4_IfcProduct_type);
    IFC4_IfcProcedure_type = new entity("IfcProcedure", 700, IFC4_IfcProcess_type);
    IFC4_IfcProjectOrder_type = new entity("IfcProjectOrder", 719, IFC4_IfcControl_type);
    IFC4_IfcProjectionElement_type = new entity("IfcProjectionElement", 716, IFC4_IfcFeatureElementAddition_type);
    IFC4_IfcProtectiveDeviceType_type = new entity("IfcProtectiveDeviceType", 744, IFC4_IfcFlowControllerType_type);
    IFC4_IfcPumpType_type = new entity("IfcPumpType", 748, IFC4_IfcFlowMovingDeviceType_type);
    IFC4_IfcRailingType_type = new entity("IfcRailingType", 759, IFC4_IfcBuildingElementType_type);
    IFC4_IfcRampFlightType_type = new entity("IfcRampFlightType", 763, IFC4_IfcBuildingElementType_type);
    IFC4_IfcRampType_type = new entity("IfcRampType", 765, IFC4_IfcBuildingElementType_type);
    IFC4_IfcRationalBSplineSurfaceWithKnots_type = new entity("IfcRationalBSplineSurfaceWithKnots", 769, IFC4_IfcBSplineSurfaceWithKnots_type);
    IFC4_IfcReinforcingElement_type = new entity("IfcReinforcingElement", 787, IFC4_IfcElementComponent_type);
    IFC4_IfcReinforcingElementType_type = new entity("IfcReinforcingElementType", 788, IFC4_IfcElementComponentType_type);
    IFC4_IfcReinforcingMesh_type = new entity("IfcReinforcingMesh", 789, IFC4_IfcReinforcingElement_type);
    IFC4_IfcReinforcingMeshType_type = new entity("IfcReinforcingMeshType", 790, IFC4_IfcReinforcingElementType_type);
    IFC4_IfcRelAggregates_type = new entity("IfcRelAggregates", 792, IFC4_IfcRelDecomposes_type);
    IFC4_IfcRoofType_type = new entity("IfcRoofType", 858, IFC4_IfcBuildingElementType_type);
    IFC4_IfcSanitaryTerminalType_type = new entity("IfcSanitaryTerminalType", 867, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcShadingDeviceType_type = new entity("IfcShadingDeviceType", 882, IFC4_IfcBuildingElementType_type);
    IFC4_IfcSite_type = new entity("IfcSite", 895, IFC4_IfcSpatialStructureElement_type);
    IFC4_IfcSlabType_type = new entity("IfcSlabType", 902, IFC4_IfcBuildingElementType_type);
    IFC4_IfcSolarDeviceType_type = new entity("IfcSolarDeviceType", 906, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcSpace_type = new entity("IfcSpace", 915, IFC4_IfcSpatialStructureElement_type);
    IFC4_IfcSpaceHeaterType_type = new entity("IfcSpaceHeaterType", 918, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcSpaceType_type = new entity("IfcSpaceType", 920, IFC4_IfcSpatialStructureElementType_type);
    IFC4_IfcStackTerminalType_type = new entity("IfcStackTerminalType", 935, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcStairFlightType_type = new entity("IfcStairFlightType", 939, IFC4_IfcBuildingElementType_type);
    IFC4_IfcStairType_type = new entity("IfcStairType", 941, IFC4_IfcBuildingElementType_type);
    IFC4_IfcStructuralAction_type = new entity("IfcStructuralAction", 945, IFC4_IfcStructuralActivity_type);
    IFC4_IfcStructuralConnection_type = new entity("IfcStructuralConnection", 949, IFC4_IfcStructuralItem_type);
    IFC4_IfcStructuralCurveAction_type = new entity("IfcStructuralCurveAction", 951, IFC4_IfcStructuralAction_type);
    IFC4_IfcStructuralCurveConnection_type = new entity("IfcStructuralCurveConnection", 953, IFC4_IfcStructuralConnection_type);
    IFC4_IfcStructuralCurveMember_type = new entity("IfcStructuralCurveMember", 954, IFC4_IfcStructuralMember_type);
    IFC4_IfcStructuralCurveMemberVarying_type = new entity("IfcStructuralCurveMemberVarying", 956, IFC4_IfcStructuralCurveMember_type);
    IFC4_IfcStructuralCurveReaction_type = new entity("IfcStructuralCurveReaction", 957, IFC4_IfcStructuralReaction_type);
    IFC4_IfcStructuralLinearAction_type = new entity("IfcStructuralLinearAction", 959, IFC4_IfcStructuralCurveAction_type);
    IFC4_IfcStructuralLoadGroup_type = new entity("IfcStructuralLoadGroup", 963, IFC4_IfcGroup_type);
    IFC4_IfcStructuralPointAction_type = new entity("IfcStructuralPointAction", 975, IFC4_IfcStructuralAction_type);
    IFC4_IfcStructuralPointConnection_type = new entity("IfcStructuralPointConnection", 976, IFC4_IfcStructuralConnection_type);
    IFC4_IfcStructuralPointReaction_type = new entity("IfcStructuralPointReaction", 977, IFC4_IfcStructuralReaction_type);
    IFC4_IfcStructuralResultGroup_type = new entity("IfcStructuralResultGroup", 979, IFC4_IfcGroup_type);
    IFC4_IfcStructuralSurfaceAction_type = new entity("IfcStructuralSurfaceAction", 980, IFC4_IfcStructuralAction_type);
    IFC4_IfcStructuralSurfaceConnection_type = new entity("IfcStructuralSurfaceConnection", 982, IFC4_IfcStructuralConnection_type);
    IFC4_IfcSubContractResource_type = new entity("IfcSubContractResource", 991, IFC4_IfcConstructionResource_type);
    IFC4_IfcSurfaceFeature_type = new entity("IfcSurfaceFeature", 997, IFC4_IfcFeatureElement_type);
    IFC4_IfcSwitchingDeviceType_type = new entity("IfcSwitchingDeviceType", 1017, IFC4_IfcFlowControllerType_type);
    IFC4_IfcSystem_type = new entity("IfcSystem", 1019, IFC4_IfcGroup_type);
    IFC4_IfcSystemFurnitureElement_type = new entity("IfcSystemFurnitureElement", 1020, IFC4_IfcFurnishingElement_type);
    IFC4_IfcTankType_type = new entity("IfcTankType", 1027, IFC4_IfcFlowStorageDeviceType_type);
    IFC4_IfcTendon_type = new entity("IfcTendon", 1038, IFC4_IfcReinforcingElement_type);
    IFC4_IfcTendonAnchor_type = new entity("IfcTendonAnchor", 1039, IFC4_IfcReinforcingElement_type);
    IFC4_IfcTendonAnchorType_type = new entity("IfcTendonAnchorType", 1040, IFC4_IfcReinforcingElementType_type);
    IFC4_IfcTendonType_type = new entity("IfcTendonType", 1042, IFC4_IfcReinforcingElementType_type);
    IFC4_IfcTransformerType_type = new entity("IfcTransformerType", 1082, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcTransportElement_type = new entity("IfcTransportElement", 1086, IFC4_IfcElement_type);
    IFC4_IfcTrimmedCurve_type = new entity("IfcTrimmedCurve", 1091, IFC4_IfcBoundedCurve_type);
    IFC4_IfcTubeBundleType_type = new entity("IfcTubeBundleType", 1096, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcUnitaryEquipmentType_type = new entity("IfcUnitaryEquipmentType", 1107, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcValveType_type = new entity("IfcValveType", 1115, IFC4_IfcFlowControllerType_type);
    IFC4_IfcVibrationIsolator_type = new entity("IfcVibrationIsolator", 1123, IFC4_IfcElementComponent_type);
    IFC4_IfcVibrationIsolatorType_type = new entity("IfcVibrationIsolatorType", 1124, IFC4_IfcElementComponentType_type);
    IFC4_IfcVirtualElement_type = new entity("IfcVirtualElement", 1126, IFC4_IfcElement_type);
    IFC4_IfcVoidingFeature_type = new entity("IfcVoidingFeature", 1128, IFC4_IfcFeatureElementSubtraction_type);
    IFC4_IfcWallType_type = new entity("IfcWallType", 1135, IFC4_IfcBuildingElementType_type);
    IFC4_IfcWasteTerminalType_type = new entity("IfcWasteTerminalType", 1141, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcWindowType_type = new entity("IfcWindowType", 1152, IFC4_IfcBuildingElementType_type);
    IFC4_IfcWorkCalendar_type = new entity("IfcWorkCalendar", 1155, IFC4_IfcControl_type);
    IFC4_IfcWorkControl_type = new entity("IfcWorkControl", 1157, IFC4_IfcControl_type);
    IFC4_IfcWorkPlan_type = new entity("IfcWorkPlan", 1158, IFC4_IfcWorkControl_type);
    IFC4_IfcWorkSchedule_type = new entity("IfcWorkSchedule", 1160, IFC4_IfcWorkControl_type);
    IFC4_IfcZone_type = new entity("IfcZone", 1163, IFC4_IfcSystem_type);
    IFC4_IfcActionRequest_type = new entity("IfcActionRequest", 2, IFC4_IfcControl_type);
    IFC4_IfcAirTerminalBoxType_type = new entity("IfcAirTerminalBoxType", 19, IFC4_IfcFlowControllerType_type);
    IFC4_IfcAirTerminalType_type = new entity("IfcAirTerminalType", 21, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcAirToAirHeatRecoveryType_type = new entity("IfcAirToAirHeatRecoveryType", 24, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcAsset_type = new entity("IfcAsset", 48, IFC4_IfcGroup_type);
    IFC4_IfcAudioVisualApplianceType_type = new entity("IfcAudioVisualApplianceType", 51, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcBSplineCurve_type = new entity("IfcBSplineCurve", 85, IFC4_IfcBoundedCurve_type);
    IFC4_IfcBSplineCurveWithKnots_type = new entity("IfcBSplineCurveWithKnots", 87, IFC4_IfcBSplineCurve_type);
    IFC4_IfcBeamType_type = new entity("IfcBeamType", 59, IFC4_IfcBuildingElementType_type);
    IFC4_IfcBoilerType_type = new entity("IfcBoilerType", 67, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcBoundaryCurve_type = new entity("IfcBoundaryCurve", 75, IFC4_IfcCompositeCurveOnSurface_type);
    IFC4_IfcBuildingElement_type = new entity("IfcBuildingElement", 92, IFC4_IfcElement_type);
    IFC4_IfcBuildingElementPart_type = new entity("IfcBuildingElementPart", 93, IFC4_IfcElementComponent_type);
    IFC4_IfcBuildingElementPartType_type = new entity("IfcBuildingElementPartType", 94, IFC4_IfcElementComponentType_type);
    IFC4_IfcBuildingElementProxy_type = new entity("IfcBuildingElementProxy", 96, IFC4_IfcBuildingElement_type);
    IFC4_IfcBuildingElementProxyType_type = new entity("IfcBuildingElementProxyType", 97, IFC4_IfcBuildingElementType_type);
    IFC4_IfcBuildingSystem_type = new entity("IfcBuildingSystem", 101, IFC4_IfcSystem_type);
    IFC4_IfcBurnerType_type = new entity("IfcBurnerType", 104, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcCableCarrierFittingType_type = new entity("IfcCableCarrierFittingType", 107, IFC4_IfcFlowFittingType_type);
    IFC4_IfcCableCarrierSegmentType_type = new entity("IfcCableCarrierSegmentType", 110, IFC4_IfcFlowSegmentType_type);
    IFC4_IfcCableFittingType_type = new entity("IfcCableFittingType", 113, IFC4_IfcFlowFittingType_type);
    IFC4_IfcCableSegmentType_type = new entity("IfcCableSegmentType", 116, IFC4_IfcFlowSegmentType_type);
    IFC4_IfcChillerType_type = new entity("IfcChillerType", 131, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcChimney_type = new entity("IfcChimney", 133, IFC4_IfcBuildingElement_type);
    IFC4_IfcCircle_type = new entity("IfcCircle", 136, IFC4_IfcConic_type);
    IFC4_IfcCivilElement_type = new entity("IfcCivilElement", 139, IFC4_IfcElement_type);
    IFC4_IfcCoilType_type = new entity("IfcCoilType", 147, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcColumn_type = new entity("IfcColumn", 154, IFC4_IfcBuildingElement_type);
    IFC4_IfcColumnStandardCase_type = new entity("IfcColumnStandardCase", 155, IFC4_IfcColumn_type);
    IFC4_IfcCommunicationsApplianceType_type = new entity("IfcCommunicationsApplianceType", 159, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcCompressorType_type = new entity("IfcCompressorType", 171, IFC4_IfcFlowMovingDeviceType_type);
    IFC4_IfcCondenserType_type = new entity("IfcCondenserType", 174, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcConstructionEquipmentResource_type = new entity("IfcConstructionEquipmentResource", 187, IFC4_IfcConstructionResource_type);
    IFC4_IfcConstructionMaterialResource_type = new entity("IfcConstructionMaterialResource", 190, IFC4_IfcConstructionResource_type);
    IFC4_IfcConstructionProductResource_type = new entity("IfcConstructionProductResource", 193, IFC4_IfcConstructionResource_type);
    IFC4_IfcCooledBeamType_type = new entity("IfcCooledBeamType", 208, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcCoolingTowerType_type = new entity("IfcCoolingTowerType", 211, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcCovering_type = new entity("IfcCovering", 222, IFC4_IfcBuildingElement_type);
    IFC4_IfcCurtainWall_type = new entity("IfcCurtainWall", 233, IFC4_IfcBuildingElement_type);
    IFC4_IfcDamperType_type = new entity("IfcDamperType", 251, IFC4_IfcFlowControllerType_type);
    IFC4_IfcDiscreteAccessory_type = new entity("IfcDiscreteAccessory", 269, IFC4_IfcElementComponent_type);
    IFC4_IfcDiscreteAccessoryType_type = new entity("IfcDiscreteAccessoryType", 270, IFC4_IfcElementComponentType_type);
    IFC4_IfcDistributionChamberElementType_type = new entity("IfcDistributionChamberElementType", 273, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcDistributionControlElementType_type = new entity("IfcDistributionControlElementType", 277, IFC4_IfcDistributionElementType_type);
    IFC4_IfcDistributionElement_type = new entity("IfcDistributionElement", 278, IFC4_IfcElement_type);
    IFC4_IfcDistributionFlowElement_type = new entity("IfcDistributionFlowElement", 280, IFC4_IfcDistributionElement_type);
    IFC4_IfcDistributionPort_type = new entity("IfcDistributionPort", 282, IFC4_IfcPort_type);
    IFC4_IfcDistributionSystem_type = new entity("IfcDistributionSystem", 284, IFC4_IfcSystem_type);
    IFC4_IfcDoor_type = new entity("IfcDoor", 292, IFC4_IfcBuildingElement_type);
    IFC4_IfcDoorStandardCase_type = new entity("IfcDoorStandardCase", 297, IFC4_IfcDoor_type);
    IFC4_IfcDuctFittingType_type = new entity("IfcDuctFittingType", 308, IFC4_IfcFlowFittingType_type);
    IFC4_IfcDuctSegmentType_type = new entity("IfcDuctSegmentType", 311, IFC4_IfcFlowSegmentType_type);
    IFC4_IfcDuctSilencerType_type = new entity("IfcDuctSilencerType", 314, IFC4_IfcFlowTreatmentDeviceType_type);
    IFC4_IfcElectricApplianceType_type = new entity("IfcElectricApplianceType", 322, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcElectricDistributionBoardType_type = new entity("IfcElectricDistributionBoardType", 329, IFC4_IfcFlowControllerType_type);
    IFC4_IfcElectricFlowStorageDeviceType_type = new entity("IfcElectricFlowStorageDeviceType", 332, IFC4_IfcFlowStorageDeviceType_type);
    IFC4_IfcElectricGeneratorType_type = new entity("IfcElectricGeneratorType", 335, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcElectricMotorType_type = new entity("IfcElectricMotorType", 338, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcElectricTimeControlType_type = new entity("IfcElectricTimeControlType", 342, IFC4_IfcFlowControllerType_type);
    IFC4_IfcEnergyConversionDevice_type = new entity("IfcEnergyConversionDevice", 357, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcEngine_type = new entity("IfcEngine", 360, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcEvaporativeCooler_type = new entity("IfcEvaporativeCooler", 363, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcEvaporator_type = new entity("IfcEvaporator", 366, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcExternalSpatialElement_type = new entity("IfcExternalSpatialElement", 381, IFC4_IfcExternalSpatialStructureElement_type);
    IFC4_IfcFanType_type = new entity("IfcFanType", 395, IFC4_IfcFlowMovingDeviceType_type);
    IFC4_IfcFilterType_type = new entity("IfcFilterType", 408, IFC4_IfcFlowTreatmentDeviceType_type);
    IFC4_IfcFireSuppressionTerminalType_type = new entity("IfcFireSuppressionTerminalType", 411, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcFlowController_type = new entity("IfcFlowController", 414, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowFitting_type = new entity("IfcFlowFitting", 417, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowInstrumentType_type = new entity("IfcFlowInstrumentType", 420, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcFlowMeter_type = new entity("IfcFlowMeter", 422, IFC4_IfcFlowController_type);
    IFC4_IfcFlowMovingDevice_type = new entity("IfcFlowMovingDevice", 425, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowSegment_type = new entity("IfcFlowSegment", 427, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowStorageDevice_type = new entity("IfcFlowStorageDevice", 429, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowTerminal_type = new entity("IfcFlowTerminal", 431, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowTreatmentDevice_type = new entity("IfcFlowTreatmentDevice", 433, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFooting_type = new entity("IfcFooting", 438, IFC4_IfcBuildingElement_type);
    IFC4_IfcHeatExchanger_type = new entity("IfcHeatExchanger", 468, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcHumidifier_type = new entity("IfcHumidifier", 473, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcInterceptor_type = new entity("IfcInterceptor", 486, IFC4_IfcFlowTreatmentDevice_type);
    IFC4_IfcJunctionBox_type = new entity("IfcJunctionBox", 497, IFC4_IfcFlowFitting_type);
    IFC4_IfcLamp_type = new entity("IfcLamp", 507, IFC4_IfcFlowTerminal_type);
    IFC4_IfcLightFixture_type = new entity("IfcLightFixture", 521, IFC4_IfcFlowTerminal_type);
    IFC4_IfcMedicalDevice_type = new entity("IfcMedicalDevice", 580, IFC4_IfcFlowTerminal_type);
    IFC4_IfcMember_type = new entity("IfcMember", 583, IFC4_IfcBuildingElement_type);
    IFC4_IfcMemberStandardCase_type = new entity("IfcMemberStandardCase", 584, IFC4_IfcMember_type);
    IFC4_IfcMotorConnection_type = new entity("IfcMotorConnection", 603, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcOuterBoundaryCurve_type = new entity("IfcOuterBoundaryCurve", 629, IFC4_IfcBoundaryCurve_type);
    IFC4_IfcOutlet_type = new entity("IfcOutlet", 630, IFC4_IfcFlowTerminal_type);
    IFC4_IfcPile_type = new entity("IfcPile", 651, IFC4_IfcBuildingElement_type);
    IFC4_IfcPipeFitting_type = new entity("IfcPipeFitting", 655, IFC4_IfcFlowFitting_type);
    IFC4_IfcPipeSegment_type = new entity("IfcPipeSegment", 658, IFC4_IfcFlowSegment_type);
    IFC4_IfcPlate_type = new entity("IfcPlate", 668, IFC4_IfcBuildingElement_type);
    IFC4_IfcPlateStandardCase_type = new entity("IfcPlateStandardCase", 669, IFC4_IfcPlate_type);
    IFC4_IfcProtectiveDevice_type = new entity("IfcProtectiveDevice", 740, IFC4_IfcFlowController_type);
    IFC4_IfcProtectiveDeviceTrippingUnitType_type = new entity("IfcProtectiveDeviceTrippingUnitType", 742, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcPump_type = new entity("IfcPump", 747, IFC4_IfcFlowMovingDevice_type);
    IFC4_IfcRailing_type = new entity("IfcRailing", 758, IFC4_IfcBuildingElement_type);
    IFC4_IfcRamp_type = new entity("IfcRamp", 761, IFC4_IfcBuildingElement_type);
    IFC4_IfcRampFlight_type = new entity("IfcRampFlight", 762, IFC4_IfcBuildingElement_type);
    IFC4_IfcRationalBSplineCurveWithKnots_type = new entity("IfcRationalBSplineCurveWithKnots", 768, IFC4_IfcBSplineCurveWithKnots_type);
    IFC4_IfcReinforcingBar_type = new entity("IfcReinforcingBar", 782, IFC4_IfcReinforcingElement_type);
    IFC4_IfcReinforcingBarType_type = new entity("IfcReinforcingBarType", 785, IFC4_IfcReinforcingElementType_type);
    IFC4_IfcRoof_type = new entity("IfcRoof", 857, IFC4_IfcBuildingElement_type);
    IFC4_IfcSanitaryTerminal_type = new entity("IfcSanitaryTerminal", 866, IFC4_IfcFlowTerminal_type);
    IFC4_IfcSensorType_type = new entity("IfcSensorType", 878, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcShadingDevice_type = new entity("IfcShadingDevice", 881, IFC4_IfcBuildingElement_type);
    IFC4_IfcSlab_type = new entity("IfcSlab", 899, IFC4_IfcBuildingElement_type);
    IFC4_IfcSlabElementedCase_type = new entity("IfcSlabElementedCase", 900, IFC4_IfcSlab_type);
    IFC4_IfcSlabStandardCase_type = new entity("IfcSlabStandardCase", 901, IFC4_IfcSlab_type);
    IFC4_IfcSolarDevice_type = new entity("IfcSolarDevice", 905, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcSpaceHeater_type = new entity("IfcSpaceHeater", 917, IFC4_IfcFlowTerminal_type);
    IFC4_IfcStackTerminal_type = new entity("IfcStackTerminal", 934, IFC4_IfcFlowTerminal_type);
    IFC4_IfcStair_type = new entity("IfcStair", 937, IFC4_IfcBuildingElement_type);
    IFC4_IfcStairFlight_type = new entity("IfcStairFlight", 938, IFC4_IfcBuildingElement_type);
    IFC4_IfcStructuralAnalysisModel_type = new entity("IfcStructuralAnalysisModel", 948, IFC4_IfcSystem_type);
    IFC4_IfcStructuralLoadCase_type = new entity("IfcStructuralLoadCase", 961, IFC4_IfcStructuralLoadGroup_type);
    IFC4_IfcStructuralPlanarAction_type = new entity("IfcStructuralPlanarAction", 974, IFC4_IfcStructuralSurfaceAction_type);
    IFC4_IfcSwitchingDevice_type = new entity("IfcSwitchingDevice", 1016, IFC4_IfcFlowController_type);
    IFC4_IfcTank_type = new entity("IfcTank", 1026, IFC4_IfcFlowStorageDevice_type);
    IFC4_IfcTransformer_type = new entity("IfcTransformer", 1081, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcTubeBundle_type = new entity("IfcTubeBundle", 1095, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcUnitaryControlElementType_type = new entity("IfcUnitaryControlElementType", 1104, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcUnitaryEquipment_type = new entity("IfcUnitaryEquipment", 1106, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcValve_type = new entity("IfcValve", 1114, IFC4_IfcFlowController_type);
    IFC4_IfcWall_type = new entity("IfcWall", 1132, IFC4_IfcBuildingElement_type);
    IFC4_IfcWallElementedCase_type = new entity("IfcWallElementedCase", 1133, IFC4_IfcWall_type);
    IFC4_IfcWallStandardCase_type = new entity("IfcWallStandardCase", 1134, IFC4_IfcWall_type);
    IFC4_IfcWasteTerminal_type = new entity("IfcWasteTerminal", 1140, IFC4_IfcFlowTerminal_type);
    IFC4_IfcWindow_type = new entity("IfcWindow", 1143, IFC4_IfcBuildingElement_type);
    IFC4_IfcWindowStandardCase_type = new entity("IfcWindowStandardCase", 1148, IFC4_IfcWindow_type);
    IFC4_IfcActuatorType_type = new entity("IfcActuatorType", 10, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcAirTerminal_type = new entity("IfcAirTerminal", 17, IFC4_IfcFlowTerminal_type);
    IFC4_IfcAirTerminalBox_type = new entity("IfcAirTerminalBox", 18, IFC4_IfcFlowController_type);
    IFC4_IfcAirToAirHeatRecovery_type = new entity("IfcAirToAirHeatRecovery", 23, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcAlarmType_type = new entity("IfcAlarmType", 27, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcAudioVisualAppliance_type = new entity("IfcAudioVisualAppliance", 50, IFC4_IfcFlowTerminal_type);
    IFC4_IfcBeam_type = new entity("IfcBeam", 57, IFC4_IfcBuildingElement_type);
    IFC4_IfcBeamStandardCase_type = new entity("IfcBeamStandardCase", 58, IFC4_IfcBeam_type);
    IFC4_IfcBoiler_type = new entity("IfcBoiler", 66, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcBurner_type = new entity("IfcBurner", 103, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcCableCarrierFitting_type = new entity("IfcCableCarrierFitting", 106, IFC4_IfcFlowFitting_type);
    IFC4_IfcCableCarrierSegment_type = new entity("IfcCableCarrierSegment", 109, IFC4_IfcFlowSegment_type);
    IFC4_IfcCableFitting_type = new entity("IfcCableFitting", 112, IFC4_IfcFlowFitting_type);
    IFC4_IfcCableSegment_type = new entity("IfcCableSegment", 115, IFC4_IfcFlowSegment_type);
    IFC4_IfcChiller_type = new entity("IfcChiller", 130, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcCoil_type = new entity("IfcCoil", 146, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcCommunicationsAppliance_type = new entity("IfcCommunicationsAppliance", 158, IFC4_IfcFlowTerminal_type);
    IFC4_IfcCompressor_type = new entity("IfcCompressor", 170, IFC4_IfcFlowMovingDevice_type);
    IFC4_IfcCondenser_type = new entity("IfcCondenser", 173, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcControllerType_type = new entity("IfcControllerType", 203, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcCooledBeam_type = new entity("IfcCooledBeam", 207, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcCoolingTower_type = new entity("IfcCoolingTower", 210, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcDamper_type = new entity("IfcDamper", 250, IFC4_IfcFlowController_type);
    IFC4_IfcDistributionChamberElement_type = new entity("IfcDistributionChamberElement", 272, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcDistributionCircuit_type = new entity("IfcDistributionCircuit", 275, IFC4_IfcDistributionSystem_type);
    IFC4_IfcDistributionControlElement_type = new entity("IfcDistributionControlElement", 276, IFC4_IfcDistributionElement_type);
    IFC4_IfcDuctFitting_type = new entity("IfcDuctFitting", 307, IFC4_IfcFlowFitting_type);
    IFC4_IfcDuctSegment_type = new entity("IfcDuctSegment", 310, IFC4_IfcFlowSegment_type);
    IFC4_IfcDuctSilencer_type = new entity("IfcDuctSilencer", 313, IFC4_IfcFlowTreatmentDevice_type);
    IFC4_IfcElectricAppliance_type = new entity("IfcElectricAppliance", 321, IFC4_IfcFlowTerminal_type);
    IFC4_IfcElectricDistributionBoard_type = new entity("IfcElectricDistributionBoard", 328, IFC4_IfcFlowController_type);
    IFC4_IfcElectricFlowStorageDevice_type = new entity("IfcElectricFlowStorageDevice", 331, IFC4_IfcFlowStorageDevice_type);
    IFC4_IfcElectricGenerator_type = new entity("IfcElectricGenerator", 334, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcElectricMotor_type = new entity("IfcElectricMotor", 337, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcElectricTimeControl_type = new entity("IfcElectricTimeControl", 341, IFC4_IfcFlowController_type);
    IFC4_IfcFan_type = new entity("IfcFan", 394, IFC4_IfcFlowMovingDevice_type);
    IFC4_IfcFilter_type = new entity("IfcFilter", 407, IFC4_IfcFlowTreatmentDevice_type);
    IFC4_IfcFireSuppressionTerminal_type = new entity("IfcFireSuppressionTerminal", 410, IFC4_IfcFlowTerminal_type);
    IFC4_IfcFlowInstrument_type = new entity("IfcFlowInstrument", 419, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcProtectiveDeviceTrippingUnit_type = new entity("IfcProtectiveDeviceTrippingUnit", 741, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcSensor_type = new entity("IfcSensor", 877, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcUnitaryControlElement_type = new entity("IfcUnitaryControlElement", 1103, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcActuator_type = new entity("IfcActuator", 9, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcAlarm_type = new entity("IfcAlarm", 26, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcController_type = new entity("IfcController", 202, IFC4_IfcDistributionControlElement_type);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_IfcOrganization_type);
        items.push_back(IFC4_IfcPerson_type);
        items.push_back(IFC4_IfcPersonAndOrganization_type);
        IFC4_IfcActorSelect_type = new select_type("IfcActorSelect", 8, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcAxis2Placement2D_type);
        items.push_back(IFC4_IfcAxis2Placement3D_type);
        IFC4_IfcAxis2Placement_type = new select_type("IfcAxis2Placement", 54, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcLengthMeasure_type);
        items.push_back(IFC4_IfcPlaneAngleMeasure_type);
        IFC4_IfcBendingParameterSelect_type = new select_type("IfcBendingParameterSelect", 62, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC4_IfcBooleanResult_type);
        items.push_back(IFC4_IfcCsgPrimitive3D_type);
        items.push_back(IFC4_IfcHalfSpaceSolid_type);
        items.push_back(IFC4_IfcSolidModel_type);
        IFC4_IfcBooleanOperand_type = new select_type("IfcBooleanOperand", 71, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcClassification_type);
        items.push_back(IFC4_IfcClassificationReference_type);
        IFC4_IfcClassificationReferenceSelect_type = new select_type("IfcClassificationReferenceSelect", 143, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcClassification_type);
        items.push_back(IFC4_IfcClassificationReference_type);
        IFC4_IfcClassificationSelect_type = new select_type("IfcClassificationSelect", 144, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcColourSpecification_type);
        items.push_back(IFC4_IfcPreDefinedColour_type);
        IFC4_IfcColour_type = new select_type("IfcColour", 149, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcColourRgb_type);
        items.push_back(IFC4_IfcNormalisedRatioMeasure_type);
        IFC4_IfcColourOrFactor_type = new select_type("IfcColourOrFactor", 150, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcCoordinateReferenceSystem_type);
        items.push_back(IFC4_IfcGeometricRepresentationContext_type);
        IFC4_IfcCoordinateReferenceSystemSelect_type = new select_type("IfcCoordinateReferenceSystemSelect", 215, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcBooleanResult_type);
        items.push_back(IFC4_IfcCsgPrimitive3D_type);
        IFC4_IfcCsgSelect_type = new select_type("IfcCsgSelect", 229, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcCompositeCurveOnSurface_type);
        items.push_back(IFC4_IfcPcurve_type);
        IFC4_IfcCurveOnSurface_type = new select_type("IfcCurveOnSurface", 242, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcBoundedCurve_type);
        items.push_back(IFC4_IfcEdgeCurve_type);
        IFC4_IfcCurveOrEdgeCurve_type = new select_type("IfcCurveOrEdgeCurve", 243, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcCurveStyleFont_type);
        items.push_back(IFC4_IfcPreDefinedCurveFont_type);
        IFC4_IfcCurveStyleFontSelect_type = new select_type("IfcCurveStyleFontSelect", 248, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcObjectDefinition_type);
        items.push_back(IFC4_IfcPropertyDefinition_type);
        IFC4_IfcDefinitionSelect_type = new select_type("IfcDefinitionSelect", 258, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(71);
        items.push_back(IFC4_IfcAbsorbedDoseMeasure_type);
        items.push_back(IFC4_IfcAccelerationMeasure_type);
        items.push_back(IFC4_IfcAngularVelocityMeasure_type);
        items.push_back(IFC4_IfcAreaDensityMeasure_type);
        items.push_back(IFC4_IfcCompoundPlaneAngleMeasure_type);
        items.push_back(IFC4_IfcCurvatureMeasure_type);
        items.push_back(IFC4_IfcDoseEquivalentMeasure_type);
        items.push_back(IFC4_IfcDynamicViscosityMeasure_type);
        items.push_back(IFC4_IfcElectricCapacitanceMeasure_type);
        items.push_back(IFC4_IfcElectricChargeMeasure_type);
        items.push_back(IFC4_IfcElectricConductanceMeasure_type);
        items.push_back(IFC4_IfcElectricResistanceMeasure_type);
        items.push_back(IFC4_IfcElectricVoltageMeasure_type);
        items.push_back(IFC4_IfcEnergyMeasure_type);
        items.push_back(IFC4_IfcForceMeasure_type);
        items.push_back(IFC4_IfcFrequencyMeasure_type);
        items.push_back(IFC4_IfcHeatFluxDensityMeasure_type);
        items.push_back(IFC4_IfcHeatingValueMeasure_type);
        items.push_back(IFC4_IfcIlluminanceMeasure_type);
        items.push_back(IFC4_IfcInductanceMeasure_type);
        items.push_back(IFC4_IfcIntegerCountRateMeasure_type);
        items.push_back(IFC4_IfcIonConcentrationMeasure_type);
        items.push_back(IFC4_IfcIsothermalMoistureCapacityMeasure_type);
        items.push_back(IFC4_IfcKinematicViscosityMeasure_type);
        items.push_back(IFC4_IfcLinearForceMeasure_type);
        items.push_back(IFC4_IfcLinearMomentMeasure_type);
        items.push_back(IFC4_IfcLinearStiffnessMeasure_type);
        items.push_back(IFC4_IfcLinearVelocityMeasure_type);
        items.push_back(IFC4_IfcLuminousFluxMeasure_type);
        items.push_back(IFC4_IfcLuminousIntensityDistributionMeasure_type);
        items.push_back(IFC4_IfcMagneticFluxDensityMeasure_type);
        items.push_back(IFC4_IfcMagneticFluxMeasure_type);
        items.push_back(IFC4_IfcMassDensityMeasure_type);
        items.push_back(IFC4_IfcMassFlowRateMeasure_type);
        items.push_back(IFC4_IfcMassPerLengthMeasure_type);
        items.push_back(IFC4_IfcModulusOfElasticityMeasure_type);
        items.push_back(IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type);
        items.push_back(IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type);
        items.push_back(IFC4_IfcModulusOfSubgradeReactionMeasure_type);
        items.push_back(IFC4_IfcMoistureDiffusivityMeasure_type);
        items.push_back(IFC4_IfcMolecularWeightMeasure_type);
        items.push_back(IFC4_IfcMomentOfInertiaMeasure_type);
        items.push_back(IFC4_IfcMonetaryMeasure_type);
        items.push_back(IFC4_IfcPHMeasure_type);
        items.push_back(IFC4_IfcPlanarForceMeasure_type);
        items.push_back(IFC4_IfcPowerMeasure_type);
        items.push_back(IFC4_IfcPressureMeasure_type);
        items.push_back(IFC4_IfcRadioActivityMeasure_type);
        items.push_back(IFC4_IfcRotationalFrequencyMeasure_type);
        items.push_back(IFC4_IfcRotationalMassMeasure_type);
        items.push_back(IFC4_IfcRotationalStiffnessMeasure_type);
        items.push_back(IFC4_IfcSectionModulusMeasure_type);
        items.push_back(IFC4_IfcSectionalAreaIntegralMeasure_type);
        items.push_back(IFC4_IfcShearModulusMeasure_type);
        items.push_back(IFC4_IfcSoundPowerLevelMeasure_type);
        items.push_back(IFC4_IfcSoundPowerMeasure_type);
        items.push_back(IFC4_IfcSoundPressureLevelMeasure_type);
        items.push_back(IFC4_IfcSoundPressureMeasure_type);
        items.push_back(IFC4_IfcSpecificHeatCapacityMeasure_type);
        items.push_back(IFC4_IfcTemperatureGradientMeasure_type);
        items.push_back(IFC4_IfcTemperatureRateOfChangeMeasure_type);
        items.push_back(IFC4_IfcThermalAdmittanceMeasure_type);
        items.push_back(IFC4_IfcThermalConductivityMeasure_type);
        items.push_back(IFC4_IfcThermalExpansionCoefficientMeasure_type);
        items.push_back(IFC4_IfcThermalResistanceMeasure_type);
        items.push_back(IFC4_IfcThermalTransmittanceMeasure_type);
        items.push_back(IFC4_IfcTorqueMeasure_type);
        items.push_back(IFC4_IfcVaporPermeabilityMeasure_type);
        items.push_back(IFC4_IfcVolumetricFlowRateMeasure_type);
        items.push_back(IFC4_IfcWarpingConstantMeasure_type);
        items.push_back(IFC4_IfcWarpingMomentMeasure_type);
        IFC4_IfcDerivedMeasureValue_type = new select_type("IfcDerivedMeasureValue", 259, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcDocumentInformation_type);
        items.push_back(IFC4_IfcDocumentReference_type);
        IFC4_IfcDocumentSelect_type = new select_type("IfcDocumentSelect", 290, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC4_IfcColour_type);
        items.push_back(IFC4_IfcExternallyDefinedHatchStyle_type);
        items.push_back(IFC4_IfcFillAreaStyleHatching_type);
        items.push_back(IFC4_IfcFillAreaStyleTiles_type);
        IFC4_IfcFillStyleSelect_type = new select_type("IfcFillStyleSelect", 406, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_IfcCurve_type);
        items.push_back(IFC4_IfcPoint_type);
        items.push_back(IFC4_IfcSurface_type);
        IFC4_IfcGeometricSetSelect_type = new select_type("IfcGeometricSetSelect", 457, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcDirection_type);
        items.push_back(IFC4_IfcVirtualGridIntersection_type);
        IFC4_IfcGridPlacementDirectionSelect_type = new select_type("IfcGridPlacementDirectionSelect", 463, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcPositiveLengthMeasure_type);
        items.push_back(IFC4_IfcVector_type);
        IFC4_IfcHatchLineDistanceSelect_type = new select_type("IfcHatchLineDistanceSelect", 467, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcRepresentation_type);
        items.push_back(IFC4_IfcRepresentationItem_type);
        IFC4_IfcLayeredItem_type = new select_type("IfcLayeredItem", 511, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcLibraryInformation_type);
        items.push_back(IFC4_IfcLibraryReference_type);
        IFC4_IfcLibrarySelect_type = new select_type("IfcLibrarySelect", 516, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcExternalReference_type);
        items.push_back(IFC4_IfcLightIntensityDistribution_type);
        IFC4_IfcLightDistributionDataSourceSelect_type = new select_type("IfcLightDistributionDataSourceSelect", 519, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_IfcMaterialDefinition_type);
        items.push_back(IFC4_IfcMaterialList_type);
        items.push_back(IFC4_IfcMaterialUsageDefinition_type);
        IFC4_IfcMaterialSelect_type = new select_type("IfcMaterialSelect", 573, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(23);
        items.push_back(IFC4_IfcAmountOfSubstanceMeasure_type);
        items.push_back(IFC4_IfcAreaMeasure_type);
        items.push_back(IFC4_IfcComplexNumber_type);
        items.push_back(IFC4_IfcContextDependentMeasure_type);
        items.push_back(IFC4_IfcCountMeasure_type);
        items.push_back(IFC4_IfcDescriptiveMeasure_type);
        items.push_back(IFC4_IfcElectricCurrentMeasure_type);
        items.push_back(IFC4_IfcLengthMeasure_type);
        items.push_back(IFC4_IfcLuminousIntensityMeasure_type);
        items.push_back(IFC4_IfcMassMeasure_type);
        items.push_back(IFC4_IfcNonNegativeLengthMeasure_type);
        items.push_back(IFC4_IfcNormalisedRatioMeasure_type);
        items.push_back(IFC4_IfcNumericMeasure_type);
        items.push_back(IFC4_IfcParameterValue_type);
        items.push_back(IFC4_IfcPlaneAngleMeasure_type);
        items.push_back(IFC4_IfcPositiveLengthMeasure_type);
        items.push_back(IFC4_IfcPositivePlaneAngleMeasure_type);
        items.push_back(IFC4_IfcPositiveRatioMeasure_type);
        items.push_back(IFC4_IfcRatioMeasure_type);
        items.push_back(IFC4_IfcSolidAngleMeasure_type);
        items.push_back(IFC4_IfcThermodynamicTemperatureMeasure_type);
        items.push_back(IFC4_IfcTimeMeasure_type);
        items.push_back(IFC4_IfcVolumeMeasure_type);
        IFC4_IfcMeasureValue_type = new select_type("IfcMeasureValue", 575, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcBoolean_type);
        items.push_back(IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type);
        IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type = new select_type("IfcModulusOfRotationalSubgradeReactionSelect", 593, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcBoolean_type);
        items.push_back(IFC4_IfcModulusOfSubgradeReactionMeasure_type);
        IFC4_IfcModulusOfSubgradeReactionSelect_type = new select_type("IfcModulusOfSubgradeReactionSelect", 595, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcBoolean_type);
        items.push_back(IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type);
        IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type = new select_type("IfcModulusOfTranslationalSubgradeReactionSelect", 596, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(9);
        items.push_back(IFC4_IfcAddress_type);
        items.push_back(IFC4_IfcAppliedValue_type);
        items.push_back(IFC4_IfcExternalReference_type);
        items.push_back(IFC4_IfcMaterialDefinition_type);
        items.push_back(IFC4_IfcOrganization_type);
        items.push_back(IFC4_IfcPerson_type);
        items.push_back(IFC4_IfcPersonAndOrganization_type);
        items.push_back(IFC4_IfcTable_type);
        items.push_back(IFC4_IfcTimeSeries_type);
        IFC4_IfcObjectReferenceSelect_type = new select_type("IfcObjectReferenceSelect", 616, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcPoint_type);
        items.push_back(IFC4_IfcVertexPoint_type);
        IFC4_IfcPointOrVertexPoint_type = new select_type("IfcPointOrVertexPoint", 675, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4_IfcCurveStyle_type);
        items.push_back(IFC4_IfcFillAreaStyle_type);
        items.push_back(IFC4_IfcNullStyle_type);
        items.push_back(IFC4_IfcSurfaceStyle_type);
        items.push_back(IFC4_IfcTextStyle_type);
        IFC4_IfcPresentationStyleSelect_type = new select_type("IfcPresentationStyleSelect", 698, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcProcess_type);
        items.push_back(IFC4_IfcTypeProcess_type);
        IFC4_IfcProcessSelect_type = new select_type("IfcProcessSelect", 704, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcProductDefinitionShape_type);
        items.push_back(IFC4_IfcRepresentationMap_type);
        IFC4_IfcProductRepresentationSelect_type = new select_type("IfcProductRepresentationSelect", 708, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcProduct_type);
        items.push_back(IFC4_IfcTypeProduct_type);
        IFC4_IfcProductSelect_type = new select_type("IfcProductSelect", 709, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcPropertySetDefinition_type);
        items.push_back(IFC4_IfcPropertySetDefinitionSet_type);
        IFC4_IfcPropertySetDefinitionSelect_type = new select_type("IfcPropertySetDefinitionSelect", 732, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(16);
        items.push_back(IFC4_IfcActorRole_type);
        items.push_back(IFC4_IfcAppliedValue_type);
        items.push_back(IFC4_IfcApproval_type);
        items.push_back(IFC4_IfcConstraint_type);
        items.push_back(IFC4_IfcContextDependentUnit_type);
        items.push_back(IFC4_IfcConversionBasedUnit_type);
        items.push_back(IFC4_IfcExternalInformation_type);
        items.push_back(IFC4_IfcExternalReference_type);
        items.push_back(IFC4_IfcMaterialDefinition_type);
        items.push_back(IFC4_IfcOrganization_type);
        items.push_back(IFC4_IfcPerson_type);
        items.push_back(IFC4_IfcPersonAndOrganization_type);
        items.push_back(IFC4_IfcPhysicalQuantity_type);
        items.push_back(IFC4_IfcProfileDef_type);
        items.push_back(IFC4_IfcPropertyAbstraction_type);
        items.push_back(IFC4_IfcTimeSeries_type);
        IFC4_IfcResourceObjectSelect_type = new select_type("IfcResourceObjectSelect", 849, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcResource_type);
        items.push_back(IFC4_IfcTypeResource_type);
        IFC4_IfcResourceSelect_type = new select_type("IfcResourceSelect", 850, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcBoolean_type);
        items.push_back(IFC4_IfcRotationalStiffnessMeasure_type);
        IFC4_IfcRotationalStiffnessSelect_type = new select_type("IfcRotationalStiffnessSelect", 864, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcArcIndex_type);
        items.push_back(IFC4_IfcLineIndex_type);
        IFC4_IfcSegmentIndexSelect_type = new select_type("IfcSegmentIndexSelect", 876, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcClosedShell_type);
        items.push_back(IFC4_IfcOpenShell_type);
        IFC4_IfcShell_type = new select_type("IfcShell", 888, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(13);
        items.push_back(IFC4_IfcBoolean_type);
        items.push_back(IFC4_IfcDate_type);
        items.push_back(IFC4_IfcDateTime_type);
        items.push_back(IFC4_IfcDuration_type);
        items.push_back(IFC4_IfcIdentifier_type);
        items.push_back(IFC4_IfcInteger_type);
        items.push_back(IFC4_IfcLabel_type);
        items.push_back(IFC4_IfcLogical_type);
        items.push_back(IFC4_IfcPositiveInteger_type);
        items.push_back(IFC4_IfcReal_type);
        items.push_back(IFC4_IfcText_type);
        items.push_back(IFC4_IfcTime_type);
        items.push_back(IFC4_IfcTimeStamp_type);
        IFC4_IfcSimpleValue_type = new select_type("IfcSimpleValue", 893, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC4_IfcDescriptiveMeasure_type);
        items.push_back(IFC4_IfcLengthMeasure_type);
        items.push_back(IFC4_IfcNormalisedRatioMeasure_type);
        items.push_back(IFC4_IfcPositiveLengthMeasure_type);
        items.push_back(IFC4_IfcPositiveRatioMeasure_type);
        items.push_back(IFC4_IfcRatioMeasure_type);
        IFC4_IfcSizeSelect_type = new select_type("IfcSizeSelect", 898, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcClosedShell_type);
        items.push_back(IFC4_IfcSolidModel_type);
        IFC4_IfcSolidOrShell_type = new select_type("IfcSolidOrShell", 910, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcExternalSpatialElement_type);
        items.push_back(IFC4_IfcSpace_type);
        IFC4_IfcSpaceBoundarySelect_type = new select_type("IfcSpaceBoundarySelect", 916, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcSpecularExponent_type);
        items.push_back(IFC4_IfcSpecularRoughness_type);
        IFC4_IfcSpecularHighlightSelect_type = new select_type("IfcSpecularHighlightSelect", 931, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcElement_type);
        items.push_back(IFC4_IfcStructuralItem_type);
        IFC4_IfcStructuralActivityAssignmentSelect_type = new select_type("IfcStructuralActivityAssignmentSelect", 947, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcPresentationStyle_type);
        items.push_back(IFC4_IfcPresentationStyleAssignment_type);
        IFC4_IfcStyleAssignmentSelect_type = new select_type("IfcStyleAssignmentSelect", 987, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_IfcFaceBasedSurfaceModel_type);
        items.push_back(IFC4_IfcFaceSurface_type);
        items.push_back(IFC4_IfcSurface_type);
        IFC4_IfcSurfaceOrFaceSurface_type = new select_type("IfcSurfaceOrFaceSurface", 1001, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4_IfcExternallyDefinedSurfaceStyle_type);
        items.push_back(IFC4_IfcSurfaceStyleLighting_type);
        items.push_back(IFC4_IfcSurfaceStyleRefraction_type);
        items.push_back(IFC4_IfcSurfaceStyleShading_type);
        items.push_back(IFC4_IfcSurfaceStyleWithTextures_type);
        IFC4_IfcSurfaceStyleElementSelect_type = new select_type("IfcSurfaceStyleElementSelect", 1005, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcExternallyDefinedTextFont_type);
        items.push_back(IFC4_IfcPreDefinedTextFont_type);
        IFC4_IfcTextFontSelect_type = new select_type("IfcTextFontSelect", 1050, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcDuration_type);
        items.push_back(IFC4_IfcRatioMeasure_type);
        IFC4_IfcTimeOrRatioSelect_type = new select_type("IfcTimeOrRatioSelect", 1072, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcBoolean_type);
        items.push_back(IFC4_IfcLinearStiffnessMeasure_type);
        IFC4_IfcTranslationalStiffnessSelect_type = new select_type("IfcTranslationalStiffnessSelect", 1085, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcCartesianPoint_type);
        items.push_back(IFC4_IfcParameterValue_type);
        IFC4_IfcTrimmingSelect_type = new select_type("IfcTrimmingSelect", 1093, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_IfcDerivedUnit_type);
        items.push_back(IFC4_IfcMonetaryUnit_type);
        items.push_back(IFC4_IfcNamedUnit_type);
        IFC4_IfcUnit_type = new select_type("IfcUnit", 1102, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_IfcDerivedMeasureValue_type);
        items.push_back(IFC4_IfcMeasureValue_type);
        items.push_back(IFC4_IfcSimpleValue_type);
        IFC4_IfcValue_type = new select_type("IfcValue", 1113, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcDirection_type);
        items.push_back(IFC4_IfcVector_type);
        IFC4_IfcVectorOrDirection_type = new select_type("IfcVectorOrDirection", 1119, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcBoolean_type);
        items.push_back(IFC4_IfcWarpingMomentMeasure_type);
        IFC4_IfcWarpingStiffnessSelect_type = new select_type("IfcWarpingStiffnessSelect", 1139, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_IfcMeasureWithUnit_type);
        items.push_back(IFC4_IfcReference_type);
        items.push_back(IFC4_IfcValue_type);
        IFC4_IfcAppliedValueSelect_type = new select_type("IfcAppliedValueSelect", 37, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_IfcCurveStyleFontAndScaling_type);
        items.push_back(IFC4_IfcCurveStyleFontSelect_type);
        IFC4_IfcCurveFontOrScaledCurveFontSelect_type = new select_type("IfcCurveFontOrScaledCurveFontSelect", 240, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC4_IfcAppliedValue_type);
        items.push_back(IFC4_IfcMeasureWithUnit_type);
        items.push_back(IFC4_IfcReference_type);
        items.push_back(IFC4_IfcTable_type);
        items.push_back(IFC4_IfcTimeSeries_type);
        items.push_back(IFC4_IfcValue_type);
        IFC4_IfcMetricValueSelect_type = new select_type("IfcMetricValueSelect", 588, items);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcActionRequestTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcActionRequest_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TheActor", new named_type(IFC4_IfcActorSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcActor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Role", new named_type(IFC4_IfcRoleEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedRole", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcActorRole_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcActuatorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcActuator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcActuatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcActuatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Purpose", new named_type(IFC4_IfcAddressTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPurpose", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcAdvancedBrep_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcClosedShell_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcAdvancedBrepWithVoids_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAdvancedFace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAirTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAirTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAirTerminalBoxTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAirTerminalBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAirTerminalBoxTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAirTerminalBoxType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAirTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAirTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAirToAirHeatRecoveryTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAirToAirHeatRecovery_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAirToAirHeatRecoveryTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAirToAirHeatRecoveryType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAlarmTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAlarm_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAlarmTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAlarmType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAnnotation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OuterBoundary", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcCurve_type)), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcAnnotationFillArea_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ApplicationDeveloper", new named_type(IFC4_IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("Version", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ApplicationFullName", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ApplicationIdentifier", new named_type(IFC4_IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcApplication_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("AppliedValue", new named_type(IFC4_IfcAppliedValueSelect_type), true));
        attributes.push_back(new entity::attribute("UnitBasis", new named_type(IFC4_IfcMeasureWithUnit_type), true));
        attributes.push_back(new entity::attribute("ApplicableDate", new named_type(IFC4_IfcDate_type), true));
        attributes.push_back(new entity::attribute("FixedUntilDate", new named_type(IFC4_IfcDate_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Condition", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ArithmeticOperator", new named_type(IFC4_IfcArithmeticOperatorEnum_type), true));
        attributes.push_back(new entity::attribute("Components", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAppliedValue_type)), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAppliedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("Identifier", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("TimeOfApproval", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Level", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Qualifier", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("RequestingApproval", new named_type(IFC4_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("GivingApproval", new named_type(IFC4_IfcActorSelect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcApproval_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IFC4_IfcApproval_type), false));
        attributes.push_back(new entity::attribute("RelatedApprovals", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcApproval_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcApprovalRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("OuterCurve", new named_type(IFC4_IfcCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcArbitraryClosedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Curve", new named_type(IFC4_IfcBoundedCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcArbitraryOpenProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("InnerCurves", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcCurve_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcArbitraryProfileDefWithVoids_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("OriginalValue", new named_type(IFC4_IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("CurrentValue", new named_type(IFC4_IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("TotalReplacementCost", new named_type(IFC4_IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("Owner", new named_type(IFC4_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("User", new named_type(IFC4_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("ResponsiblePerson", new named_type(IFC4_IfcPerson_type), true));
        attributes.push_back(new entity::attribute("IncorporationDate", new named_type(IFC4_IfcDate_type), true));
        attributes.push_back(new entity::attribute("DepreciatedValue", new named_type(IFC4_IfcCostValue_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAsset_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::attribute("BottomFlangeWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("OverallDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BottomFlangeThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BottomFlangeFilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopFlangeThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeFilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BottomFlangeEdgeRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BottomFlangeSlope", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeEdgeRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeSlope", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAsymmetricIShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAudioVisualApplianceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAudioVisualAppliance_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAudioVisualApplianceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAudioVisualApplianceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Axis", new named_type(IFC4_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcAxis1Placement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IFC4_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcAxis2Placement2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Axis", new named_type(IFC4_IfcDirection_type), true));
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IFC4_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcAxis2Placement3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Degree", new named_type(IFC4_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcCartesianPoint_type)), false));
        attributes.push_back(new entity::attribute("CurveForm", new named_type(IFC4_IfcBSplineCurveForm_type), false));
        attributes.push_back(new entity::attribute("ClosedCurve", new named_type(IFC4_IfcLogical_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IFC4_IfcLogical_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBSplineCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("KnotMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("Knots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcParameterValue_type)), false));
        attributes.push_back(new entity::attribute("KnotSpec", new named_type(IFC4_IfcKnotType_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBSplineCurveWithKnots_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("UDegree", new named_type(IFC4_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("VDegree", new named_type(IFC4_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcCartesianPoint_type))), false));
        attributes.push_back(new entity::attribute("SurfaceForm", new named_type(IFC4_IfcBSplineSurfaceForm_type), false));
        attributes.push_back(new entity::attribute("UClosed", new named_type(IFC4_IfcLogical_type), false));
        attributes.push_back(new entity::attribute("VClosed", new named_type(IFC4_IfcLogical_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IFC4_IfcLogical_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBSplineSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("UMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("VMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("UKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcParameterValue_type)), false));
        attributes.push_back(new entity::attribute("VKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcParameterValue_type)), false));
        attributes.push_back(new entity::attribute("KnotSpec", new named_type(IFC4_IfcKnotType_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBSplineSurfaceWithKnots_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBeamTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBeam_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBeamStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBeamTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBeamType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RasterFormat", new named_type(IFC4_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("RasterCode", new named_type(IFC4_IfcBinary_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBlobTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("XLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ZLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBlock_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBoilerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoiler_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBoilerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoilerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBooleanClippingResult_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Operator", new named_type(IFC4_IfcBooleanOperator_type), false));
        attributes.push_back(new entity::attribute("FirstOperand", new named_type(IFC4_IfcBooleanOperand_type), false));
        attributes.push_back(new entity::attribute("SecondOperand", new named_type(IFC4_IfcBooleanOperand_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBooleanResult_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcBoundaryCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoundaryCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TranslationalStiffnessByLengthX", new named_type(IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessByLengthY", new named_type(IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessByLengthZ", new named_type(IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthX", new named_type(IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthY", new named_type(IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthZ", new named_type(IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoundaryEdgeCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TranslationalStiffnessByAreaX", new named_type(IFC4_IfcModulusOfSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessByAreaY", new named_type(IFC4_IfcModulusOfSubgradeReactionSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessByAreaZ", new named_type(IFC4_IfcModulusOfSubgradeReactionSelect_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoundaryFaceCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TranslationalStiffnessX", new named_type(IFC4_IfcTranslationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessY", new named_type(IFC4_IfcTranslationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("TranslationalStiffnessZ", new named_type(IFC4_IfcTranslationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessX", new named_type(IFC4_IfcRotationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessY", new named_type(IFC4_IfcRotationalStiffnessSelect_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessZ", new named_type(IFC4_IfcRotationalStiffnessSelect_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoundaryNodeCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WarpingStiffness", new named_type(IFC4_IfcWarpingStiffnessSelect_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoundaryNodeConditionWarping_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcBoundedCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcBoundedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Corner", new named_type(IFC4_IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("XDim", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ZDim", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoundingBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Enclosure", new named_type(IFC4_IfcBoundingBox_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBoxedHalfSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ElevationOfRefHeight", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ElevationOfTerrain", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BuildingAddress", new named_type(IFC4_IfcPostalAddress_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuilding_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuildingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBuildingElementPartTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuildingElementPart_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBuildingElementPartTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuildingElementPartType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBuildingElementProxyTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuildingElementProxy_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBuildingElementProxyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuildingElementProxyType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuildingElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Elevation", new named_type(IFC4_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuildingStorey_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBuildingSystemTypeEnum_type), true));
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBuildingSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBurnerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBurner_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcBurnerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcBurnerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Width", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Girth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InternalFilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCableCarrierFittingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCableCarrierFitting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCableCarrierFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCableCarrierFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCableCarrierSegmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCableCarrierSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCableCarrierSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCableCarrierSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCableFittingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCableFitting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCableFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCableFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCableSegmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCableSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCableSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCableSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC4_IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcCartesianPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcCartesianPointList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcLengthMeasure_type))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcCartesianPointList2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcLengthMeasure_type))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcCartesianPointList3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Axis1", new named_type(IFC4_IfcDirection_type), true));
        attributes.push_back(new entity::attribute("Axis2", new named_type(IFC4_IfcDirection_type), true));
        attributes.push_back(new entity::attribute("LocalOrigin", new named_type(IFC4_IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Scale", new named_type(IFC4_IfcReal_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCartesianTransformationOperator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCartesianTransformationOperator2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Scale2", new named_type(IFC4_IfcReal_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCartesianTransformationOperator2DnonUniform_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Axis3", new named_type(IFC4_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCartesianTransformationOperator3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Scale2", new named_type(IFC4_IfcReal_type), true));
        attributes.push_back(new entity::attribute("Scale3", new named_type(IFC4_IfcReal_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCartesianTransformationOperator3DnonUniform_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Thickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCenterLineProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcChillerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcChiller_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcChillerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcChillerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcChimneyTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcChimney_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcChimneyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcChimneyType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcCircle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCircleHollowProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCircleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCivilElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCivilElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Source", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Edition", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("EditionDate", new named_type(IFC4_IfcDate_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Location", new named_type(IFC4_IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("ReferenceTokens", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcIdentifier_type)), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcClassification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ReferencedSource", new named_type(IFC4_IfcClassificationReferenceSelect_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Sort", new named_type(IFC4_IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcClassificationReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcClosedShell_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCoilTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCoil_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCoilTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCoilType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Red", new named_type(IFC4_IfcNormalisedRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("Green", new named_type(IFC4_IfcNormalisedRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("Blue", new named_type(IFC4_IfcNormalisedRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcColourRgb_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ColourList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcNormalisedRatioMeasure_type))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcColourRgbList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcColourSpecification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcColumnTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcColumn_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcColumnStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcColumnTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcColumnType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCommunicationsApplianceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCommunicationsAppliance_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCommunicationsApplianceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCommunicationsApplianceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IFC4_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcComplexProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("TemplateType", new named_type(IFC4_IfcComplexPropertyTemplateTypeEnum_type), true));
        attributes.push_back(new entity::attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertyTemplate_type)), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcComplexPropertyTemplate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcCompositeCurveSegment_type)), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IFC4_IfcLogical_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcCompositeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcCompositeCurveOnSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Transition", new named_type(IFC4_IfcTransitionCode_type), false));
        attributes.push_back(new entity::attribute("SameSense", new named_type(IFC4_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("ParentCurve", new named_type(IFC4_IfcCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCompositeCurveSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Profiles", new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC4_IfcProfileDef_type)), false));
        attributes.push_back(new entity::attribute("Label", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCompositeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCompressorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCompressor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCompressorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCompressorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCondenserTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCondenser_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCondenserTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCondenserType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcConic_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CfsFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcFace_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcConnectedFaceSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CurveOnRelatingElement", new named_type(IFC4_IfcCurveOrEdgeCurve_type), false));
        attributes.push_back(new entity::attribute("CurveOnRelatedElement", new named_type(IFC4_IfcCurveOrEdgeCurve_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcConnectionCurveGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcConnectionGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("EccentricityInX", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EccentricityInY", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EccentricityInZ", new named_type(IFC4_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConnectionPointEccentricity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PointOnRelatingElement", new named_type(IFC4_IfcPointOrVertexPoint_type), false));
        attributes.push_back(new entity::attribute("PointOnRelatedElement", new named_type(IFC4_IfcPointOrVertexPoint_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcConnectionPointGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SurfaceOnRelatingElement", new named_type(IFC4_IfcSurfaceOrFaceSurface_type), false));
        attributes.push_back(new entity::attribute("SurfaceOnRelatedElement", new named_type(IFC4_IfcSurfaceOrFaceSurface_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcConnectionSurfaceGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VolumeOnRelatingElement", new named_type(IFC4_IfcSolidOrShell_type), false));
        attributes.push_back(new entity::attribute("VolumeOnRelatedElement", new named_type(IFC4_IfcSolidOrShell_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcConnectionVolumeGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("ConstraintGrade", new named_type(IFC4_IfcConstraintEnum_type), false));
        attributes.push_back(new entity::attribute("ConstraintSource", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CreatingActor", new named_type(IFC4_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("CreationTime", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("UserDefinedGrade", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstraint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcConstructionEquipmentResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstructionEquipmentResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcConstructionEquipmentResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstructionEquipmentResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcConstructionMaterialResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstructionMaterialResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcConstructionMaterialResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstructionMaterialResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcConstructionProductResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstructionProductResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcConstructionProductResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstructionProductResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Usage", new named_type(IFC4_IfcResourceTime_type), true));
        attributes.push_back(new entity::attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAppliedValue_type)), true));
        attributes.push_back(new entity::attribute("BaseQuantity", new named_type(IFC4_IfcPhysicalQuantity_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstructionResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAppliedValue_type)), true));
        attributes.push_back(new entity::attribute("BaseQuantity", new named_type(IFC4_IfcPhysicalQuantity_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConstructionResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ObjectType", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Phase", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("RepresentationContexts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcRepresentationContext_type)), true));
        attributes.push_back(new entity::attribute("UnitsInContext", new named_type(IFC4_IfcUnitAssignment_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcContextDependentUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcControllerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcController_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcControllerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcControllerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ConversionFactor", new named_type(IFC4_IfcMeasureWithUnit_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConversionBasedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ConversionOffset", new named_type(IFC4_IfcReal_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcConversionBasedUnitWithOffset_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCooledBeamTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCooledBeam_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCooledBeamTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCooledBeamType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCoolingTowerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCoolingTower_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCoolingTowerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCoolingTowerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SourceCRS", new named_type(IFC4_IfcCoordinateReferenceSystemSelect_type), false));
        attributes.push_back(new entity::attribute("TargetCRS", new named_type(IFC4_IfcCoordinateReferenceSystem_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcCoordinateOperation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("GeodeticDatum", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("VerticalDatum", new named_type(IFC4_IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCoordinateReferenceSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCostItemTypeEnum_type), true));
        attributes.push_back(new entity::attribute("CostValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcCostValue_type)), true));
        attributes.push_back(new entity::attribute("CostQuantities", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcPhysicalQuantity_type)), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCostItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCostScheduleTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("SubmittedOn", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("UpdateDate", new named_type(IFC4_IfcDateTime_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCostSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCostValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCoveringTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCovering_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCoveringTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCoveringType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCrewResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCrewResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCrewResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCrewResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcCsgPrimitive3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TreeRootExpression", new named_type(IFC4_IfcCsgSelect_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcCsgSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingMonetaryUnit", new named_type(IFC4_IfcMonetaryUnit_type), false));
        attributes.push_back(new entity::attribute("RelatedMonetaryUnit", new named_type(IFC4_IfcMonetaryUnit_type), false));
        attributes.push_back(new entity::attribute("ExchangeRate", new named_type(IFC4_IfcPositiveRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("RateDateTime", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("RateSource", new named_type(IFC4_IfcLibraryInformation_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurrencyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCurtainWallTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurtainWall_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcCurtainWallTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurtainWallType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IFC4_IfcPlane_type), false));
        attributes.push_back(new entity::attribute("OuterBoundary", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4_IfcCurve_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurveBoundedPlane_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IFC4_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("Boundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcBoundaryCurve_type)), false));
        attributes.push_back(new entity::attribute("ImplicitOuter", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurveBoundedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("CurveFont", new named_type(IFC4_IfcCurveFontOrScaledCurveFontSelect_type), true));
        attributes.push_back(new entity::attribute("CurveWidth", new named_type(IFC4_IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("CurveColour", new named_type(IFC4_IfcColour_type), true));
        attributes.push_back(new entity::attribute("ModelOrDraughting", new named_type(IFC4_IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurveStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PatternList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcCurveStyleFontPattern_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurveStyleFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CurveFont", new named_type(IFC4_IfcCurveStyleFontSelect_type), false));
        attributes.push_back(new entity::attribute("CurveFontScaling", new named_type(IFC4_IfcPositiveRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurveStyleFontAndScaling_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VisibleSegmentLength", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InvisibleSegmentLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcCurveStyleFontPattern_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcCylindricalSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDamperTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDamper_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDamperTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDamperType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ParentProfile", new named_type(IFC4_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Operator", new named_type(IFC4_IfcCartesianTransformationOperator2D_type), false));
        attributes.push_back(new entity::attribute("Label", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDerivedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDerivedUnitElement_type)), false));
        attributes.push_back(new entity::attribute("UnitType", new named_type(IFC4_IfcDerivedUnitEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDerivedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC4_IfcNamedUnit_type), false));
        attributes.push_back(new entity::attribute("Exponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcDerivedUnitElement_type->set_attributes(attributes, derived);
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
        IFC4_IfcDimensionalExponents_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("DirectionRatios", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_IfcReal_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcDirection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDiscreteAccessoryTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDiscreteAccessory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDiscreteAccessoryTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDiscreteAccessoryType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDistributionChamberElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionChamberElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDistributionChamberElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionChamberElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionCircuit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionControlElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionControlElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionFlowElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionFlowElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("FlowDirection", new named_type(IFC4_IfcFlowDirectionEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDistributionPortTypeEnum_type), true));
        attributes.push_back(new entity::attribute("SystemType", new named_type(IFC4_IfcDistributionSystemEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionPort_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDistributionSystemEnum_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDistributionSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Location", new named_type(IFC4_IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("IntendedUse", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Scope", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Revision", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DocumentOwner", new named_type(IFC4_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("Editors", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcActorSelect_type)), true));
        attributes.push_back(new entity::attribute("CreationTime", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("LastRevisionTime", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ElectronicFormat", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("ValidFrom", new named_type(IFC4_IfcDate_type), true));
        attributes.push_back(new entity::attribute("ValidUntil", new named_type(IFC4_IfcDate_type), true));
        attributes.push_back(new entity::attribute("Confidentiality", new named_type(IFC4_IfcDocumentConfidentialityEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC4_IfcDocumentStatusEnum_type), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDocumentInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingDocument", new named_type(IFC4_IfcDocumentInformation_type), false));
        attributes.push_back(new entity::attribute("RelatedDocuments", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDocumentInformation_type)), false));
        attributes.push_back(new entity::attribute("RelationshipType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDocumentInformationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("ReferencedDocument", new named_type(IFC4_IfcDocumentInformation_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDocumentReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDoorTypeEnum_type), true));
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC4_IfcDoorTypeOperationEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedOperationType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDoor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(13);
        attributes.push_back(new entity::attribute("LiningDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningThickness", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdThickness", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomThickness", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomOffset", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningOffset", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdOffset", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CasingThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CasingDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC4_IfcShapeAspect_type), true));
        attributes.push_back(new entity::attribute("LiningToPanelOffsetX", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningToPanelOffsetY", new named_type(IFC4_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDoorLiningProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PanelDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PanelOperation", new named_type(IFC4_IfcDoorPanelOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelWidth", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IFC4_IfcDoorPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC4_IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDoorPanelProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDoorStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC4_IfcDoorStyleOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IFC4_IfcDoorStyleConstructionEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new named_type(IFC4_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Sizeable", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDoorStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDoorTypeEnum_type), false));
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC4_IfcDoorTypeOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new named_type(IFC4_IfcBoolean_type), true));
        attributes.push_back(new entity::attribute("UserDefinedOperationType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDoorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcDraughtingPreDefinedColour_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcDraughtingPreDefinedCurveFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDuctFittingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDuctFitting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDuctFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDuctFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDuctSegmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDuctSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDuctSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDuctSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDuctSilencerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDuctSilencer_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcDuctSilencerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcDuctSilencerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeStart", new named_type(IFC4_IfcVertex_type), false));
        attributes.push_back(new entity::attribute("EdgeEnd", new named_type(IFC4_IfcVertex_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcEdge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeGeometry", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("SameSense", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEdgeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcOrientedEdge_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcEdgeLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricApplianceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricAppliance_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricApplianceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricApplianceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricDistributionBoardTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricDistributionBoard_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricDistributionBoardTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricDistributionBoardType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricFlowStorageDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricFlowStorageDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricFlowStorageDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricFlowStorageDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricGeneratorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricGenerator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricGeneratorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricGeneratorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricMotorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricMotor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricMotorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricMotorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricTimeControlTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricTimeControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElectricTimeControlTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElectricTimeControlType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Tag", new named_type(IFC4_IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AssemblyPlace", new named_type(IFC4_IfcAssemblyPlaceEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElementAssemblyTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElementAssembly_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcElementAssemblyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElementAssemblyType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElementComponent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElementComponentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MethodOfMeasurement", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Quantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPhysicalQuantity_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElementQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ElementType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcElementarySurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SemiAxis1", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SemiAxis2", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEllipse_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SemiAxis1", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SemiAxis2", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEllipseProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEnergyConversionDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEnergyConversionDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcEngineTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEngine_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcEngineTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEngineType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcEvaporativeCoolerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEvaporativeCooler_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcEvaporativeCoolerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEvaporativeCoolerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcEvaporatorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEvaporator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcEvaporatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEvaporatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcEventTypeEnum_type), true));
        attributes.push_back(new entity::attribute("EventTriggerType", new named_type(IFC4_IfcEventTriggerTypeEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedEventTriggerType", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("EventOccurenceTime", new named_type(IFC4_IfcEventTime_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEvent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ActualDate", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("EarlyDate", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("LateDate", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ScheduleDate", new named_type(IFC4_IfcDateTime_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEventTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcEventTypeEnum_type), false));
        attributes.push_back(new entity::attribute("EventTriggerType", new named_type(IFC4_IfcEventTriggerTypeEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedEventTriggerType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcEventType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Properties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExtendedProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcExternalInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Location", new named_type(IFC4_IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExternalReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingReference", new named_type(IFC4_IfcExternalReference_type), false));
        attributes.push_back(new entity::attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcResourceObjectSelect_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExternalReferenceRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcExternalSpatialElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExternalSpatialElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExternalSpatialStructureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExternallyDefinedHatchStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExternallyDefinedSurfaceStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExternallyDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ExtrudedDirection", new named_type(IFC4_IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExtrudedAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EndSweptArea", new named_type(IFC4_IfcProfileDef_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcExtrudedAreaSolidTapered_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Bounds", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcFaceBound_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcFace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FbsmFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcConnectedFaceSet_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcFaceBasedSurfaceModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Bound", new named_type(IFC4_IfcLoop_type), false));
        attributes.push_back(new entity::attribute("Orientation", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcFaceBound_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcFaceOuterBound_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("FaceSurface", new named_type(IFC4_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("SameSense", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFaceSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcFacetedBrep_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcClosedShell_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcFacetedBrepWithVoids_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TensionFailureX", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("TensionFailureY", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("TensionFailureZ", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureX", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureY", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureZ", new named_type(IFC4_IfcForceMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFailureConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFanTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFan_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFanTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFanType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFastenerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFastener_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFastenerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFastenerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFeatureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFeatureElementAddition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFeatureElementSubtraction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("FillStyles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcFillStyleSelect_type)), false));
        attributes.push_back(new entity::attribute("ModelorDraughting", new named_type(IFC4_IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFillAreaStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("HatchLineAppearance", new named_type(IFC4_IfcCurveStyle_type), false));
        attributes.push_back(new entity::attribute("StartOfNextHatchLine", new named_type(IFC4_IfcHatchLineDistanceSelect_type), false));
        attributes.push_back(new entity::attribute("PointOfReferenceHatchLine", new named_type(IFC4_IfcCartesianPoint_type), true));
        attributes.push_back(new entity::attribute("PatternStart", new named_type(IFC4_IfcCartesianPoint_type), true));
        attributes.push_back(new entity::attribute("HatchLineAngle", new named_type(IFC4_IfcPlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFillAreaStyleHatching_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TilingPattern", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcVector_type)), false));
        attributes.push_back(new entity::attribute("Tiles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcStyledItem_type)), false));
        attributes.push_back(new entity::attribute("TilingScale", new named_type(IFC4_IfcPositiveRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFillAreaStyleTiles_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFilterTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFilter_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFilterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFilterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFireSuppressionTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFireSuppressionTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFireSuppressionTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFireSuppressionTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IFC4_IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IFC4_IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("FixedReference", new named_type(IFC4_IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFixedReferenceSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowController_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowControllerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowFitting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFlowInstrumentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowInstrument_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFlowInstrumentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowInstrumentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFlowMeterTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowMeter_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFlowMeterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowMeterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowMovingDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowMovingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowStorageDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowStorageDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowTreatmentDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFlowTreatmentDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFootingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFooting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFootingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFootingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFurnishingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFurnishingElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFurnitureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFurniture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AssemblyPlace", new named_type(IFC4_IfcAssemblyPlaceEnum_type), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcFurnitureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcFurnitureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcGeographicElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcGeographicElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcGeographicElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcGeographicElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcGeometricCurveSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("CoordinateSpaceDimension", new named_type(IFC4_IfcDimensionCount_type), false));
        attributes.push_back(new entity::attribute("Precision", new named_type(IFC4_IfcReal_type), true));
        attributes.push_back(new entity::attribute("WorldCoordinateSystem", new named_type(IFC4_IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("TrueNorth", new named_type(IFC4_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcGeometricRepresentationContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcGeometricRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ParentContext", new named_type(IFC4_IfcGeometricRepresentationContext_type), false));
        attributes.push_back(new entity::attribute("TargetScale", new named_type(IFC4_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("TargetView", new named_type(IFC4_IfcGeometricProjectionEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedTargetView", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcGeometricRepresentationSubContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcGeometricSetSelect_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcGeometricSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("UAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("VAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("WAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcGridAxis_type)), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcGridTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcGrid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("AxisTag", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("AxisCurve", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("SameSense", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcGridAxis_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PlacementLocation", new named_type(IFC4_IfcVirtualGridIntersection_type), false));
        attributes.push_back(new entity::attribute("PlacementRefDirection", new named_type(IFC4_IfcGridPlacementDirectionSelect_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcGridPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BaseSurface", new named_type(IFC4_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("AgreementFlag", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcHalfSpaceSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcHeatExchangerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcHeatExchanger_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcHeatExchangerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcHeatExchangerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcHumidifierTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcHumidifier_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcHumidifierTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcHumidifierType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("OverallDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeEdgeRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcIShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("URLReference", new named_type(IFC4_IfcURIReference_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcImageTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("MappedTo", new named_type(IFC4_IfcTessellatedFaceSet_type), false));
        attributes.push_back(new entity::attribute("Opacity", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Colours", new named_type(IFC4_IfcColourRgbList_type), false));
        attributes.push_back(new entity::attribute("ColourIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcPositiveInteger_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcIndexedColourMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Points", new named_type(IFC4_IfcCartesianPointList_type), false));
        attributes.push_back(new entity::attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcSegmentIndexSelect_type)), true));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IFC4_IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcIndexedPolyCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MappedTo", new named_type(IFC4_IfcTessellatedFaceSet_type), false));
        attributes.push_back(new entity::attribute("TexCoords", new named_type(IFC4_IfcTextureVertexList_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcIndexedTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TexCoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcPositiveInteger_type))), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcIndexedTriangleTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcInterceptorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcInterceptor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcInterceptorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcInterceptorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcInventoryTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Jurisdiction", new named_type(IFC4_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("ResponsiblePersons", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPerson_type)), true));
        attributes.push_back(new entity::attribute("LastUpdateDate", new named_type(IFC4_IfcDate_type), true));
        attributes.push_back(new entity::attribute("CurrentValue", new named_type(IFC4_IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("OriginalValue", new named_type(IFC4_IfcCostValue_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcInventory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcIrregularTimeSeriesValue_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcIrregularTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TimeStamp", new named_type(IFC4_IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcIrregularTimeSeriesValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcJunctionBoxTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcJunctionBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcJunctionBoxTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcJunctionBoxType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Width", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Thickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LegSlope", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcLaborResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLaborResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcLaborResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLaborResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LagValue", new named_type(IFC4_IfcTimeOrRatioSelect_type), false));
        attributes.push_back(new entity::attribute("DurationType", new named_type(IFC4_IfcTaskDurationEnum_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLagTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcLampTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLamp_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcLampTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLampType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Version", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Publisher", new named_type(IFC4_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("VersionDate", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("Location", new named_type(IFC4_IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLibraryInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Language", new named_type(IFC4_IfcLanguageId_type), true));
        attributes.push_back(new entity::attribute("ReferencedLibrary", new named_type(IFC4_IfcLibraryInformation_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLibraryReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MainPlaneAngle", new named_type(IFC4_IfcPlaneAngleMeasure_type), false));
        attributes.push_back(new entity::attribute("SecondaryPlaneAngle", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcPlaneAngleMeasure_type)), false));
        attributes.push_back(new entity::attribute("LuminousIntensity", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLuminousIntensityDistributionMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightDistributionData_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcLightFixtureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightFixture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcLightFixtureTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightFixtureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LightDistributionCurve", new named_type(IFC4_IfcLightDistributionCurveEnum_type), false));
        attributes.push_back(new entity::attribute("DistributionData", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLightDistributionData_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightIntensityDistribution_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LightColour", new named_type(IFC4_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("AmbientIntensity", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Intensity", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightSource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightSourceAmbient_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IFC4_IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightSourceDirectional_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcAxis2Placement3D_type), false));
        attributes.push_back(new entity::attribute("ColourAppearance", new named_type(IFC4_IfcColourRgb_type), true));
        attributes.push_back(new entity::attribute("ColourTemperature", new named_type(IFC4_IfcThermodynamicTemperatureMeasure_type), false));
        attributes.push_back(new entity::attribute("LuminousFlux", new named_type(IFC4_IfcLuminousFluxMeasure_type), false));
        attributes.push_back(new entity::attribute("LightEmissionSource", new named_type(IFC4_IfcLightEmissionSourceEnum_type), false));
        attributes.push_back(new entity::attribute("LightDistributionDataSource", new named_type(IFC4_IfcLightDistributionDataSourceSelect_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightSourceGoniometric_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ConstantAttenuation", new named_type(IFC4_IfcReal_type), false));
        attributes.push_back(new entity::attribute("DistanceAttenuation", new named_type(IFC4_IfcReal_type), false));
        attributes.push_back(new entity::attribute("QuadricAttenuation", new named_type(IFC4_IfcReal_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightSourcePositional_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IFC4_IfcDirection_type), false));
        attributes.push_back(new entity::attribute("ConcentrationExponent", new named_type(IFC4_IfcReal_type), true));
        attributes.push_back(new entity::attribute("SpreadAngle", new named_type(IFC4_IfcPositivePlaneAngleMeasure_type), false));
        attributes.push_back(new entity::attribute("BeamWidthAngle", new named_type(IFC4_IfcPositivePlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcLightSourceSpot_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Pnt", new named_type(IFC4_IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Dir", new named_type(IFC4_IfcVector_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcLine_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PlacementRelTo", new named_type(IFC4_IfcObjectPlacement_type), true));
        attributes.push_back(new entity::attribute("RelativePlacement", new named_type(IFC4_IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcLocalPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Outer", new named_type(IFC4_IfcClosedShell_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcManifoldSolidBrep_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Eastings", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Northings", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("OrthogonalHeight", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("XAxisAbscissa", new named_type(IFC4_IfcReal_type), true));
        attributes.push_back(new entity::attribute("XAxisOrdinate", new named_type(IFC4_IfcReal_type), true));
        attributes.push_back(new entity::attribute("Scale", new named_type(IFC4_IfcReal_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMapConversion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MappingSource", new named_type(IFC4_IfcRepresentationMap_type), false));
        attributes.push_back(new entity::attribute("MappingTarget", new named_type(IFC4_IfcCartesianTransformationOperator_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcMappedItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterial_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MaterialClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcClassificationSelect_type)), false));
        attributes.push_back(new entity::attribute("ClassifiedMaterial", new named_type(IFC4_IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialClassificationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Material", new named_type(IFC4_IfcMaterial_type), false));
        attributes.push_back(new entity::attribute("Fraction", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialConstituent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("MaterialConstituents", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcMaterialConstituent_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialConstituentSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcMaterialDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RepresentedMaterial", new named_type(IFC4_IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialDefinitionRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Material", new named_type(IFC4_IfcMaterial_type), true));
        attributes.push_back(new entity::attribute("LayerThickness", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("IsVentilated", new named_type(IFC4_IfcLogical_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Priority", new named_type(IFC4_IfcInteger_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialLayer_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MaterialLayers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcMaterialLayer_type)), false));
        attributes.push_back(new entity::attribute("LayerSetName", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialLayerSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ForLayerSet", new named_type(IFC4_IfcMaterialLayerSet_type), false));
        attributes.push_back(new entity::attribute("LayerSetDirection", new named_type(IFC4_IfcLayerSetDirectionEnum_type), false));
        attributes.push_back(new entity::attribute("DirectionSense", new named_type(IFC4_IfcDirectionSenseEnum_type), false));
        attributes.push_back(new entity::attribute("OffsetFromReferenceLine", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ReferenceExtent", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialLayerSetUsage_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OffsetDirection", new named_type(IFC4_IfcLayerSetDirectionEnum_type), false));
        attributes.push_back(new entity::attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4_IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialLayerWithOffsets_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Materials", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcMaterial_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcMaterialList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Material", new named_type(IFC4_IfcMaterial_type), true));
        attributes.push_back(new entity::attribute("Profile", new named_type(IFC4_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Priority", new named_type(IFC4_IfcInteger_type), true));
        attributes.push_back(new entity::attribute("Category", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialProfile_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("MaterialProfiles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcMaterialProfile_type)), false));
        attributes.push_back(new entity::attribute("CompositeProfile", new named_type(IFC4_IfcCompositeProfileDef_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialProfileSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ForProfileSet", new named_type(IFC4_IfcMaterialProfileSet_type), false));
        attributes.push_back(new entity::attribute("CardinalPoint", new named_type(IFC4_IfcCardinalPointReference_type), true));
        attributes.push_back(new entity::attribute("ReferenceExtent", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialProfileSetUsage_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ForProfileEndSet", new named_type(IFC4_IfcMaterialProfileSet_type), false));
        attributes.push_back(new entity::attribute("CardinalEndPoint", new named_type(IFC4_IfcCardinalPointReference_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialProfileSetUsageTapering_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4_IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialProfileWithOffsets_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Material", new named_type(IFC4_IfcMaterialDefinition_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingMaterial", new named_type(IFC4_IfcMaterial_type), false));
        attributes.push_back(new entity::attribute("RelatedMaterials", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcMaterial_type)), false));
        attributes.push_back(new entity::attribute("Expression", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMaterialRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcMaterialUsageDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ValueComponent", new named_type(IFC4_IfcValue_type), false));
        attributes.push_back(new entity::attribute("UnitComponent", new named_type(IFC4_IfcUnit_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcMeasureWithUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcMechanicalFastenerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMechanicalFastener_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcMechanicalFastenerTypeEnum_type), false));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMechanicalFastenerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcMedicalDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMedicalDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcMedicalDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMedicalDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcMemberTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMemberStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcMemberTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMemberType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Benchmark", new named_type(IFC4_IfcBenchmarkEnum_type), false));
        attributes.push_back(new entity::attribute("ValueSource", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DataValue", new named_type(IFC4_IfcMetricValueSelect_type), true));
        attributes.push_back(new entity::attribute("ReferencePath", new named_type(IFC4_IfcReference_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMetric_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(false);
        IFC4_IfcMirroredProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Currency", new named_type(IFC4_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcMonetaryUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcMotorConnectionTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMotorConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcMotorConnectionTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcMotorConnectionType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Dimensions", new named_type(IFC4_IfcDimensionalExponents_type), false));
        attributes.push_back(new entity::attribute("UnitType", new named_type(IFC4_IfcUnitEnum_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcNamedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ObjectType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcObjectDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcObjectPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BenchmarkValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcConstraint_type)), true));
        attributes.push_back(new entity::attribute("LogicalAggregator", new named_type(IFC4_IfcLogicalOperatorEnum_type), true));
        attributes.push_back(new entity::attribute("ObjectiveQualifier", new named_type(IFC4_IfcObjectiveEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedQualifier", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcObjective_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcOccupantTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOccupant_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Distance", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IFC4_IfcLogical_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOffsetCurve2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Distance", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new named_type(IFC4_IfcLogical_type), false));
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IFC4_IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOffsetCurve3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcOpenShell_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcOpeningElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOpeningElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOpeningStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcActorRole_type)), true));
        attributes.push_back(new entity::attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAddress_type)), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOrganization_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingOrganization", new named_type(IFC4_IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("RelatedOrganizations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcOrganization_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOrganizationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeElement", new named_type(IFC4_IfcEdge_type), false));
        attributes.push_back(new entity::attribute("Orientation", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOrientedEdge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcOuterBoundaryCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcOutletTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOutlet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcOutletTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOutletType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("OwningUser", new named_type(IFC4_IfcPersonAndOrganization_type), false));
        attributes.push_back(new entity::attribute("OwningApplication", new named_type(IFC4_IfcApplication_type), false));
        attributes.push_back(new entity::attribute("State", new named_type(IFC4_IfcStateEnum_type), true));
        attributes.push_back(new entity::attribute("ChangeAction", new named_type(IFC4_IfcChangeActionEnum_type), true));
        attributes.push_back(new entity::attribute("LastModifiedDate", new named_type(IFC4_IfcTimeStamp_type), true));
        attributes.push_back(new entity::attribute("LastModifyingUser", new named_type(IFC4_IfcPersonAndOrganization_type), true));
        attributes.push_back(new entity::attribute("LastModifyingApplication", new named_type(IFC4_IfcApplication_type), true));
        attributes.push_back(new entity::attribute("CreationDate", new named_type(IFC4_IfcTimeStamp_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcOwnerHistory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcAxis2Placement2D_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcParameterizedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcOrientedEdge_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPath_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IFC4_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("ReferenceCurve", new named_type(IFC4_IfcCurve_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcPcurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LifeCyclePhase", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPerformanceHistoryTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPerformanceHistory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC4_IfcPermeableCoveringOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IFC4_IfcWindowPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("FrameDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FrameThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC4_IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPermeableCoveringProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPermitTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPermit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("FamilyName", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("GivenName", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("MiddleNames", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PrefixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("SuffixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcActorRole_type)), true));
        attributes.push_back(new entity::attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAddress_type)), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPerson_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ThePerson", new named_type(IFC4_IfcPerson_type), false));
        attributes.push_back(new entity::attribute("TheOrganization", new named_type(IFC4_IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcActorRole_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPersonAndOrganization_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("HasQuantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPhysicalQuantity_type)), false));
        attributes.push_back(new entity::attribute("Discrimination", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Quality", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Usage", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPhysicalComplexQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcPhysicalQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC4_IfcNamedUnit_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPhysicalSimpleQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPileTypeEnum_type), true));
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IFC4_IfcPileConstructionEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPile_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPileTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPileType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPipeFittingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPipeFitting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPipeFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPipeFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPipeSegmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPipeSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPipeSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPipeSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Width", new named_type(IFC4_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("Height", new named_type(IFC4_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("ColourComponents", new named_type(IFC4_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("Pixel", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcBinary_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPixelTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Location", new named_type(IFC4_IfcCartesianPoint_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Placement", new named_type(IFC4_IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPlanarBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SizeInX", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SizeInY", new named_type(IFC4_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcPlanarExtent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPlane_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPlateTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPlate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPlateStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPlateTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPlateType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("PointParameter", new named_type(IFC4_IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcPointOnCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IFC4_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("PointParameterU", new named_type(IFC4_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("PointParameterV", new named_type(IFC4_IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPointOnSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Polygon", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_IfcCartesianPoint_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPolyLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcAxis2Placement3D_type), false));
        attributes.push_back(new entity::attribute("PolygonalBoundary", new named_type(IFC4_IfcBoundedCurve_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPolygonalBoundedHalfSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Points", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcCartesianPoint_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPolyline_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPort_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("InternalLocation", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("AddressLines", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PostalBox", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Town", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Region", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PostalCode", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Country", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPostalAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPreDefinedColour_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPreDefinedCurveFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPreDefinedItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcPreDefinedProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPreDefinedPropertySet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPreDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcPresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("AssignedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcLayeredItem_type)), false));
        attributes.push_back(new entity::attribute("Identifier", new named_type(IFC4_IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPresentationLayerAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("LayerOn", new named_type(IFC4_IfcLogical_type), false));
        attributes.push_back(new entity::attribute("LayerFrozen", new named_type(IFC4_IfcLogical_type), false));
        attributes.push_back(new entity::attribute("LayerBlocked", new named_type(IFC4_IfcLogical_type), false));
        attributes.push_back(new entity::attribute("LayerStyles", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4_IfcPresentationStyle_type)), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPresentationLayerWithStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPresentationStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPresentationStyleSelect_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcPresentationStyleAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcProcedureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProcedure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcProcedureTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProcedureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProcess_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ObjectPlacement", new named_type(IFC4_IfcObjectPlacement_type), true));
        attributes.push_back(new entity::attribute("Representation", new named_type(IFC4_IfcProductRepresentation_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProductDefinitionShape_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Representations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcRepresentation_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProductRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProfileType", new named_type(IFC4_IfcProfileTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ProfileName", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ProfileDefinition", new named_type(IFC4_IfcProfileDef_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProjectLibrary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcProjectOrderTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProjectOrder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MapProjection", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("MapZone", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("MapUnit", new named_type(IFC4_IfcNamedUnit_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProjectedCRS_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcProjectionElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProjectionElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcPropertyAbstraction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("UpperBoundValue", new named_type(IFC4_IfcValue_type), true));
        attributes.push_back(new entity::attribute("LowerBoundValue", new named_type(IFC4_IfcValue_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC4_IfcUnit_type), true));
        attributes.push_back(new entity::attribute("SetPointValue", new named_type(IFC4_IfcValue_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyBoundedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("DependingProperty", new named_type(IFC4_IfcProperty_type), false));
        attributes.push_back(new entity::attribute("DependantProperty", new named_type(IFC4_IfcProperty_type), false));
        attributes.push_back(new entity::attribute("Expression", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyDependencyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true));
        attributes.push_back(new entity::attribute("EnumerationReference", new named_type(IFC4_IfcPropertyEnumeration_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyEnumeratedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), false));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC4_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyEnumeration_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC4_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyListValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("PropertyReference", new named_type(IFC4_IfcObjectReferenceSelect_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyReferenceValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertySet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertySetDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TemplateType", new named_type(IFC4_IfcPropertySetTemplateTypeEnum_type), true));
        attributes.push_back(new entity::attribute("ApplicableEntity", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertyTemplate_type)), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertySetTemplate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("NominalValue", new named_type(IFC4_IfcValue_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC4_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertySingleValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("DefiningValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true));
        attributes.push_back(new entity::attribute("DefinedValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true));
        attributes.push_back(new entity::attribute("Expression", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("DefiningUnit", new named_type(IFC4_IfcUnit_type), true));
        attributes.push_back(new entity::attribute("DefinedUnit", new named_type(IFC4_IfcUnit_type), true));
        attributes.push_back(new entity::attribute("CurveInterpolation", new named_type(IFC4_IfcCurveInterpolationEnum_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyTableValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyTemplate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPropertyTemplateDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcProtectiveDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProtectiveDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProtectiveDeviceTrippingUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProtectiveDeviceTrippingUnitType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcProtectiveDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProtectiveDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProxyType", new named_type(IFC4_IfcObjectTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Tag", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcProxy_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPumpTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPump_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcPumpTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcPumpType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AreaValue", new named_type(IFC4_IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcQuantityArea_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CountValue", new named_type(IFC4_IfcCountMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcQuantityCount_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LengthValue", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcQuantityLength_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcQuantitySet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TimeValue", new named_type(IFC4_IfcTimeMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcQuantityTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VolumeValue", new named_type(IFC4_IfcVolumeMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcQuantityVolume_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("WeightValue", new named_type(IFC4_IfcMassMeasure_type), false));
        attributes.push_back(new entity::attribute("Formula", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcQuantityWeight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcRailingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRailing_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcRailingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRailingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcRampTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRamp_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcRampFlightTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRampFlight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcRampFlightTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRampFlightType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcRampTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRampType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcReal_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRationalBSplineCurveWithKnots_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcReal_type))), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRationalBSplineSurfaceWithKnots_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InnerFilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OuterFilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRectangleHollowProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("XDim", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRectangleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("XLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Height", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRectangularPyramid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IFC4_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("U1", new named_type(IFC4_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("V1", new named_type(IFC4_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("U2", new named_type(IFC4_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("V2", new named_type(IFC4_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("Usense", new named_type(IFC4_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Vsense", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRectangularTrimmedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("RecurrenceType", new named_type(IFC4_IfcRecurrenceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("DayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDayInMonthNumber_type)), true));
        attributes.push_back(new entity::attribute("WeekdayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDayInWeekNumber_type)), true));
        attributes.push_back(new entity::attribute("MonthComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcMonthInYearNumber_type)), true));
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcInteger_type), true));
        attributes.push_back(new entity::attribute("Interval", new named_type(IFC4_IfcInteger_type), true));
        attributes.push_back(new entity::attribute("Occurrences", new named_type(IFC4_IfcInteger_type), true));
        attributes.push_back(new entity::attribute("TimePeriods", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTimePeriod_type)), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRecurrencePattern_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("TypeIdentifier", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("AttributeIdentifier", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("InstanceName", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ListPositions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcInteger_type)), true));
        attributes.push_back(new entity::attribute("InnerReference", new named_type(IFC4_IfcReference_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TimeStep", new named_type(IFC4_IfcTimeMeasure_type), false));
        attributes.push_back(new entity::attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTimeSeriesValue_type)), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRegularTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TotalCrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("SteelGrade", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IFC4_IfcReinforcingBarSurfaceEnum_type), true));
        attributes.push_back(new entity::attribute("EffectiveDepth", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalBarDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BarCount", new named_type(IFC4_IfcCountMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReinforcementBarProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DefinitionType", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ReinforcementSectionDefinitions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcSectionReinforcementProperties_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReinforcementDefinitionProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("BarLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcReinforcingBarTypeEnum_type), true));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IFC4_IfcReinforcingBarSurfaceEnum_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReinforcingBar_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcReinforcingBarTypeEnum_type), false));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("BarLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IFC4_IfcReinforcingBarSurfaceEnum_type), true));
        attributes.push_back(new entity::attribute("BendingShapeCode", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcBendingParameterSelect_type)), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReinforcingBarType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SteelGrade", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReinforcingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReinforcingElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("MeshLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MeshWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarNominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarNominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarCrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarCrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarSpacing", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarSpacing", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcReinforcingMeshTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReinforcingMesh_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(11);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcReinforcingMeshTypeEnum_type), false));
        attributes.push_back(new entity::attribute("MeshLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MeshWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarNominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarNominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarCrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarCrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarSpacing", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransverseBarSpacing", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BendingShapeCode", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcBendingParameterSelect_type)), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReinforcingMeshType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingObject", new named_type(IFC4_IfcObjectDefinition_type), false));
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObjectDefinition_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAggregates_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObjectDefinition_type)), false));
        attributes.push_back(new entity::attribute("RelatedObjectsType", new named_type(IFC4_IfcObjectTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssigns_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingActor", new named_type(IFC4_IfcActor_type), false));
        attributes.push_back(new entity::attribute("ActingRole", new named_type(IFC4_IfcActorRole_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssignsToActor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingControl", new named_type(IFC4_IfcControl_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssignsToControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingGroup", new named_type(IFC4_IfcGroup_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssignsToGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Factor", new named_type(IFC4_IfcRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssignsToGroupByFactor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingProcess", new named_type(IFC4_IfcProcessSelect_type), false));
        attributes.push_back(new entity::attribute("QuantityInProcess", new named_type(IFC4_IfcMeasureWithUnit_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssignsToProcess_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingProduct", new named_type(IFC4_IfcProductSelect_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssignsToProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingResource", new named_type(IFC4_IfcResourceSelect_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssignsToResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDefinitionSelect_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssociates_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IFC4_IfcApproval_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssociatesApproval_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingClassification", new named_type(IFC4_IfcClassificationSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssociatesClassification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Intent", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IFC4_IfcConstraint_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssociatesConstraint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingDocument", new named_type(IFC4_IfcDocumentSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssociatesDocument_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingLibrary", new named_type(IFC4_IfcLibrarySelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssociatesLibrary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingMaterial", new named_type(IFC4_IfcMaterialSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelAssociatesMaterial_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnects_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ConnectionGeometry", new named_type(IFC4_IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IFC4_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IFC4_IfcElement_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnectsElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatingPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4_IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("RelatedPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4_IfcInteger_type)), false));
        attributes.push_back(new entity::attribute("RelatedConnectionType", new named_type(IFC4_IfcConnectionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("RelatingConnectionType", new named_type(IFC4_IfcConnectionTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnectsPathElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingPort", new named_type(IFC4_IfcPort_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IFC4_IfcDistributionElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnectsPortToElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingPort", new named_type(IFC4_IfcPort_type), false));
        attributes.push_back(new entity::attribute("RelatedPort", new named_type(IFC4_IfcPort_type), false));
        attributes.push_back(new entity::attribute("RealizingElement", new named_type(IFC4_IfcElement_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnectsPorts_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IFC4_IfcStructuralActivityAssignmentSelect_type), false));
        attributes.push_back(new entity::attribute("RelatedStructuralActivity", new named_type(IFC4_IfcStructuralActivity_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnectsStructuralActivity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("RelatingStructuralMember", new named_type(IFC4_IfcStructuralMember_type), false));
        attributes.push_back(new entity::attribute("RelatedStructuralConnection", new named_type(IFC4_IfcStructuralConnection_type), false));
        attributes.push_back(new entity::attribute("AppliedCondition", new named_type(IFC4_IfcBoundaryCondition_type), true));
        attributes.push_back(new entity::attribute("AdditionalConditions", new named_type(IFC4_IfcStructuralConnectionCondition_type), true));
        attributes.push_back(new entity::attribute("SupportedLength", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ConditionCoordinateSystem", new named_type(IFC4_IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnectsStructuralMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ConnectionConstraint", new named_type(IFC4_IfcConnectionGeometry_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnectsWithEccentricity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RealizingElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcElement_type)), false));
        attributes.push_back(new entity::attribute("ConnectionType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelConnectsWithRealizingElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProduct_type)), false));
        attributes.push_back(new entity::attribute("RelatingStructure", new named_type(IFC4_IfcSpatialElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelContainedInSpatialStructure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingBuildingElement", new named_type(IFC4_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcCovering_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelCoversBldgElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingSpace", new named_type(IFC4_IfcSpace_type), false));
        attributes.push_back(new entity::attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcCovering_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelCoversSpaces_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingContext", new named_type(IFC4_IfcContext_type), false));
        attributes.push_back(new entity::attribute("RelatedDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDefinitionSelect_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelDeclares_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelDecomposes_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelDefines_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObject_type)), false));
        attributes.push_back(new entity::attribute("RelatingObject", new named_type(IFC4_IfcObject_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelDefinesByObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObjectDefinition_type)), false));
        attributes.push_back(new entity::attribute("RelatingPropertyDefinition", new named_type(IFC4_IfcPropertySetDefinitionSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelDefinesByProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertySetDefinition_type)), false));
        attributes.push_back(new entity::attribute("RelatingTemplate", new named_type(IFC4_IfcPropertySetTemplate_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelDefinesByTemplate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObject_type)), false));
        attributes.push_back(new entity::attribute("RelatingType", new named_type(IFC4_IfcTypeObject_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelDefinesByType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingOpeningElement", new named_type(IFC4_IfcOpeningElement_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildingElement", new named_type(IFC4_IfcElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelFillsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedControlElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDistributionControlElement_type)), false));
        attributes.push_back(new entity::attribute("RelatingFlowElement", new named_type(IFC4_IfcDistributionFlowElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelFlowControlElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IFC4_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IFC4_IfcElement_type), false));
        attributes.push_back(new entity::attribute("InterferenceGeometry", new named_type(IFC4_IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("InterferenceType", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("ImpliedOrder", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelInterferesElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingObject", new named_type(IFC4_IfcObjectDefinition_type), false));
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcObjectDefinition_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelNests_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IFC4_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedFeatureElement", new named_type(IFC4_IfcFeatureElementAddition_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelProjectsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProduct_type)), false));
        attributes.push_back(new entity::attribute("RelatingStructure", new named_type(IFC4_IfcSpatialElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelReferencedInSpatialStructure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingProcess", new named_type(IFC4_IfcProcess_type), false));
        attributes.push_back(new entity::attribute("RelatedProcess", new named_type(IFC4_IfcProcess_type), false));
        attributes.push_back(new entity::attribute("TimeLag", new named_type(IFC4_IfcLagTime_type), true));
        attributes.push_back(new entity::attribute("SequenceType", new named_type(IFC4_IfcSequenceEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedSequenceType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelSequence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingSystem", new named_type(IFC4_IfcSystem_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcSpatialElement_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelServicesBuildings_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingSpace", new named_type(IFC4_IfcSpaceBoundarySelect_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildingElement", new named_type(IFC4_IfcElement_type), false));
        attributes.push_back(new entity::attribute("ConnectionGeometry", new named_type(IFC4_IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("PhysicalOrVirtualBoundary", new named_type(IFC4_IfcPhysicalOrVirtualEnum_type), false));
        attributes.push_back(new entity::attribute("InternalOrExternalBoundary", new named_type(IFC4_IfcInternalOrExternalEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelSpaceBoundary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ParentBoundary", new named_type(IFC4_IfcRelSpaceBoundary1stLevel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelSpaceBoundary1stLevel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CorrespondingBoundary", new named_type(IFC4_IfcRelSpaceBoundary2ndLevel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelSpaceBoundary2ndLevel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingBuildingElement", new named_type(IFC4_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedOpeningElement", new named_type(IFC4_IfcFeatureElementSubtraction_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelVoidsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ParamLength", new named_type(IFC4_IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcReparametrisedCompositeCurveSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ContextOfItems", new named_type(IFC4_IfcRepresentationContext_type), false));
        attributes.push_back(new entity::attribute("RepresentationIdentifier", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("RepresentationType", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Items", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcRepresentationItem_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ContextIdentifier", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ContextType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcRepresentationContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MappingOrigin", new named_type(IFC4_IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("MappedRepresentation", new named_type(IFC4_IfcRepresentation_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcRepresentationMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcResourceObjectSelect_type)), false));
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IFC4_IfcApproval_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcResourceApprovalRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IFC4_IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcResourceObjectSelect_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcResourceConstraintRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcResourceLevelRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(15);
        attributes.push_back(new entity::attribute("ScheduleWork", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("ScheduleUsage", new named_type(IFC4_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ScheduleStart", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ScheduleFinish", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ScheduleContour", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LevelingDelay", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("IsOverAllocated", new named_type(IFC4_IfcBoolean_type), true));
        attributes.push_back(new entity::attribute("StatusTime", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ActualWork", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("ActualUsage", new named_type(IFC4_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ActualStart", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ActualFinish", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("RemainingWork", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("RemainingUsage", new named_type(IFC4_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Completion", new named_type(IFC4_IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcResourceTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Axis", new named_type(IFC4_IfcAxis1Placement_type), false));
        attributes.push_back(new entity::attribute("Angle", new named_type(IFC4_IfcPlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRevolvedAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EndSweptArea", new named_type(IFC4_IfcProfileDef_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRevolvedAreaSolidTapered_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Height", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BottomRadius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRightCircularCone_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Height", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRightCircularCylinder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcRoofTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRoof_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcRoofTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRoofType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("GlobalId", new named_type(IFC4_IfcGloballyUniqueId_type), false));
        attributes.push_back(new entity::attribute("OwnerHistory", new named_type(IFC4_IfcOwnerHistory_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRoot_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RoundingRadius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcRoundedRectangleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Prefix", new named_type(IFC4_IfcSIPrefix_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcSIUnitName_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSIUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSanitaryTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSanitaryTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSanitaryTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSanitaryTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DataOrigin", new named_type(IFC4_IfcDataOriginEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedDataOrigin", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSchedulingTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SectionType", new named_type(IFC4_IfcSectionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("StartProfile", new named_type(IFC4_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("EndProfile", new named_type(IFC4_IfcProfileDef_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSectionProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LongitudinalStartPosition", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("LongitudinalEndPosition", new named_type(IFC4_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TransversePosition", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ReinforcementRole", new named_type(IFC4_IfcReinforcingBarRoleEnum_type), false));
        attributes.push_back(new entity::attribute("SectionDefinition", new named_type(IFC4_IfcSectionProperties_type), false));
        attributes.push_back(new entity::attribute("CrossSectionReinforcementDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcReinforcementBarProperties_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSectionReinforcementProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SpineCurve", new named_type(IFC4_IfcCompositeCurve_type), false));
        attributes.push_back(new entity::attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcProfileDef_type)), false));
        attributes.push_back(new entity::attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcAxis2Placement3D_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSectionedSpine_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSensorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSensor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSensorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSensorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcShadingDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcShadingDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcShadingDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcShadingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ShapeRepresentations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcShapeModel_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("ProductDefinitional", new named_type(IFC4_IfcLogical_type), false));
        attributes.push_back(new entity::attribute("PartOfProductDefinitionShape", new named_type(IFC4_IfcProductRepresentationSelect_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcShapeAspect_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcShapeModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcShapeRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SbsmBoundary", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcShell_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcShellBasedSurfaceModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcSimpleProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("TemplateType", new named_type(IFC4_IfcSimplePropertyTemplateTypeEnum_type), true));
        attributes.push_back(new entity::attribute("PrimaryMeasureType", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("SecondaryMeasureType", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Enumerators", new named_type(IFC4_IfcPropertyEnumeration_type), true));
        attributes.push_back(new entity::attribute("PrimaryUnit", new named_type(IFC4_IfcUnit_type), true));
        attributes.push_back(new entity::attribute("SecondaryUnit", new named_type(IFC4_IfcUnit_type), true));
        attributes.push_back(new entity::attribute("Expression", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("AccessState", new named_type(IFC4_IfcStateEnum_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSimplePropertyTemplate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RefLatitude", new named_type(IFC4_IfcCompoundPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RefLongitude", new named_type(IFC4_IfcCompoundPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RefElevation", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LandTitleNumber", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("SiteAddress", new named_type(IFC4_IfcPostalAddress_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSite_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSlabTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSlab_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSlabElementedCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSlabStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSlabTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSlabType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SlippageX", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("SlippageY", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("SlippageZ", new named_type(IFC4_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSlippageConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSolarDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSolarDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSolarDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSolarDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcSolidModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSpaceTypeEnum_type), true));
        attributes.push_back(new entity::attribute("ElevationWithFlooring", new named_type(IFC4_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSpaceHeaterTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpaceHeater_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSpaceHeaterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpaceHeaterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSpaceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpaceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpatialElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ElementType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpatialElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CompositionType", new named_type(IFC4_IfcElementCompositionEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpatialStructureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpatialStructureElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSpatialZoneTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpatialZone_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSpatialZoneTypeEnum_type), false));
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSpatialZoneType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcSphere_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStackTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStackTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStackTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStackTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStairTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStair_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("NumberOfRisers", new named_type(IFC4_IfcInteger_type), true));
        attributes.push_back(new entity::attribute("NumberOfTreads", new named_type(IFC4_IfcInteger_type), true));
        attributes.push_back(new entity::attribute("RiserHeight", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TreadLength", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStairFlightTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStairFlight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStairFlightTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStairFlightType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStairTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStairType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("DestabilizingLoad", new named_type(IFC4_IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AppliedLoad", new named_type(IFC4_IfcStructuralLoad_type), false));
        attributes.push_back(new entity::attribute("GlobalOrLocal", new named_type(IFC4_IfcGlobalOrLocalEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralActivity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcAnalysisModelTypeEnum_type), false));
        attributes.push_back(new entity::attribute("OrientationOf2DPlane", new named_type(IFC4_IfcAxis2Placement3D_type), true));
        attributes.push_back(new entity::attribute("LoadedBy", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcStructuralLoadGroup_type)), true));
        attributes.push_back(new entity::attribute("HasResults", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcStructuralResultGroup_type)), true));
        attributes.push_back(new entity::attribute("SharedPlacement", new named_type(IFC4_IfcObjectPlacement_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralAnalysisModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AppliedCondition", new named_type(IFC4_IfcBoundaryCondition_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcStructuralConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProjectedOrTrue", new named_type(IFC4_IfcProjectedOrTrueLengthEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStructuralCurveActivityTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralCurveAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Axis", new named_type(IFC4_IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralCurveConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStructuralCurveMemberTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Axis", new named_type(IFC4_IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralCurveMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralCurveMemberVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStructuralCurveActivityTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralCurveReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLinearAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcStructuralLoad_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SelfWeightCoefficients", new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcRatioMeasure_type)), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcStructuralLoadOrResult_type)), false));
        attributes.push_back(new entity::attribute("Locations", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4_IfcLengthMeasure_type))), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadConfiguration_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcLoadGroupTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ActionType", new named_type(IFC4_IfcActionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ActionSource", new named_type(IFC4_IfcActionSourceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Coefficient", new named_type(IFC4_IfcRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LinearForceX", new named_type(IFC4_IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearForceY", new named_type(IFC4_IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearForceZ", new named_type(IFC4_IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentX", new named_type(IFC4_IfcLinearMomentMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentY", new named_type(IFC4_IfcLinearMomentMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentZ", new named_type(IFC4_IfcLinearMomentMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadLinearForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcStructuralLoadOrResult_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PlanarForceX", new named_type(IFC4_IfcPlanarForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PlanarForceY", new named_type(IFC4_IfcPlanarForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PlanarForceZ", new named_type(IFC4_IfcPlanarForceMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadPlanarForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("DisplacementX", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("DisplacementY", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("DisplacementZ", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRX", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRY", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRZ", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadSingleDisplacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Distortion", new named_type(IFC4_IfcCurvatureMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadSingleDisplacementDistortion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("ForceX", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("ForceY", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("ForceZ", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentX", new named_type(IFC4_IfcTorqueMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentY", new named_type(IFC4_IfcTorqueMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentZ", new named_type(IFC4_IfcTorqueMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadSingleForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WarpingMoment", new named_type(IFC4_IfcWarpingMomentMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadSingleForceWarping_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcStructuralLoadStatic_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("DeltaTConstant", new named_type(IFC4_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("DeltaTY", new named_type(IFC4_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("DeltaTZ", new named_type(IFC4_IfcThermodynamicTemperatureMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralLoadTemperature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralPlanarAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralPointAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ConditionCoordinateSystem", new named_type(IFC4_IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralPointConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralPointReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TheoryType", new named_type(IFC4_IfcAnalysisTheoryTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ResultForLoadGroup", new named_type(IFC4_IfcStructuralLoadGroup_type), true));
        attributes.push_back(new entity::attribute("IsLinear", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralResultGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProjectedOrTrue", new named_type(IFC4_IfcProjectedOrTrueLengthEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStructuralSurfaceActivityTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralSurfaceAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralSurfaceConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStructuralSurfaceMemberTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Thickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralSurfaceMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralSurfaceMemberVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcStructuralSurfaceActivityTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStructuralSurfaceReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStyleModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Item", new named_type(IFC4_IfcRepresentationItem_type), true));
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcStyleAssignmentSelect_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStyledItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcStyledRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSubContractResourceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSubContractResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSubContractResourceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSubContractResourceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ParentEdge", new named_type(IFC4_IfcEdge_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSubedge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IFC4_IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IFC4_IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("ReferenceSurface", new named_type(IFC4_IfcSurface_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceCurveSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSurfaceFeatureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ExtrudedDirection", new named_type(IFC4_IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC4_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceOfLinearExtrusion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AxisPosition", new named_type(IFC4_IfcAxis1Placement_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceOfRevolution_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SurfaceReinforcement1", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_IfcLengthMeasure_type)), true));
        attributes.push_back(new entity::attribute("SurfaceReinforcement2", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_IfcLengthMeasure_type)), true));
        attributes.push_back(new entity::attribute("ShearReinforcement", new named_type(IFC4_IfcRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceReinforcementArea_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Side", new named_type(IFC4_IfcSurfaceSide_type), false));
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC4_IfcSurfaceStyleElementSelect_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("DiffuseTransmissionColour", new named_type(IFC4_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("DiffuseReflectionColour", new named_type(IFC4_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("TransmissionColour", new named_type(IFC4_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("ReflectanceColour", new named_type(IFC4_IfcColourRgb_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceStyleLighting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RefractionIndex", new named_type(IFC4_IfcReal_type), true));
        attributes.push_back(new entity::attribute("DispersionFactor", new named_type(IFC4_IfcReal_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceStyleRefraction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("DiffuseColour", new named_type(IFC4_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("TransmissionColour", new named_type(IFC4_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("DiffuseTransmissionColour", new named_type(IFC4_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("ReflectionColour", new named_type(IFC4_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("SpecularColour", new named_type(IFC4_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("SpecularHighlight", new named_type(IFC4_IfcSpecularHighlightSelect_type), true));
        attributes.push_back(new entity::attribute("ReflectanceMethod", new named_type(IFC4_IfcReflectanceMethodEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceStyleRendering_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SurfaceColour", new named_type(IFC4_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("Transparency", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceStyleShading_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Textures", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcSurfaceTexture_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcSurfaceStyleWithTextures_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RepeatS", new named_type(IFC4_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("RepeatT", new named_type(IFC4_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Mode", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("TextureTransform", new named_type(IFC4_IfcCartesianTransformationOperator2D_type), true));
        attributes.push_back(new entity::attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcIdentifier_type)), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSurfaceTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SweptArea", new named_type(IFC4_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InnerRadius", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IFC4_IfcParameterValue_type), true));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IFC4_IfcParameterValue_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSweptDiskSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSweptDiskSolidPolygonal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SweptCurve", new named_type(IFC4_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Position", new named_type(IFC4_IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcSweptSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSwitchingDeviceTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSwitchingDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSwitchingDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSwitchingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSystemFurnitureElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSystemFurnitureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcSystemFurnitureElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcSystemFurnitureElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeEdgeRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("WebEdgeRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("WebSlope", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Rows", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTableRow_type)), true));
        attributes.push_back(new entity::attribute("Columns", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTableColumn_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTable_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Identifier", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC4_IfcUnit_type), true));
        attributes.push_back(new entity::attribute("ReferencePath", new named_type(IFC4_IfcReference_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTableColumn_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RowCells", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true));
        attributes.push_back(new entity::attribute("IsHeading", new named_type(IFC4_IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcTableRow_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTankTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTank_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTankTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTankType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Status", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("WorkMethod", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("IsMilestone", new named_type(IFC4_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Priority", new named_type(IFC4_IfcInteger_type), true));
        attributes.push_back(new entity::attribute("TaskTime", new named_type(IFC4_IfcTaskTime_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTaskTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTask_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new entity::attribute("DurationType", new named_type(IFC4_IfcTaskDurationEnum_type), true));
        attributes.push_back(new entity::attribute("ScheduleDuration", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("ScheduleStart", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ScheduleFinish", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("EarlyStart", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("EarlyFinish", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("LateStart", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("LateFinish", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("FreeFloat", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("TotalFloat", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("IsCritical", new named_type(IFC4_IfcBoolean_type), true));
        attributes.push_back(new entity::attribute("StatusTime", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ActualDuration", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("ActualStart", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("ActualFinish", new named_type(IFC4_IfcDateTime_type), true));
        attributes.push_back(new entity::attribute("RemainingTime", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("Completion", new named_type(IFC4_IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTaskTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Recurrence", new named_type(IFC4_IfcRecurrencePattern_type), false));
        std::vector<bool> derived; derived.reserve(21);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTaskTimeRecurring_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTaskTypeEnum_type), false));
        attributes.push_back(new entity::attribute("WorkMethod", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTaskType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TelephoneNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("FacsimileNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PagerNumber", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ElectronicMailAddresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("WWWHomePageURL", new named_type(IFC4_IfcURIReference_type), true));
        attributes.push_back(new entity::attribute("MessagingIDs", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcURIReference_type)), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTelecomAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTendonTypeEnum_type), true));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("TensionForce", new named_type(IFC4_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PreStress", new named_type(IFC4_IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("FrictionCoefficient", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("AnchorageSlip", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MinCurvatureRadius", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTendon_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTendonAnchorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTendonAnchor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTendonAnchorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTendonAnchorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTendonTypeEnum_type), false));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IFC4_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("SheethDiameter", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTendonType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Coordinates", new named_type(IFC4_IfcCartesianPointList3D_type), false));
        attributes.push_back(new entity::attribute("Normals", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcParameterValue_type))), true));
        attributes.push_back(new entity::attribute("Closed", new named_type(IFC4_IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTessellatedFaceSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcTessellatedItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Literal", new named_type(IFC4_IfcPresentableText_type), false));
        attributes.push_back(new entity::attribute("Placement", new named_type(IFC4_IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("Path", new named_type(IFC4_IfcTextPath_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTextLiteral_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Extent", new named_type(IFC4_IfcPlanarExtent_type), false));
        attributes.push_back(new entity::attribute("BoxAlignment", new named_type(IFC4_IfcBoxAlignment_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTextLiteralWithExtent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("TextCharacterAppearance", new named_type(IFC4_IfcTextStyleForDefinedFont_type), true));
        attributes.push_back(new entity::attribute("TextStyle", new named_type(IFC4_IfcTextStyleTextModel_type), true));
        attributes.push_back(new entity::attribute("TextFontStyle", new named_type(IFC4_IfcTextFontSelect_type), false));
        attributes.push_back(new entity::attribute("ModelOrDraughting", new named_type(IFC4_IfcBoolean_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTextStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("FontFamily", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTextFontName_type)), false));
        attributes.push_back(new entity::attribute("FontStyle", new named_type(IFC4_IfcFontStyle_type), true));
        attributes.push_back(new entity::attribute("FontVariant", new named_type(IFC4_IfcFontVariant_type), true));
        attributes.push_back(new entity::attribute("FontWeight", new named_type(IFC4_IfcFontWeight_type), true));
        attributes.push_back(new entity::attribute("FontSize", new named_type(IFC4_IfcSizeSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTextStyleFontModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Colour", new named_type(IFC4_IfcColour_type), false));
        attributes.push_back(new entity::attribute("BackgroundColour", new named_type(IFC4_IfcColour_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcTextStyleForDefinedFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("TextIndent", new named_type(IFC4_IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("TextAlign", new named_type(IFC4_IfcTextAlignment_type), true));
        attributes.push_back(new entity::attribute("TextDecoration", new named_type(IFC4_IfcTextDecoration_type), true));
        attributes.push_back(new entity::attribute("LetterSpacing", new named_type(IFC4_IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("WordSpacing", new named_type(IFC4_IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("TextTransform", new named_type(IFC4_IfcTextTransformation_type), true));
        attributes.push_back(new entity::attribute("LineHeight", new named_type(IFC4_IfcSizeSelect_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTextStyleTextModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Maps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcSurfaceTexture_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcTextureCoordinate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Mode", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcReal_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTextureCoordinateGenerator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Vertices", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_IfcTextureVertex_type)), false));
        attributes.push_back(new entity::attribute("MappedTo", new named_type(IFC4_IfcFace_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcParameterValue_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcTextureVertex_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TexCoordsList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcParameterValue_type))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcTextureVertexList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("StartTime", new named_type(IFC4_IfcTime_type), false));
        attributes.push_back(new entity::attribute("EndTime", new named_type(IFC4_IfcTime_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcTimePeriod_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC4_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("StartTime", new named_type(IFC4_IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("EndTime", new named_type(IFC4_IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("TimeSeriesDataType", new named_type(IFC4_IfcTimeSeriesDataTypeEnum_type), false));
        attributes.push_back(new entity::attribute("DataOrigin", new named_type(IFC4_IfcDataOriginEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedDataOrigin", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC4_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcTimeSeriesValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcTopologicalRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTopologyRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTransformerTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTransformer_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTransformerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTransformerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTransportElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTransportElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTransportElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTransportElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BottomXDim", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopXDim", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopXOffset", new named_type(IFC4_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTrapeziumProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcPositiveInteger_type))), false));
        attributes.push_back(new entity::attribute("NormalIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcPositiveInteger_type))), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTriangulatedFaceSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IFC4_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Trim1", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4_IfcTrimmingSelect_type)), false));
        attributes.push_back(new entity::attribute("Trim2", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4_IfcTrimmingSelect_type)), false));
        attributes.push_back(new entity::attribute("SenseAgreement", new named_type(IFC4_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("MasterRepresentation", new named_type(IFC4_IfcTrimmingPreference_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTrimmedCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTubeBundleTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTubeBundle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcTubeBundleTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTubeBundleType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ApplicableOccurrence", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("HasPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertySetDefinition_type)), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTypeObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("ProcessType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTypeProcess_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RepresentationMaps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcRepresentationMap_type)), true));
        attributes.push_back(new entity::attribute("Tag", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTypeProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Identification", new named_type(IFC4_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("LongDescription", new named_type(IFC4_IfcText_type), true));
        attributes.push_back(new entity::attribute("ResourceType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcTypeResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IFC4_IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcUShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Units", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcUnit_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcUnitAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcUnitaryControlElementTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcUnitaryControlElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcUnitaryControlElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcUnitaryControlElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcUnitaryEquipmentTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcUnitaryEquipment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcUnitaryEquipmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcUnitaryEquipmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcValveTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcValve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcValveTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcValveType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IFC4_IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Magnitude", new named_type(IFC4_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcVector_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC4_IfcVertex_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LoopVertex", new named_type(IFC4_IfcVertex_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcVertexLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("VertexGeometry", new named_type(IFC4_IfcPoint_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC4_IfcVertexPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcVibrationIsolatorTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcVibrationIsolator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcVibrationIsolatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcVibrationIsolatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcVirtualElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("IntersectingAxes", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("OffsetDistances", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC4_IfcVirtualGridIntersection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcVoidingFeatureTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcVoidingFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWallTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWall_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWallElementedCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWallStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWallTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWallType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWasteTerminalTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWasteTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWasteTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWasteTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWindowTypeEnum_type), true));
        attributes.push_back(new entity::attribute("PartitioningType", new named_type(IFC4_IfcWindowTypePartitioningEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPartitioningType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWindow_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::attribute("LiningDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningThickness", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomThickness", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MullionThickness", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FirstTransomOffset", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SecondTransomOffset", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("FirstMullionOffset", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SecondMullionOffset", new named_type(IFC4_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC4_IfcShapeAspect_type), true));
        attributes.push_back(new entity::attribute("LiningOffset", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningToPanelOffsetX", new named_type(IFC4_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningToPanelOffsetY", new named_type(IFC4_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWindowLiningProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC4_IfcWindowPanelOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IFC4_IfcWindowPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("FrameDepth", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FrameThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC4_IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWindowPanelProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWindowStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IFC4_IfcWindowStyleConstructionEnum_type), false));
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC4_IfcWindowStyleOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new named_type(IFC4_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("Sizeable", new named_type(IFC4_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWindowStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWindowTypeEnum_type), false));
        attributes.push_back(new entity::attribute("PartitioningType", new named_type(IFC4_IfcWindowTypePartitioningEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new named_type(IFC4_IfcBoolean_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPartitioningType", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWindowType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("WorkingTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcWorkTime_type)), true));
        attributes.push_back(new entity::attribute("ExceptionTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcWorkTime_type)), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWorkCalendarTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWorkCalendar_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("CreationDate", new named_type(IFC4_IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("Creators", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPerson_type)), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IFC4_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Duration", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("TotalFloat", new named_type(IFC4_IfcDuration_type), true));
        attributes.push_back(new entity::attribute("StartTime", new named_type(IFC4_IfcDateTime_type), false));
        attributes.push_back(new entity::attribute("FinishTime", new named_type(IFC4_IfcDateTime_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWorkControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWorkPlanTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWorkPlan_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC4_IfcWorkScheduleTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWorkSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RecurrencePattern", new named_type(IFC4_IfcRecurrencePattern_type), true));
        attributes.push_back(new entity::attribute("Start", new named_type(IFC4_IfcDate_type), true));
        attributes.push_back(new entity::attribute("Finish", new named_type(IFC4_IfcDate_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcWorkTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IFC4_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcZShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC4_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC4_IfcZone_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("IsActingUpon", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToActor_type, IFC4_IfcRelAssignsToActor_type->attributes()[0]));
        IFC4_IfcActor_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasExternalReference", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        IFC4_IfcActorRole_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("OfPerson", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcPerson_type, IFC4_IfcPerson_type->attributes()[7]));
        attributes.push_back(new entity::inverse_attribute("OfOrganization", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcOrganization_type, IFC4_IfcOrganization_type->attributes()[4]));
        IFC4_IfcAddress_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelContainedInSpatialStructure_type, IFC4_IfcRelContainedInSpatialStructure_type->attributes()[0]));
        IFC4_IfcAnnotation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasExternalReference", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        IFC4_IfcAppliedValue_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::inverse_attribute("HasExternalReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ApprovedObjects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesApproval_type, IFC4_IfcRelAssociatesApproval_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ApprovedResources", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcResourceApprovalRelationship_type, IFC4_IfcResourceApprovalRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsRelatedWith", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcApprovalRelationship_type, IFC4_IfcApprovalRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("Relates", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcApprovalRelationship_type, IFC4_IfcApprovalRelationship_type->attributes()[0]));
        IFC4_IfcApproval_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("ClassificationForObjects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesClassification_type, IFC4_IfcRelAssociatesClassification_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcClassificationReference_type, IFC4_IfcClassificationReference_type->attributes()[0]));
        IFC4_IfcClassification_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("ClassificationRefForObjects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesClassification_type, IFC4_IfcRelAssociatesClassification_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcClassificationReference_type, IFC4_IfcClassificationReference_type->attributes()[0]));
        IFC4_IfcClassificationReference_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("UsingCurves", entity::inverse_attribute::set_type, 1, -1, IFC4_IfcCompositeCurve_type, IFC4_IfcCompositeCurve_type->attributes()[0]));
        IFC4_IfcCompositeCurveSegment_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasExternalReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("PropertiesForConstraint", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcResourceConstraintRelationship_type, IFC4_IfcResourceConstraintRelationship_type->attributes()[0]));
        IFC4_IfcConstraint_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("IsDefinedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByProperties_type, IFC4_IfcRelDefinesByProperties_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Declares", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelDeclares_type, IFC4_IfcRelDeclares_type->attributes()[0]));
        IFC4_IfcContext_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasExternalReference", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        IFC4_IfcContextDependentUnit_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Controls", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToControl_type, IFC4_IfcRelAssignsToControl_type->attributes()[0]));
        IFC4_IfcControl_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasExternalReference", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        IFC4_IfcConversionBasedUnit_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasCoordinateOperation", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcCoordinateOperation_type, IFC4_IfcCoordinateOperation_type->attributes()[0]));
        IFC4_IfcCoordinateReferenceSystem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("CoversSpaces", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelCoversSpaces_type, IFC4_IfcRelCoversSpaces_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("CoversElements", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelCoversBldgElements_type, IFC4_IfcRelCoversBldgElements_type->attributes()[1]));
        IFC4_IfcCovering_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedToFlowElement", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelFlowControlElements_type, IFC4_IfcRelFlowControlElements_type->attributes()[0]));
        IFC4_IfcDistributionControlElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasPorts", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsPortToElement_type, IFC4_IfcRelConnectsPortToElement_type->attributes()[1]));
        IFC4_IfcDistributionElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasControlElements", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelFlowControlElements_type, IFC4_IfcRelFlowControlElements_type->attributes()[1]));
        IFC4_IfcDistributionFlowElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::inverse_attribute("DocumentInfoForObjects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesDocument_type, IFC4_IfcRelAssociatesDocument_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasDocumentReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcDocumentReference_type, IFC4_IfcDocumentReference_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsPointedTo", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcDocumentInformationRelationship_type, IFC4_IfcDocumentInformationRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsPointer", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcDocumentInformationRelationship_type, IFC4_IfcDocumentInformationRelationship_type->attributes()[0]));
        IFC4_IfcDocumentInformation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("DocumentRefForObjects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesDocument_type, IFC4_IfcRelAssociatesDocument_type->attributes()[0]));
        IFC4_IfcDocumentReference_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::inverse_attribute("FillsVoids", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelFillsElement_type, IFC4_IfcRelFillsElement_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedTo", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsElements_type, IFC4_IfcRelConnectsElements_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsInterferedByElements", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelInterferesElements_type, IFC4_IfcRelInterferesElements_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("InterferesElements", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelInterferesElements_type, IFC4_IfcRelInterferesElements_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasProjections", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelProjectsElement_type, IFC4_IfcRelProjectsElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ReferencedInStructures", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelReferencedInSpatialStructure_type, IFC4_IfcRelReferencedInSpatialStructure_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasOpenings", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelVoidsElement_type, IFC4_IfcRelVoidsElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsConnectionRealization", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsWithRealizingElements_type, IFC4_IfcRelConnectsWithRealizingElements_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ProvidesBoundaries", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelSpaceBoundary_type, IFC4_IfcRelSpaceBoundary_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedFrom", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsElements_type, IFC4_IfcRelConnectsElements_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelContainedInSpatialStructure_type, IFC4_IfcRelContainedInSpatialStructure_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasCoverings", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelCoversBldgElements_type, IFC4_IfcRelCoversBldgElements_type->attributes()[0]));
        IFC4_IfcElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ExternalReferenceForResources", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[0]));
        IFC4_IfcExternalReference_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("BoundedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelSpaceBoundary_type, IFC4_IfcRelSpaceBoundary_type->attributes()[0]));
        IFC4_IfcExternalSpatialElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasTextureMaps", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcTextureMap_type, IFC4_IfcTextureMap_type->attributes()[1]));
        IFC4_IfcFace_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ProjectsElements", entity::inverse_attribute::unspecified_type, -1, -1, IFC4_IfcRelProjectsElement_type, IFC4_IfcRelProjectsElement_type->attributes()[1]));
        IFC4_IfcFeatureElementAddition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("VoidsElements", entity::inverse_attribute::unspecified_type, -1, -1, IFC4_IfcRelVoidsElement_type, IFC4_IfcRelVoidsElement_type->attributes()[1]));
        IFC4_IfcFeatureElementSubtraction_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasSubContexts", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcGeometricRepresentationSubContext_type, IFC4_IfcGeometricRepresentationSubContext_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasCoordinateOperation", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcCoordinateOperation_type, IFC4_IfcCoordinateOperation_type->attributes()[0]));
        IFC4_IfcGeometricRepresentationContext_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelContainedInSpatialStructure_type, IFC4_IfcRelContainedInSpatialStructure_type->attributes()[0]));
        IFC4_IfcGrid_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::inverse_attribute("PartOfW", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcGrid_type, IFC4_IfcGrid_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("PartOfV", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcGrid_type, IFC4_IfcGrid_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("PartOfU", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcGrid_type, IFC4_IfcGrid_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasIntersections", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcVirtualGridIntersection_type, IFC4_IfcVirtualGridIntersection_type->attributes()[0]));
        IFC4_IfcGridAxis_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("IsGroupedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToGroup_type, IFC4_IfcRelAssignsToGroup_type->attributes()[0]));
        IFC4_IfcGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("LibraryInfoForObjects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesLibrary_type, IFC4_IfcRelAssociatesLibrary_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasLibraryReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcLibraryReference_type, IFC4_IfcLibraryReference_type->attributes()[2]));
        IFC4_IfcLibraryInformation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("LibraryRefForObjects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesLibrary_type, IFC4_IfcRelAssociatesLibrary_type->attributes()[0]));
        IFC4_IfcLibraryReference_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("HasRepresentation", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcMaterialDefinitionRepresentation_type, IFC4_IfcMaterialDefinitionRepresentation_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsRelatedWith", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcMaterialRelationship_type, IFC4_IfcMaterialRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("RelatesTo", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcMaterialRelationship_type, IFC4_IfcMaterialRelationship_type->attributes()[0]));
        IFC4_IfcMaterial_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ToMaterialConstituentSet", entity::inverse_attribute::unspecified_type, -1, -1, IFC4_IfcMaterialConstituentSet_type, IFC4_IfcMaterialConstituentSet_type->attributes()[2]));
        IFC4_IfcMaterialConstituent_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("AssociatedTo", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesMaterial_type, IFC4_IfcRelAssociatesMaterial_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasExternalReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasProperties", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcMaterialProperties_type, IFC4_IfcMaterialProperties_type->attributes()[0]));
        IFC4_IfcMaterialDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ToMaterialLayerSet", entity::inverse_attribute::unspecified_type, -1, -1, IFC4_IfcMaterialLayerSet_type, IFC4_IfcMaterialLayerSet_type->attributes()[0]));
        IFC4_IfcMaterialLayer_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ToMaterialProfileSet", entity::inverse_attribute::unspecified_type, -1, -1, IFC4_IfcMaterialProfileSet_type, IFC4_IfcMaterialProfileSet_type->attributes()[2]));
        IFC4_IfcMaterialProfile_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssociatedTo", entity::inverse_attribute::set_type, 1, -1, IFC4_IfcRelAssociatesMaterial_type, IFC4_IfcRelAssociatesMaterial_type->attributes()[0]));
        IFC4_IfcMaterialUsageDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::inverse_attribute("IsDeclaredBy", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelDefinesByObject_type, IFC4_IfcRelDefinesByObject_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Declares", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByObject_type, IFC4_IfcRelDefinesByObject_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsTypedBy", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelDefinesByType_type, IFC4_IfcRelDefinesByType_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsDefinedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByProperties_type, IFC4_IfcRelDefinesByProperties_type->attributes()[0]));
        IFC4_IfcObject_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::inverse_attribute("HasAssignments", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssigns_type, IFC4_IfcRelAssigns_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Nests", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelNests_type, IFC4_IfcRelNests_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsNestedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelNests_type, IFC4_IfcRelNests_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasContext", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelDeclares_type, IFC4_IfcRelDeclares_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsDecomposedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAggregates_type, IFC4_IfcRelAggregates_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Decomposes", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelAggregates_type, IFC4_IfcRelAggregates_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasAssociations", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociates_type, IFC4_IfcRelAssociates_type->attributes()[0]));
        IFC4_IfcObjectDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("PlacesObject", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcProduct_type, IFC4_IfcProduct_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ReferencedByPlacements", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcLocalPlacement_type, IFC4_IfcLocalPlacement_type->attributes()[0]));
        IFC4_IfcObjectPlacement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasFillings", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelFillsElement_type, IFC4_IfcRelFillsElement_type->attributes()[0]));
        IFC4_IfcOpeningElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("IsRelatedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcOrganizationRelationship_type, IFC4_IfcOrganizationRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("Relates", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcOrganizationRelationship_type, IFC4_IfcOrganizationRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Engages", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcPersonAndOrganization_type, IFC4_IfcPersonAndOrganization_type->attributes()[1]));
        IFC4_IfcOrganization_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("EngagedIn", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcPersonAndOrganization_type, IFC4_IfcPersonAndOrganization_type->attributes()[0]));
        IFC4_IfcPerson_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasExternalReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("PartOfComplex", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcPhysicalComplexQuantity_type, IFC4_IfcPhysicalComplexQuantity_type->attributes()[0]));
        IFC4_IfcPhysicalQuantity_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("ContainedIn", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelConnectsPortToElement_type, IFC4_IfcRelConnectsPortToElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ConnectedFrom", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelConnectsPorts_type, IFC4_IfcRelConnectsPorts_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedTo", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelConnectsPorts_type, IFC4_IfcRelConnectsPorts_type->attributes()[0]));
        IFC4_IfcPort_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("IsPredecessorTo", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelSequence_type, IFC4_IfcRelSequence_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsSuccessorFrom", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelSequence_type, IFC4_IfcRelSequence_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("OperatesOn", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToProcess_type, IFC4_IfcRelAssignsToProcess_type->attributes()[0]));
        IFC4_IfcProcess_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ReferencedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToProduct_type, IFC4_IfcRelAssignsToProduct_type->attributes()[0]));
        IFC4_IfcProduct_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("ShapeOfProduct", entity::inverse_attribute::set_type, 1, -1, IFC4_IfcProduct_type, IFC4_IfcProduct_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasShapeAspects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcShapeAspect_type, IFC4_IfcShapeAspect_type->attributes()[4]));
        IFC4_IfcProductDefinitionShape_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasExternalReference", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasProperties", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcProfileProperties_type, IFC4_IfcProfileProperties_type->attributes()[0]));
        IFC4_IfcProfileDef_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::inverse_attribute("PartOfPset", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcPropertySet_type, IFC4_IfcPropertySet_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("PropertyForDependance", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcPropertyDependencyRelationship_type, IFC4_IfcPropertyDependencyRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("PropertyDependsOn", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcPropertyDependencyRelationship_type, IFC4_IfcPropertyDependencyRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("PartOfComplex", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcComplexProperty_type, IFC4_IfcComplexProperty_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasConstraints", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcResourceConstraintRelationship_type, IFC4_IfcResourceConstraintRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasApprovals", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcResourceApprovalRelationship_type, IFC4_IfcResourceApprovalRelationship_type->attributes()[0]));
        IFC4_IfcProperty_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasExternalReferences", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        IFC4_IfcPropertyAbstraction_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasContext", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelDeclares_type, IFC4_IfcRelDeclares_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasAssociations", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociates_type, IFC4_IfcRelAssociates_type->attributes()[0]));
        IFC4_IfcPropertyDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("DefinesType", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcTypeObject_type, IFC4_IfcTypeObject_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsDefinedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByTemplate_type, IFC4_IfcRelDefinesByTemplate_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("DefinesOccurrence", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByProperties_type, IFC4_IfcRelDefinesByProperties_type->attributes()[1]));
        IFC4_IfcPropertySetDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Defines", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByTemplate_type, IFC4_IfcRelDefinesByTemplate_type->attributes()[1]));
        IFC4_IfcPropertySetTemplate_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("PartOfComplexTemplate", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcComplexPropertyTemplate_type, IFC4_IfcComplexPropertyTemplate_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("PartOfPsetTemplate", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcPropertySetTemplate_type, IFC4_IfcPropertySetTemplate_type->attributes()[2]));
        IFC4_IfcPropertyTemplate_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("InnerBoundaries", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelSpaceBoundary1stLevel_type, IFC4_IfcRelSpaceBoundary1stLevel_type->attributes()[0]));
        IFC4_IfcRelSpaceBoundary1stLevel_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Corresponds", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelSpaceBoundary2ndLevel_type, IFC4_IfcRelSpaceBoundary2ndLevel_type->attributes()[0]));
        IFC4_IfcRelSpaceBoundary2ndLevel_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("RepresentationMap", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRepresentationMap_type, IFC4_IfcRepresentationMap_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("LayerAssignments", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcPresentationLayerAssignment_type, IFC4_IfcPresentationLayerAssignment_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("OfProductRepresentation", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcProductRepresentation_type, IFC4_IfcProductRepresentation_type->attributes()[2]));
        IFC4_IfcRepresentation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("RepresentationsInContext", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRepresentation_type, IFC4_IfcRepresentation_type->attributes()[0]));
        IFC4_IfcRepresentationContext_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("LayerAssignment", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcPresentationLayerAssignment_type, IFC4_IfcPresentationLayerAssignment_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("StyledByItem", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcStyledItem_type, IFC4_IfcStyledItem_type->attributes()[0]));
        IFC4_IfcRepresentationItem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasShapeAspects", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcShapeAspect_type, IFC4_IfcShapeAspect_type->attributes()[4]));
        attributes.push_back(new entity::inverse_attribute("MapUsage", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcMappedItem_type, IFC4_IfcMappedItem_type->attributes()[0]));
        IFC4_IfcRepresentationMap_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ResourceOf", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToResource_type, IFC4_IfcRelAssignsToResource_type->attributes()[0]));
        IFC4_IfcResource_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("OfShapeAspect", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcShapeAspect_type, IFC4_IfcShapeAspect_type->attributes()[0]));
        IFC4_IfcShapeModel_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasCoverings", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelCoversSpaces_type, IFC4_IfcRelCoversSpaces_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("BoundedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelSpaceBoundary_type, IFC4_IfcRelSpaceBoundary_type->attributes()[0]));
        IFC4_IfcSpace_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("ContainsElements", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelContainedInSpatialStructure_type, IFC4_IfcRelContainedInSpatialStructure_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ServicedBySystems", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelServicesBuildings_type, IFC4_IfcRelServicesBuildings_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ReferencesElements", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelReferencedInSpatialStructure_type, IFC4_IfcRelReferencedInSpatialStructure_type->attributes()[1]));
        IFC4_IfcSpatialElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedToStructuralItem", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelConnectsStructuralActivity_type, IFC4_IfcRelConnectsStructuralActivity_type->attributes()[1]));
        IFC4_IfcStructuralActivity_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ConnectsStructuralMembers", entity::inverse_attribute::set_type, 1, -1, IFC4_IfcRelConnectsStructuralMember_type, IFC4_IfcRelConnectsStructuralMember_type->attributes()[1]));
        IFC4_IfcStructuralConnection_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedStructuralActivity", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsStructuralActivity_type, IFC4_IfcRelConnectsStructuralActivity_type->attributes()[0]));
        IFC4_IfcStructuralItem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("SourceOfResultGroup", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcStructuralResultGroup_type, IFC4_IfcStructuralResultGroup_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("LoadGroupFor", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcStructuralAnalysisModel_type, IFC4_IfcStructuralAnalysisModel_type->attributes()[2]));
        IFC4_IfcStructuralLoadGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ConnectedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsStructuralMember_type, IFC4_IfcRelConnectsStructuralMember_type->attributes()[0]));
        IFC4_IfcStructuralMember_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ResultGroupFor", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcStructuralAnalysisModel_type, IFC4_IfcStructuralAnalysisModel_type->attributes()[3]));
        IFC4_IfcStructuralResultGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("IsMappedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcTextureCoordinate_type, IFC4_IfcTextureCoordinate_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("UsedInStyles", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcSurfaceStyleWithTextures_type, IFC4_IfcSurfaceStyleWithTextures_type->attributes()[0]));
        IFC4_IfcSurfaceTexture_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ServicesBuildings", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelServicesBuildings_type, IFC4_IfcRelServicesBuildings_type->attributes()[0]));
        IFC4_IfcSystem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasColours", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcIndexedColourMap_type, IFC4_IfcIndexedColourMap_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasTextures", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcIndexedTextureMap_type, IFC4_IfcIndexedTextureMap_type->attributes()[0]));
        IFC4_IfcTessellatedFaceSet_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasExternalReference", entity::inverse_attribute::set_type, 1, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]));
        IFC4_IfcTimeSeries_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Types", entity::inverse_attribute::set_type, 0, 1, IFC4_IfcRelDefinesByType_type, IFC4_IfcRelDefinesByType_type->attributes()[1]));
        IFC4_IfcTypeObject_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("OperatesOn", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToProcess_type, IFC4_IfcRelAssignsToProcess_type->attributes()[0]));
        IFC4_IfcTypeProcess_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ReferencedBy", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToProduct_type, IFC4_IfcRelAssignsToProduct_type->attributes()[0]));
        IFC4_IfcTypeProduct_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ResourceOf", entity::inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToResource_type, IFC4_IfcRelAssignsToResource_type->attributes()[0]));
        IFC4_IfcTypeResource_type->set_inverse_attributes(attributes);
    }

    std::vector<const declaration*> declarations; declarations.reserve(1165);
    declarations.push_back(IFC4_IfcAbsorbedDoseMeasure_type);
    declarations.push_back(IFC4_IfcAccelerationMeasure_type);
    declarations.push_back(IFC4_IfcAmountOfSubstanceMeasure_type);
    declarations.push_back(IFC4_IfcAngularVelocityMeasure_type);
    declarations.push_back(IFC4_IfcArcIndex_type);
    declarations.push_back(IFC4_IfcAreaDensityMeasure_type);
    declarations.push_back(IFC4_IfcAreaMeasure_type);
    declarations.push_back(IFC4_IfcBinary_type);
    declarations.push_back(IFC4_IfcBoolean_type);
    declarations.push_back(IFC4_IfcCardinalPointReference_type);
    declarations.push_back(IFC4_IfcComplexNumber_type);
    declarations.push_back(IFC4_IfcCompoundPlaneAngleMeasure_type);
    declarations.push_back(IFC4_IfcContextDependentMeasure_type);
    declarations.push_back(IFC4_IfcCountMeasure_type);
    declarations.push_back(IFC4_IfcCurvatureMeasure_type);
    declarations.push_back(IFC4_IfcDate_type);
    declarations.push_back(IFC4_IfcDateTime_type);
    declarations.push_back(IFC4_IfcDayInMonthNumber_type);
    declarations.push_back(IFC4_IfcDayInWeekNumber_type);
    declarations.push_back(IFC4_IfcDescriptiveMeasure_type);
    declarations.push_back(IFC4_IfcDimensionCount_type);
    declarations.push_back(IFC4_IfcDoseEquivalentMeasure_type);
    declarations.push_back(IFC4_IfcDuration_type);
    declarations.push_back(IFC4_IfcDynamicViscosityMeasure_type);
    declarations.push_back(IFC4_IfcElectricCapacitanceMeasure_type);
    declarations.push_back(IFC4_IfcElectricChargeMeasure_type);
    declarations.push_back(IFC4_IfcElectricConductanceMeasure_type);
    declarations.push_back(IFC4_IfcElectricCurrentMeasure_type);
    declarations.push_back(IFC4_IfcElectricResistanceMeasure_type);
    declarations.push_back(IFC4_IfcElectricVoltageMeasure_type);
    declarations.push_back(IFC4_IfcEnergyMeasure_type);
    declarations.push_back(IFC4_IfcFontStyle_type);
    declarations.push_back(IFC4_IfcFontVariant_type);
    declarations.push_back(IFC4_IfcFontWeight_type);
    declarations.push_back(IFC4_IfcForceMeasure_type);
    declarations.push_back(IFC4_IfcFrequencyMeasure_type);
    declarations.push_back(IFC4_IfcGloballyUniqueId_type);
    declarations.push_back(IFC4_IfcHeatFluxDensityMeasure_type);
    declarations.push_back(IFC4_IfcHeatingValueMeasure_type);
    declarations.push_back(IFC4_IfcIdentifier_type);
    declarations.push_back(IFC4_IfcIlluminanceMeasure_type);
    declarations.push_back(IFC4_IfcInductanceMeasure_type);
    declarations.push_back(IFC4_IfcInteger_type);
    declarations.push_back(IFC4_IfcIntegerCountRateMeasure_type);
    declarations.push_back(IFC4_IfcIonConcentrationMeasure_type);
    declarations.push_back(IFC4_IfcIsothermalMoistureCapacityMeasure_type);
    declarations.push_back(IFC4_IfcKinematicViscosityMeasure_type);
    declarations.push_back(IFC4_IfcLabel_type);
    declarations.push_back(IFC4_IfcLanguageId_type);
    declarations.push_back(IFC4_IfcLengthMeasure_type);
    declarations.push_back(IFC4_IfcLineIndex_type);
    declarations.push_back(IFC4_IfcLinearForceMeasure_type);
    declarations.push_back(IFC4_IfcLinearMomentMeasure_type);
    declarations.push_back(IFC4_IfcLinearStiffnessMeasure_type);
    declarations.push_back(IFC4_IfcLinearVelocityMeasure_type);
    declarations.push_back(IFC4_IfcLogical_type);
    declarations.push_back(IFC4_IfcLuminousFluxMeasure_type);
    declarations.push_back(IFC4_IfcLuminousIntensityDistributionMeasure_type);
    declarations.push_back(IFC4_IfcLuminousIntensityMeasure_type);
    declarations.push_back(IFC4_IfcMagneticFluxDensityMeasure_type);
    declarations.push_back(IFC4_IfcMagneticFluxMeasure_type);
    declarations.push_back(IFC4_IfcMassDensityMeasure_type);
    declarations.push_back(IFC4_IfcMassFlowRateMeasure_type);
    declarations.push_back(IFC4_IfcMassMeasure_type);
    declarations.push_back(IFC4_IfcMassPerLengthMeasure_type);
    declarations.push_back(IFC4_IfcModulusOfElasticityMeasure_type);
    declarations.push_back(IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type);
    declarations.push_back(IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type);
    declarations.push_back(IFC4_IfcModulusOfSubgradeReactionMeasure_type);
    declarations.push_back(IFC4_IfcMoistureDiffusivityMeasure_type);
    declarations.push_back(IFC4_IfcMolecularWeightMeasure_type);
    declarations.push_back(IFC4_IfcMomentOfInertiaMeasure_type);
    declarations.push_back(IFC4_IfcMonetaryMeasure_type);
    declarations.push_back(IFC4_IfcMonthInYearNumber_type);
    declarations.push_back(IFC4_IfcNonNegativeLengthMeasure_type);
    declarations.push_back(IFC4_IfcNumericMeasure_type);
    declarations.push_back(IFC4_IfcPHMeasure_type);
    declarations.push_back(IFC4_IfcParameterValue_type);
    declarations.push_back(IFC4_IfcPlanarForceMeasure_type);
    declarations.push_back(IFC4_IfcPlaneAngleMeasure_type);
    declarations.push_back(IFC4_IfcPositiveInteger_type);
    declarations.push_back(IFC4_IfcPositiveLengthMeasure_type);
    declarations.push_back(IFC4_IfcPositivePlaneAngleMeasure_type);
    declarations.push_back(IFC4_IfcPowerMeasure_type);
    declarations.push_back(IFC4_IfcPresentableText_type);
    declarations.push_back(IFC4_IfcPressureMeasure_type);
    declarations.push_back(IFC4_IfcPropertySetDefinitionSet_type);
    declarations.push_back(IFC4_IfcRadioActivityMeasure_type);
    declarations.push_back(IFC4_IfcRatioMeasure_type);
    declarations.push_back(IFC4_IfcReal_type);
    declarations.push_back(IFC4_IfcRotationalFrequencyMeasure_type);
    declarations.push_back(IFC4_IfcRotationalMassMeasure_type);
    declarations.push_back(IFC4_IfcRotationalStiffnessMeasure_type);
    declarations.push_back(IFC4_IfcSectionModulusMeasure_type);
    declarations.push_back(IFC4_IfcSectionalAreaIntegralMeasure_type);
    declarations.push_back(IFC4_IfcShearModulusMeasure_type);
    declarations.push_back(IFC4_IfcSolidAngleMeasure_type);
    declarations.push_back(IFC4_IfcSoundPowerLevelMeasure_type);
    declarations.push_back(IFC4_IfcSoundPowerMeasure_type);
    declarations.push_back(IFC4_IfcSoundPressureLevelMeasure_type);
    declarations.push_back(IFC4_IfcSoundPressureMeasure_type);
    declarations.push_back(IFC4_IfcSpecificHeatCapacityMeasure_type);
    declarations.push_back(IFC4_IfcSpecularExponent_type);
    declarations.push_back(IFC4_IfcSpecularRoughness_type);
    declarations.push_back(IFC4_IfcStrippedOptional_type);
    declarations.push_back(IFC4_IfcTemperatureGradientMeasure_type);
    declarations.push_back(IFC4_IfcTemperatureRateOfChangeMeasure_type);
    declarations.push_back(IFC4_IfcText_type);
    declarations.push_back(IFC4_IfcTextAlignment_type);
    declarations.push_back(IFC4_IfcTextDecoration_type);
    declarations.push_back(IFC4_IfcTextFontName_type);
    declarations.push_back(IFC4_IfcTextTransformation_type);
    declarations.push_back(IFC4_IfcThermalAdmittanceMeasure_type);
    declarations.push_back(IFC4_IfcThermalConductivityMeasure_type);
    declarations.push_back(IFC4_IfcThermalExpansionCoefficientMeasure_type);
    declarations.push_back(IFC4_IfcThermalResistanceMeasure_type);
    declarations.push_back(IFC4_IfcThermalTransmittanceMeasure_type);
    declarations.push_back(IFC4_IfcThermodynamicTemperatureMeasure_type);
    declarations.push_back(IFC4_IfcTime_type);
    declarations.push_back(IFC4_IfcTimeMeasure_type);
    declarations.push_back(IFC4_IfcTimeStamp_type);
    declarations.push_back(IFC4_IfcTorqueMeasure_type);
    declarations.push_back(IFC4_IfcURIReference_type);
    declarations.push_back(IFC4_IfcVaporPermeabilityMeasure_type);
    declarations.push_back(IFC4_IfcVolumeMeasure_type);
    declarations.push_back(IFC4_IfcVolumetricFlowRateMeasure_type);
    declarations.push_back(IFC4_IfcWarpingConstantMeasure_type);
    declarations.push_back(IFC4_IfcWarpingMomentMeasure_type);
    declarations.push_back(IFC4_IfcBoxAlignment_type);
    declarations.push_back(IFC4_IfcNormalisedRatioMeasure_type);
    declarations.push_back(IFC4_IfcPositiveRatioMeasure_type);
    declarations.push_back(IFC4_IfcActionRequestTypeEnum_type);
    declarations.push_back(IFC4_IfcActionSourceTypeEnum_type);
    declarations.push_back(IFC4_IfcActionTypeEnum_type);
    declarations.push_back(IFC4_IfcActuatorTypeEnum_type);
    declarations.push_back(IFC4_IfcAddressTypeEnum_type);
    declarations.push_back(IFC4_IfcAirTerminalBoxTypeEnum_type);
    declarations.push_back(IFC4_IfcAirTerminalTypeEnum_type);
    declarations.push_back(IFC4_IfcAirToAirHeatRecoveryTypeEnum_type);
    declarations.push_back(IFC4_IfcAlarmTypeEnum_type);
    declarations.push_back(IFC4_IfcAnalysisModelTypeEnum_type);
    declarations.push_back(IFC4_IfcAnalysisTheoryTypeEnum_type);
    declarations.push_back(IFC4_IfcArithmeticOperatorEnum_type);
    declarations.push_back(IFC4_IfcAssemblyPlaceEnum_type);
    declarations.push_back(IFC4_IfcAudioVisualApplianceTypeEnum_type);
    declarations.push_back(IFC4_IfcBSplineCurveForm_type);
    declarations.push_back(IFC4_IfcBSplineSurfaceForm_type);
    declarations.push_back(IFC4_IfcBeamTypeEnum_type);
    declarations.push_back(IFC4_IfcBenchmarkEnum_type);
    declarations.push_back(IFC4_IfcBoilerTypeEnum_type);
    declarations.push_back(IFC4_IfcBooleanOperator_type);
    declarations.push_back(IFC4_IfcBuildingElementPartTypeEnum_type);
    declarations.push_back(IFC4_IfcBuildingElementProxyTypeEnum_type);
    declarations.push_back(IFC4_IfcBuildingSystemTypeEnum_type);
    declarations.push_back(IFC4_IfcBurnerTypeEnum_type);
    declarations.push_back(IFC4_IfcCableCarrierFittingTypeEnum_type);
    declarations.push_back(IFC4_IfcCableCarrierSegmentTypeEnum_type);
    declarations.push_back(IFC4_IfcCableFittingTypeEnum_type);
    declarations.push_back(IFC4_IfcCableSegmentTypeEnum_type);
    declarations.push_back(IFC4_IfcChangeActionEnum_type);
    declarations.push_back(IFC4_IfcChillerTypeEnum_type);
    declarations.push_back(IFC4_IfcChimneyTypeEnum_type);
    declarations.push_back(IFC4_IfcCoilTypeEnum_type);
    declarations.push_back(IFC4_IfcColumnTypeEnum_type);
    declarations.push_back(IFC4_IfcCommunicationsApplianceTypeEnum_type);
    declarations.push_back(IFC4_IfcComplexPropertyTemplateTypeEnum_type);
    declarations.push_back(IFC4_IfcCompressorTypeEnum_type);
    declarations.push_back(IFC4_IfcCondenserTypeEnum_type);
    declarations.push_back(IFC4_IfcConnectionTypeEnum_type);
    declarations.push_back(IFC4_IfcConstraintEnum_type);
    declarations.push_back(IFC4_IfcConstructionEquipmentResourceTypeEnum_type);
    declarations.push_back(IFC4_IfcConstructionMaterialResourceTypeEnum_type);
    declarations.push_back(IFC4_IfcConstructionProductResourceTypeEnum_type);
    declarations.push_back(IFC4_IfcControllerTypeEnum_type);
    declarations.push_back(IFC4_IfcCooledBeamTypeEnum_type);
    declarations.push_back(IFC4_IfcCoolingTowerTypeEnum_type);
    declarations.push_back(IFC4_IfcCostItemTypeEnum_type);
    declarations.push_back(IFC4_IfcCostScheduleTypeEnum_type);
    declarations.push_back(IFC4_IfcCoveringTypeEnum_type);
    declarations.push_back(IFC4_IfcCrewResourceTypeEnum_type);
    declarations.push_back(IFC4_IfcCurtainWallTypeEnum_type);
    declarations.push_back(IFC4_IfcCurveInterpolationEnum_type);
    declarations.push_back(IFC4_IfcDamperTypeEnum_type);
    declarations.push_back(IFC4_IfcDataOriginEnum_type);
    declarations.push_back(IFC4_IfcDerivedUnitEnum_type);
    declarations.push_back(IFC4_IfcDirectionSenseEnum_type);
    declarations.push_back(IFC4_IfcDiscreteAccessoryTypeEnum_type);
    declarations.push_back(IFC4_IfcDistributionChamberElementTypeEnum_type);
    declarations.push_back(IFC4_IfcDistributionPortTypeEnum_type);
    declarations.push_back(IFC4_IfcDistributionSystemEnum_type);
    declarations.push_back(IFC4_IfcDocumentConfidentialityEnum_type);
    declarations.push_back(IFC4_IfcDocumentStatusEnum_type);
    declarations.push_back(IFC4_IfcDoorPanelOperationEnum_type);
    declarations.push_back(IFC4_IfcDoorPanelPositionEnum_type);
    declarations.push_back(IFC4_IfcDoorStyleConstructionEnum_type);
    declarations.push_back(IFC4_IfcDoorStyleOperationEnum_type);
    declarations.push_back(IFC4_IfcDoorTypeEnum_type);
    declarations.push_back(IFC4_IfcDoorTypeOperationEnum_type);
    declarations.push_back(IFC4_IfcDuctFittingTypeEnum_type);
    declarations.push_back(IFC4_IfcDuctSegmentTypeEnum_type);
    declarations.push_back(IFC4_IfcDuctSilencerTypeEnum_type);
    declarations.push_back(IFC4_IfcElectricApplianceTypeEnum_type);
    declarations.push_back(IFC4_IfcElectricDistributionBoardTypeEnum_type);
    declarations.push_back(IFC4_IfcElectricFlowStorageDeviceTypeEnum_type);
    declarations.push_back(IFC4_IfcElectricGeneratorTypeEnum_type);
    declarations.push_back(IFC4_IfcElectricMotorTypeEnum_type);
    declarations.push_back(IFC4_IfcElectricTimeControlTypeEnum_type);
    declarations.push_back(IFC4_IfcElementAssemblyTypeEnum_type);
    declarations.push_back(IFC4_IfcElementCompositionEnum_type);
    declarations.push_back(IFC4_IfcEngineTypeEnum_type);
    declarations.push_back(IFC4_IfcEvaporativeCoolerTypeEnum_type);
    declarations.push_back(IFC4_IfcEvaporatorTypeEnum_type);
    declarations.push_back(IFC4_IfcEventTriggerTypeEnum_type);
    declarations.push_back(IFC4_IfcEventTypeEnum_type);
    declarations.push_back(IFC4_IfcExternalSpatialElementTypeEnum_type);
    declarations.push_back(IFC4_IfcFanTypeEnum_type);
    declarations.push_back(IFC4_IfcFastenerTypeEnum_type);
    declarations.push_back(IFC4_IfcFilterTypeEnum_type);
    declarations.push_back(IFC4_IfcFireSuppressionTerminalTypeEnum_type);
    declarations.push_back(IFC4_IfcFlowDirectionEnum_type);
    declarations.push_back(IFC4_IfcFlowInstrumentTypeEnum_type);
    declarations.push_back(IFC4_IfcFlowMeterTypeEnum_type);
    declarations.push_back(IFC4_IfcFootingTypeEnum_type);
    declarations.push_back(IFC4_IfcFurnitureTypeEnum_type);
    declarations.push_back(IFC4_IfcGeographicElementTypeEnum_type);
    declarations.push_back(IFC4_IfcGeometricProjectionEnum_type);
    declarations.push_back(IFC4_IfcGlobalOrLocalEnum_type);
    declarations.push_back(IFC4_IfcGridTypeEnum_type);
    declarations.push_back(IFC4_IfcHeatExchangerTypeEnum_type);
    declarations.push_back(IFC4_IfcHumidifierTypeEnum_type);
    declarations.push_back(IFC4_IfcInterceptorTypeEnum_type);
    declarations.push_back(IFC4_IfcInternalOrExternalEnum_type);
    declarations.push_back(IFC4_IfcInventoryTypeEnum_type);
    declarations.push_back(IFC4_IfcJunctionBoxTypeEnum_type);
    declarations.push_back(IFC4_IfcKnotType_type);
    declarations.push_back(IFC4_IfcLaborResourceTypeEnum_type);
    declarations.push_back(IFC4_IfcLampTypeEnum_type);
    declarations.push_back(IFC4_IfcLayerSetDirectionEnum_type);
    declarations.push_back(IFC4_IfcLightDistributionCurveEnum_type);
    declarations.push_back(IFC4_IfcLightEmissionSourceEnum_type);
    declarations.push_back(IFC4_IfcLightFixtureTypeEnum_type);
    declarations.push_back(IFC4_IfcLoadGroupTypeEnum_type);
    declarations.push_back(IFC4_IfcLogicalOperatorEnum_type);
    declarations.push_back(IFC4_IfcMechanicalFastenerTypeEnum_type);
    declarations.push_back(IFC4_IfcMedicalDeviceTypeEnum_type);
    declarations.push_back(IFC4_IfcMemberTypeEnum_type);
    declarations.push_back(IFC4_IfcMotorConnectionTypeEnum_type);
    declarations.push_back(IFC4_IfcNullStyle_type);
    declarations.push_back(IFC4_IfcObjectTypeEnum_type);
    declarations.push_back(IFC4_IfcObjectiveEnum_type);
    declarations.push_back(IFC4_IfcOccupantTypeEnum_type);
    declarations.push_back(IFC4_IfcOpeningElementTypeEnum_type);
    declarations.push_back(IFC4_IfcOutletTypeEnum_type);
    declarations.push_back(IFC4_IfcPerformanceHistoryTypeEnum_type);
    declarations.push_back(IFC4_IfcPermeableCoveringOperationEnum_type);
    declarations.push_back(IFC4_IfcPermitTypeEnum_type);
    declarations.push_back(IFC4_IfcPhysicalOrVirtualEnum_type);
    declarations.push_back(IFC4_IfcPileConstructionEnum_type);
    declarations.push_back(IFC4_IfcPileTypeEnum_type);
    declarations.push_back(IFC4_IfcPipeFittingTypeEnum_type);
    declarations.push_back(IFC4_IfcPipeSegmentTypeEnum_type);
    declarations.push_back(IFC4_IfcPlateTypeEnum_type);
    declarations.push_back(IFC4_IfcProcedureTypeEnum_type);
    declarations.push_back(IFC4_IfcProfileTypeEnum_type);
    declarations.push_back(IFC4_IfcProjectOrderTypeEnum_type);
    declarations.push_back(IFC4_IfcProjectedOrTrueLengthEnum_type);
    declarations.push_back(IFC4_IfcProjectionElementTypeEnum_type);
    declarations.push_back(IFC4_IfcPropertySetTemplateTypeEnum_type);
    declarations.push_back(IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type);
    declarations.push_back(IFC4_IfcProtectiveDeviceTypeEnum_type);
    declarations.push_back(IFC4_IfcPumpTypeEnum_type);
    declarations.push_back(IFC4_IfcRailingTypeEnum_type);
    declarations.push_back(IFC4_IfcRampFlightTypeEnum_type);
    declarations.push_back(IFC4_IfcRampTypeEnum_type);
    declarations.push_back(IFC4_IfcRecurrenceTypeEnum_type);
    declarations.push_back(IFC4_IfcReflectanceMethodEnum_type);
    declarations.push_back(IFC4_IfcReinforcingBarRoleEnum_type);
    declarations.push_back(IFC4_IfcReinforcingBarSurfaceEnum_type);
    declarations.push_back(IFC4_IfcReinforcingBarTypeEnum_type);
    declarations.push_back(IFC4_IfcReinforcingMeshTypeEnum_type);
    declarations.push_back(IFC4_IfcRoleEnum_type);
    declarations.push_back(IFC4_IfcRoofTypeEnum_type);
    declarations.push_back(IFC4_IfcSIPrefix_type);
    declarations.push_back(IFC4_IfcSIUnitName_type);
    declarations.push_back(IFC4_IfcSanitaryTerminalTypeEnum_type);
    declarations.push_back(IFC4_IfcSectionTypeEnum_type);
    declarations.push_back(IFC4_IfcSensorTypeEnum_type);
    declarations.push_back(IFC4_IfcSequenceEnum_type);
    declarations.push_back(IFC4_IfcShadingDeviceTypeEnum_type);
    declarations.push_back(IFC4_IfcSimplePropertyTemplateTypeEnum_type);
    declarations.push_back(IFC4_IfcSlabTypeEnum_type);
    declarations.push_back(IFC4_IfcSolarDeviceTypeEnum_type);
    declarations.push_back(IFC4_IfcSpaceHeaterTypeEnum_type);
    declarations.push_back(IFC4_IfcSpaceTypeEnum_type);
    declarations.push_back(IFC4_IfcSpatialZoneTypeEnum_type);
    declarations.push_back(IFC4_IfcStackTerminalTypeEnum_type);
    declarations.push_back(IFC4_IfcStairFlightTypeEnum_type);
    declarations.push_back(IFC4_IfcStairTypeEnum_type);
    declarations.push_back(IFC4_IfcStateEnum_type);
    declarations.push_back(IFC4_IfcStructuralCurveActivityTypeEnum_type);
    declarations.push_back(IFC4_IfcStructuralCurveMemberTypeEnum_type);
    declarations.push_back(IFC4_IfcStructuralSurfaceActivityTypeEnum_type);
    declarations.push_back(IFC4_IfcStructuralSurfaceMemberTypeEnum_type);
    declarations.push_back(IFC4_IfcSubContractResourceTypeEnum_type);
    declarations.push_back(IFC4_IfcSurfaceFeatureTypeEnum_type);
    declarations.push_back(IFC4_IfcSurfaceSide_type);
    declarations.push_back(IFC4_IfcSwitchingDeviceTypeEnum_type);
    declarations.push_back(IFC4_IfcSystemFurnitureElementTypeEnum_type);
    declarations.push_back(IFC4_IfcTankTypeEnum_type);
    declarations.push_back(IFC4_IfcTaskDurationEnum_type);
    declarations.push_back(IFC4_IfcTaskTypeEnum_type);
    declarations.push_back(IFC4_IfcTendonAnchorTypeEnum_type);
    declarations.push_back(IFC4_IfcTendonTypeEnum_type);
    declarations.push_back(IFC4_IfcTextPath_type);
    declarations.push_back(IFC4_IfcTimeSeriesDataTypeEnum_type);
    declarations.push_back(IFC4_IfcTransformerTypeEnum_type);
    declarations.push_back(IFC4_IfcTransitionCode_type);
    declarations.push_back(IFC4_IfcTransportElementTypeEnum_type);
    declarations.push_back(IFC4_IfcTrimmingPreference_type);
    declarations.push_back(IFC4_IfcTubeBundleTypeEnum_type);
    declarations.push_back(IFC4_IfcUnitEnum_type);
    declarations.push_back(IFC4_IfcUnitaryControlElementTypeEnum_type);
    declarations.push_back(IFC4_IfcUnitaryEquipmentTypeEnum_type);
    declarations.push_back(IFC4_IfcValveTypeEnum_type);
    declarations.push_back(IFC4_IfcVibrationIsolatorTypeEnum_type);
    declarations.push_back(IFC4_IfcVoidingFeatureTypeEnum_type);
    declarations.push_back(IFC4_IfcWallTypeEnum_type);
    declarations.push_back(IFC4_IfcWasteTerminalTypeEnum_type);
    declarations.push_back(IFC4_IfcWindowPanelOperationEnum_type);
    declarations.push_back(IFC4_IfcWindowPanelPositionEnum_type);
    declarations.push_back(IFC4_IfcWindowStyleConstructionEnum_type);
    declarations.push_back(IFC4_IfcWindowStyleOperationEnum_type);
    declarations.push_back(IFC4_IfcWindowTypeEnum_type);
    declarations.push_back(IFC4_IfcWindowTypePartitioningEnum_type);
    declarations.push_back(IFC4_IfcWorkCalendarTypeEnum_type);
    declarations.push_back(IFC4_IfcWorkPlanTypeEnum_type);
    declarations.push_back(IFC4_IfcWorkScheduleTypeEnum_type);
    declarations.push_back(IFC4_IfcActorRole_type);
    declarations.push_back(IFC4_IfcAddress_type);
    declarations.push_back(IFC4_IfcApplication_type);
    declarations.push_back(IFC4_IfcAppliedValue_type);
    declarations.push_back(IFC4_IfcApproval_type);
    declarations.push_back(IFC4_IfcBoundaryCondition_type);
    declarations.push_back(IFC4_IfcBoundaryEdgeCondition_type);
    declarations.push_back(IFC4_IfcBoundaryFaceCondition_type);
    declarations.push_back(IFC4_IfcBoundaryNodeCondition_type);
    declarations.push_back(IFC4_IfcBoundaryNodeConditionWarping_type);
    declarations.push_back(IFC4_IfcConnectionGeometry_type);
    declarations.push_back(IFC4_IfcConnectionPointGeometry_type);
    declarations.push_back(IFC4_IfcConnectionSurfaceGeometry_type);
    declarations.push_back(IFC4_IfcConnectionVolumeGeometry_type);
    declarations.push_back(IFC4_IfcConstraint_type);
    declarations.push_back(IFC4_IfcCoordinateOperation_type);
    declarations.push_back(IFC4_IfcCoordinateReferenceSystem_type);
    declarations.push_back(IFC4_IfcCostValue_type);
    declarations.push_back(IFC4_IfcDerivedUnit_type);
    declarations.push_back(IFC4_IfcDerivedUnitElement_type);
    declarations.push_back(IFC4_IfcDimensionalExponents_type);
    declarations.push_back(IFC4_IfcExternalInformation_type);
    declarations.push_back(IFC4_IfcExternalReference_type);
    declarations.push_back(IFC4_IfcExternallyDefinedHatchStyle_type);
    declarations.push_back(IFC4_IfcExternallyDefinedSurfaceStyle_type);
    declarations.push_back(IFC4_IfcExternallyDefinedTextFont_type);
    declarations.push_back(IFC4_IfcGridAxis_type);
    declarations.push_back(IFC4_IfcIrregularTimeSeriesValue_type);
    declarations.push_back(IFC4_IfcLibraryInformation_type);
    declarations.push_back(IFC4_IfcLibraryReference_type);
    declarations.push_back(IFC4_IfcLightDistributionData_type);
    declarations.push_back(IFC4_IfcLightIntensityDistribution_type);
    declarations.push_back(IFC4_IfcMapConversion_type);
    declarations.push_back(IFC4_IfcMaterialClassificationRelationship_type);
    declarations.push_back(IFC4_IfcMaterialDefinition_type);
    declarations.push_back(IFC4_IfcMaterialLayer_type);
    declarations.push_back(IFC4_IfcMaterialLayerSet_type);
    declarations.push_back(IFC4_IfcMaterialLayerWithOffsets_type);
    declarations.push_back(IFC4_IfcMaterialList_type);
    declarations.push_back(IFC4_IfcMaterialProfile_type);
    declarations.push_back(IFC4_IfcMaterialProfileSet_type);
    declarations.push_back(IFC4_IfcMaterialProfileWithOffsets_type);
    declarations.push_back(IFC4_IfcMaterialUsageDefinition_type);
    declarations.push_back(IFC4_IfcMeasureWithUnit_type);
    declarations.push_back(IFC4_IfcMetric_type);
    declarations.push_back(IFC4_IfcMonetaryUnit_type);
    declarations.push_back(IFC4_IfcNamedUnit_type);
    declarations.push_back(IFC4_IfcObjectPlacement_type);
    declarations.push_back(IFC4_IfcObjective_type);
    declarations.push_back(IFC4_IfcOrganization_type);
    declarations.push_back(IFC4_IfcOwnerHistory_type);
    declarations.push_back(IFC4_IfcPerson_type);
    declarations.push_back(IFC4_IfcPersonAndOrganization_type);
    declarations.push_back(IFC4_IfcPhysicalQuantity_type);
    declarations.push_back(IFC4_IfcPhysicalSimpleQuantity_type);
    declarations.push_back(IFC4_IfcPostalAddress_type);
    declarations.push_back(IFC4_IfcPresentationItem_type);
    declarations.push_back(IFC4_IfcPresentationLayerAssignment_type);
    declarations.push_back(IFC4_IfcPresentationLayerWithStyle_type);
    declarations.push_back(IFC4_IfcPresentationStyle_type);
    declarations.push_back(IFC4_IfcPresentationStyleAssignment_type);
    declarations.push_back(IFC4_IfcProductRepresentation_type);
    declarations.push_back(IFC4_IfcProfileDef_type);
    declarations.push_back(IFC4_IfcProjectedCRS_type);
    declarations.push_back(IFC4_IfcPropertyAbstraction_type);
    declarations.push_back(IFC4_IfcPropertyEnumeration_type);
    declarations.push_back(IFC4_IfcQuantityArea_type);
    declarations.push_back(IFC4_IfcQuantityCount_type);
    declarations.push_back(IFC4_IfcQuantityLength_type);
    declarations.push_back(IFC4_IfcQuantityTime_type);
    declarations.push_back(IFC4_IfcQuantityVolume_type);
    declarations.push_back(IFC4_IfcQuantityWeight_type);
    declarations.push_back(IFC4_IfcRecurrencePattern_type);
    declarations.push_back(IFC4_IfcReference_type);
    declarations.push_back(IFC4_IfcRepresentation_type);
    declarations.push_back(IFC4_IfcRepresentationContext_type);
    declarations.push_back(IFC4_IfcRepresentationItem_type);
    declarations.push_back(IFC4_IfcRepresentationMap_type);
    declarations.push_back(IFC4_IfcResourceLevelRelationship_type);
    declarations.push_back(IFC4_IfcRoot_type);
    declarations.push_back(IFC4_IfcSIUnit_type);
    declarations.push_back(IFC4_IfcSchedulingTime_type);
    declarations.push_back(IFC4_IfcShapeAspect_type);
    declarations.push_back(IFC4_IfcShapeModel_type);
    declarations.push_back(IFC4_IfcShapeRepresentation_type);
    declarations.push_back(IFC4_IfcStructuralConnectionCondition_type);
    declarations.push_back(IFC4_IfcStructuralLoad_type);
    declarations.push_back(IFC4_IfcStructuralLoadConfiguration_type);
    declarations.push_back(IFC4_IfcStructuralLoadOrResult_type);
    declarations.push_back(IFC4_IfcStructuralLoadStatic_type);
    declarations.push_back(IFC4_IfcStructuralLoadTemperature_type);
    declarations.push_back(IFC4_IfcStyleModel_type);
    declarations.push_back(IFC4_IfcStyledItem_type);
    declarations.push_back(IFC4_IfcStyledRepresentation_type);
    declarations.push_back(IFC4_IfcSurfaceReinforcementArea_type);
    declarations.push_back(IFC4_IfcSurfaceStyle_type);
    declarations.push_back(IFC4_IfcSurfaceStyleLighting_type);
    declarations.push_back(IFC4_IfcSurfaceStyleRefraction_type);
    declarations.push_back(IFC4_IfcSurfaceStyleShading_type);
    declarations.push_back(IFC4_IfcSurfaceStyleWithTextures_type);
    declarations.push_back(IFC4_IfcSurfaceTexture_type);
    declarations.push_back(IFC4_IfcTable_type);
    declarations.push_back(IFC4_IfcTableColumn_type);
    declarations.push_back(IFC4_IfcTableRow_type);
    declarations.push_back(IFC4_IfcTaskTime_type);
    declarations.push_back(IFC4_IfcTaskTimeRecurring_type);
    declarations.push_back(IFC4_IfcTelecomAddress_type);
    declarations.push_back(IFC4_IfcTextStyle_type);
    declarations.push_back(IFC4_IfcTextStyleForDefinedFont_type);
    declarations.push_back(IFC4_IfcTextStyleTextModel_type);
    declarations.push_back(IFC4_IfcTextureCoordinate_type);
    declarations.push_back(IFC4_IfcTextureCoordinateGenerator_type);
    declarations.push_back(IFC4_IfcTextureMap_type);
    declarations.push_back(IFC4_IfcTextureVertex_type);
    declarations.push_back(IFC4_IfcTextureVertexList_type);
    declarations.push_back(IFC4_IfcTimePeriod_type);
    declarations.push_back(IFC4_IfcTimeSeries_type);
    declarations.push_back(IFC4_IfcTimeSeriesValue_type);
    declarations.push_back(IFC4_IfcTopologicalRepresentationItem_type);
    declarations.push_back(IFC4_IfcTopologyRepresentation_type);
    declarations.push_back(IFC4_IfcUnitAssignment_type);
    declarations.push_back(IFC4_IfcVertex_type);
    declarations.push_back(IFC4_IfcVertexPoint_type);
    declarations.push_back(IFC4_IfcVirtualGridIntersection_type);
    declarations.push_back(IFC4_IfcWorkTime_type);
    declarations.push_back(IFC4_IfcApprovalRelationship_type);
    declarations.push_back(IFC4_IfcArbitraryClosedProfileDef_type);
    declarations.push_back(IFC4_IfcArbitraryOpenProfileDef_type);
    declarations.push_back(IFC4_IfcArbitraryProfileDefWithVoids_type);
    declarations.push_back(IFC4_IfcBlobTexture_type);
    declarations.push_back(IFC4_IfcCenterLineProfileDef_type);
    declarations.push_back(IFC4_IfcClassification_type);
    declarations.push_back(IFC4_IfcClassificationReference_type);
    declarations.push_back(IFC4_IfcColourRgbList_type);
    declarations.push_back(IFC4_IfcColourSpecification_type);
    declarations.push_back(IFC4_IfcCompositeProfileDef_type);
    declarations.push_back(IFC4_IfcConnectedFaceSet_type);
    declarations.push_back(IFC4_IfcConnectionCurveGeometry_type);
    declarations.push_back(IFC4_IfcConnectionPointEccentricity_type);
    declarations.push_back(IFC4_IfcContextDependentUnit_type);
    declarations.push_back(IFC4_IfcConversionBasedUnit_type);
    declarations.push_back(IFC4_IfcConversionBasedUnitWithOffset_type);
    declarations.push_back(IFC4_IfcCurrencyRelationship_type);
    declarations.push_back(IFC4_IfcCurveStyle_type);
    declarations.push_back(IFC4_IfcCurveStyleFont_type);
    declarations.push_back(IFC4_IfcCurveStyleFontAndScaling_type);
    declarations.push_back(IFC4_IfcCurveStyleFontPattern_type);
    declarations.push_back(IFC4_IfcDerivedProfileDef_type);
    declarations.push_back(IFC4_IfcDocumentInformation_type);
    declarations.push_back(IFC4_IfcDocumentInformationRelationship_type);
    declarations.push_back(IFC4_IfcDocumentReference_type);
    declarations.push_back(IFC4_IfcEdge_type);
    declarations.push_back(IFC4_IfcEdgeCurve_type);
    declarations.push_back(IFC4_IfcEventTime_type);
    declarations.push_back(IFC4_IfcExtendedProperties_type);
    declarations.push_back(IFC4_IfcExternalReferenceRelationship_type);
    declarations.push_back(IFC4_IfcFace_type);
    declarations.push_back(IFC4_IfcFaceBound_type);
    declarations.push_back(IFC4_IfcFaceOuterBound_type);
    declarations.push_back(IFC4_IfcFaceSurface_type);
    declarations.push_back(IFC4_IfcFailureConnectionCondition_type);
    declarations.push_back(IFC4_IfcFillAreaStyle_type);
    declarations.push_back(IFC4_IfcGeometricRepresentationContext_type);
    declarations.push_back(IFC4_IfcGeometricRepresentationItem_type);
    declarations.push_back(IFC4_IfcGeometricRepresentationSubContext_type);
    declarations.push_back(IFC4_IfcGeometricSet_type);
    declarations.push_back(IFC4_IfcGridPlacement_type);
    declarations.push_back(IFC4_IfcHalfSpaceSolid_type);
    declarations.push_back(IFC4_IfcImageTexture_type);
    declarations.push_back(IFC4_IfcIndexedColourMap_type);
    declarations.push_back(IFC4_IfcIndexedTextureMap_type);
    declarations.push_back(IFC4_IfcIndexedTriangleTextureMap_type);
    declarations.push_back(IFC4_IfcIrregularTimeSeries_type);
    declarations.push_back(IFC4_IfcLagTime_type);
    declarations.push_back(IFC4_IfcLightSource_type);
    declarations.push_back(IFC4_IfcLightSourceAmbient_type);
    declarations.push_back(IFC4_IfcLightSourceDirectional_type);
    declarations.push_back(IFC4_IfcLightSourceGoniometric_type);
    declarations.push_back(IFC4_IfcLightSourcePositional_type);
    declarations.push_back(IFC4_IfcLightSourceSpot_type);
    declarations.push_back(IFC4_IfcLocalPlacement_type);
    declarations.push_back(IFC4_IfcLoop_type);
    declarations.push_back(IFC4_IfcMappedItem_type);
    declarations.push_back(IFC4_IfcMaterial_type);
    declarations.push_back(IFC4_IfcMaterialConstituent_type);
    declarations.push_back(IFC4_IfcMaterialConstituentSet_type);
    declarations.push_back(IFC4_IfcMaterialDefinitionRepresentation_type);
    declarations.push_back(IFC4_IfcMaterialLayerSetUsage_type);
    declarations.push_back(IFC4_IfcMaterialProfileSetUsage_type);
    declarations.push_back(IFC4_IfcMaterialProfileSetUsageTapering_type);
    declarations.push_back(IFC4_IfcMaterialProperties_type);
    declarations.push_back(IFC4_IfcMaterialRelationship_type);
    declarations.push_back(IFC4_IfcMirroredProfileDef_type);
    declarations.push_back(IFC4_IfcObjectDefinition_type);
    declarations.push_back(IFC4_IfcOpenShell_type);
    declarations.push_back(IFC4_IfcOrganizationRelationship_type);
    declarations.push_back(IFC4_IfcOrientedEdge_type);
    declarations.push_back(IFC4_IfcParameterizedProfileDef_type);
    declarations.push_back(IFC4_IfcPath_type);
    declarations.push_back(IFC4_IfcPhysicalComplexQuantity_type);
    declarations.push_back(IFC4_IfcPixelTexture_type);
    declarations.push_back(IFC4_IfcPlacement_type);
    declarations.push_back(IFC4_IfcPlanarExtent_type);
    declarations.push_back(IFC4_IfcPoint_type);
    declarations.push_back(IFC4_IfcPointOnCurve_type);
    declarations.push_back(IFC4_IfcPointOnSurface_type);
    declarations.push_back(IFC4_IfcPolyLoop_type);
    declarations.push_back(IFC4_IfcPolygonalBoundedHalfSpace_type);
    declarations.push_back(IFC4_IfcPreDefinedItem_type);
    declarations.push_back(IFC4_IfcPreDefinedProperties_type);
    declarations.push_back(IFC4_IfcPreDefinedTextFont_type);
    declarations.push_back(IFC4_IfcProductDefinitionShape_type);
    declarations.push_back(IFC4_IfcProfileProperties_type);
    declarations.push_back(IFC4_IfcProperty_type);
    declarations.push_back(IFC4_IfcPropertyDefinition_type);
    declarations.push_back(IFC4_IfcPropertyDependencyRelationship_type);
    declarations.push_back(IFC4_IfcPropertySetDefinition_type);
    declarations.push_back(IFC4_IfcPropertyTemplateDefinition_type);
    declarations.push_back(IFC4_IfcQuantitySet_type);
    declarations.push_back(IFC4_IfcRectangleProfileDef_type);
    declarations.push_back(IFC4_IfcRegularTimeSeries_type);
    declarations.push_back(IFC4_IfcReinforcementBarProperties_type);
    declarations.push_back(IFC4_IfcRelationship_type);
    declarations.push_back(IFC4_IfcResourceApprovalRelationship_type);
    declarations.push_back(IFC4_IfcResourceConstraintRelationship_type);
    declarations.push_back(IFC4_IfcResourceTime_type);
    declarations.push_back(IFC4_IfcRoundedRectangleProfileDef_type);
    declarations.push_back(IFC4_IfcSectionProperties_type);
    declarations.push_back(IFC4_IfcSectionReinforcementProperties_type);
    declarations.push_back(IFC4_IfcSectionedSpine_type);
    declarations.push_back(IFC4_IfcShellBasedSurfaceModel_type);
    declarations.push_back(IFC4_IfcSimpleProperty_type);
    declarations.push_back(IFC4_IfcSlippageConnectionCondition_type);
    declarations.push_back(IFC4_IfcSolidModel_type);
    declarations.push_back(IFC4_IfcStructuralLoadLinearForce_type);
    declarations.push_back(IFC4_IfcStructuralLoadPlanarForce_type);
    declarations.push_back(IFC4_IfcStructuralLoadSingleDisplacement_type);
    declarations.push_back(IFC4_IfcStructuralLoadSingleDisplacementDistortion_type);
    declarations.push_back(IFC4_IfcStructuralLoadSingleForce_type);
    declarations.push_back(IFC4_IfcStructuralLoadSingleForceWarping_type);
    declarations.push_back(IFC4_IfcSubedge_type);
    declarations.push_back(IFC4_IfcSurface_type);
    declarations.push_back(IFC4_IfcSurfaceStyleRendering_type);
    declarations.push_back(IFC4_IfcSweptAreaSolid_type);
    declarations.push_back(IFC4_IfcSweptDiskSolid_type);
    declarations.push_back(IFC4_IfcSweptDiskSolidPolygonal_type);
    declarations.push_back(IFC4_IfcSweptSurface_type);
    declarations.push_back(IFC4_IfcTShapeProfileDef_type);
    declarations.push_back(IFC4_IfcTessellatedItem_type);
    declarations.push_back(IFC4_IfcTextLiteral_type);
    declarations.push_back(IFC4_IfcTextLiteralWithExtent_type);
    declarations.push_back(IFC4_IfcTextStyleFontModel_type);
    declarations.push_back(IFC4_IfcTrapeziumProfileDef_type);
    declarations.push_back(IFC4_IfcTypeObject_type);
    declarations.push_back(IFC4_IfcTypeProcess_type);
    declarations.push_back(IFC4_IfcTypeProduct_type);
    declarations.push_back(IFC4_IfcTypeResource_type);
    declarations.push_back(IFC4_IfcUShapeProfileDef_type);
    declarations.push_back(IFC4_IfcVector_type);
    declarations.push_back(IFC4_IfcVertexLoop_type);
    declarations.push_back(IFC4_IfcWindowStyle_type);
    declarations.push_back(IFC4_IfcZShapeProfileDef_type);
    declarations.push_back(IFC4_IfcAdvancedFace_type);
    declarations.push_back(IFC4_IfcAnnotationFillArea_type);
    declarations.push_back(IFC4_IfcAsymmetricIShapeProfileDef_type);
    declarations.push_back(IFC4_IfcAxis1Placement_type);
    declarations.push_back(IFC4_IfcAxis2Placement2D_type);
    declarations.push_back(IFC4_IfcAxis2Placement3D_type);
    declarations.push_back(IFC4_IfcBooleanResult_type);
    declarations.push_back(IFC4_IfcBoundedSurface_type);
    declarations.push_back(IFC4_IfcBoundingBox_type);
    declarations.push_back(IFC4_IfcBoxedHalfSpace_type);
    declarations.push_back(IFC4_IfcCShapeProfileDef_type);
    declarations.push_back(IFC4_IfcCartesianPoint_type);
    declarations.push_back(IFC4_IfcCartesianPointList_type);
    declarations.push_back(IFC4_IfcCartesianPointList2D_type);
    declarations.push_back(IFC4_IfcCartesianPointList3D_type);
    declarations.push_back(IFC4_IfcCartesianTransformationOperator_type);
    declarations.push_back(IFC4_IfcCartesianTransformationOperator2D_type);
    declarations.push_back(IFC4_IfcCartesianTransformationOperator2DnonUniform_type);
    declarations.push_back(IFC4_IfcCartesianTransformationOperator3D_type);
    declarations.push_back(IFC4_IfcCartesianTransformationOperator3DnonUniform_type);
    declarations.push_back(IFC4_IfcCircleProfileDef_type);
    declarations.push_back(IFC4_IfcClosedShell_type);
    declarations.push_back(IFC4_IfcColourRgb_type);
    declarations.push_back(IFC4_IfcComplexProperty_type);
    declarations.push_back(IFC4_IfcCompositeCurveSegment_type);
    declarations.push_back(IFC4_IfcConstructionResourceType_type);
    declarations.push_back(IFC4_IfcContext_type);
    declarations.push_back(IFC4_IfcCrewResourceType_type);
    declarations.push_back(IFC4_IfcCsgPrimitive3D_type);
    declarations.push_back(IFC4_IfcCsgSolid_type);
    declarations.push_back(IFC4_IfcCurve_type);
    declarations.push_back(IFC4_IfcCurveBoundedPlane_type);
    declarations.push_back(IFC4_IfcCurveBoundedSurface_type);
    declarations.push_back(IFC4_IfcDirection_type);
    declarations.push_back(IFC4_IfcDoorStyle_type);
    declarations.push_back(IFC4_IfcEdgeLoop_type);
    declarations.push_back(IFC4_IfcElementQuantity_type);
    declarations.push_back(IFC4_IfcElementType_type);
    declarations.push_back(IFC4_IfcElementarySurface_type);
    declarations.push_back(IFC4_IfcEllipseProfileDef_type);
    declarations.push_back(IFC4_IfcEventType_type);
    declarations.push_back(IFC4_IfcExtrudedAreaSolid_type);
    declarations.push_back(IFC4_IfcExtrudedAreaSolidTapered_type);
    declarations.push_back(IFC4_IfcFaceBasedSurfaceModel_type);
    declarations.push_back(IFC4_IfcFillAreaStyleHatching_type);
    declarations.push_back(IFC4_IfcFillAreaStyleTiles_type);
    declarations.push_back(IFC4_IfcFixedReferenceSweptAreaSolid_type);
    declarations.push_back(IFC4_IfcFurnishingElementType_type);
    declarations.push_back(IFC4_IfcFurnitureType_type);
    declarations.push_back(IFC4_IfcGeographicElementType_type);
    declarations.push_back(IFC4_IfcGeometricCurveSet_type);
    declarations.push_back(IFC4_IfcIShapeProfileDef_type);
    declarations.push_back(IFC4_IfcLShapeProfileDef_type);
    declarations.push_back(IFC4_IfcLaborResourceType_type);
    declarations.push_back(IFC4_IfcLine_type);
    declarations.push_back(IFC4_IfcManifoldSolidBrep_type);
    declarations.push_back(IFC4_IfcObject_type);
    declarations.push_back(IFC4_IfcOffsetCurve2D_type);
    declarations.push_back(IFC4_IfcOffsetCurve3D_type);
    declarations.push_back(IFC4_IfcPcurve_type);
    declarations.push_back(IFC4_IfcPlanarBox_type);
    declarations.push_back(IFC4_IfcPlane_type);
    declarations.push_back(IFC4_IfcPreDefinedColour_type);
    declarations.push_back(IFC4_IfcPreDefinedCurveFont_type);
    declarations.push_back(IFC4_IfcPreDefinedPropertySet_type);
    declarations.push_back(IFC4_IfcProcedureType_type);
    declarations.push_back(IFC4_IfcProcess_type);
    declarations.push_back(IFC4_IfcProduct_type);
    declarations.push_back(IFC4_IfcProject_type);
    declarations.push_back(IFC4_IfcProjectLibrary_type);
    declarations.push_back(IFC4_IfcPropertyBoundedValue_type);
    declarations.push_back(IFC4_IfcPropertyEnumeratedValue_type);
    declarations.push_back(IFC4_IfcPropertyListValue_type);
    declarations.push_back(IFC4_IfcPropertyReferenceValue_type);
    declarations.push_back(IFC4_IfcPropertySet_type);
    declarations.push_back(IFC4_IfcPropertySetTemplate_type);
    declarations.push_back(IFC4_IfcPropertySingleValue_type);
    declarations.push_back(IFC4_IfcPropertyTableValue_type);
    declarations.push_back(IFC4_IfcPropertyTemplate_type);
    declarations.push_back(IFC4_IfcProxy_type);
    declarations.push_back(IFC4_IfcRectangleHollowProfileDef_type);
    declarations.push_back(IFC4_IfcRectangularPyramid_type);
    declarations.push_back(IFC4_IfcRectangularTrimmedSurface_type);
    declarations.push_back(IFC4_IfcReinforcementDefinitionProperties_type);
    declarations.push_back(IFC4_IfcRelAssigns_type);
    declarations.push_back(IFC4_IfcRelAssignsToActor_type);
    declarations.push_back(IFC4_IfcRelAssignsToControl_type);
    declarations.push_back(IFC4_IfcRelAssignsToGroup_type);
    declarations.push_back(IFC4_IfcRelAssignsToGroupByFactor_type);
    declarations.push_back(IFC4_IfcRelAssignsToProcess_type);
    declarations.push_back(IFC4_IfcRelAssignsToProduct_type);
    declarations.push_back(IFC4_IfcRelAssignsToResource_type);
    declarations.push_back(IFC4_IfcRelAssociates_type);
    declarations.push_back(IFC4_IfcRelAssociatesApproval_type);
    declarations.push_back(IFC4_IfcRelAssociatesClassification_type);
    declarations.push_back(IFC4_IfcRelAssociatesConstraint_type);
    declarations.push_back(IFC4_IfcRelAssociatesDocument_type);
    declarations.push_back(IFC4_IfcRelAssociatesLibrary_type);
    declarations.push_back(IFC4_IfcRelAssociatesMaterial_type);
    declarations.push_back(IFC4_IfcRelConnects_type);
    declarations.push_back(IFC4_IfcRelConnectsElements_type);
    declarations.push_back(IFC4_IfcRelConnectsPathElements_type);
    declarations.push_back(IFC4_IfcRelConnectsPortToElement_type);
    declarations.push_back(IFC4_IfcRelConnectsPorts_type);
    declarations.push_back(IFC4_IfcRelConnectsStructuralActivity_type);
    declarations.push_back(IFC4_IfcRelConnectsStructuralMember_type);
    declarations.push_back(IFC4_IfcRelConnectsWithEccentricity_type);
    declarations.push_back(IFC4_IfcRelConnectsWithRealizingElements_type);
    declarations.push_back(IFC4_IfcRelContainedInSpatialStructure_type);
    declarations.push_back(IFC4_IfcRelCoversBldgElements_type);
    declarations.push_back(IFC4_IfcRelCoversSpaces_type);
    declarations.push_back(IFC4_IfcRelDeclares_type);
    declarations.push_back(IFC4_IfcRelDecomposes_type);
    declarations.push_back(IFC4_IfcRelDefines_type);
    declarations.push_back(IFC4_IfcRelDefinesByObject_type);
    declarations.push_back(IFC4_IfcRelDefinesByProperties_type);
    declarations.push_back(IFC4_IfcRelDefinesByTemplate_type);
    declarations.push_back(IFC4_IfcRelDefinesByType_type);
    declarations.push_back(IFC4_IfcRelFillsElement_type);
    declarations.push_back(IFC4_IfcRelFlowControlElements_type);
    declarations.push_back(IFC4_IfcRelInterferesElements_type);
    declarations.push_back(IFC4_IfcRelNests_type);
    declarations.push_back(IFC4_IfcRelProjectsElement_type);
    declarations.push_back(IFC4_IfcRelReferencedInSpatialStructure_type);
    declarations.push_back(IFC4_IfcRelSequence_type);
    declarations.push_back(IFC4_IfcRelServicesBuildings_type);
    declarations.push_back(IFC4_IfcRelSpaceBoundary_type);
    declarations.push_back(IFC4_IfcRelSpaceBoundary1stLevel_type);
    declarations.push_back(IFC4_IfcRelSpaceBoundary2ndLevel_type);
    declarations.push_back(IFC4_IfcRelVoidsElement_type);
    declarations.push_back(IFC4_IfcReparametrisedCompositeCurveSegment_type);
    declarations.push_back(IFC4_IfcResource_type);
    declarations.push_back(IFC4_IfcRevolvedAreaSolid_type);
    declarations.push_back(IFC4_IfcRevolvedAreaSolidTapered_type);
    declarations.push_back(IFC4_IfcRightCircularCone_type);
    declarations.push_back(IFC4_IfcRightCircularCylinder_type);
    declarations.push_back(IFC4_IfcSimplePropertyTemplate_type);
    declarations.push_back(IFC4_IfcSpatialElement_type);
    declarations.push_back(IFC4_IfcSpatialElementType_type);
    declarations.push_back(IFC4_IfcSpatialStructureElement_type);
    declarations.push_back(IFC4_IfcSpatialStructureElementType_type);
    declarations.push_back(IFC4_IfcSpatialZone_type);
    declarations.push_back(IFC4_IfcSpatialZoneType_type);
    declarations.push_back(IFC4_IfcSphere_type);
    declarations.push_back(IFC4_IfcStructuralActivity_type);
    declarations.push_back(IFC4_IfcStructuralItem_type);
    declarations.push_back(IFC4_IfcStructuralMember_type);
    declarations.push_back(IFC4_IfcStructuralReaction_type);
    declarations.push_back(IFC4_IfcStructuralSurfaceMember_type);
    declarations.push_back(IFC4_IfcStructuralSurfaceMemberVarying_type);
    declarations.push_back(IFC4_IfcStructuralSurfaceReaction_type);
    declarations.push_back(IFC4_IfcSubContractResourceType_type);
    declarations.push_back(IFC4_IfcSurfaceCurveSweptAreaSolid_type);
    declarations.push_back(IFC4_IfcSurfaceOfLinearExtrusion_type);
    declarations.push_back(IFC4_IfcSurfaceOfRevolution_type);
    declarations.push_back(IFC4_IfcSystemFurnitureElementType_type);
    declarations.push_back(IFC4_IfcTask_type);
    declarations.push_back(IFC4_IfcTaskType_type);
    declarations.push_back(IFC4_IfcTessellatedFaceSet_type);
    declarations.push_back(IFC4_IfcTransportElementType_type);
    declarations.push_back(IFC4_IfcTriangulatedFaceSet_type);
    declarations.push_back(IFC4_IfcWindowLiningProperties_type);
    declarations.push_back(IFC4_IfcWindowPanelProperties_type);
    declarations.push_back(IFC4_IfcActor_type);
    declarations.push_back(IFC4_IfcAdvancedBrep_type);
    declarations.push_back(IFC4_IfcAdvancedBrepWithVoids_type);
    declarations.push_back(IFC4_IfcAnnotation_type);
    declarations.push_back(IFC4_IfcBSplineSurface_type);
    declarations.push_back(IFC4_IfcBSplineSurfaceWithKnots_type);
    declarations.push_back(IFC4_IfcBlock_type);
    declarations.push_back(IFC4_IfcBooleanClippingResult_type);
    declarations.push_back(IFC4_IfcBoundedCurve_type);
    declarations.push_back(IFC4_IfcBuilding_type);
    declarations.push_back(IFC4_IfcBuildingElementType_type);
    declarations.push_back(IFC4_IfcBuildingStorey_type);
    declarations.push_back(IFC4_IfcChimneyType_type);
    declarations.push_back(IFC4_IfcCircleHollowProfileDef_type);
    declarations.push_back(IFC4_IfcCivilElementType_type);
    declarations.push_back(IFC4_IfcColumnType_type);
    declarations.push_back(IFC4_IfcComplexPropertyTemplate_type);
    declarations.push_back(IFC4_IfcCompositeCurve_type);
    declarations.push_back(IFC4_IfcCompositeCurveOnSurface_type);
    declarations.push_back(IFC4_IfcConic_type);
    declarations.push_back(IFC4_IfcConstructionEquipmentResourceType_type);
    declarations.push_back(IFC4_IfcConstructionMaterialResourceType_type);
    declarations.push_back(IFC4_IfcConstructionProductResourceType_type);
    declarations.push_back(IFC4_IfcConstructionResource_type);
    declarations.push_back(IFC4_IfcControl_type);
    declarations.push_back(IFC4_IfcCostItem_type);
    declarations.push_back(IFC4_IfcCostSchedule_type);
    declarations.push_back(IFC4_IfcCoveringType_type);
    declarations.push_back(IFC4_IfcCrewResource_type);
    declarations.push_back(IFC4_IfcCurtainWallType_type);
    declarations.push_back(IFC4_IfcCylindricalSurface_type);
    declarations.push_back(IFC4_IfcDistributionElementType_type);
    declarations.push_back(IFC4_IfcDistributionFlowElementType_type);
    declarations.push_back(IFC4_IfcDoorLiningProperties_type);
    declarations.push_back(IFC4_IfcDoorPanelProperties_type);
    declarations.push_back(IFC4_IfcDoorType_type);
    declarations.push_back(IFC4_IfcDraughtingPreDefinedColour_type);
    declarations.push_back(IFC4_IfcDraughtingPreDefinedCurveFont_type);
    declarations.push_back(IFC4_IfcElement_type);
    declarations.push_back(IFC4_IfcElementAssembly_type);
    declarations.push_back(IFC4_IfcElementAssemblyType_type);
    declarations.push_back(IFC4_IfcElementComponent_type);
    declarations.push_back(IFC4_IfcElementComponentType_type);
    declarations.push_back(IFC4_IfcEllipse_type);
    declarations.push_back(IFC4_IfcEnergyConversionDeviceType_type);
    declarations.push_back(IFC4_IfcEngineType_type);
    declarations.push_back(IFC4_IfcEvaporativeCoolerType_type);
    declarations.push_back(IFC4_IfcEvaporatorType_type);
    declarations.push_back(IFC4_IfcEvent_type);
    declarations.push_back(IFC4_IfcExternalSpatialStructureElement_type);
    declarations.push_back(IFC4_IfcFacetedBrep_type);
    declarations.push_back(IFC4_IfcFacetedBrepWithVoids_type);
    declarations.push_back(IFC4_IfcFastener_type);
    declarations.push_back(IFC4_IfcFastenerType_type);
    declarations.push_back(IFC4_IfcFeatureElement_type);
    declarations.push_back(IFC4_IfcFeatureElementAddition_type);
    declarations.push_back(IFC4_IfcFeatureElementSubtraction_type);
    declarations.push_back(IFC4_IfcFlowControllerType_type);
    declarations.push_back(IFC4_IfcFlowFittingType_type);
    declarations.push_back(IFC4_IfcFlowMeterType_type);
    declarations.push_back(IFC4_IfcFlowMovingDeviceType_type);
    declarations.push_back(IFC4_IfcFlowSegmentType_type);
    declarations.push_back(IFC4_IfcFlowStorageDeviceType_type);
    declarations.push_back(IFC4_IfcFlowTerminalType_type);
    declarations.push_back(IFC4_IfcFlowTreatmentDeviceType_type);
    declarations.push_back(IFC4_IfcFootingType_type);
    declarations.push_back(IFC4_IfcFurnishingElement_type);
    declarations.push_back(IFC4_IfcFurniture_type);
    declarations.push_back(IFC4_IfcGeographicElement_type);
    declarations.push_back(IFC4_IfcGrid_type);
    declarations.push_back(IFC4_IfcGroup_type);
    declarations.push_back(IFC4_IfcHeatExchangerType_type);
    declarations.push_back(IFC4_IfcHumidifierType_type);
    declarations.push_back(IFC4_IfcIndexedPolyCurve_type);
    declarations.push_back(IFC4_IfcInterceptorType_type);
    declarations.push_back(IFC4_IfcInventory_type);
    declarations.push_back(IFC4_IfcJunctionBoxType_type);
    declarations.push_back(IFC4_IfcLaborResource_type);
    declarations.push_back(IFC4_IfcLampType_type);
    declarations.push_back(IFC4_IfcLightFixtureType_type);
    declarations.push_back(IFC4_IfcMechanicalFastener_type);
    declarations.push_back(IFC4_IfcMechanicalFastenerType_type);
    declarations.push_back(IFC4_IfcMedicalDeviceType_type);
    declarations.push_back(IFC4_IfcMemberType_type);
    declarations.push_back(IFC4_IfcMotorConnectionType_type);
    declarations.push_back(IFC4_IfcOccupant_type);
    declarations.push_back(IFC4_IfcOpeningElement_type);
    declarations.push_back(IFC4_IfcOpeningStandardCase_type);
    declarations.push_back(IFC4_IfcOutletType_type);
    declarations.push_back(IFC4_IfcPerformanceHistory_type);
    declarations.push_back(IFC4_IfcPermeableCoveringProperties_type);
    declarations.push_back(IFC4_IfcPermit_type);
    declarations.push_back(IFC4_IfcPileType_type);
    declarations.push_back(IFC4_IfcPipeFittingType_type);
    declarations.push_back(IFC4_IfcPipeSegmentType_type);
    declarations.push_back(IFC4_IfcPlateType_type);
    declarations.push_back(IFC4_IfcPolyline_type);
    declarations.push_back(IFC4_IfcPort_type);
    declarations.push_back(IFC4_IfcProcedure_type);
    declarations.push_back(IFC4_IfcProjectOrder_type);
    declarations.push_back(IFC4_IfcProjectionElement_type);
    declarations.push_back(IFC4_IfcProtectiveDeviceType_type);
    declarations.push_back(IFC4_IfcPumpType_type);
    declarations.push_back(IFC4_IfcRailingType_type);
    declarations.push_back(IFC4_IfcRampFlightType_type);
    declarations.push_back(IFC4_IfcRampType_type);
    declarations.push_back(IFC4_IfcRationalBSplineSurfaceWithKnots_type);
    declarations.push_back(IFC4_IfcReinforcingElement_type);
    declarations.push_back(IFC4_IfcReinforcingElementType_type);
    declarations.push_back(IFC4_IfcReinforcingMesh_type);
    declarations.push_back(IFC4_IfcReinforcingMeshType_type);
    declarations.push_back(IFC4_IfcRelAggregates_type);
    declarations.push_back(IFC4_IfcRoofType_type);
    declarations.push_back(IFC4_IfcSanitaryTerminalType_type);
    declarations.push_back(IFC4_IfcShadingDeviceType_type);
    declarations.push_back(IFC4_IfcSite_type);
    declarations.push_back(IFC4_IfcSlabType_type);
    declarations.push_back(IFC4_IfcSolarDeviceType_type);
    declarations.push_back(IFC4_IfcSpace_type);
    declarations.push_back(IFC4_IfcSpaceHeaterType_type);
    declarations.push_back(IFC4_IfcSpaceType_type);
    declarations.push_back(IFC4_IfcStackTerminalType_type);
    declarations.push_back(IFC4_IfcStairFlightType_type);
    declarations.push_back(IFC4_IfcStairType_type);
    declarations.push_back(IFC4_IfcStructuralAction_type);
    declarations.push_back(IFC4_IfcStructuralConnection_type);
    declarations.push_back(IFC4_IfcStructuralCurveAction_type);
    declarations.push_back(IFC4_IfcStructuralCurveConnection_type);
    declarations.push_back(IFC4_IfcStructuralCurveMember_type);
    declarations.push_back(IFC4_IfcStructuralCurveMemberVarying_type);
    declarations.push_back(IFC4_IfcStructuralCurveReaction_type);
    declarations.push_back(IFC4_IfcStructuralLinearAction_type);
    declarations.push_back(IFC4_IfcStructuralLoadGroup_type);
    declarations.push_back(IFC4_IfcStructuralPointAction_type);
    declarations.push_back(IFC4_IfcStructuralPointConnection_type);
    declarations.push_back(IFC4_IfcStructuralPointReaction_type);
    declarations.push_back(IFC4_IfcStructuralResultGroup_type);
    declarations.push_back(IFC4_IfcStructuralSurfaceAction_type);
    declarations.push_back(IFC4_IfcStructuralSurfaceConnection_type);
    declarations.push_back(IFC4_IfcSubContractResource_type);
    declarations.push_back(IFC4_IfcSurfaceFeature_type);
    declarations.push_back(IFC4_IfcSwitchingDeviceType_type);
    declarations.push_back(IFC4_IfcSystem_type);
    declarations.push_back(IFC4_IfcSystemFurnitureElement_type);
    declarations.push_back(IFC4_IfcTankType_type);
    declarations.push_back(IFC4_IfcTendon_type);
    declarations.push_back(IFC4_IfcTendonAnchor_type);
    declarations.push_back(IFC4_IfcTendonAnchorType_type);
    declarations.push_back(IFC4_IfcTendonType_type);
    declarations.push_back(IFC4_IfcTransformerType_type);
    declarations.push_back(IFC4_IfcTransportElement_type);
    declarations.push_back(IFC4_IfcTrimmedCurve_type);
    declarations.push_back(IFC4_IfcTubeBundleType_type);
    declarations.push_back(IFC4_IfcUnitaryEquipmentType_type);
    declarations.push_back(IFC4_IfcValveType_type);
    declarations.push_back(IFC4_IfcVibrationIsolator_type);
    declarations.push_back(IFC4_IfcVibrationIsolatorType_type);
    declarations.push_back(IFC4_IfcVirtualElement_type);
    declarations.push_back(IFC4_IfcVoidingFeature_type);
    declarations.push_back(IFC4_IfcWallType_type);
    declarations.push_back(IFC4_IfcWasteTerminalType_type);
    declarations.push_back(IFC4_IfcWindowType_type);
    declarations.push_back(IFC4_IfcWorkCalendar_type);
    declarations.push_back(IFC4_IfcWorkControl_type);
    declarations.push_back(IFC4_IfcWorkPlan_type);
    declarations.push_back(IFC4_IfcWorkSchedule_type);
    declarations.push_back(IFC4_IfcZone_type);
    declarations.push_back(IFC4_IfcActionRequest_type);
    declarations.push_back(IFC4_IfcAirTerminalBoxType_type);
    declarations.push_back(IFC4_IfcAirTerminalType_type);
    declarations.push_back(IFC4_IfcAirToAirHeatRecoveryType_type);
    declarations.push_back(IFC4_IfcAsset_type);
    declarations.push_back(IFC4_IfcAudioVisualApplianceType_type);
    declarations.push_back(IFC4_IfcBSplineCurve_type);
    declarations.push_back(IFC4_IfcBSplineCurveWithKnots_type);
    declarations.push_back(IFC4_IfcBeamType_type);
    declarations.push_back(IFC4_IfcBoilerType_type);
    declarations.push_back(IFC4_IfcBoundaryCurve_type);
    declarations.push_back(IFC4_IfcBuildingElement_type);
    declarations.push_back(IFC4_IfcBuildingElementPart_type);
    declarations.push_back(IFC4_IfcBuildingElementPartType_type);
    declarations.push_back(IFC4_IfcBuildingElementProxy_type);
    declarations.push_back(IFC4_IfcBuildingElementProxyType_type);
    declarations.push_back(IFC4_IfcBuildingSystem_type);
    declarations.push_back(IFC4_IfcBurnerType_type);
    declarations.push_back(IFC4_IfcCableCarrierFittingType_type);
    declarations.push_back(IFC4_IfcCableCarrierSegmentType_type);
    declarations.push_back(IFC4_IfcCableFittingType_type);
    declarations.push_back(IFC4_IfcCableSegmentType_type);
    declarations.push_back(IFC4_IfcChillerType_type);
    declarations.push_back(IFC4_IfcChimney_type);
    declarations.push_back(IFC4_IfcCircle_type);
    declarations.push_back(IFC4_IfcCivilElement_type);
    declarations.push_back(IFC4_IfcCoilType_type);
    declarations.push_back(IFC4_IfcColumn_type);
    declarations.push_back(IFC4_IfcColumnStandardCase_type);
    declarations.push_back(IFC4_IfcCommunicationsApplianceType_type);
    declarations.push_back(IFC4_IfcCompressorType_type);
    declarations.push_back(IFC4_IfcCondenserType_type);
    declarations.push_back(IFC4_IfcConstructionEquipmentResource_type);
    declarations.push_back(IFC4_IfcConstructionMaterialResource_type);
    declarations.push_back(IFC4_IfcConstructionProductResource_type);
    declarations.push_back(IFC4_IfcCooledBeamType_type);
    declarations.push_back(IFC4_IfcCoolingTowerType_type);
    declarations.push_back(IFC4_IfcCovering_type);
    declarations.push_back(IFC4_IfcCurtainWall_type);
    declarations.push_back(IFC4_IfcDamperType_type);
    declarations.push_back(IFC4_IfcDiscreteAccessory_type);
    declarations.push_back(IFC4_IfcDiscreteAccessoryType_type);
    declarations.push_back(IFC4_IfcDistributionChamberElementType_type);
    declarations.push_back(IFC4_IfcDistributionControlElementType_type);
    declarations.push_back(IFC4_IfcDistributionElement_type);
    declarations.push_back(IFC4_IfcDistributionFlowElement_type);
    declarations.push_back(IFC4_IfcDistributionPort_type);
    declarations.push_back(IFC4_IfcDistributionSystem_type);
    declarations.push_back(IFC4_IfcDoor_type);
    declarations.push_back(IFC4_IfcDoorStandardCase_type);
    declarations.push_back(IFC4_IfcDuctFittingType_type);
    declarations.push_back(IFC4_IfcDuctSegmentType_type);
    declarations.push_back(IFC4_IfcDuctSilencerType_type);
    declarations.push_back(IFC4_IfcElectricApplianceType_type);
    declarations.push_back(IFC4_IfcElectricDistributionBoardType_type);
    declarations.push_back(IFC4_IfcElectricFlowStorageDeviceType_type);
    declarations.push_back(IFC4_IfcElectricGeneratorType_type);
    declarations.push_back(IFC4_IfcElectricMotorType_type);
    declarations.push_back(IFC4_IfcElectricTimeControlType_type);
    declarations.push_back(IFC4_IfcEnergyConversionDevice_type);
    declarations.push_back(IFC4_IfcEngine_type);
    declarations.push_back(IFC4_IfcEvaporativeCooler_type);
    declarations.push_back(IFC4_IfcEvaporator_type);
    declarations.push_back(IFC4_IfcExternalSpatialElement_type);
    declarations.push_back(IFC4_IfcFanType_type);
    declarations.push_back(IFC4_IfcFilterType_type);
    declarations.push_back(IFC4_IfcFireSuppressionTerminalType_type);
    declarations.push_back(IFC4_IfcFlowController_type);
    declarations.push_back(IFC4_IfcFlowFitting_type);
    declarations.push_back(IFC4_IfcFlowInstrumentType_type);
    declarations.push_back(IFC4_IfcFlowMeter_type);
    declarations.push_back(IFC4_IfcFlowMovingDevice_type);
    declarations.push_back(IFC4_IfcFlowSegment_type);
    declarations.push_back(IFC4_IfcFlowStorageDevice_type);
    declarations.push_back(IFC4_IfcFlowTerminal_type);
    declarations.push_back(IFC4_IfcFlowTreatmentDevice_type);
    declarations.push_back(IFC4_IfcFooting_type);
    declarations.push_back(IFC4_IfcHeatExchanger_type);
    declarations.push_back(IFC4_IfcHumidifier_type);
    declarations.push_back(IFC4_IfcInterceptor_type);
    declarations.push_back(IFC4_IfcJunctionBox_type);
    declarations.push_back(IFC4_IfcLamp_type);
    declarations.push_back(IFC4_IfcLightFixture_type);
    declarations.push_back(IFC4_IfcMedicalDevice_type);
    declarations.push_back(IFC4_IfcMember_type);
    declarations.push_back(IFC4_IfcMemberStandardCase_type);
    declarations.push_back(IFC4_IfcMotorConnection_type);
    declarations.push_back(IFC4_IfcOuterBoundaryCurve_type);
    declarations.push_back(IFC4_IfcOutlet_type);
    declarations.push_back(IFC4_IfcPile_type);
    declarations.push_back(IFC4_IfcPipeFitting_type);
    declarations.push_back(IFC4_IfcPipeSegment_type);
    declarations.push_back(IFC4_IfcPlate_type);
    declarations.push_back(IFC4_IfcPlateStandardCase_type);
    declarations.push_back(IFC4_IfcProtectiveDevice_type);
    declarations.push_back(IFC4_IfcProtectiveDeviceTrippingUnitType_type);
    declarations.push_back(IFC4_IfcPump_type);
    declarations.push_back(IFC4_IfcRailing_type);
    declarations.push_back(IFC4_IfcRamp_type);
    declarations.push_back(IFC4_IfcRampFlight_type);
    declarations.push_back(IFC4_IfcRationalBSplineCurveWithKnots_type);
    declarations.push_back(IFC4_IfcReinforcingBar_type);
    declarations.push_back(IFC4_IfcReinforcingBarType_type);
    declarations.push_back(IFC4_IfcRoof_type);
    declarations.push_back(IFC4_IfcSanitaryTerminal_type);
    declarations.push_back(IFC4_IfcSensorType_type);
    declarations.push_back(IFC4_IfcShadingDevice_type);
    declarations.push_back(IFC4_IfcSlab_type);
    declarations.push_back(IFC4_IfcSlabElementedCase_type);
    declarations.push_back(IFC4_IfcSlabStandardCase_type);
    declarations.push_back(IFC4_IfcSolarDevice_type);
    declarations.push_back(IFC4_IfcSpaceHeater_type);
    declarations.push_back(IFC4_IfcStackTerminal_type);
    declarations.push_back(IFC4_IfcStair_type);
    declarations.push_back(IFC4_IfcStairFlight_type);
    declarations.push_back(IFC4_IfcStructuralAnalysisModel_type);
    declarations.push_back(IFC4_IfcStructuralLoadCase_type);
    declarations.push_back(IFC4_IfcStructuralPlanarAction_type);
    declarations.push_back(IFC4_IfcSwitchingDevice_type);
    declarations.push_back(IFC4_IfcTank_type);
    declarations.push_back(IFC4_IfcTransformer_type);
    declarations.push_back(IFC4_IfcTubeBundle_type);
    declarations.push_back(IFC4_IfcUnitaryControlElementType_type);
    declarations.push_back(IFC4_IfcUnitaryEquipment_type);
    declarations.push_back(IFC4_IfcValve_type);
    declarations.push_back(IFC4_IfcWall_type);
    declarations.push_back(IFC4_IfcWallElementedCase_type);
    declarations.push_back(IFC4_IfcWallStandardCase_type);
    declarations.push_back(IFC4_IfcWasteTerminal_type);
    declarations.push_back(IFC4_IfcWindow_type);
    declarations.push_back(IFC4_IfcWindowStandardCase_type);
    declarations.push_back(IFC4_IfcActuatorType_type);
    declarations.push_back(IFC4_IfcAirTerminal_type);
    declarations.push_back(IFC4_IfcAirTerminalBox_type);
    declarations.push_back(IFC4_IfcAirToAirHeatRecovery_type);
    declarations.push_back(IFC4_IfcAlarmType_type);
    declarations.push_back(IFC4_IfcAudioVisualAppliance_type);
    declarations.push_back(IFC4_IfcBeam_type);
    declarations.push_back(IFC4_IfcBeamStandardCase_type);
    declarations.push_back(IFC4_IfcBoiler_type);
    declarations.push_back(IFC4_IfcBurner_type);
    declarations.push_back(IFC4_IfcCableCarrierFitting_type);
    declarations.push_back(IFC4_IfcCableCarrierSegment_type);
    declarations.push_back(IFC4_IfcCableFitting_type);
    declarations.push_back(IFC4_IfcCableSegment_type);
    declarations.push_back(IFC4_IfcChiller_type);
    declarations.push_back(IFC4_IfcCoil_type);
    declarations.push_back(IFC4_IfcCommunicationsAppliance_type);
    declarations.push_back(IFC4_IfcCompressor_type);
    declarations.push_back(IFC4_IfcCondenser_type);
    declarations.push_back(IFC4_IfcControllerType_type);
    declarations.push_back(IFC4_IfcCooledBeam_type);
    declarations.push_back(IFC4_IfcCoolingTower_type);
    declarations.push_back(IFC4_IfcDamper_type);
    declarations.push_back(IFC4_IfcDistributionChamberElement_type);
    declarations.push_back(IFC4_IfcDistributionCircuit_type);
    declarations.push_back(IFC4_IfcDistributionControlElement_type);
    declarations.push_back(IFC4_IfcDuctFitting_type);
    declarations.push_back(IFC4_IfcDuctSegment_type);
    declarations.push_back(IFC4_IfcDuctSilencer_type);
    declarations.push_back(IFC4_IfcElectricAppliance_type);
    declarations.push_back(IFC4_IfcElectricDistributionBoard_type);
    declarations.push_back(IFC4_IfcElectricFlowStorageDevice_type);
    declarations.push_back(IFC4_IfcElectricGenerator_type);
    declarations.push_back(IFC4_IfcElectricMotor_type);
    declarations.push_back(IFC4_IfcElectricTimeControl_type);
    declarations.push_back(IFC4_IfcFan_type);
    declarations.push_back(IFC4_IfcFilter_type);
    declarations.push_back(IFC4_IfcFireSuppressionTerminal_type);
    declarations.push_back(IFC4_IfcFlowInstrument_type);
    declarations.push_back(IFC4_IfcProtectiveDeviceTrippingUnit_type);
    declarations.push_back(IFC4_IfcSensor_type);
    declarations.push_back(IFC4_IfcUnitaryControlElement_type);
    declarations.push_back(IFC4_IfcActuator_type);
    declarations.push_back(IFC4_IfcAlarm_type);
    declarations.push_back(IFC4_IfcController_type);
    declarations.push_back(IFC4_IfcActorSelect_type);
    declarations.push_back(IFC4_IfcAxis2Placement_type);
    declarations.push_back(IFC4_IfcBendingParameterSelect_type);
    declarations.push_back(IFC4_IfcBooleanOperand_type);
    declarations.push_back(IFC4_IfcClassificationReferenceSelect_type);
    declarations.push_back(IFC4_IfcClassificationSelect_type);
    declarations.push_back(IFC4_IfcColour_type);
    declarations.push_back(IFC4_IfcColourOrFactor_type);
    declarations.push_back(IFC4_IfcCoordinateReferenceSystemSelect_type);
    declarations.push_back(IFC4_IfcCsgSelect_type);
    declarations.push_back(IFC4_IfcCurveOnSurface_type);
    declarations.push_back(IFC4_IfcCurveOrEdgeCurve_type);
    declarations.push_back(IFC4_IfcCurveStyleFontSelect_type);
    declarations.push_back(IFC4_IfcDefinitionSelect_type);
    declarations.push_back(IFC4_IfcDerivedMeasureValue_type);
    declarations.push_back(IFC4_IfcDocumentSelect_type);
    declarations.push_back(IFC4_IfcFillStyleSelect_type);
    declarations.push_back(IFC4_IfcGeometricSetSelect_type);
    declarations.push_back(IFC4_IfcGridPlacementDirectionSelect_type);
    declarations.push_back(IFC4_IfcHatchLineDistanceSelect_type);
    declarations.push_back(IFC4_IfcLayeredItem_type);
    declarations.push_back(IFC4_IfcLibrarySelect_type);
    declarations.push_back(IFC4_IfcLightDistributionDataSourceSelect_type);
    declarations.push_back(IFC4_IfcMaterialSelect_type);
    declarations.push_back(IFC4_IfcMeasureValue_type);
    declarations.push_back(IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type);
    declarations.push_back(IFC4_IfcModulusOfSubgradeReactionSelect_type);
    declarations.push_back(IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type);
    declarations.push_back(IFC4_IfcObjectReferenceSelect_type);
    declarations.push_back(IFC4_IfcPointOrVertexPoint_type);
    declarations.push_back(IFC4_IfcPresentationStyleSelect_type);
    declarations.push_back(IFC4_IfcProcessSelect_type);
    declarations.push_back(IFC4_IfcProductRepresentationSelect_type);
    declarations.push_back(IFC4_IfcProductSelect_type);
    declarations.push_back(IFC4_IfcPropertySetDefinitionSelect_type);
    declarations.push_back(IFC4_IfcResourceObjectSelect_type);
    declarations.push_back(IFC4_IfcResourceSelect_type);
    declarations.push_back(IFC4_IfcRotationalStiffnessSelect_type);
    declarations.push_back(IFC4_IfcSegmentIndexSelect_type);
    declarations.push_back(IFC4_IfcShell_type);
    declarations.push_back(IFC4_IfcSimpleValue_type);
    declarations.push_back(IFC4_IfcSizeSelect_type);
    declarations.push_back(IFC4_IfcSolidOrShell_type);
    declarations.push_back(IFC4_IfcSpaceBoundarySelect_type);
    declarations.push_back(IFC4_IfcSpecularHighlightSelect_type);
    declarations.push_back(IFC4_IfcStructuralActivityAssignmentSelect_type);
    declarations.push_back(IFC4_IfcStyleAssignmentSelect_type);
    declarations.push_back(IFC4_IfcSurfaceOrFaceSurface_type);
    declarations.push_back(IFC4_IfcSurfaceStyleElementSelect_type);
    declarations.push_back(IFC4_IfcTextFontSelect_type);
    declarations.push_back(IFC4_IfcTimeOrRatioSelect_type);
    declarations.push_back(IFC4_IfcTranslationalStiffnessSelect_type);
    declarations.push_back(IFC4_IfcTrimmingSelect_type);
    declarations.push_back(IFC4_IfcUnit_type);
    declarations.push_back(IFC4_IfcValue_type);
    declarations.push_back(IFC4_IfcVectorOrDirection_type);
    declarations.push_back(IFC4_IfcWarpingStiffnessSelect_type);
    declarations.push_back(IFC4_IfcAppliedValueSelect_type);
    declarations.push_back(IFC4_IfcCurveFontOrScaledCurveFontSelect_type);
    declarations.push_back(IFC4_IfcMetricValueSelect_type);
    return new schema_definition("IFC4", declarations, new IFC4_instance_factory());
}


#ifdef _MSC_VER
#pragma optimize("", on)
#endif
        
const schema_definition& Ifc4::get_schema() {

    static const schema_definition* s = IFC4_populate_schema();
    return *s;
}

