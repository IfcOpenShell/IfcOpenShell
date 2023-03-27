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
entity* IFC4_IfcIndexedPolygonalFace_type = 0;
entity* IFC4_IfcIndexedPolygonalFaceWithVoids_type = 0;
entity* IFC4_IfcIndexedTextureMap_type = 0;
entity* IFC4_IfcIndexedTriangleTextureMap_type = 0;
entity* IFC4_IfcInterceptor_type = 0;
entity* IFC4_IfcInterceptorType_type = 0;
entity* IFC4_IfcIntersectionCurve_type = 0;
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
entity* IFC4_IfcPolygonalFaceSet_type = 0;
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
entity* IFC4_IfcSeamCurve_type = 0;
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
entity* IFC4_IfcSphericalSurface_type = 0;
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
entity* IFC4_IfcSurfaceCurve_type = 0;
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
entity* IFC4_IfcToroidalSurface_type = 0;
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
enumeration_type* IFC4_IfcPreferredSurfaceCurveRepresentation_type = 0;
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
            case 3: return new ::Ifc4::IfcActionRequestTypeEnum(data);
            case 4: return new ::Ifc4::IfcActionSourceTypeEnum(data);
            case 5: return new ::Ifc4::IfcActionTypeEnum(data);
            case 6: return new ::Ifc4::IfcActor(data);
            case 7: return new ::Ifc4::IfcActorRole(data);
            case 9: return new ::Ifc4::IfcActuator(data);
            case 10: return new ::Ifc4::IfcActuatorType(data);
            case 11: return new ::Ifc4::IfcActuatorTypeEnum(data);
            case 12: return new ::Ifc4::IfcAddress(data);
            case 13: return new ::Ifc4::IfcAddressTypeEnum(data);
            case 14: return new ::Ifc4::IfcAdvancedBrep(data);
            case 15: return new ::Ifc4::IfcAdvancedBrepWithVoids(data);
            case 16: return new ::Ifc4::IfcAdvancedFace(data);
            case 17: return new ::Ifc4::IfcAirTerminal(data);
            case 18: return new ::Ifc4::IfcAirTerminalBox(data);
            case 19: return new ::Ifc4::IfcAirTerminalBoxType(data);
            case 20: return new ::Ifc4::IfcAirTerminalBoxTypeEnum(data);
            case 21: return new ::Ifc4::IfcAirTerminalType(data);
            case 22: return new ::Ifc4::IfcAirTerminalTypeEnum(data);
            case 23: return new ::Ifc4::IfcAirToAirHeatRecovery(data);
            case 24: return new ::Ifc4::IfcAirToAirHeatRecoveryType(data);
            case 25: return new ::Ifc4::IfcAirToAirHeatRecoveryTypeEnum(data);
            case 26: return new ::Ifc4::IfcAlarm(data);
            case 27: return new ::Ifc4::IfcAlarmType(data);
            case 28: return new ::Ifc4::IfcAlarmTypeEnum(data);
            case 29: return new ::Ifc4::IfcAmountOfSubstanceMeasure(data);
            case 30: return new ::Ifc4::IfcAnalysisModelTypeEnum(data);
            case 31: return new ::Ifc4::IfcAnalysisTheoryTypeEnum(data);
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
            case 46: return new ::Ifc4::IfcArithmeticOperatorEnum(data);
            case 47: return new ::Ifc4::IfcAssemblyPlaceEnum(data);
            case 48: return new ::Ifc4::IfcAsset(data);
            case 49: return new ::Ifc4::IfcAsymmetricIShapeProfileDef(data);
            case 50: return new ::Ifc4::IfcAudioVisualAppliance(data);
            case 51: return new ::Ifc4::IfcAudioVisualApplianceType(data);
            case 52: return new ::Ifc4::IfcAudioVisualApplianceTypeEnum(data);
            case 53: return new ::Ifc4::IfcAxis1Placement(data);
            case 55: return new ::Ifc4::IfcAxis2Placement2D(data);
            case 56: return new ::Ifc4::IfcAxis2Placement3D(data);
            case 57: return new ::Ifc4::IfcBeam(data);
            case 58: return new ::Ifc4::IfcBeamStandardCase(data);
            case 59: return new ::Ifc4::IfcBeamType(data);
            case 60: return new ::Ifc4::IfcBeamTypeEnum(data);
            case 61: return new ::Ifc4::IfcBenchmarkEnum(data);
            case 63: return new ::Ifc4::IfcBinary(data);
            case 64: return new ::Ifc4::IfcBlobTexture(data);
            case 65: return new ::Ifc4::IfcBlock(data);
            case 66: return new ::Ifc4::IfcBoiler(data);
            case 67: return new ::Ifc4::IfcBoilerType(data);
            case 68: return new ::Ifc4::IfcBoilerTypeEnum(data);
            case 69: return new ::Ifc4::IfcBoolean(data);
            case 70: return new ::Ifc4::IfcBooleanClippingResult(data);
            case 72: return new ::Ifc4::IfcBooleanOperator(data);
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
            case 86: return new ::Ifc4::IfcBSplineCurveForm(data);
            case 87: return new ::Ifc4::IfcBSplineCurveWithKnots(data);
            case 88: return new ::Ifc4::IfcBSplineSurface(data);
            case 89: return new ::Ifc4::IfcBSplineSurfaceForm(data);
            case 90: return new ::Ifc4::IfcBSplineSurfaceWithKnots(data);
            case 91: return new ::Ifc4::IfcBuilding(data);
            case 92: return new ::Ifc4::IfcBuildingElement(data);
            case 93: return new ::Ifc4::IfcBuildingElementPart(data);
            case 94: return new ::Ifc4::IfcBuildingElementPartType(data);
            case 95: return new ::Ifc4::IfcBuildingElementPartTypeEnum(data);
            case 96: return new ::Ifc4::IfcBuildingElementProxy(data);
            case 97: return new ::Ifc4::IfcBuildingElementProxyType(data);
            case 98: return new ::Ifc4::IfcBuildingElementProxyTypeEnum(data);
            case 99: return new ::Ifc4::IfcBuildingElementType(data);
            case 100: return new ::Ifc4::IfcBuildingStorey(data);
            case 101: return new ::Ifc4::IfcBuildingSystem(data);
            case 102: return new ::Ifc4::IfcBuildingSystemTypeEnum(data);
            case 103: return new ::Ifc4::IfcBurner(data);
            case 104: return new ::Ifc4::IfcBurnerType(data);
            case 105: return new ::Ifc4::IfcBurnerTypeEnum(data);
            case 106: return new ::Ifc4::IfcCableCarrierFitting(data);
            case 107: return new ::Ifc4::IfcCableCarrierFittingType(data);
            case 108: return new ::Ifc4::IfcCableCarrierFittingTypeEnum(data);
            case 109: return new ::Ifc4::IfcCableCarrierSegment(data);
            case 110: return new ::Ifc4::IfcCableCarrierSegmentType(data);
            case 111: return new ::Ifc4::IfcCableCarrierSegmentTypeEnum(data);
            case 112: return new ::Ifc4::IfcCableFitting(data);
            case 113: return new ::Ifc4::IfcCableFittingType(data);
            case 114: return new ::Ifc4::IfcCableFittingTypeEnum(data);
            case 115: return new ::Ifc4::IfcCableSegment(data);
            case 116: return new ::Ifc4::IfcCableSegmentType(data);
            case 117: return new ::Ifc4::IfcCableSegmentTypeEnum(data);
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
            case 129: return new ::Ifc4::IfcChangeActionEnum(data);
            case 130: return new ::Ifc4::IfcChiller(data);
            case 131: return new ::Ifc4::IfcChillerType(data);
            case 132: return new ::Ifc4::IfcChillerTypeEnum(data);
            case 133: return new ::Ifc4::IfcChimney(data);
            case 134: return new ::Ifc4::IfcChimneyType(data);
            case 135: return new ::Ifc4::IfcChimneyTypeEnum(data);
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
            case 148: return new ::Ifc4::IfcCoilTypeEnum(data);
            case 151: return new ::Ifc4::IfcColourRgb(data);
            case 152: return new ::Ifc4::IfcColourRgbList(data);
            case 153: return new ::Ifc4::IfcColourSpecification(data);
            case 154: return new ::Ifc4::IfcColumn(data);
            case 155: return new ::Ifc4::IfcColumnStandardCase(data);
            case 156: return new ::Ifc4::IfcColumnType(data);
            case 157: return new ::Ifc4::IfcColumnTypeEnum(data);
            case 158: return new ::Ifc4::IfcCommunicationsAppliance(data);
            case 159: return new ::Ifc4::IfcCommunicationsApplianceType(data);
            case 160: return new ::Ifc4::IfcCommunicationsApplianceTypeEnum(data);
            case 161: return new ::Ifc4::IfcComplexNumber(data);
            case 162: return new ::Ifc4::IfcComplexProperty(data);
            case 163: return new ::Ifc4::IfcComplexPropertyTemplate(data);
            case 164: return new ::Ifc4::IfcComplexPropertyTemplateTypeEnum(data);
            case 165: return new ::Ifc4::IfcCompositeCurve(data);
            case 166: return new ::Ifc4::IfcCompositeCurveOnSurface(data);
            case 167: return new ::Ifc4::IfcCompositeCurveSegment(data);
            case 168: return new ::Ifc4::IfcCompositeProfileDef(data);
            case 169: return new ::Ifc4::IfcCompoundPlaneAngleMeasure(data);
            case 170: return new ::Ifc4::IfcCompressor(data);
            case 171: return new ::Ifc4::IfcCompressorType(data);
            case 172: return new ::Ifc4::IfcCompressorTypeEnum(data);
            case 173: return new ::Ifc4::IfcCondenser(data);
            case 174: return new ::Ifc4::IfcCondenserType(data);
            case 175: return new ::Ifc4::IfcCondenserTypeEnum(data);
            case 176: return new ::Ifc4::IfcConic(data);
            case 177: return new ::Ifc4::IfcConnectedFaceSet(data);
            case 178: return new ::Ifc4::IfcConnectionCurveGeometry(data);
            case 179: return new ::Ifc4::IfcConnectionGeometry(data);
            case 180: return new ::Ifc4::IfcConnectionPointEccentricity(data);
            case 181: return new ::Ifc4::IfcConnectionPointGeometry(data);
            case 182: return new ::Ifc4::IfcConnectionSurfaceGeometry(data);
            case 183: return new ::Ifc4::IfcConnectionTypeEnum(data);
            case 184: return new ::Ifc4::IfcConnectionVolumeGeometry(data);
            case 185: return new ::Ifc4::IfcConstraint(data);
            case 186: return new ::Ifc4::IfcConstraintEnum(data);
            case 187: return new ::Ifc4::IfcConstructionEquipmentResource(data);
            case 188: return new ::Ifc4::IfcConstructionEquipmentResourceType(data);
            case 189: return new ::Ifc4::IfcConstructionEquipmentResourceTypeEnum(data);
            case 190: return new ::Ifc4::IfcConstructionMaterialResource(data);
            case 191: return new ::Ifc4::IfcConstructionMaterialResourceType(data);
            case 192: return new ::Ifc4::IfcConstructionMaterialResourceTypeEnum(data);
            case 193: return new ::Ifc4::IfcConstructionProductResource(data);
            case 194: return new ::Ifc4::IfcConstructionProductResourceType(data);
            case 195: return new ::Ifc4::IfcConstructionProductResourceTypeEnum(data);
            case 196: return new ::Ifc4::IfcConstructionResource(data);
            case 197: return new ::Ifc4::IfcConstructionResourceType(data);
            case 198: return new ::Ifc4::IfcContext(data);
            case 199: return new ::Ifc4::IfcContextDependentMeasure(data);
            case 200: return new ::Ifc4::IfcContextDependentUnit(data);
            case 201: return new ::Ifc4::IfcControl(data);
            case 202: return new ::Ifc4::IfcController(data);
            case 203: return new ::Ifc4::IfcControllerType(data);
            case 204: return new ::Ifc4::IfcControllerTypeEnum(data);
            case 205: return new ::Ifc4::IfcConversionBasedUnit(data);
            case 206: return new ::Ifc4::IfcConversionBasedUnitWithOffset(data);
            case 207: return new ::Ifc4::IfcCooledBeam(data);
            case 208: return new ::Ifc4::IfcCooledBeamType(data);
            case 209: return new ::Ifc4::IfcCooledBeamTypeEnum(data);
            case 210: return new ::Ifc4::IfcCoolingTower(data);
            case 211: return new ::Ifc4::IfcCoolingTowerType(data);
            case 212: return new ::Ifc4::IfcCoolingTowerTypeEnum(data);
            case 213: return new ::Ifc4::IfcCoordinateOperation(data);
            case 214: return new ::Ifc4::IfcCoordinateReferenceSystem(data);
            case 216: return new ::Ifc4::IfcCostItem(data);
            case 217: return new ::Ifc4::IfcCostItemTypeEnum(data);
            case 218: return new ::Ifc4::IfcCostSchedule(data);
            case 219: return new ::Ifc4::IfcCostScheduleTypeEnum(data);
            case 220: return new ::Ifc4::IfcCostValue(data);
            case 221: return new ::Ifc4::IfcCountMeasure(data);
            case 222: return new ::Ifc4::IfcCovering(data);
            case 223: return new ::Ifc4::IfcCoveringType(data);
            case 224: return new ::Ifc4::IfcCoveringTypeEnum(data);
            case 225: return new ::Ifc4::IfcCrewResource(data);
            case 226: return new ::Ifc4::IfcCrewResourceType(data);
            case 227: return new ::Ifc4::IfcCrewResourceTypeEnum(data);
            case 228: return new ::Ifc4::IfcCsgPrimitive3D(data);
            case 230: return new ::Ifc4::IfcCsgSolid(data);
            case 231: return new ::Ifc4::IfcCShapeProfileDef(data);
            case 232: return new ::Ifc4::IfcCurrencyRelationship(data);
            case 233: return new ::Ifc4::IfcCurtainWall(data);
            case 234: return new ::Ifc4::IfcCurtainWallType(data);
            case 235: return new ::Ifc4::IfcCurtainWallTypeEnum(data);
            case 236: return new ::Ifc4::IfcCurvatureMeasure(data);
            case 237: return new ::Ifc4::IfcCurve(data);
            case 238: return new ::Ifc4::IfcCurveBoundedPlane(data);
            case 239: return new ::Ifc4::IfcCurveBoundedSurface(data);
            case 241: return new ::Ifc4::IfcCurveInterpolationEnum(data);
            case 244: return new ::Ifc4::IfcCurveStyle(data);
            case 245: return new ::Ifc4::IfcCurveStyleFont(data);
            case 246: return new ::Ifc4::IfcCurveStyleFontAndScaling(data);
            case 247: return new ::Ifc4::IfcCurveStyleFontPattern(data);
            case 249: return new ::Ifc4::IfcCylindricalSurface(data);
            case 250: return new ::Ifc4::IfcDamper(data);
            case 251: return new ::Ifc4::IfcDamperType(data);
            case 252: return new ::Ifc4::IfcDamperTypeEnum(data);
            case 253: return new ::Ifc4::IfcDataOriginEnum(data);
            case 254: return new ::Ifc4::IfcDate(data);
            case 255: return new ::Ifc4::IfcDateTime(data);
            case 256: return new ::Ifc4::IfcDayInMonthNumber(data);
            case 257: return new ::Ifc4::IfcDayInWeekNumber(data);
            case 260: return new ::Ifc4::IfcDerivedProfileDef(data);
            case 261: return new ::Ifc4::IfcDerivedUnit(data);
            case 262: return new ::Ifc4::IfcDerivedUnitElement(data);
            case 263: return new ::Ifc4::IfcDerivedUnitEnum(data);
            case 264: return new ::Ifc4::IfcDescriptiveMeasure(data);
            case 265: return new ::Ifc4::IfcDimensionalExponents(data);
            case 266: return new ::Ifc4::IfcDimensionCount(data);
            case 267: return new ::Ifc4::IfcDirection(data);
            case 268: return new ::Ifc4::IfcDirectionSenseEnum(data);
            case 269: return new ::Ifc4::IfcDiscreteAccessory(data);
            case 270: return new ::Ifc4::IfcDiscreteAccessoryType(data);
            case 271: return new ::Ifc4::IfcDiscreteAccessoryTypeEnum(data);
            case 272: return new ::Ifc4::IfcDistributionChamberElement(data);
            case 273: return new ::Ifc4::IfcDistributionChamberElementType(data);
            case 274: return new ::Ifc4::IfcDistributionChamberElementTypeEnum(data);
            case 275: return new ::Ifc4::IfcDistributionCircuit(data);
            case 276: return new ::Ifc4::IfcDistributionControlElement(data);
            case 277: return new ::Ifc4::IfcDistributionControlElementType(data);
            case 278: return new ::Ifc4::IfcDistributionElement(data);
            case 279: return new ::Ifc4::IfcDistributionElementType(data);
            case 280: return new ::Ifc4::IfcDistributionFlowElement(data);
            case 281: return new ::Ifc4::IfcDistributionFlowElementType(data);
            case 282: return new ::Ifc4::IfcDistributionPort(data);
            case 283: return new ::Ifc4::IfcDistributionPortTypeEnum(data);
            case 284: return new ::Ifc4::IfcDistributionSystem(data);
            case 285: return new ::Ifc4::IfcDistributionSystemEnum(data);
            case 286: return new ::Ifc4::IfcDocumentConfidentialityEnum(data);
            case 287: return new ::Ifc4::IfcDocumentInformation(data);
            case 288: return new ::Ifc4::IfcDocumentInformationRelationship(data);
            case 289: return new ::Ifc4::IfcDocumentReference(data);
            case 291: return new ::Ifc4::IfcDocumentStatusEnum(data);
            case 292: return new ::Ifc4::IfcDoor(data);
            case 293: return new ::Ifc4::IfcDoorLiningProperties(data);
            case 294: return new ::Ifc4::IfcDoorPanelOperationEnum(data);
            case 295: return new ::Ifc4::IfcDoorPanelPositionEnum(data);
            case 296: return new ::Ifc4::IfcDoorPanelProperties(data);
            case 297: return new ::Ifc4::IfcDoorStandardCase(data);
            case 298: return new ::Ifc4::IfcDoorStyle(data);
            case 299: return new ::Ifc4::IfcDoorStyleConstructionEnum(data);
            case 300: return new ::Ifc4::IfcDoorStyleOperationEnum(data);
            case 301: return new ::Ifc4::IfcDoorType(data);
            case 302: return new ::Ifc4::IfcDoorTypeEnum(data);
            case 303: return new ::Ifc4::IfcDoorTypeOperationEnum(data);
            case 304: return new ::Ifc4::IfcDoseEquivalentMeasure(data);
            case 305: return new ::Ifc4::IfcDraughtingPreDefinedColour(data);
            case 306: return new ::Ifc4::IfcDraughtingPreDefinedCurveFont(data);
            case 307: return new ::Ifc4::IfcDuctFitting(data);
            case 308: return new ::Ifc4::IfcDuctFittingType(data);
            case 309: return new ::Ifc4::IfcDuctFittingTypeEnum(data);
            case 310: return new ::Ifc4::IfcDuctSegment(data);
            case 311: return new ::Ifc4::IfcDuctSegmentType(data);
            case 312: return new ::Ifc4::IfcDuctSegmentTypeEnum(data);
            case 313: return new ::Ifc4::IfcDuctSilencer(data);
            case 314: return new ::Ifc4::IfcDuctSilencerType(data);
            case 315: return new ::Ifc4::IfcDuctSilencerTypeEnum(data);
            case 316: return new ::Ifc4::IfcDuration(data);
            case 317: return new ::Ifc4::IfcDynamicViscosityMeasure(data);
            case 318: return new ::Ifc4::IfcEdge(data);
            case 319: return new ::Ifc4::IfcEdgeCurve(data);
            case 320: return new ::Ifc4::IfcEdgeLoop(data);
            case 321: return new ::Ifc4::IfcElectricAppliance(data);
            case 322: return new ::Ifc4::IfcElectricApplianceType(data);
            case 323: return new ::Ifc4::IfcElectricApplianceTypeEnum(data);
            case 324: return new ::Ifc4::IfcElectricCapacitanceMeasure(data);
            case 325: return new ::Ifc4::IfcElectricChargeMeasure(data);
            case 326: return new ::Ifc4::IfcElectricConductanceMeasure(data);
            case 327: return new ::Ifc4::IfcElectricCurrentMeasure(data);
            case 328: return new ::Ifc4::IfcElectricDistributionBoard(data);
            case 329: return new ::Ifc4::IfcElectricDistributionBoardType(data);
            case 330: return new ::Ifc4::IfcElectricDistributionBoardTypeEnum(data);
            case 331: return new ::Ifc4::IfcElectricFlowStorageDevice(data);
            case 332: return new ::Ifc4::IfcElectricFlowStorageDeviceType(data);
            case 333: return new ::Ifc4::IfcElectricFlowStorageDeviceTypeEnum(data);
            case 334: return new ::Ifc4::IfcElectricGenerator(data);
            case 335: return new ::Ifc4::IfcElectricGeneratorType(data);
            case 336: return new ::Ifc4::IfcElectricGeneratorTypeEnum(data);
            case 337: return new ::Ifc4::IfcElectricMotor(data);
            case 338: return new ::Ifc4::IfcElectricMotorType(data);
            case 339: return new ::Ifc4::IfcElectricMotorTypeEnum(data);
            case 340: return new ::Ifc4::IfcElectricResistanceMeasure(data);
            case 341: return new ::Ifc4::IfcElectricTimeControl(data);
            case 342: return new ::Ifc4::IfcElectricTimeControlType(data);
            case 343: return new ::Ifc4::IfcElectricTimeControlTypeEnum(data);
            case 344: return new ::Ifc4::IfcElectricVoltageMeasure(data);
            case 345: return new ::Ifc4::IfcElement(data);
            case 346: return new ::Ifc4::IfcElementarySurface(data);
            case 347: return new ::Ifc4::IfcElementAssembly(data);
            case 348: return new ::Ifc4::IfcElementAssemblyType(data);
            case 349: return new ::Ifc4::IfcElementAssemblyTypeEnum(data);
            case 350: return new ::Ifc4::IfcElementComponent(data);
            case 351: return new ::Ifc4::IfcElementComponentType(data);
            case 352: return new ::Ifc4::IfcElementCompositionEnum(data);
            case 353: return new ::Ifc4::IfcElementQuantity(data);
            case 354: return new ::Ifc4::IfcElementType(data);
            case 355: return new ::Ifc4::IfcEllipse(data);
            case 356: return new ::Ifc4::IfcEllipseProfileDef(data);
            case 357: return new ::Ifc4::IfcEnergyConversionDevice(data);
            case 358: return new ::Ifc4::IfcEnergyConversionDeviceType(data);
            case 359: return new ::Ifc4::IfcEnergyMeasure(data);
            case 360: return new ::Ifc4::IfcEngine(data);
            case 361: return new ::Ifc4::IfcEngineType(data);
            case 362: return new ::Ifc4::IfcEngineTypeEnum(data);
            case 363: return new ::Ifc4::IfcEvaporativeCooler(data);
            case 364: return new ::Ifc4::IfcEvaporativeCoolerType(data);
            case 365: return new ::Ifc4::IfcEvaporativeCoolerTypeEnum(data);
            case 366: return new ::Ifc4::IfcEvaporator(data);
            case 367: return new ::Ifc4::IfcEvaporatorType(data);
            case 368: return new ::Ifc4::IfcEvaporatorTypeEnum(data);
            case 369: return new ::Ifc4::IfcEvent(data);
            case 370: return new ::Ifc4::IfcEventTime(data);
            case 371: return new ::Ifc4::IfcEventTriggerTypeEnum(data);
            case 372: return new ::Ifc4::IfcEventType(data);
            case 373: return new ::Ifc4::IfcEventTypeEnum(data);
            case 374: return new ::Ifc4::IfcExtendedProperties(data);
            case 375: return new ::Ifc4::IfcExternalInformation(data);
            case 376: return new ::Ifc4::IfcExternallyDefinedHatchStyle(data);
            case 377: return new ::Ifc4::IfcExternallyDefinedSurfaceStyle(data);
            case 378: return new ::Ifc4::IfcExternallyDefinedTextFont(data);
            case 379: return new ::Ifc4::IfcExternalReference(data);
            case 380: return new ::Ifc4::IfcExternalReferenceRelationship(data);
            case 381: return new ::Ifc4::IfcExternalSpatialElement(data);
            case 382: return new ::Ifc4::IfcExternalSpatialElementTypeEnum(data);
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
            case 396: return new ::Ifc4::IfcFanTypeEnum(data);
            case 397: return new ::Ifc4::IfcFastener(data);
            case 398: return new ::Ifc4::IfcFastenerType(data);
            case 399: return new ::Ifc4::IfcFastenerTypeEnum(data);
            case 400: return new ::Ifc4::IfcFeatureElement(data);
            case 401: return new ::Ifc4::IfcFeatureElementAddition(data);
            case 402: return new ::Ifc4::IfcFeatureElementSubtraction(data);
            case 403: return new ::Ifc4::IfcFillAreaStyle(data);
            case 404: return new ::Ifc4::IfcFillAreaStyleHatching(data);
            case 405: return new ::Ifc4::IfcFillAreaStyleTiles(data);
            case 407: return new ::Ifc4::IfcFilter(data);
            case 408: return new ::Ifc4::IfcFilterType(data);
            case 409: return new ::Ifc4::IfcFilterTypeEnum(data);
            case 410: return new ::Ifc4::IfcFireSuppressionTerminal(data);
            case 411: return new ::Ifc4::IfcFireSuppressionTerminalType(data);
            case 412: return new ::Ifc4::IfcFireSuppressionTerminalTypeEnum(data);
            case 413: return new ::Ifc4::IfcFixedReferenceSweptAreaSolid(data);
            case 414: return new ::Ifc4::IfcFlowController(data);
            case 415: return new ::Ifc4::IfcFlowControllerType(data);
            case 416: return new ::Ifc4::IfcFlowDirectionEnum(data);
            case 417: return new ::Ifc4::IfcFlowFitting(data);
            case 418: return new ::Ifc4::IfcFlowFittingType(data);
            case 419: return new ::Ifc4::IfcFlowInstrument(data);
            case 420: return new ::Ifc4::IfcFlowInstrumentType(data);
            case 421: return new ::Ifc4::IfcFlowInstrumentTypeEnum(data);
            case 422: return new ::Ifc4::IfcFlowMeter(data);
            case 423: return new ::Ifc4::IfcFlowMeterType(data);
            case 424: return new ::Ifc4::IfcFlowMeterTypeEnum(data);
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
            case 440: return new ::Ifc4::IfcFootingTypeEnum(data);
            case 441: return new ::Ifc4::IfcForceMeasure(data);
            case 442: return new ::Ifc4::IfcFrequencyMeasure(data);
            case 443: return new ::Ifc4::IfcFurnishingElement(data);
            case 444: return new ::Ifc4::IfcFurnishingElementType(data);
            case 445: return new ::Ifc4::IfcFurniture(data);
            case 446: return new ::Ifc4::IfcFurnitureType(data);
            case 447: return new ::Ifc4::IfcFurnitureTypeEnum(data);
            case 448: return new ::Ifc4::IfcGeographicElement(data);
            case 449: return new ::Ifc4::IfcGeographicElementType(data);
            case 450: return new ::Ifc4::IfcGeographicElementTypeEnum(data);
            case 451: return new ::Ifc4::IfcGeometricCurveSet(data);
            case 452: return new ::Ifc4::IfcGeometricProjectionEnum(data);
            case 453: return new ::Ifc4::IfcGeometricRepresentationContext(data);
            case 454: return new ::Ifc4::IfcGeometricRepresentationItem(data);
            case 455: return new ::Ifc4::IfcGeometricRepresentationSubContext(data);
            case 456: return new ::Ifc4::IfcGeometricSet(data);
            case 458: return new ::Ifc4::IfcGloballyUniqueId(data);
            case 459: return new ::Ifc4::IfcGlobalOrLocalEnum(data);
            case 460: return new ::Ifc4::IfcGrid(data);
            case 461: return new ::Ifc4::IfcGridAxis(data);
            case 462: return new ::Ifc4::IfcGridPlacement(data);
            case 464: return new ::Ifc4::IfcGridTypeEnum(data);
            case 465: return new ::Ifc4::IfcGroup(data);
            case 466: return new ::Ifc4::IfcHalfSpaceSolid(data);
            case 468: return new ::Ifc4::IfcHeatExchanger(data);
            case 469: return new ::Ifc4::IfcHeatExchangerType(data);
            case 470: return new ::Ifc4::IfcHeatExchangerTypeEnum(data);
            case 471: return new ::Ifc4::IfcHeatFluxDensityMeasure(data);
            case 472: return new ::Ifc4::IfcHeatingValueMeasure(data);
            case 473: return new ::Ifc4::IfcHumidifier(data);
            case 474: return new ::Ifc4::IfcHumidifierType(data);
            case 475: return new ::Ifc4::IfcHumidifierTypeEnum(data);
            case 476: return new ::Ifc4::IfcIdentifier(data);
            case 477: return new ::Ifc4::IfcIlluminanceMeasure(data);
            case 478: return new ::Ifc4::IfcImageTexture(data);
            case 479: return new ::Ifc4::IfcIndexedColourMap(data);
            case 480: return new ::Ifc4::IfcIndexedPolyCurve(data);
            case 481: return new ::Ifc4::IfcIndexedPolygonalFace(data);
            case 482: return new ::Ifc4::IfcIndexedPolygonalFaceWithVoids(data);
            case 483: return new ::Ifc4::IfcIndexedTextureMap(data);
            case 484: return new ::Ifc4::IfcIndexedTriangleTextureMap(data);
            case 485: return new ::Ifc4::IfcInductanceMeasure(data);
            case 486: return new ::Ifc4::IfcInteger(data);
            case 487: return new ::Ifc4::IfcIntegerCountRateMeasure(data);
            case 488: return new ::Ifc4::IfcInterceptor(data);
            case 489: return new ::Ifc4::IfcInterceptorType(data);
            case 490: return new ::Ifc4::IfcInterceptorTypeEnum(data);
            case 491: return new ::Ifc4::IfcInternalOrExternalEnum(data);
            case 492: return new ::Ifc4::IfcIntersectionCurve(data);
            case 493: return new ::Ifc4::IfcInventory(data);
            case 494: return new ::Ifc4::IfcInventoryTypeEnum(data);
            case 495: return new ::Ifc4::IfcIonConcentrationMeasure(data);
            case 496: return new ::Ifc4::IfcIrregularTimeSeries(data);
            case 497: return new ::Ifc4::IfcIrregularTimeSeriesValue(data);
            case 498: return new ::Ifc4::IfcIShapeProfileDef(data);
            case 499: return new ::Ifc4::IfcIsothermalMoistureCapacityMeasure(data);
            case 500: return new ::Ifc4::IfcJunctionBox(data);
            case 501: return new ::Ifc4::IfcJunctionBoxType(data);
            case 502: return new ::Ifc4::IfcJunctionBoxTypeEnum(data);
            case 503: return new ::Ifc4::IfcKinematicViscosityMeasure(data);
            case 504: return new ::Ifc4::IfcKnotType(data);
            case 505: return new ::Ifc4::IfcLabel(data);
            case 506: return new ::Ifc4::IfcLaborResource(data);
            case 507: return new ::Ifc4::IfcLaborResourceType(data);
            case 508: return new ::Ifc4::IfcLaborResourceTypeEnum(data);
            case 509: return new ::Ifc4::IfcLagTime(data);
            case 510: return new ::Ifc4::IfcLamp(data);
            case 511: return new ::Ifc4::IfcLampType(data);
            case 512: return new ::Ifc4::IfcLampTypeEnum(data);
            case 513: return new ::Ifc4::IfcLanguageId(data);
            case 515: return new ::Ifc4::IfcLayerSetDirectionEnum(data);
            case 516: return new ::Ifc4::IfcLengthMeasure(data);
            case 517: return new ::Ifc4::IfcLibraryInformation(data);
            case 518: return new ::Ifc4::IfcLibraryReference(data);
            case 520: return new ::Ifc4::IfcLightDistributionCurveEnum(data);
            case 521: return new ::Ifc4::IfcLightDistributionData(data);
            case 523: return new ::Ifc4::IfcLightEmissionSourceEnum(data);
            case 524: return new ::Ifc4::IfcLightFixture(data);
            case 525: return new ::Ifc4::IfcLightFixtureType(data);
            case 526: return new ::Ifc4::IfcLightFixtureTypeEnum(data);
            case 527: return new ::Ifc4::IfcLightIntensityDistribution(data);
            case 528: return new ::Ifc4::IfcLightSource(data);
            case 529: return new ::Ifc4::IfcLightSourceAmbient(data);
            case 530: return new ::Ifc4::IfcLightSourceDirectional(data);
            case 531: return new ::Ifc4::IfcLightSourceGoniometric(data);
            case 532: return new ::Ifc4::IfcLightSourcePositional(data);
            case 533: return new ::Ifc4::IfcLightSourceSpot(data);
            case 534: return new ::Ifc4::IfcLine(data);
            case 535: return new ::Ifc4::IfcLinearForceMeasure(data);
            case 536: return new ::Ifc4::IfcLinearMomentMeasure(data);
            case 537: return new ::Ifc4::IfcLinearStiffnessMeasure(data);
            case 538: return new ::Ifc4::IfcLinearVelocityMeasure(data);
            case 539: return new ::Ifc4::IfcLineIndex(data);
            case 540: return new ::Ifc4::IfcLoadGroupTypeEnum(data);
            case 541: return new ::Ifc4::IfcLocalPlacement(data);
            case 542: return new ::Ifc4::IfcLogical(data);
            case 543: return new ::Ifc4::IfcLogicalOperatorEnum(data);
            case 544: return new ::Ifc4::IfcLoop(data);
            case 545: return new ::Ifc4::IfcLShapeProfileDef(data);
            case 546: return new ::Ifc4::IfcLuminousFluxMeasure(data);
            case 547: return new ::Ifc4::IfcLuminousIntensityDistributionMeasure(data);
            case 548: return new ::Ifc4::IfcLuminousIntensityMeasure(data);
            case 549: return new ::Ifc4::IfcMagneticFluxDensityMeasure(data);
            case 550: return new ::Ifc4::IfcMagneticFluxMeasure(data);
            case 551: return new ::Ifc4::IfcManifoldSolidBrep(data);
            case 552: return new ::Ifc4::IfcMapConversion(data);
            case 553: return new ::Ifc4::IfcMappedItem(data);
            case 554: return new ::Ifc4::IfcMassDensityMeasure(data);
            case 555: return new ::Ifc4::IfcMassFlowRateMeasure(data);
            case 556: return new ::Ifc4::IfcMassMeasure(data);
            case 557: return new ::Ifc4::IfcMassPerLengthMeasure(data);
            case 558: return new ::Ifc4::IfcMaterial(data);
            case 559: return new ::Ifc4::IfcMaterialClassificationRelationship(data);
            case 560: return new ::Ifc4::IfcMaterialConstituent(data);
            case 561: return new ::Ifc4::IfcMaterialConstituentSet(data);
            case 562: return new ::Ifc4::IfcMaterialDefinition(data);
            case 563: return new ::Ifc4::IfcMaterialDefinitionRepresentation(data);
            case 564: return new ::Ifc4::IfcMaterialLayer(data);
            case 565: return new ::Ifc4::IfcMaterialLayerSet(data);
            case 566: return new ::Ifc4::IfcMaterialLayerSetUsage(data);
            case 567: return new ::Ifc4::IfcMaterialLayerWithOffsets(data);
            case 568: return new ::Ifc4::IfcMaterialList(data);
            case 569: return new ::Ifc4::IfcMaterialProfile(data);
            case 570: return new ::Ifc4::IfcMaterialProfileSet(data);
            case 571: return new ::Ifc4::IfcMaterialProfileSetUsage(data);
            case 572: return new ::Ifc4::IfcMaterialProfileSetUsageTapering(data);
            case 573: return new ::Ifc4::IfcMaterialProfileWithOffsets(data);
            case 574: return new ::Ifc4::IfcMaterialProperties(data);
            case 575: return new ::Ifc4::IfcMaterialRelationship(data);
            case 577: return new ::Ifc4::IfcMaterialUsageDefinition(data);
            case 579: return new ::Ifc4::IfcMeasureWithUnit(data);
            case 580: return new ::Ifc4::IfcMechanicalFastener(data);
            case 581: return new ::Ifc4::IfcMechanicalFastenerType(data);
            case 582: return new ::Ifc4::IfcMechanicalFastenerTypeEnum(data);
            case 583: return new ::Ifc4::IfcMedicalDevice(data);
            case 584: return new ::Ifc4::IfcMedicalDeviceType(data);
            case 585: return new ::Ifc4::IfcMedicalDeviceTypeEnum(data);
            case 586: return new ::Ifc4::IfcMember(data);
            case 587: return new ::Ifc4::IfcMemberStandardCase(data);
            case 588: return new ::Ifc4::IfcMemberType(data);
            case 589: return new ::Ifc4::IfcMemberTypeEnum(data);
            case 590: return new ::Ifc4::IfcMetric(data);
            case 592: return new ::Ifc4::IfcMirroredProfileDef(data);
            case 593: return new ::Ifc4::IfcModulusOfElasticityMeasure(data);
            case 594: return new ::Ifc4::IfcModulusOfLinearSubgradeReactionMeasure(data);
            case 595: return new ::Ifc4::IfcModulusOfRotationalSubgradeReactionMeasure(data);
            case 597: return new ::Ifc4::IfcModulusOfSubgradeReactionMeasure(data);
            case 600: return new ::Ifc4::IfcMoistureDiffusivityMeasure(data);
            case 601: return new ::Ifc4::IfcMolecularWeightMeasure(data);
            case 602: return new ::Ifc4::IfcMomentOfInertiaMeasure(data);
            case 603: return new ::Ifc4::IfcMonetaryMeasure(data);
            case 604: return new ::Ifc4::IfcMonetaryUnit(data);
            case 605: return new ::Ifc4::IfcMonthInYearNumber(data);
            case 606: return new ::Ifc4::IfcMotorConnection(data);
            case 607: return new ::Ifc4::IfcMotorConnectionType(data);
            case 608: return new ::Ifc4::IfcMotorConnectionTypeEnum(data);
            case 609: return new ::Ifc4::IfcNamedUnit(data);
            case 610: return new ::Ifc4::IfcNonNegativeLengthMeasure(data);
            case 611: return new ::Ifc4::IfcNormalisedRatioMeasure(data);
            case 612: return new ::Ifc4::IfcNullStyle(data);
            case 613: return new ::Ifc4::IfcNumericMeasure(data);
            case 614: return new ::Ifc4::IfcObject(data);
            case 615: return new ::Ifc4::IfcObjectDefinition(data);
            case 616: return new ::Ifc4::IfcObjective(data);
            case 617: return new ::Ifc4::IfcObjectiveEnum(data);
            case 618: return new ::Ifc4::IfcObjectPlacement(data);
            case 620: return new ::Ifc4::IfcObjectTypeEnum(data);
            case 621: return new ::Ifc4::IfcOccupant(data);
            case 622: return new ::Ifc4::IfcOccupantTypeEnum(data);
            case 623: return new ::Ifc4::IfcOffsetCurve2D(data);
            case 624: return new ::Ifc4::IfcOffsetCurve3D(data);
            case 625: return new ::Ifc4::IfcOpeningElement(data);
            case 626: return new ::Ifc4::IfcOpeningElementTypeEnum(data);
            case 627: return new ::Ifc4::IfcOpeningStandardCase(data);
            case 628: return new ::Ifc4::IfcOpenShell(data);
            case 629: return new ::Ifc4::IfcOrganization(data);
            case 630: return new ::Ifc4::IfcOrganizationRelationship(data);
            case 631: return new ::Ifc4::IfcOrientedEdge(data);
            case 632: return new ::Ifc4::IfcOuterBoundaryCurve(data);
            case 633: return new ::Ifc4::IfcOutlet(data);
            case 634: return new ::Ifc4::IfcOutletType(data);
            case 635: return new ::Ifc4::IfcOutletTypeEnum(data);
            case 636: return new ::Ifc4::IfcOwnerHistory(data);
            case 637: return new ::Ifc4::IfcParameterizedProfileDef(data);
            case 638: return new ::Ifc4::IfcParameterValue(data);
            case 639: return new ::Ifc4::IfcPath(data);
            case 640: return new ::Ifc4::IfcPcurve(data);
            case 641: return new ::Ifc4::IfcPerformanceHistory(data);
            case 642: return new ::Ifc4::IfcPerformanceHistoryTypeEnum(data);
            case 643: return new ::Ifc4::IfcPermeableCoveringOperationEnum(data);
            case 644: return new ::Ifc4::IfcPermeableCoveringProperties(data);
            case 645: return new ::Ifc4::IfcPermit(data);
            case 646: return new ::Ifc4::IfcPermitTypeEnum(data);
            case 647: return new ::Ifc4::IfcPerson(data);
            case 648: return new ::Ifc4::IfcPersonAndOrganization(data);
            case 649: return new ::Ifc4::IfcPHMeasure(data);
            case 650: return new ::Ifc4::IfcPhysicalComplexQuantity(data);
            case 651: return new ::Ifc4::IfcPhysicalOrVirtualEnum(data);
            case 652: return new ::Ifc4::IfcPhysicalQuantity(data);
            case 653: return new ::Ifc4::IfcPhysicalSimpleQuantity(data);
            case 654: return new ::Ifc4::IfcPile(data);
            case 655: return new ::Ifc4::IfcPileConstructionEnum(data);
            case 656: return new ::Ifc4::IfcPileType(data);
            case 657: return new ::Ifc4::IfcPileTypeEnum(data);
            case 658: return new ::Ifc4::IfcPipeFitting(data);
            case 659: return new ::Ifc4::IfcPipeFittingType(data);
            case 660: return new ::Ifc4::IfcPipeFittingTypeEnum(data);
            case 661: return new ::Ifc4::IfcPipeSegment(data);
            case 662: return new ::Ifc4::IfcPipeSegmentType(data);
            case 663: return new ::Ifc4::IfcPipeSegmentTypeEnum(data);
            case 664: return new ::Ifc4::IfcPixelTexture(data);
            case 665: return new ::Ifc4::IfcPlacement(data);
            case 666: return new ::Ifc4::IfcPlanarBox(data);
            case 667: return new ::Ifc4::IfcPlanarExtent(data);
            case 668: return new ::Ifc4::IfcPlanarForceMeasure(data);
            case 669: return new ::Ifc4::IfcPlane(data);
            case 670: return new ::Ifc4::IfcPlaneAngleMeasure(data);
            case 671: return new ::Ifc4::IfcPlate(data);
            case 672: return new ::Ifc4::IfcPlateStandardCase(data);
            case 673: return new ::Ifc4::IfcPlateType(data);
            case 674: return new ::Ifc4::IfcPlateTypeEnum(data);
            case 675: return new ::Ifc4::IfcPoint(data);
            case 676: return new ::Ifc4::IfcPointOnCurve(data);
            case 677: return new ::Ifc4::IfcPointOnSurface(data);
            case 679: return new ::Ifc4::IfcPolygonalBoundedHalfSpace(data);
            case 680: return new ::Ifc4::IfcPolygonalFaceSet(data);
            case 681: return new ::Ifc4::IfcPolyline(data);
            case 682: return new ::Ifc4::IfcPolyLoop(data);
            case 683: return new ::Ifc4::IfcPort(data);
            case 684: return new ::Ifc4::IfcPositiveInteger(data);
            case 685: return new ::Ifc4::IfcPositiveLengthMeasure(data);
            case 686: return new ::Ifc4::IfcPositivePlaneAngleMeasure(data);
            case 687: return new ::Ifc4::IfcPositiveRatioMeasure(data);
            case 688: return new ::Ifc4::IfcPostalAddress(data);
            case 689: return new ::Ifc4::IfcPowerMeasure(data);
            case 690: return new ::Ifc4::IfcPreDefinedColour(data);
            case 691: return new ::Ifc4::IfcPreDefinedCurveFont(data);
            case 692: return new ::Ifc4::IfcPreDefinedItem(data);
            case 693: return new ::Ifc4::IfcPreDefinedProperties(data);
            case 694: return new ::Ifc4::IfcPreDefinedPropertySet(data);
            case 695: return new ::Ifc4::IfcPreDefinedTextFont(data);
            case 696: return new ::Ifc4::IfcPreferredSurfaceCurveRepresentation(data);
            case 697: return new ::Ifc4::IfcPresentableText(data);
            case 698: return new ::Ifc4::IfcPresentationItem(data);
            case 699: return new ::Ifc4::IfcPresentationLayerAssignment(data);
            case 700: return new ::Ifc4::IfcPresentationLayerWithStyle(data);
            case 701: return new ::Ifc4::IfcPresentationStyle(data);
            case 702: return new ::Ifc4::IfcPresentationStyleAssignment(data);
            case 704: return new ::Ifc4::IfcPressureMeasure(data);
            case 705: return new ::Ifc4::IfcProcedure(data);
            case 706: return new ::Ifc4::IfcProcedureType(data);
            case 707: return new ::Ifc4::IfcProcedureTypeEnum(data);
            case 708: return new ::Ifc4::IfcProcess(data);
            case 710: return new ::Ifc4::IfcProduct(data);
            case 711: return new ::Ifc4::IfcProductDefinitionShape(data);
            case 712: return new ::Ifc4::IfcProductRepresentation(data);
            case 715: return new ::Ifc4::IfcProfileDef(data);
            case 716: return new ::Ifc4::IfcProfileProperties(data);
            case 717: return new ::Ifc4::IfcProfileTypeEnum(data);
            case 718: return new ::Ifc4::IfcProject(data);
            case 719: return new ::Ifc4::IfcProjectedCRS(data);
            case 720: return new ::Ifc4::IfcProjectedOrTrueLengthEnum(data);
            case 721: return new ::Ifc4::IfcProjectionElement(data);
            case 722: return new ::Ifc4::IfcProjectionElementTypeEnum(data);
            case 723: return new ::Ifc4::IfcProjectLibrary(data);
            case 724: return new ::Ifc4::IfcProjectOrder(data);
            case 725: return new ::Ifc4::IfcProjectOrderTypeEnum(data);
            case 726: return new ::Ifc4::IfcProperty(data);
            case 727: return new ::Ifc4::IfcPropertyAbstraction(data);
            case 728: return new ::Ifc4::IfcPropertyBoundedValue(data);
            case 729: return new ::Ifc4::IfcPropertyDefinition(data);
            case 730: return new ::Ifc4::IfcPropertyDependencyRelationship(data);
            case 731: return new ::Ifc4::IfcPropertyEnumeratedValue(data);
            case 732: return new ::Ifc4::IfcPropertyEnumeration(data);
            case 733: return new ::Ifc4::IfcPropertyListValue(data);
            case 734: return new ::Ifc4::IfcPropertyReferenceValue(data);
            case 735: return new ::Ifc4::IfcPropertySet(data);
            case 736: return new ::Ifc4::IfcPropertySetDefinition(data);
            case 738: return new ::Ifc4::IfcPropertySetDefinitionSet(data);
            case 739: return new ::Ifc4::IfcPropertySetTemplate(data);
            case 740: return new ::Ifc4::IfcPropertySetTemplateTypeEnum(data);
            case 741: return new ::Ifc4::IfcPropertySingleValue(data);
            case 742: return new ::Ifc4::IfcPropertyTableValue(data);
            case 743: return new ::Ifc4::IfcPropertyTemplate(data);
            case 744: return new ::Ifc4::IfcPropertyTemplateDefinition(data);
            case 745: return new ::Ifc4::IfcProtectiveDevice(data);
            case 746: return new ::Ifc4::IfcProtectiveDeviceTrippingUnit(data);
            case 747: return new ::Ifc4::IfcProtectiveDeviceTrippingUnitType(data);
            case 748: return new ::Ifc4::IfcProtectiveDeviceTrippingUnitTypeEnum(data);
            case 749: return new ::Ifc4::IfcProtectiveDeviceType(data);
            case 750: return new ::Ifc4::IfcProtectiveDeviceTypeEnum(data);
            case 751: return new ::Ifc4::IfcProxy(data);
            case 752: return new ::Ifc4::IfcPump(data);
            case 753: return new ::Ifc4::IfcPumpType(data);
            case 754: return new ::Ifc4::IfcPumpTypeEnum(data);
            case 755: return new ::Ifc4::IfcQuantityArea(data);
            case 756: return new ::Ifc4::IfcQuantityCount(data);
            case 757: return new ::Ifc4::IfcQuantityLength(data);
            case 758: return new ::Ifc4::IfcQuantitySet(data);
            case 759: return new ::Ifc4::IfcQuantityTime(data);
            case 760: return new ::Ifc4::IfcQuantityVolume(data);
            case 761: return new ::Ifc4::IfcQuantityWeight(data);
            case 762: return new ::Ifc4::IfcRadioActivityMeasure(data);
            case 763: return new ::Ifc4::IfcRailing(data);
            case 764: return new ::Ifc4::IfcRailingType(data);
            case 765: return new ::Ifc4::IfcRailingTypeEnum(data);
            case 766: return new ::Ifc4::IfcRamp(data);
            case 767: return new ::Ifc4::IfcRampFlight(data);
            case 768: return new ::Ifc4::IfcRampFlightType(data);
            case 769: return new ::Ifc4::IfcRampFlightTypeEnum(data);
            case 770: return new ::Ifc4::IfcRampType(data);
            case 771: return new ::Ifc4::IfcRampTypeEnum(data);
            case 772: return new ::Ifc4::IfcRatioMeasure(data);
            case 773: return new ::Ifc4::IfcRationalBSplineCurveWithKnots(data);
            case 774: return new ::Ifc4::IfcRationalBSplineSurfaceWithKnots(data);
            case 775: return new ::Ifc4::IfcReal(data);
            case 776: return new ::Ifc4::IfcRectangleHollowProfileDef(data);
            case 777: return new ::Ifc4::IfcRectangleProfileDef(data);
            case 778: return new ::Ifc4::IfcRectangularPyramid(data);
            case 779: return new ::Ifc4::IfcRectangularTrimmedSurface(data);
            case 780: return new ::Ifc4::IfcRecurrencePattern(data);
            case 781: return new ::Ifc4::IfcRecurrenceTypeEnum(data);
            case 782: return new ::Ifc4::IfcReference(data);
            case 783: return new ::Ifc4::IfcReflectanceMethodEnum(data);
            case 784: return new ::Ifc4::IfcRegularTimeSeries(data);
            case 785: return new ::Ifc4::IfcReinforcementBarProperties(data);
            case 786: return new ::Ifc4::IfcReinforcementDefinitionProperties(data);
            case 787: return new ::Ifc4::IfcReinforcingBar(data);
            case 788: return new ::Ifc4::IfcReinforcingBarRoleEnum(data);
            case 789: return new ::Ifc4::IfcReinforcingBarSurfaceEnum(data);
            case 790: return new ::Ifc4::IfcReinforcingBarType(data);
            case 791: return new ::Ifc4::IfcReinforcingBarTypeEnum(data);
            case 792: return new ::Ifc4::IfcReinforcingElement(data);
            case 793: return new ::Ifc4::IfcReinforcingElementType(data);
            case 794: return new ::Ifc4::IfcReinforcingMesh(data);
            case 795: return new ::Ifc4::IfcReinforcingMeshType(data);
            case 796: return new ::Ifc4::IfcReinforcingMeshTypeEnum(data);
            case 797: return new ::Ifc4::IfcRelAggregates(data);
            case 798: return new ::Ifc4::IfcRelAssigns(data);
            case 799: return new ::Ifc4::IfcRelAssignsToActor(data);
            case 800: return new ::Ifc4::IfcRelAssignsToControl(data);
            case 801: return new ::Ifc4::IfcRelAssignsToGroup(data);
            case 802: return new ::Ifc4::IfcRelAssignsToGroupByFactor(data);
            case 803: return new ::Ifc4::IfcRelAssignsToProcess(data);
            case 804: return new ::Ifc4::IfcRelAssignsToProduct(data);
            case 805: return new ::Ifc4::IfcRelAssignsToResource(data);
            case 806: return new ::Ifc4::IfcRelAssociates(data);
            case 807: return new ::Ifc4::IfcRelAssociatesApproval(data);
            case 808: return new ::Ifc4::IfcRelAssociatesClassification(data);
            case 809: return new ::Ifc4::IfcRelAssociatesConstraint(data);
            case 810: return new ::Ifc4::IfcRelAssociatesDocument(data);
            case 811: return new ::Ifc4::IfcRelAssociatesLibrary(data);
            case 812: return new ::Ifc4::IfcRelAssociatesMaterial(data);
            case 813: return new ::Ifc4::IfcRelationship(data);
            case 814: return new ::Ifc4::IfcRelConnects(data);
            case 815: return new ::Ifc4::IfcRelConnectsElements(data);
            case 816: return new ::Ifc4::IfcRelConnectsPathElements(data);
            case 817: return new ::Ifc4::IfcRelConnectsPorts(data);
            case 818: return new ::Ifc4::IfcRelConnectsPortToElement(data);
            case 819: return new ::Ifc4::IfcRelConnectsStructuralActivity(data);
            case 820: return new ::Ifc4::IfcRelConnectsStructuralMember(data);
            case 821: return new ::Ifc4::IfcRelConnectsWithEccentricity(data);
            case 822: return new ::Ifc4::IfcRelConnectsWithRealizingElements(data);
            case 823: return new ::Ifc4::IfcRelContainedInSpatialStructure(data);
            case 824: return new ::Ifc4::IfcRelCoversBldgElements(data);
            case 825: return new ::Ifc4::IfcRelCoversSpaces(data);
            case 826: return new ::Ifc4::IfcRelDeclares(data);
            case 827: return new ::Ifc4::IfcRelDecomposes(data);
            case 828: return new ::Ifc4::IfcRelDefines(data);
            case 829: return new ::Ifc4::IfcRelDefinesByObject(data);
            case 830: return new ::Ifc4::IfcRelDefinesByProperties(data);
            case 831: return new ::Ifc4::IfcRelDefinesByTemplate(data);
            case 832: return new ::Ifc4::IfcRelDefinesByType(data);
            case 833: return new ::Ifc4::IfcRelFillsElement(data);
            case 834: return new ::Ifc4::IfcRelFlowControlElements(data);
            case 835: return new ::Ifc4::IfcRelInterferesElements(data);
            case 836: return new ::Ifc4::IfcRelNests(data);
            case 837: return new ::Ifc4::IfcRelProjectsElement(data);
            case 838: return new ::Ifc4::IfcRelReferencedInSpatialStructure(data);
            case 839: return new ::Ifc4::IfcRelSequence(data);
            case 840: return new ::Ifc4::IfcRelServicesBuildings(data);
            case 841: return new ::Ifc4::IfcRelSpaceBoundary(data);
            case 842: return new ::Ifc4::IfcRelSpaceBoundary1stLevel(data);
            case 843: return new ::Ifc4::IfcRelSpaceBoundary2ndLevel(data);
            case 844: return new ::Ifc4::IfcRelVoidsElement(data);
            case 845: return new ::Ifc4::IfcReparametrisedCompositeCurveSegment(data);
            case 846: return new ::Ifc4::IfcRepresentation(data);
            case 847: return new ::Ifc4::IfcRepresentationContext(data);
            case 848: return new ::Ifc4::IfcRepresentationItem(data);
            case 849: return new ::Ifc4::IfcRepresentationMap(data);
            case 850: return new ::Ifc4::IfcResource(data);
            case 851: return new ::Ifc4::IfcResourceApprovalRelationship(data);
            case 852: return new ::Ifc4::IfcResourceConstraintRelationship(data);
            case 853: return new ::Ifc4::IfcResourceLevelRelationship(data);
            case 856: return new ::Ifc4::IfcResourceTime(data);
            case 857: return new ::Ifc4::IfcRevolvedAreaSolid(data);
            case 858: return new ::Ifc4::IfcRevolvedAreaSolidTapered(data);
            case 859: return new ::Ifc4::IfcRightCircularCone(data);
            case 860: return new ::Ifc4::IfcRightCircularCylinder(data);
            case 861: return new ::Ifc4::IfcRoleEnum(data);
            case 862: return new ::Ifc4::IfcRoof(data);
            case 863: return new ::Ifc4::IfcRoofType(data);
            case 864: return new ::Ifc4::IfcRoofTypeEnum(data);
            case 865: return new ::Ifc4::IfcRoot(data);
            case 866: return new ::Ifc4::IfcRotationalFrequencyMeasure(data);
            case 867: return new ::Ifc4::IfcRotationalMassMeasure(data);
            case 868: return new ::Ifc4::IfcRotationalStiffnessMeasure(data);
            case 870: return new ::Ifc4::IfcRoundedRectangleProfileDef(data);
            case 871: return new ::Ifc4::IfcSanitaryTerminal(data);
            case 872: return new ::Ifc4::IfcSanitaryTerminalType(data);
            case 873: return new ::Ifc4::IfcSanitaryTerminalTypeEnum(data);
            case 874: return new ::Ifc4::IfcSchedulingTime(data);
            case 875: return new ::Ifc4::IfcSeamCurve(data);
            case 876: return new ::Ifc4::IfcSectionalAreaIntegralMeasure(data);
            case 877: return new ::Ifc4::IfcSectionedSpine(data);
            case 878: return new ::Ifc4::IfcSectionModulusMeasure(data);
            case 879: return new ::Ifc4::IfcSectionProperties(data);
            case 880: return new ::Ifc4::IfcSectionReinforcementProperties(data);
            case 881: return new ::Ifc4::IfcSectionTypeEnum(data);
            case 883: return new ::Ifc4::IfcSensor(data);
            case 884: return new ::Ifc4::IfcSensorType(data);
            case 885: return new ::Ifc4::IfcSensorTypeEnum(data);
            case 886: return new ::Ifc4::IfcSequenceEnum(data);
            case 887: return new ::Ifc4::IfcShadingDevice(data);
            case 888: return new ::Ifc4::IfcShadingDeviceType(data);
            case 889: return new ::Ifc4::IfcShadingDeviceTypeEnum(data);
            case 890: return new ::Ifc4::IfcShapeAspect(data);
            case 891: return new ::Ifc4::IfcShapeModel(data);
            case 892: return new ::Ifc4::IfcShapeRepresentation(data);
            case 893: return new ::Ifc4::IfcShearModulusMeasure(data);
            case 895: return new ::Ifc4::IfcShellBasedSurfaceModel(data);
            case 896: return new ::Ifc4::IfcSimpleProperty(data);
            case 897: return new ::Ifc4::IfcSimplePropertyTemplate(data);
            case 898: return new ::Ifc4::IfcSimplePropertyTemplateTypeEnum(data);
            case 900: return new ::Ifc4::IfcSIPrefix(data);
            case 901: return new ::Ifc4::IfcSite(data);
            case 902: return new ::Ifc4::IfcSIUnit(data);
            case 903: return new ::Ifc4::IfcSIUnitName(data);
            case 905: return new ::Ifc4::IfcSlab(data);
            case 906: return new ::Ifc4::IfcSlabElementedCase(data);
            case 907: return new ::Ifc4::IfcSlabStandardCase(data);
            case 908: return new ::Ifc4::IfcSlabType(data);
            case 909: return new ::Ifc4::IfcSlabTypeEnum(data);
            case 910: return new ::Ifc4::IfcSlippageConnectionCondition(data);
            case 911: return new ::Ifc4::IfcSolarDevice(data);
            case 912: return new ::Ifc4::IfcSolarDeviceType(data);
            case 913: return new ::Ifc4::IfcSolarDeviceTypeEnum(data);
            case 914: return new ::Ifc4::IfcSolidAngleMeasure(data);
            case 915: return new ::Ifc4::IfcSolidModel(data);
            case 917: return new ::Ifc4::IfcSoundPowerLevelMeasure(data);
            case 918: return new ::Ifc4::IfcSoundPowerMeasure(data);
            case 919: return new ::Ifc4::IfcSoundPressureLevelMeasure(data);
            case 920: return new ::Ifc4::IfcSoundPressureMeasure(data);
            case 921: return new ::Ifc4::IfcSpace(data);
            case 923: return new ::Ifc4::IfcSpaceHeater(data);
            case 924: return new ::Ifc4::IfcSpaceHeaterType(data);
            case 925: return new ::Ifc4::IfcSpaceHeaterTypeEnum(data);
            case 926: return new ::Ifc4::IfcSpaceType(data);
            case 927: return new ::Ifc4::IfcSpaceTypeEnum(data);
            case 928: return new ::Ifc4::IfcSpatialElement(data);
            case 929: return new ::Ifc4::IfcSpatialElementType(data);
            case 930: return new ::Ifc4::IfcSpatialStructureElement(data);
            case 931: return new ::Ifc4::IfcSpatialStructureElementType(data);
            case 932: return new ::Ifc4::IfcSpatialZone(data);
            case 933: return new ::Ifc4::IfcSpatialZoneType(data);
            case 934: return new ::Ifc4::IfcSpatialZoneTypeEnum(data);
            case 935: return new ::Ifc4::IfcSpecificHeatCapacityMeasure(data);
            case 936: return new ::Ifc4::IfcSpecularExponent(data);
            case 938: return new ::Ifc4::IfcSpecularRoughness(data);
            case 939: return new ::Ifc4::IfcSphere(data);
            case 940: return new ::Ifc4::IfcSphericalSurface(data);
            case 941: return new ::Ifc4::IfcStackTerminal(data);
            case 942: return new ::Ifc4::IfcStackTerminalType(data);
            case 943: return new ::Ifc4::IfcStackTerminalTypeEnum(data);
            case 944: return new ::Ifc4::IfcStair(data);
            case 945: return new ::Ifc4::IfcStairFlight(data);
            case 946: return new ::Ifc4::IfcStairFlightType(data);
            case 947: return new ::Ifc4::IfcStairFlightTypeEnum(data);
            case 948: return new ::Ifc4::IfcStairType(data);
            case 949: return new ::Ifc4::IfcStairTypeEnum(data);
            case 950: return new ::Ifc4::IfcStateEnum(data);
            case 951: return new ::Ifc4::IfcStructuralAction(data);
            case 952: return new ::Ifc4::IfcStructuralActivity(data);
            case 954: return new ::Ifc4::IfcStructuralAnalysisModel(data);
            case 955: return new ::Ifc4::IfcStructuralConnection(data);
            case 956: return new ::Ifc4::IfcStructuralConnectionCondition(data);
            case 957: return new ::Ifc4::IfcStructuralCurveAction(data);
            case 958: return new ::Ifc4::IfcStructuralCurveActivityTypeEnum(data);
            case 959: return new ::Ifc4::IfcStructuralCurveConnection(data);
            case 960: return new ::Ifc4::IfcStructuralCurveMember(data);
            case 961: return new ::Ifc4::IfcStructuralCurveMemberTypeEnum(data);
            case 962: return new ::Ifc4::IfcStructuralCurveMemberVarying(data);
            case 963: return new ::Ifc4::IfcStructuralCurveReaction(data);
            case 964: return new ::Ifc4::IfcStructuralItem(data);
            case 965: return new ::Ifc4::IfcStructuralLinearAction(data);
            case 966: return new ::Ifc4::IfcStructuralLoad(data);
            case 967: return new ::Ifc4::IfcStructuralLoadCase(data);
            case 968: return new ::Ifc4::IfcStructuralLoadConfiguration(data);
            case 969: return new ::Ifc4::IfcStructuralLoadGroup(data);
            case 970: return new ::Ifc4::IfcStructuralLoadLinearForce(data);
            case 971: return new ::Ifc4::IfcStructuralLoadOrResult(data);
            case 972: return new ::Ifc4::IfcStructuralLoadPlanarForce(data);
            case 973: return new ::Ifc4::IfcStructuralLoadSingleDisplacement(data);
            case 974: return new ::Ifc4::IfcStructuralLoadSingleDisplacementDistortion(data);
            case 975: return new ::Ifc4::IfcStructuralLoadSingleForce(data);
            case 976: return new ::Ifc4::IfcStructuralLoadSingleForceWarping(data);
            case 977: return new ::Ifc4::IfcStructuralLoadStatic(data);
            case 978: return new ::Ifc4::IfcStructuralLoadTemperature(data);
            case 979: return new ::Ifc4::IfcStructuralMember(data);
            case 980: return new ::Ifc4::IfcStructuralPlanarAction(data);
            case 981: return new ::Ifc4::IfcStructuralPointAction(data);
            case 982: return new ::Ifc4::IfcStructuralPointConnection(data);
            case 983: return new ::Ifc4::IfcStructuralPointReaction(data);
            case 984: return new ::Ifc4::IfcStructuralReaction(data);
            case 985: return new ::Ifc4::IfcStructuralResultGroup(data);
            case 986: return new ::Ifc4::IfcStructuralSurfaceAction(data);
            case 987: return new ::Ifc4::IfcStructuralSurfaceActivityTypeEnum(data);
            case 988: return new ::Ifc4::IfcStructuralSurfaceConnection(data);
            case 989: return new ::Ifc4::IfcStructuralSurfaceMember(data);
            case 990: return new ::Ifc4::IfcStructuralSurfaceMemberTypeEnum(data);
            case 991: return new ::Ifc4::IfcStructuralSurfaceMemberVarying(data);
            case 992: return new ::Ifc4::IfcStructuralSurfaceReaction(data);
            case 994: return new ::Ifc4::IfcStyledItem(data);
            case 995: return new ::Ifc4::IfcStyledRepresentation(data);
            case 996: return new ::Ifc4::IfcStyleModel(data);
            case 997: return new ::Ifc4::IfcSubContractResource(data);
            case 998: return new ::Ifc4::IfcSubContractResourceType(data);
            case 999: return new ::Ifc4::IfcSubContractResourceTypeEnum(data);
            case 1000: return new ::Ifc4::IfcSubedge(data);
            case 1001: return new ::Ifc4::IfcSurface(data);
            case 1002: return new ::Ifc4::IfcSurfaceCurve(data);
            case 1003: return new ::Ifc4::IfcSurfaceCurveSweptAreaSolid(data);
            case 1004: return new ::Ifc4::IfcSurfaceFeature(data);
            case 1005: return new ::Ifc4::IfcSurfaceFeatureTypeEnum(data);
            case 1006: return new ::Ifc4::IfcSurfaceOfLinearExtrusion(data);
            case 1007: return new ::Ifc4::IfcSurfaceOfRevolution(data);
            case 1009: return new ::Ifc4::IfcSurfaceReinforcementArea(data);
            case 1010: return new ::Ifc4::IfcSurfaceSide(data);
            case 1011: return new ::Ifc4::IfcSurfaceStyle(data);
            case 1013: return new ::Ifc4::IfcSurfaceStyleLighting(data);
            case 1014: return new ::Ifc4::IfcSurfaceStyleRefraction(data);
            case 1015: return new ::Ifc4::IfcSurfaceStyleRendering(data);
            case 1016: return new ::Ifc4::IfcSurfaceStyleShading(data);
            case 1017: return new ::Ifc4::IfcSurfaceStyleWithTextures(data);
            case 1018: return new ::Ifc4::IfcSurfaceTexture(data);
            case 1019: return new ::Ifc4::IfcSweptAreaSolid(data);
            case 1020: return new ::Ifc4::IfcSweptDiskSolid(data);
            case 1021: return new ::Ifc4::IfcSweptDiskSolidPolygonal(data);
            case 1022: return new ::Ifc4::IfcSweptSurface(data);
            case 1023: return new ::Ifc4::IfcSwitchingDevice(data);
            case 1024: return new ::Ifc4::IfcSwitchingDeviceType(data);
            case 1025: return new ::Ifc4::IfcSwitchingDeviceTypeEnum(data);
            case 1026: return new ::Ifc4::IfcSystem(data);
            case 1027: return new ::Ifc4::IfcSystemFurnitureElement(data);
            case 1028: return new ::Ifc4::IfcSystemFurnitureElementType(data);
            case 1029: return new ::Ifc4::IfcSystemFurnitureElementTypeEnum(data);
            case 1030: return new ::Ifc4::IfcTable(data);
            case 1031: return new ::Ifc4::IfcTableColumn(data);
            case 1032: return new ::Ifc4::IfcTableRow(data);
            case 1033: return new ::Ifc4::IfcTank(data);
            case 1034: return new ::Ifc4::IfcTankType(data);
            case 1035: return new ::Ifc4::IfcTankTypeEnum(data);
            case 1036: return new ::Ifc4::IfcTask(data);
            case 1037: return new ::Ifc4::IfcTaskDurationEnum(data);
            case 1038: return new ::Ifc4::IfcTaskTime(data);
            case 1039: return new ::Ifc4::IfcTaskTimeRecurring(data);
            case 1040: return new ::Ifc4::IfcTaskType(data);
            case 1041: return new ::Ifc4::IfcTaskTypeEnum(data);
            case 1042: return new ::Ifc4::IfcTelecomAddress(data);
            case 1043: return new ::Ifc4::IfcTemperatureGradientMeasure(data);
            case 1044: return new ::Ifc4::IfcTemperatureRateOfChangeMeasure(data);
            case 1045: return new ::Ifc4::IfcTendon(data);
            case 1046: return new ::Ifc4::IfcTendonAnchor(data);
            case 1047: return new ::Ifc4::IfcTendonAnchorType(data);
            case 1048: return new ::Ifc4::IfcTendonAnchorTypeEnum(data);
            case 1049: return new ::Ifc4::IfcTendonType(data);
            case 1050: return new ::Ifc4::IfcTendonTypeEnum(data);
            case 1051: return new ::Ifc4::IfcTessellatedFaceSet(data);
            case 1052: return new ::Ifc4::IfcTessellatedItem(data);
            case 1053: return new ::Ifc4::IfcText(data);
            case 1054: return new ::Ifc4::IfcTextAlignment(data);
            case 1055: return new ::Ifc4::IfcTextDecoration(data);
            case 1056: return new ::Ifc4::IfcTextFontName(data);
            case 1058: return new ::Ifc4::IfcTextLiteral(data);
            case 1059: return new ::Ifc4::IfcTextLiteralWithExtent(data);
            case 1060: return new ::Ifc4::IfcTextPath(data);
            case 1061: return new ::Ifc4::IfcTextStyle(data);
            case 1062: return new ::Ifc4::IfcTextStyleFontModel(data);
            case 1063: return new ::Ifc4::IfcTextStyleForDefinedFont(data);
            case 1064: return new ::Ifc4::IfcTextStyleTextModel(data);
            case 1065: return new ::Ifc4::IfcTextTransformation(data);
            case 1066: return new ::Ifc4::IfcTextureCoordinate(data);
            case 1067: return new ::Ifc4::IfcTextureCoordinateGenerator(data);
            case 1068: return new ::Ifc4::IfcTextureMap(data);
            case 1069: return new ::Ifc4::IfcTextureVertex(data);
            case 1070: return new ::Ifc4::IfcTextureVertexList(data);
            case 1071: return new ::Ifc4::IfcThermalAdmittanceMeasure(data);
            case 1072: return new ::Ifc4::IfcThermalConductivityMeasure(data);
            case 1073: return new ::Ifc4::IfcThermalExpansionCoefficientMeasure(data);
            case 1074: return new ::Ifc4::IfcThermalResistanceMeasure(data);
            case 1075: return new ::Ifc4::IfcThermalTransmittanceMeasure(data);
            case 1076: return new ::Ifc4::IfcThermodynamicTemperatureMeasure(data);
            case 1077: return new ::Ifc4::IfcTime(data);
            case 1078: return new ::Ifc4::IfcTimeMeasure(data);
            case 1080: return new ::Ifc4::IfcTimePeriod(data);
            case 1081: return new ::Ifc4::IfcTimeSeries(data);
            case 1082: return new ::Ifc4::IfcTimeSeriesDataTypeEnum(data);
            case 1083: return new ::Ifc4::IfcTimeSeriesValue(data);
            case 1084: return new ::Ifc4::IfcTimeStamp(data);
            case 1085: return new ::Ifc4::IfcTopologicalRepresentationItem(data);
            case 1086: return new ::Ifc4::IfcTopologyRepresentation(data);
            case 1087: return new ::Ifc4::IfcToroidalSurface(data);
            case 1088: return new ::Ifc4::IfcTorqueMeasure(data);
            case 1089: return new ::Ifc4::IfcTransformer(data);
            case 1090: return new ::Ifc4::IfcTransformerType(data);
            case 1091: return new ::Ifc4::IfcTransformerTypeEnum(data);
            case 1092: return new ::Ifc4::IfcTransitionCode(data);
            case 1094: return new ::Ifc4::IfcTransportElement(data);
            case 1095: return new ::Ifc4::IfcTransportElementType(data);
            case 1096: return new ::Ifc4::IfcTransportElementTypeEnum(data);
            case 1097: return new ::Ifc4::IfcTrapeziumProfileDef(data);
            case 1098: return new ::Ifc4::IfcTriangulatedFaceSet(data);
            case 1099: return new ::Ifc4::IfcTrimmedCurve(data);
            case 1100: return new ::Ifc4::IfcTrimmingPreference(data);
            case 1102: return new ::Ifc4::IfcTShapeProfileDef(data);
            case 1103: return new ::Ifc4::IfcTubeBundle(data);
            case 1104: return new ::Ifc4::IfcTubeBundleType(data);
            case 1105: return new ::Ifc4::IfcTubeBundleTypeEnum(data);
            case 1106: return new ::Ifc4::IfcTypeObject(data);
            case 1107: return new ::Ifc4::IfcTypeProcess(data);
            case 1108: return new ::Ifc4::IfcTypeProduct(data);
            case 1109: return new ::Ifc4::IfcTypeResource(data);
            case 1111: return new ::Ifc4::IfcUnitaryControlElement(data);
            case 1112: return new ::Ifc4::IfcUnitaryControlElementType(data);
            case 1113: return new ::Ifc4::IfcUnitaryControlElementTypeEnum(data);
            case 1114: return new ::Ifc4::IfcUnitaryEquipment(data);
            case 1115: return new ::Ifc4::IfcUnitaryEquipmentType(data);
            case 1116: return new ::Ifc4::IfcUnitaryEquipmentTypeEnum(data);
            case 1117: return new ::Ifc4::IfcUnitAssignment(data);
            case 1118: return new ::Ifc4::IfcUnitEnum(data);
            case 1119: return new ::Ifc4::IfcURIReference(data);
            case 1120: return new ::Ifc4::IfcUShapeProfileDef(data);
            case 1122: return new ::Ifc4::IfcValve(data);
            case 1123: return new ::Ifc4::IfcValveType(data);
            case 1124: return new ::Ifc4::IfcValveTypeEnum(data);
            case 1125: return new ::Ifc4::IfcVaporPermeabilityMeasure(data);
            case 1126: return new ::Ifc4::IfcVector(data);
            case 1128: return new ::Ifc4::IfcVertex(data);
            case 1129: return new ::Ifc4::IfcVertexLoop(data);
            case 1130: return new ::Ifc4::IfcVertexPoint(data);
            case 1131: return new ::Ifc4::IfcVibrationIsolator(data);
            case 1132: return new ::Ifc4::IfcVibrationIsolatorType(data);
            case 1133: return new ::Ifc4::IfcVibrationIsolatorTypeEnum(data);
            case 1134: return new ::Ifc4::IfcVirtualElement(data);
            case 1135: return new ::Ifc4::IfcVirtualGridIntersection(data);
            case 1136: return new ::Ifc4::IfcVoidingFeature(data);
            case 1137: return new ::Ifc4::IfcVoidingFeatureTypeEnum(data);
            case 1138: return new ::Ifc4::IfcVolumeMeasure(data);
            case 1139: return new ::Ifc4::IfcVolumetricFlowRateMeasure(data);
            case 1140: return new ::Ifc4::IfcWall(data);
            case 1141: return new ::Ifc4::IfcWallElementedCase(data);
            case 1142: return new ::Ifc4::IfcWallStandardCase(data);
            case 1143: return new ::Ifc4::IfcWallType(data);
            case 1144: return new ::Ifc4::IfcWallTypeEnum(data);
            case 1145: return new ::Ifc4::IfcWarpingConstantMeasure(data);
            case 1146: return new ::Ifc4::IfcWarpingMomentMeasure(data);
            case 1148: return new ::Ifc4::IfcWasteTerminal(data);
            case 1149: return new ::Ifc4::IfcWasteTerminalType(data);
            case 1150: return new ::Ifc4::IfcWasteTerminalTypeEnum(data);
            case 1151: return new ::Ifc4::IfcWindow(data);
            case 1152: return new ::Ifc4::IfcWindowLiningProperties(data);
            case 1153: return new ::Ifc4::IfcWindowPanelOperationEnum(data);
            case 1154: return new ::Ifc4::IfcWindowPanelPositionEnum(data);
            case 1155: return new ::Ifc4::IfcWindowPanelProperties(data);
            case 1156: return new ::Ifc4::IfcWindowStandardCase(data);
            case 1157: return new ::Ifc4::IfcWindowStyle(data);
            case 1158: return new ::Ifc4::IfcWindowStyleConstructionEnum(data);
            case 1159: return new ::Ifc4::IfcWindowStyleOperationEnum(data);
            case 1160: return new ::Ifc4::IfcWindowType(data);
            case 1161: return new ::Ifc4::IfcWindowTypeEnum(data);
            case 1162: return new ::Ifc4::IfcWindowTypePartitioningEnum(data);
            case 1163: return new ::Ifc4::IfcWorkCalendar(data);
            case 1164: return new ::Ifc4::IfcWorkCalendarTypeEnum(data);
            case 1165: return new ::Ifc4::IfcWorkControl(data);
            case 1166: return new ::Ifc4::IfcWorkPlan(data);
            case 1167: return new ::Ifc4::IfcWorkPlanTypeEnum(data);
            case 1168: return new ::Ifc4::IfcWorkSchedule(data);
            case 1169: return new ::Ifc4::IfcWorkScheduleTypeEnum(data);
            case 1170: return new ::Ifc4::IfcWorkTime(data);
            case 1171: return new ::Ifc4::IfcZone(data);
            case 1172: return new ::Ifc4::IfcZShapeProfileDef(data);
            default: throw IfcParse::IfcException(data->type()->name() + " cannot be instantiated");
        }

    }
};

using namespace std::string_literals;
static std::string strings[] = {"IfcAbsorbedDoseMeasure"s,
"IfcAccelerationMeasure"s,
"IfcActionRequestTypeEnum"s,
"EMAIL"s,
"FAX"s,
"PHONE"s,
"POST"s,
"VERBAL"s,
"USERDEFINED"s,
"NOTDEFINED"s,
"IfcActionSourceTypeEnum"s,
"DEAD_LOAD_G"s,
"COMPLETION_G1"s,
"LIVE_LOAD_Q"s,
"SNOW_S"s,
"WIND_W"s,
"PRESTRESSING_P"s,
"SETTLEMENT_U"s,
"TEMPERATURE_T"s,
"EARTHQUAKE_E"s,
"FIRE"s,
"IMPULSE"s,
"IMPACT"s,
"TRANSPORT"s,
"ERECTION"s,
"PROPPING"s,
"SYSTEM_IMPERFECTION"s,
"SHRINKAGE"s,
"CREEP"s,
"LACK_OF_FIT"s,
"BUOYANCY"s,
"ICE"s,
"CURRENT"s,
"WAVE"s,
"RAIN"s,
"BRAKES"s,
"IfcActionTypeEnum"s,
"PERMANENT_G"s,
"VARIABLE_Q"s,
"EXTRAORDINARY_A"s,
"IfcActuatorTypeEnum"s,
"ELECTRICACTUATOR"s,
"HANDOPERATEDACTUATOR"s,
"HYDRAULICACTUATOR"s,
"PNEUMATICACTUATOR"s,
"THERMOSTATICACTUATOR"s,
"IfcAddressTypeEnum"s,
"OFFICE"s,
"SITE"s,
"HOME"s,
"DISTRIBUTIONPOINT"s,
"IfcAirTerminalBoxTypeEnum"s,
"CONSTANTFLOW"s,
"VARIABLEFLOWPRESSUREDEPENDANT"s,
"VARIABLEFLOWPRESSUREINDEPENDANT"s,
"IfcAirTerminalTypeEnum"s,
"DIFFUSER"s,
"GRILLE"s,
"LOUVRE"s,
"REGISTER"s,
"IfcAirToAirHeatRecoveryTypeEnum"s,
"FIXEDPLATECOUNTERFLOWEXCHANGER"s,
"FIXEDPLATECROSSFLOWEXCHANGER"s,
"FIXEDPLATEPARALLELFLOWEXCHANGER"s,
"ROTARYWHEEL"s,
"RUNAROUNDCOILLOOP"s,
"HEATPIPE"s,
"TWINTOWERENTHALPYRECOVERYLOOPS"s,
"THERMOSIPHONSEALEDTUBEHEATEXCHANGERS"s,
"THERMOSIPHONCOILTYPEHEATEXCHANGERS"s,
"IfcAlarmTypeEnum"s,
"BELL"s,
"BREAKGLASSBUTTON"s,
"LIGHT"s,
"MANUALPULLBOX"s,
"SIREN"s,
"WHISTLE"s,
"IfcAmountOfSubstanceMeasure"s,
"IfcAnalysisModelTypeEnum"s,
"IN_PLANE_LOADING_2D"s,
"OUT_PLANE_LOADING_2D"s,
"LOADING_3D"s,
"IfcAnalysisTheoryTypeEnum"s,
"FIRST_ORDER_THEORY"s,
"SECOND_ORDER_THEORY"s,
"THIRD_ORDER_THEORY"s,
"FULL_NONLINEAR_THEORY"s,
"IfcAngularVelocityMeasure"s,
"IfcAreaDensityMeasure"s,
"IfcAreaMeasure"s,
"IfcArithmeticOperatorEnum"s,
"ADD"s,
"DIVIDE"s,
"MULTIPLY"s,
"SUBTRACT"s,
"IfcAssemblyPlaceEnum"s,
"FACTORY"s,
"IfcAudioVisualApplianceTypeEnum"s,
"AMPLIFIER"s,
"CAMERA"s,
"DISPLAY"s,
"MICROPHONE"s,
"PLAYER"s,
"PROJECTOR"s,
"RECEIVER"s,
"SPEAKER"s,
"SWITCHER"s,
"TELEPHONE"s,
"TUNER"s,
"IfcBSplineCurveForm"s,
"POLYLINE_FORM"s,
"CIRCULAR_ARC"s,
"ELLIPTIC_ARC"s,
"PARABOLIC_ARC"s,
"HYPERBOLIC_ARC"s,
"UNSPECIFIED"s,
"IfcBSplineSurfaceForm"s,
"PLANE_SURF"s,
"CYLINDRICAL_SURF"s,
"CONICAL_SURF"s,
"SPHERICAL_SURF"s,
"TOROIDAL_SURF"s,
"SURF_OF_REVOLUTION"s,
"RULED_SURF"s,
"GENERALISED_CONE"s,
"QUADRIC_SURF"s,
"SURF_OF_LINEAR_EXTRUSION"s,
"IfcBeamTypeEnum"s,
"BEAM"s,
"JOIST"s,
"HOLLOWCORE"s,
"LINTEL"s,
"SPANDREL"s,
"T_BEAM"s,
"IfcBenchmarkEnum"s,
"GREATERTHAN"s,
"GREATERTHANOREQUALTO"s,
"LESSTHAN"s,
"LESSTHANOREQUALTO"s,
"EQUALTO"s,
"NOTEQUALTO"s,
"INCLUDES"s,
"NOTINCLUDES"s,
"INCLUDEDIN"s,
"NOTINCLUDEDIN"s,
"IfcBinary"s,
"IfcBoilerTypeEnum"s,
"WATER"s,
"STEAM"s,
"IfcBoolean"s,
"IfcBooleanOperator"s,
"UNION"s,
"INTERSECTION"s,
"DIFFERENCE"s,
"IfcBuildingElementPartTypeEnum"s,
"INSULATION"s,
"PRECASTPANEL"s,
"IfcBuildingElementProxyTypeEnum"s,
"COMPLEX"s,
"ELEMENT"s,
"PARTIAL"s,
"PROVISIONFORVOID"s,
"PROVISIONFORSPACE"s,
"IfcBuildingSystemTypeEnum"s,
"FENESTRATION"s,
"FOUNDATION"s,
"LOADBEARING"s,
"OUTERSHELL"s,
"SHADING"s,
"IfcBurnerTypeEnum"s,
"IfcCableCarrierFittingTypeEnum"s,
"BEND"s,
"CROSS"s,
"REDUCER"s,
"TEE"s,
"IfcCableCarrierSegmentTypeEnum"s,
"CABLELADDERSEGMENT"s,
"CABLETRAYSEGMENT"s,
"CABLETRUNKINGSEGMENT"s,
"CONDUITSEGMENT"s,
"IfcCableFittingTypeEnum"s,
"CONNECTOR"s,
"ENTRY"s,
"EXIT"s,
"JUNCTION"s,
"TRANSITION"s,
"IfcCableSegmentTypeEnum"s,
"BUSBARSEGMENT"s,
"CABLESEGMENT"s,
"CONDUCTORSEGMENT"s,
"CORESEGMENT"s,
"IfcCardinalPointReference"s,
"IfcChangeActionEnum"s,
"NOCHANGE"s,
"MODIFIED"s,
"ADDED"s,
"DELETED"s,
"IfcChillerTypeEnum"s,
"AIRCOOLED"s,
"WATERCOOLED"s,
"HEATRECOVERY"s,
"IfcChimneyTypeEnum"s,
"IfcCoilTypeEnum"s,
"DXCOOLINGCOIL"s,
"ELECTRICHEATINGCOIL"s,
"GASHEATINGCOIL"s,
"HYDRONICCOIL"s,
"STEAMHEATINGCOIL"s,
"WATERCOOLINGCOIL"s,
"WATERHEATINGCOIL"s,
"IfcColumnTypeEnum"s,
"COLUMN"s,
"PILASTER"s,
"IfcCommunicationsApplianceTypeEnum"s,
"ANTENNA"s,
"COMPUTER"s,
"GATEWAY"s,
"MODEM"s,
"NETWORKAPPLIANCE"s,
"NETWORKBRIDGE"s,
"NETWORKHUB"s,
"PRINTER"s,
"REPEATER"s,
"ROUTER"s,
"SCANNER"s,
"IfcComplexNumber"s,
"IfcComplexPropertyTemplateTypeEnum"s,
"P_COMPLEX"s,
"Q_COMPLEX"s,
"IfcCompoundPlaneAngleMeasure"s,
"IfcCompressorTypeEnum"s,
"DYNAMIC"s,
"RECIPROCATING"s,
"ROTARY"s,
"SCROLL"s,
"TROCHOIDAL"s,
"SINGLESTAGE"s,
"BOOSTER"s,
"OPENTYPE"s,
"HERMETIC"s,
"SEMIHERMETIC"s,
"WELDEDSHELLHERMETIC"s,
"ROLLINGPISTON"s,
"ROTARYVANE"s,
"SINGLESCREW"s,
"TWINSCREW"s,
"IfcCondenserTypeEnum"s,
"EVAPORATIVECOOLED"s,
"WATERCOOLEDBRAZEDPLATE"s,
"WATERCOOLEDSHELLCOIL"s,
"WATERCOOLEDSHELLTUBE"s,
"WATERCOOLEDTUBEINTUBE"s,
"IfcConnectionTypeEnum"s,
"ATPATH"s,
"ATSTART"s,
"ATEND"s,
"IfcConstraintEnum"s,
"HARD"s,
"SOFT"s,
"ADVISORY"s,
"IfcConstructionEquipmentResourceTypeEnum"s,
"DEMOLISHING"s,
"EARTHMOVING"s,
"ERECTING"s,
"HEATING"s,
"LIGHTING"s,
"PAVING"s,
"PUMPING"s,
"TRANSPORTING"s,
"IfcConstructionMaterialResourceTypeEnum"s,
"AGGREGATES"s,
"CONCRETE"s,
"DRYWALL"s,
"FUEL"s,
"GYPSUM"s,
"MASONRY"s,
"METAL"s,
"PLASTIC"s,
"WOOD"s,
"IfcConstructionProductResourceTypeEnum"s,
"ASSEMBLY"s,
"FORMWORK"s,
"IfcContextDependentMeasure"s,
"IfcControllerTypeEnum"s,
"FLOATING"s,
"PROGRAMMABLE"s,
"PROPORTIONAL"s,
"MULTIPOSITION"s,
"TWOPOSITION"s,
"IfcCooledBeamTypeEnum"s,
"ACTIVE"s,
"PASSIVE"s,
"IfcCoolingTowerTypeEnum"s,
"NATURALDRAFT"s,
"MECHANICALINDUCEDDRAFT"s,
"MECHANICALFORCEDDRAFT"s,
"IfcCostItemTypeEnum"s,
"IfcCostScheduleTypeEnum"s,
"BUDGET"s,
"COSTPLAN"s,
"ESTIMATE"s,
"TENDER"s,
"PRICEDBILLOFQUANTITIES"s,
"UNPRICEDBILLOFQUANTITIES"s,
"SCHEDULEOFRATES"s,
"IfcCountMeasure"s,
"IfcCoveringTypeEnum"s,
"CEILING"s,
"FLOORING"s,
"CLADDING"s,
"ROOFING"s,
"MOLDING"s,
"SKIRTINGBOARD"s,
"MEMBRANE"s,
"SLEEVING"s,
"WRAPPING"s,
"IfcCrewResourceTypeEnum"s,
"IfcCurtainWallTypeEnum"s,
"IfcCurvatureMeasure"s,
"IfcCurveInterpolationEnum"s,
"LINEAR"s,
"LOG_LINEAR"s,
"LOG_LOG"s,
"IfcDamperTypeEnum"s,
"BACKDRAFTDAMPER"s,
"BALANCINGDAMPER"s,
"BLASTDAMPER"s,
"CONTROLDAMPER"s,
"FIREDAMPER"s,
"FIRESMOKEDAMPER"s,
"FUMEHOODEXHAUST"s,
"GRAVITYDAMPER"s,
"GRAVITYRELIEFDAMPER"s,
"RELIEFDAMPER"s,
"SMOKEDAMPER"s,
"IfcDataOriginEnum"s,
"MEASURED"s,
"PREDICTED"s,
"SIMULATED"s,
"IfcDate"s,
"IfcDateTime"s,
"IfcDayInMonthNumber"s,
"IfcDayInWeekNumber"s,
"IfcDerivedUnitEnum"s,
"ANGULARVELOCITYUNIT"s,
"AREADENSITYUNIT"s,
"COMPOUNDPLANEANGLEUNIT"s,
"DYNAMICVISCOSITYUNIT"s,
"HEATFLUXDENSITYUNIT"s,
"INTEGERCOUNTRATEUNIT"s,
"ISOTHERMALMOISTURECAPACITYUNIT"s,
"KINEMATICVISCOSITYUNIT"s,
"LINEARVELOCITYUNIT"s,
"MASSDENSITYUNIT"s,
"MASSFLOWRATEUNIT"s,
"MOISTUREDIFFUSIVITYUNIT"s,
"MOLECULARWEIGHTUNIT"s,
"SPECIFICHEATCAPACITYUNIT"s,
"THERMALADMITTANCEUNIT"s,
"THERMALCONDUCTANCEUNIT"s,
"THERMALRESISTANCEUNIT"s,
"THERMALTRANSMITTANCEUNIT"s,
"VAPORPERMEABILITYUNIT"s,
"VOLUMETRICFLOWRATEUNIT"s,
"ROTATIONALFREQUENCYUNIT"s,
"TORQUEUNIT"s,
"MOMENTOFINERTIAUNIT"s,
"LINEARMOMENTUNIT"s,
"LINEARFORCEUNIT"s,
"PLANARFORCEUNIT"s,
"MODULUSOFELASTICITYUNIT"s,
"SHEARMODULUSUNIT"s,
"LINEARSTIFFNESSUNIT"s,
"ROTATIONALSTIFFNESSUNIT"s,
"MODULUSOFSUBGRADEREACTIONUNIT"s,
"ACCELERATIONUNIT"s,
"CURVATUREUNIT"s,
"HEATINGVALUEUNIT"s,
"IONCONCENTRATIONUNIT"s,
"LUMINOUSINTENSITYDISTRIBUTIONUNIT"s,
"MASSPERLENGTHUNIT"s,
"MODULUSOFLINEARSUBGRADEREACTIONUNIT"s,
"MODULUSOFROTATIONALSUBGRADEREACTIONUNIT"s,
"PHUNIT"s,
"ROTATIONALMASSUNIT"s,
"SECTIONAREAINTEGRALUNIT"s,
"SECTIONMODULUSUNIT"s,
"SOUNDPOWERLEVELUNIT"s,
"SOUNDPOWERUNIT"s,
"SOUNDPRESSURELEVELUNIT"s,
"SOUNDPRESSUREUNIT"s,
"TEMPERATUREGRADIENTUNIT"s,
"TEMPERATURERATEOFCHANGEUNIT"s,
"THERMALEXPANSIONCOEFFICIENTUNIT"s,
"WARPINGCONSTANTUNIT"s,
"WARPINGMOMENTUNIT"s,
"IfcDescriptiveMeasure"s,
"IfcDimensionCount"s,
"IfcDirectionSenseEnum"s,
"POSITIVE"s,
"NEGATIVE"s,
"IfcDiscreteAccessoryTypeEnum"s,
"ANCHORPLATE"s,
"BRACKET"s,
"SHOE"s,
"IfcDistributionChamberElementTypeEnum"s,
"FORMEDDUCT"s,
"INSPECTIONCHAMBER"s,
"INSPECTIONPIT"s,
"MANHOLE"s,
"METERCHAMBER"s,
"SUMP"s,
"TRENCH"s,
"VALVECHAMBER"s,
"IfcDistributionPortTypeEnum"s,
"CABLE"s,
"CABLECARRIER"s,
"DUCT"s,
"PIPE"s,
"IfcDistributionSystemEnum"s,
"AIRCONDITIONING"s,
"AUDIOVISUAL"s,
"CHEMICAL"s,
"CHILLEDWATER"s,
"COMMUNICATION"s,
"COMPRESSEDAIR"s,
"CONDENSERWATER"s,
"CONTROL"s,
"CONVEYING"s,
"DATA"s,
"DISPOSAL"s,
"DOMESTICCOLDWATER"s,
"DOMESTICHOTWATER"s,
"DRAINAGE"s,
"EARTHING"s,
"ELECTRICAL"s,
"ELECTROACOUSTIC"s,
"EXHAUST"s,
"FIREPROTECTION"s,
"GAS"s,
"HAZARDOUS"s,
"LIGHTNINGPROTECTION"s,
"MUNICIPALSOLIDWASTE"s,
"OIL"s,
"OPERATIONAL"s,
"POWERGENERATION"s,
"RAINWATER"s,
"REFRIGERATION"s,
"SECURITY"s,
"SEWAGE"s,
"SIGNAL"s,
"STORMWATER"s,
"TV"s,
"VACUUM"s,
"VENT"s,
"VENTILATION"s,
"WASTEWATER"s,
"WATERSUPPLY"s,
"IfcDocumentConfidentialityEnum"s,
"PUBLIC"s,
"RESTRICTED"s,
"CONFIDENTIAL"s,
"PERSONAL"s,
"IfcDocumentStatusEnum"s,
"DRAFT"s,
"FINALDRAFT"s,
"FINAL"s,
"REVISION"s,
"IfcDoorPanelOperationEnum"s,
"SWINGING"s,
"DOUBLE_ACTING"s,
"SLIDING"s,
"FOLDING"s,
"REVOLVING"s,
"ROLLINGUP"s,
"FIXEDPANEL"s,
"IfcDoorPanelPositionEnum"s,
"LEFT"s,
"MIDDLE"s,
"RIGHT"s,
"IfcDoorStyleConstructionEnum"s,
"ALUMINIUM"s,
"HIGH_GRADE_STEEL"s,
"STEEL"s,
"ALUMINIUM_WOOD"s,
"ALUMINIUM_PLASTIC"s,
"IfcDoorStyleOperationEnum"s,
"SINGLE_SWING_LEFT"s,
"SINGLE_SWING_RIGHT"s,
"DOUBLE_DOOR_SINGLE_SWING"s,
"DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT"s,
"DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT"s,
"DOUBLE_SWING_LEFT"s,
"DOUBLE_SWING_RIGHT"s,
"DOUBLE_DOOR_DOUBLE_SWING"s,
"SLIDING_TO_LEFT"s,
"SLIDING_TO_RIGHT"s,
"DOUBLE_DOOR_SLIDING"s,
"FOLDING_TO_LEFT"s,
"FOLDING_TO_RIGHT"s,
"DOUBLE_DOOR_FOLDING"s,
"IfcDoorTypeEnum"s,
"DOOR"s,
"GATE"s,
"TRAPDOOR"s,
"IfcDoorTypeOperationEnum"s,
"SWING_FIXED_LEFT"s,
"SWING_FIXED_RIGHT"s,
"IfcDoseEquivalentMeasure"s,
"IfcDuctFittingTypeEnum"s,
"OBSTRUCTION"s,
"IfcDuctSegmentTypeEnum"s,
"RIGIDSEGMENT"s,
"FLEXIBLESEGMENT"s,
"IfcDuctSilencerTypeEnum"s,
"FLATOVAL"s,
"RECTANGULAR"s,
"ROUND"s,
"IfcDuration"s,
"IfcDynamicViscosityMeasure"s,
"IfcElectricApplianceTypeEnum"s,
"DISHWASHER"s,
"ELECTRICCOOKER"s,
"FREESTANDINGELECTRICHEATER"s,
"FREESTANDINGFAN"s,
"FREESTANDINGWATERHEATER"s,
"FREESTANDINGWATERCOOLER"s,
"FREEZER"s,
"FRIDGE_FREEZER"s,
"HANDDRYER"s,
"KITCHENMACHINE"s,
"MICROWAVE"s,
"PHOTOCOPIER"s,
"REFRIGERATOR"s,
"TUMBLEDRYER"s,
"VENDINGMACHINE"s,
"WASHINGMACHINE"s,
"IfcElectricCapacitanceMeasure"s,
"IfcElectricChargeMeasure"s,
"IfcElectricConductanceMeasure"s,
"IfcElectricCurrentMeasure"s,
"IfcElectricDistributionBoardTypeEnum"s,
"CONSUMERUNIT"s,
"DISTRIBUTIONBOARD"s,
"MOTORCONTROLCENTRE"s,
"SWITCHBOARD"s,
"IfcElectricFlowStorageDeviceTypeEnum"s,
"BATTERY"s,
"CAPACITORBANK"s,
"HARMONICFILTER"s,
"INDUCTORBANK"s,
"UPS"s,
"IfcElectricGeneratorTypeEnum"s,
"CHP"s,
"ENGINEGENERATOR"s,
"STANDALONE"s,
"IfcElectricMotorTypeEnum"s,
"DC"s,
"INDUCTION"s,
"POLYPHASE"s,
"RELUCTANCESYNCHRONOUS"s,
"SYNCHRONOUS"s,
"IfcElectricResistanceMeasure"s,
"IfcElectricTimeControlTypeEnum"s,
"TIMECLOCK"s,
"TIMEDELAY"s,
"RELAY"s,
"IfcElectricVoltageMeasure"s,
"IfcElementAssemblyTypeEnum"s,
"ACCESSORY_ASSEMBLY"s,
"ARCH"s,
"BEAM_GRID"s,
"BRACED_FRAME"s,
"GIRDER"s,
"REINFORCEMENT_UNIT"s,
"RIGID_FRAME"s,
"SLAB_FIELD"s,
"TRUSS"s,
"IfcElementCompositionEnum"s,
"IfcEnergyMeasure"s,
"IfcEngineTypeEnum"s,
"EXTERNALCOMBUSTION"s,
"INTERNALCOMBUSTION"s,
"IfcEvaporativeCoolerTypeEnum"s,
"DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER"s,
"DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER"s,
"DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER"s,
"DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER"s,
"DIRECTEVAPORATIVEAIRWASHER"s,
"INDIRECTEVAPORATIVEPACKAGEAIRCOOLER"s,
"INDIRECTEVAPORATIVEWETCOIL"s,
"INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER"s,
"INDIRECTDIRECTCOMBINATION"s,
"IfcEvaporatorTypeEnum"s,
"DIRECTEXPANSION"s,
"DIRECTEXPANSIONSHELLANDTUBE"s,
"DIRECTEXPANSIONTUBEINTUBE"s,
"DIRECTEXPANSIONBRAZEDPLATE"s,
"FLOODEDSHELLANDTUBE"s,
"SHELLANDCOIL"s,
"IfcEventTriggerTypeEnum"s,
"EVENTRULE"s,
"EVENTMESSAGE"s,
"EVENTTIME"s,
"EVENTCOMPLEX"s,
"IfcEventTypeEnum"s,
"STARTEVENT"s,
"ENDEVENT"s,
"INTERMEDIATEEVENT"s,
"IfcExternalSpatialElementTypeEnum"s,
"EXTERNAL"s,
"EXTERNAL_EARTH"s,
"EXTERNAL_WATER"s,
"EXTERNAL_FIRE"s,
"IfcFanTypeEnum"s,
"CENTRIFUGALFORWARDCURVED"s,
"CENTRIFUGALRADIAL"s,
"CENTRIFUGALBACKWARDINCLINEDCURVED"s,
"CENTRIFUGALAIRFOIL"s,
"TUBEAXIAL"s,
"VANEAXIAL"s,
"PROPELLORAXIAL"s,
"IfcFastenerTypeEnum"s,
"GLUE"s,
"MORTAR"s,
"WELD"s,
"IfcFilterTypeEnum"s,
"AIRPARTICLEFILTER"s,
"COMPRESSEDAIRFILTER"s,
"ODORFILTER"s,
"OILFILTER"s,
"STRAINER"s,
"WATERFILTER"s,
"IfcFireSuppressionTerminalTypeEnum"s,
"BREECHINGINLET"s,
"FIREHYDRANT"s,
"HOSEREEL"s,
"SPRINKLER"s,
"SPRINKLERDEFLECTOR"s,
"IfcFlowDirectionEnum"s,
"SOURCE"s,
"SINK"s,
"SOURCEANDSINK"s,
"IfcFlowInstrumentTypeEnum"s,
"PRESSUREGAUGE"s,
"THERMOMETER"s,
"AMMETER"s,
"FREQUENCYMETER"s,
"POWERFACTORMETER"s,
"PHASEANGLEMETER"s,
"VOLTMETER_PEAK"s,
"VOLTMETER_RMS"s,
"IfcFlowMeterTypeEnum"s,
"ENERGYMETER"s,
"GASMETER"s,
"OILMETER"s,
"WATERMETER"s,
"IfcFontStyle"s,
"IfcFontVariant"s,
"IfcFontWeight"s,
"IfcFootingTypeEnum"s,
"CAISSON_FOUNDATION"s,
"FOOTING_BEAM"s,
"PAD_FOOTING"s,
"PILE_CAP"s,
"STRIP_FOOTING"s,
"IfcForceMeasure"s,
"IfcFrequencyMeasure"s,
"IfcFurnitureTypeEnum"s,
"CHAIR"s,
"TABLE"s,
"DESK"s,
"BED"s,
"FILECABINET"s,
"SHELF"s,
"SOFA"s,
"IfcGeographicElementTypeEnum"s,
"TERRAIN"s,
"IfcGeometricProjectionEnum"s,
"GRAPH_VIEW"s,
"SKETCH_VIEW"s,
"MODEL_VIEW"s,
"PLAN_VIEW"s,
"REFLECTED_PLAN_VIEW"s,
"SECTION_VIEW"s,
"ELEVATION_VIEW"s,
"IfcGlobalOrLocalEnum"s,
"GLOBAL_COORDS"s,
"LOCAL_COORDS"s,
"IfcGloballyUniqueId"s,
"IfcGridTypeEnum"s,
"RADIAL"s,
"TRIANGULAR"s,
"IRREGULAR"s,
"IfcHeatExchangerTypeEnum"s,
"PLATE"s,
"SHELLANDTUBE"s,
"IfcHeatFluxDensityMeasure"s,
"IfcHeatingValueMeasure"s,
"IfcHumidifierTypeEnum"s,
"STEAMINJECTION"s,
"ADIABATICAIRWASHER"s,
"ADIABATICPAN"s,
"ADIABATICWETTEDELEMENT"s,
"ADIABATICATOMIZING"s,
"ADIABATICULTRASONIC"s,
"ADIABATICRIGIDMEDIA"s,
"ADIABATICCOMPRESSEDAIRNOZZLE"s,
"ASSISTEDELECTRIC"s,
"ASSISTEDNATURALGAS"s,
"ASSISTEDPROPANE"s,
"ASSISTEDBUTANE"s,
"ASSISTEDSTEAM"s,
"IfcIdentifier"s,
"IfcIlluminanceMeasure"s,
"IfcInductanceMeasure"s,
"IfcInteger"s,
"IfcIntegerCountRateMeasure"s,
"IfcInterceptorTypeEnum"s,
"CYCLONIC"s,
"GREASE"s,
"PETROL"s,
"IfcInternalOrExternalEnum"s,
"INTERNAL"s,
"IfcInventoryTypeEnum"s,
"ASSETINVENTORY"s,
"SPACEINVENTORY"s,
"FURNITUREINVENTORY"s,
"IfcIonConcentrationMeasure"s,
"IfcIsothermalMoistureCapacityMeasure"s,
"IfcJunctionBoxTypeEnum"s,
"POWER"s,
"IfcKinematicViscosityMeasure"s,
"IfcKnotType"s,
"UNIFORM_KNOTS"s,
"QUASI_UNIFORM_KNOTS"s,
"PIECEWISE_BEZIER_KNOTS"s,
"IfcLabel"s,
"IfcLaborResourceTypeEnum"s,
"ADMINISTRATION"s,
"CARPENTRY"s,
"CLEANING"s,
"ELECTRIC"s,
"FINISHING"s,
"GENERAL"s,
"HVAC"s,
"LANDSCAPING"s,
"PAINTING"s,
"PLUMBING"s,
"SITEGRADING"s,
"STEELWORK"s,
"SURVEYING"s,
"IfcLampTypeEnum"s,
"COMPACTFLUORESCENT"s,
"FLUORESCENT"s,
"HALOGEN"s,
"HIGHPRESSUREMERCURY"s,
"HIGHPRESSURESODIUM"s,
"LED"s,
"METALHALIDE"s,
"OLED"s,
"TUNGSTENFILAMENT"s,
"IfcLanguageId"s,
"IfcLayerSetDirectionEnum"s,
"AXIS1"s,
"AXIS2"s,
"AXIS3"s,
"IfcLengthMeasure"s,
"IfcLightDistributionCurveEnum"s,
"TYPE_A"s,
"TYPE_B"s,
"TYPE_C"s,
"IfcLightEmissionSourceEnum"s,
"LIGHTEMITTINGDIODE"s,
"LOWPRESSURESODIUM"s,
"LOWVOLTAGEHALOGEN"s,
"MAINVOLTAGEHALOGEN"s,
"IfcLightFixtureTypeEnum"s,
"POINTSOURCE"s,
"DIRECTIONSOURCE"s,
"SECURITYLIGHTING"s,
"IfcLinearForceMeasure"s,
"IfcLinearMomentMeasure"s,
"IfcLinearStiffnessMeasure"s,
"IfcLinearVelocityMeasure"s,
"IfcLoadGroupTypeEnum"s,
"LOAD_GROUP"s,
"LOAD_CASE"s,
"LOAD_COMBINATION"s,
"IfcLogical"s,
"IfcLogicalOperatorEnum"s,
"LOGICALAND"s,
"LOGICALOR"s,
"LOGICALXOR"s,
"LOGICALNOTAND"s,
"LOGICALNOTOR"s,
"IfcLuminousFluxMeasure"s,
"IfcLuminousIntensityDistributionMeasure"s,
"IfcLuminousIntensityMeasure"s,
"IfcMagneticFluxDensityMeasure"s,
"IfcMagneticFluxMeasure"s,
"IfcMassDensityMeasure"s,
"IfcMassFlowRateMeasure"s,
"IfcMassMeasure"s,
"IfcMassPerLengthMeasure"s,
"IfcMechanicalFastenerTypeEnum"s,
"ANCHORBOLT"s,
"BOLT"s,
"DOWEL"s,
"NAIL"s,
"NAILPLATE"s,
"RIVET"s,
"SCREW"s,
"SHEARCONNECTOR"s,
"STAPLE"s,
"STUDSHEARCONNECTOR"s,
"IfcMedicalDeviceTypeEnum"s,
"AIRSTATION"s,
"FEEDAIRUNIT"s,
"OXYGENGENERATOR"s,
"OXYGENPLANT"s,
"VACUUMSTATION"s,
"IfcMemberTypeEnum"s,
"BRACE"s,
"CHORD"s,
"COLLAR"s,
"MEMBER"s,
"MULLION"s,
"PURLIN"s,
"RAFTER"s,
"STRINGER"s,
"STRUT"s,
"STUD"s,
"IfcModulusOfElasticityMeasure"s,
"IfcModulusOfLinearSubgradeReactionMeasure"s,
"IfcModulusOfRotationalSubgradeReactionMeasure"s,
"IfcModulusOfRotationalSubgradeReactionSelect"s,
"IfcModulusOfSubgradeReactionMeasure"s,
"IfcModulusOfSubgradeReactionSelect"s,
"IfcModulusOfTranslationalSubgradeReactionSelect"s,
"IfcMoistureDiffusivityMeasure"s,
"IfcMolecularWeightMeasure"s,
"IfcMomentOfInertiaMeasure"s,
"IfcMonetaryMeasure"s,
"IfcMonthInYearNumber"s,
"IfcMotorConnectionTypeEnum"s,
"BELTDRIVE"s,
"COUPLING"s,
"DIRECTDRIVE"s,
"IfcNonNegativeLengthMeasure"s,
"IfcNullStyle"s,
"NULL"s,
"IfcNumericMeasure"s,
"IfcObjectTypeEnum"s,
"PRODUCT"s,
"PROCESS"s,
"RESOURCE"s,
"ACTOR"s,
"GROUP"s,
"PROJECT"s,
"IfcObjectiveEnum"s,
"CODECOMPLIANCE"s,
"CODEWAIVER"s,
"DESIGNINTENT"s,
"HEALTHANDSAFETY"s,
"MERGECONFLICT"s,
"MODELVIEW"s,
"PARAMETER"s,
"REQUIREMENT"s,
"SPECIFICATION"s,
"TRIGGERCONDITION"s,
"IfcOccupantTypeEnum"s,
"ASSIGNEE"s,
"ASSIGNOR"s,
"LESSEE"s,
"LESSOR"s,
"LETTINGAGENT"s,
"OWNER"s,
"TENANT"s,
"IfcOpeningElementTypeEnum"s,
"OPENING"s,
"RECESS"s,
"IfcOutletTypeEnum"s,
"AUDIOVISUALOUTLET"s,
"COMMUNICATIONSOUTLET"s,
"POWEROUTLET"s,
"DATAOUTLET"s,
"TELEPHONEOUTLET"s,
"IfcPHMeasure"s,
"IfcParameterValue"s,
"IfcPerformanceHistoryTypeEnum"s,
"IfcPermeableCoveringOperationEnum"s,
"GRILL"s,
"LOUVER"s,
"SCREEN"s,
"IfcPermitTypeEnum"s,
"ACCESS"s,
"BUILDING"s,
"WORK"s,
"IfcPhysicalOrVirtualEnum"s,
"PHYSICAL"s,
"VIRTUAL"s,
"IfcPileConstructionEnum"s,
"CAST_IN_PLACE"s,
"COMPOSITE"s,
"PRECAST_CONCRETE"s,
"PREFAB_STEEL"s,
"IfcPileTypeEnum"s,
"BORED"s,
"DRIVEN"s,
"JETGROUTING"s,
"COHESION"s,
"FRICTION"s,
"SUPPORT"s,
"IfcPipeFittingTypeEnum"s,
"IfcPipeSegmentTypeEnum"s,
"CULVERT"s,
"GUTTER"s,
"SPOOL"s,
"IfcPlanarForceMeasure"s,
"IfcPlaneAngleMeasure"s,
"IfcPlateTypeEnum"s,
"CURTAIN_PANEL"s,
"SHEET"s,
"IfcPositiveInteger"s,
"IfcPositiveLengthMeasure"s,
"IfcPositivePlaneAngleMeasure"s,
"IfcPowerMeasure"s,
"IfcPreferredSurfaceCurveRepresentation"s,
"CURVE3D"s,
"PCURVE_S1"s,
"PCURVE_S2"s,
"IfcPresentableText"s,
"IfcPressureMeasure"s,
"IfcProcedureTypeEnum"s,
"ADVICE_CAUTION"s,
"ADVICE_NOTE"s,
"ADVICE_WARNING"s,
"CALIBRATION"s,
"DIAGNOSTIC"s,
"SHUTDOWN"s,
"STARTUP"s,
"IfcProfileTypeEnum"s,
"CURVE"s,
"AREA"s,
"IfcProjectOrderTypeEnum"s,
"CHANGEORDER"s,
"MAINTENANCEWORKORDER"s,
"MOVEORDER"s,
"PURCHASEORDER"s,
"WORKORDER"s,
"IfcProjectedOrTrueLengthEnum"s,
"PROJECTED_LENGTH"s,
"TRUE_LENGTH"s,
"IfcProjectionElementTypeEnum"s,
"IfcPropertySetTemplateTypeEnum"s,
"PSET_TYPEDRIVENONLY"s,
"PSET_TYPEDRIVENOVERRIDE"s,
"PSET_OCCURRENCEDRIVEN"s,
"PSET_PERFORMANCEDRIVEN"s,
"QTO_TYPEDRIVENONLY"s,
"QTO_TYPEDRIVENOVERRIDE"s,
"QTO_OCCURRENCEDRIVEN"s,
"IfcProtectiveDeviceTrippingUnitTypeEnum"s,
"ELECTRONIC"s,
"ELECTROMAGNETIC"s,
"RESIDUALCURRENT"s,
"THERMAL"s,
"IfcProtectiveDeviceTypeEnum"s,
"CIRCUITBREAKER"s,
"EARTHLEAKAGECIRCUITBREAKER"s,
"EARTHINGSWITCH"s,
"FUSEDISCONNECTOR"s,
"RESIDUALCURRENTCIRCUITBREAKER"s,
"RESIDUALCURRENTSWITCH"s,
"VARISTOR"s,
"IfcPumpTypeEnum"s,
"CIRCULATOR"s,
"ENDSUCTION"s,
"SPLITCASE"s,
"SUBMERSIBLEPUMP"s,
"SUMPPUMP"s,
"VERTICALINLINE"s,
"VERTICALTURBINE"s,
"IfcRadioActivityMeasure"s,
"IfcRailingTypeEnum"s,
"HANDRAIL"s,
"GUARDRAIL"s,
"BALUSTRADE"s,
"IfcRampFlightTypeEnum"s,
"STRAIGHT"s,
"SPIRAL"s,
"IfcRampTypeEnum"s,
"STRAIGHT_RUN_RAMP"s,
"TWO_STRAIGHT_RUN_RAMP"s,
"QUARTER_TURN_RAMP"s,
"TWO_QUARTER_TURN_RAMP"s,
"HALF_TURN_RAMP"s,
"SPIRAL_RAMP"s,
"IfcRatioMeasure"s,
"IfcReal"s,
"IfcRecurrenceTypeEnum"s,
"DAILY"s,
"WEEKLY"s,
"MONTHLY_BY_DAY_OF_MONTH"s,
"MONTHLY_BY_POSITION"s,
"BY_DAY_COUNT"s,
"BY_WEEKDAY_COUNT"s,
"YEARLY_BY_DAY_OF_MONTH"s,
"YEARLY_BY_POSITION"s,
"IfcReflectanceMethodEnum"s,
"BLINN"s,
"FLAT"s,
"GLASS"s,
"MATT"s,
"MIRROR"s,
"PHONG"s,
"STRAUSS"s,
"IfcReinforcingBarRoleEnum"s,
"MAIN"s,
"SHEAR"s,
"LIGATURE"s,
"PUNCHING"s,
"EDGE"s,
"RING"s,
"ANCHORING"s,
"IfcReinforcingBarSurfaceEnum"s,
"PLAIN"s,
"TEXTURED"s,
"IfcReinforcingBarTypeEnum"s,
"IfcReinforcingMeshTypeEnum"s,
"IfcRoleEnum"s,
"SUPPLIER"s,
"MANUFACTURER"s,
"CONTRACTOR"s,
"SUBCONTRACTOR"s,
"ARCHITECT"s,
"STRUCTURALENGINEER"s,
"COSTENGINEER"s,
"CLIENT"s,
"BUILDINGOWNER"s,
"BUILDINGOPERATOR"s,
"MECHANICALENGINEER"s,
"ELECTRICALENGINEER"s,
"PROJECTMANAGER"s,
"FACILITIESMANAGER"s,
"CIVILENGINEER"s,
"COMMISSIONINGENGINEER"s,
"ENGINEER"s,
"CONSULTANT"s,
"CONSTRUCTIONMANAGER"s,
"FIELDCONSTRUCTIONMANAGER"s,
"RESELLER"s,
"IfcRoofTypeEnum"s,
"FLAT_ROOF"s,
"SHED_ROOF"s,
"GABLE_ROOF"s,
"HIP_ROOF"s,
"HIPPED_GABLE_ROOF"s,
"GAMBREL_ROOF"s,
"MANSARD_ROOF"s,
"BARREL_ROOF"s,
"RAINBOW_ROOF"s,
"BUTTERFLY_ROOF"s,
"PAVILION_ROOF"s,
"DOME_ROOF"s,
"FREEFORM"s,
"IfcRotationalFrequencyMeasure"s,
"IfcRotationalMassMeasure"s,
"IfcRotationalStiffnessMeasure"s,
"IfcRotationalStiffnessSelect"s,
"IfcSIPrefix"s,
"EXA"s,
"PETA"s,
"TERA"s,
"GIGA"s,
"MEGA"s,
"KILO"s,
"HECTO"s,
"DECA"s,
"DECI"s,
"CENTI"s,
"MILLI"s,
"MICRO"s,
"NANO"s,
"PICO"s,
"FEMTO"s,
"ATTO"s,
"IfcSIUnitName"s,
"AMPERE"s,
"BECQUEREL"s,
"CANDELA"s,
"COULOMB"s,
"CUBIC_METRE"s,
"DEGREE_CELSIUS"s,
"FARAD"s,
"GRAM"s,
"GRAY"s,
"HENRY"s,
"HERTZ"s,
"JOULE"s,
"KELVIN"s,
"LUMEN"s,
"LUX"s,
"METRE"s,
"MOLE"s,
"NEWTON"s,
"OHM"s,
"PASCAL"s,
"RADIAN"s,
"SECOND"s,
"SIEMENS"s,
"SIEVERT"s,
"SQUARE_METRE"s,
"STERADIAN"s,
"TESLA"s,
"VOLT"s,
"WATT"s,
"WEBER"s,
"IfcSanitaryTerminalTypeEnum"s,
"BATH"s,
"BIDET"s,
"CISTERN"s,
"SHOWER"s,
"SANITARYFOUNTAIN"s,
"TOILETPAN"s,
"URINAL"s,
"WASHHANDBASIN"s,
"WCSEAT"s,
"IfcSectionModulusMeasure"s,
"IfcSectionTypeEnum"s,
"UNIFORM"s,
"TAPERED"s,
"IfcSectionalAreaIntegralMeasure"s,
"IfcSensorTypeEnum"s,
"COSENSOR"s,
"CO2SENSOR"s,
"CONDUCTANCESENSOR"s,
"CONTACTSENSOR"s,
"FIRESENSOR"s,
"FLOWSENSOR"s,
"FROSTSENSOR"s,
"GASSENSOR"s,
"HEATSENSOR"s,
"HUMIDITYSENSOR"s,
"IDENTIFIERSENSOR"s,
"IONCONCENTRATIONSENSOR"s,
"LEVELSENSOR"s,
"LIGHTSENSOR"s,
"MOISTURESENSOR"s,
"MOVEMENTSENSOR"s,
"PHSENSOR"s,
"PRESSURESENSOR"s,
"RADIATIONSENSOR"s,
"RADIOACTIVITYSENSOR"s,
"SMOKESENSOR"s,
"SOUNDSENSOR"s,
"TEMPERATURESENSOR"s,
"WINDSENSOR"s,
"IfcSequenceEnum"s,
"START_START"s,
"START_FINISH"s,
"FINISH_START"s,
"FINISH_FINISH"s,
"IfcShadingDeviceTypeEnum"s,
"JALOUSIE"s,
"SHUTTER"s,
"AWNING"s,
"IfcShearModulusMeasure"s,
"IfcSimplePropertyTemplateTypeEnum"s,
"P_SINGLEVALUE"s,
"P_ENUMERATEDVALUE"s,
"P_BOUNDEDVALUE"s,
"P_LISTVALUE"s,
"P_TABLEVALUE"s,
"P_REFERENCEVALUE"s,
"Q_LENGTH"s,
"Q_AREA"s,
"Q_VOLUME"s,
"Q_COUNT"s,
"Q_WEIGHT"s,
"Q_TIME"s,
"IfcSlabTypeEnum"s,
"FLOOR"s,
"ROOF"s,
"LANDING"s,
"BASESLAB"s,
"IfcSolarDeviceTypeEnum"s,
"SOLARCOLLECTOR"s,
"SOLARPANEL"s,
"IfcSolidAngleMeasure"s,
"IfcSoundPowerLevelMeasure"s,
"IfcSoundPowerMeasure"s,
"IfcSoundPressureLevelMeasure"s,
"IfcSoundPressureMeasure"s,
"IfcSpaceHeaterTypeEnum"s,
"CONVECTOR"s,
"RADIATOR"s,
"IfcSpaceTypeEnum"s,
"SPACE"s,
"PARKING"s,
"GFA"s,
"IfcSpatialZoneTypeEnum"s,
"CONSTRUCTION"s,
"FIRESAFETY"s,
"OCCUPANCY"s,
"IfcSpecificHeatCapacityMeasure"s,
"IfcSpecularExponent"s,
"IfcSpecularRoughness"s,
"IfcStackTerminalTypeEnum"s,
"BIRDCAGE"s,
"COWL"s,
"RAINWATERHOPPER"s,
"IfcStairFlightTypeEnum"s,
"WINDER"s,
"CURVED"s,
"IfcStairTypeEnum"s,
"STRAIGHT_RUN_STAIR"s,
"TWO_STRAIGHT_RUN_STAIR"s,
"QUARTER_WINDING_STAIR"s,
"QUARTER_TURN_STAIR"s,
"HALF_WINDING_STAIR"s,
"HALF_TURN_STAIR"s,
"TWO_QUARTER_WINDING_STAIR"s,
"TWO_QUARTER_TURN_STAIR"s,
"THREE_QUARTER_WINDING_STAIR"s,
"THREE_QUARTER_TURN_STAIR"s,
"SPIRAL_STAIR"s,
"DOUBLE_RETURN_STAIR"s,
"CURVED_RUN_STAIR"s,
"TWO_CURVED_RUN_STAIR"s,
"IfcStateEnum"s,
"READWRITE"s,
"READONLY"s,
"LOCKED"s,
"READWRITELOCKED"s,
"READONLYLOCKED"s,
"IfcStructuralCurveActivityTypeEnum"s,
"CONST"s,
"POLYGONAL"s,
"EQUIDISTANT"s,
"SINUS"s,
"PARABOLA"s,
"DISCRETE"s,
"IfcStructuralCurveMemberTypeEnum"s,
"RIGID_JOINED_MEMBER"s,
"PIN_JOINED_MEMBER"s,
"TENSION_MEMBER"s,
"COMPRESSION_MEMBER"s,
"IfcStructuralSurfaceActivityTypeEnum"s,
"BILINEAR"s,
"ISOCONTOUR"s,
"IfcStructuralSurfaceMemberTypeEnum"s,
"BENDING_ELEMENT"s,
"MEMBRANE_ELEMENT"s,
"SHELL"s,
"IfcSubContractResourceTypeEnum"s,
"PURCHASE"s,
"IfcSurfaceFeatureTypeEnum"s,
"MARK"s,
"TAG"s,
"TREATMENT"s,
"IfcSurfaceSide"s,
"BOTH"s,
"IfcSwitchingDeviceTypeEnum"s,
"CONTACTOR"s,
"DIMMERSWITCH"s,
"EMERGENCYSTOP"s,
"KEYPAD"s,
"MOMENTARYSWITCH"s,
"SELECTORSWITCH"s,
"STARTER"s,
"SWITCHDISCONNECTOR"s,
"TOGGLESWITCH"s,
"IfcSystemFurnitureElementTypeEnum"s,
"PANEL"s,
"WORKSURFACE"s,
"IfcTankTypeEnum"s,
"BASIN"s,
"BREAKPRESSURE"s,
"EXPANSION"s,
"FEEDANDEXPANSION"s,
"PRESSUREVESSEL"s,
"STORAGE"s,
"VESSEL"s,
"IfcTaskDurationEnum"s,
"ELAPSEDTIME"s,
"WORKTIME"s,
"IfcTaskTypeEnum"s,
"ATTENDANCE"s,
"DEMOLITION"s,
"DISMANTLE"s,
"INSTALLATION"s,
"LOGISTIC"s,
"MAINTENANCE"s,
"MOVE"s,
"OPERATION"s,
"REMOVAL"s,
"RENOVATION"s,
"IfcTemperatureGradientMeasure"s,
"IfcTemperatureRateOfChangeMeasure"s,
"IfcTendonAnchorTypeEnum"s,
"COUPLER"s,
"FIXED_END"s,
"TENSIONING_END"s,
"IfcTendonTypeEnum"s,
"BAR"s,
"COATED"s,
"STRAND"s,
"WIRE"s,
"IfcText"s,
"IfcTextAlignment"s,
"IfcTextDecoration"s,
"IfcTextFontName"s,
"IfcTextPath"s,
"UP"s,
"DOWN"s,
"IfcTextTransformation"s,
"IfcThermalAdmittanceMeasure"s,
"IfcThermalConductivityMeasure"s,
"IfcThermalExpansionCoefficientMeasure"s,
"IfcThermalResistanceMeasure"s,
"IfcThermalTransmittanceMeasure"s,
"IfcThermodynamicTemperatureMeasure"s,
"IfcTime"s,
"IfcTimeMeasure"s,
"IfcTimeOrRatioSelect"s,
"IfcTimeSeriesDataTypeEnum"s,
"CONTINUOUS"s,
"DISCRETEBINARY"s,
"PIECEWISEBINARY"s,
"PIECEWISECONSTANT"s,
"PIECEWISECONTINUOUS"s,
"IfcTimeStamp"s,
"IfcTorqueMeasure"s,
"IfcTransformerTypeEnum"s,
"FREQUENCY"s,
"INVERTER"s,
"RECTIFIER"s,
"VOLTAGE"s,
"IfcTransitionCode"s,
"DISCONTINUOUS"s,
"CONTSAMEGRADIENT"s,
"CONTSAMEGRADIENTSAMECURVATURE"s,
"IfcTranslationalStiffnessSelect"s,
"IfcTransportElementTypeEnum"s,
"ELEVATOR"s,
"ESCALATOR"s,
"MOVINGWALKWAY"s,
"CRANEWAY"s,
"LIFTINGGEAR"s,
"IfcTrimmingPreference"s,
"CARTESIAN"s,
"IfcTubeBundleTypeEnum"s,
"FINNED"s,
"IfcURIReference"s,
"IfcUnitEnum"s,
"ABSORBEDDOSEUNIT"s,
"AMOUNTOFSUBSTANCEUNIT"s,
"AREAUNIT"s,
"DOSEEQUIVALENTUNIT"s,
"ELECTRICCAPACITANCEUNIT"s,
"ELECTRICCHARGEUNIT"s,
"ELECTRICCONDUCTANCEUNIT"s,
"ELECTRICCURRENTUNIT"s,
"ELECTRICRESISTANCEUNIT"s,
"ELECTRICVOLTAGEUNIT"s,
"ENERGYUNIT"s,
"FORCEUNIT"s,
"FREQUENCYUNIT"s,
"ILLUMINANCEUNIT"s,
"INDUCTANCEUNIT"s,
"LENGTHUNIT"s,
"LUMINOUSFLUXUNIT"s,
"LUMINOUSINTENSITYUNIT"s,
"MAGNETICFLUXDENSITYUNIT"s,
"MAGNETICFLUXUNIT"s,
"MASSUNIT"s,
"PLANEANGLEUNIT"s,
"POWERUNIT"s,
"PRESSUREUNIT"s,
"RADIOACTIVITYUNIT"s,
"SOLIDANGLEUNIT"s,
"THERMODYNAMICTEMPERATUREUNIT"s,
"TIMEUNIT"s,
"VOLUMEUNIT"s,
"IfcUnitaryControlElementTypeEnum"s,
"ALARMPANEL"s,
"CONTROLPANEL"s,
"GASDETECTIONPANEL"s,
"INDICATORPANEL"s,
"MIMICPANEL"s,
"HUMIDISTAT"s,
"THERMOSTAT"s,
"WEATHERSTATION"s,
"IfcUnitaryEquipmentTypeEnum"s,
"AIRHANDLER"s,
"AIRCONDITIONINGUNIT"s,
"DEHUMIDIFIER"s,
"SPLITSYSTEM"s,
"ROOFTOPUNIT"s,
"IfcValveTypeEnum"s,
"AIRRELEASE"s,
"ANTIVACUUM"s,
"CHANGEOVER"s,
"CHECK"s,
"COMMISSIONING"s,
"DIVERTING"s,
"DRAWOFFCOCK"s,
"DOUBLECHECK"s,
"DOUBLEREGULATING"s,
"FAUCET"s,
"FLUSHING"s,
"GASCOCK"s,
"GASTAP"s,
"ISOLATING"s,
"MIXING"s,
"PRESSUREREDUCING"s,
"PRESSURERELIEF"s,
"REGULATING"s,
"SAFETYCUTOFF"s,
"STEAMTRAP"s,
"STOPCOCK"s,
"IfcVaporPermeabilityMeasure"s,
"IfcVibrationIsolatorTypeEnum"s,
"COMPRESSION"s,
"SPRING"s,
"IfcVoidingFeatureTypeEnum"s,
"CUTOUT"s,
"NOTCH"s,
"HOLE"s,
"MITER"s,
"CHAMFER"s,
"IfcVolumeMeasure"s,
"IfcVolumetricFlowRateMeasure"s,
"IfcWallTypeEnum"s,
"MOVABLE"s,
"PARAPET"s,
"PARTITIONING"s,
"PLUMBINGWALL"s,
"SOLIDWALL"s,
"STANDARD"s,
"ELEMENTEDWALL"s,
"IfcWarpingConstantMeasure"s,
"IfcWarpingMomentMeasure"s,
"IfcWarpingStiffnessSelect"s,
"IfcWasteTerminalTypeEnum"s,
"FLOORTRAP"s,
"FLOORWASTE"s,
"GULLYSUMP"s,
"GULLYTRAP"s,
"ROOFDRAIN"s,
"WASTEDISPOSALUNIT"s,
"WASTETRAP"s,
"IfcWindowPanelOperationEnum"s,
"SIDEHUNGRIGHTHAND"s,
"SIDEHUNGLEFTHAND"s,
"TILTANDTURNRIGHTHAND"s,
"TILTANDTURNLEFTHAND"s,
"TOPHUNG"s,
"BOTTOMHUNG"s,
"PIVOTHORIZONTAL"s,
"PIVOTVERTICAL"s,
"SLIDINGHORIZONTAL"s,
"SLIDINGVERTICAL"s,
"REMOVABLECASEMENT"s,
"FIXEDCASEMENT"s,
"OTHEROPERATION"s,
"IfcWindowPanelPositionEnum"s,
"BOTTOM"s,
"TOP"s,
"IfcWindowStyleConstructionEnum"s,
"OTHER_CONSTRUCTION"s,
"IfcWindowStyleOperationEnum"s,
"SINGLE_PANEL"s,
"DOUBLE_PANEL_VERTICAL"s,
"DOUBLE_PANEL_HORIZONTAL"s,
"TRIPLE_PANEL_VERTICAL"s,
"TRIPLE_PANEL_BOTTOM"s,
"TRIPLE_PANEL_TOP"s,
"TRIPLE_PANEL_LEFT"s,
"TRIPLE_PANEL_RIGHT"s,
"TRIPLE_PANEL_HORIZONTAL"s,
"IfcWindowTypeEnum"s,
"WINDOW"s,
"SKYLIGHT"s,
"LIGHTDOME"s,
"IfcWindowTypePartitioningEnum"s,
"IfcWorkCalendarTypeEnum"s,
"FIRSTSHIFT"s,
"SECONDSHIFT"s,
"THIRDSHIFT"s,
"IfcWorkPlanTypeEnum"s,
"ACTUAL"s,
"BASELINE"s,
"PLANNED"s,
"IfcWorkScheduleTypeEnum"s,
"IfcActorRole"s,
"IfcAddress"s,
"IfcApplication"s,
"IfcAppliedValue"s,
"IfcApproval"s,
"IfcBoundaryCondition"s,
"IfcBoundaryEdgeCondition"s,
"IfcBoundaryFaceCondition"s,
"IfcBoundaryNodeCondition"s,
"IfcBoundaryNodeConditionWarping"s,
"IfcConnectionGeometry"s,
"IfcConnectionPointGeometry"s,
"IfcConnectionSurfaceGeometry"s,
"IfcConnectionVolumeGeometry"s,
"IfcConstraint"s,
"IfcCoordinateOperation"s,
"IfcCoordinateReferenceSystem"s,
"IfcCostValue"s,
"IfcDerivedUnit"s,
"IfcDerivedUnitElement"s,
"IfcDimensionalExponents"s,
"IfcExternalInformation"s,
"IfcExternalReference"s,
"IfcExternallyDefinedHatchStyle"s,
"IfcExternallyDefinedSurfaceStyle"s,
"IfcExternallyDefinedTextFont"s,
"IfcGridAxis"s,
"IfcIrregularTimeSeriesValue"s,
"IfcLibraryInformation"s,
"IfcLibraryReference"s,
"IfcLightDistributionData"s,
"IfcLightIntensityDistribution"s,
"IfcMapConversion"s,
"IfcMaterialClassificationRelationship"s,
"IfcMaterialDefinition"s,
"IfcMaterialLayer"s,
"IfcMaterialLayerSet"s,
"IfcMaterialLayerWithOffsets"s,
"IfcMaterialList"s,
"IfcMaterialProfile"s,
"IfcMaterialProfileSet"s,
"IfcMaterialProfileWithOffsets"s,
"IfcMaterialUsageDefinition"s,
"IfcMeasureWithUnit"s,
"IfcMetric"s,
"IfcMonetaryUnit"s,
"IfcNamedUnit"s,
"IfcObjectPlacement"s,
"IfcObjective"s,
"IfcOrganization"s,
"IfcOwnerHistory"s,
"IfcPerson"s,
"IfcPersonAndOrganization"s,
"IfcPhysicalQuantity"s,
"IfcPhysicalSimpleQuantity"s,
"IfcPostalAddress"s,
"IfcPresentationItem"s,
"IfcPresentationLayerAssignment"s,
"IfcPresentationLayerWithStyle"s,
"IfcPresentationStyle"s,
"IfcPresentationStyleAssignment"s,
"IfcProductRepresentation"s,
"IfcProfileDef"s,
"IfcProjectedCRS"s,
"IfcPropertyAbstraction"s,
"IfcPropertyEnumeration"s,
"IfcQuantityArea"s,
"IfcQuantityCount"s,
"IfcQuantityLength"s,
"IfcQuantityTime"s,
"IfcQuantityVolume"s,
"IfcQuantityWeight"s,
"IfcRecurrencePattern"s,
"IfcReference"s,
"IfcRepresentation"s,
"IfcRepresentationContext"s,
"IfcRepresentationItem"s,
"IfcRepresentationMap"s,
"IfcResourceLevelRelationship"s,
"IfcRoot"s,
"IfcSIUnit"s,
"IfcSchedulingTime"s,
"IfcShapeAspect"s,
"IfcShapeModel"s,
"IfcShapeRepresentation"s,
"IfcStructuralConnectionCondition"s,
"IfcStructuralLoad"s,
"IfcStructuralLoadConfiguration"s,
"IfcStructuralLoadOrResult"s,
"IfcStructuralLoadStatic"s,
"IfcStructuralLoadTemperature"s,
"IfcStyleModel"s,
"IfcStyledItem"s,
"IfcStyledRepresentation"s,
"IfcSurfaceReinforcementArea"s,
"IfcSurfaceStyle"s,
"IfcSurfaceStyleLighting"s,
"IfcSurfaceStyleRefraction"s,
"IfcSurfaceStyleShading"s,
"IfcSurfaceStyleWithTextures"s,
"IfcSurfaceTexture"s,
"IfcTable"s,
"IfcTableColumn"s,
"IfcTableRow"s,
"IfcTaskTime"s,
"IfcTaskTimeRecurring"s,
"IfcTelecomAddress"s,
"IfcTextStyle"s,
"IfcTextStyleForDefinedFont"s,
"IfcTextStyleTextModel"s,
"IfcTextureCoordinate"s,
"IfcTextureCoordinateGenerator"s,
"IfcTextureMap"s,
"IfcTextureVertex"s,
"IfcTextureVertexList"s,
"IfcTimePeriod"s,
"IfcTimeSeries"s,
"IfcTimeSeriesValue"s,
"IfcTopologicalRepresentationItem"s,
"IfcTopologyRepresentation"s,
"IfcUnitAssignment"s,
"IfcVertex"s,
"IfcVertexPoint"s,
"IfcVirtualGridIntersection"s,
"IfcWorkTime"s,
"IfcActorSelect"s,
"IfcArcIndex"s,
"IfcBendingParameterSelect"s,
"IfcBoxAlignment"s,
"IfcDerivedMeasureValue"s,
"IfcLayeredItem"s,
"IfcLibrarySelect"s,
"IfcLightDistributionDataSourceSelect"s,
"IfcLineIndex"s,
"IfcMaterialSelect"s,
"IfcNormalisedRatioMeasure"s,
"IfcObjectReferenceSelect"s,
"IfcPositiveRatioMeasure"s,
"IfcSegmentIndexSelect"s,
"IfcSimpleValue"s,
"IfcSizeSelect"s,
"IfcSpecularHighlightSelect"s,
"IfcStyleAssignmentSelect"s,
"IfcSurfaceStyleElementSelect"s,
"IfcUnit"s,
"IfcApprovalRelationship"s,
"IfcArbitraryClosedProfileDef"s,
"IfcArbitraryOpenProfileDef"s,
"IfcArbitraryProfileDefWithVoids"s,
"IfcBlobTexture"s,
"IfcCenterLineProfileDef"s,
"IfcClassification"s,
"IfcClassificationReference"s,
"IfcColourRgbList"s,
"IfcColourSpecification"s,
"IfcCompositeProfileDef"s,
"IfcConnectedFaceSet"s,
"IfcConnectionCurveGeometry"s,
"IfcConnectionPointEccentricity"s,
"IfcContextDependentUnit"s,
"IfcConversionBasedUnit"s,
"IfcConversionBasedUnitWithOffset"s,
"IfcCurrencyRelationship"s,
"IfcCurveStyle"s,
"IfcCurveStyleFont"s,
"IfcCurveStyleFontAndScaling"s,
"IfcCurveStyleFontPattern"s,
"IfcDerivedProfileDef"s,
"IfcDocumentInformation"s,
"IfcDocumentInformationRelationship"s,
"IfcDocumentReference"s,
"IfcEdge"s,
"IfcEdgeCurve"s,
"IfcEventTime"s,
"IfcExtendedProperties"s,
"IfcExternalReferenceRelationship"s,
"IfcFace"s,
"IfcFaceBound"s,
"IfcFaceOuterBound"s,
"IfcFaceSurface"s,
"IfcFailureConnectionCondition"s,
"IfcFillAreaStyle"s,
"IfcGeometricRepresentationContext"s,
"IfcGeometricRepresentationItem"s,
"IfcGeometricRepresentationSubContext"s,
"IfcGeometricSet"s,
"IfcGridPlacement"s,
"IfcHalfSpaceSolid"s,
"IfcImageTexture"s,
"IfcIndexedColourMap"s,
"IfcIndexedTextureMap"s,
"IfcIndexedTriangleTextureMap"s,
"IfcIrregularTimeSeries"s,
"IfcLagTime"s,
"IfcLightSource"s,
"IfcLightSourceAmbient"s,
"IfcLightSourceDirectional"s,
"IfcLightSourceGoniometric"s,
"IfcLightSourcePositional"s,
"IfcLightSourceSpot"s,
"IfcLocalPlacement"s,
"IfcLoop"s,
"IfcMappedItem"s,
"IfcMaterial"s,
"IfcMaterialConstituent"s,
"IfcMaterialConstituentSet"s,
"IfcMaterialDefinitionRepresentation"s,
"IfcMaterialLayerSetUsage"s,
"IfcMaterialProfileSetUsage"s,
"IfcMaterialProfileSetUsageTapering"s,
"IfcMaterialProperties"s,
"IfcMaterialRelationship"s,
"IfcMirroredProfileDef"s,
"IfcObjectDefinition"s,
"IfcOpenShell"s,
"IfcOrganizationRelationship"s,
"IfcOrientedEdge"s,
"IfcParameterizedProfileDef"s,
"IfcPath"s,
"IfcPhysicalComplexQuantity"s,
"IfcPixelTexture"s,
"IfcPlacement"s,
"IfcPlanarExtent"s,
"IfcPoint"s,
"IfcPointOnCurve"s,
"IfcPointOnSurface"s,
"IfcPolyLoop"s,
"IfcPolygonalBoundedHalfSpace"s,
"IfcPreDefinedItem"s,
"IfcPreDefinedProperties"s,
"IfcPreDefinedTextFont"s,
"IfcProductDefinitionShape"s,
"IfcProfileProperties"s,
"IfcProperty"s,
"IfcPropertyDefinition"s,
"IfcPropertyDependencyRelationship"s,
"IfcPropertySetDefinition"s,
"IfcPropertyTemplateDefinition"s,
"IfcQuantitySet"s,
"IfcRectangleProfileDef"s,
"IfcRegularTimeSeries"s,
"IfcReinforcementBarProperties"s,
"IfcRelationship"s,
"IfcResourceApprovalRelationship"s,
"IfcResourceConstraintRelationship"s,
"IfcResourceTime"s,
"IfcRoundedRectangleProfileDef"s,
"IfcSectionProperties"s,
"IfcSectionReinforcementProperties"s,
"IfcSectionedSpine"s,
"IfcShellBasedSurfaceModel"s,
"IfcSimpleProperty"s,
"IfcSlippageConnectionCondition"s,
"IfcSolidModel"s,
"IfcStructuralLoadLinearForce"s,
"IfcStructuralLoadPlanarForce"s,
"IfcStructuralLoadSingleDisplacement"s,
"IfcStructuralLoadSingleDisplacementDistortion"s,
"IfcStructuralLoadSingleForce"s,
"IfcStructuralLoadSingleForceWarping"s,
"IfcSubedge"s,
"IfcSurface"s,
"IfcSurfaceStyleRendering"s,
"IfcSweptAreaSolid"s,
"IfcSweptDiskSolid"s,
"IfcSweptDiskSolidPolygonal"s,
"IfcSweptSurface"s,
"IfcTShapeProfileDef"s,
"IfcTessellatedItem"s,
"IfcTextLiteral"s,
"IfcTextLiteralWithExtent"s,
"IfcTextStyleFontModel"s,
"IfcTrapeziumProfileDef"s,
"IfcTypeObject"s,
"IfcTypeProcess"s,
"IfcTypeProduct"s,
"IfcTypeResource"s,
"IfcUShapeProfileDef"s,
"IfcVector"s,
"IfcVertexLoop"s,
"IfcWindowStyle"s,
"IfcZShapeProfileDef"s,
"IfcClassificationReferenceSelect"s,
"IfcClassificationSelect"s,
"IfcCoordinateReferenceSystemSelect"s,
"IfcDefinitionSelect"s,
"IfcDocumentSelect"s,
"IfcHatchLineDistanceSelect"s,
"IfcMeasureValue"s,
"IfcPointOrVertexPoint"s,
"IfcPresentationStyleSelect"s,
"IfcProductRepresentationSelect"s,
"IfcPropertySetDefinitionSet"s,
"IfcResourceObjectSelect"s,
"IfcTextFontSelect"s,
"IfcValue"s,
"IfcAdvancedFace"s,
"IfcAnnotationFillArea"s,
"IfcAsymmetricIShapeProfileDef"s,
"IfcAxis1Placement"s,
"IfcAxis2Placement2D"s,
"IfcAxis2Placement3D"s,
"IfcBooleanResult"s,
"IfcBoundedSurface"s,
"IfcBoundingBox"s,
"IfcBoxedHalfSpace"s,
"IfcCShapeProfileDef"s,
"IfcCartesianPoint"s,
"IfcCartesianPointList"s,
"IfcCartesianPointList2D"s,
"IfcCartesianPointList3D"s,
"IfcCartesianTransformationOperator"s,
"IfcCartesianTransformationOperator2D"s,
"IfcCartesianTransformationOperator2DnonUniform"s,
"IfcCartesianTransformationOperator3D"s,
"IfcCartesianTransformationOperator3DnonUniform"s,
"IfcCircleProfileDef"s,
"IfcClosedShell"s,
"IfcColourRgb"s,
"IfcComplexProperty"s,
"IfcCompositeCurveSegment"s,
"IfcConstructionResourceType"s,
"IfcContext"s,
"IfcCrewResourceType"s,
"IfcCsgPrimitive3D"s,
"IfcCsgSolid"s,
"IfcCurve"s,
"IfcCurveBoundedPlane"s,
"IfcCurveBoundedSurface"s,
"IfcDirection"s,
"IfcDoorStyle"s,
"IfcEdgeLoop"s,
"IfcElementQuantity"s,
"IfcElementType"s,
"IfcElementarySurface"s,
"IfcEllipseProfileDef"s,
"IfcEventType"s,
"IfcExtrudedAreaSolid"s,
"IfcExtrudedAreaSolidTapered"s,
"IfcFaceBasedSurfaceModel"s,
"IfcFillAreaStyleHatching"s,
"IfcFillAreaStyleTiles"s,
"IfcFixedReferenceSweptAreaSolid"s,
"IfcFurnishingElementType"s,
"IfcFurnitureType"s,
"IfcGeographicElementType"s,
"IfcGeometricCurveSet"s,
"IfcIShapeProfileDef"s,
"IfcIndexedPolygonalFace"s,
"IfcIndexedPolygonalFaceWithVoids"s,
"IfcLShapeProfileDef"s,
"IfcLaborResourceType"s,
"IfcLine"s,
"IfcManifoldSolidBrep"s,
"IfcObject"s,
"IfcOffsetCurve2D"s,
"IfcOffsetCurve3D"s,
"IfcPcurve"s,
"IfcPlanarBox"s,
"IfcPlane"s,
"IfcPreDefinedColour"s,
"IfcPreDefinedCurveFont"s,
"IfcPreDefinedPropertySet"s,
"IfcProcedureType"s,
"IfcProcess"s,
"IfcProduct"s,
"IfcProject"s,
"IfcProjectLibrary"s,
"IfcPropertyBoundedValue"s,
"IfcPropertyEnumeratedValue"s,
"IfcPropertyListValue"s,
"IfcPropertyReferenceValue"s,
"IfcPropertySet"s,
"IfcPropertySetTemplate"s,
"IfcPropertySingleValue"s,
"IfcPropertyTableValue"s,
"IfcPropertyTemplate"s,
"IfcProxy"s,
"IfcRectangleHollowProfileDef"s,
"IfcRectangularPyramid"s,
"IfcRectangularTrimmedSurface"s,
"IfcReinforcementDefinitionProperties"s,
"IfcRelAssigns"s,
"IfcRelAssignsToActor"s,
"IfcRelAssignsToControl"s,
"IfcRelAssignsToGroup"s,
"IfcRelAssignsToGroupByFactor"s,
"IfcRelAssignsToProcess"s,
"IfcRelAssignsToProduct"s,
"IfcRelAssignsToResource"s,
"IfcRelAssociates"s,
"IfcRelAssociatesApproval"s,
"IfcRelAssociatesClassification"s,
"IfcRelAssociatesConstraint"s,
"IfcRelAssociatesDocument"s,
"IfcRelAssociatesLibrary"s,
"IfcRelAssociatesMaterial"s,
"IfcRelConnects"s,
"IfcRelConnectsElements"s,
"IfcRelConnectsPathElements"s,
"IfcRelConnectsPortToElement"s,
"IfcRelConnectsPorts"s,
"IfcRelConnectsStructuralActivity"s,
"IfcRelConnectsStructuralMember"s,
"IfcRelConnectsWithEccentricity"s,
"IfcRelConnectsWithRealizingElements"s,
"IfcRelContainedInSpatialStructure"s,
"IfcRelCoversBldgElements"s,
"IfcRelCoversSpaces"s,
"IfcRelDeclares"s,
"IfcRelDecomposes"s,
"IfcRelDefines"s,
"IfcRelDefinesByObject"s,
"IfcRelDefinesByProperties"s,
"IfcRelDefinesByTemplate"s,
"IfcRelDefinesByType"s,
"IfcRelFillsElement"s,
"IfcRelFlowControlElements"s,
"IfcRelInterferesElements"s,
"IfcRelNests"s,
"IfcRelProjectsElement"s,
"IfcRelReferencedInSpatialStructure"s,
"IfcRelSequence"s,
"IfcRelServicesBuildings"s,
"IfcRelSpaceBoundary"s,
"IfcRelSpaceBoundary1stLevel"s,
"IfcRelSpaceBoundary2ndLevel"s,
"IfcRelVoidsElement"s,
"IfcReparametrisedCompositeCurveSegment"s,
"IfcResource"s,
"IfcRevolvedAreaSolid"s,
"IfcRevolvedAreaSolidTapered"s,
"IfcRightCircularCone"s,
"IfcRightCircularCylinder"s,
"IfcSimplePropertyTemplate"s,
"IfcSpatialElement"s,
"IfcSpatialElementType"s,
"IfcSpatialStructureElement"s,
"IfcSpatialStructureElementType"s,
"IfcSpatialZone"s,
"IfcSpatialZoneType"s,
"IfcSphere"s,
"IfcSphericalSurface"s,
"IfcStructuralActivity"s,
"IfcStructuralItem"s,
"IfcStructuralMember"s,
"IfcStructuralReaction"s,
"IfcStructuralSurfaceMember"s,
"IfcStructuralSurfaceMemberVarying"s,
"IfcStructuralSurfaceReaction"s,
"IfcSubContractResourceType"s,
"IfcSurfaceCurve"s,
"IfcSurfaceCurveSweptAreaSolid"s,
"IfcSurfaceOfLinearExtrusion"s,
"IfcSurfaceOfRevolution"s,
"IfcSystemFurnitureElementType"s,
"IfcTask"s,
"IfcTaskType"s,
"IfcTessellatedFaceSet"s,
"IfcToroidalSurface"s,
"IfcTransportElementType"s,
"IfcTriangulatedFaceSet"s,
"IfcWindowLiningProperties"s,
"IfcWindowPanelProperties"s,
"IfcAppliedValueSelect"s,
"IfcAxis2Placement"s,
"IfcBooleanOperand"s,
"IfcColour"s,
"IfcColourOrFactor"s,
"IfcCsgSelect"s,
"IfcCurveStyleFontSelect"s,
"IfcFillStyleSelect"s,
"IfcGeometricSetSelect"s,
"IfcGridPlacementDirectionSelect"s,
"IfcMetricValueSelect"s,
"IfcProcessSelect"s,
"IfcProductSelect"s,
"IfcPropertySetDefinitionSelect"s,
"IfcResourceSelect"s,
"IfcShell"s,
"IfcSolidOrShell"s,
"IfcSurfaceOrFaceSurface"s,
"IfcTrimmingSelect"s,
"IfcVectorOrDirection"s,
"IfcActor"s,
"IfcAdvancedBrep"s,
"IfcAdvancedBrepWithVoids"s,
"IfcAnnotation"s,
"IfcBSplineSurface"s,
"IfcBSplineSurfaceWithKnots"s,
"IfcBlock"s,
"IfcBooleanClippingResult"s,
"IfcBoundedCurve"s,
"IfcBuilding"s,
"IfcBuildingElementType"s,
"IfcBuildingStorey"s,
"IfcChimneyType"s,
"IfcCircleHollowProfileDef"s,
"IfcCivilElementType"s,
"IfcColumnType"s,
"IfcComplexPropertyTemplate"s,
"IfcCompositeCurve"s,
"IfcCompositeCurveOnSurface"s,
"IfcConic"s,
"IfcConstructionEquipmentResourceType"s,
"IfcConstructionMaterialResourceType"s,
"IfcConstructionProductResourceType"s,
"IfcConstructionResource"s,
"IfcControl"s,
"IfcCostItem"s,
"IfcCostSchedule"s,
"IfcCoveringType"s,
"IfcCrewResource"s,
"IfcCurtainWallType"s,
"IfcCylindricalSurface"s,
"IfcDistributionElementType"s,
"IfcDistributionFlowElementType"s,
"IfcDoorLiningProperties"s,
"IfcDoorPanelProperties"s,
"IfcDoorType"s,
"IfcDraughtingPreDefinedColour"s,
"IfcDraughtingPreDefinedCurveFont"s,
"IfcElement"s,
"IfcElementAssembly"s,
"IfcElementAssemblyType"s,
"IfcElementComponent"s,
"IfcElementComponentType"s,
"IfcEllipse"s,
"IfcEnergyConversionDeviceType"s,
"IfcEngineType"s,
"IfcEvaporativeCoolerType"s,
"IfcEvaporatorType"s,
"IfcEvent"s,
"IfcExternalSpatialStructureElement"s,
"IfcFacetedBrep"s,
"IfcFacetedBrepWithVoids"s,
"IfcFastener"s,
"IfcFastenerType"s,
"IfcFeatureElement"s,
"IfcFeatureElementAddition"s,
"IfcFeatureElementSubtraction"s,
"IfcFlowControllerType"s,
"IfcFlowFittingType"s,
"IfcFlowMeterType"s,
"IfcFlowMovingDeviceType"s,
"IfcFlowSegmentType"s,
"IfcFlowStorageDeviceType"s,
"IfcFlowTerminalType"s,
"IfcFlowTreatmentDeviceType"s,
"IfcFootingType"s,
"IfcFurnishingElement"s,
"IfcFurniture"s,
"IfcGeographicElement"s,
"IfcGrid"s,
"IfcGroup"s,
"IfcHeatExchangerType"s,
"IfcHumidifierType"s,
"IfcIndexedPolyCurve"s,
"IfcInterceptorType"s,
"IfcIntersectionCurve"s,
"IfcInventory"s,
"IfcJunctionBoxType"s,
"IfcLaborResource"s,
"IfcLampType"s,
"IfcLightFixtureType"s,
"IfcMechanicalFastener"s,
"IfcMechanicalFastenerType"s,
"IfcMedicalDeviceType"s,
"IfcMemberType"s,
"IfcMotorConnectionType"s,
"IfcOccupant"s,
"IfcOpeningElement"s,
"IfcOpeningStandardCase"s,
"IfcOutletType"s,
"IfcPerformanceHistory"s,
"IfcPermeableCoveringProperties"s,
"IfcPermit"s,
"IfcPileType"s,
"IfcPipeFittingType"s,
"IfcPipeSegmentType"s,
"IfcPlateType"s,
"IfcPolygonalFaceSet"s,
"IfcPolyline"s,
"IfcPort"s,
"IfcProcedure"s,
"IfcProjectOrder"s,
"IfcProjectionElement"s,
"IfcProtectiveDeviceType"s,
"IfcPumpType"s,
"IfcRailingType"s,
"IfcRampFlightType"s,
"IfcRampType"s,
"IfcRationalBSplineSurfaceWithKnots"s,
"IfcReinforcingElement"s,
"IfcReinforcingElementType"s,
"IfcReinforcingMesh"s,
"IfcReinforcingMeshType"s,
"IfcRelAggregates"s,
"IfcRoofType"s,
"IfcSanitaryTerminalType"s,
"IfcSeamCurve"s,
"IfcShadingDeviceType"s,
"IfcSite"s,
"IfcSlabType"s,
"IfcSolarDeviceType"s,
"IfcSpace"s,
"IfcSpaceHeaterType"s,
"IfcSpaceType"s,
"IfcStackTerminalType"s,
"IfcStairFlightType"s,
"IfcStairType"s,
"IfcStructuralAction"s,
"IfcStructuralConnection"s,
"IfcStructuralCurveAction"s,
"IfcStructuralCurveConnection"s,
"IfcStructuralCurveMember"s,
"IfcStructuralCurveMemberVarying"s,
"IfcStructuralCurveReaction"s,
"IfcStructuralLinearAction"s,
"IfcStructuralLoadGroup"s,
"IfcStructuralPointAction"s,
"IfcStructuralPointConnection"s,
"IfcStructuralPointReaction"s,
"IfcStructuralResultGroup"s,
"IfcStructuralSurfaceAction"s,
"IfcStructuralSurfaceConnection"s,
"IfcSubContractResource"s,
"IfcSurfaceFeature"s,
"IfcSwitchingDeviceType"s,
"IfcSystem"s,
"IfcSystemFurnitureElement"s,
"IfcTankType"s,
"IfcTendon"s,
"IfcTendonAnchor"s,
"IfcTendonAnchorType"s,
"IfcTendonType"s,
"IfcTransformerType"s,
"IfcTransportElement"s,
"IfcTrimmedCurve"s,
"IfcTubeBundleType"s,
"IfcUnitaryEquipmentType"s,
"IfcValveType"s,
"IfcVibrationIsolator"s,
"IfcVibrationIsolatorType"s,
"IfcVirtualElement"s,
"IfcVoidingFeature"s,
"IfcWallType"s,
"IfcWasteTerminalType"s,
"IfcWindowType"s,
"IfcWorkCalendar"s,
"IfcWorkControl"s,
"IfcWorkPlan"s,
"IfcWorkSchedule"s,
"IfcZone"s,
"IfcCurveFontOrScaledCurveFontSelect"s,
"IfcCurveOnSurface"s,
"IfcCurveOrEdgeCurve"s,
"IfcStructuralActivityAssignmentSelect"s,
"IfcActionRequest"s,
"IfcAirTerminalBoxType"s,
"IfcAirTerminalType"s,
"IfcAirToAirHeatRecoveryType"s,
"IfcAsset"s,
"IfcAudioVisualApplianceType"s,
"IfcBSplineCurve"s,
"IfcBSplineCurveWithKnots"s,
"IfcBeamType"s,
"IfcBoilerType"s,
"IfcBoundaryCurve"s,
"IfcBuildingElement"s,
"IfcBuildingElementPart"s,
"IfcBuildingElementPartType"s,
"IfcBuildingElementProxy"s,
"IfcBuildingElementProxyType"s,
"IfcBuildingSystem"s,
"IfcBurnerType"s,
"IfcCableCarrierFittingType"s,
"IfcCableCarrierSegmentType"s,
"IfcCableFittingType"s,
"IfcCableSegmentType"s,
"IfcChillerType"s,
"IfcChimney"s,
"IfcCircle"s,
"IfcCivilElement"s,
"IfcCoilType"s,
"IfcColumn"s,
"IfcColumnStandardCase"s,
"IfcCommunicationsApplianceType"s,
"IfcCompressorType"s,
"IfcCondenserType"s,
"IfcConstructionEquipmentResource"s,
"IfcConstructionMaterialResource"s,
"IfcConstructionProductResource"s,
"IfcCooledBeamType"s,
"IfcCoolingTowerType"s,
"IfcCovering"s,
"IfcCurtainWall"s,
"IfcDamperType"s,
"IfcDiscreteAccessory"s,
"IfcDiscreteAccessoryType"s,
"IfcDistributionChamberElementType"s,
"IfcDistributionControlElementType"s,
"IfcDistributionElement"s,
"IfcDistributionFlowElement"s,
"IfcDistributionPort"s,
"IfcDistributionSystem"s,
"IfcDoor"s,
"IfcDoorStandardCase"s,
"IfcDuctFittingType"s,
"IfcDuctSegmentType"s,
"IfcDuctSilencerType"s,
"IfcElectricApplianceType"s,
"IfcElectricDistributionBoardType"s,
"IfcElectricFlowStorageDeviceType"s,
"IfcElectricGeneratorType"s,
"IfcElectricMotorType"s,
"IfcElectricTimeControlType"s,
"IfcEnergyConversionDevice"s,
"IfcEngine"s,
"IfcEvaporativeCooler"s,
"IfcEvaporator"s,
"IfcExternalSpatialElement"s,
"IfcFanType"s,
"IfcFilterType"s,
"IfcFireSuppressionTerminalType"s,
"IfcFlowController"s,
"IfcFlowFitting"s,
"IfcFlowInstrumentType"s,
"IfcFlowMeter"s,
"IfcFlowMovingDevice"s,
"IfcFlowSegment"s,
"IfcFlowStorageDevice"s,
"IfcFlowTerminal"s,
"IfcFlowTreatmentDevice"s,
"IfcFooting"s,
"IfcHeatExchanger"s,
"IfcHumidifier"s,
"IfcInterceptor"s,
"IfcJunctionBox"s,
"IfcLamp"s,
"IfcLightFixture"s,
"IfcMedicalDevice"s,
"IfcMember"s,
"IfcMemberStandardCase"s,
"IfcMotorConnection"s,
"IfcOuterBoundaryCurve"s,
"IfcOutlet"s,
"IfcPile"s,
"IfcPipeFitting"s,
"IfcPipeSegment"s,
"IfcPlate"s,
"IfcPlateStandardCase"s,
"IfcProtectiveDevice"s,
"IfcProtectiveDeviceTrippingUnitType"s,
"IfcPump"s,
"IfcRailing"s,
"IfcRamp"s,
"IfcRampFlight"s,
"IfcRationalBSplineCurveWithKnots"s,
"IfcReinforcingBar"s,
"IfcReinforcingBarType"s,
"IfcRoof"s,
"IfcSanitaryTerminal"s,
"IfcSensorType"s,
"IfcShadingDevice"s,
"IfcSlab"s,
"IfcSlabElementedCase"s,
"IfcSlabStandardCase"s,
"IfcSolarDevice"s,
"IfcSpaceHeater"s,
"IfcStackTerminal"s,
"IfcStair"s,
"IfcStairFlight"s,
"IfcStructuralAnalysisModel"s,
"IfcStructuralLoadCase"s,
"IfcStructuralPlanarAction"s,
"IfcSwitchingDevice"s,
"IfcTank"s,
"IfcTransformer"s,
"IfcTubeBundle"s,
"IfcUnitaryControlElementType"s,
"IfcUnitaryEquipment"s,
"IfcValve"s,
"IfcWall"s,
"IfcWallElementedCase"s,
"IfcWallStandardCase"s,
"IfcWasteTerminal"s,
"IfcWindow"s,
"IfcWindowStandardCase"s,
"IfcSpaceBoundarySelect"s,
"IfcActuatorType"s,
"IfcAirTerminal"s,
"IfcAirTerminalBox"s,
"IfcAirToAirHeatRecovery"s,
"IfcAlarmType"s,
"IfcAudioVisualAppliance"s,
"IfcBeam"s,
"IfcBeamStandardCase"s,
"IfcBoiler"s,
"IfcBurner"s,
"IfcCableCarrierFitting"s,
"IfcCableCarrierSegment"s,
"IfcCableFitting"s,
"IfcCableSegment"s,
"IfcChiller"s,
"IfcCoil"s,
"IfcCommunicationsAppliance"s,
"IfcCompressor"s,
"IfcCondenser"s,
"IfcControllerType"s,
"IfcCooledBeam"s,
"IfcCoolingTower"s,
"IfcDamper"s,
"IfcDistributionChamberElement"s,
"IfcDistributionCircuit"s,
"IfcDistributionControlElement"s,
"IfcDuctFitting"s,
"IfcDuctSegment"s,
"IfcDuctSilencer"s,
"IfcElectricAppliance"s,
"IfcElectricDistributionBoard"s,
"IfcElectricFlowStorageDevice"s,
"IfcElectricGenerator"s,
"IfcElectricMotor"s,
"IfcElectricTimeControl"s,
"IfcFan"s,
"IfcFilter"s,
"IfcFireSuppressionTerminal"s,
"IfcFlowInstrument"s,
"IfcProtectiveDeviceTrippingUnit"s,
"IfcSensor"s,
"IfcUnitaryControlElement"s,
"IfcActuator"s,
"IfcAlarm"s,
"IfcController"s,
"PredefinedType"s,
"Status"s,
"LongDescription"s,
"TheActor"s,
"Role"s,
"UserDefinedRole"s,
"Description"s,
"Purpose"s,
"UserDefinedPurpose"s,
"Voids"s,
"OuterBoundary"s,
"InnerBoundaries"s,
"ApplicationDeveloper"s,
"Version"s,
"ApplicationFullName"s,
"ApplicationIdentifier"s,
"Name"s,
"AppliedValue"s,
"UnitBasis"s,
"ApplicableDate"s,
"FixedUntilDate"s,
"Category"s,
"Condition"s,
"ArithmeticOperator"s,
"Components"s,
"Identifier"s,
"TimeOfApproval"s,
"Level"s,
"Qualifier"s,
"RequestingApproval"s,
"GivingApproval"s,
"RelatingApproval"s,
"RelatedApprovals"s,
"OuterCurve"s,
"Curve"s,
"InnerCurves"s,
"Identification"s,
"OriginalValue"s,
"CurrentValue"s,
"TotalReplacementCost"s,
"Owner"s,
"User"s,
"ResponsiblePerson"s,
"IncorporationDate"s,
"DepreciatedValue"s,
"BottomFlangeWidth"s,
"OverallDepth"s,
"WebThickness"s,
"BottomFlangeThickness"s,
"BottomFlangeFilletRadius"s,
"TopFlangeWidth"s,
"TopFlangeThickness"s,
"TopFlangeFilletRadius"s,
"BottomFlangeEdgeRadius"s,
"BottomFlangeSlope"s,
"TopFlangeEdgeRadius"s,
"TopFlangeSlope"s,
"Axis"s,
"RefDirection"s,
"Degree"s,
"ControlPointsList"s,
"CurveForm"s,
"ClosedCurve"s,
"SelfIntersect"s,
"KnotMultiplicities"s,
"Knots"s,
"KnotSpec"s,
"UDegree"s,
"VDegree"s,
"SurfaceForm"s,
"UClosed"s,
"VClosed"s,
"UMultiplicities"s,
"VMultiplicities"s,
"UKnots"s,
"VKnots"s,
"RasterFormat"s,
"RasterCode"s,
"XLength"s,
"YLength"s,
"ZLength"s,
"Operator"s,
"FirstOperand"s,
"SecondOperand"s,
"TranslationalStiffnessByLengthX"s,
"TranslationalStiffnessByLengthY"s,
"TranslationalStiffnessByLengthZ"s,
"RotationalStiffnessByLengthX"s,
"RotationalStiffnessByLengthY"s,
"RotationalStiffnessByLengthZ"s,
"TranslationalStiffnessByAreaX"s,
"TranslationalStiffnessByAreaY"s,
"TranslationalStiffnessByAreaZ"s,
"TranslationalStiffnessX"s,
"TranslationalStiffnessY"s,
"TranslationalStiffnessZ"s,
"RotationalStiffnessX"s,
"RotationalStiffnessY"s,
"RotationalStiffnessZ"s,
"WarpingStiffness"s,
"Corner"s,
"XDim"s,
"YDim"s,
"ZDim"s,
"Enclosure"s,
"ElevationOfRefHeight"s,
"ElevationOfTerrain"s,
"BuildingAddress"s,
"Elevation"s,
"LongName"s,
"Depth"s,
"Width"s,
"WallThickness"s,
"Girth"s,
"InternalFilletRadius"s,
"Coordinates"s,
"CoordList"s,
"Axis1"s,
"Axis2"s,
"LocalOrigin"s,
"Scale"s,
"Scale2"s,
"Axis3"s,
"Scale3"s,
"Thickness"s,
"Radius"s,
"Source"s,
"Edition"s,
"EditionDate"s,
"Location"s,
"ReferenceTokens"s,
"ReferencedSource"s,
"Sort"s,
"Red"s,
"Green"s,
"Blue"s,
"ColourList"s,
"UsageName"s,
"HasProperties"s,
"TemplateType"s,
"HasPropertyTemplates"s,
"Segments"s,
"Transition"s,
"SameSense"s,
"ParentCurve"s,
"Profiles"s,
"Label"s,
"Position"s,
"CfsFaces"s,
"CurveOnRelatingElement"s,
"CurveOnRelatedElement"s,
"EccentricityInX"s,
"EccentricityInY"s,
"EccentricityInZ"s,
"PointOnRelatingElement"s,
"PointOnRelatedElement"s,
"SurfaceOnRelatingElement"s,
"SurfaceOnRelatedElement"s,
"VolumeOnRelatingElement"s,
"VolumeOnRelatedElement"s,
"ConstraintGrade"s,
"ConstraintSource"s,
"CreatingActor"s,
"CreationTime"s,
"UserDefinedGrade"s,
"Usage"s,
"BaseCosts"s,
"BaseQuantity"s,
"ObjectType"s,
"Phase"s,
"RepresentationContexts"s,
"UnitsInContext"s,
"ConversionFactor"s,
"ConversionOffset"s,
"SourceCRS"s,
"TargetCRS"s,
"GeodeticDatum"s,
"VerticalDatum"s,
"CostValues"s,
"CostQuantities"s,
"SubmittedOn"s,
"UpdateDate"s,
"TreeRootExpression"s,
"RelatingMonetaryUnit"s,
"RelatedMonetaryUnit"s,
"ExchangeRate"s,
"RateDateTime"s,
"RateSource"s,
"BasisSurface"s,
"Boundaries"s,
"ImplicitOuter"s,
"CurveFont"s,
"CurveWidth"s,
"CurveColour"s,
"ModelOrDraughting"s,
"PatternList"s,
"CurveFontScaling"s,
"VisibleSegmentLength"s,
"InvisibleSegmentLength"s,
"ParentProfile"s,
"Elements"s,
"UnitType"s,
"UserDefinedType"s,
"Unit"s,
"Exponent"s,
"LengthExponent"s,
"MassExponent"s,
"TimeExponent"s,
"ElectricCurrentExponent"s,
"ThermodynamicTemperatureExponent"s,
"AmountOfSubstanceExponent"s,
"LuminousIntensityExponent"s,
"DirectionRatios"s,
"FlowDirection"s,
"SystemType"s,
"IntendedUse"s,
"Scope"s,
"Revision"s,
"DocumentOwner"s,
"Editors"s,
"LastRevisionTime"s,
"ElectronicFormat"s,
"ValidFrom"s,
"ValidUntil"s,
"Confidentiality"s,
"RelatingDocument"s,
"RelatedDocuments"s,
"RelationshipType"s,
"ReferencedDocument"s,
"OverallHeight"s,
"OverallWidth"s,
"OperationType"s,
"UserDefinedOperationType"s,
"LiningDepth"s,
"LiningThickness"s,
"ThresholdDepth"s,
"ThresholdThickness"s,
"TransomThickness"s,
"TransomOffset"s,
"LiningOffset"s,
"ThresholdOffset"s,
"CasingThickness"s,
"CasingDepth"s,
"ShapeAspectStyle"s,
"LiningToPanelOffsetX"s,
"LiningToPanelOffsetY"s,
"PanelDepth"s,
"PanelOperation"s,
"PanelWidth"s,
"PanelPosition"s,
"ConstructionType"s,
"ParameterTakesPrecedence"s,
"Sizeable"s,
"EdgeStart"s,
"EdgeEnd"s,
"EdgeGeometry"s,
"EdgeList"s,
"Tag"s,
"AssemblyPlace"s,
"MethodOfMeasurement"s,
"Quantities"s,
"ElementType"s,
"SemiAxis1"s,
"SemiAxis2"s,
"EventTriggerType"s,
"UserDefinedEventTriggerType"s,
"EventOccurenceTime"s,
"ActualDate"s,
"EarlyDate"s,
"LateDate"s,
"ScheduleDate"s,
"Properties"s,
"RelatingReference"s,
"RelatedResourceObjects"s,
"ExtrudedDirection"s,
"EndSweptArea"s,
"Bounds"s,
"FbsmFaces"s,
"Bound"s,
"Orientation"s,
"FaceSurface"s,
"TensionFailureX"s,
"TensionFailureY"s,
"TensionFailureZ"s,
"CompressionFailureX"s,
"CompressionFailureY"s,
"CompressionFailureZ"s,
"FillStyles"s,
"ModelorDraughting"s,
"HatchLineAppearance"s,
"StartOfNextHatchLine"s,
"PointOfReferenceHatchLine"s,
"PatternStart"s,
"HatchLineAngle"s,
"TilingPattern"s,
"Tiles"s,
"TilingScale"s,
"Directrix"s,
"StartParam"s,
"EndParam"s,
"FixedReference"s,
"CoordinateSpaceDimension"s,
"Precision"s,
"WorldCoordinateSystem"s,
"TrueNorth"s,
"ParentContext"s,
"TargetScale"s,
"TargetView"s,
"UserDefinedTargetView"s,
"UAxes"s,
"VAxes"s,
"WAxes"s,
"AxisTag"s,
"AxisCurve"s,
"PlacementLocation"s,
"PlacementRefDirection"s,
"BaseSurface"s,
"AgreementFlag"s,
"FlangeThickness"s,
"FilletRadius"s,
"FlangeEdgeRadius"s,
"FlangeSlope"s,
"URLReference"s,
"MappedTo"s,
"Opacity"s,
"Colours"s,
"ColourIndex"s,
"Points"s,
"CoordIndex"s,
"InnerCoordIndices"s,
"TexCoords"s,
"TexCoordIndex"s,
"Jurisdiction"s,
"ResponsiblePersons"s,
"LastUpdateDate"s,
"Values"s,
"TimeStamp"s,
"ListValues"s,
"EdgeRadius"s,
"LegSlope"s,
"LagValue"s,
"DurationType"s,
"Publisher"s,
"VersionDate"s,
"Language"s,
"ReferencedLibrary"s,
"MainPlaneAngle"s,
"SecondaryPlaneAngle"s,
"LuminousIntensity"s,
"LightDistributionCurve"s,
"DistributionData"s,
"LightColour"s,
"AmbientIntensity"s,
"Intensity"s,
"ColourAppearance"s,
"ColourTemperature"s,
"LuminousFlux"s,
"LightEmissionSource"s,
"LightDistributionDataSource"s,
"ConstantAttenuation"s,
"DistanceAttenuation"s,
"QuadricAttenuation"s,
"ConcentrationExponent"s,
"SpreadAngle"s,
"BeamWidthAngle"s,
"Pnt"s,
"Dir"s,
"PlacementRelTo"s,
"RelativePlacement"s,
"Outer"s,
"Eastings"s,
"Northings"s,
"OrthogonalHeight"s,
"XAxisAbscissa"s,
"XAxisOrdinate"s,
"MappingSource"s,
"MappingTarget"s,
"MaterialClassifications"s,
"ClassifiedMaterial"s,
"Material"s,
"Fraction"s,
"MaterialConstituents"s,
"RepresentedMaterial"s,
"LayerThickness"s,
"IsVentilated"s,
"Priority"s,
"MaterialLayers"s,
"LayerSetName"s,
"ForLayerSet"s,
"LayerSetDirection"s,
"DirectionSense"s,
"OffsetFromReferenceLine"s,
"ReferenceExtent"s,
"OffsetDirection"s,
"OffsetValues"s,
"Materials"s,
"Profile"s,
"MaterialProfiles"s,
"CompositeProfile"s,
"ForProfileSet"s,
"CardinalPoint"s,
"ForProfileEndSet"s,
"CardinalEndPoint"s,
"RelatingMaterial"s,
"RelatedMaterials"s,
"Expression"s,
"ValueComponent"s,
"UnitComponent"s,
"NominalDiameter"s,
"NominalLength"s,
"Benchmark"s,
"ValueSource"s,
"DataValue"s,
"ReferencePath"s,
"Currency"s,
"Dimensions"s,
"BenchmarkValues"s,
"LogicalAggregator"s,
"ObjectiveQualifier"s,
"UserDefinedQualifier"s,
"BasisCurve"s,
"Distance"s,
"Roles"s,
"Addresses"s,
"RelatingOrganization"s,
"RelatedOrganizations"s,
"EdgeElement"s,
"OwningUser"s,
"OwningApplication"s,
"State"s,
"ChangeAction"s,
"LastModifiedDate"s,
"LastModifyingUser"s,
"LastModifyingApplication"s,
"CreationDate"s,
"ReferenceCurve"s,
"LifeCyclePhase"s,
"FrameDepth"s,
"FrameThickness"s,
"FamilyName"s,
"GivenName"s,
"MiddleNames"s,
"PrefixTitles"s,
"SuffixTitles"s,
"ThePerson"s,
"TheOrganization"s,
"HasQuantities"s,
"Discrimination"s,
"Quality"s,
"Height"s,
"ColourComponents"s,
"Pixel"s,
"Placement"s,
"SizeInX"s,
"SizeInY"s,
"PointParameter"s,
"PointParameterU"s,
"PointParameterV"s,
"Polygon"s,
"PolygonalBoundary"s,
"Closed"s,
"Faces"s,
"PnIndex"s,
"InternalLocation"s,
"AddressLines"s,
"PostalBox"s,
"Town"s,
"Region"s,
"PostalCode"s,
"Country"s,
"AssignedItems"s,
"LayerOn"s,
"LayerFrozen"s,
"LayerBlocked"s,
"LayerStyles"s,
"Styles"s,
"ObjectPlacement"s,
"Representation"s,
"Representations"s,
"ProfileType"s,
"ProfileName"s,
"ProfileDefinition"s,
"MapProjection"s,
"MapZone"s,
"MapUnit"s,
"UpperBoundValue"s,
"LowerBoundValue"s,
"SetPointValue"s,
"DependingProperty"s,
"DependantProperty"s,
"EnumerationValues"s,
"EnumerationReference"s,
"PropertyReference"s,
"ApplicableEntity"s,
"NominalValue"s,
"DefiningValues"s,
"DefinedValues"s,
"DefiningUnit"s,
"DefinedUnit"s,
"CurveInterpolation"s,
"ProxyType"s,
"AreaValue"s,
"Formula"s,
"CountValue"s,
"LengthValue"s,
"TimeValue"s,
"VolumeValue"s,
"WeightValue"s,
"WeightsData"s,
"InnerFilletRadius"s,
"OuterFilletRadius"s,
"U1"s,
"V1"s,
"U2"s,
"V2"s,
"Usense"s,
"Vsense"s,
"RecurrenceType"s,
"DayComponent"s,
"WeekdayComponent"s,
"MonthComponent"s,
"Interval"s,
"Occurrences"s,
"TimePeriods"s,
"TypeIdentifier"s,
"AttributeIdentifier"s,
"InstanceName"s,
"ListPositions"s,
"InnerReference"s,
"TimeStep"s,
"TotalCrossSectionArea"s,
"SteelGrade"s,
"BarSurface"s,
"EffectiveDepth"s,
"NominalBarDiameter"s,
"BarCount"s,
"DefinitionType"s,
"ReinforcementSectionDefinitions"s,
"CrossSectionArea"s,
"BarLength"s,
"BendingShapeCode"s,
"BendingParameters"s,
"MeshLength"s,
"MeshWidth"s,
"LongitudinalBarNominalDiameter"s,
"TransverseBarNominalDiameter"s,
"LongitudinalBarCrossSectionArea"s,
"TransverseBarCrossSectionArea"s,
"LongitudinalBarSpacing"s,
"TransverseBarSpacing"s,
"RelatingObject"s,
"RelatedObjects"s,
"RelatedObjectsType"s,
"RelatingActor"s,
"ActingRole"s,
"RelatingControl"s,
"RelatingGroup"s,
"Factor"s,
"RelatingProcess"s,
"QuantityInProcess"s,
"RelatingProduct"s,
"RelatingResource"s,
"RelatingClassification"s,
"Intent"s,
"RelatingConstraint"s,
"RelatingLibrary"s,
"ConnectionGeometry"s,
"RelatingElement"s,
"RelatedElement"s,
"RelatingPriorities"s,
"RelatedPriorities"s,
"RelatedConnectionType"s,
"RelatingConnectionType"s,
"RelatingPort"s,
"RelatedPort"s,
"RealizingElement"s,
"RelatedStructuralActivity"s,
"RelatingStructuralMember"s,
"RelatedStructuralConnection"s,
"AppliedCondition"s,
"AdditionalConditions"s,
"SupportedLength"s,
"ConditionCoordinateSystem"s,
"ConnectionConstraint"s,
"RealizingElements"s,
"ConnectionType"s,
"RelatedElements"s,
"RelatingStructure"s,
"RelatingBuildingElement"s,
"RelatedCoverings"s,
"RelatingSpace"s,
"RelatingContext"s,
"RelatedDefinitions"s,
"RelatingPropertyDefinition"s,
"RelatedPropertySets"s,
"RelatingTemplate"s,
"RelatingType"s,
"RelatingOpeningElement"s,
"RelatedBuildingElement"s,
"RelatedControlElements"s,
"RelatingFlowElement"s,
"InterferenceGeometry"s,
"InterferenceType"s,
"ImpliedOrder"s,
"RelatedFeatureElement"s,
"RelatedProcess"s,
"TimeLag"s,
"SequenceType"s,
"UserDefinedSequenceType"s,
"RelatingSystem"s,
"RelatedBuildings"s,
"PhysicalOrVirtualBoundary"s,
"InternalOrExternalBoundary"s,
"ParentBoundary"s,
"CorrespondingBoundary"s,
"RelatedOpeningElement"s,
"ParamLength"s,
"ContextOfItems"s,
"RepresentationIdentifier"s,
"RepresentationType"s,
"Items"s,
"ContextIdentifier"s,
"ContextType"s,
"MappingOrigin"s,
"MappedRepresentation"s,
"ScheduleWork"s,
"ScheduleUsage"s,
"ScheduleStart"s,
"ScheduleFinish"s,
"ScheduleContour"s,
"LevelingDelay"s,
"IsOverAllocated"s,
"StatusTime"s,
"ActualWork"s,
"ActualUsage"s,
"ActualStart"s,
"ActualFinish"s,
"RemainingWork"s,
"RemainingUsage"s,
"Completion"s,
"Angle"s,
"BottomRadius"s,
"GlobalId"s,
"OwnerHistory"s,
"RoundingRadius"s,
"Prefix"s,
"DataOrigin"s,
"UserDefinedDataOrigin"s,
"SectionType"s,
"StartProfile"s,
"EndProfile"s,
"LongitudinalStartPosition"s,
"LongitudinalEndPosition"s,
"TransversePosition"s,
"ReinforcementRole"s,
"SectionDefinition"s,
"CrossSectionReinforcementDefinitions"s,
"SpineCurve"s,
"CrossSections"s,
"CrossSectionPositions"s,
"ShapeRepresentations"s,
"ProductDefinitional"s,
"PartOfProductDefinitionShape"s,
"SbsmBoundary"s,
"PrimaryMeasureType"s,
"SecondaryMeasureType"s,
"Enumerators"s,
"PrimaryUnit"s,
"SecondaryUnit"s,
"AccessState"s,
"RefLatitude"s,
"RefLongitude"s,
"RefElevation"s,
"LandTitleNumber"s,
"SiteAddress"s,
"SlippageX"s,
"SlippageY"s,
"SlippageZ"s,
"ElevationWithFlooring"s,
"CompositionType"s,
"NumberOfRisers"s,
"NumberOfTreads"s,
"RiserHeight"s,
"TreadLength"s,
"DestabilizingLoad"s,
"AppliedLoad"s,
"GlobalOrLocal"s,
"OrientationOf2DPlane"s,
"LoadedBy"s,
"HasResults"s,
"SharedPlacement"s,
"ProjectedOrTrue"s,
"SelfWeightCoefficients"s,
"Locations"s,
"ActionType"s,
"ActionSource"s,
"Coefficient"s,
"LinearForceX"s,
"LinearForceY"s,
"LinearForceZ"s,
"LinearMomentX"s,
"LinearMomentY"s,
"LinearMomentZ"s,
"PlanarForceX"s,
"PlanarForceY"s,
"PlanarForceZ"s,
"DisplacementX"s,
"DisplacementY"s,
"DisplacementZ"s,
"RotationalDisplacementRX"s,
"RotationalDisplacementRY"s,
"RotationalDisplacementRZ"s,
"Distortion"s,
"ForceX"s,
"ForceY"s,
"ForceZ"s,
"MomentX"s,
"MomentY"s,
"MomentZ"s,
"WarpingMoment"s,
"DeltaTConstant"s,
"DeltaTY"s,
"DeltaTZ"s,
"TheoryType"s,
"ResultForLoadGroup"s,
"IsLinear"s,
"Item"s,
"ParentEdge"s,
"Curve3D"s,
"AssociatedGeometry"s,
"MasterRepresentation"s,
"ReferenceSurface"s,
"AxisPosition"s,
"SurfaceReinforcement1"s,
"SurfaceReinforcement2"s,
"ShearReinforcement"s,
"Side"s,
"DiffuseTransmissionColour"s,
"DiffuseReflectionColour"s,
"TransmissionColour"s,
"ReflectanceColour"s,
"RefractionIndex"s,
"DispersionFactor"s,
"DiffuseColour"s,
"ReflectionColour"s,
"SpecularColour"s,
"SpecularHighlight"s,
"ReflectanceMethod"s,
"SurfaceColour"s,
"Transparency"s,
"Textures"s,
"RepeatS"s,
"RepeatT"s,
"Mode"s,
"TextureTransform"s,
"Parameter"s,
"SweptArea"s,
"InnerRadius"s,
"SweptCurve"s,
"FlangeWidth"s,
"WebEdgeRadius"s,
"WebSlope"s,
"Rows"s,
"Columns"s,
"RowCells"s,
"IsHeading"s,
"WorkMethod"s,
"IsMilestone"s,
"TaskTime"s,
"ScheduleDuration"s,
"EarlyStart"s,
"EarlyFinish"s,
"LateStart"s,
"LateFinish"s,
"FreeFloat"s,
"TotalFloat"s,
"IsCritical"s,
"ActualDuration"s,
"RemainingTime"s,
"Recurrence"s,
"TelephoneNumbers"s,
"FacsimileNumbers"s,
"PagerNumber"s,
"ElectronicMailAddresses"s,
"WWWHomePageURL"s,
"MessagingIDs"s,
"TensionForce"s,
"PreStress"s,
"FrictionCoefficient"s,
"AnchorageSlip"s,
"MinCurvatureRadius"s,
"SheathDiameter"s,
"Literal"s,
"Path"s,
"Extent"s,
"BoxAlignment"s,
"TextCharacterAppearance"s,
"TextStyle"s,
"TextFontStyle"s,
"FontFamily"s,
"FontStyle"s,
"FontVariant"s,
"FontWeight"s,
"FontSize"s,
"Colour"s,
"BackgroundColour"s,
"TextIndent"s,
"TextAlign"s,
"TextDecoration"s,
"LetterSpacing"s,
"WordSpacing"s,
"TextTransform"s,
"LineHeight"s,
"Maps"s,
"Vertices"s,
"TexCoordsList"s,
"StartTime"s,
"EndTime"s,
"TimeSeriesDataType"s,
"MajorRadius"s,
"MinorRadius"s,
"BottomXDim"s,
"TopXDim"s,
"TopXOffset"s,
"Normals"s,
"Trim1"s,
"Trim2"s,
"SenseAgreement"s,
"ApplicableOccurrence"s,
"HasPropertySets"s,
"ProcessType"s,
"RepresentationMaps"s,
"ResourceType"s,
"Units"s,
"Magnitude"s,
"LoopVertex"s,
"VertexGeometry"s,
"IntersectingAxes"s,
"OffsetDistances"s,
"PartitioningType"s,
"UserDefinedPartitioningType"s,
"MullionThickness"s,
"FirstTransomOffset"s,
"SecondTransomOffset"s,
"FirstMullionOffset"s,
"SecondMullionOffset"s,
"WorkingTimes"s,
"ExceptionTimes"s,
"Creators"s,
"Duration"s,
"FinishTime"s,
"RecurrencePattern"s,
"Start"s,
"Finish"s,
"IsActingUpon"s,
"HasExternalReference"s,
"OfPerson"s,
"OfOrganization"s,
"ContainedInStructure"s,
"HasExternalReferences"s,
"ApprovedObjects"s,
"ApprovedResources"s,
"IsRelatedWith"s,
"Relates"s,
"ClassificationForObjects"s,
"HasReferences"s,
"ClassificationRefForObjects"s,
"UsingCurves"s,
"PropertiesForConstraint"s,
"IsDefinedBy"s,
"Declares"s,
"Controls"s,
"HasCoordinateOperation"s,
"CoversSpaces"s,
"CoversElements"s,
"AssignedToFlowElement"s,
"HasPorts"s,
"HasControlElements"s,
"DocumentInfoForObjects"s,
"HasDocumentReferences"s,
"IsPointedTo"s,
"IsPointer"s,
"DocumentRefForObjects"s,
"FillsVoids"s,
"ConnectedTo"s,
"IsInterferedByElements"s,
"InterferesElements"s,
"HasProjections"s,
"ReferencedInStructures"s,
"HasOpenings"s,
"IsConnectionRealization"s,
"ProvidesBoundaries"s,
"ConnectedFrom"s,
"HasCoverings"s,
"ExternalReferenceForResources"s,
"BoundedBy"s,
"HasTextureMaps"s,
"ProjectsElements"s,
"VoidsElements"s,
"HasSubContexts"s,
"PartOfW"s,
"PartOfV"s,
"PartOfU"s,
"HasIntersections"s,
"IsGroupedBy"s,
"ToFaceSet"s,
"LibraryInfoForObjects"s,
"HasLibraryReferences"s,
"LibraryRefForObjects"s,
"HasRepresentation"s,
"RelatesTo"s,
"ToMaterialConstituentSet"s,
"AssociatedTo"s,
"ToMaterialLayerSet"s,
"ToMaterialProfileSet"s,
"IsDeclaredBy"s,
"IsTypedBy"s,
"HasAssignments"s,
"Nests"s,
"IsNestedBy"s,
"HasContext"s,
"IsDecomposedBy"s,
"Decomposes"s,
"HasAssociations"s,
"PlacesObject"s,
"ReferencedByPlacements"s,
"HasFillings"s,
"IsRelatedBy"s,
"Engages"s,
"EngagedIn"s,
"PartOfComplex"s,
"ContainedIn"s,
"IsPredecessorTo"s,
"IsSuccessorFrom"s,
"OperatesOn"s,
"ReferencedBy"s,
"ShapeOfProduct"s,
"HasShapeAspects"s,
"PartOfPset"s,
"PropertyForDependance"s,
"PropertyDependsOn"s,
"HasConstraints"s,
"HasApprovals"s,
"DefinesType"s,
"DefinesOccurrence"s,
"Defines"s,
"PartOfComplexTemplate"s,
"PartOfPsetTemplate"s,
"Corresponds"s,
"RepresentationMap"s,
"LayerAssignments"s,
"OfProductRepresentation"s,
"RepresentationsInContext"s,
"LayerAssignment"s,
"StyledByItem"s,
"MapUsage"s,
"ResourceOf"s,
"OfShapeAspect"s,
"ContainsElements"s,
"ServicedBySystems"s,
"ReferencesElements"s,
"AssignedToStructuralItem"s,
"ConnectsStructuralMembers"s,
"AssignedStructuralActivity"s,
"SourceOfResultGroup"s,
"LoadGroupFor"s,
"ConnectedBy"s,
"ResultGroupFor"s,
"IsMappedBy"s,
"UsedInStyles"s,
"ServicesBuildings"s,
"HasColours"s,
"HasTextures"s,
"Types"s,
"IFC4"s};

#if defined(__clang__)
__attribute__((optnone))
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC4_populate_schema() {
    IFC4_IfcAbsorbedDoseMeasure_type = new type_declaration(strings[0], 0, new simple_type(simple_type::real_type));
    IFC4_IfcAccelerationMeasure_type = new type_declaration(strings[1], 1, new simple_type(simple_type::real_type));
    IFC4_IfcActionRequestTypeEnum_type = new enumeration_type(strings[2], 3, {
        strings[3],
        strings[4],
        strings[5],
        strings[6],
        strings[7],
        strings[8],
        strings[9]
    });
    IFC4_IfcActionSourceTypeEnum_type = new enumeration_type(strings[10], 4, {
        strings[11],
        strings[12],
        strings[13],
        strings[14],
        strings[15],
        strings[16],
        strings[17],
        strings[18],
        strings[19],
        strings[20],
        strings[21],
        strings[22],
        strings[23],
        strings[24],
        strings[25],
        strings[26],
        strings[27],
        strings[28],
        strings[29],
        strings[30],
        strings[31],
        strings[32],
        strings[33],
        strings[34],
        strings[35],
        strings[8],
        strings[9]
    });
    IFC4_IfcActionTypeEnum_type = new enumeration_type(strings[36], 5, {
        strings[37],
        strings[38],
        strings[39],
        strings[8],
        strings[9]
    });
    IFC4_IfcActuatorTypeEnum_type = new enumeration_type(strings[40], 11, {
        strings[41],
        strings[42],
        strings[43],
        strings[44],
        strings[45],
        strings[8],
        strings[9]
    });
    IFC4_IfcAddressTypeEnum_type = new enumeration_type(strings[46], 13, {
        strings[47],
        strings[48],
        strings[49],
        strings[50],
        strings[8]
    });
    IFC4_IfcAirTerminalBoxTypeEnum_type = new enumeration_type(strings[51], 20, {
        strings[52],
        strings[53],
        strings[54],
        strings[8],
        strings[9]
    });
    IFC4_IfcAirTerminalTypeEnum_type = new enumeration_type(strings[55], 22, {
        strings[56],
        strings[57],
        strings[58],
        strings[59],
        strings[8],
        strings[9]
    });
    IFC4_IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type(strings[60], 25, {
        strings[61],
        strings[62],
        strings[63],
        strings[64],
        strings[65],
        strings[66],
        strings[67],
        strings[68],
        strings[69],
        strings[8],
        strings[9]
    });
    IFC4_IfcAlarmTypeEnum_type = new enumeration_type(strings[70], 28, {
        strings[71],
        strings[72],
        strings[73],
        strings[74],
        strings[75],
        strings[76],
        strings[8],
        strings[9]
    });
    IFC4_IfcAmountOfSubstanceMeasure_type = new type_declaration(strings[77], 29, new simple_type(simple_type::real_type));
    IFC4_IfcAnalysisModelTypeEnum_type = new enumeration_type(strings[78], 30, {
        strings[79],
        strings[80],
        strings[81],
        strings[8],
        strings[9]
    });
    IFC4_IfcAnalysisTheoryTypeEnum_type = new enumeration_type(strings[82], 31, {
        strings[83],
        strings[84],
        strings[85],
        strings[86],
        strings[8],
        strings[9]
    });
    IFC4_IfcAngularVelocityMeasure_type = new type_declaration(strings[87], 32, new simple_type(simple_type::real_type));
    IFC4_IfcAreaDensityMeasure_type = new type_declaration(strings[88], 44, new simple_type(simple_type::real_type));
    IFC4_IfcAreaMeasure_type = new type_declaration(strings[89], 45, new simple_type(simple_type::real_type));
    IFC4_IfcArithmeticOperatorEnum_type = new enumeration_type(strings[90], 46, {
        strings[91],
        strings[92],
        strings[93],
        strings[94]
    });
    IFC4_IfcAssemblyPlaceEnum_type = new enumeration_type(strings[95], 47, {
        strings[48],
        strings[96],
        strings[9]
    });
    IFC4_IfcAudioVisualApplianceTypeEnum_type = new enumeration_type(strings[97], 52, {
        strings[98],
        strings[99],
        strings[100],
        strings[101],
        strings[102],
        strings[103],
        strings[104],
        strings[105],
        strings[106],
        strings[107],
        strings[108],
        strings[8],
        strings[9]
    });
    IFC4_IfcBSplineCurveForm_type = new enumeration_type(strings[109], 86, {
        strings[110],
        strings[111],
        strings[112],
        strings[113],
        strings[114],
        strings[115]
    });
    IFC4_IfcBSplineSurfaceForm_type = new enumeration_type(strings[116], 89, {
        strings[117],
        strings[118],
        strings[119],
        strings[120],
        strings[121],
        strings[122],
        strings[123],
        strings[124],
        strings[125],
        strings[126],
        strings[115]
    });
    IFC4_IfcBeamTypeEnum_type = new enumeration_type(strings[127], 60, {
        strings[128],
        strings[129],
        strings[130],
        strings[131],
        strings[132],
        strings[133],
        strings[8],
        strings[9]
    });
    IFC4_IfcBenchmarkEnum_type = new enumeration_type(strings[134], 61, {
        strings[135],
        strings[136],
        strings[137],
        strings[138],
        strings[139],
        strings[140],
        strings[141],
        strings[142],
        strings[143],
        strings[144]
    });
    IFC4_IfcBinary_type = new type_declaration(strings[145], 63, new simple_type(simple_type::binary_type));
    IFC4_IfcBoilerTypeEnum_type = new enumeration_type(strings[146], 68, {
        strings[147],
        strings[148],
        strings[8],
        strings[9]
    });
    IFC4_IfcBoolean_type = new type_declaration(strings[149], 69, new simple_type(simple_type::boolean_type));
    IFC4_IfcBooleanOperator_type = new enumeration_type(strings[150], 72, {
        strings[151],
        strings[152],
        strings[153]
    });
    IFC4_IfcBuildingElementPartTypeEnum_type = new enumeration_type(strings[154], 95, {
        strings[155],
        strings[156],
        strings[8],
        strings[9]
    });
    IFC4_IfcBuildingElementProxyTypeEnum_type = new enumeration_type(strings[157], 98, {
        strings[158],
        strings[159],
        strings[160],
        strings[161],
        strings[162],
        strings[8],
        strings[9]
    });
    IFC4_IfcBuildingSystemTypeEnum_type = new enumeration_type(strings[163], 102, {
        strings[164],
        strings[165],
        strings[166],
        strings[167],
        strings[168],
        strings[23],
        strings[8],
        strings[9]
    });
    IFC4_IfcBurnerTypeEnum_type = new enumeration_type(strings[169], 105, {
        strings[8],
        strings[9]
    });
    IFC4_IfcCableCarrierFittingTypeEnum_type = new enumeration_type(strings[170], 108, {
        strings[171],
        strings[172],
        strings[173],
        strings[174],
        strings[8],
        strings[9]
    });
    IFC4_IfcCableCarrierSegmentTypeEnum_type = new enumeration_type(strings[175], 111, {
        strings[176],
        strings[177],
        strings[178],
        strings[179],
        strings[8],
        strings[9]
    });
    IFC4_IfcCableFittingTypeEnum_type = new enumeration_type(strings[180], 114, {
        strings[181],
        strings[182],
        strings[183],
        strings[184],
        strings[185],
        strings[8],
        strings[9]
    });
    IFC4_IfcCableSegmentTypeEnum_type = new enumeration_type(strings[186], 117, {
        strings[187],
        strings[188],
        strings[189],
        strings[190],
        strings[8],
        strings[9]
    });
    IFC4_IfcCardinalPointReference_type = new type_declaration(strings[191], 118, new simple_type(simple_type::integer_type));
    IFC4_IfcChangeActionEnum_type = new enumeration_type(strings[192], 129, {
        strings[193],
        strings[194],
        strings[195],
        strings[196],
        strings[9]
    });
    IFC4_IfcChillerTypeEnum_type = new enumeration_type(strings[197], 132, {
        strings[198],
        strings[199],
        strings[200],
        strings[8],
        strings[9]
    });
    IFC4_IfcChimneyTypeEnum_type = new enumeration_type(strings[201], 135, {
        strings[8],
        strings[9]
    });
    IFC4_IfcCoilTypeEnum_type = new enumeration_type(strings[202], 148, {
        strings[203],
        strings[204],
        strings[205],
        strings[206],
        strings[207],
        strings[208],
        strings[209],
        strings[8],
        strings[9]
    });
    IFC4_IfcColumnTypeEnum_type = new enumeration_type(strings[210], 157, {
        strings[211],
        strings[212],
        strings[8],
        strings[9]
    });
    IFC4_IfcCommunicationsApplianceTypeEnum_type = new enumeration_type(strings[213], 160, {
        strings[214],
        strings[215],
        strings[4],
        strings[216],
        strings[217],
        strings[218],
        strings[219],
        strings[220],
        strings[221],
        strings[222],
        strings[223],
        strings[224],
        strings[8],
        strings[9]
    });
    IFC4_IfcComplexNumber_type = new type_declaration(strings[225], 161, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IFC4_IfcComplexPropertyTemplateTypeEnum_type = new enumeration_type(strings[226], 164, {
        strings[227],
        strings[228]
    });
    IFC4_IfcCompoundPlaneAngleMeasure_type = new type_declaration(strings[229], 169, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
    IFC4_IfcCompressorTypeEnum_type = new enumeration_type(strings[230], 172, {
        strings[231],
        strings[232],
        strings[233],
        strings[234],
        strings[235],
        strings[236],
        strings[237],
        strings[238],
        strings[239],
        strings[240],
        strings[241],
        strings[242],
        strings[243],
        strings[244],
        strings[245],
        strings[8],
        strings[9]
    });
    IFC4_IfcCondenserTypeEnum_type = new enumeration_type(strings[246], 175, {
        strings[198],
        strings[247],
        strings[199],
        strings[248],
        strings[249],
        strings[250],
        strings[251],
        strings[8],
        strings[9]
    });
    IFC4_IfcConnectionTypeEnum_type = new enumeration_type(strings[252], 183, {
        strings[253],
        strings[254],
        strings[255],
        strings[9]
    });
    IFC4_IfcConstraintEnum_type = new enumeration_type(strings[256], 186, {
        strings[257],
        strings[258],
        strings[259],
        strings[8],
        strings[9]
    });
    IFC4_IfcConstructionEquipmentResourceTypeEnum_type = new enumeration_type(strings[260], 189, {
        strings[261],
        strings[262],
        strings[263],
        strings[264],
        strings[265],
        strings[266],
        strings[267],
        strings[268],
        strings[8],
        strings[9]
    });
    IFC4_IfcConstructionMaterialResourceTypeEnum_type = new enumeration_type(strings[269], 192, {
        strings[270],
        strings[271],
        strings[272],
        strings[273],
        strings[274],
        strings[275],
        strings[276],
        strings[277],
        strings[278],
        strings[9],
        strings[8]
    });
    IFC4_IfcConstructionProductResourceTypeEnum_type = new enumeration_type(strings[279], 195, {
        strings[280],
        strings[281],
        strings[8],
        strings[9]
    });
    IFC4_IfcContextDependentMeasure_type = new type_declaration(strings[282], 199, new simple_type(simple_type::real_type));
    IFC4_IfcControllerTypeEnum_type = new enumeration_type(strings[283], 204, {
        strings[284],
        strings[285],
        strings[286],
        strings[287],
        strings[288],
        strings[8],
        strings[9]
    });
    IFC4_IfcCooledBeamTypeEnum_type = new enumeration_type(strings[289], 209, {
        strings[290],
        strings[291],
        strings[8],
        strings[9]
    });
    IFC4_IfcCoolingTowerTypeEnum_type = new enumeration_type(strings[292], 212, {
        strings[293],
        strings[294],
        strings[295],
        strings[8],
        strings[9]
    });
    IFC4_IfcCostItemTypeEnum_type = new enumeration_type(strings[296], 217, {
        strings[8],
        strings[9]
    });
    IFC4_IfcCostScheduleTypeEnum_type = new enumeration_type(strings[297], 219, {
        strings[298],
        strings[299],
        strings[300],
        strings[301],
        strings[302],
        strings[303],
        strings[304],
        strings[8],
        strings[9]
    });
    IFC4_IfcCountMeasure_type = new type_declaration(strings[305], 221, new simple_type(simple_type::number_type));
    IFC4_IfcCoveringTypeEnum_type = new enumeration_type(strings[306], 224, {
        strings[307],
        strings[308],
        strings[309],
        strings[310],
        strings[311],
        strings[312],
        strings[155],
        strings[313],
        strings[314],
        strings[315],
        strings[8],
        strings[9]
    });
    IFC4_IfcCrewResourceTypeEnum_type = new enumeration_type(strings[316], 227, {
        strings[47],
        strings[48],
        strings[8],
        strings[9]
    });
    IFC4_IfcCurtainWallTypeEnum_type = new enumeration_type(strings[317], 235, {
        strings[8],
        strings[9]
    });
    IFC4_IfcCurvatureMeasure_type = new type_declaration(strings[318], 236, new simple_type(simple_type::real_type));
    IFC4_IfcCurveInterpolationEnum_type = new enumeration_type(strings[319], 241, {
        strings[320],
        strings[321],
        strings[322],
        strings[9]
    });
    IFC4_IfcDamperTypeEnum_type = new enumeration_type(strings[323], 252, {
        strings[324],
        strings[325],
        strings[326],
        strings[327],
        strings[328],
        strings[329],
        strings[330],
        strings[331],
        strings[332],
        strings[333],
        strings[334],
        strings[8],
        strings[9]
    });
    IFC4_IfcDataOriginEnum_type = new enumeration_type(strings[335], 253, {
        strings[336],
        strings[337],
        strings[338],
        strings[8],
        strings[9]
    });
    IFC4_IfcDate_type = new type_declaration(strings[339], 254, new simple_type(simple_type::string_type));
    IFC4_IfcDateTime_type = new type_declaration(strings[340], 255, new simple_type(simple_type::string_type));
    IFC4_IfcDayInMonthNumber_type = new type_declaration(strings[341], 256, new simple_type(simple_type::integer_type));
    IFC4_IfcDayInWeekNumber_type = new type_declaration(strings[342], 257, new simple_type(simple_type::integer_type));
    IFC4_IfcDerivedUnitEnum_type = new enumeration_type(strings[343], 263, {
        strings[344],
        strings[345],
        strings[346],
        strings[347],
        strings[348],
        strings[349],
        strings[350],
        strings[351],
        strings[352],
        strings[353],
        strings[354],
        strings[355],
        strings[356],
        strings[357],
        strings[358],
        strings[359],
        strings[360],
        strings[361],
        strings[362],
        strings[363],
        strings[364],
        strings[365],
        strings[366],
        strings[367],
        strings[368],
        strings[369],
        strings[370],
        strings[371],
        strings[372],
        strings[373],
        strings[374],
        strings[375],
        strings[376],
        strings[377],
        strings[378],
        strings[379],
        strings[380],
        strings[381],
        strings[382],
        strings[383],
        strings[384],
        strings[385],
        strings[386],
        strings[387],
        strings[388],
        strings[389],
        strings[390],
        strings[391],
        strings[392],
        strings[393],
        strings[394],
        strings[395],
        strings[8]
    });
    IFC4_IfcDescriptiveMeasure_type = new type_declaration(strings[396], 264, new simple_type(simple_type::string_type));
    IFC4_IfcDimensionCount_type = new type_declaration(strings[397], 266, new simple_type(simple_type::integer_type));
    IFC4_IfcDirectionSenseEnum_type = new enumeration_type(strings[398], 268, {
        strings[399],
        strings[400]
    });
    IFC4_IfcDiscreteAccessoryTypeEnum_type = new enumeration_type(strings[401], 271, {
        strings[402],
        strings[403],
        strings[404],
        strings[8],
        strings[9]
    });
    IFC4_IfcDistributionChamberElementTypeEnum_type = new enumeration_type(strings[405], 274, {
        strings[406],
        strings[407],
        strings[408],
        strings[409],
        strings[410],
        strings[411],
        strings[412],
        strings[413],
        strings[8],
        strings[9]
    });
    IFC4_IfcDistributionPortTypeEnum_type = new enumeration_type(strings[414], 283, {
        strings[415],
        strings[416],
        strings[417],
        strings[418],
        strings[8],
        strings[9]
    });
    IFC4_IfcDistributionSystemEnum_type = new enumeration_type(strings[419], 285, {
        strings[420],
        strings[421],
        strings[422],
        strings[423],
        strings[424],
        strings[425],
        strings[426],
        strings[427],
        strings[428],
        strings[429],
        strings[430],
        strings[431],
        strings[432],
        strings[433],
        strings[434],
        strings[435],
        strings[436],
        strings[437],
        strings[438],
        strings[273],
        strings[439],
        strings[440],
        strings[264],
        strings[265],
        strings[441],
        strings[442],
        strings[443],
        strings[444],
        strings[445],
        strings[446],
        strings[447],
        strings[448],
        strings[449],
        strings[450],
        strings[451],
        strings[107],
        strings[452],
        strings[453],
        strings[454],
        strings[455],
        strings[456],
        strings[457],
        strings[8],
        strings[9]
    });
    IFC4_IfcDocumentConfidentialityEnum_type = new enumeration_type(strings[458], 286, {
        strings[459],
        strings[460],
        strings[461],
        strings[462],
        strings[8],
        strings[9]
    });
    IFC4_IfcDocumentStatusEnum_type = new enumeration_type(strings[463], 291, {
        strings[464],
        strings[465],
        strings[466],
        strings[467],
        strings[9]
    });
    IFC4_IfcDoorPanelOperationEnum_type = new enumeration_type(strings[468], 294, {
        strings[469],
        strings[470],
        strings[471],
        strings[472],
        strings[473],
        strings[474],
        strings[475],
        strings[8],
        strings[9]
    });
    IFC4_IfcDoorPanelPositionEnum_type = new enumeration_type(strings[476], 295, {
        strings[477],
        strings[478],
        strings[479],
        strings[9]
    });
    IFC4_IfcDoorStyleConstructionEnum_type = new enumeration_type(strings[480], 299, {
        strings[481],
        strings[482],
        strings[483],
        strings[278],
        strings[484],
        strings[485],
        strings[277],
        strings[8],
        strings[9]
    });
    IFC4_IfcDoorStyleOperationEnum_type = new enumeration_type(strings[486], 300, {
        strings[487],
        strings[488],
        strings[489],
        strings[490],
        strings[491],
        strings[492],
        strings[493],
        strings[494],
        strings[495],
        strings[496],
        strings[497],
        strings[498],
        strings[499],
        strings[500],
        strings[473],
        strings[474],
        strings[8],
        strings[9]
    });
    IFC4_IfcDoorTypeEnum_type = new enumeration_type(strings[501], 302, {
        strings[502],
        strings[503],
        strings[504],
        strings[8],
        strings[9]
    });
    IFC4_IfcDoorTypeOperationEnum_type = new enumeration_type(strings[505], 303, {
        strings[487],
        strings[488],
        strings[489],
        strings[490],
        strings[491],
        strings[492],
        strings[493],
        strings[494],
        strings[495],
        strings[496],
        strings[497],
        strings[498],
        strings[499],
        strings[500],
        strings[473],
        strings[474],
        strings[506],
        strings[507],
        strings[8],
        strings[9]
    });
    IFC4_IfcDoseEquivalentMeasure_type = new type_declaration(strings[508], 304, new simple_type(simple_type::real_type));
    IFC4_IfcDuctFittingTypeEnum_type = new enumeration_type(strings[509], 309, {
        strings[171],
        strings[181],
        strings[182],
        strings[183],
        strings[184],
        strings[510],
        strings[185],
        strings[8],
        strings[9]
    });
    IFC4_IfcDuctSegmentTypeEnum_type = new enumeration_type(strings[511], 312, {
        strings[512],
        strings[513],
        strings[8],
        strings[9]
    });
    IFC4_IfcDuctSilencerTypeEnum_type = new enumeration_type(strings[514], 315, {
        strings[515],
        strings[516],
        strings[517],
        strings[8],
        strings[9]
    });
    IFC4_IfcDuration_type = new type_declaration(strings[518], 316, new simple_type(simple_type::string_type));
    IFC4_IfcDynamicViscosityMeasure_type = new type_declaration(strings[519], 317, new simple_type(simple_type::real_type));
    IFC4_IfcElectricApplianceTypeEnum_type = new enumeration_type(strings[520], 323, {
        strings[521],
        strings[522],
        strings[523],
        strings[524],
        strings[525],
        strings[526],
        strings[527],
        strings[528],
        strings[529],
        strings[530],
        strings[531],
        strings[532],
        strings[533],
        strings[534],
        strings[535],
        strings[536],
        strings[8],
        strings[9]
    });
    IFC4_IfcElectricCapacitanceMeasure_type = new type_declaration(strings[537], 324, new simple_type(simple_type::real_type));
    IFC4_IfcElectricChargeMeasure_type = new type_declaration(strings[538], 325, new simple_type(simple_type::real_type));
    IFC4_IfcElectricConductanceMeasure_type = new type_declaration(strings[539], 326, new simple_type(simple_type::real_type));
    IFC4_IfcElectricCurrentMeasure_type = new type_declaration(strings[540], 327, new simple_type(simple_type::real_type));
    IFC4_IfcElectricDistributionBoardTypeEnum_type = new enumeration_type(strings[541], 330, {
        strings[542],
        strings[543],
        strings[544],
        strings[545],
        strings[8],
        strings[9]
    });
    IFC4_IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type(strings[546], 333, {
        strings[547],
        strings[548],
        strings[549],
        strings[550],
        strings[551],
        strings[8],
        strings[9]
    });
    IFC4_IfcElectricGeneratorTypeEnum_type = new enumeration_type(strings[552], 336, {
        strings[553],
        strings[554],
        strings[555],
        strings[8],
        strings[9]
    });
    IFC4_IfcElectricMotorTypeEnum_type = new enumeration_type(strings[556], 339, {
        strings[557],
        strings[558],
        strings[559],
        strings[560],
        strings[561],
        strings[8],
        strings[9]
    });
    IFC4_IfcElectricResistanceMeasure_type = new type_declaration(strings[562], 340, new simple_type(simple_type::real_type));
    IFC4_IfcElectricTimeControlTypeEnum_type = new enumeration_type(strings[563], 343, {
        strings[564],
        strings[565],
        strings[566],
        strings[8],
        strings[9]
    });
    IFC4_IfcElectricVoltageMeasure_type = new type_declaration(strings[567], 344, new simple_type(simple_type::real_type));
    IFC4_IfcElementAssemblyTypeEnum_type = new enumeration_type(strings[568], 349, {
        strings[569],
        strings[570],
        strings[571],
        strings[572],
        strings[573],
        strings[574],
        strings[575],
        strings[576],
        strings[577],
        strings[8],
        strings[9]
    });
    IFC4_IfcElementCompositionEnum_type = new enumeration_type(strings[578], 352, {
        strings[158],
        strings[159],
        strings[160]
    });
    IFC4_IfcEnergyMeasure_type = new type_declaration(strings[579], 359, new simple_type(simple_type::real_type));
    IFC4_IfcEngineTypeEnum_type = new enumeration_type(strings[580], 362, {
        strings[581],
        strings[582],
        strings[8],
        strings[9]
    });
    IFC4_IfcEvaporativeCoolerTypeEnum_type = new enumeration_type(strings[583], 365, {
        strings[584],
        strings[585],
        strings[586],
        strings[587],
        strings[588],
        strings[589],
        strings[590],
        strings[591],
        strings[592],
        strings[8],
        strings[9]
    });
    IFC4_IfcEvaporatorTypeEnum_type = new enumeration_type(strings[593], 368, {
        strings[594],
        strings[595],
        strings[596],
        strings[597],
        strings[598],
        strings[599],
        strings[8],
        strings[9]
    });
    IFC4_IfcEventTriggerTypeEnum_type = new enumeration_type(strings[600], 371, {
        strings[601],
        strings[602],
        strings[603],
        strings[604],
        strings[8],
        strings[9]
    });
    IFC4_IfcEventTypeEnum_type = new enumeration_type(strings[605], 373, {
        strings[606],
        strings[607],
        strings[608],
        strings[8],
        strings[9]
    });
    IFC4_IfcExternalSpatialElementTypeEnum_type = new enumeration_type(strings[609], 382, {
        strings[610],
        strings[611],
        strings[612],
        strings[613],
        strings[8],
        strings[9]
    });
    IFC4_IfcFanTypeEnum_type = new enumeration_type(strings[614], 396, {
        strings[615],
        strings[616],
        strings[617],
        strings[618],
        strings[619],
        strings[620],
        strings[621],
        strings[8],
        strings[9]
    });
    IFC4_IfcFastenerTypeEnum_type = new enumeration_type(strings[622], 399, {
        strings[623],
        strings[624],
        strings[625],
        strings[8],
        strings[9]
    });
    IFC4_IfcFilterTypeEnum_type = new enumeration_type(strings[626], 409, {
        strings[627],
        strings[628],
        strings[629],
        strings[630],
        strings[631],
        strings[632],
        strings[8],
        strings[9]
    });
    IFC4_IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type(strings[633], 412, {
        strings[634],
        strings[635],
        strings[636],
        strings[637],
        strings[638],
        strings[8],
        strings[9]
    });
    IFC4_IfcFlowDirectionEnum_type = new enumeration_type(strings[639], 416, {
        strings[640],
        strings[641],
        strings[642],
        strings[9]
    });
    IFC4_IfcFlowInstrumentTypeEnum_type = new enumeration_type(strings[643], 421, {
        strings[644],
        strings[645],
        strings[646],
        strings[647],
        strings[648],
        strings[649],
        strings[650],
        strings[651],
        strings[8],
        strings[9]
    });
    IFC4_IfcFlowMeterTypeEnum_type = new enumeration_type(strings[652], 424, {
        strings[653],
        strings[654],
        strings[655],
        strings[656],
        strings[8],
        strings[9]
    });
    IFC4_IfcFontStyle_type = new type_declaration(strings[657], 435, new simple_type(simple_type::string_type));
    IFC4_IfcFontVariant_type = new type_declaration(strings[658], 436, new simple_type(simple_type::string_type));
    IFC4_IfcFontWeight_type = new type_declaration(strings[659], 437, new simple_type(simple_type::string_type));
    IFC4_IfcFootingTypeEnum_type = new enumeration_type(strings[660], 440, {
        strings[661],
        strings[662],
        strings[663],
        strings[664],
        strings[665],
        strings[8],
        strings[9]
    });
    IFC4_IfcForceMeasure_type = new type_declaration(strings[666], 441, new simple_type(simple_type::real_type));
    IFC4_IfcFrequencyMeasure_type = new type_declaration(strings[667], 442, new simple_type(simple_type::real_type));
    IFC4_IfcFurnitureTypeEnum_type = new enumeration_type(strings[668], 447, {
        strings[669],
        strings[670],
        strings[671],
        strings[672],
        strings[673],
        strings[674],
        strings[675],
        strings[8],
        strings[9]
    });
    IFC4_IfcGeographicElementTypeEnum_type = new enumeration_type(strings[676], 450, {
        strings[677],
        strings[8],
        strings[9]
    });
    IFC4_IfcGeometricProjectionEnum_type = new enumeration_type(strings[678], 452, {
        strings[679],
        strings[680],
        strings[681],
        strings[682],
        strings[683],
        strings[684],
        strings[685],
        strings[8],
        strings[9]
    });
    IFC4_IfcGlobalOrLocalEnum_type = new enumeration_type(strings[686], 459, {
        strings[687],
        strings[688]
    });
    IFC4_IfcGloballyUniqueId_type = new type_declaration(strings[689], 458, new simple_type(simple_type::string_type));
    IFC4_IfcGridTypeEnum_type = new enumeration_type(strings[690], 464, {
        strings[516],
        strings[691],
        strings[692],
        strings[693],
        strings[8],
        strings[9]
    });
    IFC4_IfcHeatExchangerTypeEnum_type = new enumeration_type(strings[694], 470, {
        strings[695],
        strings[696],
        strings[8],
        strings[9]
    });
    IFC4_IfcHeatFluxDensityMeasure_type = new type_declaration(strings[697], 471, new simple_type(simple_type::real_type));
    IFC4_IfcHeatingValueMeasure_type = new type_declaration(strings[698], 472, new simple_type(simple_type::real_type));
    IFC4_IfcHumidifierTypeEnum_type = new enumeration_type(strings[699], 475, {
        strings[700],
        strings[701],
        strings[702],
        strings[703],
        strings[704],
        strings[705],
        strings[706],
        strings[707],
        strings[708],
        strings[709],
        strings[710],
        strings[711],
        strings[712],
        strings[8],
        strings[9]
    });
    IFC4_IfcIdentifier_type = new type_declaration(strings[713], 476, new simple_type(simple_type::string_type));
    IFC4_IfcIlluminanceMeasure_type = new type_declaration(strings[714], 477, new simple_type(simple_type::real_type));
    IFC4_IfcInductanceMeasure_type = new type_declaration(strings[715], 485, new simple_type(simple_type::real_type));
    IFC4_IfcInteger_type = new type_declaration(strings[716], 486, new simple_type(simple_type::integer_type));
    IFC4_IfcIntegerCountRateMeasure_type = new type_declaration(strings[717], 487, new simple_type(simple_type::integer_type));
    IFC4_IfcInterceptorTypeEnum_type = new enumeration_type(strings[718], 490, {
        strings[719],
        strings[720],
        strings[443],
        strings[721],
        strings[8],
        strings[9]
    });
    IFC4_IfcInternalOrExternalEnum_type = new enumeration_type(strings[722], 491, {
        strings[723],
        strings[610],
        strings[611],
        strings[612],
        strings[613],
        strings[9]
    });
    IFC4_IfcInventoryTypeEnum_type = new enumeration_type(strings[724], 494, {
        strings[725],
        strings[726],
        strings[727],
        strings[8],
        strings[9]
    });
    IFC4_IfcIonConcentrationMeasure_type = new type_declaration(strings[728], 495, new simple_type(simple_type::real_type));
    IFC4_IfcIsothermalMoistureCapacityMeasure_type = new type_declaration(strings[729], 499, new simple_type(simple_type::real_type));
    IFC4_IfcJunctionBoxTypeEnum_type = new enumeration_type(strings[730], 502, {
        strings[429],
        strings[731],
        strings[8],
        strings[9]
    });
    IFC4_IfcKinematicViscosityMeasure_type = new type_declaration(strings[732], 503, new simple_type(simple_type::real_type));
    IFC4_IfcKnotType_type = new enumeration_type(strings[733], 504, {
        strings[734],
        strings[735],
        strings[736],
        strings[115]
    });
    IFC4_IfcLabel_type = new type_declaration(strings[737], 505, new simple_type(simple_type::string_type));
    IFC4_IfcLaborResourceTypeEnum_type = new enumeration_type(strings[738], 508, {
        strings[739],
        strings[740],
        strings[741],
        strings[271],
        strings[272],
        strings[742],
        strings[743],
        strings[308],
        strings[744],
        strings[745],
        strings[746],
        strings[275],
        strings[747],
        strings[266],
        strings[748],
        strings[310],
        strings[749],
        strings[750],
        strings[751],
        strings[8],
        strings[9]
    });
    IFC4_IfcLampTypeEnum_type = new enumeration_type(strings[752], 512, {
        strings[753],
        strings[754],
        strings[755],
        strings[756],
        strings[757],
        strings[758],
        strings[759],
        strings[760],
        strings[761],
        strings[8],
        strings[9]
    });
    IFC4_IfcLanguageId_type = new type_declaration(strings[762], 513, new named_type(IFC4_IfcIdentifier_type));
    IFC4_IfcLayerSetDirectionEnum_type = new enumeration_type(strings[763], 515, {
        strings[764],
        strings[765],
        strings[766]
    });
    IFC4_IfcLengthMeasure_type = new type_declaration(strings[767], 516, new simple_type(simple_type::real_type));
    IFC4_IfcLightDistributionCurveEnum_type = new enumeration_type(strings[768], 520, {
        strings[769],
        strings[770],
        strings[771],
        strings[9]
    });
    IFC4_IfcLightEmissionSourceEnum_type = new enumeration_type(strings[772], 523, {
        strings[753],
        strings[754],
        strings[756],
        strings[757],
        strings[773],
        strings[774],
        strings[775],
        strings[776],
        strings[759],
        strings[761],
        strings[9]
    });
    IFC4_IfcLightFixtureTypeEnum_type = new enumeration_type(strings[777], 526, {
        strings[778],
        strings[779],
        strings[780],
        strings[8],
        strings[9]
    });
    IFC4_IfcLinearForceMeasure_type = new type_declaration(strings[781], 535, new simple_type(simple_type::real_type));
    IFC4_IfcLinearMomentMeasure_type = new type_declaration(strings[782], 536, new simple_type(simple_type::real_type));
    IFC4_IfcLinearStiffnessMeasure_type = new type_declaration(strings[783], 537, new simple_type(simple_type::real_type));
    IFC4_IfcLinearVelocityMeasure_type = new type_declaration(strings[784], 538, new simple_type(simple_type::real_type));
    IFC4_IfcLoadGroupTypeEnum_type = new enumeration_type(strings[785], 540, {
        strings[786],
        strings[787],
        strings[788],
        strings[8],
        strings[9]
    });
    IFC4_IfcLogical_type = new type_declaration(strings[789], 542, new simple_type(simple_type::logical_type));
    IFC4_IfcLogicalOperatorEnum_type = new enumeration_type(strings[790], 543, {
        strings[791],
        strings[792],
        strings[793],
        strings[794],
        strings[795]
    });
    IFC4_IfcLuminousFluxMeasure_type = new type_declaration(strings[796], 546, new simple_type(simple_type::real_type));
    IFC4_IfcLuminousIntensityDistributionMeasure_type = new type_declaration(strings[797], 547, new simple_type(simple_type::real_type));
    IFC4_IfcLuminousIntensityMeasure_type = new type_declaration(strings[798], 548, new simple_type(simple_type::real_type));
    IFC4_IfcMagneticFluxDensityMeasure_type = new type_declaration(strings[799], 549, new simple_type(simple_type::real_type));
    IFC4_IfcMagneticFluxMeasure_type = new type_declaration(strings[800], 550, new simple_type(simple_type::real_type));
    IFC4_IfcMassDensityMeasure_type = new type_declaration(strings[801], 554, new simple_type(simple_type::real_type));
    IFC4_IfcMassFlowRateMeasure_type = new type_declaration(strings[802], 555, new simple_type(simple_type::real_type));
    IFC4_IfcMassMeasure_type = new type_declaration(strings[803], 556, new simple_type(simple_type::real_type));
    IFC4_IfcMassPerLengthMeasure_type = new type_declaration(strings[804], 557, new simple_type(simple_type::real_type));
    IFC4_IfcMechanicalFastenerTypeEnum_type = new enumeration_type(strings[805], 582, {
        strings[806],
        strings[807],
        strings[808],
        strings[809],
        strings[810],
        strings[811],
        strings[812],
        strings[813],
        strings[814],
        strings[815],
        strings[8],
        strings[9]
    });
    IFC4_IfcMedicalDeviceTypeEnum_type = new enumeration_type(strings[816], 585, {
        strings[817],
        strings[818],
        strings[819],
        strings[820],
        strings[821],
        strings[8],
        strings[9]
    });
    IFC4_IfcMemberTypeEnum_type = new enumeration_type(strings[822], 589, {
        strings[823],
        strings[824],
        strings[825],
        strings[826],
        strings[827],
        strings[695],
        strings[6],
        strings[828],
        strings[829],
        strings[830],
        strings[831],
        strings[832],
        strings[8],
        strings[9]
    });
    IFC4_IfcModulusOfElasticityMeasure_type = new type_declaration(strings[833], 593, new simple_type(simple_type::real_type));
    IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration(strings[834], 594, new simple_type(simple_type::real_type));
    IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration(strings[835], 595, new simple_type(simple_type::real_type));
    IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type = new select_type(strings[836], 596, {
        IFC4_IfcBoolean_type,
        IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type
    });
    IFC4_IfcModulusOfSubgradeReactionMeasure_type = new type_declaration(strings[837], 597, new simple_type(simple_type::real_type));
    IFC4_IfcModulusOfSubgradeReactionSelect_type = new select_type(strings[838], 598, {
        IFC4_IfcBoolean_type,
        IFC4_IfcModulusOfSubgradeReactionMeasure_type
    });
    IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type = new select_type(strings[839], 599, {
        IFC4_IfcBoolean_type,
        IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type
    });
    IFC4_IfcMoistureDiffusivityMeasure_type = new type_declaration(strings[840], 600, new simple_type(simple_type::real_type));
    IFC4_IfcMolecularWeightMeasure_type = new type_declaration(strings[841], 601, new simple_type(simple_type::real_type));
    IFC4_IfcMomentOfInertiaMeasure_type = new type_declaration(strings[842], 602, new simple_type(simple_type::real_type));
    IFC4_IfcMonetaryMeasure_type = new type_declaration(strings[843], 603, new simple_type(simple_type::real_type));
    IFC4_IfcMonthInYearNumber_type = new type_declaration(strings[844], 605, new simple_type(simple_type::integer_type));
    IFC4_IfcMotorConnectionTypeEnum_type = new enumeration_type(strings[845], 608, {
        strings[846],
        strings[847],
        strings[848],
        strings[8],
        strings[9]
    });
    IFC4_IfcNonNegativeLengthMeasure_type = new type_declaration(strings[849], 610, new named_type(IFC4_IfcLengthMeasure_type));
    IFC4_IfcNullStyle_type = new enumeration_type(strings[850], 612, {
        strings[851]
    });
    IFC4_IfcNumericMeasure_type = new type_declaration(strings[852], 613, new simple_type(simple_type::number_type));
    IFC4_IfcObjectTypeEnum_type = new enumeration_type(strings[853], 620, {
        strings[854],
        strings[855],
        strings[427],
        strings[856],
        strings[857],
        strings[858],
        strings[859],
        strings[9]
    });
    IFC4_IfcObjectiveEnum_type = new enumeration_type(strings[860], 617, {
        strings[861],
        strings[862],
        strings[863],
        strings[610],
        strings[864],
        strings[865],
        strings[866],
        strings[867],
        strings[868],
        strings[869],
        strings[870],
        strings[8],
        strings[9]
    });
    IFC4_IfcOccupantTypeEnum_type = new enumeration_type(strings[871], 622, {
        strings[872],
        strings[873],
        strings[874],
        strings[875],
        strings[876],
        strings[877],
        strings[878],
        strings[8],
        strings[9]
    });
    IFC4_IfcOpeningElementTypeEnum_type = new enumeration_type(strings[879], 626, {
        strings[880],
        strings[881],
        strings[8],
        strings[9]
    });
    IFC4_IfcOutletTypeEnum_type = new enumeration_type(strings[882], 635, {
        strings[883],
        strings[884],
        strings[885],
        strings[886],
        strings[887],
        strings[8],
        strings[9]
    });
    IFC4_IfcPHMeasure_type = new type_declaration(strings[888], 649, new simple_type(simple_type::real_type));
    IFC4_IfcParameterValue_type = new type_declaration(strings[889], 638, new simple_type(simple_type::real_type));
    IFC4_IfcPerformanceHistoryTypeEnum_type = new enumeration_type(strings[890], 642, {
        strings[8],
        strings[9]
    });
    IFC4_IfcPermeableCoveringOperationEnum_type = new enumeration_type(strings[891], 643, {
        strings[892],
        strings[893],
        strings[894],
        strings[8],
        strings[9]
    });
    IFC4_IfcPermitTypeEnum_type = new enumeration_type(strings[895], 646, {
        strings[896],
        strings[897],
        strings[898],
        strings[8],
        strings[9]
    });
    IFC4_IfcPhysicalOrVirtualEnum_type = new enumeration_type(strings[899], 651, {
        strings[900],
        strings[901],
        strings[9]
    });
    IFC4_IfcPileConstructionEnum_type = new enumeration_type(strings[902], 655, {
        strings[903],
        strings[904],
        strings[905],
        strings[906],
        strings[8],
        strings[9]
    });
    IFC4_IfcPileTypeEnum_type = new enumeration_type(strings[907], 657, {
        strings[908],
        strings[909],
        strings[910],
        strings[911],
        strings[912],
        strings[913],
        strings[8],
        strings[9]
    });
    IFC4_IfcPipeFittingTypeEnum_type = new enumeration_type(strings[914], 660, {
        strings[171],
        strings[181],
        strings[182],
        strings[183],
        strings[184],
        strings[510],
        strings[185],
        strings[8],
        strings[9]
    });
    IFC4_IfcPipeSegmentTypeEnum_type = new enumeration_type(strings[915], 663, {
        strings[916],
        strings[513],
        strings[512],
        strings[917],
        strings[918],
        strings[8],
        strings[9]
    });
    IFC4_IfcPlanarForceMeasure_type = new type_declaration(strings[919], 668, new simple_type(simple_type::real_type));
    IFC4_IfcPlaneAngleMeasure_type = new type_declaration(strings[920], 670, new simple_type(simple_type::real_type));
    IFC4_IfcPlateTypeEnum_type = new enumeration_type(strings[921], 674, {
        strings[922],
        strings[923],
        strings[8],
        strings[9]
    });
    IFC4_IfcPositiveInteger_type = new type_declaration(strings[924], 684, new named_type(IFC4_IfcInteger_type));
    IFC4_IfcPositiveLengthMeasure_type = new type_declaration(strings[925], 685, new named_type(IFC4_IfcLengthMeasure_type));
    IFC4_IfcPositivePlaneAngleMeasure_type = new type_declaration(strings[926], 686, new named_type(IFC4_IfcPlaneAngleMeasure_type));
    IFC4_IfcPowerMeasure_type = new type_declaration(strings[927], 689, new simple_type(simple_type::real_type));
    IFC4_IfcPreferredSurfaceCurveRepresentation_type = new enumeration_type(strings[928], 696, {
        strings[929],
        strings[930],
        strings[931]
    });
    IFC4_IfcPresentableText_type = new type_declaration(strings[932], 697, new simple_type(simple_type::string_type));
    IFC4_IfcPressureMeasure_type = new type_declaration(strings[933], 704, new simple_type(simple_type::real_type));
    IFC4_IfcProcedureTypeEnum_type = new enumeration_type(strings[934], 707, {
        strings[935],
        strings[936],
        strings[937],
        strings[938],
        strings[939],
        strings[940],
        strings[941],
        strings[8],
        strings[9]
    });
    IFC4_IfcProfileTypeEnum_type = new enumeration_type(strings[942], 717, {
        strings[943],
        strings[944]
    });
    IFC4_IfcProjectOrderTypeEnum_type = new enumeration_type(strings[945], 725, {
        strings[946],
        strings[947],
        strings[948],
        strings[949],
        strings[950],
        strings[8],
        strings[9]
    });
    IFC4_IfcProjectedOrTrueLengthEnum_type = new enumeration_type(strings[951], 720, {
        strings[952],
        strings[953]
    });
    IFC4_IfcProjectionElementTypeEnum_type = new enumeration_type(strings[954], 722, {
        strings[8],
        strings[9]
    });
    IFC4_IfcPropertySetTemplateTypeEnum_type = new enumeration_type(strings[955], 740, {
        strings[956],
        strings[957],
        strings[958],
        strings[959],
        strings[960],
        strings[961],
        strings[962],
        strings[9]
    });
    IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type = new enumeration_type(strings[963], 748, {
        strings[964],
        strings[965],
        strings[966],
        strings[967],
        strings[8],
        strings[9]
    });
    IFC4_IfcProtectiveDeviceTypeEnum_type = new enumeration_type(strings[968], 750, {
        strings[969],
        strings[970],
        strings[971],
        strings[972],
        strings[973],
        strings[974],
        strings[975],
        strings[8],
        strings[9]
    });
    IFC4_IfcPumpTypeEnum_type = new enumeration_type(strings[976], 754, {
        strings[977],
        strings[978],
        strings[979],
        strings[980],
        strings[981],
        strings[982],
        strings[983],
        strings[8],
        strings[9]
    });
    IFC4_IfcRadioActivityMeasure_type = new type_declaration(strings[984], 762, new simple_type(simple_type::real_type));
    IFC4_IfcRailingTypeEnum_type = new enumeration_type(strings[985], 765, {
        strings[986],
        strings[987],
        strings[988],
        strings[8],
        strings[9]
    });
    IFC4_IfcRampFlightTypeEnum_type = new enumeration_type(strings[989], 769, {
        strings[990],
        strings[991],
        strings[8],
        strings[9]
    });
    IFC4_IfcRampTypeEnum_type = new enumeration_type(strings[992], 771, {
        strings[993],
        strings[994],
        strings[995],
        strings[996],
        strings[997],
        strings[998],
        strings[8],
        strings[9]
    });
    IFC4_IfcRatioMeasure_type = new type_declaration(strings[999], 772, new simple_type(simple_type::real_type));
    IFC4_IfcReal_type = new type_declaration(strings[1000], 775, new simple_type(simple_type::real_type));
    IFC4_IfcRecurrenceTypeEnum_type = new enumeration_type(strings[1001], 781, {
        strings[1002],
        strings[1003],
        strings[1004],
        strings[1005],
        strings[1006],
        strings[1007],
        strings[1008],
        strings[1009]
    });
    IFC4_IfcReflectanceMethodEnum_type = new enumeration_type(strings[1010], 783, {
        strings[1011],
        strings[1012],
        strings[1013],
        strings[1014],
        strings[276],
        strings[1015],
        strings[1016],
        strings[277],
        strings[1017],
        strings[9]
    });
    IFC4_IfcReinforcingBarRoleEnum_type = new enumeration_type(strings[1018], 788, {
        strings[1019],
        strings[1020],
        strings[1021],
        strings[832],
        strings[1022],
        strings[1023],
        strings[1024],
        strings[1025],
        strings[8],
        strings[9]
    });
    IFC4_IfcReinforcingBarSurfaceEnum_type = new enumeration_type(strings[1026], 789, {
        strings[1027],
        strings[1028]
    });
    IFC4_IfcReinforcingBarTypeEnum_type = new enumeration_type(strings[1029], 791, {
        strings[1025],
        strings[1023],
        strings[1021],
        strings[1019],
        strings[1022],
        strings[1024],
        strings[1020],
        strings[832],
        strings[8],
        strings[9]
    });
    IFC4_IfcReinforcingMeshTypeEnum_type = new enumeration_type(strings[1030], 796, {
        strings[8],
        strings[9]
    });
    IFC4_IfcRoleEnum_type = new enumeration_type(strings[1031], 861, {
        strings[1032],
        strings[1033],
        strings[1034],
        strings[1035],
        strings[1036],
        strings[1037],
        strings[1038],
        strings[1039],
        strings[1040],
        strings[1041],
        strings[1042],
        strings[1043],
        strings[1044],
        strings[1045],
        strings[1046],
        strings[1047],
        strings[1048],
        strings[877],
        strings[1049],
        strings[1050],
        strings[1051],
        strings[1052],
        strings[8]
    });
    IFC4_IfcRoofTypeEnum_type = new enumeration_type(strings[1053], 864, {
        strings[1054],
        strings[1055],
        strings[1056],
        strings[1057],
        strings[1058],
        strings[1059],
        strings[1060],
        strings[1061],
        strings[1062],
        strings[1063],
        strings[1064],
        strings[1065],
        strings[1066],
        strings[8],
        strings[9]
    });
    IFC4_IfcRotationalFrequencyMeasure_type = new type_declaration(strings[1067], 866, new simple_type(simple_type::real_type));
    IFC4_IfcRotationalMassMeasure_type = new type_declaration(strings[1068], 867, new simple_type(simple_type::real_type));
    IFC4_IfcRotationalStiffnessMeasure_type = new type_declaration(strings[1069], 868, new simple_type(simple_type::real_type));
    IFC4_IfcRotationalStiffnessSelect_type = new select_type(strings[1070], 869, {
        IFC4_IfcBoolean_type,
        IFC4_IfcRotationalStiffnessMeasure_type
    });
    IFC4_IfcSIPrefix_type = new enumeration_type(strings[1071], 900, {
        strings[1072],
        strings[1073],
        strings[1074],
        strings[1075],
        strings[1076],
        strings[1077],
        strings[1078],
        strings[1079],
        strings[1080],
        strings[1081],
        strings[1082],
        strings[1083],
        strings[1084],
        strings[1085],
        strings[1086],
        strings[1087]
    });
    IFC4_IfcSIUnitName_type = new enumeration_type(strings[1088], 903, {
        strings[1089],
        strings[1090],
        strings[1091],
        strings[1092],
        strings[1093],
        strings[1094],
        strings[1095],
        strings[1096],
        strings[1097],
        strings[1098],
        strings[1099],
        strings[1100],
        strings[1101],
        strings[1102],
        strings[1103],
        strings[1104],
        strings[1105],
        strings[1106],
        strings[1107],
        strings[1108],
        strings[1109],
        strings[1110],
        strings[1111],
        strings[1112],
        strings[1113],
        strings[1114],
        strings[1115],
        strings[1116],
        strings[1117],
        strings[1118]
    });
    IFC4_IfcSanitaryTerminalTypeEnum_type = new enumeration_type(strings[1119], 873, {
        strings[1120],
        strings[1121],
        strings[1122],
        strings[1123],
        strings[641],
        strings[1124],
        strings[1125],
        strings[1126],
        strings[1127],
        strings[1128],
        strings[8],
        strings[9]
    });
    IFC4_IfcSectionModulusMeasure_type = new type_declaration(strings[1129], 878, new simple_type(simple_type::real_type));
    IFC4_IfcSectionTypeEnum_type = new enumeration_type(strings[1130], 881, {
        strings[1131],
        strings[1132]
    });
    IFC4_IfcSectionalAreaIntegralMeasure_type = new type_declaration(strings[1133], 876, new simple_type(simple_type::real_type));
    IFC4_IfcSensorTypeEnum_type = new enumeration_type(strings[1134], 885, {
        strings[1135],
        strings[1136],
        strings[1137],
        strings[1138],
        strings[1139],
        strings[1140],
        strings[1141],
        strings[1142],
        strings[1143],
        strings[1144],
        strings[1145],
        strings[1146],
        strings[1147],
        strings[1148],
        strings[1149],
        strings[1150],
        strings[1151],
        strings[1152],
        strings[1153],
        strings[1154],
        strings[1155],
        strings[1156],
        strings[1157],
        strings[1158],
        strings[8],
        strings[9]
    });
    IFC4_IfcSequenceEnum_type = new enumeration_type(strings[1159], 886, {
        strings[1160],
        strings[1161],
        strings[1162],
        strings[1163],
        strings[8],
        strings[9]
    });
    IFC4_IfcShadingDeviceTypeEnum_type = new enumeration_type(strings[1164], 889, {
        strings[1165],
        strings[1166],
        strings[1167],
        strings[8],
        strings[9]
    });
    IFC4_IfcShearModulusMeasure_type = new type_declaration(strings[1168], 893, new simple_type(simple_type::real_type));
    IFC4_IfcSimplePropertyTemplateTypeEnum_type = new enumeration_type(strings[1169], 898, {
        strings[1170],
        strings[1171],
        strings[1172],
        strings[1173],
        strings[1174],
        strings[1175],
        strings[1176],
        strings[1177],
        strings[1178],
        strings[1179],
        strings[1180],
        strings[1181]
    });
    IFC4_IfcSlabTypeEnum_type = new enumeration_type(strings[1182], 909, {
        strings[1183],
        strings[1184],
        strings[1185],
        strings[1186],
        strings[8],
        strings[9]
    });
    IFC4_IfcSolarDeviceTypeEnum_type = new enumeration_type(strings[1187], 913, {
        strings[1188],
        strings[1189],
        strings[8],
        strings[9]
    });
    IFC4_IfcSolidAngleMeasure_type = new type_declaration(strings[1190], 914, new simple_type(simple_type::real_type));
    IFC4_IfcSoundPowerLevelMeasure_type = new type_declaration(strings[1191], 917, new simple_type(simple_type::real_type));
    IFC4_IfcSoundPowerMeasure_type = new type_declaration(strings[1192], 918, new simple_type(simple_type::real_type));
    IFC4_IfcSoundPressureLevelMeasure_type = new type_declaration(strings[1193], 919, new simple_type(simple_type::real_type));
    IFC4_IfcSoundPressureMeasure_type = new type_declaration(strings[1194], 920, new simple_type(simple_type::real_type));
    IFC4_IfcSpaceHeaterTypeEnum_type = new enumeration_type(strings[1195], 925, {
        strings[1196],
        strings[1197],
        strings[8],
        strings[9]
    });
    IFC4_IfcSpaceTypeEnum_type = new enumeration_type(strings[1198], 927, {
        strings[1199],
        strings[1200],
        strings[1201],
        strings[723],
        strings[610],
        strings[8],
        strings[9]
    });
    IFC4_IfcSpatialZoneTypeEnum_type = new enumeration_type(strings[1202], 934, {
        strings[1203],
        strings[1204],
        strings[265],
        strings[1205],
        strings[448],
        strings[967],
        strings[23],
        strings[455],
        strings[8],
        strings[9]
    });
    IFC4_IfcSpecificHeatCapacityMeasure_type = new type_declaration(strings[1206], 935, new simple_type(simple_type::real_type));
    IFC4_IfcSpecularExponent_type = new type_declaration(strings[1207], 936, new simple_type(simple_type::real_type));
    IFC4_IfcSpecularRoughness_type = new type_declaration(strings[1208], 938, new simple_type(simple_type::real_type));
    IFC4_IfcStackTerminalTypeEnum_type = new enumeration_type(strings[1209], 943, {
        strings[1210],
        strings[1211],
        strings[1212],
        strings[8],
        strings[9]
    });
    IFC4_IfcStairFlightTypeEnum_type = new enumeration_type(strings[1213], 947, {
        strings[990],
        strings[1214],
        strings[991],
        strings[1215],
        strings[1066],
        strings[8],
        strings[9]
    });
    IFC4_IfcStairTypeEnum_type = new enumeration_type(strings[1216], 949, {
        strings[1217],
        strings[1218],
        strings[1219],
        strings[1220],
        strings[1221],
        strings[1222],
        strings[1223],
        strings[1224],
        strings[1225],
        strings[1226],
        strings[1227],
        strings[1228],
        strings[1229],
        strings[1230],
        strings[8],
        strings[9]
    });
    IFC4_IfcStateEnum_type = new enumeration_type(strings[1231], 950, {
        strings[1232],
        strings[1233],
        strings[1234],
        strings[1235],
        strings[1236]
    });
    IFC4_IfcStructuralCurveActivityTypeEnum_type = new enumeration_type(strings[1237], 958, {
        strings[1238],
        strings[320],
        strings[1239],
        strings[1240],
        strings[1241],
        strings[1242],
        strings[1243],
        strings[8],
        strings[9]
    });
    IFC4_IfcStructuralCurveMemberTypeEnum_type = new enumeration_type(strings[1244], 961, {
        strings[1245],
        strings[1246],
        strings[415],
        strings[1247],
        strings[1248],
        strings[8],
        strings[9]
    });
    IFC4_IfcStructuralSurfaceActivityTypeEnum_type = new enumeration_type(strings[1249], 987, {
        strings[1238],
        strings[1250],
        strings[1243],
        strings[1251],
        strings[8],
        strings[9]
    });
    IFC4_IfcStructuralSurfaceMemberTypeEnum_type = new enumeration_type(strings[1252], 990, {
        strings[1253],
        strings[1254],
        strings[1255],
        strings[8],
        strings[9]
    });
    IFC4_IfcSubContractResourceTypeEnum_type = new enumeration_type(strings[1256], 999, {
        strings[1257],
        strings[898],
        strings[8],
        strings[9]
    });
    IFC4_IfcSurfaceFeatureTypeEnum_type = new enumeration_type(strings[1258], 1005, {
        strings[1259],
        strings[1260],
        strings[1261],
        strings[8],
        strings[9]
    });
    IFC4_IfcSurfaceSide_type = new enumeration_type(strings[1262], 1010, {
        strings[399],
        strings[400],
        strings[1263]
    });
    IFC4_IfcSwitchingDeviceTypeEnum_type = new enumeration_type(strings[1264], 1025, {
        strings[1265],
        strings[1266],
        strings[1267],
        strings[1268],
        strings[1269],
        strings[1270],
        strings[1271],
        strings[1272],
        strings[1273],
        strings[8],
        strings[9]
    });
    IFC4_IfcSystemFurnitureElementTypeEnum_type = new enumeration_type(strings[1274], 1029, {
        strings[1275],
        strings[1276],
        strings[8],
        strings[9]
    });
    IFC4_IfcTankTypeEnum_type = new enumeration_type(strings[1277], 1035, {
        strings[1278],
        strings[1279],
        strings[1280],
        strings[1281],
        strings[1282],
        strings[1283],
        strings[1284],
        strings[8],
        strings[9]
    });
    IFC4_IfcTaskDurationEnum_type = new enumeration_type(strings[1285], 1037, {
        strings[1286],
        strings[1287],
        strings[9]
    });
    IFC4_IfcTaskTypeEnum_type = new enumeration_type(strings[1288], 1041, {
        strings[1289],
        strings[1203],
        strings[1290],
        strings[1291],
        strings[430],
        strings[1292],
        strings[1293],
        strings[1294],
        strings[1295],
        strings[1296],
        strings[1297],
        strings[1298],
        strings[8],
        strings[9]
    });
    IFC4_IfcTemperatureGradientMeasure_type = new type_declaration(strings[1299], 1043, new simple_type(simple_type::real_type));
    IFC4_IfcTemperatureRateOfChangeMeasure_type = new type_declaration(strings[1300], 1044, new simple_type(simple_type::real_type));
    IFC4_IfcTendonAnchorTypeEnum_type = new enumeration_type(strings[1301], 1048, {
        strings[1302],
        strings[1303],
        strings[1304],
        strings[8],
        strings[9]
    });
    IFC4_IfcTendonTypeEnum_type = new enumeration_type(strings[1305], 1050, {
        strings[1306],
        strings[1307],
        strings[1308],
        strings[1309],
        strings[8],
        strings[9]
    });
    IFC4_IfcText_type = new type_declaration(strings[1310], 1053, new simple_type(simple_type::string_type));
    IFC4_IfcTextAlignment_type = new type_declaration(strings[1311], 1054, new simple_type(simple_type::string_type));
    IFC4_IfcTextDecoration_type = new type_declaration(strings[1312], 1055, new simple_type(simple_type::string_type));
    IFC4_IfcTextFontName_type = new type_declaration(strings[1313], 1056, new simple_type(simple_type::string_type));
    IFC4_IfcTextPath_type = new enumeration_type(strings[1314], 1060, {
        strings[477],
        strings[479],
        strings[1315],
        strings[1316]
    });
    IFC4_IfcTextTransformation_type = new type_declaration(strings[1317], 1065, new simple_type(simple_type::string_type));
    IFC4_IfcThermalAdmittanceMeasure_type = new type_declaration(strings[1318], 1071, new simple_type(simple_type::real_type));
    IFC4_IfcThermalConductivityMeasure_type = new type_declaration(strings[1319], 1072, new simple_type(simple_type::real_type));
    IFC4_IfcThermalExpansionCoefficientMeasure_type = new type_declaration(strings[1320], 1073, new simple_type(simple_type::real_type));
    IFC4_IfcThermalResistanceMeasure_type = new type_declaration(strings[1321], 1074, new simple_type(simple_type::real_type));
    IFC4_IfcThermalTransmittanceMeasure_type = new type_declaration(strings[1322], 1075, new simple_type(simple_type::real_type));
    IFC4_IfcThermodynamicTemperatureMeasure_type = new type_declaration(strings[1323], 1076, new simple_type(simple_type::real_type));
    IFC4_IfcTime_type = new type_declaration(strings[1324], 1077, new simple_type(simple_type::string_type));
    IFC4_IfcTimeMeasure_type = new type_declaration(strings[1325], 1078, new simple_type(simple_type::real_type));
    IFC4_IfcTimeOrRatioSelect_type = new select_type(strings[1326], 1079, {
        IFC4_IfcDuration_type,
        IFC4_IfcRatioMeasure_type
    });
    IFC4_IfcTimeSeriesDataTypeEnum_type = new enumeration_type(strings[1327], 1082, {
        strings[1328],
        strings[1243],
        strings[1329],
        strings[1330],
        strings[1331],
        strings[1332],
        strings[9]
    });
    IFC4_IfcTimeStamp_type = new type_declaration(strings[1333], 1084, new simple_type(simple_type::integer_type));
    IFC4_IfcTorqueMeasure_type = new type_declaration(strings[1334], 1088, new simple_type(simple_type::real_type));
    IFC4_IfcTransformerTypeEnum_type = new enumeration_type(strings[1335], 1091, {
        strings[32],
        strings[1336],
        strings[1337],
        strings[1338],
        strings[1339],
        strings[8],
        strings[9]
    });
    IFC4_IfcTransitionCode_type = new enumeration_type(strings[1340], 1092, {
        strings[1341],
        strings[1328],
        strings[1342],
        strings[1343]
    });
    IFC4_IfcTranslationalStiffnessSelect_type = new select_type(strings[1344], 1093, {
        IFC4_IfcBoolean_type,
        IFC4_IfcLinearStiffnessMeasure_type
    });
    IFC4_IfcTransportElementTypeEnum_type = new enumeration_type(strings[1345], 1096, {
        strings[1346],
        strings[1347],
        strings[1348],
        strings[1349],
        strings[1350],
        strings[8],
        strings[9]
    });
    IFC4_IfcTrimmingPreference_type = new enumeration_type(strings[1351], 1100, {
        strings[1352],
        strings[867],
        strings[115]
    });
    IFC4_IfcTubeBundleTypeEnum_type = new enumeration_type(strings[1353], 1105, {
        strings[1354],
        strings[8],
        strings[9]
    });
    IFC4_IfcURIReference_type = new type_declaration(strings[1355], 1119, new simple_type(simple_type::string_type));
    IFC4_IfcUnitEnum_type = new enumeration_type(strings[1356], 1118, {
        strings[1357],
        strings[1358],
        strings[1359],
        strings[1360],
        strings[1361],
        strings[1362],
        strings[1363],
        strings[1364],
        strings[1365],
        strings[1366],
        strings[1367],
        strings[1368],
        strings[1369],
        strings[1370],
        strings[1371],
        strings[1372],
        strings[1373],
        strings[1374],
        strings[1375],
        strings[1376],
        strings[1377],
        strings[1378],
        strings[1379],
        strings[1380],
        strings[1381],
        strings[1382],
        strings[1383],
        strings[1384],
        strings[1385],
        strings[8]
    });
    IFC4_IfcUnitaryControlElementTypeEnum_type = new enumeration_type(strings[1386], 1113, {
        strings[1387],
        strings[1388],
        strings[1389],
        strings[1390],
        strings[1391],
        strings[1392],
        strings[1393],
        strings[1394],
        strings[8],
        strings[9]
    });
    IFC4_IfcUnitaryEquipmentTypeEnum_type = new enumeration_type(strings[1395], 1116, {
        strings[1396],
        strings[1397],
        strings[1398],
        strings[1399],
        strings[1400],
        strings[8],
        strings[9]
    });
    IFC4_IfcValveTypeEnum_type = new enumeration_type(strings[1401], 1124, {
        strings[1402],
        strings[1403],
        strings[1404],
        strings[1405],
        strings[1406],
        strings[1407],
        strings[1408],
        strings[1409],
        strings[1410],
        strings[1411],
        strings[1412],
        strings[1413],
        strings[1414],
        strings[1415],
        strings[1416],
        strings[1417],
        strings[1418],
        strings[1419],
        strings[1420],
        strings[1421],
        strings[1422],
        strings[8],
        strings[9]
    });
    IFC4_IfcVaporPermeabilityMeasure_type = new type_declaration(strings[1423], 1125, new simple_type(simple_type::real_type));
    IFC4_IfcVibrationIsolatorTypeEnum_type = new enumeration_type(strings[1424], 1133, {
        strings[1425],
        strings[1426],
        strings[8],
        strings[9]
    });
    IFC4_IfcVoidingFeatureTypeEnum_type = new enumeration_type(strings[1427], 1137, {
        strings[1428],
        strings[1429],
        strings[1430],
        strings[1431],
        strings[1432],
        strings[1023],
        strings[8],
        strings[9]
    });
    IFC4_IfcVolumeMeasure_type = new type_declaration(strings[1433], 1138, new simple_type(simple_type::real_type));
    IFC4_IfcVolumetricFlowRateMeasure_type = new type_declaration(strings[1434], 1139, new simple_type(simple_type::real_type));
    IFC4_IfcWallTypeEnum_type = new enumeration_type(strings[1435], 1144, {
        strings[1436],
        strings[1437],
        strings[1438],
        strings[1439],
        strings[1020],
        strings[1440],
        strings[1441],
        strings[1239],
        strings[1442],
        strings[8],
        strings[9]
    });
    IFC4_IfcWarpingConstantMeasure_type = new type_declaration(strings[1443], 1145, new simple_type(simple_type::real_type));
    IFC4_IfcWarpingMomentMeasure_type = new type_declaration(strings[1444], 1146, new simple_type(simple_type::real_type));
    IFC4_IfcWarpingStiffnessSelect_type = new select_type(strings[1445], 1147, {
        IFC4_IfcBoolean_type,
        IFC4_IfcWarpingMomentMeasure_type
    });
    IFC4_IfcWasteTerminalTypeEnum_type = new enumeration_type(strings[1446], 1150, {
        strings[1447],
        strings[1448],
        strings[1449],
        strings[1450],
        strings[1451],
        strings[1452],
        strings[1453],
        strings[8],
        strings[9]
    });
    IFC4_IfcWindowPanelOperationEnum_type = new enumeration_type(strings[1454], 1153, {
        strings[1455],
        strings[1456],
        strings[1457],
        strings[1458],
        strings[1459],
        strings[1460],
        strings[1461],
        strings[1462],
        strings[1463],
        strings[1464],
        strings[1465],
        strings[1466],
        strings[1467],
        strings[9]
    });
    IFC4_IfcWindowPanelPositionEnum_type = new enumeration_type(strings[1468], 1154, {
        strings[477],
        strings[478],
        strings[479],
        strings[1469],
        strings[1470],
        strings[9]
    });
    IFC4_IfcWindowStyleConstructionEnum_type = new enumeration_type(strings[1471], 1158, {
        strings[481],
        strings[482],
        strings[483],
        strings[278],
        strings[484],
        strings[277],
        strings[1472],
        strings[9]
    });
    IFC4_IfcWindowStyleOperationEnum_type = new enumeration_type(strings[1473], 1159, {
        strings[1474],
        strings[1475],
        strings[1476],
        strings[1477],
        strings[1478],
        strings[1479],
        strings[1480],
        strings[1481],
        strings[1482],
        strings[8],
        strings[9]
    });
    IFC4_IfcWindowTypeEnum_type = new enumeration_type(strings[1483], 1161, {
        strings[1484],
        strings[1485],
        strings[1486],
        strings[8],
        strings[9]
    });
    IFC4_IfcWindowTypePartitioningEnum_type = new enumeration_type(strings[1487], 1162, {
        strings[1474],
        strings[1475],
        strings[1476],
        strings[1477],
        strings[1478],
        strings[1479],
        strings[1480],
        strings[1481],
        strings[1482],
        strings[8],
        strings[9]
    });
    IFC4_IfcWorkCalendarTypeEnum_type = new enumeration_type(strings[1488], 1164, {
        strings[1489],
        strings[1490],
        strings[1491],
        strings[8],
        strings[9]
    });
    IFC4_IfcWorkPlanTypeEnum_type = new enumeration_type(strings[1492], 1167, {
        strings[1493],
        strings[1494],
        strings[1495],
        strings[8],
        strings[9]
    });
    IFC4_IfcWorkScheduleTypeEnum_type = new enumeration_type(strings[1496], 1169, {
        strings[1493],
        strings[1494],
        strings[1495],
        strings[8],
        strings[9]
    });
    IFC4_IfcActorRole_type = new entity(strings[1497], false, 7, 0);
    IFC4_IfcAddress_type = new entity(strings[1498], true, 12, 0);
    IFC4_IfcApplication_type = new entity(strings[1499], false, 35, 0);
    IFC4_IfcAppliedValue_type = new entity(strings[1500], false, 36, 0);
    IFC4_IfcApproval_type = new entity(strings[1501], false, 38, 0);
    IFC4_IfcBoundaryCondition_type = new entity(strings[1502], true, 74, 0);
    IFC4_IfcBoundaryEdgeCondition_type = new entity(strings[1503], false, 76, IFC4_IfcBoundaryCondition_type);
    IFC4_IfcBoundaryFaceCondition_type = new entity(strings[1504], false, 77, IFC4_IfcBoundaryCondition_type);
    IFC4_IfcBoundaryNodeCondition_type = new entity(strings[1505], false, 78, IFC4_IfcBoundaryCondition_type);
    IFC4_IfcBoundaryNodeConditionWarping_type = new entity(strings[1506], false, 79, IFC4_IfcBoundaryNodeCondition_type);
    IFC4_IfcConnectionGeometry_type = new entity(strings[1507], true, 179, 0);
    IFC4_IfcConnectionPointGeometry_type = new entity(strings[1508], false, 181, IFC4_IfcConnectionGeometry_type);
    IFC4_IfcConnectionSurfaceGeometry_type = new entity(strings[1509], false, 182, IFC4_IfcConnectionGeometry_type);
    IFC4_IfcConnectionVolumeGeometry_type = new entity(strings[1510], false, 184, IFC4_IfcConnectionGeometry_type);
    IFC4_IfcConstraint_type = new entity(strings[1511], true, 185, 0);
    IFC4_IfcCoordinateOperation_type = new entity(strings[1512], true, 213, 0);
    IFC4_IfcCoordinateReferenceSystem_type = new entity(strings[1513], true, 214, 0);
    IFC4_IfcCostValue_type = new entity(strings[1514], false, 220, IFC4_IfcAppliedValue_type);
    IFC4_IfcDerivedUnit_type = new entity(strings[1515], false, 261, 0);
    IFC4_IfcDerivedUnitElement_type = new entity(strings[1516], false, 262, 0);
    IFC4_IfcDimensionalExponents_type = new entity(strings[1517], false, 265, 0);
    IFC4_IfcExternalInformation_type = new entity(strings[1518], true, 375, 0);
    IFC4_IfcExternalReference_type = new entity(strings[1519], true, 379, 0);
    IFC4_IfcExternallyDefinedHatchStyle_type = new entity(strings[1520], false, 376, IFC4_IfcExternalReference_type);
    IFC4_IfcExternallyDefinedSurfaceStyle_type = new entity(strings[1521], false, 377, IFC4_IfcExternalReference_type);
    IFC4_IfcExternallyDefinedTextFont_type = new entity(strings[1522], false, 378, IFC4_IfcExternalReference_type);
    IFC4_IfcGridAxis_type = new entity(strings[1523], false, 461, 0);
    IFC4_IfcIrregularTimeSeriesValue_type = new entity(strings[1524], false, 497, 0);
    IFC4_IfcLibraryInformation_type = new entity(strings[1525], false, 517, IFC4_IfcExternalInformation_type);
    IFC4_IfcLibraryReference_type = new entity(strings[1526], false, 518, IFC4_IfcExternalReference_type);
    IFC4_IfcLightDistributionData_type = new entity(strings[1527], false, 521, 0);
    IFC4_IfcLightIntensityDistribution_type = new entity(strings[1528], false, 527, 0);
    IFC4_IfcMapConversion_type = new entity(strings[1529], false, 552, IFC4_IfcCoordinateOperation_type);
    IFC4_IfcMaterialClassificationRelationship_type = new entity(strings[1530], false, 559, 0);
    IFC4_IfcMaterialDefinition_type = new entity(strings[1531], true, 562, 0);
    IFC4_IfcMaterialLayer_type = new entity(strings[1532], false, 564, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialLayerSet_type = new entity(strings[1533], false, 565, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialLayerWithOffsets_type = new entity(strings[1534], false, 567, IFC4_IfcMaterialLayer_type);
    IFC4_IfcMaterialList_type = new entity(strings[1535], false, 568, 0);
    IFC4_IfcMaterialProfile_type = new entity(strings[1536], false, 569, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialProfileSet_type = new entity(strings[1537], false, 570, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialProfileWithOffsets_type = new entity(strings[1538], false, 573, IFC4_IfcMaterialProfile_type);
    IFC4_IfcMaterialUsageDefinition_type = new entity(strings[1539], true, 577, 0);
    IFC4_IfcMeasureWithUnit_type = new entity(strings[1540], false, 579, 0);
    IFC4_IfcMetric_type = new entity(strings[1541], false, 590, IFC4_IfcConstraint_type);
    IFC4_IfcMonetaryUnit_type = new entity(strings[1542], false, 604, 0);
    IFC4_IfcNamedUnit_type = new entity(strings[1543], true, 609, 0);
    IFC4_IfcObjectPlacement_type = new entity(strings[1544], true, 618, 0);
    IFC4_IfcObjective_type = new entity(strings[1545], false, 616, IFC4_IfcConstraint_type);
    IFC4_IfcOrganization_type = new entity(strings[1546], false, 629, 0);
    IFC4_IfcOwnerHistory_type = new entity(strings[1547], false, 636, 0);
    IFC4_IfcPerson_type = new entity(strings[1548], false, 647, 0);
    IFC4_IfcPersonAndOrganization_type = new entity(strings[1549], false, 648, 0);
    IFC4_IfcPhysicalQuantity_type = new entity(strings[1550], true, 652, 0);
    IFC4_IfcPhysicalSimpleQuantity_type = new entity(strings[1551], true, 653, IFC4_IfcPhysicalQuantity_type);
    IFC4_IfcPostalAddress_type = new entity(strings[1552], false, 688, IFC4_IfcAddress_type);
    IFC4_IfcPresentationItem_type = new entity(strings[1553], true, 698, 0);
    IFC4_IfcPresentationLayerAssignment_type = new entity(strings[1554], false, 699, 0);
    IFC4_IfcPresentationLayerWithStyle_type = new entity(strings[1555], false, 700, IFC4_IfcPresentationLayerAssignment_type);
    IFC4_IfcPresentationStyle_type = new entity(strings[1556], true, 701, 0);
    IFC4_IfcPresentationStyleAssignment_type = new entity(strings[1557], false, 702, 0);
    IFC4_IfcProductRepresentation_type = new entity(strings[1558], true, 712, 0);
    IFC4_IfcProfileDef_type = new entity(strings[1559], false, 715, 0);
    IFC4_IfcProjectedCRS_type = new entity(strings[1560], false, 719, IFC4_IfcCoordinateReferenceSystem_type);
    IFC4_IfcPropertyAbstraction_type = new entity(strings[1561], true, 727, 0);
    IFC4_IfcPropertyEnumeration_type = new entity(strings[1562], false, 732, IFC4_IfcPropertyAbstraction_type);
    IFC4_IfcQuantityArea_type = new entity(strings[1563], false, 755, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityCount_type = new entity(strings[1564], false, 756, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityLength_type = new entity(strings[1565], false, 757, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityTime_type = new entity(strings[1566], false, 759, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityVolume_type = new entity(strings[1567], false, 760, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcQuantityWeight_type = new entity(strings[1568], false, 761, IFC4_IfcPhysicalSimpleQuantity_type);
    IFC4_IfcRecurrencePattern_type = new entity(strings[1569], false, 780, 0);
    IFC4_IfcReference_type = new entity(strings[1570], false, 782, 0);
    IFC4_IfcRepresentation_type = new entity(strings[1571], true, 846, 0);
    IFC4_IfcRepresentationContext_type = new entity(strings[1572], true, 847, 0);
    IFC4_IfcRepresentationItem_type = new entity(strings[1573], true, 848, 0);
    IFC4_IfcRepresentationMap_type = new entity(strings[1574], false, 849, 0);
    IFC4_IfcResourceLevelRelationship_type = new entity(strings[1575], true, 853, 0);
    IFC4_IfcRoot_type = new entity(strings[1576], true, 865, 0);
    IFC4_IfcSIUnit_type = new entity(strings[1577], false, 902, IFC4_IfcNamedUnit_type);
    IFC4_IfcSchedulingTime_type = new entity(strings[1578], true, 874, 0);
    IFC4_IfcShapeAspect_type = new entity(strings[1579], false, 890, 0);
    IFC4_IfcShapeModel_type = new entity(strings[1580], true, 891, IFC4_IfcRepresentation_type);
    IFC4_IfcShapeRepresentation_type = new entity(strings[1581], false, 892, IFC4_IfcShapeModel_type);
    IFC4_IfcStructuralConnectionCondition_type = new entity(strings[1582], true, 956, 0);
    IFC4_IfcStructuralLoad_type = new entity(strings[1583], true, 966, 0);
    IFC4_IfcStructuralLoadConfiguration_type = new entity(strings[1584], false, 968, IFC4_IfcStructuralLoad_type);
    IFC4_IfcStructuralLoadOrResult_type = new entity(strings[1585], true, 971, IFC4_IfcStructuralLoad_type);
    IFC4_IfcStructuralLoadStatic_type = new entity(strings[1586], true, 977, IFC4_IfcStructuralLoadOrResult_type);
    IFC4_IfcStructuralLoadTemperature_type = new entity(strings[1587], false, 978, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStyleModel_type = new entity(strings[1588], true, 996, IFC4_IfcRepresentation_type);
    IFC4_IfcStyledItem_type = new entity(strings[1589], false, 994, IFC4_IfcRepresentationItem_type);
    IFC4_IfcStyledRepresentation_type = new entity(strings[1590], false, 995, IFC4_IfcStyleModel_type);
    IFC4_IfcSurfaceReinforcementArea_type = new entity(strings[1591], false, 1009, IFC4_IfcStructuralLoadOrResult_type);
    IFC4_IfcSurfaceStyle_type = new entity(strings[1592], false, 1011, IFC4_IfcPresentationStyle_type);
    IFC4_IfcSurfaceStyleLighting_type = new entity(strings[1593], false, 1013, IFC4_IfcPresentationItem_type);
    IFC4_IfcSurfaceStyleRefraction_type = new entity(strings[1594], false, 1014, IFC4_IfcPresentationItem_type);
    IFC4_IfcSurfaceStyleShading_type = new entity(strings[1595], false, 1016, IFC4_IfcPresentationItem_type);
    IFC4_IfcSurfaceStyleWithTextures_type = new entity(strings[1596], false, 1017, IFC4_IfcPresentationItem_type);
    IFC4_IfcSurfaceTexture_type = new entity(strings[1597], true, 1018, IFC4_IfcPresentationItem_type);
    IFC4_IfcTable_type = new entity(strings[1598], false, 1030, 0);
    IFC4_IfcTableColumn_type = new entity(strings[1599], false, 1031, 0);
    IFC4_IfcTableRow_type = new entity(strings[1600], false, 1032, 0);
    IFC4_IfcTaskTime_type = new entity(strings[1601], false, 1038, IFC4_IfcSchedulingTime_type);
    IFC4_IfcTaskTimeRecurring_type = new entity(strings[1602], false, 1039, IFC4_IfcTaskTime_type);
    IFC4_IfcTelecomAddress_type = new entity(strings[1603], false, 1042, IFC4_IfcAddress_type);
    IFC4_IfcTextStyle_type = new entity(strings[1604], false, 1061, IFC4_IfcPresentationStyle_type);
    IFC4_IfcTextStyleForDefinedFont_type = new entity(strings[1605], false, 1063, IFC4_IfcPresentationItem_type);
    IFC4_IfcTextStyleTextModel_type = new entity(strings[1606], false, 1064, IFC4_IfcPresentationItem_type);
    IFC4_IfcTextureCoordinate_type = new entity(strings[1607], true, 1066, IFC4_IfcPresentationItem_type);
    IFC4_IfcTextureCoordinateGenerator_type = new entity(strings[1608], false, 1067, IFC4_IfcTextureCoordinate_type);
    IFC4_IfcTextureMap_type = new entity(strings[1609], false, 1068, IFC4_IfcTextureCoordinate_type);
    IFC4_IfcTextureVertex_type = new entity(strings[1610], false, 1069, IFC4_IfcPresentationItem_type);
    IFC4_IfcTextureVertexList_type = new entity(strings[1611], false, 1070, IFC4_IfcPresentationItem_type);
    IFC4_IfcTimePeriod_type = new entity(strings[1612], false, 1080, 0);
    IFC4_IfcTimeSeries_type = new entity(strings[1613], true, 1081, 0);
    IFC4_IfcTimeSeriesValue_type = new entity(strings[1614], false, 1083, 0);
    IFC4_IfcTopologicalRepresentationItem_type = new entity(strings[1615], true, 1085, IFC4_IfcRepresentationItem_type);
    IFC4_IfcTopologyRepresentation_type = new entity(strings[1616], false, 1086, IFC4_IfcShapeModel_type);
    IFC4_IfcUnitAssignment_type = new entity(strings[1617], false, 1117, 0);
    IFC4_IfcVertex_type = new entity(strings[1618], false, 1128, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcVertexPoint_type = new entity(strings[1619], false, 1130, IFC4_IfcVertex_type);
    IFC4_IfcVirtualGridIntersection_type = new entity(strings[1620], false, 1135, 0);
    IFC4_IfcWorkTime_type = new entity(strings[1621], false, 1170, IFC4_IfcSchedulingTime_type);
    IFC4_IfcActorSelect_type = new select_type(strings[1622], 8, {
        IFC4_IfcOrganization_type,
        IFC4_IfcPerson_type,
        IFC4_IfcPersonAndOrganization_type
    });
    IFC4_IfcArcIndex_type = new type_declaration(strings[1623], 43, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcPositiveInteger_type)));
    IFC4_IfcBendingParameterSelect_type = new select_type(strings[1624], 62, {
        IFC4_IfcLengthMeasure_type,
        IFC4_IfcPlaneAngleMeasure_type
    });
    IFC4_IfcBoxAlignment_type = new type_declaration(strings[1625], 83, new named_type(IFC4_IfcLabel_type));
    IFC4_IfcDerivedMeasureValue_type = new select_type(strings[1626], 259, {
        IFC4_IfcAbsorbedDoseMeasure_type,
        IFC4_IfcAccelerationMeasure_type,
        IFC4_IfcAngularVelocityMeasure_type,
        IFC4_IfcAreaDensityMeasure_type,
        IFC4_IfcCompoundPlaneAngleMeasure_type,
        IFC4_IfcCurvatureMeasure_type,
        IFC4_IfcDoseEquivalentMeasure_type,
        IFC4_IfcDynamicViscosityMeasure_type,
        IFC4_IfcElectricCapacitanceMeasure_type,
        IFC4_IfcElectricChargeMeasure_type,
        IFC4_IfcElectricConductanceMeasure_type,
        IFC4_IfcElectricResistanceMeasure_type,
        IFC4_IfcElectricVoltageMeasure_type,
        IFC4_IfcEnergyMeasure_type,
        IFC4_IfcForceMeasure_type,
        IFC4_IfcFrequencyMeasure_type,
        IFC4_IfcHeatFluxDensityMeasure_type,
        IFC4_IfcHeatingValueMeasure_type,
        IFC4_IfcIlluminanceMeasure_type,
        IFC4_IfcInductanceMeasure_type,
        IFC4_IfcIntegerCountRateMeasure_type,
        IFC4_IfcIonConcentrationMeasure_type,
        IFC4_IfcIsothermalMoistureCapacityMeasure_type,
        IFC4_IfcKinematicViscosityMeasure_type,
        IFC4_IfcLinearForceMeasure_type,
        IFC4_IfcLinearMomentMeasure_type,
        IFC4_IfcLinearStiffnessMeasure_type,
        IFC4_IfcLinearVelocityMeasure_type,
        IFC4_IfcLuminousFluxMeasure_type,
        IFC4_IfcLuminousIntensityDistributionMeasure_type,
        IFC4_IfcMagneticFluxDensityMeasure_type,
        IFC4_IfcMagneticFluxMeasure_type,
        IFC4_IfcMassDensityMeasure_type,
        IFC4_IfcMassFlowRateMeasure_type,
        IFC4_IfcMassPerLengthMeasure_type,
        IFC4_IfcModulusOfElasticityMeasure_type,
        IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type,
        IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type,
        IFC4_IfcModulusOfSubgradeReactionMeasure_type,
        IFC4_IfcMoistureDiffusivityMeasure_type,
        IFC4_IfcMolecularWeightMeasure_type,
        IFC4_IfcMomentOfInertiaMeasure_type,
        IFC4_IfcMonetaryMeasure_type,
        IFC4_IfcPHMeasure_type,
        IFC4_IfcPlanarForceMeasure_type,
        IFC4_IfcPowerMeasure_type,
        IFC4_IfcPressureMeasure_type,
        IFC4_IfcRadioActivityMeasure_type,
        IFC4_IfcRotationalFrequencyMeasure_type,
        IFC4_IfcRotationalMassMeasure_type,
        IFC4_IfcRotationalStiffnessMeasure_type,
        IFC4_IfcSectionModulusMeasure_type,
        IFC4_IfcSectionalAreaIntegralMeasure_type,
        IFC4_IfcShearModulusMeasure_type,
        IFC4_IfcSoundPowerLevelMeasure_type,
        IFC4_IfcSoundPowerMeasure_type,
        IFC4_IfcSoundPressureLevelMeasure_type,
        IFC4_IfcSoundPressureMeasure_type,
        IFC4_IfcSpecificHeatCapacityMeasure_type,
        IFC4_IfcTemperatureGradientMeasure_type,
        IFC4_IfcTemperatureRateOfChangeMeasure_type,
        IFC4_IfcThermalAdmittanceMeasure_type,
        IFC4_IfcThermalConductivityMeasure_type,
        IFC4_IfcThermalExpansionCoefficientMeasure_type,
        IFC4_IfcThermalResistanceMeasure_type,
        IFC4_IfcThermalTransmittanceMeasure_type,
        IFC4_IfcTorqueMeasure_type,
        IFC4_IfcVaporPermeabilityMeasure_type,
        IFC4_IfcVolumetricFlowRateMeasure_type,
        IFC4_IfcWarpingConstantMeasure_type,
        IFC4_IfcWarpingMomentMeasure_type
    });
    IFC4_IfcLayeredItem_type = new select_type(strings[1627], 514, {
        IFC4_IfcRepresentation_type,
        IFC4_IfcRepresentationItem_type
    });
    IFC4_IfcLibrarySelect_type = new select_type(strings[1628], 519, {
        IFC4_IfcLibraryInformation_type,
        IFC4_IfcLibraryReference_type
    });
    IFC4_IfcLightDistributionDataSourceSelect_type = new select_type(strings[1629], 522, {
        IFC4_IfcExternalReference_type,
        IFC4_IfcLightIntensityDistribution_type
    });
    IFC4_IfcLineIndex_type = new type_declaration(strings[1630], 539, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcPositiveInteger_type)));
    IFC4_IfcMaterialSelect_type = new select_type(strings[1631], 576, {
        IFC4_IfcMaterialDefinition_type,
        IFC4_IfcMaterialList_type,
        IFC4_IfcMaterialUsageDefinition_type
    });
    IFC4_IfcNormalisedRatioMeasure_type = new type_declaration(strings[1632], 611, new named_type(IFC4_IfcRatioMeasure_type));
    IFC4_IfcObjectReferenceSelect_type = new select_type(strings[1633], 619, {
        IFC4_IfcAddress_type,
        IFC4_IfcAppliedValue_type,
        IFC4_IfcExternalReference_type,
        IFC4_IfcMaterialDefinition_type,
        IFC4_IfcOrganization_type,
        IFC4_IfcPerson_type,
        IFC4_IfcPersonAndOrganization_type,
        IFC4_IfcTable_type,
        IFC4_IfcTimeSeries_type
    });
    IFC4_IfcPositiveRatioMeasure_type = new type_declaration(strings[1634], 687, new named_type(IFC4_IfcRatioMeasure_type));
    IFC4_IfcSegmentIndexSelect_type = new select_type(strings[1635], 882, {
        IFC4_IfcArcIndex_type,
        IFC4_IfcLineIndex_type
    });
    IFC4_IfcSimpleValue_type = new select_type(strings[1636], 899, {
        IFC4_IfcBinary_type,
        IFC4_IfcBoolean_type,
        IFC4_IfcDate_type,
        IFC4_IfcDateTime_type,
        IFC4_IfcDuration_type,
        IFC4_IfcIdentifier_type,
        IFC4_IfcInteger_type,
        IFC4_IfcLabel_type,
        IFC4_IfcLogical_type,
        IFC4_IfcPositiveInteger_type,
        IFC4_IfcReal_type,
        IFC4_IfcText_type,
        IFC4_IfcTime_type,
        IFC4_IfcTimeStamp_type
    });
    IFC4_IfcSizeSelect_type = new select_type(strings[1637], 904, {
        IFC4_IfcDescriptiveMeasure_type,
        IFC4_IfcLengthMeasure_type,
        IFC4_IfcNormalisedRatioMeasure_type,
        IFC4_IfcPositiveLengthMeasure_type,
        IFC4_IfcPositiveRatioMeasure_type,
        IFC4_IfcRatioMeasure_type
    });
    IFC4_IfcSpecularHighlightSelect_type = new select_type(strings[1638], 937, {
        IFC4_IfcSpecularExponent_type,
        IFC4_IfcSpecularRoughness_type
    });
    IFC4_IfcStyleAssignmentSelect_type = new select_type(strings[1639], 993, {
        IFC4_IfcPresentationStyle_type,
        IFC4_IfcPresentationStyleAssignment_type
    });
    IFC4_IfcSurfaceStyleElementSelect_type = new select_type(strings[1640], 1012, {
        IFC4_IfcExternallyDefinedSurfaceStyle_type,
        IFC4_IfcSurfaceStyleLighting_type,
        IFC4_IfcSurfaceStyleRefraction_type,
        IFC4_IfcSurfaceStyleShading_type,
        IFC4_IfcSurfaceStyleWithTextures_type
    });
    IFC4_IfcUnit_type = new select_type(strings[1641], 1110, {
        IFC4_IfcDerivedUnit_type,
        IFC4_IfcMonetaryUnit_type,
        IFC4_IfcNamedUnit_type
    });
    IFC4_IfcApprovalRelationship_type = new entity(strings[1642], false, 39, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcArbitraryClosedProfileDef_type = new entity(strings[1643], false, 40, IFC4_IfcProfileDef_type);
    IFC4_IfcArbitraryOpenProfileDef_type = new entity(strings[1644], false, 41, IFC4_IfcProfileDef_type);
    IFC4_IfcArbitraryProfileDefWithVoids_type = new entity(strings[1645], false, 42, IFC4_IfcArbitraryClosedProfileDef_type);
    IFC4_IfcBlobTexture_type = new entity(strings[1646], false, 64, IFC4_IfcSurfaceTexture_type);
    IFC4_IfcCenterLineProfileDef_type = new entity(strings[1647], false, 128, IFC4_IfcArbitraryOpenProfileDef_type);
    IFC4_IfcClassification_type = new entity(strings[1648], false, 141, IFC4_IfcExternalInformation_type);
    IFC4_IfcClassificationReference_type = new entity(strings[1649], false, 142, IFC4_IfcExternalReference_type);
    IFC4_IfcColourRgbList_type = new entity(strings[1650], false, 152, IFC4_IfcPresentationItem_type);
    IFC4_IfcColourSpecification_type = new entity(strings[1651], true, 153, IFC4_IfcPresentationItem_type);
    IFC4_IfcCompositeProfileDef_type = new entity(strings[1652], false, 168, IFC4_IfcProfileDef_type);
    IFC4_IfcConnectedFaceSet_type = new entity(strings[1653], false, 177, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcConnectionCurveGeometry_type = new entity(strings[1654], false, 178, IFC4_IfcConnectionGeometry_type);
    IFC4_IfcConnectionPointEccentricity_type = new entity(strings[1655], false, 180, IFC4_IfcConnectionPointGeometry_type);
    IFC4_IfcContextDependentUnit_type = new entity(strings[1656], false, 200, IFC4_IfcNamedUnit_type);
    IFC4_IfcConversionBasedUnit_type = new entity(strings[1657], false, 205, IFC4_IfcNamedUnit_type);
    IFC4_IfcConversionBasedUnitWithOffset_type = new entity(strings[1658], false, 206, IFC4_IfcConversionBasedUnit_type);
    IFC4_IfcCurrencyRelationship_type = new entity(strings[1659], false, 232, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcCurveStyle_type = new entity(strings[1660], false, 244, IFC4_IfcPresentationStyle_type);
    IFC4_IfcCurveStyleFont_type = new entity(strings[1661], false, 245, IFC4_IfcPresentationItem_type);
    IFC4_IfcCurveStyleFontAndScaling_type = new entity(strings[1662], false, 246, IFC4_IfcPresentationItem_type);
    IFC4_IfcCurveStyleFontPattern_type = new entity(strings[1663], false, 247, IFC4_IfcPresentationItem_type);
    IFC4_IfcDerivedProfileDef_type = new entity(strings[1664], false, 260, IFC4_IfcProfileDef_type);
    IFC4_IfcDocumentInformation_type = new entity(strings[1665], false, 287, IFC4_IfcExternalInformation_type);
    IFC4_IfcDocumentInformationRelationship_type = new entity(strings[1666], false, 288, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcDocumentReference_type = new entity(strings[1667], false, 289, IFC4_IfcExternalReference_type);
    IFC4_IfcEdge_type = new entity(strings[1668], false, 318, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcEdgeCurve_type = new entity(strings[1669], false, 319, IFC4_IfcEdge_type);
    IFC4_IfcEventTime_type = new entity(strings[1670], false, 370, IFC4_IfcSchedulingTime_type);
    IFC4_IfcExtendedProperties_type = new entity(strings[1671], true, 374, IFC4_IfcPropertyAbstraction_type);
    IFC4_IfcExternalReferenceRelationship_type = new entity(strings[1672], false, 380, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcFace_type = new entity(strings[1673], false, 386, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcFaceBound_type = new entity(strings[1674], false, 388, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcFaceOuterBound_type = new entity(strings[1675], false, 389, IFC4_IfcFaceBound_type);
    IFC4_IfcFaceSurface_type = new entity(strings[1676], false, 390, IFC4_IfcFace_type);
    IFC4_IfcFailureConnectionCondition_type = new entity(strings[1677], false, 393, IFC4_IfcStructuralConnectionCondition_type);
    IFC4_IfcFillAreaStyle_type = new entity(strings[1678], false, 403, IFC4_IfcPresentationStyle_type);
    IFC4_IfcGeometricRepresentationContext_type = new entity(strings[1679], false, 453, IFC4_IfcRepresentationContext_type);
    IFC4_IfcGeometricRepresentationItem_type = new entity(strings[1680], true, 454, IFC4_IfcRepresentationItem_type);
    IFC4_IfcGeometricRepresentationSubContext_type = new entity(strings[1681], false, 455, IFC4_IfcGeometricRepresentationContext_type);
    IFC4_IfcGeometricSet_type = new entity(strings[1682], false, 456, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcGridPlacement_type = new entity(strings[1683], false, 462, IFC4_IfcObjectPlacement_type);
    IFC4_IfcHalfSpaceSolid_type = new entity(strings[1684], false, 466, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcImageTexture_type = new entity(strings[1685], false, 478, IFC4_IfcSurfaceTexture_type);
    IFC4_IfcIndexedColourMap_type = new entity(strings[1686], false, 479, IFC4_IfcPresentationItem_type);
    IFC4_IfcIndexedTextureMap_type = new entity(strings[1687], true, 483, IFC4_IfcTextureCoordinate_type);
    IFC4_IfcIndexedTriangleTextureMap_type = new entity(strings[1688], false, 484, IFC4_IfcIndexedTextureMap_type);
    IFC4_IfcIrregularTimeSeries_type = new entity(strings[1689], false, 496, IFC4_IfcTimeSeries_type);
    IFC4_IfcLagTime_type = new entity(strings[1690], false, 509, IFC4_IfcSchedulingTime_type);
    IFC4_IfcLightSource_type = new entity(strings[1691], true, 528, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcLightSourceAmbient_type = new entity(strings[1692], false, 529, IFC4_IfcLightSource_type);
    IFC4_IfcLightSourceDirectional_type = new entity(strings[1693], false, 530, IFC4_IfcLightSource_type);
    IFC4_IfcLightSourceGoniometric_type = new entity(strings[1694], false, 531, IFC4_IfcLightSource_type);
    IFC4_IfcLightSourcePositional_type = new entity(strings[1695], false, 532, IFC4_IfcLightSource_type);
    IFC4_IfcLightSourceSpot_type = new entity(strings[1696], false, 533, IFC4_IfcLightSourcePositional_type);
    IFC4_IfcLocalPlacement_type = new entity(strings[1697], false, 541, IFC4_IfcObjectPlacement_type);
    IFC4_IfcLoop_type = new entity(strings[1698], false, 544, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcMappedItem_type = new entity(strings[1699], false, 553, IFC4_IfcRepresentationItem_type);
    IFC4_IfcMaterial_type = new entity(strings[1700], false, 558, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialConstituent_type = new entity(strings[1701], false, 560, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialConstituentSet_type = new entity(strings[1702], false, 561, IFC4_IfcMaterialDefinition_type);
    IFC4_IfcMaterialDefinitionRepresentation_type = new entity(strings[1703], false, 563, IFC4_IfcProductRepresentation_type);
    IFC4_IfcMaterialLayerSetUsage_type = new entity(strings[1704], false, 566, IFC4_IfcMaterialUsageDefinition_type);
    IFC4_IfcMaterialProfileSetUsage_type = new entity(strings[1705], false, 571, IFC4_IfcMaterialUsageDefinition_type);
    IFC4_IfcMaterialProfileSetUsageTapering_type = new entity(strings[1706], false, 572, IFC4_IfcMaterialProfileSetUsage_type);
    IFC4_IfcMaterialProperties_type = new entity(strings[1707], false, 574, IFC4_IfcExtendedProperties_type);
    IFC4_IfcMaterialRelationship_type = new entity(strings[1708], false, 575, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcMirroredProfileDef_type = new entity(strings[1709], false, 592, IFC4_IfcDerivedProfileDef_type);
    IFC4_IfcObjectDefinition_type = new entity(strings[1710], true, 615, IFC4_IfcRoot_type);
    IFC4_IfcOpenShell_type = new entity(strings[1711], false, 628, IFC4_IfcConnectedFaceSet_type);
    IFC4_IfcOrganizationRelationship_type = new entity(strings[1712], false, 630, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcOrientedEdge_type = new entity(strings[1713], false, 631, IFC4_IfcEdge_type);
    IFC4_IfcParameterizedProfileDef_type = new entity(strings[1714], true, 637, IFC4_IfcProfileDef_type);
    IFC4_IfcPath_type = new entity(strings[1715], false, 639, IFC4_IfcTopologicalRepresentationItem_type);
    IFC4_IfcPhysicalComplexQuantity_type = new entity(strings[1716], false, 650, IFC4_IfcPhysicalQuantity_type);
    IFC4_IfcPixelTexture_type = new entity(strings[1717], false, 664, IFC4_IfcSurfaceTexture_type);
    IFC4_IfcPlacement_type = new entity(strings[1718], true, 665, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcPlanarExtent_type = new entity(strings[1719], false, 667, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcPoint_type = new entity(strings[1720], true, 675, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcPointOnCurve_type = new entity(strings[1721], false, 676, IFC4_IfcPoint_type);
    IFC4_IfcPointOnSurface_type = new entity(strings[1722], false, 677, IFC4_IfcPoint_type);
    IFC4_IfcPolyLoop_type = new entity(strings[1723], false, 682, IFC4_IfcLoop_type);
    IFC4_IfcPolygonalBoundedHalfSpace_type = new entity(strings[1724], false, 679, IFC4_IfcHalfSpaceSolid_type);
    IFC4_IfcPreDefinedItem_type = new entity(strings[1725], true, 692, IFC4_IfcPresentationItem_type);
    IFC4_IfcPreDefinedProperties_type = new entity(strings[1726], true, 693, IFC4_IfcPropertyAbstraction_type);
    IFC4_IfcPreDefinedTextFont_type = new entity(strings[1727], true, 695, IFC4_IfcPreDefinedItem_type);
    IFC4_IfcProductDefinitionShape_type = new entity(strings[1728], false, 711, IFC4_IfcProductRepresentation_type);
    IFC4_IfcProfileProperties_type = new entity(strings[1729], false, 716, IFC4_IfcExtendedProperties_type);
    IFC4_IfcProperty_type = new entity(strings[1730], true, 726, IFC4_IfcPropertyAbstraction_type);
    IFC4_IfcPropertyDefinition_type = new entity(strings[1731], true, 729, IFC4_IfcRoot_type);
    IFC4_IfcPropertyDependencyRelationship_type = new entity(strings[1732], false, 730, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcPropertySetDefinition_type = new entity(strings[1733], true, 736, IFC4_IfcPropertyDefinition_type);
    IFC4_IfcPropertyTemplateDefinition_type = new entity(strings[1734], true, 744, IFC4_IfcPropertyDefinition_type);
    IFC4_IfcQuantitySet_type = new entity(strings[1735], true, 758, IFC4_IfcPropertySetDefinition_type);
    IFC4_IfcRectangleProfileDef_type = new entity(strings[1736], false, 777, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcRegularTimeSeries_type = new entity(strings[1737], false, 784, IFC4_IfcTimeSeries_type);
    IFC4_IfcReinforcementBarProperties_type = new entity(strings[1738], false, 785, IFC4_IfcPreDefinedProperties_type);
    IFC4_IfcRelationship_type = new entity(strings[1739], true, 813, IFC4_IfcRoot_type);
    IFC4_IfcResourceApprovalRelationship_type = new entity(strings[1740], false, 851, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcResourceConstraintRelationship_type = new entity(strings[1741], false, 852, IFC4_IfcResourceLevelRelationship_type);
    IFC4_IfcResourceTime_type = new entity(strings[1742], false, 856, IFC4_IfcSchedulingTime_type);
    IFC4_IfcRoundedRectangleProfileDef_type = new entity(strings[1743], false, 870, IFC4_IfcRectangleProfileDef_type);
    IFC4_IfcSectionProperties_type = new entity(strings[1744], false, 879, IFC4_IfcPreDefinedProperties_type);
    IFC4_IfcSectionReinforcementProperties_type = new entity(strings[1745], false, 880, IFC4_IfcPreDefinedProperties_type);
    IFC4_IfcSectionedSpine_type = new entity(strings[1746], false, 877, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcShellBasedSurfaceModel_type = new entity(strings[1747], false, 895, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcSimpleProperty_type = new entity(strings[1748], true, 896, IFC4_IfcProperty_type);
    IFC4_IfcSlippageConnectionCondition_type = new entity(strings[1749], false, 910, IFC4_IfcStructuralConnectionCondition_type);
    IFC4_IfcSolidModel_type = new entity(strings[1750], true, 915, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcStructuralLoadLinearForce_type = new entity(strings[1751], false, 970, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStructuralLoadPlanarForce_type = new entity(strings[1752], false, 972, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStructuralLoadSingleDisplacement_type = new entity(strings[1753], false, 973, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStructuralLoadSingleDisplacementDistortion_type = new entity(strings[1754], false, 974, IFC4_IfcStructuralLoadSingleDisplacement_type);
    IFC4_IfcStructuralLoadSingleForce_type = new entity(strings[1755], false, 975, IFC4_IfcStructuralLoadStatic_type);
    IFC4_IfcStructuralLoadSingleForceWarping_type = new entity(strings[1756], false, 976, IFC4_IfcStructuralLoadSingleForce_type);
    IFC4_IfcSubedge_type = new entity(strings[1757], false, 1000, IFC4_IfcEdge_type);
    IFC4_IfcSurface_type = new entity(strings[1758], true, 1001, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcSurfaceStyleRendering_type = new entity(strings[1759], false, 1015, IFC4_IfcSurfaceStyleShading_type);
    IFC4_IfcSweptAreaSolid_type = new entity(strings[1760], true, 1019, IFC4_IfcSolidModel_type);
    IFC4_IfcSweptDiskSolid_type = new entity(strings[1761], false, 1020, IFC4_IfcSolidModel_type);
    IFC4_IfcSweptDiskSolidPolygonal_type = new entity(strings[1762], false, 1021, IFC4_IfcSweptDiskSolid_type);
    IFC4_IfcSweptSurface_type = new entity(strings[1763], true, 1022, IFC4_IfcSurface_type);
    IFC4_IfcTShapeProfileDef_type = new entity(strings[1764], false, 1102, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcTessellatedItem_type = new entity(strings[1765], true, 1052, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcTextLiteral_type = new entity(strings[1766], false, 1058, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcTextLiteralWithExtent_type = new entity(strings[1767], false, 1059, IFC4_IfcTextLiteral_type);
    IFC4_IfcTextStyleFontModel_type = new entity(strings[1768], false, 1062, IFC4_IfcPreDefinedTextFont_type);
    IFC4_IfcTrapeziumProfileDef_type = new entity(strings[1769], false, 1097, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcTypeObject_type = new entity(strings[1770], false, 1106, IFC4_IfcObjectDefinition_type);
    IFC4_IfcTypeProcess_type = new entity(strings[1771], true, 1107, IFC4_IfcTypeObject_type);
    IFC4_IfcTypeProduct_type = new entity(strings[1772], false, 1108, IFC4_IfcTypeObject_type);
    IFC4_IfcTypeResource_type = new entity(strings[1773], true, 1109, IFC4_IfcTypeObject_type);
    IFC4_IfcUShapeProfileDef_type = new entity(strings[1774], false, 1120, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcVector_type = new entity(strings[1775], false, 1126, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcVertexLoop_type = new entity(strings[1776], false, 1129, IFC4_IfcLoop_type);
    IFC4_IfcWindowStyle_type = new entity(strings[1777], false, 1157, IFC4_IfcTypeProduct_type);
    IFC4_IfcZShapeProfileDef_type = new entity(strings[1778], false, 1172, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcClassificationReferenceSelect_type = new select_type(strings[1779], 143, {
        IFC4_IfcClassification_type,
        IFC4_IfcClassificationReference_type
    });
    IFC4_IfcClassificationSelect_type = new select_type(strings[1780], 144, {
        IFC4_IfcClassification_type,
        IFC4_IfcClassificationReference_type
    });
    IFC4_IfcCoordinateReferenceSystemSelect_type = new select_type(strings[1781], 215, {
        IFC4_IfcCoordinateReferenceSystem_type,
        IFC4_IfcGeometricRepresentationContext_type
    });
    IFC4_IfcDefinitionSelect_type = new select_type(strings[1782], 258, {
        IFC4_IfcObjectDefinition_type,
        IFC4_IfcPropertyDefinition_type
    });
    IFC4_IfcDocumentSelect_type = new select_type(strings[1783], 290, {
        IFC4_IfcDocumentInformation_type,
        IFC4_IfcDocumentReference_type
    });
    IFC4_IfcHatchLineDistanceSelect_type = new select_type(strings[1784], 467, {
        IFC4_IfcPositiveLengthMeasure_type,
        IFC4_IfcVector_type
    });
    IFC4_IfcMeasureValue_type = new select_type(strings[1785], 578, {
        IFC4_IfcAmountOfSubstanceMeasure_type,
        IFC4_IfcAreaMeasure_type,
        IFC4_IfcComplexNumber_type,
        IFC4_IfcContextDependentMeasure_type,
        IFC4_IfcCountMeasure_type,
        IFC4_IfcDescriptiveMeasure_type,
        IFC4_IfcElectricCurrentMeasure_type,
        IFC4_IfcLengthMeasure_type,
        IFC4_IfcLuminousIntensityMeasure_type,
        IFC4_IfcMassMeasure_type,
        IFC4_IfcNonNegativeLengthMeasure_type,
        IFC4_IfcNormalisedRatioMeasure_type,
        IFC4_IfcNumericMeasure_type,
        IFC4_IfcParameterValue_type,
        IFC4_IfcPlaneAngleMeasure_type,
        IFC4_IfcPositiveLengthMeasure_type,
        IFC4_IfcPositivePlaneAngleMeasure_type,
        IFC4_IfcPositiveRatioMeasure_type,
        IFC4_IfcRatioMeasure_type,
        IFC4_IfcSolidAngleMeasure_type,
        IFC4_IfcThermodynamicTemperatureMeasure_type,
        IFC4_IfcTimeMeasure_type,
        IFC4_IfcVolumeMeasure_type
    });
    IFC4_IfcPointOrVertexPoint_type = new select_type(strings[1786], 678, {
        IFC4_IfcPoint_type,
        IFC4_IfcVertexPoint_type
    });
    IFC4_IfcPresentationStyleSelect_type = new select_type(strings[1787], 703, {
        IFC4_IfcCurveStyle_type,
        IFC4_IfcFillAreaStyle_type,
        IFC4_IfcNullStyle_type,
        IFC4_IfcSurfaceStyle_type,
        IFC4_IfcTextStyle_type
    });
    IFC4_IfcProductRepresentationSelect_type = new select_type(strings[1788], 713, {
        IFC4_IfcProductDefinitionShape_type,
        IFC4_IfcRepresentationMap_type
    });
    IFC4_IfcPropertySetDefinitionSet_type = new type_declaration(strings[1789], 738, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertySetDefinition_type)));
    IFC4_IfcResourceObjectSelect_type = new select_type(strings[1790], 854, {
        IFC4_IfcActorRole_type,
        IFC4_IfcAppliedValue_type,
        IFC4_IfcApproval_type,
        IFC4_IfcConstraint_type,
        IFC4_IfcContextDependentUnit_type,
        IFC4_IfcConversionBasedUnit_type,
        IFC4_IfcExternalInformation_type,
        IFC4_IfcExternalReference_type,
        IFC4_IfcMaterialDefinition_type,
        IFC4_IfcOrganization_type,
        IFC4_IfcPerson_type,
        IFC4_IfcPersonAndOrganization_type,
        IFC4_IfcPhysicalQuantity_type,
        IFC4_IfcProfileDef_type,
        IFC4_IfcPropertyAbstraction_type,
        IFC4_IfcTimeSeries_type
    });
    IFC4_IfcTextFontSelect_type = new select_type(strings[1791], 1057, {
        IFC4_IfcExternallyDefinedTextFont_type,
        IFC4_IfcPreDefinedTextFont_type
    });
    IFC4_IfcValue_type = new select_type(strings[1792], 1121, {
        IFC4_IfcDerivedMeasureValue_type,
        IFC4_IfcMeasureValue_type,
        IFC4_IfcSimpleValue_type
    });
    IFC4_IfcAdvancedFace_type = new entity(strings[1793], false, 16, IFC4_IfcFaceSurface_type);
    IFC4_IfcAnnotationFillArea_type = new entity(strings[1794], false, 34, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcAsymmetricIShapeProfileDef_type = new entity(strings[1795], false, 49, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcAxis1Placement_type = new entity(strings[1796], false, 53, IFC4_IfcPlacement_type);
    IFC4_IfcAxis2Placement2D_type = new entity(strings[1797], false, 55, IFC4_IfcPlacement_type);
    IFC4_IfcAxis2Placement3D_type = new entity(strings[1798], false, 56, IFC4_IfcPlacement_type);
    IFC4_IfcBooleanResult_type = new entity(strings[1799], false, 73, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcBoundedSurface_type = new entity(strings[1800], true, 81, IFC4_IfcSurface_type);
    IFC4_IfcBoundingBox_type = new entity(strings[1801], false, 82, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcBoxedHalfSpace_type = new entity(strings[1802], false, 84, IFC4_IfcHalfSpaceSolid_type);
    IFC4_IfcCShapeProfileDef_type = new entity(strings[1803], false, 231, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcCartesianPoint_type = new entity(strings[1804], false, 119, IFC4_IfcPoint_type);
    IFC4_IfcCartesianPointList_type = new entity(strings[1805], true, 120, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcCartesianPointList2D_type = new entity(strings[1806], false, 121, IFC4_IfcCartesianPointList_type);
    IFC4_IfcCartesianPointList3D_type = new entity(strings[1807], false, 122, IFC4_IfcCartesianPointList_type);
    IFC4_IfcCartesianTransformationOperator_type = new entity(strings[1808], true, 123, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcCartesianTransformationOperator2D_type = new entity(strings[1809], false, 124, IFC4_IfcCartesianTransformationOperator_type);
    IFC4_IfcCartesianTransformationOperator2DnonUniform_type = new entity(strings[1810], false, 125, IFC4_IfcCartesianTransformationOperator2D_type);
    IFC4_IfcCartesianTransformationOperator3D_type = new entity(strings[1811], false, 126, IFC4_IfcCartesianTransformationOperator_type);
    IFC4_IfcCartesianTransformationOperator3DnonUniform_type = new entity(strings[1812], false, 127, IFC4_IfcCartesianTransformationOperator3D_type);
    IFC4_IfcCircleProfileDef_type = new entity(strings[1813], false, 138, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcClosedShell_type = new entity(strings[1814], false, 145, IFC4_IfcConnectedFaceSet_type);
    IFC4_IfcColourRgb_type = new entity(strings[1815], false, 151, IFC4_IfcColourSpecification_type);
    IFC4_IfcComplexProperty_type = new entity(strings[1816], false, 162, IFC4_IfcProperty_type);
    IFC4_IfcCompositeCurveSegment_type = new entity(strings[1817], false, 167, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcConstructionResourceType_type = new entity(strings[1818], true, 197, IFC4_IfcTypeResource_type);
    IFC4_IfcContext_type = new entity(strings[1819], true, 198, IFC4_IfcObjectDefinition_type);
    IFC4_IfcCrewResourceType_type = new entity(strings[1820], false, 226, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcCsgPrimitive3D_type = new entity(strings[1821], true, 228, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcCsgSolid_type = new entity(strings[1822], false, 230, IFC4_IfcSolidModel_type);
    IFC4_IfcCurve_type = new entity(strings[1823], true, 237, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcCurveBoundedPlane_type = new entity(strings[1824], false, 238, IFC4_IfcBoundedSurface_type);
    IFC4_IfcCurveBoundedSurface_type = new entity(strings[1825], false, 239, IFC4_IfcBoundedSurface_type);
    IFC4_IfcDirection_type = new entity(strings[1826], false, 267, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcDoorStyle_type = new entity(strings[1827], false, 298, IFC4_IfcTypeProduct_type);
    IFC4_IfcEdgeLoop_type = new entity(strings[1828], false, 320, IFC4_IfcLoop_type);
    IFC4_IfcElementQuantity_type = new entity(strings[1829], false, 353, IFC4_IfcQuantitySet_type);
    IFC4_IfcElementType_type = new entity(strings[1830], true, 354, IFC4_IfcTypeProduct_type);
    IFC4_IfcElementarySurface_type = new entity(strings[1831], true, 346, IFC4_IfcSurface_type);
    IFC4_IfcEllipseProfileDef_type = new entity(strings[1832], false, 356, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcEventType_type = new entity(strings[1833], false, 372, IFC4_IfcTypeProcess_type);
    IFC4_IfcExtrudedAreaSolid_type = new entity(strings[1834], false, 384, IFC4_IfcSweptAreaSolid_type);
    IFC4_IfcExtrudedAreaSolidTapered_type = new entity(strings[1835], false, 385, IFC4_IfcExtrudedAreaSolid_type);
    IFC4_IfcFaceBasedSurfaceModel_type = new entity(strings[1836], false, 387, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcFillAreaStyleHatching_type = new entity(strings[1837], false, 404, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcFillAreaStyleTiles_type = new entity(strings[1838], false, 405, IFC4_IfcGeometricRepresentationItem_type);
    IFC4_IfcFixedReferenceSweptAreaSolid_type = new entity(strings[1839], false, 413, IFC4_IfcSweptAreaSolid_type);
    IFC4_IfcFurnishingElementType_type = new entity(strings[1840], false, 444, IFC4_IfcElementType_type);
    IFC4_IfcFurnitureType_type = new entity(strings[1841], false, 446, IFC4_IfcFurnishingElementType_type);
    IFC4_IfcGeographicElementType_type = new entity(strings[1842], false, 449, IFC4_IfcElementType_type);
    IFC4_IfcGeometricCurveSet_type = new entity(strings[1843], false, 451, IFC4_IfcGeometricSet_type);
    IFC4_IfcIShapeProfileDef_type = new entity(strings[1844], false, 498, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcIndexedPolygonalFace_type = new entity(strings[1845], false, 481, IFC4_IfcTessellatedItem_type);
    IFC4_IfcIndexedPolygonalFaceWithVoids_type = new entity(strings[1846], false, 482, IFC4_IfcIndexedPolygonalFace_type);
    IFC4_IfcLShapeProfileDef_type = new entity(strings[1847], false, 545, IFC4_IfcParameterizedProfileDef_type);
    IFC4_IfcLaborResourceType_type = new entity(strings[1848], false, 507, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcLine_type = new entity(strings[1849], false, 534, IFC4_IfcCurve_type);
    IFC4_IfcManifoldSolidBrep_type = new entity(strings[1850], true, 551, IFC4_IfcSolidModel_type);
    IFC4_IfcObject_type = new entity(strings[1851], true, 614, IFC4_IfcObjectDefinition_type);
    IFC4_IfcOffsetCurve2D_type = new entity(strings[1852], false, 623, IFC4_IfcCurve_type);
    IFC4_IfcOffsetCurve3D_type = new entity(strings[1853], false, 624, IFC4_IfcCurve_type);
    IFC4_IfcPcurve_type = new entity(strings[1854], false, 640, IFC4_IfcCurve_type);
    IFC4_IfcPlanarBox_type = new entity(strings[1855], false, 666, IFC4_IfcPlanarExtent_type);
    IFC4_IfcPlane_type = new entity(strings[1856], false, 669, IFC4_IfcElementarySurface_type);
    IFC4_IfcPreDefinedColour_type = new entity(strings[1857], true, 690, IFC4_IfcPreDefinedItem_type);
    IFC4_IfcPreDefinedCurveFont_type = new entity(strings[1858], true, 691, IFC4_IfcPreDefinedItem_type);
    IFC4_IfcPreDefinedPropertySet_type = new entity(strings[1859], true, 694, IFC4_IfcPropertySetDefinition_type);
    IFC4_IfcProcedureType_type = new entity(strings[1860], false, 706, IFC4_IfcTypeProcess_type);
    IFC4_IfcProcess_type = new entity(strings[1861], true, 708, IFC4_IfcObject_type);
    IFC4_IfcProduct_type = new entity(strings[1862], true, 710, IFC4_IfcObject_type);
    IFC4_IfcProject_type = new entity(strings[1863], false, 718, IFC4_IfcContext_type);
    IFC4_IfcProjectLibrary_type = new entity(strings[1864], false, 723, IFC4_IfcContext_type);
    IFC4_IfcPropertyBoundedValue_type = new entity(strings[1865], false, 728, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyEnumeratedValue_type = new entity(strings[1866], false, 731, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyListValue_type = new entity(strings[1867], false, 733, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyReferenceValue_type = new entity(strings[1868], false, 734, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertySet_type = new entity(strings[1869], false, 735, IFC4_IfcPropertySetDefinition_type);
    IFC4_IfcPropertySetTemplate_type = new entity(strings[1870], false, 739, IFC4_IfcPropertyTemplateDefinition_type);
    IFC4_IfcPropertySingleValue_type = new entity(strings[1871], false, 741, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyTableValue_type = new entity(strings[1872], false, 742, IFC4_IfcSimpleProperty_type);
    IFC4_IfcPropertyTemplate_type = new entity(strings[1873], true, 743, IFC4_IfcPropertyTemplateDefinition_type);
    IFC4_IfcProxy_type = new entity(strings[1874], false, 751, IFC4_IfcProduct_type);
    IFC4_IfcRectangleHollowProfileDef_type = new entity(strings[1875], false, 776, IFC4_IfcRectangleProfileDef_type);
    IFC4_IfcRectangularPyramid_type = new entity(strings[1876], false, 778, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcRectangularTrimmedSurface_type = new entity(strings[1877], false, 779, IFC4_IfcBoundedSurface_type);
    IFC4_IfcReinforcementDefinitionProperties_type = new entity(strings[1878], false, 786, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcRelAssigns_type = new entity(strings[1879], true, 798, IFC4_IfcRelationship_type);
    IFC4_IfcRelAssignsToActor_type = new entity(strings[1880], false, 799, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToControl_type = new entity(strings[1881], false, 800, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToGroup_type = new entity(strings[1882], false, 801, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToGroupByFactor_type = new entity(strings[1883], false, 802, IFC4_IfcRelAssignsToGroup_type);
    IFC4_IfcRelAssignsToProcess_type = new entity(strings[1884], false, 803, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToProduct_type = new entity(strings[1885], false, 804, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssignsToResource_type = new entity(strings[1886], false, 805, IFC4_IfcRelAssigns_type);
    IFC4_IfcRelAssociates_type = new entity(strings[1887], true, 806, IFC4_IfcRelationship_type);
    IFC4_IfcRelAssociatesApproval_type = new entity(strings[1888], false, 807, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesClassification_type = new entity(strings[1889], false, 808, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesConstraint_type = new entity(strings[1890], false, 809, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesDocument_type = new entity(strings[1891], false, 810, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesLibrary_type = new entity(strings[1892], false, 811, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelAssociatesMaterial_type = new entity(strings[1893], false, 812, IFC4_IfcRelAssociates_type);
    IFC4_IfcRelConnects_type = new entity(strings[1894], true, 814, IFC4_IfcRelationship_type);
    IFC4_IfcRelConnectsElements_type = new entity(strings[1895], false, 815, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsPathElements_type = new entity(strings[1896], false, 816, IFC4_IfcRelConnectsElements_type);
    IFC4_IfcRelConnectsPortToElement_type = new entity(strings[1897], false, 818, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsPorts_type = new entity(strings[1898], false, 817, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsStructuralActivity_type = new entity(strings[1899], false, 819, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsStructuralMember_type = new entity(strings[1900], false, 820, IFC4_IfcRelConnects_type);
    IFC4_IfcRelConnectsWithEccentricity_type = new entity(strings[1901], false, 821, IFC4_IfcRelConnectsStructuralMember_type);
    IFC4_IfcRelConnectsWithRealizingElements_type = new entity(strings[1902], false, 822, IFC4_IfcRelConnectsElements_type);
    IFC4_IfcRelContainedInSpatialStructure_type = new entity(strings[1903], false, 823, IFC4_IfcRelConnects_type);
    IFC4_IfcRelCoversBldgElements_type = new entity(strings[1904], false, 824, IFC4_IfcRelConnects_type);
    IFC4_IfcRelCoversSpaces_type = new entity(strings[1905], false, 825, IFC4_IfcRelConnects_type);
    IFC4_IfcRelDeclares_type = new entity(strings[1906], false, 826, IFC4_IfcRelationship_type);
    IFC4_IfcRelDecomposes_type = new entity(strings[1907], true, 827, IFC4_IfcRelationship_type);
    IFC4_IfcRelDefines_type = new entity(strings[1908], true, 828, IFC4_IfcRelationship_type);
    IFC4_IfcRelDefinesByObject_type = new entity(strings[1909], false, 829, IFC4_IfcRelDefines_type);
    IFC4_IfcRelDefinesByProperties_type = new entity(strings[1910], false, 830, IFC4_IfcRelDefines_type);
    IFC4_IfcRelDefinesByTemplate_type = new entity(strings[1911], false, 831, IFC4_IfcRelDefines_type);
    IFC4_IfcRelDefinesByType_type = new entity(strings[1912], false, 832, IFC4_IfcRelDefines_type);
    IFC4_IfcRelFillsElement_type = new entity(strings[1913], false, 833, IFC4_IfcRelConnects_type);
    IFC4_IfcRelFlowControlElements_type = new entity(strings[1914], false, 834, IFC4_IfcRelConnects_type);
    IFC4_IfcRelInterferesElements_type = new entity(strings[1915], false, 835, IFC4_IfcRelConnects_type);
    IFC4_IfcRelNests_type = new entity(strings[1916], false, 836, IFC4_IfcRelDecomposes_type);
    IFC4_IfcRelProjectsElement_type = new entity(strings[1917], false, 837, IFC4_IfcRelDecomposes_type);
    IFC4_IfcRelReferencedInSpatialStructure_type = new entity(strings[1918], false, 838, IFC4_IfcRelConnects_type);
    IFC4_IfcRelSequence_type = new entity(strings[1919], false, 839, IFC4_IfcRelConnects_type);
    IFC4_IfcRelServicesBuildings_type = new entity(strings[1920], false, 840, IFC4_IfcRelConnects_type);
    IFC4_IfcRelSpaceBoundary_type = new entity(strings[1921], false, 841, IFC4_IfcRelConnects_type);
    IFC4_IfcRelSpaceBoundary1stLevel_type = new entity(strings[1922], false, 842, IFC4_IfcRelSpaceBoundary_type);
    IFC4_IfcRelSpaceBoundary2ndLevel_type = new entity(strings[1923], false, 843, IFC4_IfcRelSpaceBoundary1stLevel_type);
    IFC4_IfcRelVoidsElement_type = new entity(strings[1924], false, 844, IFC4_IfcRelDecomposes_type);
    IFC4_IfcReparametrisedCompositeCurveSegment_type = new entity(strings[1925], false, 845, IFC4_IfcCompositeCurveSegment_type);
    IFC4_IfcResource_type = new entity(strings[1926], true, 850, IFC4_IfcObject_type);
    IFC4_IfcRevolvedAreaSolid_type = new entity(strings[1927], false, 857, IFC4_IfcSweptAreaSolid_type);
    IFC4_IfcRevolvedAreaSolidTapered_type = new entity(strings[1928], false, 858, IFC4_IfcRevolvedAreaSolid_type);
    IFC4_IfcRightCircularCone_type = new entity(strings[1929], false, 859, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcRightCircularCylinder_type = new entity(strings[1930], false, 860, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcSimplePropertyTemplate_type = new entity(strings[1931], false, 897, IFC4_IfcPropertyTemplate_type);
    IFC4_IfcSpatialElement_type = new entity(strings[1932], true, 928, IFC4_IfcProduct_type);
    IFC4_IfcSpatialElementType_type = new entity(strings[1933], true, 929, IFC4_IfcTypeProduct_type);
    IFC4_IfcSpatialStructureElement_type = new entity(strings[1934], true, 930, IFC4_IfcSpatialElement_type);
    IFC4_IfcSpatialStructureElementType_type = new entity(strings[1935], true, 931, IFC4_IfcSpatialElementType_type);
    IFC4_IfcSpatialZone_type = new entity(strings[1936], false, 932, IFC4_IfcSpatialElement_type);
    IFC4_IfcSpatialZoneType_type = new entity(strings[1937], false, 933, IFC4_IfcSpatialElementType_type);
    IFC4_IfcSphere_type = new entity(strings[1938], false, 939, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcSphericalSurface_type = new entity(strings[1939], false, 940, IFC4_IfcElementarySurface_type);
    IFC4_IfcStructuralActivity_type = new entity(strings[1940], true, 952, IFC4_IfcProduct_type);
    IFC4_IfcStructuralItem_type = new entity(strings[1941], true, 964, IFC4_IfcProduct_type);
    IFC4_IfcStructuralMember_type = new entity(strings[1942], true, 979, IFC4_IfcStructuralItem_type);
    IFC4_IfcStructuralReaction_type = new entity(strings[1943], true, 984, IFC4_IfcStructuralActivity_type);
    IFC4_IfcStructuralSurfaceMember_type = new entity(strings[1944], false, 989, IFC4_IfcStructuralMember_type);
    IFC4_IfcStructuralSurfaceMemberVarying_type = new entity(strings[1945], false, 991, IFC4_IfcStructuralSurfaceMember_type);
    IFC4_IfcStructuralSurfaceReaction_type = new entity(strings[1946], false, 992, IFC4_IfcStructuralReaction_type);
    IFC4_IfcSubContractResourceType_type = new entity(strings[1947], false, 998, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcSurfaceCurve_type = new entity(strings[1948], false, 1002, IFC4_IfcCurve_type);
    IFC4_IfcSurfaceCurveSweptAreaSolid_type = new entity(strings[1949], false, 1003, IFC4_IfcSweptAreaSolid_type);
    IFC4_IfcSurfaceOfLinearExtrusion_type = new entity(strings[1950], false, 1006, IFC4_IfcSweptSurface_type);
    IFC4_IfcSurfaceOfRevolution_type = new entity(strings[1951], false, 1007, IFC4_IfcSweptSurface_type);
    IFC4_IfcSystemFurnitureElementType_type = new entity(strings[1952], false, 1028, IFC4_IfcFurnishingElementType_type);
    IFC4_IfcTask_type = new entity(strings[1953], false, 1036, IFC4_IfcProcess_type);
    IFC4_IfcTaskType_type = new entity(strings[1954], false, 1040, IFC4_IfcTypeProcess_type);
    IFC4_IfcTessellatedFaceSet_type = new entity(strings[1955], true, 1051, IFC4_IfcTessellatedItem_type);
    IFC4_IfcToroidalSurface_type = new entity(strings[1956], false, 1087, IFC4_IfcElementarySurface_type);
    IFC4_IfcTransportElementType_type = new entity(strings[1957], false, 1095, IFC4_IfcElementType_type);
    IFC4_IfcTriangulatedFaceSet_type = new entity(strings[1958], false, 1098, IFC4_IfcTessellatedFaceSet_type);
    IFC4_IfcWindowLiningProperties_type = new entity(strings[1959], false, 1152, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcWindowPanelProperties_type = new entity(strings[1960], false, 1155, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcAppliedValueSelect_type = new select_type(strings[1961], 37, {
        IFC4_IfcMeasureWithUnit_type,
        IFC4_IfcReference_type,
        IFC4_IfcValue_type
    });
    IFC4_IfcAxis2Placement_type = new select_type(strings[1962], 54, {
        IFC4_IfcAxis2Placement2D_type,
        IFC4_IfcAxis2Placement3D_type
    });
    IFC4_IfcBooleanOperand_type = new select_type(strings[1963], 71, {
        IFC4_IfcBooleanResult_type,
        IFC4_IfcCsgPrimitive3D_type,
        IFC4_IfcHalfSpaceSolid_type,
        IFC4_IfcSolidModel_type,
        IFC4_IfcTessellatedFaceSet_type
    });
    IFC4_IfcColour_type = new select_type(strings[1964], 149, {
        IFC4_IfcColourSpecification_type,
        IFC4_IfcPreDefinedColour_type
    });
    IFC4_IfcColourOrFactor_type = new select_type(strings[1965], 150, {
        IFC4_IfcColourRgb_type,
        IFC4_IfcNormalisedRatioMeasure_type
    });
    IFC4_IfcCsgSelect_type = new select_type(strings[1966], 229, {
        IFC4_IfcBooleanResult_type,
        IFC4_IfcCsgPrimitive3D_type
    });
    IFC4_IfcCurveStyleFontSelect_type = new select_type(strings[1967], 248, {
        IFC4_IfcCurveStyleFont_type,
        IFC4_IfcPreDefinedCurveFont_type
    });
    IFC4_IfcFillStyleSelect_type = new select_type(strings[1968], 406, {
        IFC4_IfcColour_type,
        IFC4_IfcExternallyDefinedHatchStyle_type,
        IFC4_IfcFillAreaStyleHatching_type,
        IFC4_IfcFillAreaStyleTiles_type
    });
    IFC4_IfcGeometricSetSelect_type = new select_type(strings[1969], 457, {
        IFC4_IfcCurve_type,
        IFC4_IfcPoint_type,
        IFC4_IfcSurface_type
    });
    IFC4_IfcGridPlacementDirectionSelect_type = new select_type(strings[1970], 463, {
        IFC4_IfcDirection_type,
        IFC4_IfcVirtualGridIntersection_type
    });
    IFC4_IfcMetricValueSelect_type = new select_type(strings[1971], 591, {
        IFC4_IfcAppliedValue_type,
        IFC4_IfcMeasureWithUnit_type,
        IFC4_IfcReference_type,
        IFC4_IfcTable_type,
        IFC4_IfcTimeSeries_type,
        IFC4_IfcValue_type
    });
    IFC4_IfcProcessSelect_type = new select_type(strings[1972], 709, {
        IFC4_IfcProcess_type,
        IFC4_IfcTypeProcess_type
    });
    IFC4_IfcProductSelect_type = new select_type(strings[1973], 714, {
        IFC4_IfcProduct_type,
        IFC4_IfcTypeProduct_type
    });
    IFC4_IfcPropertySetDefinitionSelect_type = new select_type(strings[1974], 737, {
        IFC4_IfcPropertySetDefinition_type,
        IFC4_IfcPropertySetDefinitionSet_type
    });
    IFC4_IfcResourceSelect_type = new select_type(strings[1975], 855, {
        IFC4_IfcResource_type,
        IFC4_IfcTypeResource_type
    });
    IFC4_IfcShell_type = new select_type(strings[1976], 894, {
        IFC4_IfcClosedShell_type,
        IFC4_IfcOpenShell_type
    });
    IFC4_IfcSolidOrShell_type = new select_type(strings[1977], 916, {
        IFC4_IfcClosedShell_type,
        IFC4_IfcSolidModel_type
    });
    IFC4_IfcSurfaceOrFaceSurface_type = new select_type(strings[1978], 1008, {
        IFC4_IfcFaceBasedSurfaceModel_type,
        IFC4_IfcFaceSurface_type,
        IFC4_IfcSurface_type
    });
    IFC4_IfcTrimmingSelect_type = new select_type(strings[1979], 1101, {
        IFC4_IfcCartesianPoint_type,
        IFC4_IfcParameterValue_type
    });
    IFC4_IfcVectorOrDirection_type = new select_type(strings[1980], 1127, {
        IFC4_IfcDirection_type,
        IFC4_IfcVector_type
    });
    IFC4_IfcActor_type = new entity(strings[1981], false, 6, IFC4_IfcObject_type);
    IFC4_IfcAdvancedBrep_type = new entity(strings[1982], false, 14, IFC4_IfcManifoldSolidBrep_type);
    IFC4_IfcAdvancedBrepWithVoids_type = new entity(strings[1983], false, 15, IFC4_IfcAdvancedBrep_type);
    IFC4_IfcAnnotation_type = new entity(strings[1984], false, 33, IFC4_IfcProduct_type);
    IFC4_IfcBSplineSurface_type = new entity(strings[1985], true, 88, IFC4_IfcBoundedSurface_type);
    IFC4_IfcBSplineSurfaceWithKnots_type = new entity(strings[1986], false, 90, IFC4_IfcBSplineSurface_type);
    IFC4_IfcBlock_type = new entity(strings[1987], false, 65, IFC4_IfcCsgPrimitive3D_type);
    IFC4_IfcBooleanClippingResult_type = new entity(strings[1988], false, 70, IFC4_IfcBooleanResult_type);
    IFC4_IfcBoundedCurve_type = new entity(strings[1989], true, 80, IFC4_IfcCurve_type);
    IFC4_IfcBuilding_type = new entity(strings[1990], false, 91, IFC4_IfcSpatialStructureElement_type);
    IFC4_IfcBuildingElementType_type = new entity(strings[1991], true, 99, IFC4_IfcElementType_type);
    IFC4_IfcBuildingStorey_type = new entity(strings[1992], false, 100, IFC4_IfcSpatialStructureElement_type);
    IFC4_IfcChimneyType_type = new entity(strings[1993], false, 134, IFC4_IfcBuildingElementType_type);
    IFC4_IfcCircleHollowProfileDef_type = new entity(strings[1994], false, 137, IFC4_IfcCircleProfileDef_type);
    IFC4_IfcCivilElementType_type = new entity(strings[1995], false, 140, IFC4_IfcElementType_type);
    IFC4_IfcColumnType_type = new entity(strings[1996], false, 156, IFC4_IfcBuildingElementType_type);
    IFC4_IfcComplexPropertyTemplate_type = new entity(strings[1997], false, 163, IFC4_IfcPropertyTemplate_type);
    IFC4_IfcCompositeCurve_type = new entity(strings[1998], false, 165, IFC4_IfcBoundedCurve_type);
    IFC4_IfcCompositeCurveOnSurface_type = new entity(strings[1999], false, 166, IFC4_IfcCompositeCurve_type);
    IFC4_IfcConic_type = new entity(strings[2000], true, 176, IFC4_IfcCurve_type);
    IFC4_IfcConstructionEquipmentResourceType_type = new entity(strings[2001], false, 188, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcConstructionMaterialResourceType_type = new entity(strings[2002], false, 191, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcConstructionProductResourceType_type = new entity(strings[2003], false, 194, IFC4_IfcConstructionResourceType_type);
    IFC4_IfcConstructionResource_type = new entity(strings[2004], true, 196, IFC4_IfcResource_type);
    IFC4_IfcControl_type = new entity(strings[2005], true, 201, IFC4_IfcObject_type);
    IFC4_IfcCostItem_type = new entity(strings[2006], false, 216, IFC4_IfcControl_type);
    IFC4_IfcCostSchedule_type = new entity(strings[2007], false, 218, IFC4_IfcControl_type);
    IFC4_IfcCoveringType_type = new entity(strings[2008], false, 223, IFC4_IfcBuildingElementType_type);
    IFC4_IfcCrewResource_type = new entity(strings[2009], false, 225, IFC4_IfcConstructionResource_type);
    IFC4_IfcCurtainWallType_type = new entity(strings[2010], false, 234, IFC4_IfcBuildingElementType_type);
    IFC4_IfcCylindricalSurface_type = new entity(strings[2011], false, 249, IFC4_IfcElementarySurface_type);
    IFC4_IfcDistributionElementType_type = new entity(strings[2012], false, 279, IFC4_IfcElementType_type);
    IFC4_IfcDistributionFlowElementType_type = new entity(strings[2013], true, 281, IFC4_IfcDistributionElementType_type);
    IFC4_IfcDoorLiningProperties_type = new entity(strings[2014], false, 293, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcDoorPanelProperties_type = new entity(strings[2015], false, 296, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcDoorType_type = new entity(strings[2016], false, 301, IFC4_IfcBuildingElementType_type);
    IFC4_IfcDraughtingPreDefinedColour_type = new entity(strings[2017], false, 305, IFC4_IfcPreDefinedColour_type);
    IFC4_IfcDraughtingPreDefinedCurveFont_type = new entity(strings[2018], false, 306, IFC4_IfcPreDefinedCurveFont_type);
    IFC4_IfcElement_type = new entity(strings[2019], true, 345, IFC4_IfcProduct_type);
    IFC4_IfcElementAssembly_type = new entity(strings[2020], false, 347, IFC4_IfcElement_type);
    IFC4_IfcElementAssemblyType_type = new entity(strings[2021], false, 348, IFC4_IfcElementType_type);
    IFC4_IfcElementComponent_type = new entity(strings[2022], true, 350, IFC4_IfcElement_type);
    IFC4_IfcElementComponentType_type = new entity(strings[2023], true, 351, IFC4_IfcElementType_type);
    IFC4_IfcEllipse_type = new entity(strings[2024], false, 355, IFC4_IfcConic_type);
    IFC4_IfcEnergyConversionDeviceType_type = new entity(strings[2025], true, 358, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcEngineType_type = new entity(strings[2026], false, 361, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcEvaporativeCoolerType_type = new entity(strings[2027], false, 364, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcEvaporatorType_type = new entity(strings[2028], false, 367, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcEvent_type = new entity(strings[2029], false, 369, IFC4_IfcProcess_type);
    IFC4_IfcExternalSpatialStructureElement_type = new entity(strings[2030], true, 383, IFC4_IfcSpatialElement_type);
    IFC4_IfcFacetedBrep_type = new entity(strings[2031], false, 391, IFC4_IfcManifoldSolidBrep_type);
    IFC4_IfcFacetedBrepWithVoids_type = new entity(strings[2032], false, 392, IFC4_IfcFacetedBrep_type);
    IFC4_IfcFastener_type = new entity(strings[2033], false, 397, IFC4_IfcElementComponent_type);
    IFC4_IfcFastenerType_type = new entity(strings[2034], false, 398, IFC4_IfcElementComponentType_type);
    IFC4_IfcFeatureElement_type = new entity(strings[2035], true, 400, IFC4_IfcElement_type);
    IFC4_IfcFeatureElementAddition_type = new entity(strings[2036], true, 401, IFC4_IfcFeatureElement_type);
    IFC4_IfcFeatureElementSubtraction_type = new entity(strings[2037], true, 402, IFC4_IfcFeatureElement_type);
    IFC4_IfcFlowControllerType_type = new entity(strings[2038], true, 415, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowFittingType_type = new entity(strings[2039], true, 418, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowMeterType_type = new entity(strings[2040], false, 423, IFC4_IfcFlowControllerType_type);
    IFC4_IfcFlowMovingDeviceType_type = new entity(strings[2041], true, 426, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowSegmentType_type = new entity(strings[2042], true, 428, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowStorageDeviceType_type = new entity(strings[2043], true, 430, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowTerminalType_type = new entity(strings[2044], true, 432, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFlowTreatmentDeviceType_type = new entity(strings[2045], true, 434, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcFootingType_type = new entity(strings[2046], false, 439, IFC4_IfcBuildingElementType_type);
    IFC4_IfcFurnishingElement_type = new entity(strings[2047], false, 443, IFC4_IfcElement_type);
    IFC4_IfcFurniture_type = new entity(strings[2048], false, 445, IFC4_IfcFurnishingElement_type);
    IFC4_IfcGeographicElement_type = new entity(strings[2049], false, 448, IFC4_IfcElement_type);
    IFC4_IfcGrid_type = new entity(strings[2050], false, 460, IFC4_IfcProduct_type);
    IFC4_IfcGroup_type = new entity(strings[2051], false, 465, IFC4_IfcObject_type);
    IFC4_IfcHeatExchangerType_type = new entity(strings[2052], false, 469, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcHumidifierType_type = new entity(strings[2053], false, 474, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcIndexedPolyCurve_type = new entity(strings[2054], false, 480, IFC4_IfcBoundedCurve_type);
    IFC4_IfcInterceptorType_type = new entity(strings[2055], false, 489, IFC4_IfcFlowTreatmentDeviceType_type);
    IFC4_IfcIntersectionCurve_type = new entity(strings[2056], false, 492, IFC4_IfcSurfaceCurve_type);
    IFC4_IfcInventory_type = new entity(strings[2057], false, 493, IFC4_IfcGroup_type);
    IFC4_IfcJunctionBoxType_type = new entity(strings[2058], false, 501, IFC4_IfcFlowFittingType_type);
    IFC4_IfcLaborResource_type = new entity(strings[2059], false, 506, IFC4_IfcConstructionResource_type);
    IFC4_IfcLampType_type = new entity(strings[2060], false, 511, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcLightFixtureType_type = new entity(strings[2061], false, 525, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcMechanicalFastener_type = new entity(strings[2062], false, 580, IFC4_IfcElementComponent_type);
    IFC4_IfcMechanicalFastenerType_type = new entity(strings[2063], false, 581, IFC4_IfcElementComponentType_type);
    IFC4_IfcMedicalDeviceType_type = new entity(strings[2064], false, 584, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcMemberType_type = new entity(strings[2065], false, 588, IFC4_IfcBuildingElementType_type);
    IFC4_IfcMotorConnectionType_type = new entity(strings[2066], false, 607, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcOccupant_type = new entity(strings[2067], false, 621, IFC4_IfcActor_type);
    IFC4_IfcOpeningElement_type = new entity(strings[2068], false, 625, IFC4_IfcFeatureElementSubtraction_type);
    IFC4_IfcOpeningStandardCase_type = new entity(strings[2069], false, 627, IFC4_IfcOpeningElement_type);
    IFC4_IfcOutletType_type = new entity(strings[2070], false, 634, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcPerformanceHistory_type = new entity(strings[2071], false, 641, IFC4_IfcControl_type);
    IFC4_IfcPermeableCoveringProperties_type = new entity(strings[2072], false, 644, IFC4_IfcPreDefinedPropertySet_type);
    IFC4_IfcPermit_type = new entity(strings[2073], false, 645, IFC4_IfcControl_type);
    IFC4_IfcPileType_type = new entity(strings[2074], false, 656, IFC4_IfcBuildingElementType_type);
    IFC4_IfcPipeFittingType_type = new entity(strings[2075], false, 659, IFC4_IfcFlowFittingType_type);
    IFC4_IfcPipeSegmentType_type = new entity(strings[2076], false, 662, IFC4_IfcFlowSegmentType_type);
    IFC4_IfcPlateType_type = new entity(strings[2077], false, 673, IFC4_IfcBuildingElementType_type);
    IFC4_IfcPolygonalFaceSet_type = new entity(strings[2078], false, 680, IFC4_IfcTessellatedFaceSet_type);
    IFC4_IfcPolyline_type = new entity(strings[2079], false, 681, IFC4_IfcBoundedCurve_type);
    IFC4_IfcPort_type = new entity(strings[2080], true, 683, IFC4_IfcProduct_type);
    IFC4_IfcProcedure_type = new entity(strings[2081], false, 705, IFC4_IfcProcess_type);
    IFC4_IfcProjectOrder_type = new entity(strings[2082], false, 724, IFC4_IfcControl_type);
    IFC4_IfcProjectionElement_type = new entity(strings[2083], false, 721, IFC4_IfcFeatureElementAddition_type);
    IFC4_IfcProtectiveDeviceType_type = new entity(strings[2084], false, 749, IFC4_IfcFlowControllerType_type);
    IFC4_IfcPumpType_type = new entity(strings[2085], false, 753, IFC4_IfcFlowMovingDeviceType_type);
    IFC4_IfcRailingType_type = new entity(strings[2086], false, 764, IFC4_IfcBuildingElementType_type);
    IFC4_IfcRampFlightType_type = new entity(strings[2087], false, 768, IFC4_IfcBuildingElementType_type);
    IFC4_IfcRampType_type = new entity(strings[2088], false, 770, IFC4_IfcBuildingElementType_type);
    IFC4_IfcRationalBSplineSurfaceWithKnots_type = new entity(strings[2089], false, 774, IFC4_IfcBSplineSurfaceWithKnots_type);
    IFC4_IfcReinforcingElement_type = new entity(strings[2090], true, 792, IFC4_IfcElementComponent_type);
    IFC4_IfcReinforcingElementType_type = new entity(strings[2091], true, 793, IFC4_IfcElementComponentType_type);
    IFC4_IfcReinforcingMesh_type = new entity(strings[2092], false, 794, IFC4_IfcReinforcingElement_type);
    IFC4_IfcReinforcingMeshType_type = new entity(strings[2093], false, 795, IFC4_IfcReinforcingElementType_type);
    IFC4_IfcRelAggregates_type = new entity(strings[2094], false, 797, IFC4_IfcRelDecomposes_type);
    IFC4_IfcRoofType_type = new entity(strings[2095], false, 863, IFC4_IfcBuildingElementType_type);
    IFC4_IfcSanitaryTerminalType_type = new entity(strings[2096], false, 872, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcSeamCurve_type = new entity(strings[2097], false, 875, IFC4_IfcSurfaceCurve_type);
    IFC4_IfcShadingDeviceType_type = new entity(strings[2098], false, 888, IFC4_IfcBuildingElementType_type);
    IFC4_IfcSite_type = new entity(strings[2099], false, 901, IFC4_IfcSpatialStructureElement_type);
    IFC4_IfcSlabType_type = new entity(strings[2100], false, 908, IFC4_IfcBuildingElementType_type);
    IFC4_IfcSolarDeviceType_type = new entity(strings[2101], false, 912, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcSpace_type = new entity(strings[2102], false, 921, IFC4_IfcSpatialStructureElement_type);
    IFC4_IfcSpaceHeaterType_type = new entity(strings[2103], false, 924, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcSpaceType_type = new entity(strings[2104], false, 926, IFC4_IfcSpatialStructureElementType_type);
    IFC4_IfcStackTerminalType_type = new entity(strings[2105], false, 942, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcStairFlightType_type = new entity(strings[2106], false, 946, IFC4_IfcBuildingElementType_type);
    IFC4_IfcStairType_type = new entity(strings[2107], false, 948, IFC4_IfcBuildingElementType_type);
    IFC4_IfcStructuralAction_type = new entity(strings[2108], true, 951, IFC4_IfcStructuralActivity_type);
    IFC4_IfcStructuralConnection_type = new entity(strings[2109], true, 955, IFC4_IfcStructuralItem_type);
    IFC4_IfcStructuralCurveAction_type = new entity(strings[2110], false, 957, IFC4_IfcStructuralAction_type);
    IFC4_IfcStructuralCurveConnection_type = new entity(strings[2111], false, 959, IFC4_IfcStructuralConnection_type);
    IFC4_IfcStructuralCurveMember_type = new entity(strings[2112], false, 960, IFC4_IfcStructuralMember_type);
    IFC4_IfcStructuralCurveMemberVarying_type = new entity(strings[2113], false, 962, IFC4_IfcStructuralCurveMember_type);
    IFC4_IfcStructuralCurveReaction_type = new entity(strings[2114], false, 963, IFC4_IfcStructuralReaction_type);
    IFC4_IfcStructuralLinearAction_type = new entity(strings[2115], false, 965, IFC4_IfcStructuralCurveAction_type);
    IFC4_IfcStructuralLoadGroup_type = new entity(strings[2116], false, 969, IFC4_IfcGroup_type);
    IFC4_IfcStructuralPointAction_type = new entity(strings[2117], false, 981, IFC4_IfcStructuralAction_type);
    IFC4_IfcStructuralPointConnection_type = new entity(strings[2118], false, 982, IFC4_IfcStructuralConnection_type);
    IFC4_IfcStructuralPointReaction_type = new entity(strings[2119], false, 983, IFC4_IfcStructuralReaction_type);
    IFC4_IfcStructuralResultGroup_type = new entity(strings[2120], false, 985, IFC4_IfcGroup_type);
    IFC4_IfcStructuralSurfaceAction_type = new entity(strings[2121], false, 986, IFC4_IfcStructuralAction_type);
    IFC4_IfcStructuralSurfaceConnection_type = new entity(strings[2122], false, 988, IFC4_IfcStructuralConnection_type);
    IFC4_IfcSubContractResource_type = new entity(strings[2123], false, 997, IFC4_IfcConstructionResource_type);
    IFC4_IfcSurfaceFeature_type = new entity(strings[2124], false, 1004, IFC4_IfcFeatureElement_type);
    IFC4_IfcSwitchingDeviceType_type = new entity(strings[2125], false, 1024, IFC4_IfcFlowControllerType_type);
    IFC4_IfcSystem_type = new entity(strings[2126], false, 1026, IFC4_IfcGroup_type);
    IFC4_IfcSystemFurnitureElement_type = new entity(strings[2127], false, 1027, IFC4_IfcFurnishingElement_type);
    IFC4_IfcTankType_type = new entity(strings[2128], false, 1034, IFC4_IfcFlowStorageDeviceType_type);
    IFC4_IfcTendon_type = new entity(strings[2129], false, 1045, IFC4_IfcReinforcingElement_type);
    IFC4_IfcTendonAnchor_type = new entity(strings[2130], false, 1046, IFC4_IfcReinforcingElement_type);
    IFC4_IfcTendonAnchorType_type = new entity(strings[2131], false, 1047, IFC4_IfcReinforcingElementType_type);
    IFC4_IfcTendonType_type = new entity(strings[2132], false, 1049, IFC4_IfcReinforcingElementType_type);
    IFC4_IfcTransformerType_type = new entity(strings[2133], false, 1090, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcTransportElement_type = new entity(strings[2134], false, 1094, IFC4_IfcElement_type);
    IFC4_IfcTrimmedCurve_type = new entity(strings[2135], false, 1099, IFC4_IfcBoundedCurve_type);
    IFC4_IfcTubeBundleType_type = new entity(strings[2136], false, 1104, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcUnitaryEquipmentType_type = new entity(strings[2137], false, 1115, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcValveType_type = new entity(strings[2138], false, 1123, IFC4_IfcFlowControllerType_type);
    IFC4_IfcVibrationIsolator_type = new entity(strings[2139], false, 1131, IFC4_IfcElementComponent_type);
    IFC4_IfcVibrationIsolatorType_type = new entity(strings[2140], false, 1132, IFC4_IfcElementComponentType_type);
    IFC4_IfcVirtualElement_type = new entity(strings[2141], false, 1134, IFC4_IfcElement_type);
    IFC4_IfcVoidingFeature_type = new entity(strings[2142], false, 1136, IFC4_IfcFeatureElementSubtraction_type);
    IFC4_IfcWallType_type = new entity(strings[2143], false, 1143, IFC4_IfcBuildingElementType_type);
    IFC4_IfcWasteTerminalType_type = new entity(strings[2144], false, 1149, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcWindowType_type = new entity(strings[2145], false, 1160, IFC4_IfcBuildingElementType_type);
    IFC4_IfcWorkCalendar_type = new entity(strings[2146], false, 1163, IFC4_IfcControl_type);
    IFC4_IfcWorkControl_type = new entity(strings[2147], true, 1165, IFC4_IfcControl_type);
    IFC4_IfcWorkPlan_type = new entity(strings[2148], false, 1166, IFC4_IfcWorkControl_type);
    IFC4_IfcWorkSchedule_type = new entity(strings[2149], false, 1168, IFC4_IfcWorkControl_type);
    IFC4_IfcZone_type = new entity(strings[2150], false, 1171, IFC4_IfcSystem_type);
    IFC4_IfcCurveFontOrScaledCurveFontSelect_type = new select_type(strings[2151], 240, {
        IFC4_IfcCurveStyleFontAndScaling_type,
        IFC4_IfcCurveStyleFontSelect_type
    });
    IFC4_IfcCurveOnSurface_type = new select_type(strings[2152], 242, {
        IFC4_IfcCompositeCurveOnSurface_type,
        IFC4_IfcPcurve_type,
        IFC4_IfcSurfaceCurve_type
    });
    IFC4_IfcCurveOrEdgeCurve_type = new select_type(strings[2153], 243, {
        IFC4_IfcBoundedCurve_type,
        IFC4_IfcEdgeCurve_type
    });
    IFC4_IfcStructuralActivityAssignmentSelect_type = new select_type(strings[2154], 953, {
        IFC4_IfcElement_type,
        IFC4_IfcStructuralItem_type
    });
    IFC4_IfcActionRequest_type = new entity(strings[2155], false, 2, IFC4_IfcControl_type);
    IFC4_IfcAirTerminalBoxType_type = new entity(strings[2156], false, 19, IFC4_IfcFlowControllerType_type);
    IFC4_IfcAirTerminalType_type = new entity(strings[2157], false, 21, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcAirToAirHeatRecoveryType_type = new entity(strings[2158], false, 24, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcAsset_type = new entity(strings[2159], false, 48, IFC4_IfcGroup_type);
    IFC4_IfcAudioVisualApplianceType_type = new entity(strings[2160], false, 51, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcBSplineCurve_type = new entity(strings[2161], true, 85, IFC4_IfcBoundedCurve_type);
    IFC4_IfcBSplineCurveWithKnots_type = new entity(strings[2162], false, 87, IFC4_IfcBSplineCurve_type);
    IFC4_IfcBeamType_type = new entity(strings[2163], false, 59, IFC4_IfcBuildingElementType_type);
    IFC4_IfcBoilerType_type = new entity(strings[2164], false, 67, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcBoundaryCurve_type = new entity(strings[2165], false, 75, IFC4_IfcCompositeCurveOnSurface_type);
    IFC4_IfcBuildingElement_type = new entity(strings[2166], true, 92, IFC4_IfcElement_type);
    IFC4_IfcBuildingElementPart_type = new entity(strings[2167], false, 93, IFC4_IfcElementComponent_type);
    IFC4_IfcBuildingElementPartType_type = new entity(strings[2168], false, 94, IFC4_IfcElementComponentType_type);
    IFC4_IfcBuildingElementProxy_type = new entity(strings[2169], false, 96, IFC4_IfcBuildingElement_type);
    IFC4_IfcBuildingElementProxyType_type = new entity(strings[2170], false, 97, IFC4_IfcBuildingElementType_type);
    IFC4_IfcBuildingSystem_type = new entity(strings[2171], false, 101, IFC4_IfcSystem_type);
    IFC4_IfcBurnerType_type = new entity(strings[2172], false, 104, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcCableCarrierFittingType_type = new entity(strings[2173], false, 107, IFC4_IfcFlowFittingType_type);
    IFC4_IfcCableCarrierSegmentType_type = new entity(strings[2174], false, 110, IFC4_IfcFlowSegmentType_type);
    IFC4_IfcCableFittingType_type = new entity(strings[2175], false, 113, IFC4_IfcFlowFittingType_type);
    IFC4_IfcCableSegmentType_type = new entity(strings[2176], false, 116, IFC4_IfcFlowSegmentType_type);
    IFC4_IfcChillerType_type = new entity(strings[2177], false, 131, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcChimney_type = new entity(strings[2178], false, 133, IFC4_IfcBuildingElement_type);
    IFC4_IfcCircle_type = new entity(strings[2179], false, 136, IFC4_IfcConic_type);
    IFC4_IfcCivilElement_type = new entity(strings[2180], false, 139, IFC4_IfcElement_type);
    IFC4_IfcCoilType_type = new entity(strings[2181], false, 147, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcColumn_type = new entity(strings[2182], false, 154, IFC4_IfcBuildingElement_type);
    IFC4_IfcColumnStandardCase_type = new entity(strings[2183], false, 155, IFC4_IfcColumn_type);
    IFC4_IfcCommunicationsApplianceType_type = new entity(strings[2184], false, 159, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcCompressorType_type = new entity(strings[2185], false, 171, IFC4_IfcFlowMovingDeviceType_type);
    IFC4_IfcCondenserType_type = new entity(strings[2186], false, 174, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcConstructionEquipmentResource_type = new entity(strings[2187], false, 187, IFC4_IfcConstructionResource_type);
    IFC4_IfcConstructionMaterialResource_type = new entity(strings[2188], false, 190, IFC4_IfcConstructionResource_type);
    IFC4_IfcConstructionProductResource_type = new entity(strings[2189], false, 193, IFC4_IfcConstructionResource_type);
    IFC4_IfcCooledBeamType_type = new entity(strings[2190], false, 208, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcCoolingTowerType_type = new entity(strings[2191], false, 211, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcCovering_type = new entity(strings[2192], false, 222, IFC4_IfcBuildingElement_type);
    IFC4_IfcCurtainWall_type = new entity(strings[2193], false, 233, IFC4_IfcBuildingElement_type);
    IFC4_IfcDamperType_type = new entity(strings[2194], false, 251, IFC4_IfcFlowControllerType_type);
    IFC4_IfcDiscreteAccessory_type = new entity(strings[2195], false, 269, IFC4_IfcElementComponent_type);
    IFC4_IfcDiscreteAccessoryType_type = new entity(strings[2196], false, 270, IFC4_IfcElementComponentType_type);
    IFC4_IfcDistributionChamberElementType_type = new entity(strings[2197], false, 273, IFC4_IfcDistributionFlowElementType_type);
    IFC4_IfcDistributionControlElementType_type = new entity(strings[2198], true, 277, IFC4_IfcDistributionElementType_type);
    IFC4_IfcDistributionElement_type = new entity(strings[2199], false, 278, IFC4_IfcElement_type);
    IFC4_IfcDistributionFlowElement_type = new entity(strings[2200], false, 280, IFC4_IfcDistributionElement_type);
    IFC4_IfcDistributionPort_type = new entity(strings[2201], false, 282, IFC4_IfcPort_type);
    IFC4_IfcDistributionSystem_type = new entity(strings[2202], false, 284, IFC4_IfcSystem_type);
    IFC4_IfcDoor_type = new entity(strings[2203], false, 292, IFC4_IfcBuildingElement_type);
    IFC4_IfcDoorStandardCase_type = new entity(strings[2204], false, 297, IFC4_IfcDoor_type);
    IFC4_IfcDuctFittingType_type = new entity(strings[2205], false, 308, IFC4_IfcFlowFittingType_type);
    IFC4_IfcDuctSegmentType_type = new entity(strings[2206], false, 311, IFC4_IfcFlowSegmentType_type);
    IFC4_IfcDuctSilencerType_type = new entity(strings[2207], false, 314, IFC4_IfcFlowTreatmentDeviceType_type);
    IFC4_IfcElectricApplianceType_type = new entity(strings[2208], false, 322, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcElectricDistributionBoardType_type = new entity(strings[2209], false, 329, IFC4_IfcFlowControllerType_type);
    IFC4_IfcElectricFlowStorageDeviceType_type = new entity(strings[2210], false, 332, IFC4_IfcFlowStorageDeviceType_type);
    IFC4_IfcElectricGeneratorType_type = new entity(strings[2211], false, 335, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcElectricMotorType_type = new entity(strings[2212], false, 338, IFC4_IfcEnergyConversionDeviceType_type);
    IFC4_IfcElectricTimeControlType_type = new entity(strings[2213], false, 342, IFC4_IfcFlowControllerType_type);
    IFC4_IfcEnergyConversionDevice_type = new entity(strings[2214], false, 357, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcEngine_type = new entity(strings[2215], false, 360, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcEvaporativeCooler_type = new entity(strings[2216], false, 363, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcEvaporator_type = new entity(strings[2217], false, 366, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcExternalSpatialElement_type = new entity(strings[2218], false, 381, IFC4_IfcExternalSpatialStructureElement_type);
    IFC4_IfcFanType_type = new entity(strings[2219], false, 395, IFC4_IfcFlowMovingDeviceType_type);
    IFC4_IfcFilterType_type = new entity(strings[2220], false, 408, IFC4_IfcFlowTreatmentDeviceType_type);
    IFC4_IfcFireSuppressionTerminalType_type = new entity(strings[2221], false, 411, IFC4_IfcFlowTerminalType_type);
    IFC4_IfcFlowController_type = new entity(strings[2222], false, 414, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowFitting_type = new entity(strings[2223], false, 417, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowInstrumentType_type = new entity(strings[2224], false, 420, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcFlowMeter_type = new entity(strings[2225], false, 422, IFC4_IfcFlowController_type);
    IFC4_IfcFlowMovingDevice_type = new entity(strings[2226], false, 425, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowSegment_type = new entity(strings[2227], false, 427, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowStorageDevice_type = new entity(strings[2228], false, 429, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowTerminal_type = new entity(strings[2229], false, 431, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFlowTreatmentDevice_type = new entity(strings[2230], false, 433, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcFooting_type = new entity(strings[2231], false, 438, IFC4_IfcBuildingElement_type);
    IFC4_IfcHeatExchanger_type = new entity(strings[2232], false, 468, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcHumidifier_type = new entity(strings[2233], false, 473, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcInterceptor_type = new entity(strings[2234], false, 488, IFC4_IfcFlowTreatmentDevice_type);
    IFC4_IfcJunctionBox_type = new entity(strings[2235], false, 500, IFC4_IfcFlowFitting_type);
    IFC4_IfcLamp_type = new entity(strings[2236], false, 510, IFC4_IfcFlowTerminal_type);
    IFC4_IfcLightFixture_type = new entity(strings[2237], false, 524, IFC4_IfcFlowTerminal_type);
    IFC4_IfcMedicalDevice_type = new entity(strings[2238], false, 583, IFC4_IfcFlowTerminal_type);
    IFC4_IfcMember_type = new entity(strings[2239], false, 586, IFC4_IfcBuildingElement_type);
    IFC4_IfcMemberStandardCase_type = new entity(strings[2240], false, 587, IFC4_IfcMember_type);
    IFC4_IfcMotorConnection_type = new entity(strings[2241], false, 606, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcOuterBoundaryCurve_type = new entity(strings[2242], false, 632, IFC4_IfcBoundaryCurve_type);
    IFC4_IfcOutlet_type = new entity(strings[2243], false, 633, IFC4_IfcFlowTerminal_type);
    IFC4_IfcPile_type = new entity(strings[2244], false, 654, IFC4_IfcBuildingElement_type);
    IFC4_IfcPipeFitting_type = new entity(strings[2245], false, 658, IFC4_IfcFlowFitting_type);
    IFC4_IfcPipeSegment_type = new entity(strings[2246], false, 661, IFC4_IfcFlowSegment_type);
    IFC4_IfcPlate_type = new entity(strings[2247], false, 671, IFC4_IfcBuildingElement_type);
    IFC4_IfcPlateStandardCase_type = new entity(strings[2248], false, 672, IFC4_IfcPlate_type);
    IFC4_IfcProtectiveDevice_type = new entity(strings[2249], false, 745, IFC4_IfcFlowController_type);
    IFC4_IfcProtectiveDeviceTrippingUnitType_type = new entity(strings[2250], false, 747, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcPump_type = new entity(strings[2251], false, 752, IFC4_IfcFlowMovingDevice_type);
    IFC4_IfcRailing_type = new entity(strings[2252], false, 763, IFC4_IfcBuildingElement_type);
    IFC4_IfcRamp_type = new entity(strings[2253], false, 766, IFC4_IfcBuildingElement_type);
    IFC4_IfcRampFlight_type = new entity(strings[2254], false, 767, IFC4_IfcBuildingElement_type);
    IFC4_IfcRationalBSplineCurveWithKnots_type = new entity(strings[2255], false, 773, IFC4_IfcBSplineCurveWithKnots_type);
    IFC4_IfcReinforcingBar_type = new entity(strings[2256], false, 787, IFC4_IfcReinforcingElement_type);
    IFC4_IfcReinforcingBarType_type = new entity(strings[2257], false, 790, IFC4_IfcReinforcingElementType_type);
    IFC4_IfcRoof_type = new entity(strings[2258], false, 862, IFC4_IfcBuildingElement_type);
    IFC4_IfcSanitaryTerminal_type = new entity(strings[2259], false, 871, IFC4_IfcFlowTerminal_type);
    IFC4_IfcSensorType_type = new entity(strings[2260], false, 884, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcShadingDevice_type = new entity(strings[2261], false, 887, IFC4_IfcBuildingElement_type);
    IFC4_IfcSlab_type = new entity(strings[2262], false, 905, IFC4_IfcBuildingElement_type);
    IFC4_IfcSlabElementedCase_type = new entity(strings[2263], false, 906, IFC4_IfcSlab_type);
    IFC4_IfcSlabStandardCase_type = new entity(strings[2264], false, 907, IFC4_IfcSlab_type);
    IFC4_IfcSolarDevice_type = new entity(strings[2265], false, 911, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcSpaceHeater_type = new entity(strings[2266], false, 923, IFC4_IfcFlowTerminal_type);
    IFC4_IfcStackTerminal_type = new entity(strings[2267], false, 941, IFC4_IfcFlowTerminal_type);
    IFC4_IfcStair_type = new entity(strings[2268], false, 944, IFC4_IfcBuildingElement_type);
    IFC4_IfcStairFlight_type = new entity(strings[2269], false, 945, IFC4_IfcBuildingElement_type);
    IFC4_IfcStructuralAnalysisModel_type = new entity(strings[2270], false, 954, IFC4_IfcSystem_type);
    IFC4_IfcStructuralLoadCase_type = new entity(strings[2271], false, 967, IFC4_IfcStructuralLoadGroup_type);
    IFC4_IfcStructuralPlanarAction_type = new entity(strings[2272], false, 980, IFC4_IfcStructuralSurfaceAction_type);
    IFC4_IfcSwitchingDevice_type = new entity(strings[2273], false, 1023, IFC4_IfcFlowController_type);
    IFC4_IfcTank_type = new entity(strings[2274], false, 1033, IFC4_IfcFlowStorageDevice_type);
    IFC4_IfcTransformer_type = new entity(strings[2275], false, 1089, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcTubeBundle_type = new entity(strings[2276], false, 1103, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcUnitaryControlElementType_type = new entity(strings[2277], false, 1112, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcUnitaryEquipment_type = new entity(strings[2278], false, 1114, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcValve_type = new entity(strings[2279], false, 1122, IFC4_IfcFlowController_type);
    IFC4_IfcWall_type = new entity(strings[2280], false, 1140, IFC4_IfcBuildingElement_type);
    IFC4_IfcWallElementedCase_type = new entity(strings[2281], false, 1141, IFC4_IfcWall_type);
    IFC4_IfcWallStandardCase_type = new entity(strings[2282], false, 1142, IFC4_IfcWall_type);
    IFC4_IfcWasteTerminal_type = new entity(strings[2283], false, 1148, IFC4_IfcFlowTerminal_type);
    IFC4_IfcWindow_type = new entity(strings[2284], false, 1151, IFC4_IfcBuildingElement_type);
    IFC4_IfcWindowStandardCase_type = new entity(strings[2285], false, 1156, IFC4_IfcWindow_type);
    IFC4_IfcSpaceBoundarySelect_type = new select_type(strings[2286], 922, {
        IFC4_IfcExternalSpatialElement_type,
        IFC4_IfcSpace_type
    });
    IFC4_IfcActuatorType_type = new entity(strings[2287], false, 10, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcAirTerminal_type = new entity(strings[2288], false, 17, IFC4_IfcFlowTerminal_type);
    IFC4_IfcAirTerminalBox_type = new entity(strings[2289], false, 18, IFC4_IfcFlowController_type);
    IFC4_IfcAirToAirHeatRecovery_type = new entity(strings[2290], false, 23, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcAlarmType_type = new entity(strings[2291], false, 27, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcAudioVisualAppliance_type = new entity(strings[2292], false, 50, IFC4_IfcFlowTerminal_type);
    IFC4_IfcBeam_type = new entity(strings[2293], false, 57, IFC4_IfcBuildingElement_type);
    IFC4_IfcBeamStandardCase_type = new entity(strings[2294], false, 58, IFC4_IfcBeam_type);
    IFC4_IfcBoiler_type = new entity(strings[2295], false, 66, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcBurner_type = new entity(strings[2296], false, 103, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcCableCarrierFitting_type = new entity(strings[2297], false, 106, IFC4_IfcFlowFitting_type);
    IFC4_IfcCableCarrierSegment_type = new entity(strings[2298], false, 109, IFC4_IfcFlowSegment_type);
    IFC4_IfcCableFitting_type = new entity(strings[2299], false, 112, IFC4_IfcFlowFitting_type);
    IFC4_IfcCableSegment_type = new entity(strings[2300], false, 115, IFC4_IfcFlowSegment_type);
    IFC4_IfcChiller_type = new entity(strings[2301], false, 130, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcCoil_type = new entity(strings[2302], false, 146, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcCommunicationsAppliance_type = new entity(strings[2303], false, 158, IFC4_IfcFlowTerminal_type);
    IFC4_IfcCompressor_type = new entity(strings[2304], false, 170, IFC4_IfcFlowMovingDevice_type);
    IFC4_IfcCondenser_type = new entity(strings[2305], false, 173, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcControllerType_type = new entity(strings[2306], false, 203, IFC4_IfcDistributionControlElementType_type);
    IFC4_IfcCooledBeam_type = new entity(strings[2307], false, 207, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcCoolingTower_type = new entity(strings[2308], false, 210, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcDamper_type = new entity(strings[2309], false, 250, IFC4_IfcFlowController_type);
    IFC4_IfcDistributionChamberElement_type = new entity(strings[2310], false, 272, IFC4_IfcDistributionFlowElement_type);
    IFC4_IfcDistributionCircuit_type = new entity(strings[2311], false, 275, IFC4_IfcDistributionSystem_type);
    IFC4_IfcDistributionControlElement_type = new entity(strings[2312], false, 276, IFC4_IfcDistributionElement_type);
    IFC4_IfcDuctFitting_type = new entity(strings[2313], false, 307, IFC4_IfcFlowFitting_type);
    IFC4_IfcDuctSegment_type = new entity(strings[2314], false, 310, IFC4_IfcFlowSegment_type);
    IFC4_IfcDuctSilencer_type = new entity(strings[2315], false, 313, IFC4_IfcFlowTreatmentDevice_type);
    IFC4_IfcElectricAppliance_type = new entity(strings[2316], false, 321, IFC4_IfcFlowTerminal_type);
    IFC4_IfcElectricDistributionBoard_type = new entity(strings[2317], false, 328, IFC4_IfcFlowController_type);
    IFC4_IfcElectricFlowStorageDevice_type = new entity(strings[2318], false, 331, IFC4_IfcFlowStorageDevice_type);
    IFC4_IfcElectricGenerator_type = new entity(strings[2319], false, 334, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcElectricMotor_type = new entity(strings[2320], false, 337, IFC4_IfcEnergyConversionDevice_type);
    IFC4_IfcElectricTimeControl_type = new entity(strings[2321], false, 341, IFC4_IfcFlowController_type);
    IFC4_IfcFan_type = new entity(strings[2322], false, 394, IFC4_IfcFlowMovingDevice_type);
    IFC4_IfcFilter_type = new entity(strings[2323], false, 407, IFC4_IfcFlowTreatmentDevice_type);
    IFC4_IfcFireSuppressionTerminal_type = new entity(strings[2324], false, 410, IFC4_IfcFlowTerminal_type);
    IFC4_IfcFlowInstrument_type = new entity(strings[2325], false, 419, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcProtectiveDeviceTrippingUnit_type = new entity(strings[2326], false, 746, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcSensor_type = new entity(strings[2327], false, 883, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcUnitaryControlElement_type = new entity(strings[2328], false, 1111, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcActuator_type = new entity(strings[2329], false, 9, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcAlarm_type = new entity(strings[2330], false, 26, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcController_type = new entity(strings[2331], false, 202, IFC4_IfcDistributionControlElement_type);
    IFC4_IfcActionRequest_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcActionRequestTypeEnum_type), true),
            new attribute(strings[2333], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2334], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcActor_type->set_attributes({
            new attribute(strings[2335], new named_type(IFC4_IfcActorSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcActorRole_type->set_attributes({
            new attribute(strings[2336], new named_type(IFC4_IfcRoleEnum_type), false),
            new attribute(strings[2337], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false
    });
    IFC4_IfcActuator_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcActuatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcActuatorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcActuatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAddress_type->set_attributes({
            new attribute(strings[2339], new named_type(IFC4_IfcAddressTypeEnum_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2340], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4_IfcAdvancedBrep_type->set_attributes({
    },{
            false
    });
    IFC4_IfcAdvancedBrepWithVoids_type->set_attributes({
            new attribute(strings[2341], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcClosedShell_type)), false)
    },{
            false, false
    });
    IFC4_IfcAdvancedFace_type->set_attributes({
    },{
            false, false, false
    });
    IFC4_IfcAirTerminal_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAirTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAirTerminalBox_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAirTerminalBoxTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAirTerminalBoxType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAirTerminalBoxTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAirTerminalType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAirTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAirToAirHeatRecovery_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAirToAirHeatRecoveryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAirToAirHeatRecoveryType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAirToAirHeatRecoveryTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAlarm_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAlarmTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAlarmType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAlarmTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAnnotation_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcAnnotationFillArea_type->set_attributes({
            new attribute(strings[2342], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2343], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcCurve_type)), true)
    },{
            false, false
    });
    IFC4_IfcApplication_type->set_attributes({
            new attribute(strings[2344], new named_type(IFC4_IfcOrganization_type), false),
            new attribute(strings[2345], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2346], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2347], new named_type(IFC4_IfcIdentifier_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcAppliedValue_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2349], new named_type(IFC4_IfcAppliedValueSelect_type), true),
            new attribute(strings[2350], new named_type(IFC4_IfcMeasureWithUnit_type), true),
            new attribute(strings[2351], new named_type(IFC4_IfcDate_type), true),
            new attribute(strings[2352], new named_type(IFC4_IfcDate_type), true),
            new attribute(strings[2353], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2354], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2355], new named_type(IFC4_IfcArithmeticOperatorEnum_type), true),
            new attribute(strings[2356], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAppliedValue_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcApproval_type->set_attributes({
            new attribute(strings[2357], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2358], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2333], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2359], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2360], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2361], new named_type(IFC4_IfcActorSelect_type), true),
            new attribute(strings[2362], new named_type(IFC4_IfcActorSelect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcApprovalRelationship_type->set_attributes({
            new attribute(strings[2363], new named_type(IFC4_IfcApproval_type), false),
            new attribute(strings[2364], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcApproval_type)), false)
    },{
            false, false, false, false
    });
    IFC4_IfcArbitraryClosedProfileDef_type->set_attributes({
            new attribute(strings[2365], new named_type(IFC4_IfcCurve_type), false)
    },{
            false, false, false
    });
    IFC4_IfcArbitraryOpenProfileDef_type->set_attributes({
            new attribute(strings[2366], new named_type(IFC4_IfcBoundedCurve_type), false)
    },{
            false, false, false
    });
    IFC4_IfcArbitraryProfileDefWithVoids_type->set_attributes({
            new attribute(strings[2367], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcCurve_type)), false)
    },{
            false, false, false, false
    });
    IFC4_IfcAsset_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2369], new named_type(IFC4_IfcCostValue_type), true),
            new attribute(strings[2370], new named_type(IFC4_IfcCostValue_type), true),
            new attribute(strings[2371], new named_type(IFC4_IfcCostValue_type), true),
            new attribute(strings[2372], new named_type(IFC4_IfcActorSelect_type), true),
            new attribute(strings[2373], new named_type(IFC4_IfcActorSelect_type), true),
            new attribute(strings[2374], new named_type(IFC4_IfcPerson_type), true),
            new attribute(strings[2375], new named_type(IFC4_IfcDate_type), true),
            new attribute(strings[2376], new named_type(IFC4_IfcCostValue_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAsymmetricIShapeProfileDef_type->set_attributes({
            new attribute(strings[2377], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2378], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2379], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2380], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2381], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2382], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2383], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2384], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2385], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2386], new named_type(IFC4_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[2387], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2388], new named_type(IFC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAudioVisualAppliance_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAudioVisualApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAudioVisualApplianceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAudioVisualApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcAxis1Placement_type->set_attributes({
            new attribute(strings[2389], new named_type(IFC4_IfcDirection_type), true)
    },{
            false, false
    });
    IFC4_IfcAxis2Placement2D_type->set_attributes({
            new attribute(strings[2390], new named_type(IFC4_IfcDirection_type), true)
    },{
            false, false
    });
    IFC4_IfcAxis2Placement3D_type->set_attributes({
            new attribute(strings[2389], new named_type(IFC4_IfcDirection_type), true),
            new attribute(strings[2390], new named_type(IFC4_IfcDirection_type), true)
    },{
            false, false, false
    });
    IFC4_IfcBSplineCurve_type->set_attributes({
            new attribute(strings[2391], new named_type(IFC4_IfcInteger_type), false),
            new attribute(strings[2392], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcCartesianPoint_type)), false),
            new attribute(strings[2393], new named_type(IFC4_IfcBSplineCurveForm_type), false),
            new attribute(strings[2394], new named_type(IFC4_IfcLogical_type), false),
            new attribute(strings[2395], new named_type(IFC4_IfcLogical_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcBSplineCurveWithKnots_type->set_attributes({
            new attribute(strings[2396], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcInteger_type)), false),
            new attribute(strings[2397], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcParameterValue_type)), false),
            new attribute(strings[2398], new named_type(IFC4_IfcKnotType_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcBSplineSurface_type->set_attributes({
            new attribute(strings[2399], new named_type(IFC4_IfcInteger_type), false),
            new attribute(strings[2400], new named_type(IFC4_IfcInteger_type), false),
            new attribute(strings[2392], new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcCartesianPoint_type))), false),
            new attribute(strings[2401], new named_type(IFC4_IfcBSplineSurfaceForm_type), false),
            new attribute(strings[2402], new named_type(IFC4_IfcLogical_type), false),
            new attribute(strings[2403], new named_type(IFC4_IfcLogical_type), false),
            new attribute(strings[2395], new named_type(IFC4_IfcLogical_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcBSplineSurfaceWithKnots_type->set_attributes({
            new attribute(strings[2404], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcInteger_type)), false),
            new attribute(strings[2405], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcInteger_type)), false),
            new attribute(strings[2406], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcParameterValue_type)), false),
            new attribute(strings[2407], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcParameterValue_type)), false),
            new attribute(strings[2398], new named_type(IFC4_IfcKnotType_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBeam_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBeamTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBeamStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBeamType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBeamTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBlobTexture_type->set_attributes({
            new attribute(strings[2408], new named_type(IFC4_IfcIdentifier_type), false),
            new attribute(strings[2409], new named_type(IFC4_IfcBinary_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcBlock_type->set_attributes({
            new attribute(strings[2410], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2411], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2412], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcBoiler_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBoilerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBoilerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBoilerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBooleanClippingResult_type->set_attributes({
    },{
            false, false, false
    });
    IFC4_IfcBooleanResult_type->set_attributes({
            new attribute(strings[2413], new named_type(IFC4_IfcBooleanOperator_type), false),
            new attribute(strings[2414], new named_type(IFC4_IfcBooleanOperand_type), false),
            new attribute(strings[2415], new named_type(IFC4_IfcBooleanOperand_type), false)
    },{
            false, false, false
    });
    IFC4_IfcBoundaryCondition_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4_IfcBoundaryCurve_type->set_attributes({
    },{
            false, false
    });
    IFC4_IfcBoundaryEdgeCondition_type->set_attributes({
            new attribute(strings[2416], new named_type(IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2417], new named_type(IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2418], new named_type(IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2419], new named_type(IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true),
            new attribute(strings[2420], new named_type(IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true),
            new attribute(strings[2421], new named_type(IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcBoundaryFaceCondition_type->set_attributes({
            new attribute(strings[2422], new named_type(IFC4_IfcModulusOfSubgradeReactionSelect_type), true),
            new attribute(strings[2423], new named_type(IFC4_IfcModulusOfSubgradeReactionSelect_type), true),
            new attribute(strings[2424], new named_type(IFC4_IfcModulusOfSubgradeReactionSelect_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcBoundaryNodeCondition_type->set_attributes({
            new attribute(strings[2425], new named_type(IFC4_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2426], new named_type(IFC4_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2427], new named_type(IFC4_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2428], new named_type(IFC4_IfcRotationalStiffnessSelect_type), true),
            new attribute(strings[2429], new named_type(IFC4_IfcRotationalStiffnessSelect_type), true),
            new attribute(strings[2430], new named_type(IFC4_IfcRotationalStiffnessSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcBoundaryNodeConditionWarping_type->set_attributes({
            new attribute(strings[2431], new named_type(IFC4_IfcWarpingStiffnessSelect_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcBoundedCurve_type->set_attributes({
    },{
            
    });
    IFC4_IfcBoundedSurface_type->set_attributes({
    },{
            
    });
    IFC4_IfcBoundingBox_type->set_attributes({
            new attribute(strings[2432], new named_type(IFC4_IfcCartesianPoint_type), false),
            new attribute(strings[2433], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2434], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2435], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcBoxedHalfSpace_type->set_attributes({
            new attribute(strings[2436], new named_type(IFC4_IfcBoundingBox_type), false)
    },{
            false, false, false
    });
    IFC4_IfcBuilding_type->set_attributes({
            new attribute(strings[2437], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2438], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2439], new named_type(IFC4_IfcPostalAddress_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBuildingElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcBuildingElementPart_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBuildingElementPartTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBuildingElementPartType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBuildingElementPartTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBuildingElementProxy_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBuildingElementProxyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBuildingElementProxyType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBuildingElementProxyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBuildingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBuildingStorey_type->set_attributes({
            new attribute(strings[2440], new named_type(IFC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBuildingSystem_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBuildingSystemTypeEnum_type), true),
            new attribute(strings[2441], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcBurner_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBurnerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcBurnerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcBurnerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCShapeProfileDef_type->set_attributes({
            new attribute(strings[2442], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2443], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2444], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2445], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2446], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcCableCarrierFitting_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCableCarrierFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCableCarrierFittingType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCableCarrierFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCableCarrierSegment_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCableCarrierSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCableCarrierSegmentType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCableCarrierSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCableFitting_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCableFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCableFittingType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCableFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCableSegment_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCableSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCableSegmentType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCableSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCartesianPoint_type->set_attributes({
            new attribute(strings[2447], new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC4_IfcLengthMeasure_type)), false)
    },{
            false
    });
    IFC4_IfcCartesianPointList_type->set_attributes({
    },{
            
    });
    IFC4_IfcCartesianPointList2D_type->set_attributes({
            new attribute(strings[2448], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcLengthMeasure_type))), false)
    },{
            false
    });
    IFC4_IfcCartesianPointList3D_type->set_attributes({
            new attribute(strings[2448], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcLengthMeasure_type))), false)
    },{
            false
    });
    IFC4_IfcCartesianTransformationOperator_type->set_attributes({
            new attribute(strings[2449], new named_type(IFC4_IfcDirection_type), true),
            new attribute(strings[2450], new named_type(IFC4_IfcDirection_type), true),
            new attribute(strings[2451], new named_type(IFC4_IfcCartesianPoint_type), false),
            new attribute(strings[2452], new named_type(IFC4_IfcReal_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcCartesianTransformationOperator2D_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcCartesianTransformationOperator2DnonUniform_type->set_attributes({
            new attribute(strings[2453], new named_type(IFC4_IfcReal_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcCartesianTransformationOperator3D_type->set_attributes({
            new attribute(strings[2454], new named_type(IFC4_IfcDirection_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcCartesianTransformationOperator3DnonUniform_type->set_attributes({
            new attribute(strings[2453], new named_type(IFC4_IfcReal_type), true),
            new attribute(strings[2455], new named_type(IFC4_IfcReal_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcCenterLineProfileDef_type->set_attributes({
            new attribute(strings[2456], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcChiller_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcChillerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcChillerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcChillerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcChimney_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcChimneyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcChimneyType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcChimneyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCircle_type->set_attributes({
            new attribute(strings[2457], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4_IfcCircleHollowProfileDef_type->set_attributes({
            new attribute(strings[2444], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcCircleProfileDef_type->set_attributes({
            new attribute(strings[2457], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcCivilElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcCivilElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcClassification_type->set_attributes({
            new attribute(strings[2458], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2459], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2460], new named_type(IFC4_IfcDate_type), true),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2461], new named_type(IFC4_IfcURIReference_type), true),
            new attribute(strings[2462], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcIdentifier_type)), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcClassificationReference_type->set_attributes({
            new attribute(strings[2463], new named_type(IFC4_IfcClassificationReferenceSelect_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2464], new named_type(IFC4_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcClosedShell_type->set_attributes({
    },{
            false
    });
    IFC4_IfcCoil_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCoilTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCoilType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCoilTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcColourRgb_type->set_attributes({
            new attribute(strings[2465], new named_type(IFC4_IfcNormalisedRatioMeasure_type), false),
            new attribute(strings[2466], new named_type(IFC4_IfcNormalisedRatioMeasure_type), false),
            new attribute(strings[2467], new named_type(IFC4_IfcNormalisedRatioMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcColourRgbList_type->set_attributes({
            new attribute(strings[2468], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcNormalisedRatioMeasure_type))), false)
    },{
            false
    });
    IFC4_IfcColourSpecification_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4_IfcColumn_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcColumnTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcColumnStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcColumnType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcColumnTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCommunicationsAppliance_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCommunicationsApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCommunicationsApplianceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCommunicationsApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcComplexProperty_type->set_attributes({
            new attribute(strings[2469], new named_type(IFC4_IfcIdentifier_type), false),
            new attribute(strings[2470], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProperty_type)), false)
    },{
            false, false, false, false
    });
    IFC4_IfcComplexPropertyTemplate_type->set_attributes({
            new attribute(strings[2469], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2471], new named_type(IFC4_IfcComplexPropertyTemplateTypeEnum_type), true),
            new attribute(strings[2472], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertyTemplate_type)), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcCompositeCurve_type->set_attributes({
            new attribute(strings[2473], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcCompositeCurveSegment_type)), false),
            new attribute(strings[2395], new named_type(IFC4_IfcLogical_type), false)
    },{
            false, false
    });
    IFC4_IfcCompositeCurveOnSurface_type->set_attributes({
    },{
            false, false
    });
    IFC4_IfcCompositeCurveSegment_type->set_attributes({
            new attribute(strings[2474], new named_type(IFC4_IfcTransitionCode_type), false),
            new attribute(strings[2475], new named_type(IFC4_IfcBoolean_type), false),
            new attribute(strings[2476], new named_type(IFC4_IfcCurve_type), false)
    },{
            false, false, false
    });
    IFC4_IfcCompositeProfileDef_type->set_attributes({
            new attribute(strings[2477], new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC4_IfcProfileDef_type)), false),
            new attribute(strings[2478], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcCompressor_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCompressorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCompressorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCompressorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCondenser_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCondenserTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCondenserType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCondenserTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConic_type->set_attributes({
            new attribute(strings[2479], new named_type(IFC4_IfcAxis2Placement_type), false)
    },{
            false
    });
    IFC4_IfcConnectedFaceSet_type->set_attributes({
            new attribute(strings[2480], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcFace_type)), false)
    },{
            false
    });
    IFC4_IfcConnectionCurveGeometry_type->set_attributes({
            new attribute(strings[2481], new named_type(IFC4_IfcCurveOrEdgeCurve_type), false),
            new attribute(strings[2482], new named_type(IFC4_IfcCurveOrEdgeCurve_type), true)
    },{
            false, false
    });
    IFC4_IfcConnectionGeometry_type->set_attributes({
    },{
            
    });
    IFC4_IfcConnectionPointEccentricity_type->set_attributes({
            new attribute(strings[2483], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2484], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2485], new named_type(IFC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcConnectionPointGeometry_type->set_attributes({
            new attribute(strings[2486], new named_type(IFC4_IfcPointOrVertexPoint_type), false),
            new attribute(strings[2487], new named_type(IFC4_IfcPointOrVertexPoint_type), true)
    },{
            false, false
    });
    IFC4_IfcConnectionSurfaceGeometry_type->set_attributes({
            new attribute(strings[2488], new named_type(IFC4_IfcSurfaceOrFaceSurface_type), false),
            new attribute(strings[2489], new named_type(IFC4_IfcSurfaceOrFaceSurface_type), true)
    },{
            false, false
    });
    IFC4_IfcConnectionVolumeGeometry_type->set_attributes({
            new attribute(strings[2490], new named_type(IFC4_IfcSolidOrShell_type), false),
            new attribute(strings[2491], new named_type(IFC4_IfcSolidOrShell_type), true)
    },{
            false, false
    });
    IFC4_IfcConstraint_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2492], new named_type(IFC4_IfcConstraintEnum_type), false),
            new attribute(strings[2493], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2494], new named_type(IFC4_IfcActorSelect_type), true),
            new attribute(strings[2495], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2496], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcConstructionEquipmentResource_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcConstructionEquipmentResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConstructionEquipmentResourceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcConstructionEquipmentResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConstructionMaterialResource_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcConstructionMaterialResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConstructionMaterialResourceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcConstructionMaterialResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConstructionProductResource_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcConstructionProductResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConstructionProductResourceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcConstructionProductResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConstructionResource_type->set_attributes({
            new attribute(strings[2497], new named_type(IFC4_IfcResourceTime_type), true),
            new attribute(strings[2498], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAppliedValue_type)), true),
            new attribute(strings[2499], new named_type(IFC4_IfcPhysicalQuantity_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConstructionResourceType_type->set_attributes({
            new attribute(strings[2498], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAppliedValue_type)), true),
            new attribute(strings[2499], new named_type(IFC4_IfcPhysicalQuantity_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcContext_type->set_attributes({
            new attribute(strings[2500], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2441], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2501], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2502], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcRepresentationContext_type)), true),
            new attribute(strings[2503], new named_type(IFC4_IfcUnitAssignment_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcContextDependentUnit_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false)
    },{
            false, false, false
    });
    IFC4_IfcControl_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcController_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcControllerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcControllerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcControllerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcConversionBasedUnit_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2504], new named_type(IFC4_IfcMeasureWithUnit_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcConversionBasedUnitWithOffset_type->set_attributes({
            new attribute(strings[2505], new named_type(IFC4_IfcReal_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcCooledBeam_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCooledBeamTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCooledBeamType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCooledBeamTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCoolingTower_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCoolingTowerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCoolingTowerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCoolingTowerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCoordinateOperation_type->set_attributes({
            new attribute(strings[2506], new named_type(IFC4_IfcCoordinateReferenceSystemSelect_type), false),
            new attribute(strings[2507], new named_type(IFC4_IfcCoordinateReferenceSystem_type), false)
    },{
            false, false
    });
    IFC4_IfcCoordinateReferenceSystem_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2508], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2509], new named_type(IFC4_IfcIdentifier_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcCostItem_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCostItemTypeEnum_type), true),
            new attribute(strings[2510], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcCostValue_type)), true),
            new attribute(strings[2511], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcPhysicalQuantity_type)), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCostSchedule_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCostScheduleTypeEnum_type), true),
            new attribute(strings[2333], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2512], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2513], new named_type(IFC4_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCostValue_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCovering_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCoveringTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCoveringType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCoveringTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCrewResource_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCrewResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCrewResourceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCrewResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCsgPrimitive3D_type->set_attributes({
            new attribute(strings[2479], new named_type(IFC4_IfcAxis2Placement3D_type), false)
    },{
            false
    });
    IFC4_IfcCsgSolid_type->set_attributes({
            new attribute(strings[2514], new named_type(IFC4_IfcCsgSelect_type), false)
    },{
            false
    });
    IFC4_IfcCurrencyRelationship_type->set_attributes({
            new attribute(strings[2515], new named_type(IFC4_IfcMonetaryUnit_type), false),
            new attribute(strings[2516], new named_type(IFC4_IfcMonetaryUnit_type), false),
            new attribute(strings[2517], new named_type(IFC4_IfcPositiveRatioMeasure_type), false),
            new attribute(strings[2518], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2519], new named_type(IFC4_IfcLibraryInformation_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcCurtainWall_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCurtainWallTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCurtainWallType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcCurtainWallTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcCurve_type->set_attributes({
    },{
            
    });
    IFC4_IfcCurveBoundedPlane_type->set_attributes({
            new attribute(strings[2520], new named_type(IFC4_IfcPlane_type), false),
            new attribute(strings[2342], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2343], new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4_IfcCurve_type)), false)
    },{
            false, false, false
    });
    IFC4_IfcCurveBoundedSurface_type->set_attributes({
            new attribute(strings[2520], new named_type(IFC4_IfcSurface_type), false),
            new attribute(strings[2521], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcBoundaryCurve_type)), false),
            new attribute(strings[2522], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4_IfcCurveStyle_type->set_attributes({
            new attribute(strings[2523], new named_type(IFC4_IfcCurveFontOrScaledCurveFontSelect_type), true),
            new attribute(strings[2524], new named_type(IFC4_IfcSizeSelect_type), true),
            new attribute(strings[2525], new named_type(IFC4_IfcColour_type), true),
            new attribute(strings[2526], new named_type(IFC4_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcCurveStyleFont_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2527], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcCurveStyleFontPattern_type)), false)
    },{
            false, false
    });
    IFC4_IfcCurveStyleFontAndScaling_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2523], new named_type(IFC4_IfcCurveStyleFontSelect_type), false),
            new attribute(strings[2528], new named_type(IFC4_IfcPositiveRatioMeasure_type), false)
    },{
            false, false, false
    });
    IFC4_IfcCurveStyleFontPattern_type->set_attributes({
            new attribute(strings[2529], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2530], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4_IfcCylindricalSurface_type->set_attributes({
            new attribute(strings[2457], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4_IfcDamper_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDamperTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDamperType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDamperTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDerivedProfileDef_type->set_attributes({
            new attribute(strings[2531], new named_type(IFC4_IfcProfileDef_type), false),
            new attribute(strings[2413], new named_type(IFC4_IfcCartesianTransformationOperator2D_type), false),
            new attribute(strings[2478], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcDerivedUnit_type->set_attributes({
            new attribute(strings[2532], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDerivedUnitElement_type)), false),
            new attribute(strings[2533], new named_type(IFC4_IfcDerivedUnitEnum_type), false),
            new attribute(strings[2534], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4_IfcDerivedUnitElement_type->set_attributes({
            new attribute(strings[2535], new named_type(IFC4_IfcNamedUnit_type), false),
            new attribute(strings[2536], new simple_type(simple_type::integer_type), false)
    },{
            false, false
    });
    IFC4_IfcDimensionalExponents_type->set_attributes({
            new attribute(strings[2537], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2538], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2539], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2540], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2541], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2542], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2543], new simple_type(simple_type::integer_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcDirection_type->set_attributes({
            new attribute(strings[2544], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_IfcReal_type)), false)
    },{
            false
    });
    IFC4_IfcDiscreteAccessory_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDiscreteAccessoryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDiscreteAccessoryType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDiscreteAccessoryTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionChamberElement_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDistributionChamberElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionChamberElementType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDistributionChamberElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionCircuit_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionControlElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionControlElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionFlowElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionFlowElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionPort_type->set_attributes({
            new attribute(strings[2545], new named_type(IFC4_IfcFlowDirectionEnum_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcDistributionPortTypeEnum_type), true),
            new attribute(strings[2546], new named_type(IFC4_IfcDistributionSystemEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDistributionSystem_type->set_attributes({
            new attribute(strings[2441], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcDistributionSystemEnum_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcDocumentInformation_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), false),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2461], new named_type(IFC4_IfcURIReference_type), true),
            new attribute(strings[2339], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2547], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2548], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2549], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2550], new named_type(IFC4_IfcActorSelect_type), true),
            new attribute(strings[2551], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcActorSelect_type)), true),
            new attribute(strings[2495], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2552], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2553], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2554], new named_type(IFC4_IfcDate_type), true),
            new attribute(strings[2555], new named_type(IFC4_IfcDate_type), true),
            new attribute(strings[2556], new named_type(IFC4_IfcDocumentConfidentialityEnum_type), true),
            new attribute(strings[2333], new named_type(IFC4_IfcDocumentStatusEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDocumentInformationRelationship_type->set_attributes({
            new attribute(strings[2557], new named_type(IFC4_IfcDocumentInformation_type), false),
            new attribute(strings[2558], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDocumentInformation_type)), false),
            new attribute(strings[2559], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcDocumentReference_type->set_attributes({
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2560], new named_type(IFC4_IfcDocumentInformation_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcDoor_type->set_attributes({
            new attribute(strings[2561], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2562], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcDoorTypeEnum_type), true),
            new attribute(strings[2563], new named_type(IFC4_IfcDoorTypeOperationEnum_type), true),
            new attribute(strings[2564], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDoorLiningProperties_type->set_attributes({
            new attribute(strings[2565], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2566], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2567], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2568], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2569], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2570], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2571], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2572], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2573], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2574], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2575], new named_type(IFC4_IfcShapeAspect_type), true),
            new attribute(strings[2576], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2577], new named_type(IFC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDoorPanelProperties_type->set_attributes({
            new attribute(strings[2578], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2579], new named_type(IFC4_IfcDoorPanelOperationEnum_type), false),
            new attribute(strings[2580], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2581], new named_type(IFC4_IfcDoorPanelPositionEnum_type), false),
            new attribute(strings[2575], new named_type(IFC4_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDoorStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDoorStyle_type->set_attributes({
            new attribute(strings[2563], new named_type(IFC4_IfcDoorStyleOperationEnum_type), false),
            new attribute(strings[2582], new named_type(IFC4_IfcDoorStyleConstructionEnum_type), false),
            new attribute(strings[2583], new named_type(IFC4_IfcBoolean_type), false),
            new attribute(strings[2584], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDoorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDoorTypeEnum_type), false),
            new attribute(strings[2563], new named_type(IFC4_IfcDoorTypeOperationEnum_type), false),
            new attribute(strings[2583], new named_type(IFC4_IfcBoolean_type), true),
            new attribute(strings[2564], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDraughtingPreDefinedColour_type->set_attributes({
    },{
            false
    });
    IFC4_IfcDraughtingPreDefinedCurveFont_type->set_attributes({
    },{
            false
    });
    IFC4_IfcDuctFitting_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDuctFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDuctFittingType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDuctFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDuctSegment_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDuctSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDuctSegmentType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDuctSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDuctSilencer_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDuctSilencerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcDuctSilencerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcDuctSilencerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEdge_type->set_attributes({
            new attribute(strings[2585], new named_type(IFC4_IfcVertex_type), false),
            new attribute(strings[2586], new named_type(IFC4_IfcVertex_type), false)
    },{
            false, false
    });
    IFC4_IfcEdgeCurve_type->set_attributes({
            new attribute(strings[2587], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2475], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcEdgeLoop_type->set_attributes({
            new attribute(strings[2588], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcOrientedEdge_type)), false)
    },{
            false
    });
    IFC4_IfcElectricAppliance_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricApplianceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricDistributionBoard_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricDistributionBoardTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricDistributionBoardType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricDistributionBoardTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricFlowStorageDevice_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricFlowStorageDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricFlowStorageDeviceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricFlowStorageDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricGenerator_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricGeneratorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricGeneratorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricGeneratorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricMotor_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricMotorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricMotorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricMotorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricTimeControl_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricTimeControlTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElectricTimeControlType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElectricTimeControlTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElement_type->set_attributes({
            new attribute(strings[2589], new named_type(IFC4_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcElementAssembly_type->set_attributes({
            new attribute(strings[2590], new named_type(IFC4_IfcAssemblyPlaceEnum_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcElementAssemblyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElementAssemblyType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcElementAssemblyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElementComponent_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcElementComponentType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElementQuantity_type->set_attributes({
            new attribute(strings[2591], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2592], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPhysicalQuantity_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcElementType_type->set_attributes({
            new attribute(strings[2593], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcElementarySurface_type->set_attributes({
            new attribute(strings[2479], new named_type(IFC4_IfcAxis2Placement3D_type), false)
    },{
            false
    });
    IFC4_IfcEllipse_type->set_attributes({
            new attribute(strings[2594], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2595], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4_IfcEllipseProfileDef_type->set_attributes({
            new attribute(strings[2594], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2595], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcEnergyConversionDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcEnergyConversionDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEngine_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcEngineTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEngineType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcEngineTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEvaporativeCooler_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcEvaporativeCoolerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEvaporativeCoolerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcEvaporativeCoolerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEvaporator_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcEvaporatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEvaporatorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcEvaporatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEvent_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcEventTypeEnum_type), true),
            new attribute(strings[2596], new named_type(IFC4_IfcEventTriggerTypeEnum_type), true),
            new attribute(strings[2597], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2598], new named_type(IFC4_IfcEventTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcEventTime_type->set_attributes({
            new attribute(strings[2599], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2600], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2601], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2602], new named_type(IFC4_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcEventType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcEventTypeEnum_type), false),
            new attribute(strings[2596], new named_type(IFC4_IfcEventTriggerTypeEnum_type), false),
            new attribute(strings[2597], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcExtendedProperties_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2603], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProperty_type)), false)
    },{
            false, false, false
    });
    IFC4_IfcExternalInformation_type->set_attributes({
    },{
            
    });
    IFC4_IfcExternalReference_type->set_attributes({
            new attribute(strings[2461], new named_type(IFC4_IfcURIReference_type), true),
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4_IfcExternalReferenceRelationship_type->set_attributes({
            new attribute(strings[2604], new named_type(IFC4_IfcExternalReference_type), false),
            new attribute(strings[2605], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcResourceObjectSelect_type)), false)
    },{
            false, false, false, false
    });
    IFC4_IfcExternalSpatialElement_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcExternalSpatialElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcExternalSpatialStructureElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcExternallyDefinedHatchStyle_type->set_attributes({
    },{
            false, false, false
    });
    IFC4_IfcExternallyDefinedSurfaceStyle_type->set_attributes({
    },{
            false, false, false
    });
    IFC4_IfcExternallyDefinedTextFont_type->set_attributes({
    },{
            false, false, false
    });
    IFC4_IfcExtrudedAreaSolid_type->set_attributes({
            new attribute(strings[2606], new named_type(IFC4_IfcDirection_type), false),
            new attribute(strings[2442], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcExtrudedAreaSolidTapered_type->set_attributes({
            new attribute(strings[2607], new named_type(IFC4_IfcProfileDef_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcFace_type->set_attributes({
            new attribute(strings[2608], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcFaceBound_type)), false)
    },{
            false
    });
    IFC4_IfcFaceBasedSurfaceModel_type->set_attributes({
            new attribute(strings[2609], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcConnectedFaceSet_type)), false)
    },{
            false
    });
    IFC4_IfcFaceBound_type->set_attributes({
            new attribute(strings[2610], new named_type(IFC4_IfcLoop_type), false),
            new attribute(strings[2611], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false
    });
    IFC4_IfcFaceOuterBound_type->set_attributes({
    },{
            false, false
    });
    IFC4_IfcFaceSurface_type->set_attributes({
            new attribute(strings[2612], new named_type(IFC4_IfcSurface_type), false),
            new attribute(strings[2475], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4_IfcFacetedBrep_type->set_attributes({
    },{
            false
    });
    IFC4_IfcFacetedBrepWithVoids_type->set_attributes({
            new attribute(strings[2341], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcClosedShell_type)), false)
    },{
            false, false
    });
    IFC4_IfcFailureConnectionCondition_type->set_attributes({
            new attribute(strings[2613], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[2614], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[2615], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[2616], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[2617], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[2618], new named_type(IFC4_IfcForceMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcFan_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFanTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFanType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFanTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFastener_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFastenerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFastenerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFastenerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFeatureElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFeatureElementAddition_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFeatureElementSubtraction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFillAreaStyle_type->set_attributes({
            new attribute(strings[2619], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcFillStyleSelect_type)), false),
            new attribute(strings[2620], new named_type(IFC4_IfcBoolean_type), true)
    },{
            false, false, false
    });
    IFC4_IfcFillAreaStyleHatching_type->set_attributes({
            new attribute(strings[2621], new named_type(IFC4_IfcCurveStyle_type), false),
            new attribute(strings[2622], new named_type(IFC4_IfcHatchLineDistanceSelect_type), false),
            new attribute(strings[2623], new named_type(IFC4_IfcCartesianPoint_type), true),
            new attribute(strings[2624], new named_type(IFC4_IfcCartesianPoint_type), true),
            new attribute(strings[2625], new named_type(IFC4_IfcPlaneAngleMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcFillAreaStyleTiles_type->set_attributes({
            new attribute(strings[2626], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcVector_type)), false),
            new attribute(strings[2627], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcStyledItem_type)), false),
            new attribute(strings[2628], new named_type(IFC4_IfcPositiveRatioMeasure_type), false)
    },{
            false, false, false
    });
    IFC4_IfcFilter_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFilterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFilterType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFilterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFireSuppressionTerminal_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFireSuppressionTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFireSuppressionTerminalType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFireSuppressionTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFixedReferenceSweptAreaSolid_type->set_attributes({
            new attribute(strings[2629], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2630], new named_type(IFC4_IfcParameterValue_type), true),
            new attribute(strings[2631], new named_type(IFC4_IfcParameterValue_type), true),
            new attribute(strings[2632], new named_type(IFC4_IfcDirection_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcFlowController_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowControllerType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowFitting_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowFittingType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowInstrument_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFlowInstrumentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowInstrumentType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFlowInstrumentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowMeter_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFlowMeterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowMeterType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFlowMeterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowMovingDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowMovingDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowSegment_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowSegmentType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowStorageDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowStorageDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowTerminal_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowTerminalType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowTreatmentDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFlowTreatmentDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFooting_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFootingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFootingType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFootingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFurnishingElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcFurnishingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFurniture_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcFurnitureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcFurnitureType_type->set_attributes({
            new attribute(strings[2590], new named_type(IFC4_IfcAssemblyPlaceEnum_type), false),
            new attribute(strings[2332], new named_type(IFC4_IfcFurnitureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcGeographicElement_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcGeographicElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcGeographicElementType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcGeographicElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcGeometricCurveSet_type->set_attributes({
    },{
            false
    });
    IFC4_IfcGeometricRepresentationContext_type->set_attributes({
            new attribute(strings[2633], new named_type(IFC4_IfcDimensionCount_type), false),
            new attribute(strings[2634], new named_type(IFC4_IfcReal_type), true),
            new attribute(strings[2635], new named_type(IFC4_IfcAxis2Placement_type), false),
            new attribute(strings[2636], new named_type(IFC4_IfcDirection_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcGeometricRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4_IfcGeometricRepresentationSubContext_type->set_attributes({
            new attribute(strings[2637], new named_type(IFC4_IfcGeometricRepresentationContext_type), false),
            new attribute(strings[2638], new named_type(IFC4_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[2639], new named_type(IFC4_IfcGeometricProjectionEnum_type), false),
            new attribute(strings[2640], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, true, true, true, true, false, false, false, false
    });
    IFC4_IfcGeometricSet_type->set_attributes({
            new attribute(strings[2532], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcGeometricSetSelect_type)), false)
    },{
            false
    });
    IFC4_IfcGrid_type->set_attributes({
            new attribute(strings[2641], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcGridAxis_type)), false),
            new attribute(strings[2642], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcGridAxis_type)), false),
            new attribute(strings[2643], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcGridAxis_type)), true),
            new attribute(strings[2332], new named_type(IFC4_IfcGridTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcGridAxis_type->set_attributes({
            new attribute(strings[2644], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2645], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2475], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4_IfcGridPlacement_type->set_attributes({
            new attribute(strings[2646], new named_type(IFC4_IfcVirtualGridIntersection_type), false),
            new attribute(strings[2647], new named_type(IFC4_IfcGridPlacementDirectionSelect_type), true)
    },{
            false, false
    });
    IFC4_IfcGroup_type->set_attributes({
    },{
            false, false, false, false, false
    });
    IFC4_IfcHalfSpaceSolid_type->set_attributes({
            new attribute(strings[2648], new named_type(IFC4_IfcSurface_type), false),
            new attribute(strings[2649], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false
    });
    IFC4_IfcHeatExchanger_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcHeatExchangerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcHeatExchangerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcHeatExchangerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcHumidifier_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcHumidifierTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcHumidifierType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcHumidifierTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcIShapeProfileDef_type->set_attributes({
            new attribute(strings[2562], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2378], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2379], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2650], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2651], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2652], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2653], new named_type(IFC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcImageTexture_type->set_attributes({
            new attribute(strings[2654], new named_type(IFC4_IfcURIReference_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcIndexedColourMap_type->set_attributes({
            new attribute(strings[2655], new named_type(IFC4_IfcTessellatedFaceSet_type), false),
            new attribute(strings[2656], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2657], new named_type(IFC4_IfcColourRgbList_type), false),
            new attribute(strings[2658], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcPositiveInteger_type)), false)
    },{
            false, false, false, false
    });
    IFC4_IfcIndexedPolyCurve_type->set_attributes({
            new attribute(strings[2659], new named_type(IFC4_IfcCartesianPointList_type), false),
            new attribute(strings[2473], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcSegmentIndexSelect_type)), true),
            new attribute(strings[2395], new named_type(IFC4_IfcBoolean_type), true)
    },{
            false, false, false
    });
    IFC4_IfcIndexedPolygonalFace_type->set_attributes({
            new attribute(strings[2660], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_IfcPositiveInteger_type)), false)
    },{
            false
    });
    IFC4_IfcIndexedPolygonalFaceWithVoids_type->set_attributes({
            new attribute(strings[2661], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_IfcPositiveInteger_type))), false)
    },{
            false, false
    });
    IFC4_IfcIndexedTextureMap_type->set_attributes({
            new attribute(strings[2655], new named_type(IFC4_IfcTessellatedFaceSet_type), false),
            new attribute(strings[2662], new named_type(IFC4_IfcTextureVertexList_type), false)
    },{
            false, false, false
    });
    IFC4_IfcIndexedTriangleTextureMap_type->set_attributes({
            new attribute(strings[2663], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcPositiveInteger_type))), true)
    },{
            false, false, false, false
    });
    IFC4_IfcInterceptor_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcInterceptorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcInterceptorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcInterceptorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcIntersectionCurve_type->set_attributes({
    },{
            false, false, false
    });
    IFC4_IfcInventory_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcInventoryTypeEnum_type), true),
            new attribute(strings[2664], new named_type(IFC4_IfcActorSelect_type), true),
            new attribute(strings[2665], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPerson_type)), true),
            new attribute(strings[2666], new named_type(IFC4_IfcDate_type), true),
            new attribute(strings[2370], new named_type(IFC4_IfcCostValue_type), true),
            new attribute(strings[2369], new named_type(IFC4_IfcCostValue_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcIrregularTimeSeries_type->set_attributes({
            new attribute(strings[2667], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcIrregularTimeSeriesValue_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcIrregularTimeSeriesValue_type->set_attributes({
            new attribute(strings[2668], new named_type(IFC4_IfcDateTime_type), false),
            new attribute(strings[2669], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), false)
    },{
            false, false
    });
    IFC4_IfcJunctionBox_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcJunctionBoxTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcJunctionBoxType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcJunctionBoxTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLShapeProfileDef_type->set_attributes({
            new attribute(strings[2442], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2443], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2456], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2651], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2670], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2671], new named_type(IFC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLaborResource_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcLaborResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLaborResourceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcLaborResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLagTime_type->set_attributes({
            new attribute(strings[2672], new named_type(IFC4_IfcTimeOrRatioSelect_type), false),
            new attribute(strings[2673], new named_type(IFC4_IfcTaskDurationEnum_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcLamp_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcLampTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLampType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcLampTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLibraryInformation_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2345], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2674], new named_type(IFC4_IfcActorSelect_type), true),
            new attribute(strings[2675], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2461], new named_type(IFC4_IfcURIReference_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcLibraryReference_type->set_attributes({
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2676], new named_type(IFC4_IfcLanguageId_type), true),
            new attribute(strings[2677], new named_type(IFC4_IfcLibraryInformation_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcLightDistributionData_type->set_attributes({
            new attribute(strings[2678], new named_type(IFC4_IfcPlaneAngleMeasure_type), false),
            new attribute(strings[2679], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcPlaneAngleMeasure_type)), false),
            new attribute(strings[2680], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLuminousIntensityDistributionMeasure_type)), false)
    },{
            false, false, false
    });
    IFC4_IfcLightFixture_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcLightFixtureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLightFixtureType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcLightFixtureTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLightIntensityDistribution_type->set_attributes({
            new attribute(strings[2681], new named_type(IFC4_IfcLightDistributionCurveEnum_type), false),
            new attribute(strings[2682], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLightDistributionData_type)), false)
    },{
            false, false
    });
    IFC4_IfcLightSource_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2683], new named_type(IFC4_IfcColourRgb_type), false),
            new attribute(strings[2684], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2685], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcLightSourceAmbient_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcLightSourceDirectional_type->set_attributes({
            new attribute(strings[2611], new named_type(IFC4_IfcDirection_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcLightSourceGoniometric_type->set_attributes({
            new attribute(strings[2479], new named_type(IFC4_IfcAxis2Placement3D_type), false),
            new attribute(strings[2686], new named_type(IFC4_IfcColourRgb_type), true),
            new attribute(strings[2687], new named_type(IFC4_IfcThermodynamicTemperatureMeasure_type), false),
            new attribute(strings[2688], new named_type(IFC4_IfcLuminousFluxMeasure_type), false),
            new attribute(strings[2689], new named_type(IFC4_IfcLightEmissionSourceEnum_type), false),
            new attribute(strings[2690], new named_type(IFC4_IfcLightDistributionDataSourceSelect_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLightSourcePositional_type->set_attributes({
            new attribute(strings[2479], new named_type(IFC4_IfcCartesianPoint_type), false),
            new attribute(strings[2457], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2691], new named_type(IFC4_IfcReal_type), false),
            new attribute(strings[2692], new named_type(IFC4_IfcReal_type), false),
            new attribute(strings[2693], new named_type(IFC4_IfcReal_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLightSourceSpot_type->set_attributes({
            new attribute(strings[2611], new named_type(IFC4_IfcDirection_type), false),
            new attribute(strings[2694], new named_type(IFC4_IfcReal_type), true),
            new attribute(strings[2695], new named_type(IFC4_IfcPositivePlaneAngleMeasure_type), false),
            new attribute(strings[2696], new named_type(IFC4_IfcPositivePlaneAngleMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcLine_type->set_attributes({
            new attribute(strings[2697], new named_type(IFC4_IfcCartesianPoint_type), false),
            new attribute(strings[2698], new named_type(IFC4_IfcVector_type), false)
    },{
            false, false
    });
    IFC4_IfcLocalPlacement_type->set_attributes({
            new attribute(strings[2699], new named_type(IFC4_IfcObjectPlacement_type), true),
            new attribute(strings[2700], new named_type(IFC4_IfcAxis2Placement_type), false)
    },{
            false, false
    });
    IFC4_IfcLoop_type->set_attributes({
    },{
            
    });
    IFC4_IfcManifoldSolidBrep_type->set_attributes({
            new attribute(strings[2701], new named_type(IFC4_IfcClosedShell_type), false)
    },{
            false
    });
    IFC4_IfcMapConversion_type->set_attributes({
            new attribute(strings[2702], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2703], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2704], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2705], new named_type(IFC4_IfcReal_type), true),
            new attribute(strings[2706], new named_type(IFC4_IfcReal_type), true),
            new attribute(strings[2452], new named_type(IFC4_IfcReal_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcMappedItem_type->set_attributes({
            new attribute(strings[2707], new named_type(IFC4_IfcRepresentationMap_type), false),
            new attribute(strings[2708], new named_type(IFC4_IfcCartesianTransformationOperator_type), false)
    },{
            false, false
    });
    IFC4_IfcMaterial_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2353], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4_IfcMaterialClassificationRelationship_type->set_attributes({
            new attribute(strings[2709], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcClassificationSelect_type)), false),
            new attribute(strings[2710], new named_type(IFC4_IfcMaterial_type), false)
    },{
            false, false
    });
    IFC4_IfcMaterialConstituent_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2711], new named_type(IFC4_IfcMaterial_type), false),
            new attribute(strings[2712], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2353], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcMaterialConstituentSet_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2713], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcMaterialConstituent_type)), true)
    },{
            false, false, false
    });
    IFC4_IfcMaterialDefinition_type->set_attributes({
    },{
            
    });
    IFC4_IfcMaterialDefinitionRepresentation_type->set_attributes({
            new attribute(strings[2714], new named_type(IFC4_IfcMaterial_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcMaterialLayer_type->set_attributes({
            new attribute(strings[2711], new named_type(IFC4_IfcMaterial_type), true),
            new attribute(strings[2715], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[2716], new named_type(IFC4_IfcLogical_type), true),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2353], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2717], new named_type(IFC4_IfcInteger_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcMaterialLayerSet_type->set_attributes({
            new attribute(strings[2718], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcMaterialLayer_type)), false),
            new attribute(strings[2719], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false
    });
    IFC4_IfcMaterialLayerSetUsage_type->set_attributes({
            new attribute(strings[2720], new named_type(IFC4_IfcMaterialLayerSet_type), false),
            new attribute(strings[2721], new named_type(IFC4_IfcLayerSetDirectionEnum_type), false),
            new attribute(strings[2722], new named_type(IFC4_IfcDirectionSenseEnum_type), false),
            new attribute(strings[2723], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2724], new named_type(IFC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcMaterialLayerWithOffsets_type->set_attributes({
            new attribute(strings[2725], new named_type(IFC4_IfcLayerSetDirectionEnum_type), false),
            new attribute(strings[2726], new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4_IfcLengthMeasure_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMaterialList_type->set_attributes({
            new attribute(strings[2727], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcMaterial_type)), false)
    },{
            false
    });
    IFC4_IfcMaterialProfile_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2711], new named_type(IFC4_IfcMaterial_type), true),
            new attribute(strings[2728], new named_type(IFC4_IfcProfileDef_type), false),
            new attribute(strings[2717], new named_type(IFC4_IfcInteger_type), true),
            new attribute(strings[2353], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcMaterialProfileSet_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2729], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcMaterialProfile_type)), false),
            new attribute(strings[2730], new named_type(IFC4_IfcCompositeProfileDef_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcMaterialProfileSetUsage_type->set_attributes({
            new attribute(strings[2731], new named_type(IFC4_IfcMaterialProfileSet_type), false),
            new attribute(strings[2732], new named_type(IFC4_IfcCardinalPointReference_type), true),
            new attribute(strings[2724], new named_type(IFC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false
    });
    IFC4_IfcMaterialProfileSetUsageTapering_type->set_attributes({
            new attribute(strings[2733], new named_type(IFC4_IfcMaterialProfileSet_type), false),
            new attribute(strings[2734], new named_type(IFC4_IfcCardinalPointReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcMaterialProfileWithOffsets_type->set_attributes({
            new attribute(strings[2726], new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4_IfcLengthMeasure_type)), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcMaterialProperties_type->set_attributes({
            new attribute(strings[2711], new named_type(IFC4_IfcMaterialDefinition_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcMaterialRelationship_type->set_attributes({
            new attribute(strings[2735], new named_type(IFC4_IfcMaterial_type), false),
            new attribute(strings[2736], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcMaterial_type)), false),
            new attribute(strings[2737], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcMaterialUsageDefinition_type->set_attributes({
    },{
            
    });
    IFC4_IfcMeasureWithUnit_type->set_attributes({
            new attribute(strings[2738], new named_type(IFC4_IfcValue_type), false),
            new attribute(strings[2739], new named_type(IFC4_IfcUnit_type), false)
    },{
            false, false
    });
    IFC4_IfcMechanicalFastener_type->set_attributes({
            new attribute(strings[2740], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2741], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcMechanicalFastenerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMechanicalFastenerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcMechanicalFastenerTypeEnum_type), false),
            new attribute(strings[2740], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2741], new named_type(IFC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMedicalDevice_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcMedicalDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMedicalDeviceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcMedicalDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMember_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcMemberTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMemberStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMemberType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcMemberTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMetric_type->set_attributes({
            new attribute(strings[2742], new named_type(IFC4_IfcBenchmarkEnum_type), false),
            new attribute(strings[2743], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2744], new named_type(IFC4_IfcMetricValueSelect_type), true),
            new attribute(strings[2745], new named_type(IFC4_IfcReference_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMirroredProfileDef_type->set_attributes({
    },{
            false, false, false, true, false
    });
    IFC4_IfcMonetaryUnit_type->set_attributes({
            new attribute(strings[2746], new named_type(IFC4_IfcLabel_type), false)
    },{
            false
    });
    IFC4_IfcMotorConnection_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcMotorConnectionTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcMotorConnectionType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcMotorConnectionTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcNamedUnit_type->set_attributes({
            new attribute(strings[2747], new named_type(IFC4_IfcDimensionalExponents_type), false),
            new attribute(strings[2533], new named_type(IFC4_IfcUnitEnum_type), false)
    },{
            false, false
    });
    IFC4_IfcObject_type->set_attributes({
            new attribute(strings[2500], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcObjectDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcObjectPlacement_type->set_attributes({
    },{
            
    });
    IFC4_IfcObjective_type->set_attributes({
            new attribute(strings[2748], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcConstraint_type)), true),
            new attribute(strings[2749], new named_type(IFC4_IfcLogicalOperatorEnum_type), true),
            new attribute(strings[2750], new named_type(IFC4_IfcObjectiveEnum_type), false),
            new attribute(strings[2751], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcOccupant_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcOccupantTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcOffsetCurve2D_type->set_attributes({
            new attribute(strings[2752], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2753], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2395], new named_type(IFC4_IfcLogical_type), false)
    },{
            false, false, false
    });
    IFC4_IfcOffsetCurve3D_type->set_attributes({
            new attribute(strings[2752], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2753], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2395], new named_type(IFC4_IfcLogical_type), false),
            new attribute(strings[2390], new named_type(IFC4_IfcDirection_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcOpenShell_type->set_attributes({
    },{
            false
    });
    IFC4_IfcOpeningElement_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcOpeningElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcOpeningStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcOrganization_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2754], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcActorRole_type)), true),
            new attribute(strings[2755], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAddress_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcOrganizationRelationship_type->set_attributes({
            new attribute(strings[2756], new named_type(IFC4_IfcOrganization_type), false),
            new attribute(strings[2757], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcOrganization_type)), false)
    },{
            false, false, false, false
    });
    IFC4_IfcOrientedEdge_type->set_attributes({
            new attribute(strings[2758], new named_type(IFC4_IfcEdge_type), false),
            new attribute(strings[2611], new named_type(IFC4_IfcBoolean_type), false)
    },{
            true, true, false, false
    });
    IFC4_IfcOuterBoundaryCurve_type->set_attributes({
    },{
            false, false
    });
    IFC4_IfcOutlet_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcOutletTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcOutletType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcOutletTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcOwnerHistory_type->set_attributes({
            new attribute(strings[2759], new named_type(IFC4_IfcPersonAndOrganization_type), false),
            new attribute(strings[2760], new named_type(IFC4_IfcApplication_type), false),
            new attribute(strings[2761], new named_type(IFC4_IfcStateEnum_type), true),
            new attribute(strings[2762], new named_type(IFC4_IfcChangeActionEnum_type), true),
            new attribute(strings[2763], new named_type(IFC4_IfcTimeStamp_type), true),
            new attribute(strings[2764], new named_type(IFC4_IfcPersonAndOrganization_type), true),
            new attribute(strings[2765], new named_type(IFC4_IfcApplication_type), true),
            new attribute(strings[2766], new named_type(IFC4_IfcTimeStamp_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcParameterizedProfileDef_type->set_attributes({
            new attribute(strings[2479], new named_type(IFC4_IfcAxis2Placement2D_type), true)
    },{
            false, false, false
    });
    IFC4_IfcPath_type->set_attributes({
            new attribute(strings[2588], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcOrientedEdge_type)), false)
    },{
            false
    });
    IFC4_IfcPcurve_type->set_attributes({
            new attribute(strings[2520], new named_type(IFC4_IfcSurface_type), false),
            new attribute(strings[2767], new named_type(IFC4_IfcCurve_type), false)
    },{
            false, false
    });
    IFC4_IfcPerformanceHistory_type->set_attributes({
            new attribute(strings[2768], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2332], new named_type(IFC4_IfcPerformanceHistoryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcPermeableCoveringProperties_type->set_attributes({
            new attribute(strings[2563], new named_type(IFC4_IfcPermeableCoveringOperationEnum_type), false),
            new attribute(strings[2581], new named_type(IFC4_IfcWindowPanelPositionEnum_type), false),
            new attribute(strings[2769], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2770], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2575], new named_type(IFC4_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPermit_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPermitTypeEnum_type), true),
            new attribute(strings[2333], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2334], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPerson_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2771], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2772], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2773], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true),
            new attribute(strings[2774], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true),
            new attribute(strings[2775], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true),
            new attribute(strings[2754], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcActorRole_type)), true),
            new attribute(strings[2755], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcAddress_type)), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcPersonAndOrganization_type->set_attributes({
            new attribute(strings[2776], new named_type(IFC4_IfcPerson_type), false),
            new attribute(strings[2777], new named_type(IFC4_IfcOrganization_type), false),
            new attribute(strings[2754], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcActorRole_type)), true)
    },{
            false, false, false
    });
    IFC4_IfcPhysicalComplexQuantity_type->set_attributes({
            new attribute(strings[2778], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPhysicalQuantity_type)), false),
            new attribute(strings[2779], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2780], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2497], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcPhysicalQuantity_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true)
    },{
            false, false
    });
    IFC4_IfcPhysicalSimpleQuantity_type->set_attributes({
            new attribute(strings[2535], new named_type(IFC4_IfcNamedUnit_type), true)
    },{
            false, false, false
    });
    IFC4_IfcPile_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPileTypeEnum_type), true),
            new attribute(strings[2582], new named_type(IFC4_IfcPileConstructionEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPileType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPileTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPipeFitting_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPipeFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPipeFittingType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPipeFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPipeSegment_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPipeSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPipeSegmentType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPipeSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPixelTexture_type->set_attributes({
            new attribute(strings[2443], new named_type(IFC4_IfcInteger_type), false),
            new attribute(strings[2781], new named_type(IFC4_IfcInteger_type), false),
            new attribute(strings[2782], new named_type(IFC4_IfcInteger_type), false),
            new attribute(strings[2783], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcBinary_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPlacement_type->set_attributes({
            new attribute(strings[2461], new named_type(IFC4_IfcCartesianPoint_type), false)
    },{
            false
    });
    IFC4_IfcPlanarBox_type->set_attributes({
            new attribute(strings[2784], new named_type(IFC4_IfcAxis2Placement_type), false)
    },{
            false, false, false
    });
    IFC4_IfcPlanarExtent_type->set_attributes({
            new attribute(strings[2785], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2786], new named_type(IFC4_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4_IfcPlane_type->set_attributes({
    },{
            false
    });
    IFC4_IfcPlate_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPlateTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPlateStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPlateType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPlateTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPoint_type->set_attributes({
    },{
            
    });
    IFC4_IfcPointOnCurve_type->set_attributes({
            new attribute(strings[2752], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2787], new named_type(IFC4_IfcParameterValue_type), false)
    },{
            false, false
    });
    IFC4_IfcPointOnSurface_type->set_attributes({
            new attribute(strings[2520], new named_type(IFC4_IfcSurface_type), false),
            new attribute(strings[2788], new named_type(IFC4_IfcParameterValue_type), false),
            new attribute(strings[2789], new named_type(IFC4_IfcParameterValue_type), false)
    },{
            false, false, false
    });
    IFC4_IfcPolyLoop_type->set_attributes({
            new attribute(strings[2790], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_IfcCartesianPoint_type)), false)
    },{
            false
    });
    IFC4_IfcPolygonalBoundedHalfSpace_type->set_attributes({
            new attribute(strings[2479], new named_type(IFC4_IfcAxis2Placement3D_type), false),
            new attribute(strings[2791], new named_type(IFC4_IfcBoundedCurve_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcPolygonalFaceSet_type->set_attributes({
            new attribute(strings[2792], new named_type(IFC4_IfcBoolean_type), true),
            new attribute(strings[2793], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcIndexedPolygonalFace_type)), false),
            new attribute(strings[2794], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcPositiveInteger_type)), true)
    },{
            false, false, false, false
    });
    IFC4_IfcPolyline_type->set_attributes({
            new attribute(strings[2659], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcCartesianPoint_type)), false)
    },{
            false
    });
    IFC4_IfcPort_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcPostalAddress_type->set_attributes({
            new attribute(strings[2795], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2796], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true),
            new attribute(strings[2797], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2798], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2799], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2800], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2801], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPreDefinedColour_type->set_attributes({
    },{
            false
    });
    IFC4_IfcPreDefinedCurveFont_type->set_attributes({
    },{
            false
    });
    IFC4_IfcPreDefinedItem_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false)
    },{
            false
    });
    IFC4_IfcPreDefinedProperties_type->set_attributes({
    },{
            
    });
    IFC4_IfcPreDefinedPropertySet_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcPreDefinedTextFont_type->set_attributes({
    },{
            false
    });
    IFC4_IfcPresentationItem_type->set_attributes({
    },{
            
    });
    IFC4_IfcPresentationLayerAssignment_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2802], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcLayeredItem_type)), false),
            new attribute(strings[2357], new named_type(IFC4_IfcIdentifier_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcPresentationLayerWithStyle_type->set_attributes({
            new attribute(strings[2803], new named_type(IFC4_IfcLogical_type), false),
            new attribute(strings[2804], new named_type(IFC4_IfcLogical_type), false),
            new attribute(strings[2805], new named_type(IFC4_IfcLogical_type), false),
            new attribute(strings[2806], new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4_IfcPresentationStyle_type)), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcPresentationStyle_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4_IfcPresentationStyleAssignment_type->set_attributes({
            new attribute(strings[2807], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPresentationStyleSelect_type)), false)
    },{
            false
    });
    IFC4_IfcProcedure_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcProcedureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcProcedureType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcProcedureTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProcess_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2334], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcProduct_type->set_attributes({
            new attribute(strings[2808], new named_type(IFC4_IfcObjectPlacement_type), true),
            new attribute(strings[2809], new named_type(IFC4_IfcProductRepresentation_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcProductDefinitionShape_type->set_attributes({
    },{
            false, false, false
    });
    IFC4_IfcProductRepresentation_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2810], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcRepresentation_type)), false)
    },{
            false, false, false
    });
    IFC4_IfcProfileDef_type->set_attributes({
            new attribute(strings[2811], new named_type(IFC4_IfcProfileTypeEnum_type), false),
            new attribute(strings[2812], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4_IfcProfileProperties_type->set_attributes({
            new attribute(strings[2813], new named_type(IFC4_IfcProfileDef_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcProject_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProjectLibrary_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProjectOrder_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcProjectOrderTypeEnum_type), true),
            new attribute(strings[2333], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2334], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProjectedCRS_type->set_attributes({
            new attribute(strings[2814], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2815], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2816], new named_type(IFC4_IfcNamedUnit_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcProjectionElement_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcProjectionElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProperty_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcIdentifier_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true)
    },{
            false, false
    });
    IFC4_IfcPropertyAbstraction_type->set_attributes({
    },{
            
    });
    IFC4_IfcPropertyBoundedValue_type->set_attributes({
            new attribute(strings[2817], new named_type(IFC4_IfcValue_type), true),
            new attribute(strings[2818], new named_type(IFC4_IfcValue_type), true),
            new attribute(strings[2535], new named_type(IFC4_IfcUnit_type), true),
            new attribute(strings[2819], new named_type(IFC4_IfcValue_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcPropertyDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcPropertyDependencyRelationship_type->set_attributes({
            new attribute(strings[2820], new named_type(IFC4_IfcProperty_type), false),
            new attribute(strings[2821], new named_type(IFC4_IfcProperty_type), false),
            new attribute(strings[2737], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcPropertyEnumeratedValue_type->set_attributes({
            new attribute(strings[2822], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true),
            new attribute(strings[2823], new named_type(IFC4_IfcPropertyEnumeration_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcPropertyEnumeration_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2822], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), false),
            new attribute(strings[2535], new named_type(IFC4_IfcUnit_type), true)
    },{
            false, false, false
    });
    IFC4_IfcPropertyListValue_type->set_attributes({
            new attribute(strings[2669], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true),
            new attribute(strings[2535], new named_type(IFC4_IfcUnit_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcPropertyReferenceValue_type->set_attributes({
            new attribute(strings[2469], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2824], new named_type(IFC4_IfcObjectReferenceSelect_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcPropertySet_type->set_attributes({
            new attribute(strings[2470], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProperty_type)), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcPropertySetDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcPropertySetTemplate_type->set_attributes({
            new attribute(strings[2471], new named_type(IFC4_IfcPropertySetTemplateTypeEnum_type), true),
            new attribute(strings[2825], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2472], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertyTemplate_type)), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcPropertySingleValue_type->set_attributes({
            new attribute(strings[2826], new named_type(IFC4_IfcValue_type), true),
            new attribute(strings[2535], new named_type(IFC4_IfcUnit_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcPropertyTableValue_type->set_attributes({
            new attribute(strings[2827], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true),
            new attribute(strings[2828], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true),
            new attribute(strings[2737], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2829], new named_type(IFC4_IfcUnit_type), true),
            new attribute(strings[2830], new named_type(IFC4_IfcUnit_type), true),
            new attribute(strings[2831], new named_type(IFC4_IfcCurveInterpolationEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcPropertyTemplate_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcPropertyTemplateDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcProtectiveDevice_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcProtectiveDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProtectiveDeviceTrippingUnit_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProtectiveDeviceTrippingUnitType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProtectiveDeviceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcProtectiveDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcProxy_type->set_attributes({
            new attribute(strings[2832], new named_type(IFC4_IfcObjectTypeEnum_type), false),
            new attribute(strings[2589], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPump_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPumpTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcPumpType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcPumpTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcQuantityArea_type->set_attributes({
            new attribute(strings[2833], new named_type(IFC4_IfcAreaMeasure_type), false),
            new attribute(strings[2834], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcQuantityCount_type->set_attributes({
            new attribute(strings[2835], new named_type(IFC4_IfcCountMeasure_type), false),
            new attribute(strings[2834], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcQuantityLength_type->set_attributes({
            new attribute(strings[2836], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2834], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcQuantitySet_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcQuantityTime_type->set_attributes({
            new attribute(strings[2837], new named_type(IFC4_IfcTimeMeasure_type), false),
            new attribute(strings[2834], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcQuantityVolume_type->set_attributes({
            new attribute(strings[2838], new named_type(IFC4_IfcVolumeMeasure_type), false),
            new attribute(strings[2834], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcQuantityWeight_type->set_attributes({
            new attribute(strings[2839], new named_type(IFC4_IfcMassMeasure_type), false),
            new attribute(strings[2834], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcRailing_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcRailingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRailingType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcRailingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRamp_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcRampTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRampFlight_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcRampFlightTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRampFlightType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcRampFlightTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRampType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcRampTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRationalBSplineCurveWithKnots_type->set_attributes({
            new attribute(strings[2840], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcReal_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRationalBSplineSurfaceWithKnots_type->set_attributes({
            new attribute(strings[2840], new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcReal_type))), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRectangleHollowProfileDef_type->set_attributes({
            new attribute(strings[2444], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2841], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2842], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcRectangleProfileDef_type->set_attributes({
            new attribute(strings[2433], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2434], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcRectangularPyramid_type->set_attributes({
            new attribute(strings[2410], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2411], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2781], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcRectangularTrimmedSurface_type->set_attributes({
            new attribute(strings[2520], new named_type(IFC4_IfcSurface_type), false),
            new attribute(strings[2843], new named_type(IFC4_IfcParameterValue_type), false),
            new attribute(strings[2844], new named_type(IFC4_IfcParameterValue_type), false),
            new attribute(strings[2845], new named_type(IFC4_IfcParameterValue_type), false),
            new attribute(strings[2846], new named_type(IFC4_IfcParameterValue_type), false),
            new attribute(strings[2847], new named_type(IFC4_IfcBoolean_type), false),
            new attribute(strings[2848], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcRecurrencePattern_type->set_attributes({
            new attribute(strings[2849], new named_type(IFC4_IfcRecurrenceTypeEnum_type), false),
            new attribute(strings[2850], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDayInMonthNumber_type)), true),
            new attribute(strings[2851], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDayInWeekNumber_type)), true),
            new attribute(strings[2852], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcMonthInYearNumber_type)), true),
            new attribute(strings[2479], new named_type(IFC4_IfcInteger_type), true),
            new attribute(strings[2853], new named_type(IFC4_IfcInteger_type), true),
            new attribute(strings[2854], new named_type(IFC4_IfcInteger_type), true),
            new attribute(strings[2855], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTimePeriod_type)), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcReference_type->set_attributes({
            new attribute(strings[2856], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2857], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2858], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2859], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcInteger_type)), true),
            new attribute(strings[2860], new named_type(IFC4_IfcReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcRegularTimeSeries_type->set_attributes({
            new attribute(strings[2861], new named_type(IFC4_IfcTimeMeasure_type), false),
            new attribute(strings[2667], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTimeSeriesValue_type)), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcReinforcementBarProperties_type->set_attributes({
            new attribute(strings[2862], new named_type(IFC4_IfcAreaMeasure_type), false),
            new attribute(strings[2863], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2864], new named_type(IFC4_IfcReinforcingBarSurfaceEnum_type), true),
            new attribute(strings[2865], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2866], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2867], new named_type(IFC4_IfcCountMeasure_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcReinforcementDefinitionProperties_type->set_attributes({
            new attribute(strings[2868], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2869], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcSectionReinforcementProperties_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcReinforcingBar_type->set_attributes({
            new attribute(strings[2740], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2870], new named_type(IFC4_IfcAreaMeasure_type), true),
            new attribute(strings[2871], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcReinforcingBarTypeEnum_type), true),
            new attribute(strings[2864], new named_type(IFC4_IfcReinforcingBarSurfaceEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcReinforcingBarType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcReinforcingBarTypeEnum_type), false),
            new attribute(strings[2740], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2870], new named_type(IFC4_IfcAreaMeasure_type), true),
            new attribute(strings[2871], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2864], new named_type(IFC4_IfcReinforcingBarSurfaceEnum_type), true),
            new attribute(strings[2872], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2873], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcBendingParameterSelect_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcReinforcingElement_type->set_attributes({
            new attribute(strings[2863], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcReinforcingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcReinforcingMesh_type->set_attributes({
            new attribute(strings[2874], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2875], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2876], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2877], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2878], new named_type(IFC4_IfcAreaMeasure_type), true),
            new attribute(strings[2879], new named_type(IFC4_IfcAreaMeasure_type), true),
            new attribute(strings[2880], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2881], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcReinforcingMeshTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcReinforcingMeshType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcReinforcingMeshTypeEnum_type), false),
            new attribute(strings[2874], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2875], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2876], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2877], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2878], new named_type(IFC4_IfcAreaMeasure_type), true),
            new attribute(strings[2879], new named_type(IFC4_IfcAreaMeasure_type), true),
            new attribute(strings[2880], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2881], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2872], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2873], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcBendingParameterSelect_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelAggregates_type->set_attributes({
            new attribute(strings[2882], new named_type(IFC4_IfcObjectDefinition_type), false),
            new attribute(strings[2883], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObjectDefinition_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelAssigns_type->set_attributes({
            new attribute(strings[2883], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObjectDefinition_type)), false),
            new attribute(strings[2884], new named_type(IFC4_IfcObjectTypeEnum_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelAssignsToActor_type->set_attributes({
            new attribute(strings[2885], new named_type(IFC4_IfcActor_type), false),
            new attribute(strings[2886], new named_type(IFC4_IfcActorRole_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelAssignsToControl_type->set_attributes({
            new attribute(strings[2887], new named_type(IFC4_IfcControl_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcRelAssignsToGroup_type->set_attributes({
            new attribute(strings[2888], new named_type(IFC4_IfcGroup_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcRelAssignsToGroupByFactor_type->set_attributes({
            new attribute(strings[2889], new named_type(IFC4_IfcRatioMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelAssignsToProcess_type->set_attributes({
            new attribute(strings[2890], new named_type(IFC4_IfcProcessSelect_type), false),
            new attribute(strings[2891], new named_type(IFC4_IfcMeasureWithUnit_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelAssignsToProduct_type->set_attributes({
            new attribute(strings[2892], new named_type(IFC4_IfcProductSelect_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcRelAssignsToResource_type->set_attributes({
            new attribute(strings[2893], new named_type(IFC4_IfcResourceSelect_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcRelAssociates_type->set_attributes({
            new attribute(strings[2883], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDefinitionSelect_type)), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcRelAssociatesApproval_type->set_attributes({
            new attribute(strings[2363], new named_type(IFC4_IfcApproval_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelAssociatesClassification_type->set_attributes({
            new attribute(strings[2894], new named_type(IFC4_IfcClassificationSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelAssociatesConstraint_type->set_attributes({
            new attribute(strings[2895], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2896], new named_type(IFC4_IfcConstraint_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcRelAssociatesDocument_type->set_attributes({
            new attribute(strings[2557], new named_type(IFC4_IfcDocumentSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelAssociatesLibrary_type->set_attributes({
            new attribute(strings[2897], new named_type(IFC4_IfcLibrarySelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelAssociatesMaterial_type->set_attributes({
            new attribute(strings[2735], new named_type(IFC4_IfcMaterialSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelConnects_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcRelConnectsElements_type->set_attributes({
            new attribute(strings[2898], new named_type(IFC4_IfcConnectionGeometry_type), true),
            new attribute(strings[2899], new named_type(IFC4_IfcElement_type), false),
            new attribute(strings[2900], new named_type(IFC4_IfcElement_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcRelConnectsPathElements_type->set_attributes({
            new attribute(strings[2901], new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4_IfcInteger_type)), false),
            new attribute(strings[2902], new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4_IfcInteger_type)), false),
            new attribute(strings[2903], new named_type(IFC4_IfcConnectionTypeEnum_type), false),
            new attribute(strings[2904], new named_type(IFC4_IfcConnectionTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelConnectsPortToElement_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4_IfcPort_type), false),
            new attribute(strings[2900], new named_type(IFC4_IfcDistributionElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelConnectsPorts_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4_IfcPort_type), false),
            new attribute(strings[2906], new named_type(IFC4_IfcPort_type), false),
            new attribute(strings[2907], new named_type(IFC4_IfcElement_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcRelConnectsStructuralActivity_type->set_attributes({
            new attribute(strings[2899], new named_type(IFC4_IfcStructuralActivityAssignmentSelect_type), false),
            new attribute(strings[2908], new named_type(IFC4_IfcStructuralActivity_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelConnectsStructuralMember_type->set_attributes({
            new attribute(strings[2909], new named_type(IFC4_IfcStructuralMember_type), false),
            new attribute(strings[2910], new named_type(IFC4_IfcStructuralConnection_type), false),
            new attribute(strings[2911], new named_type(IFC4_IfcBoundaryCondition_type), true),
            new attribute(strings[2912], new named_type(IFC4_IfcStructuralConnectionCondition_type), true),
            new attribute(strings[2913], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2914], new named_type(IFC4_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelConnectsWithEccentricity_type->set_attributes({
            new attribute(strings[2915], new named_type(IFC4_IfcConnectionGeometry_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelConnectsWithRealizingElements_type->set_attributes({
            new attribute(strings[2916], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcElement_type)), false),
            new attribute(strings[2917], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelContainedInSpatialStructure_type->set_attributes({
            new attribute(strings[2918], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProduct_type)), false),
            new attribute(strings[2919], new named_type(IFC4_IfcSpatialElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelCoversBldgElements_type->set_attributes({
            new attribute(strings[2920], new named_type(IFC4_IfcElement_type), false),
            new attribute(strings[2921], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcCovering_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelCoversSpaces_type->set_attributes({
            new attribute(strings[2922], new named_type(IFC4_IfcSpace_type), false),
            new attribute(strings[2921], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcCovering_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelDeclares_type->set_attributes({
            new attribute(strings[2923], new named_type(IFC4_IfcContext_type), false),
            new attribute(strings[2924], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDefinitionSelect_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelDecomposes_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcRelDefines_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcRelDefinesByObject_type->set_attributes({
            new attribute(strings[2883], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObject_type)), false),
            new attribute(strings[2882], new named_type(IFC4_IfcObject_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelDefinesByProperties_type->set_attributes({
            new attribute(strings[2883], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObjectDefinition_type)), false),
            new attribute(strings[2925], new named_type(IFC4_IfcPropertySetDefinitionSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelDefinesByTemplate_type->set_attributes({
            new attribute(strings[2926], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertySetDefinition_type)), false),
            new attribute(strings[2927], new named_type(IFC4_IfcPropertySetTemplate_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelDefinesByType_type->set_attributes({
            new attribute(strings[2883], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcObject_type)), false),
            new attribute(strings[2928], new named_type(IFC4_IfcTypeObject_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelFillsElement_type->set_attributes({
            new attribute(strings[2929], new named_type(IFC4_IfcOpeningElement_type), false),
            new attribute(strings[2930], new named_type(IFC4_IfcElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelFlowControlElements_type->set_attributes({
            new attribute(strings[2931], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcDistributionControlElement_type)), false),
            new attribute(strings[2932], new named_type(IFC4_IfcDistributionFlowElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelInterferesElements_type->set_attributes({
            new attribute(strings[2899], new named_type(IFC4_IfcElement_type), false),
            new attribute(strings[2900], new named_type(IFC4_IfcElement_type), false),
            new attribute(strings[2933], new named_type(IFC4_IfcConnectionGeometry_type), true),
            new attribute(strings[2934], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2935], new simple_type(simple_type::logical_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelNests_type->set_attributes({
            new attribute(strings[2882], new named_type(IFC4_IfcObjectDefinition_type), false),
            new attribute(strings[2883], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcObjectDefinition_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelProjectsElement_type->set_attributes({
            new attribute(strings[2899], new named_type(IFC4_IfcElement_type), false),
            new attribute(strings[2936], new named_type(IFC4_IfcFeatureElementAddition_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelReferencedInSpatialStructure_type->set_attributes({
            new attribute(strings[2918], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcProduct_type)), false),
            new attribute(strings[2919], new named_type(IFC4_IfcSpatialElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelSequence_type->set_attributes({
            new attribute(strings[2890], new named_type(IFC4_IfcProcess_type), false),
            new attribute(strings[2937], new named_type(IFC4_IfcProcess_type), false),
            new attribute(strings[2938], new named_type(IFC4_IfcLagTime_type), true),
            new attribute(strings[2939], new named_type(IFC4_IfcSequenceEnum_type), true),
            new attribute(strings[2940], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelServicesBuildings_type->set_attributes({
            new attribute(strings[2941], new named_type(IFC4_IfcSystem_type), false),
            new attribute(strings[2942], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcSpatialElement_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelSpaceBoundary_type->set_attributes({
            new attribute(strings[2922], new named_type(IFC4_IfcSpaceBoundarySelect_type), false),
            new attribute(strings[2930], new named_type(IFC4_IfcElement_type), false),
            new attribute(strings[2898], new named_type(IFC4_IfcConnectionGeometry_type), true),
            new attribute(strings[2943], new named_type(IFC4_IfcPhysicalOrVirtualEnum_type), false),
            new attribute(strings[2944], new named_type(IFC4_IfcInternalOrExternalEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelSpaceBoundary1stLevel_type->set_attributes({
            new attribute(strings[2945], new named_type(IFC4_IfcRelSpaceBoundary1stLevel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelSpaceBoundary2ndLevel_type->set_attributes({
            new attribute(strings[2946], new named_type(IFC4_IfcRelSpaceBoundary2ndLevel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRelVoidsElement_type->set_attributes({
            new attribute(strings[2920], new named_type(IFC4_IfcElement_type), false),
            new attribute(strings[2947], new named_type(IFC4_IfcFeatureElementSubtraction_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcRelationship_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcReparametrisedCompositeCurveSegment_type->set_attributes({
            new attribute(strings[2948], new named_type(IFC4_IfcParameterValue_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcRepresentation_type->set_attributes({
            new attribute(strings[2949], new named_type(IFC4_IfcRepresentationContext_type), false),
            new attribute(strings[2950], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2951], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2952], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcRepresentationItem_type)), false)
    },{
            false, false, false, false
    });
    IFC4_IfcRepresentationContext_type->set_attributes({
            new attribute(strings[2953], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2954], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4_IfcRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4_IfcRepresentationMap_type->set_attributes({
            new attribute(strings[2955], new named_type(IFC4_IfcAxis2Placement_type), false),
            new attribute(strings[2956], new named_type(IFC4_IfcRepresentation_type), false)
    },{
            false, false
    });
    IFC4_IfcResource_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2334], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcResourceApprovalRelationship_type->set_attributes({
            new attribute(strings[2605], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcResourceObjectSelect_type)), false),
            new attribute(strings[2363], new named_type(IFC4_IfcApproval_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcResourceConstraintRelationship_type->set_attributes({
            new attribute(strings[2896], new named_type(IFC4_IfcConstraint_type), false),
            new attribute(strings[2605], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcResourceObjectSelect_type)), false)
    },{
            false, false, false, false
    });
    IFC4_IfcResourceLevelRelationship_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true)
    },{
            false, false
    });
    IFC4_IfcResourceTime_type->set_attributes({
            new attribute(strings[2957], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[2958], new named_type(IFC4_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[2959], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2960], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2961], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2962], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[2963], new named_type(IFC4_IfcBoolean_type), true),
            new attribute(strings[2964], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2965], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[2966], new named_type(IFC4_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[2967], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2968], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2969], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[2970], new named_type(IFC4_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[2971], new named_type(IFC4_IfcPositiveRatioMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRevolvedAreaSolid_type->set_attributes({
            new attribute(strings[2389], new named_type(IFC4_IfcAxis1Placement_type), false),
            new attribute(strings[2972], new named_type(IFC4_IfcPlaneAngleMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcRevolvedAreaSolidTapered_type->set_attributes({
            new attribute(strings[2607], new named_type(IFC4_IfcProfileDef_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcRightCircularCone_type->set_attributes({
            new attribute(strings[2781], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2973], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4_IfcRightCircularCylinder_type->set_attributes({
            new attribute(strings[2781], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2457], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4_IfcRoof_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcRoofTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRoofType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcRoofTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcRoot_type->set_attributes({
            new attribute(strings[2974], new named_type(IFC4_IfcGloballyUniqueId_type), false),
            new attribute(strings[2975], new named_type(IFC4_IfcOwnerHistory_type), true),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcRoundedRectangleProfileDef_type->set_attributes({
            new attribute(strings[2976], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcSIUnit_type->set_attributes({
            new attribute(strings[2977], new named_type(IFC4_IfcSIPrefix_type), true),
            new attribute(strings[2348], new named_type(IFC4_IfcSIUnitName_type), false)
    },{
            true, false, false, false
    });
    IFC4_IfcSanitaryTerminal_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSanitaryTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSanitaryTerminalType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSanitaryTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSchedulingTime_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2978], new named_type(IFC4_IfcDataOriginEnum_type), true),
            new attribute(strings[2979], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4_IfcSeamCurve_type->set_attributes({
    },{
            false, false, false
    });
    IFC4_IfcSectionProperties_type->set_attributes({
            new attribute(strings[2980], new named_type(IFC4_IfcSectionTypeEnum_type), false),
            new attribute(strings[2981], new named_type(IFC4_IfcProfileDef_type), false),
            new attribute(strings[2982], new named_type(IFC4_IfcProfileDef_type), true)
    },{
            false, false, false
    });
    IFC4_IfcSectionReinforcementProperties_type->set_attributes({
            new attribute(strings[2983], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2984], new named_type(IFC4_IfcLengthMeasure_type), false),
            new attribute(strings[2985], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2986], new named_type(IFC4_IfcReinforcingBarRoleEnum_type), false),
            new attribute(strings[2987], new named_type(IFC4_IfcSectionProperties_type), false),
            new attribute(strings[2988], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcReinforcementBarProperties_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcSectionedSpine_type->set_attributes({
            new attribute(strings[2989], new named_type(IFC4_IfcCompositeCurve_type), false),
            new attribute(strings[2990], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcProfileDef_type)), false),
            new attribute(strings[2991], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_IfcAxis2Placement3D_type)), false)
    },{
            false, false, false
    });
    IFC4_IfcSensor_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSensorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSensorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSensorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcShadingDevice_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcShadingDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcShadingDeviceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcShadingDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcShapeAspect_type->set_attributes({
            new attribute(strings[2992], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcShapeModel_type)), false),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2993], new named_type(IFC4_IfcLogical_type), false),
            new attribute(strings[2994], new named_type(IFC4_IfcProductRepresentationSelect_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcShapeModel_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcShapeRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcShellBasedSurfaceModel_type->set_attributes({
            new attribute(strings[2995], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcShell_type)), false)
    },{
            false
    });
    IFC4_IfcSimpleProperty_type->set_attributes({
    },{
            false, false
    });
    IFC4_IfcSimplePropertyTemplate_type->set_attributes({
            new attribute(strings[2471], new named_type(IFC4_IfcSimplePropertyTemplateTypeEnum_type), true),
            new attribute(strings[2996], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2997], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2998], new named_type(IFC4_IfcPropertyEnumeration_type), true),
            new attribute(strings[2999], new named_type(IFC4_IfcUnit_type), true),
            new attribute(strings[3000], new named_type(IFC4_IfcUnit_type), true),
            new attribute(strings[2737], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[3001], new named_type(IFC4_IfcStateEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSite_type->set_attributes({
            new attribute(strings[3002], new named_type(IFC4_IfcCompoundPlaneAngleMeasure_type), true),
            new attribute(strings[3003], new named_type(IFC4_IfcCompoundPlaneAngleMeasure_type), true),
            new attribute(strings[3004], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[3005], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[3006], new named_type(IFC4_IfcPostalAddress_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSlab_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSlabTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSlabElementedCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSlabStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSlabType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSlabTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSlippageConnectionCondition_type->set_attributes({
            new attribute(strings[3007], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[3008], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[3009], new named_type(IFC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcSolarDevice_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSolarDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSolarDeviceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSolarDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSolidModel_type->set_attributes({
    },{
            
    });
    IFC4_IfcSpace_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSpaceTypeEnum_type), true),
            new attribute(strings[3010], new named_type(IFC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpaceHeater_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSpaceHeaterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpaceHeaterType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSpaceHeaterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpaceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSpaceTypeEnum_type), false),
            new attribute(strings[2441], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpatialElement_type->set_attributes({
            new attribute(strings[2441], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpatialElementType_type->set_attributes({
            new attribute(strings[2593], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpatialStructureElement_type->set_attributes({
            new attribute(strings[3011], new named_type(IFC4_IfcElementCompositionEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpatialStructureElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpatialZone_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSpatialZoneTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSpatialZoneType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSpatialZoneTypeEnum_type), false),
            new attribute(strings[2441], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSphere_type->set_attributes({
            new attribute(strings[2457], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4_IfcSphericalSurface_type->set_attributes({
            new attribute(strings[2457], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4_IfcStackTerminal_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStackTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStackTerminalType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStackTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStair_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStairTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStairFlight_type->set_attributes({
            new attribute(strings[3012], new named_type(IFC4_IfcInteger_type), true),
            new attribute(strings[3013], new named_type(IFC4_IfcInteger_type), true),
            new attribute(strings[3014], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3015], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcStairFlightTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStairFlightType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStairFlightTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStairType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStairTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralAction_type->set_attributes({
            new attribute(strings[3016], new named_type(IFC4_IfcBoolean_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralActivity_type->set_attributes({
            new attribute(strings[3017], new named_type(IFC4_IfcStructuralLoad_type), false),
            new attribute(strings[3018], new named_type(IFC4_IfcGlobalOrLocalEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralAnalysisModel_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcAnalysisModelTypeEnum_type), false),
            new attribute(strings[3019], new named_type(IFC4_IfcAxis2Placement3D_type), true),
            new attribute(strings[3020], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcStructuralLoadGroup_type)), true),
            new attribute(strings[3021], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcStructuralResultGroup_type)), true),
            new attribute(strings[3022], new named_type(IFC4_IfcObjectPlacement_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralConnection_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4_IfcBoundaryCondition_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralConnectionCondition_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4_IfcStructuralCurveAction_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4_IfcProjectedOrTrueLengthEnum_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcStructuralCurveActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralCurveConnection_type->set_attributes({
            new attribute(strings[2389], new named_type(IFC4_IfcDirection_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralCurveMember_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStructuralCurveMemberTypeEnum_type), false),
            new attribute(strings[2389], new named_type(IFC4_IfcDirection_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralCurveMemberVarying_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralCurveReaction_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStructuralCurveActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralItem_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLinearAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLoad_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4_IfcStructuralLoadCase_type->set_attributes({
            new attribute(strings[3024], new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcRatioMeasure_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLoadConfiguration_type->set_attributes({
            new attribute(strings[2667], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcStructuralLoadOrResult_type)), false),
            new attribute(strings[3025], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4_IfcLengthMeasure_type))), true)
    },{
            false, false, false
    });
    IFC4_IfcStructuralLoadGroup_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcLoadGroupTypeEnum_type), false),
            new attribute(strings[3026], new named_type(IFC4_IfcActionTypeEnum_type), false),
            new attribute(strings[3027], new named_type(IFC4_IfcActionSourceTypeEnum_type), false),
            new attribute(strings[3028], new named_type(IFC4_IfcRatioMeasure_type), true),
            new attribute(strings[2339], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLoadLinearForce_type->set_attributes({
            new attribute(strings[3029], new named_type(IFC4_IfcLinearForceMeasure_type), true),
            new attribute(strings[3030], new named_type(IFC4_IfcLinearForceMeasure_type), true),
            new attribute(strings[3031], new named_type(IFC4_IfcLinearForceMeasure_type), true),
            new attribute(strings[3032], new named_type(IFC4_IfcLinearMomentMeasure_type), true),
            new attribute(strings[3033], new named_type(IFC4_IfcLinearMomentMeasure_type), true),
            new attribute(strings[3034], new named_type(IFC4_IfcLinearMomentMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLoadOrResult_type->set_attributes({
    },{
            false
    });
    IFC4_IfcStructuralLoadPlanarForce_type->set_attributes({
            new attribute(strings[3035], new named_type(IFC4_IfcPlanarForceMeasure_type), true),
            new attribute(strings[3036], new named_type(IFC4_IfcPlanarForceMeasure_type), true),
            new attribute(strings[3037], new named_type(IFC4_IfcPlanarForceMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcStructuralLoadSingleDisplacement_type->set_attributes({
            new attribute(strings[3038], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[3039], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[3040], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[3041], new named_type(IFC4_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3042], new named_type(IFC4_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3043], new named_type(IFC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLoadSingleDisplacementDistortion_type->set_attributes({
            new attribute(strings[3044], new named_type(IFC4_IfcCurvatureMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLoadSingleForce_type->set_attributes({
            new attribute(strings[3045], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[3046], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[3047], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[3048], new named_type(IFC4_IfcTorqueMeasure_type), true),
            new attribute(strings[3049], new named_type(IFC4_IfcTorqueMeasure_type), true),
            new attribute(strings[3050], new named_type(IFC4_IfcTorqueMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLoadSingleForceWarping_type->set_attributes({
            new attribute(strings[3051], new named_type(IFC4_IfcWarpingMomentMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralLoadStatic_type->set_attributes({
    },{
            false
    });
    IFC4_IfcStructuralLoadTemperature_type->set_attributes({
            new attribute(strings[3052], new named_type(IFC4_IfcThermodynamicTemperatureMeasure_type), true),
            new attribute(strings[3053], new named_type(IFC4_IfcThermodynamicTemperatureMeasure_type), true),
            new attribute(strings[3054], new named_type(IFC4_IfcThermodynamicTemperatureMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcStructuralMember_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralPlanarAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralPointAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralPointConnection_type->set_attributes({
            new attribute(strings[2914], new named_type(IFC4_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralPointReaction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralReaction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralResultGroup_type->set_attributes({
            new attribute(strings[3055], new named_type(IFC4_IfcAnalysisTheoryTypeEnum_type), false),
            new attribute(strings[3056], new named_type(IFC4_IfcStructuralLoadGroup_type), true),
            new attribute(strings[3057], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralSurfaceAction_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4_IfcProjectedOrTrueLengthEnum_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcStructuralSurfaceActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralSurfaceConnection_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralSurfaceMember_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStructuralSurfaceMemberTypeEnum_type), false),
            new attribute(strings[2456], new named_type(IFC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralSurfaceMemberVarying_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStructuralSurfaceReaction_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcStructuralSurfaceActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcStyleModel_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcStyledItem_type->set_attributes({
            new attribute(strings[3058], new named_type(IFC4_IfcRepresentationItem_type), true),
            new attribute(strings[2807], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcStyleAssignmentSelect_type)), false),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4_IfcStyledRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcSubContractResource_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSubContractResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSubContractResourceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSubContractResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSubedge_type->set_attributes({
            new attribute(strings[3059], new named_type(IFC4_IfcEdge_type), false)
    },{
            false, false, false
    });
    IFC4_IfcSurface_type->set_attributes({
    },{
            
    });
    IFC4_IfcSurfaceCurve_type->set_attributes({
            new attribute(strings[3060], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[3061], new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4_IfcPcurve_type)), false),
            new attribute(strings[3062], new named_type(IFC4_IfcPreferredSurfaceCurveRepresentation_type), false)
    },{
            false, false, false
    });
    IFC4_IfcSurfaceCurveSweptAreaSolid_type->set_attributes({
            new attribute(strings[2629], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2630], new named_type(IFC4_IfcParameterValue_type), true),
            new attribute(strings[2631], new named_type(IFC4_IfcParameterValue_type), true),
            new attribute(strings[3063], new named_type(IFC4_IfcSurface_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcSurfaceFeature_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSurfaceFeatureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSurfaceOfLinearExtrusion_type->set_attributes({
            new attribute(strings[2606], new named_type(IFC4_IfcDirection_type), false),
            new attribute(strings[2442], new named_type(IFC4_IfcLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcSurfaceOfRevolution_type->set_attributes({
            new attribute(strings[3064], new named_type(IFC4_IfcAxis1Placement_type), false)
    },{
            false, false, false
    });
    IFC4_IfcSurfaceReinforcementArea_type->set_attributes({
            new attribute(strings[3065], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_IfcLengthMeasure_type)), true),
            new attribute(strings[3066], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_IfcLengthMeasure_type)), true),
            new attribute(strings[3067], new named_type(IFC4_IfcRatioMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4_IfcSurfaceStyle_type->set_attributes({
            new attribute(strings[3068], new named_type(IFC4_IfcSurfaceSide_type), false),
            new attribute(strings[2807], new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC4_IfcSurfaceStyleElementSelect_type)), false)
    },{
            false, false, false
    });
    IFC4_IfcSurfaceStyleLighting_type->set_attributes({
            new attribute(strings[3069], new named_type(IFC4_IfcColourRgb_type), false),
            new attribute(strings[3070], new named_type(IFC4_IfcColourRgb_type), false),
            new attribute(strings[3071], new named_type(IFC4_IfcColourRgb_type), false),
            new attribute(strings[3072], new named_type(IFC4_IfcColourRgb_type), false)
    },{
            false, false, false, false
    });
    IFC4_IfcSurfaceStyleRefraction_type->set_attributes({
            new attribute(strings[3073], new named_type(IFC4_IfcReal_type), true),
            new attribute(strings[3074], new named_type(IFC4_IfcReal_type), true)
    },{
            false, false
    });
    IFC4_IfcSurfaceStyleRendering_type->set_attributes({
            new attribute(strings[3075], new named_type(IFC4_IfcColourOrFactor_type), true),
            new attribute(strings[3071], new named_type(IFC4_IfcColourOrFactor_type), true),
            new attribute(strings[3069], new named_type(IFC4_IfcColourOrFactor_type), true),
            new attribute(strings[3076], new named_type(IFC4_IfcColourOrFactor_type), true),
            new attribute(strings[3077], new named_type(IFC4_IfcColourOrFactor_type), true),
            new attribute(strings[3078], new named_type(IFC4_IfcSpecularHighlightSelect_type), true),
            new attribute(strings[3079], new named_type(IFC4_IfcReflectanceMethodEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSurfaceStyleShading_type->set_attributes({
            new attribute(strings[3080], new named_type(IFC4_IfcColourRgb_type), false),
            new attribute(strings[3081], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true)
    },{
            false, false
    });
    IFC4_IfcSurfaceStyleWithTextures_type->set_attributes({
            new attribute(strings[3082], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcSurfaceTexture_type)), false)
    },{
            false
    });
    IFC4_IfcSurfaceTexture_type->set_attributes({
            new attribute(strings[3083], new named_type(IFC4_IfcBoolean_type), false),
            new attribute(strings[3084], new named_type(IFC4_IfcBoolean_type), false),
            new attribute(strings[3085], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[3086], new named_type(IFC4_IfcCartesianTransformationOperator2D_type), true),
            new attribute(strings[3087], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcIdentifier_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcSweptAreaSolid_type->set_attributes({
            new attribute(strings[3088], new named_type(IFC4_IfcProfileDef_type), false),
            new attribute(strings[2479], new named_type(IFC4_IfcAxis2Placement3D_type), true)
    },{
            false, false
    });
    IFC4_IfcSweptDiskSolid_type->set_attributes({
            new attribute(strings[2629], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[2457], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3089], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2630], new named_type(IFC4_IfcParameterValue_type), true),
            new attribute(strings[2631], new named_type(IFC4_IfcParameterValue_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcSweptDiskSolidPolygonal_type->set_attributes({
            new attribute(strings[2651], new named_type(IFC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcSweptSurface_type->set_attributes({
            new attribute(strings[3090], new named_type(IFC4_IfcProfileDef_type), false),
            new attribute(strings[2479], new named_type(IFC4_IfcAxis2Placement3D_type), true)
    },{
            false, false
    });
    IFC4_IfcSwitchingDevice_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSwitchingDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSwitchingDeviceType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSwitchingDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSystem_type->set_attributes({
    },{
            false, false, false, false, false
    });
    IFC4_IfcSystemFurnitureElement_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSystemFurnitureElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcSystemFurnitureElementType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcSystemFurnitureElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTShapeProfileDef_type->set_attributes({
            new attribute(strings[2442], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3091], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2379], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2650], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2651], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2652], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3092], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3093], new named_type(IFC4_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[2653], new named_type(IFC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTable_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[3094], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTableRow_type)), true),
            new attribute(strings[3095], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTableColumn_type)), true)
    },{
            false, false, false
    });
    IFC4_IfcTableColumn_type->set_attributes({
            new attribute(strings[2357], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[2535], new named_type(IFC4_IfcUnit_type), true),
            new attribute(strings[2745], new named_type(IFC4_IfcReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcTableRow_type->set_attributes({
            new attribute(strings[3096], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), true),
            new attribute(strings[3097], new named_type(IFC4_IfcBoolean_type), true)
    },{
            false, false
    });
    IFC4_IfcTank_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTankTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTankType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTankTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTask_type->set_attributes({
            new attribute(strings[2333], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[3098], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[3099], new named_type(IFC4_IfcBoolean_type), false),
            new attribute(strings[2717], new named_type(IFC4_IfcInteger_type), true),
            new attribute(strings[3100], new named_type(IFC4_IfcTaskTime_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcTaskTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTaskTime_type->set_attributes({
            new attribute(strings[2673], new named_type(IFC4_IfcTaskDurationEnum_type), true),
            new attribute(strings[3101], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[2959], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2960], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[3102], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[3103], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[3104], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[3105], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[3106], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[3107], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[3108], new named_type(IFC4_IfcBoolean_type), true),
            new attribute(strings[2964], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[3109], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[2967], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[2968], new named_type(IFC4_IfcDateTime_type), true),
            new attribute(strings[3110], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[2971], new named_type(IFC4_IfcPositiveRatioMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTaskTimeRecurring_type->set_attributes({
            new attribute(strings[3111], new named_type(IFC4_IfcRecurrencePattern_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTaskType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTaskTypeEnum_type), false),
            new attribute(strings[3098], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTelecomAddress_type->set_attributes({
            new attribute(strings[3112], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true),
            new attribute(strings[3113], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true),
            new attribute(strings[3114], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[3115], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcLabel_type)), true),
            new attribute(strings[3116], new named_type(IFC4_IfcURIReference_type), true),
            new attribute(strings[3117], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcURIReference_type)), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTendon_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTendonTypeEnum_type), true),
            new attribute(strings[2740], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2870], new named_type(IFC4_IfcAreaMeasure_type), true),
            new attribute(strings[3118], new named_type(IFC4_IfcForceMeasure_type), true),
            new attribute(strings[3119], new named_type(IFC4_IfcPressureMeasure_type), true),
            new attribute(strings[3120], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3121], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3122], new named_type(IFC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTendonAnchor_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTendonAnchorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTendonAnchorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTendonAnchorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTendonType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTendonTypeEnum_type), false),
            new attribute(strings[2740], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2870], new named_type(IFC4_IfcAreaMeasure_type), true),
            new attribute(strings[3123], new named_type(IFC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTessellatedFaceSet_type->set_attributes({
            new attribute(strings[2447], new named_type(IFC4_IfcCartesianPointList3D_type), false)
    },{
            false
    });
    IFC4_IfcTessellatedItem_type->set_attributes({
    },{
            
    });
    IFC4_IfcTextLiteral_type->set_attributes({
            new attribute(strings[3124], new named_type(IFC4_IfcPresentableText_type), false),
            new attribute(strings[2784], new named_type(IFC4_IfcAxis2Placement_type), false),
            new attribute(strings[3125], new named_type(IFC4_IfcTextPath_type), false)
    },{
            false, false, false
    });
    IFC4_IfcTextLiteralWithExtent_type->set_attributes({
            new attribute(strings[3126], new named_type(IFC4_IfcPlanarExtent_type), false),
            new attribute(strings[3127], new named_type(IFC4_IfcBoxAlignment_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcTextStyle_type->set_attributes({
            new attribute(strings[3128], new named_type(IFC4_IfcTextStyleForDefinedFont_type), true),
            new attribute(strings[3129], new named_type(IFC4_IfcTextStyleTextModel_type), true),
            new attribute(strings[3130], new named_type(IFC4_IfcTextFontSelect_type), false),
            new attribute(strings[2526], new named_type(IFC4_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcTextStyleFontModel_type->set_attributes({
            new attribute(strings[3131], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcTextFontName_type)), false),
            new attribute(strings[3132], new named_type(IFC4_IfcFontStyle_type), true),
            new attribute(strings[3133], new named_type(IFC4_IfcFontVariant_type), true),
            new attribute(strings[3134], new named_type(IFC4_IfcFontWeight_type), true),
            new attribute(strings[3135], new named_type(IFC4_IfcSizeSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcTextStyleForDefinedFont_type->set_attributes({
            new attribute(strings[3136], new named_type(IFC4_IfcColour_type), false),
            new attribute(strings[3137], new named_type(IFC4_IfcColour_type), true)
    },{
            false, false
    });
    IFC4_IfcTextStyleTextModel_type->set_attributes({
            new attribute(strings[3138], new named_type(IFC4_IfcSizeSelect_type), true),
            new attribute(strings[3139], new named_type(IFC4_IfcTextAlignment_type), true),
            new attribute(strings[3140], new named_type(IFC4_IfcTextDecoration_type), true),
            new attribute(strings[3141], new named_type(IFC4_IfcSizeSelect_type), true),
            new attribute(strings[3142], new named_type(IFC4_IfcSizeSelect_type), true),
            new attribute(strings[3143], new named_type(IFC4_IfcTextTransformation_type), true),
            new attribute(strings[3144], new named_type(IFC4_IfcSizeSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcTextureCoordinate_type->set_attributes({
            new attribute(strings[3145], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcSurfaceTexture_type)), false)
    },{
            false
    });
    IFC4_IfcTextureCoordinateGenerator_type->set_attributes({
            new attribute(strings[3085], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[3087], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcReal_type)), true)
    },{
            false, false, false
    });
    IFC4_IfcTextureMap_type->set_attributes({
            new attribute(strings[3146], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_IfcTextureVertex_type)), false),
            new attribute(strings[2655], new named_type(IFC4_IfcFace_type), false)
    },{
            false, false, false
    });
    IFC4_IfcTextureVertex_type->set_attributes({
            new attribute(strings[2447], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcParameterValue_type)), false)
    },{
            false
    });
    IFC4_IfcTextureVertexList_type->set_attributes({
            new attribute(strings[3147], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcParameterValue_type))), false)
    },{
            false
    });
    IFC4_IfcTimePeriod_type->set_attributes({
            new attribute(strings[3148], new named_type(IFC4_IfcTime_type), false),
            new attribute(strings[3149], new named_type(IFC4_IfcTime_type), false)
    },{
            false, false
    });
    IFC4_IfcTimeSeries_type->set_attributes({
            new attribute(strings[2348], new named_type(IFC4_IfcLabel_type), false),
            new attribute(strings[2338], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[3148], new named_type(IFC4_IfcDateTime_type), false),
            new attribute(strings[3149], new named_type(IFC4_IfcDateTime_type), false),
            new attribute(strings[3150], new named_type(IFC4_IfcTimeSeriesDataTypeEnum_type), false),
            new attribute(strings[2978], new named_type(IFC4_IfcDataOriginEnum_type), false),
            new attribute(strings[2979], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[2535], new named_type(IFC4_IfcUnit_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcTimeSeriesValue_type->set_attributes({
            new attribute(strings[2669], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcValue_type)), false)
    },{
            false
    });
    IFC4_IfcTopologicalRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4_IfcTopologyRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4_IfcToroidalSurface_type->set_attributes({
            new attribute(strings[3151], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3152], new named_type(IFC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4_IfcTransformer_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTransformerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTransformerType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTransformerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTransportElement_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTransportElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTransportElementType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTransportElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTrapeziumProfileDef_type->set_attributes({
            new attribute(strings[3153], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3154], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2434], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3155], new named_type(IFC4_IfcLengthMeasure_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4_IfcTriangulatedFaceSet_type->set_attributes({
            new attribute(strings[3156], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcParameterValue_type))), true),
            new attribute(strings[2792], new named_type(IFC4_IfcBoolean_type), true),
            new attribute(strings[2660], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_IfcPositiveInteger_type))), false),
            new attribute(strings[2794], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcPositiveInteger_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4_IfcTrimmedCurve_type->set_attributes({
            new attribute(strings[2752], new named_type(IFC4_IfcCurve_type), false),
            new attribute(strings[3157], new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4_IfcTrimmingSelect_type)), false),
            new attribute(strings[3158], new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4_IfcTrimmingSelect_type)), false),
            new attribute(strings[3159], new named_type(IFC4_IfcBoolean_type), false),
            new attribute(strings[3062], new named_type(IFC4_IfcTrimmingPreference_type), false)
    },{
            false, false, false, false, false
    });
    IFC4_IfcTubeBundle_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTubeBundleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTubeBundleType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcTubeBundleTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTypeObject_type->set_attributes({
            new attribute(strings[3160], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[3161], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPropertySetDefinition_type)), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcTypeProcess_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2334], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[3162], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcTypeProduct_type->set_attributes({
            new attribute(strings[3163], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_IfcRepresentationMap_type)), true),
            new attribute(strings[2589], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcTypeResource_type->set_attributes({
            new attribute(strings[2368], new named_type(IFC4_IfcIdentifier_type), true),
            new attribute(strings[2334], new named_type(IFC4_IfcText_type), true),
            new attribute(strings[3164], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcUShapeProfileDef_type->set_attributes({
            new attribute(strings[2442], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3091], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2379], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2650], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2651], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2670], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2653], new named_type(IFC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcUnitAssignment_type->set_attributes({
            new attribute(strings[3165], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcUnit_type)), false)
    },{
            false
    });
    IFC4_IfcUnitaryControlElement_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcUnitaryControlElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcUnitaryControlElementType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcUnitaryControlElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcUnitaryEquipment_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcUnitaryEquipmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcUnitaryEquipmentType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcUnitaryEquipmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcValve_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcValveTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcValveType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcValveTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcVector_type->set_attributes({
            new attribute(strings[2611], new named_type(IFC4_IfcDirection_type), false),
            new attribute(strings[3166], new named_type(IFC4_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4_IfcVertex_type->set_attributes({
    },{
            
    });
    IFC4_IfcVertexLoop_type->set_attributes({
            new attribute(strings[3167], new named_type(IFC4_IfcVertex_type), false)
    },{
            false
    });
    IFC4_IfcVertexPoint_type->set_attributes({
            new attribute(strings[3168], new named_type(IFC4_IfcPoint_type), false)
    },{
            false
    });
    IFC4_IfcVibrationIsolator_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcVibrationIsolatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcVibrationIsolatorType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcVibrationIsolatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcVirtualElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4_IfcVirtualGridIntersection_type->set_attributes({
            new attribute(strings[3169], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_IfcGridAxis_type)), false),
            new attribute(strings[3170], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_IfcLengthMeasure_type)), false)
    },{
            false, false
    });
    IFC4_IfcVoidingFeature_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcVoidingFeatureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWall_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcWallTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWallElementedCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWallStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWallType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcWallTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWasteTerminal_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcWasteTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWasteTerminalType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcWasteTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWindow_type->set_attributes({
            new attribute(strings[2561], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2562], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2332], new named_type(IFC4_IfcWindowTypeEnum_type), true),
            new attribute(strings[3171], new named_type(IFC4_IfcWindowTypePartitioningEnum_type), true),
            new attribute(strings[3172], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWindowLiningProperties_type->set_attributes({
            new attribute(strings[2565], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2566], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2569], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3173], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3174], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3175], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3176], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3177], new named_type(IFC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2575], new named_type(IFC4_IfcShapeAspect_type), true),
            new attribute(strings[2571], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2576], new named_type(IFC4_IfcLengthMeasure_type), true),
            new attribute(strings[2577], new named_type(IFC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWindowPanelProperties_type->set_attributes({
            new attribute(strings[2563], new named_type(IFC4_IfcWindowPanelOperationEnum_type), false),
            new attribute(strings[2581], new named_type(IFC4_IfcWindowPanelPositionEnum_type), false),
            new attribute(strings[2769], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2770], new named_type(IFC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2575], new named_type(IFC4_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWindowStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWindowStyle_type->set_attributes({
            new attribute(strings[2582], new named_type(IFC4_IfcWindowStyleConstructionEnum_type), false),
            new attribute(strings[2563], new named_type(IFC4_IfcWindowStyleOperationEnum_type), false),
            new attribute(strings[2583], new named_type(IFC4_IfcBoolean_type), false),
            new attribute(strings[2584], new named_type(IFC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWindowType_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcWindowTypeEnum_type), false),
            new attribute(strings[3171], new named_type(IFC4_IfcWindowTypePartitioningEnum_type), false),
            new attribute(strings[2583], new named_type(IFC4_IfcBoolean_type), true),
            new attribute(strings[3172], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWorkCalendar_type->set_attributes({
            new attribute(strings[3178], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcWorkTime_type)), true),
            new attribute(strings[3179], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcWorkTime_type)), true),
            new attribute(strings[2332], new named_type(IFC4_IfcWorkCalendarTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWorkControl_type->set_attributes({
            new attribute(strings[2766], new named_type(IFC4_IfcDateTime_type), false),
            new attribute(strings[3180], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_IfcPerson_type)), true),
            new attribute(strings[2339], new named_type(IFC4_IfcLabel_type), true),
            new attribute(strings[3181], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[3107], new named_type(IFC4_IfcDuration_type), true),
            new attribute(strings[3148], new named_type(IFC4_IfcDateTime_type), false),
            new attribute(strings[3182], new named_type(IFC4_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWorkPlan_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcWorkPlanTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWorkSchedule_type->set_attributes({
            new attribute(strings[2332], new named_type(IFC4_IfcWorkScheduleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcWorkTime_type->set_attributes({
            new attribute(strings[3183], new named_type(IFC4_IfcRecurrencePattern_type), true),
            new attribute(strings[3184], new named_type(IFC4_IfcDate_type), true),
            new attribute(strings[3185], new named_type(IFC4_IfcDate_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcZShapeProfileDef_type->set_attributes({
            new attribute(strings[2442], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3091], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2379], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2650], new named_type(IFC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2651], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2670], new named_type(IFC4_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4_IfcZone_type->set_attributes({
            new attribute(strings[2441], new named_type(IFC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4_IfcActor_type->set_inverse_attributes({
            new inverse_attribute(strings[3186], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToActor_type, IFC4_IfcRelAssignsToActor_type->attributes()[0])
    });
    IFC4_IfcActorRole_type->set_inverse_attributes({
            new inverse_attribute(strings[3187], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4_IfcAddress_type->set_inverse_attributes({
            new inverse_attribute(strings[3188], inverse_attribute::set_type, 0, -1, IFC4_IfcPerson_type, IFC4_IfcPerson_type->attributes()[7]),
            new inverse_attribute(strings[3189], inverse_attribute::set_type, 0, -1, IFC4_IfcOrganization_type, IFC4_IfcOrganization_type->attributes()[4])
    });
    IFC4_IfcAnnotation_type->set_inverse_attributes({
            new inverse_attribute(strings[3190], inverse_attribute::set_type, 0, 1, IFC4_IfcRelContainedInSpatialStructure_type, IFC4_IfcRelContainedInSpatialStructure_type->attributes()[0])
    });
    IFC4_IfcAppliedValue_type->set_inverse_attributes({
            new inverse_attribute(strings[3187], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4_IfcApproval_type->set_inverse_attributes({
            new inverse_attribute(strings[3191], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3192], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesApproval_type, IFC4_IfcRelAssociatesApproval_type->attributes()[0]),
            new inverse_attribute(strings[3193], inverse_attribute::set_type, 0, -1, IFC4_IfcResourceApprovalRelationship_type, IFC4_IfcResourceApprovalRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3194], inverse_attribute::set_type, 0, -1, IFC4_IfcApprovalRelationship_type, IFC4_IfcApprovalRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3195], inverse_attribute::set_type, 0, -1, IFC4_IfcApprovalRelationship_type, IFC4_IfcApprovalRelationship_type->attributes()[0])
    });
    IFC4_IfcClassification_type->set_inverse_attributes({
            new inverse_attribute(strings[3196], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesClassification_type, IFC4_IfcRelAssociatesClassification_type->attributes()[0]),
            new inverse_attribute(strings[3197], inverse_attribute::set_type, 0, -1, IFC4_IfcClassificationReference_type, IFC4_IfcClassificationReference_type->attributes()[0])
    });
    IFC4_IfcClassificationReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3198], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesClassification_type, IFC4_IfcRelAssociatesClassification_type->attributes()[0]),
            new inverse_attribute(strings[3197], inverse_attribute::set_type, 0, -1, IFC4_IfcClassificationReference_type, IFC4_IfcClassificationReference_type->attributes()[0])
    });
    IFC4_IfcCompositeCurveSegment_type->set_inverse_attributes({
            new inverse_attribute(strings[3199], inverse_attribute::set_type, 1, -1, IFC4_IfcCompositeCurve_type, IFC4_IfcCompositeCurve_type->attributes()[0])
    });
    IFC4_IfcConstraint_type->set_inverse_attributes({
            new inverse_attribute(strings[3191], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3200], inverse_attribute::set_type, 0, -1, IFC4_IfcResourceConstraintRelationship_type, IFC4_IfcResourceConstraintRelationship_type->attributes()[0])
    });
    IFC4_IfcContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3201], inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByProperties_type, IFC4_IfcRelDefinesByProperties_type->attributes()[0]),
            new inverse_attribute(strings[3202], inverse_attribute::set_type, 0, -1, IFC4_IfcRelDeclares_type, IFC4_IfcRelDeclares_type->attributes()[0])
    });
    IFC4_IfcContextDependentUnit_type->set_inverse_attributes({
            new inverse_attribute(strings[3187], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4_IfcControl_type->set_inverse_attributes({
            new inverse_attribute(strings[3203], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToControl_type, IFC4_IfcRelAssignsToControl_type->attributes()[0])
    });
    IFC4_IfcConversionBasedUnit_type->set_inverse_attributes({
            new inverse_attribute(strings[3187], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4_IfcCoordinateReferenceSystem_type->set_inverse_attributes({
            new inverse_attribute(strings[3204], inverse_attribute::set_type, 0, 1, IFC4_IfcCoordinateOperation_type, IFC4_IfcCoordinateOperation_type->attributes()[0])
    });
    IFC4_IfcCovering_type->set_inverse_attributes({
            new inverse_attribute(strings[3205], inverse_attribute::set_type, 0, 1, IFC4_IfcRelCoversSpaces_type, IFC4_IfcRelCoversSpaces_type->attributes()[1]),
            new inverse_attribute(strings[3206], inverse_attribute::set_type, 0, 1, IFC4_IfcRelCoversBldgElements_type, IFC4_IfcRelCoversBldgElements_type->attributes()[1])
    });
    IFC4_IfcDistributionControlElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3207], inverse_attribute::set_type, 0, 1, IFC4_IfcRelFlowControlElements_type, IFC4_IfcRelFlowControlElements_type->attributes()[0])
    });
    IFC4_IfcDistributionElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3208], inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsPortToElement_type, IFC4_IfcRelConnectsPortToElement_type->attributes()[1])
    });
    IFC4_IfcDistributionFlowElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3209], inverse_attribute::set_type, 0, 1, IFC4_IfcRelFlowControlElements_type, IFC4_IfcRelFlowControlElements_type->attributes()[1])
    });
    IFC4_IfcDocumentInformation_type->set_inverse_attributes({
            new inverse_attribute(strings[3210], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesDocument_type, IFC4_IfcRelAssociatesDocument_type->attributes()[0]),
            new inverse_attribute(strings[3211], inverse_attribute::set_type, 0, -1, IFC4_IfcDocumentReference_type, IFC4_IfcDocumentReference_type->attributes()[1]),
            new inverse_attribute(strings[3212], inverse_attribute::set_type, 0, -1, IFC4_IfcDocumentInformationRelationship_type, IFC4_IfcDocumentInformationRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3213], inverse_attribute::set_type, 0, 1, IFC4_IfcDocumentInformationRelationship_type, IFC4_IfcDocumentInformationRelationship_type->attributes()[0])
    });
    IFC4_IfcDocumentReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3214], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesDocument_type, IFC4_IfcRelAssociatesDocument_type->attributes()[0])
    });
    IFC4_IfcElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3215], inverse_attribute::set_type, 0, 1, IFC4_IfcRelFillsElement_type, IFC4_IfcRelFillsElement_type->attributes()[1]),
            new inverse_attribute(strings[3216], inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsElements_type, IFC4_IfcRelConnectsElements_type->attributes()[1]),
            new inverse_attribute(strings[3217], inverse_attribute::set_type, 0, -1, IFC4_IfcRelInterferesElements_type, IFC4_IfcRelInterferesElements_type->attributes()[1]),
            new inverse_attribute(strings[3218], inverse_attribute::set_type, 0, -1, IFC4_IfcRelInterferesElements_type, IFC4_IfcRelInterferesElements_type->attributes()[0]),
            new inverse_attribute(strings[3219], inverse_attribute::set_type, 0, -1, IFC4_IfcRelProjectsElement_type, IFC4_IfcRelProjectsElement_type->attributes()[0]),
            new inverse_attribute(strings[3220], inverse_attribute::set_type, 0, -1, IFC4_IfcRelReferencedInSpatialStructure_type, IFC4_IfcRelReferencedInSpatialStructure_type->attributes()[0]),
            new inverse_attribute(strings[3221], inverse_attribute::set_type, 0, -1, IFC4_IfcRelVoidsElement_type, IFC4_IfcRelVoidsElement_type->attributes()[0]),
            new inverse_attribute(strings[3222], inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsWithRealizingElements_type, IFC4_IfcRelConnectsWithRealizingElements_type->attributes()[0]),
            new inverse_attribute(strings[3223], inverse_attribute::set_type, 0, -1, IFC4_IfcRelSpaceBoundary_type, IFC4_IfcRelSpaceBoundary_type->attributes()[1]),
            new inverse_attribute(strings[3224], inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsElements_type, IFC4_IfcRelConnectsElements_type->attributes()[2]),
            new inverse_attribute(strings[3190], inverse_attribute::set_type, 0, 1, IFC4_IfcRelContainedInSpatialStructure_type, IFC4_IfcRelContainedInSpatialStructure_type->attributes()[0]),
            new inverse_attribute(strings[3225], inverse_attribute::set_type, 0, -1, IFC4_IfcRelCoversBldgElements_type, IFC4_IfcRelCoversBldgElements_type->attributes()[0])
    });
    IFC4_IfcExternalReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3226], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[0])
    });
    IFC4_IfcExternalSpatialElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3227], inverse_attribute::set_type, 0, -1, IFC4_IfcRelSpaceBoundary_type, IFC4_IfcRelSpaceBoundary_type->attributes()[0])
    });
    IFC4_IfcFace_type->set_inverse_attributes({
            new inverse_attribute(strings[3228], inverse_attribute::set_type, 0, -1, IFC4_IfcTextureMap_type, IFC4_IfcTextureMap_type->attributes()[1])
    });
    IFC4_IfcFeatureElementAddition_type->set_inverse_attributes({
            new inverse_attribute(strings[3229], inverse_attribute::unspecified_type, -1, -1, IFC4_IfcRelProjectsElement_type, IFC4_IfcRelProjectsElement_type->attributes()[1])
    });
    IFC4_IfcFeatureElementSubtraction_type->set_inverse_attributes({
            new inverse_attribute(strings[3230], inverse_attribute::unspecified_type, -1, -1, IFC4_IfcRelVoidsElement_type, IFC4_IfcRelVoidsElement_type->attributes()[1])
    });
    IFC4_IfcGeometricRepresentationContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3231], inverse_attribute::set_type, 0, -1, IFC4_IfcGeometricRepresentationSubContext_type, IFC4_IfcGeometricRepresentationSubContext_type->attributes()[0]),
            new inverse_attribute(strings[3204], inverse_attribute::set_type, 0, 1, IFC4_IfcCoordinateOperation_type, IFC4_IfcCoordinateOperation_type->attributes()[0])
    });
    IFC4_IfcGrid_type->set_inverse_attributes({
            new inverse_attribute(strings[3190], inverse_attribute::set_type, 0, 1, IFC4_IfcRelContainedInSpatialStructure_type, IFC4_IfcRelContainedInSpatialStructure_type->attributes()[0])
    });
    IFC4_IfcGridAxis_type->set_inverse_attributes({
            new inverse_attribute(strings[3232], inverse_attribute::set_type, 0, 1, IFC4_IfcGrid_type, IFC4_IfcGrid_type->attributes()[2]),
            new inverse_attribute(strings[3233], inverse_attribute::set_type, 0, 1, IFC4_IfcGrid_type, IFC4_IfcGrid_type->attributes()[1]),
            new inverse_attribute(strings[3234], inverse_attribute::set_type, 0, 1, IFC4_IfcGrid_type, IFC4_IfcGrid_type->attributes()[0]),
            new inverse_attribute(strings[3235], inverse_attribute::set_type, 0, -1, IFC4_IfcVirtualGridIntersection_type, IFC4_IfcVirtualGridIntersection_type->attributes()[0])
    });
    IFC4_IfcGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3236], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToGroup_type, IFC4_IfcRelAssignsToGroup_type->attributes()[0])
    });
    IFC4_IfcIndexedPolygonalFace_type->set_inverse_attributes({
            new inverse_attribute(strings[3237], inverse_attribute::set_type, 1, -1, IFC4_IfcPolygonalFaceSet_type, IFC4_IfcPolygonalFaceSet_type->attributes()[1])
    });
    IFC4_IfcLibraryInformation_type->set_inverse_attributes({
            new inverse_attribute(strings[3238], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesLibrary_type, IFC4_IfcRelAssociatesLibrary_type->attributes()[0]),
            new inverse_attribute(strings[3239], inverse_attribute::set_type, 0, -1, IFC4_IfcLibraryReference_type, IFC4_IfcLibraryReference_type->attributes()[2])
    });
    IFC4_IfcLibraryReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3240], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesLibrary_type, IFC4_IfcRelAssociatesLibrary_type->attributes()[0])
    });
    IFC4_IfcMaterial_type->set_inverse_attributes({
            new inverse_attribute(strings[3241], inverse_attribute::set_type, 0, 1, IFC4_IfcMaterialDefinitionRepresentation_type, IFC4_IfcMaterialDefinitionRepresentation_type->attributes()[0]),
            new inverse_attribute(strings[3194], inverse_attribute::set_type, 0, -1, IFC4_IfcMaterialRelationship_type, IFC4_IfcMaterialRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3242], inverse_attribute::set_type, 0, 1, IFC4_IfcMaterialRelationship_type, IFC4_IfcMaterialRelationship_type->attributes()[0])
    });
    IFC4_IfcMaterialConstituent_type->set_inverse_attributes({
            new inverse_attribute(strings[3243], inverse_attribute::unspecified_type, -1, -1, IFC4_IfcMaterialConstituentSet_type, IFC4_IfcMaterialConstituentSet_type->attributes()[2])
    });
    IFC4_IfcMaterialDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3244], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociatesMaterial_type, IFC4_IfcRelAssociatesMaterial_type->attributes()[0]),
            new inverse_attribute(strings[3191], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[2470], inverse_attribute::set_type, 0, -1, IFC4_IfcMaterialProperties_type, IFC4_IfcMaterialProperties_type->attributes()[0])
    });
    IFC4_IfcMaterialLayer_type->set_inverse_attributes({
            new inverse_attribute(strings[3245], inverse_attribute::unspecified_type, -1, -1, IFC4_IfcMaterialLayerSet_type, IFC4_IfcMaterialLayerSet_type->attributes()[0])
    });
    IFC4_IfcMaterialProfile_type->set_inverse_attributes({
            new inverse_attribute(strings[3246], inverse_attribute::unspecified_type, -1, -1, IFC4_IfcMaterialProfileSet_type, IFC4_IfcMaterialProfileSet_type->attributes()[2])
    });
    IFC4_IfcMaterialUsageDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3244], inverse_attribute::set_type, 1, -1, IFC4_IfcRelAssociatesMaterial_type, IFC4_IfcRelAssociatesMaterial_type->attributes()[0])
    });
    IFC4_IfcObject_type->set_inverse_attributes({
            new inverse_attribute(strings[3247], inverse_attribute::set_type, 0, 1, IFC4_IfcRelDefinesByObject_type, IFC4_IfcRelDefinesByObject_type->attributes()[0]),
            new inverse_attribute(strings[3202], inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByObject_type, IFC4_IfcRelDefinesByObject_type->attributes()[1]),
            new inverse_attribute(strings[3248], inverse_attribute::set_type, 0, 1, IFC4_IfcRelDefinesByType_type, IFC4_IfcRelDefinesByType_type->attributes()[0]),
            new inverse_attribute(strings[3201], inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByProperties_type, IFC4_IfcRelDefinesByProperties_type->attributes()[0])
    });
    IFC4_IfcObjectDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3249], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssigns_type, IFC4_IfcRelAssigns_type->attributes()[0]),
            new inverse_attribute(strings[3250], inverse_attribute::set_type, 0, 1, IFC4_IfcRelNests_type, IFC4_IfcRelNests_type->attributes()[1]),
            new inverse_attribute(strings[3251], inverse_attribute::set_type, 0, -1, IFC4_IfcRelNests_type, IFC4_IfcRelNests_type->attributes()[0]),
            new inverse_attribute(strings[3252], inverse_attribute::set_type, 0, 1, IFC4_IfcRelDeclares_type, IFC4_IfcRelDeclares_type->attributes()[1]),
            new inverse_attribute(strings[3253], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAggregates_type, IFC4_IfcRelAggregates_type->attributes()[0]),
            new inverse_attribute(strings[3254], inverse_attribute::set_type, 0, 1, IFC4_IfcRelAggregates_type, IFC4_IfcRelAggregates_type->attributes()[1]),
            new inverse_attribute(strings[3255], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociates_type, IFC4_IfcRelAssociates_type->attributes()[0])
    });
    IFC4_IfcObjectPlacement_type->set_inverse_attributes({
            new inverse_attribute(strings[3256], inverse_attribute::set_type, 0, -1, IFC4_IfcProduct_type, IFC4_IfcProduct_type->attributes()[0]),
            new inverse_attribute(strings[3257], inverse_attribute::set_type, 0, -1, IFC4_IfcLocalPlacement_type, IFC4_IfcLocalPlacement_type->attributes()[0])
    });
    IFC4_IfcOpeningElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3258], inverse_attribute::set_type, 0, -1, IFC4_IfcRelFillsElement_type, IFC4_IfcRelFillsElement_type->attributes()[0])
    });
    IFC4_IfcOrganization_type->set_inverse_attributes({
            new inverse_attribute(strings[3259], inverse_attribute::set_type, 0, -1, IFC4_IfcOrganizationRelationship_type, IFC4_IfcOrganizationRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3195], inverse_attribute::set_type, 0, -1, IFC4_IfcOrganizationRelationship_type, IFC4_IfcOrganizationRelationship_type->attributes()[0]),
            new inverse_attribute(strings[3260], inverse_attribute::set_type, 0, -1, IFC4_IfcPersonAndOrganization_type, IFC4_IfcPersonAndOrganization_type->attributes()[1])
    });
    IFC4_IfcPerson_type->set_inverse_attributes({
            new inverse_attribute(strings[3261], inverse_attribute::set_type, 0, -1, IFC4_IfcPersonAndOrganization_type, IFC4_IfcPersonAndOrganization_type->attributes()[0])
    });
    IFC4_IfcPhysicalQuantity_type->set_inverse_attributes({
            new inverse_attribute(strings[3191], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3262], inverse_attribute::set_type, 0, 1, IFC4_IfcPhysicalComplexQuantity_type, IFC4_IfcPhysicalComplexQuantity_type->attributes()[0])
    });
    IFC4_IfcPort_type->set_inverse_attributes({
            new inverse_attribute(strings[3263], inverse_attribute::set_type, 0, 1, IFC4_IfcRelConnectsPortToElement_type, IFC4_IfcRelConnectsPortToElement_type->attributes()[0]),
            new inverse_attribute(strings[3224], inverse_attribute::set_type, 0, 1, IFC4_IfcRelConnectsPorts_type, IFC4_IfcRelConnectsPorts_type->attributes()[1]),
            new inverse_attribute(strings[3216], inverse_attribute::set_type, 0, 1, IFC4_IfcRelConnectsPorts_type, IFC4_IfcRelConnectsPorts_type->attributes()[0])
    });
    IFC4_IfcProcess_type->set_inverse_attributes({
            new inverse_attribute(strings[3264], inverse_attribute::set_type, 0, -1, IFC4_IfcRelSequence_type, IFC4_IfcRelSequence_type->attributes()[0]),
            new inverse_attribute(strings[3265], inverse_attribute::set_type, 0, -1, IFC4_IfcRelSequence_type, IFC4_IfcRelSequence_type->attributes()[1]),
            new inverse_attribute(strings[3266], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToProcess_type, IFC4_IfcRelAssignsToProcess_type->attributes()[0])
    });
    IFC4_IfcProduct_type->set_inverse_attributes({
            new inverse_attribute(strings[3267], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToProduct_type, IFC4_IfcRelAssignsToProduct_type->attributes()[0])
    });
    IFC4_IfcProductDefinitionShape_type->set_inverse_attributes({
            new inverse_attribute(strings[3268], inverse_attribute::set_type, 1, -1, IFC4_IfcProduct_type, IFC4_IfcProduct_type->attributes()[1]),
            new inverse_attribute(strings[3269], inverse_attribute::set_type, 0, -1, IFC4_IfcShapeAspect_type, IFC4_IfcShapeAspect_type->attributes()[4])
    });
    IFC4_IfcProfileDef_type->set_inverse_attributes({
            new inverse_attribute(strings[3187], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[2470], inverse_attribute::set_type, 0, -1, IFC4_IfcProfileProperties_type, IFC4_IfcProfileProperties_type->attributes()[0])
    });
    IFC4_IfcProperty_type->set_inverse_attributes({
            new inverse_attribute(strings[3270], inverse_attribute::set_type, 0, -1, IFC4_IfcPropertySet_type, IFC4_IfcPropertySet_type->attributes()[0]),
            new inverse_attribute(strings[3271], inverse_attribute::set_type, 0, -1, IFC4_IfcPropertyDependencyRelationship_type, IFC4_IfcPropertyDependencyRelationship_type->attributes()[0]),
            new inverse_attribute(strings[3272], inverse_attribute::set_type, 0, -1, IFC4_IfcPropertyDependencyRelationship_type, IFC4_IfcPropertyDependencyRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3262], inverse_attribute::set_type, 0, -1, IFC4_IfcComplexProperty_type, IFC4_IfcComplexProperty_type->attributes()[1]),
            new inverse_attribute(strings[3273], inverse_attribute::set_type, 0, -1, IFC4_IfcResourceConstraintRelationship_type, IFC4_IfcResourceConstraintRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3274], inverse_attribute::set_type, 0, -1, IFC4_IfcResourceApprovalRelationship_type, IFC4_IfcResourceApprovalRelationship_type->attributes()[0])
    });
    IFC4_IfcPropertyAbstraction_type->set_inverse_attributes({
            new inverse_attribute(strings[3191], inverse_attribute::set_type, 0, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4_IfcPropertyDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3252], inverse_attribute::set_type, 0, 1, IFC4_IfcRelDeclares_type, IFC4_IfcRelDeclares_type->attributes()[1]),
            new inverse_attribute(strings[3255], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssociates_type, IFC4_IfcRelAssociates_type->attributes()[0])
    });
    IFC4_IfcPropertySetDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3275], inverse_attribute::set_type, 0, -1, IFC4_IfcTypeObject_type, IFC4_IfcTypeObject_type->attributes()[1]),
            new inverse_attribute(strings[3201], inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByTemplate_type, IFC4_IfcRelDefinesByTemplate_type->attributes()[0]),
            new inverse_attribute(strings[3276], inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByProperties_type, IFC4_IfcRelDefinesByProperties_type->attributes()[1])
    });
    IFC4_IfcPropertySetTemplate_type->set_inverse_attributes({
            new inverse_attribute(strings[3277], inverse_attribute::set_type, 0, -1, IFC4_IfcRelDefinesByTemplate_type, IFC4_IfcRelDefinesByTemplate_type->attributes()[1])
    });
    IFC4_IfcPropertyTemplate_type->set_inverse_attributes({
            new inverse_attribute(strings[3278], inverse_attribute::set_type, 0, -1, IFC4_IfcComplexPropertyTemplate_type, IFC4_IfcComplexPropertyTemplate_type->attributes()[2]),
            new inverse_attribute(strings[3279], inverse_attribute::set_type, 0, -1, IFC4_IfcPropertySetTemplate_type, IFC4_IfcPropertySetTemplate_type->attributes()[2])
    });
    IFC4_IfcRelSpaceBoundary1stLevel_type->set_inverse_attributes({
            new inverse_attribute(strings[2343], inverse_attribute::set_type, 0, -1, IFC4_IfcRelSpaceBoundary1stLevel_type, IFC4_IfcRelSpaceBoundary1stLevel_type->attributes()[0])
    });
    IFC4_IfcRelSpaceBoundary2ndLevel_type->set_inverse_attributes({
            new inverse_attribute(strings[3280], inverse_attribute::set_type, 0, 1, IFC4_IfcRelSpaceBoundary2ndLevel_type, IFC4_IfcRelSpaceBoundary2ndLevel_type->attributes()[0])
    });
    IFC4_IfcRepresentation_type->set_inverse_attributes({
            new inverse_attribute(strings[3281], inverse_attribute::set_type, 0, 1, IFC4_IfcRepresentationMap_type, IFC4_IfcRepresentationMap_type->attributes()[1]),
            new inverse_attribute(strings[3282], inverse_attribute::set_type, 0, -1, IFC4_IfcPresentationLayerAssignment_type, IFC4_IfcPresentationLayerAssignment_type->attributes()[2]),
            new inverse_attribute(strings[3283], inverse_attribute::set_type, 0, -1, IFC4_IfcProductRepresentation_type, IFC4_IfcProductRepresentation_type->attributes()[2])
    });
    IFC4_IfcRepresentationContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3284], inverse_attribute::set_type, 0, -1, IFC4_IfcRepresentation_type, IFC4_IfcRepresentation_type->attributes()[0])
    });
    IFC4_IfcRepresentationItem_type->set_inverse_attributes({
            new inverse_attribute(strings[3285], inverse_attribute::set_type, 0, 1, IFC4_IfcPresentationLayerAssignment_type, IFC4_IfcPresentationLayerAssignment_type->attributes()[2]),
            new inverse_attribute(strings[3286], inverse_attribute::set_type, 0, 1, IFC4_IfcStyledItem_type, IFC4_IfcStyledItem_type->attributes()[0])
    });
    IFC4_IfcRepresentationMap_type->set_inverse_attributes({
            new inverse_attribute(strings[3269], inverse_attribute::set_type, 0, -1, IFC4_IfcShapeAspect_type, IFC4_IfcShapeAspect_type->attributes()[4]),
            new inverse_attribute(strings[3287], inverse_attribute::set_type, 0, -1, IFC4_IfcMappedItem_type, IFC4_IfcMappedItem_type->attributes()[0])
    });
    IFC4_IfcResource_type->set_inverse_attributes({
            new inverse_attribute(strings[3288], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToResource_type, IFC4_IfcRelAssignsToResource_type->attributes()[0])
    });
    IFC4_IfcShapeModel_type->set_inverse_attributes({
            new inverse_attribute(strings[3289], inverse_attribute::set_type, 0, 1, IFC4_IfcShapeAspect_type, IFC4_IfcShapeAspect_type->attributes()[0])
    });
    IFC4_IfcSpace_type->set_inverse_attributes({
            new inverse_attribute(strings[3225], inverse_attribute::set_type, 0, -1, IFC4_IfcRelCoversSpaces_type, IFC4_IfcRelCoversSpaces_type->attributes()[0]),
            new inverse_attribute(strings[3227], inverse_attribute::set_type, 0, -1, IFC4_IfcRelSpaceBoundary_type, IFC4_IfcRelSpaceBoundary_type->attributes()[0])
    });
    IFC4_IfcSpatialElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3290], inverse_attribute::set_type, 0, -1, IFC4_IfcRelContainedInSpatialStructure_type, IFC4_IfcRelContainedInSpatialStructure_type->attributes()[1]),
            new inverse_attribute(strings[3291], inverse_attribute::set_type, 0, -1, IFC4_IfcRelServicesBuildings_type, IFC4_IfcRelServicesBuildings_type->attributes()[1]),
            new inverse_attribute(strings[3292], inverse_attribute::set_type, 0, -1, IFC4_IfcRelReferencedInSpatialStructure_type, IFC4_IfcRelReferencedInSpatialStructure_type->attributes()[1])
    });
    IFC4_IfcStructuralActivity_type->set_inverse_attributes({
            new inverse_attribute(strings[3293], inverse_attribute::set_type, 0, 1, IFC4_IfcRelConnectsStructuralActivity_type, IFC4_IfcRelConnectsStructuralActivity_type->attributes()[1])
    });
    IFC4_IfcStructuralConnection_type->set_inverse_attributes({
            new inverse_attribute(strings[3294], inverse_attribute::set_type, 1, -1, IFC4_IfcRelConnectsStructuralMember_type, IFC4_IfcRelConnectsStructuralMember_type->attributes()[1])
    });
    IFC4_IfcStructuralItem_type->set_inverse_attributes({
            new inverse_attribute(strings[3295], inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsStructuralActivity_type, IFC4_IfcRelConnectsStructuralActivity_type->attributes()[0])
    });
    IFC4_IfcStructuralLoadGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3296], inverse_attribute::set_type, 0, 1, IFC4_IfcStructuralResultGroup_type, IFC4_IfcStructuralResultGroup_type->attributes()[1]),
            new inverse_attribute(strings[3297], inverse_attribute::set_type, 0, -1, IFC4_IfcStructuralAnalysisModel_type, IFC4_IfcStructuralAnalysisModel_type->attributes()[2])
    });
    IFC4_IfcStructuralMember_type->set_inverse_attributes({
            new inverse_attribute(strings[3298], inverse_attribute::set_type, 0, -1, IFC4_IfcRelConnectsStructuralMember_type, IFC4_IfcRelConnectsStructuralMember_type->attributes()[0])
    });
    IFC4_IfcStructuralResultGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3299], inverse_attribute::set_type, 0, 1, IFC4_IfcStructuralAnalysisModel_type, IFC4_IfcStructuralAnalysisModel_type->attributes()[3])
    });
    IFC4_IfcSurfaceTexture_type->set_inverse_attributes({
            new inverse_attribute(strings[3300], inverse_attribute::set_type, 0, -1, IFC4_IfcTextureCoordinate_type, IFC4_IfcTextureCoordinate_type->attributes()[0]),
            new inverse_attribute(strings[3301], inverse_attribute::set_type, 0, -1, IFC4_IfcSurfaceStyleWithTextures_type, IFC4_IfcSurfaceStyleWithTextures_type->attributes()[0])
    });
    IFC4_IfcSystem_type->set_inverse_attributes({
            new inverse_attribute(strings[3302], inverse_attribute::set_type, 0, 1, IFC4_IfcRelServicesBuildings_type, IFC4_IfcRelServicesBuildings_type->attributes()[0])
    });
    IFC4_IfcTessellatedFaceSet_type->set_inverse_attributes({
            new inverse_attribute(strings[3303], inverse_attribute::set_type, 0, 1, IFC4_IfcIndexedColourMap_type, IFC4_IfcIndexedColourMap_type->attributes()[0]),
            new inverse_attribute(strings[3304], inverse_attribute::set_type, 0, -1, IFC4_IfcIndexedTextureMap_type, IFC4_IfcIndexedTextureMap_type->attributes()[0])
    });
    IFC4_IfcTimeSeries_type->set_inverse_attributes({
            new inverse_attribute(strings[3187], inverse_attribute::set_type, 1, -1, IFC4_IfcExternalReferenceRelationship_type, IFC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4_IfcTypeObject_type->set_inverse_attributes({
            new inverse_attribute(strings[3305], inverse_attribute::set_type, 0, 1, IFC4_IfcRelDefinesByType_type, IFC4_IfcRelDefinesByType_type->attributes()[1])
    });
    IFC4_IfcTypeProcess_type->set_inverse_attributes({
            new inverse_attribute(strings[3266], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToProcess_type, IFC4_IfcRelAssignsToProcess_type->attributes()[0])
    });
    IFC4_IfcTypeProduct_type->set_inverse_attributes({
            new inverse_attribute(strings[3267], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToProduct_type, IFC4_IfcRelAssignsToProduct_type->attributes()[0])
    });
    IFC4_IfcTypeResource_type->set_inverse_attributes({
            new inverse_attribute(strings[3288], inverse_attribute::set_type, 0, -1, IFC4_IfcRelAssignsToResource_type, IFC4_IfcRelAssignsToResource_type->attributes()[0])
    });
    IFC4_IfcControl_type->set_subtypes({
        IFC4_IfcActionRequest_type,IFC4_IfcCostItem_type,IFC4_IfcCostSchedule_type,IFC4_IfcPerformanceHistory_type,IFC4_IfcPermit_type,IFC4_IfcProjectOrder_type,IFC4_IfcWorkCalendar_type,IFC4_IfcWorkControl_type
    });
    IFC4_IfcObject_type->set_subtypes({
        IFC4_IfcActor_type,IFC4_IfcControl_type,IFC4_IfcGroup_type,IFC4_IfcProcess_type,IFC4_IfcProduct_type,IFC4_IfcResource_type
    });
    IFC4_IfcDistributionControlElement_type->set_subtypes({
        IFC4_IfcActuator_type,IFC4_IfcAlarm_type,IFC4_IfcController_type,IFC4_IfcFlowInstrument_type,IFC4_IfcProtectiveDeviceTrippingUnit_type,IFC4_IfcSensor_type,IFC4_IfcUnitaryControlElement_type
    });
    IFC4_IfcDistributionControlElementType_type->set_subtypes({
        IFC4_IfcActuatorType_type,IFC4_IfcAlarmType_type,IFC4_IfcControllerType_type,IFC4_IfcFlowInstrumentType_type,IFC4_IfcProtectiveDeviceTrippingUnitType_type,IFC4_IfcSensorType_type,IFC4_IfcUnitaryControlElementType_type
    });
    IFC4_IfcManifoldSolidBrep_type->set_subtypes({
        IFC4_IfcAdvancedBrep_type,IFC4_IfcFacetedBrep_type
    });
    IFC4_IfcAdvancedBrep_type->set_subtypes({
        IFC4_IfcAdvancedBrepWithVoids_type
    });
    IFC4_IfcFaceSurface_type->set_subtypes({
        IFC4_IfcAdvancedFace_type
    });
    IFC4_IfcFlowTerminal_type->set_subtypes({
        IFC4_IfcAirTerminal_type,IFC4_IfcAudioVisualAppliance_type,IFC4_IfcCommunicationsAppliance_type,IFC4_IfcElectricAppliance_type,IFC4_IfcFireSuppressionTerminal_type,IFC4_IfcLamp_type,IFC4_IfcLightFixture_type,IFC4_IfcMedicalDevice_type,IFC4_IfcOutlet_type,IFC4_IfcSanitaryTerminal_type,IFC4_IfcSpaceHeater_type,IFC4_IfcStackTerminal_type,IFC4_IfcWasteTerminal_type
    });
    IFC4_IfcFlowController_type->set_subtypes({
        IFC4_IfcAirTerminalBox_type,IFC4_IfcDamper_type,IFC4_IfcElectricDistributionBoard_type,IFC4_IfcElectricTimeControl_type,IFC4_IfcFlowMeter_type,IFC4_IfcProtectiveDevice_type,IFC4_IfcSwitchingDevice_type,IFC4_IfcValve_type
    });
    IFC4_IfcFlowControllerType_type->set_subtypes({
        IFC4_IfcAirTerminalBoxType_type,IFC4_IfcDamperType_type,IFC4_IfcElectricDistributionBoardType_type,IFC4_IfcElectricTimeControlType_type,IFC4_IfcFlowMeterType_type,IFC4_IfcProtectiveDeviceType_type,IFC4_IfcSwitchingDeviceType_type,IFC4_IfcValveType_type
    });
    IFC4_IfcFlowTerminalType_type->set_subtypes({
        IFC4_IfcAirTerminalType_type,IFC4_IfcAudioVisualApplianceType_type,IFC4_IfcCommunicationsApplianceType_type,IFC4_IfcElectricApplianceType_type,IFC4_IfcFireSuppressionTerminalType_type,IFC4_IfcLampType_type,IFC4_IfcLightFixtureType_type,IFC4_IfcMedicalDeviceType_type,IFC4_IfcOutletType_type,IFC4_IfcSanitaryTerminalType_type,IFC4_IfcSpaceHeaterType_type,IFC4_IfcStackTerminalType_type,IFC4_IfcWasteTerminalType_type
    });
    IFC4_IfcEnergyConversionDevice_type->set_subtypes({
        IFC4_IfcAirToAirHeatRecovery_type,IFC4_IfcBoiler_type,IFC4_IfcBurner_type,IFC4_IfcChiller_type,IFC4_IfcCoil_type,IFC4_IfcCondenser_type,IFC4_IfcCooledBeam_type,IFC4_IfcCoolingTower_type,IFC4_IfcElectricGenerator_type,IFC4_IfcElectricMotor_type,IFC4_IfcEngine_type,IFC4_IfcEvaporativeCooler_type,IFC4_IfcEvaporator_type,IFC4_IfcHeatExchanger_type,IFC4_IfcHumidifier_type,IFC4_IfcMotorConnection_type,IFC4_IfcSolarDevice_type,IFC4_IfcTransformer_type,IFC4_IfcTubeBundle_type,IFC4_IfcUnitaryEquipment_type
    });
    IFC4_IfcEnergyConversionDeviceType_type->set_subtypes({
        IFC4_IfcAirToAirHeatRecoveryType_type,IFC4_IfcBoilerType_type,IFC4_IfcBurnerType_type,IFC4_IfcChillerType_type,IFC4_IfcCoilType_type,IFC4_IfcCondenserType_type,IFC4_IfcCooledBeamType_type,IFC4_IfcCoolingTowerType_type,IFC4_IfcElectricGeneratorType_type,IFC4_IfcElectricMotorType_type,IFC4_IfcEngineType_type,IFC4_IfcEvaporativeCoolerType_type,IFC4_IfcEvaporatorType_type,IFC4_IfcHeatExchangerType_type,IFC4_IfcHumidifierType_type,IFC4_IfcMotorConnectionType_type,IFC4_IfcSolarDeviceType_type,IFC4_IfcTransformerType_type,IFC4_IfcTubeBundleType_type,IFC4_IfcUnitaryEquipmentType_type
    });
    IFC4_IfcProduct_type->set_subtypes({
        IFC4_IfcAnnotation_type,IFC4_IfcElement_type,IFC4_IfcGrid_type,IFC4_IfcPort_type,IFC4_IfcProxy_type,IFC4_IfcSpatialElement_type,IFC4_IfcStructuralActivity_type,IFC4_IfcStructuralItem_type
    });
    IFC4_IfcGeometricRepresentationItem_type->set_subtypes({
        IFC4_IfcAnnotationFillArea_type,IFC4_IfcBooleanResult_type,IFC4_IfcBoundingBox_type,IFC4_IfcCartesianPointList_type,IFC4_IfcCartesianTransformationOperator_type,IFC4_IfcCompositeCurveSegment_type,IFC4_IfcCsgPrimitive3D_type,IFC4_IfcCurve_type,IFC4_IfcDirection_type,IFC4_IfcFaceBasedSurfaceModel_type,IFC4_IfcFillAreaStyleHatching_type,IFC4_IfcFillAreaStyleTiles_type,IFC4_IfcGeometricSet_type,IFC4_IfcHalfSpaceSolid_type,IFC4_IfcLightSource_type,IFC4_IfcPlacement_type,IFC4_IfcPlanarExtent_type,IFC4_IfcPoint_type,IFC4_IfcSectionedSpine_type,IFC4_IfcShellBasedSurfaceModel_type,IFC4_IfcSolidModel_type,IFC4_IfcSurface_type,IFC4_IfcTessellatedItem_type,IFC4_IfcTextLiteral_type,IFC4_IfcVector_type
    });
    IFC4_IfcResourceLevelRelationship_type->set_subtypes({
        IFC4_IfcApprovalRelationship_type,IFC4_IfcCurrencyRelationship_type,IFC4_IfcDocumentInformationRelationship_type,IFC4_IfcExternalReferenceRelationship_type,IFC4_IfcMaterialRelationship_type,IFC4_IfcOrganizationRelationship_type,IFC4_IfcPropertyDependencyRelationship_type,IFC4_IfcResourceApprovalRelationship_type,IFC4_IfcResourceConstraintRelationship_type
    });
    IFC4_IfcProfileDef_type->set_subtypes({
        IFC4_IfcArbitraryClosedProfileDef_type,IFC4_IfcArbitraryOpenProfileDef_type,IFC4_IfcCompositeProfileDef_type,IFC4_IfcDerivedProfileDef_type,IFC4_IfcParameterizedProfileDef_type
    });
    IFC4_IfcArbitraryClosedProfileDef_type->set_subtypes({
        IFC4_IfcArbitraryProfileDefWithVoids_type
    });
    IFC4_IfcGroup_type->set_subtypes({
        IFC4_IfcAsset_type,IFC4_IfcInventory_type,IFC4_IfcStructuralLoadGroup_type,IFC4_IfcStructuralResultGroup_type,IFC4_IfcSystem_type
    });
    IFC4_IfcParameterizedProfileDef_type->set_subtypes({
        IFC4_IfcAsymmetricIShapeProfileDef_type,IFC4_IfcCShapeProfileDef_type,IFC4_IfcCircleProfileDef_type,IFC4_IfcEllipseProfileDef_type,IFC4_IfcIShapeProfileDef_type,IFC4_IfcLShapeProfileDef_type,IFC4_IfcRectangleProfileDef_type,IFC4_IfcTShapeProfileDef_type,IFC4_IfcTrapeziumProfileDef_type,IFC4_IfcUShapeProfileDef_type,IFC4_IfcZShapeProfileDef_type
    });
    IFC4_IfcPlacement_type->set_subtypes({
        IFC4_IfcAxis1Placement_type,IFC4_IfcAxis2Placement2D_type,IFC4_IfcAxis2Placement3D_type
    });
    IFC4_IfcBoundedCurve_type->set_subtypes({
        IFC4_IfcBSplineCurve_type,IFC4_IfcCompositeCurve_type,IFC4_IfcIndexedPolyCurve_type,IFC4_IfcPolyline_type,IFC4_IfcTrimmedCurve_type
    });
    IFC4_IfcBSplineCurve_type->set_subtypes({
        IFC4_IfcBSplineCurveWithKnots_type
    });
    IFC4_IfcBoundedSurface_type->set_subtypes({
        IFC4_IfcBSplineSurface_type,IFC4_IfcCurveBoundedPlane_type,IFC4_IfcCurveBoundedSurface_type,IFC4_IfcRectangularTrimmedSurface_type
    });
    IFC4_IfcBSplineSurface_type->set_subtypes({
        IFC4_IfcBSplineSurfaceWithKnots_type
    });
    IFC4_IfcBuildingElement_type->set_subtypes({
        IFC4_IfcBeam_type,IFC4_IfcBuildingElementProxy_type,IFC4_IfcChimney_type,IFC4_IfcColumn_type,IFC4_IfcCovering_type,IFC4_IfcCurtainWall_type,IFC4_IfcDoor_type,IFC4_IfcFooting_type,IFC4_IfcMember_type,IFC4_IfcPile_type,IFC4_IfcPlate_type,IFC4_IfcRailing_type,IFC4_IfcRamp_type,IFC4_IfcRampFlight_type,IFC4_IfcRoof_type,IFC4_IfcShadingDevice_type,IFC4_IfcSlab_type,IFC4_IfcStair_type,IFC4_IfcStairFlight_type,IFC4_IfcWall_type,IFC4_IfcWindow_type
    });
    IFC4_IfcBeam_type->set_subtypes({
        IFC4_IfcBeamStandardCase_type
    });
    IFC4_IfcBuildingElementType_type->set_subtypes({
        IFC4_IfcBeamType_type,IFC4_IfcBuildingElementProxyType_type,IFC4_IfcChimneyType_type,IFC4_IfcColumnType_type,IFC4_IfcCoveringType_type,IFC4_IfcCurtainWallType_type,IFC4_IfcDoorType_type,IFC4_IfcFootingType_type,IFC4_IfcMemberType_type,IFC4_IfcPileType_type,IFC4_IfcPlateType_type,IFC4_IfcRailingType_type,IFC4_IfcRampFlightType_type,IFC4_IfcRampType_type,IFC4_IfcRoofType_type,IFC4_IfcShadingDeviceType_type,IFC4_IfcSlabType_type,IFC4_IfcStairFlightType_type,IFC4_IfcStairType_type,IFC4_IfcWallType_type,IFC4_IfcWindowType_type
    });
    IFC4_IfcSurfaceTexture_type->set_subtypes({
        IFC4_IfcBlobTexture_type,IFC4_IfcImageTexture_type,IFC4_IfcPixelTexture_type
    });
    IFC4_IfcCsgPrimitive3D_type->set_subtypes({
        IFC4_IfcBlock_type,IFC4_IfcRectangularPyramid_type,IFC4_IfcRightCircularCone_type,IFC4_IfcRightCircularCylinder_type,IFC4_IfcSphere_type
    });
    IFC4_IfcBooleanResult_type->set_subtypes({
        IFC4_IfcBooleanClippingResult_type
    });
    IFC4_IfcCompositeCurveOnSurface_type->set_subtypes({
        IFC4_IfcBoundaryCurve_type
    });
    IFC4_IfcBoundaryCondition_type->set_subtypes({
        IFC4_IfcBoundaryEdgeCondition_type,IFC4_IfcBoundaryFaceCondition_type,IFC4_IfcBoundaryNodeCondition_type
    });
    IFC4_IfcBoundaryNodeCondition_type->set_subtypes({
        IFC4_IfcBoundaryNodeConditionWarping_type
    });
    IFC4_IfcCurve_type->set_subtypes({
        IFC4_IfcBoundedCurve_type,IFC4_IfcConic_type,IFC4_IfcLine_type,IFC4_IfcOffsetCurve2D_type,IFC4_IfcOffsetCurve3D_type,IFC4_IfcPcurve_type,IFC4_IfcSurfaceCurve_type
    });
    IFC4_IfcSurface_type->set_subtypes({
        IFC4_IfcBoundedSurface_type,IFC4_IfcElementarySurface_type,IFC4_IfcSweptSurface_type
    });
    IFC4_IfcHalfSpaceSolid_type->set_subtypes({
        IFC4_IfcBoxedHalfSpace_type,IFC4_IfcPolygonalBoundedHalfSpace_type
    });
    IFC4_IfcSpatialStructureElement_type->set_subtypes({
        IFC4_IfcBuilding_type,IFC4_IfcBuildingStorey_type,IFC4_IfcSite_type,IFC4_IfcSpace_type
    });
    IFC4_IfcElement_type->set_subtypes({
        IFC4_IfcBuildingElement_type,IFC4_IfcCivilElement_type,IFC4_IfcDistributionElement_type,IFC4_IfcElementAssembly_type,IFC4_IfcElementComponent_type,IFC4_IfcFeatureElement_type,IFC4_IfcFurnishingElement_type,IFC4_IfcGeographicElement_type,IFC4_IfcTransportElement_type,IFC4_IfcVirtualElement_type
    });
    IFC4_IfcElementComponent_type->set_subtypes({
        IFC4_IfcBuildingElementPart_type,IFC4_IfcDiscreteAccessory_type,IFC4_IfcFastener_type,IFC4_IfcMechanicalFastener_type,IFC4_IfcReinforcingElement_type,IFC4_IfcVibrationIsolator_type
    });
    IFC4_IfcElementComponentType_type->set_subtypes({
        IFC4_IfcBuildingElementPartType_type,IFC4_IfcDiscreteAccessoryType_type,IFC4_IfcFastenerType_type,IFC4_IfcMechanicalFastenerType_type,IFC4_IfcReinforcingElementType_type,IFC4_IfcVibrationIsolatorType_type
    });
    IFC4_IfcElementType_type->set_subtypes({
        IFC4_IfcBuildingElementType_type,IFC4_IfcCivilElementType_type,IFC4_IfcDistributionElementType_type,IFC4_IfcElementAssemblyType_type,IFC4_IfcElementComponentType_type,IFC4_IfcFurnishingElementType_type,IFC4_IfcGeographicElementType_type,IFC4_IfcTransportElementType_type
    });
    IFC4_IfcSystem_type->set_subtypes({
        IFC4_IfcBuildingSystem_type,IFC4_IfcDistributionSystem_type,IFC4_IfcStructuralAnalysisModel_type,IFC4_IfcZone_type
    });
    IFC4_IfcFlowFitting_type->set_subtypes({
        IFC4_IfcCableCarrierFitting_type,IFC4_IfcCableFitting_type,IFC4_IfcDuctFitting_type,IFC4_IfcJunctionBox_type,IFC4_IfcPipeFitting_type
    });
    IFC4_IfcFlowFittingType_type->set_subtypes({
        IFC4_IfcCableCarrierFittingType_type,IFC4_IfcCableFittingType_type,IFC4_IfcDuctFittingType_type,IFC4_IfcJunctionBoxType_type,IFC4_IfcPipeFittingType_type
    });
    IFC4_IfcFlowSegment_type->set_subtypes({
        IFC4_IfcCableCarrierSegment_type,IFC4_IfcCableSegment_type,IFC4_IfcDuctSegment_type,IFC4_IfcPipeSegment_type
    });
    IFC4_IfcFlowSegmentType_type->set_subtypes({
        IFC4_IfcCableCarrierSegmentType_type,IFC4_IfcCableSegmentType_type,IFC4_IfcDuctSegmentType_type,IFC4_IfcPipeSegmentType_type
    });
    IFC4_IfcPoint_type->set_subtypes({
        IFC4_IfcCartesianPoint_type,IFC4_IfcPointOnCurve_type,IFC4_IfcPointOnSurface_type
    });
    IFC4_IfcCartesianPointList_type->set_subtypes({
        IFC4_IfcCartesianPointList2D_type,IFC4_IfcCartesianPointList3D_type
    });
    IFC4_IfcCartesianTransformationOperator_type->set_subtypes({
        IFC4_IfcCartesianTransformationOperator2D_type,IFC4_IfcCartesianTransformationOperator3D_type
    });
    IFC4_IfcCartesianTransformationOperator2D_type->set_subtypes({
        IFC4_IfcCartesianTransformationOperator2DnonUniform_type
    });
    IFC4_IfcCartesianTransformationOperator3D_type->set_subtypes({
        IFC4_IfcCartesianTransformationOperator3DnonUniform_type
    });
    IFC4_IfcArbitraryOpenProfileDef_type->set_subtypes({
        IFC4_IfcCenterLineProfileDef_type
    });
    IFC4_IfcConic_type->set_subtypes({
        IFC4_IfcCircle_type,IFC4_IfcEllipse_type
    });
    IFC4_IfcCircleProfileDef_type->set_subtypes({
        IFC4_IfcCircleHollowProfileDef_type
    });
    IFC4_IfcExternalInformation_type->set_subtypes({
        IFC4_IfcClassification_type,IFC4_IfcDocumentInformation_type,IFC4_IfcLibraryInformation_type
    });
    IFC4_IfcExternalReference_type->set_subtypes({
        IFC4_IfcClassificationReference_type,IFC4_IfcDocumentReference_type,IFC4_IfcExternallyDefinedHatchStyle_type,IFC4_IfcExternallyDefinedSurfaceStyle_type,IFC4_IfcExternallyDefinedTextFont_type,IFC4_IfcLibraryReference_type
    });
    IFC4_IfcConnectedFaceSet_type->set_subtypes({
        IFC4_IfcClosedShell_type,IFC4_IfcOpenShell_type
    });
    IFC4_IfcColourSpecification_type->set_subtypes({
        IFC4_IfcColourRgb_type
    });
    IFC4_IfcPresentationItem_type->set_subtypes({
        IFC4_IfcColourRgbList_type,IFC4_IfcColourSpecification_type,IFC4_IfcCurveStyleFont_type,IFC4_IfcCurveStyleFontAndScaling_type,IFC4_IfcCurveStyleFontPattern_type,IFC4_IfcIndexedColourMap_type,IFC4_IfcPreDefinedItem_type,IFC4_IfcSurfaceStyleLighting_type,IFC4_IfcSurfaceStyleRefraction_type,IFC4_IfcSurfaceStyleShading_type,IFC4_IfcSurfaceStyleWithTextures_type,IFC4_IfcSurfaceTexture_type,IFC4_IfcTextStyleForDefinedFont_type,IFC4_IfcTextStyleTextModel_type,IFC4_IfcTextureCoordinate_type,IFC4_IfcTextureVertex_type,IFC4_IfcTextureVertexList_type
    });
    IFC4_IfcColumn_type->set_subtypes({
        IFC4_IfcColumnStandardCase_type
    });
    IFC4_IfcProperty_type->set_subtypes({
        IFC4_IfcComplexProperty_type,IFC4_IfcSimpleProperty_type
    });
    IFC4_IfcPropertyTemplate_type->set_subtypes({
        IFC4_IfcComplexPropertyTemplate_type,IFC4_IfcSimplePropertyTemplate_type
    });
    IFC4_IfcCompositeCurve_type->set_subtypes({
        IFC4_IfcCompositeCurveOnSurface_type
    });
    IFC4_IfcFlowMovingDevice_type->set_subtypes({
        IFC4_IfcCompressor_type,IFC4_IfcFan_type,IFC4_IfcPump_type
    });
    IFC4_IfcFlowMovingDeviceType_type->set_subtypes({
        IFC4_IfcCompressorType_type,IFC4_IfcFanType_type,IFC4_IfcPumpType_type
    });
    IFC4_IfcTopologicalRepresentationItem_type->set_subtypes({
        IFC4_IfcConnectedFaceSet_type,IFC4_IfcEdge_type,IFC4_IfcFace_type,IFC4_IfcFaceBound_type,IFC4_IfcLoop_type,IFC4_IfcPath_type,IFC4_IfcVertex_type
    });
    IFC4_IfcConnectionGeometry_type->set_subtypes({
        IFC4_IfcConnectionCurveGeometry_type,IFC4_IfcConnectionPointGeometry_type,IFC4_IfcConnectionSurfaceGeometry_type,IFC4_IfcConnectionVolumeGeometry_type
    });
    IFC4_IfcConnectionPointGeometry_type->set_subtypes({
        IFC4_IfcConnectionPointEccentricity_type
    });
    IFC4_IfcConstructionResource_type->set_subtypes({
        IFC4_IfcConstructionEquipmentResource_type,IFC4_IfcConstructionMaterialResource_type,IFC4_IfcConstructionProductResource_type,IFC4_IfcCrewResource_type,IFC4_IfcLaborResource_type,IFC4_IfcSubContractResource_type
    });
    IFC4_IfcConstructionResourceType_type->set_subtypes({
        IFC4_IfcConstructionEquipmentResourceType_type,IFC4_IfcConstructionMaterialResourceType_type,IFC4_IfcConstructionProductResourceType_type,IFC4_IfcCrewResourceType_type,IFC4_IfcLaborResourceType_type,IFC4_IfcSubContractResourceType_type
    });
    IFC4_IfcResource_type->set_subtypes({
        IFC4_IfcConstructionResource_type
    });
    IFC4_IfcTypeResource_type->set_subtypes({
        IFC4_IfcConstructionResourceType_type
    });
    IFC4_IfcObjectDefinition_type->set_subtypes({
        IFC4_IfcContext_type,IFC4_IfcObject_type,IFC4_IfcTypeObject_type
    });
    IFC4_IfcNamedUnit_type->set_subtypes({
        IFC4_IfcContextDependentUnit_type,IFC4_IfcConversionBasedUnit_type,IFC4_IfcSIUnit_type
    });
    IFC4_IfcConversionBasedUnit_type->set_subtypes({
        IFC4_IfcConversionBasedUnitWithOffset_type
    });
    IFC4_IfcAppliedValue_type->set_subtypes({
        IFC4_IfcCostValue_type
    });
    IFC4_IfcSolidModel_type->set_subtypes({
        IFC4_IfcCsgSolid_type,IFC4_IfcManifoldSolidBrep_type,IFC4_IfcSweptAreaSolid_type,IFC4_IfcSweptDiskSolid_type
    });
    IFC4_IfcPresentationStyle_type->set_subtypes({
        IFC4_IfcCurveStyle_type,IFC4_IfcFillAreaStyle_type,IFC4_IfcSurfaceStyle_type,IFC4_IfcTextStyle_type
    });
    IFC4_IfcElementarySurface_type->set_subtypes({
        IFC4_IfcCylindricalSurface_type,IFC4_IfcPlane_type,IFC4_IfcSphericalSurface_type,IFC4_IfcToroidalSurface_type
    });
    IFC4_IfcDistributionFlowElement_type->set_subtypes({
        IFC4_IfcDistributionChamberElement_type,IFC4_IfcEnergyConversionDevice_type,IFC4_IfcFlowController_type,IFC4_IfcFlowFitting_type,IFC4_IfcFlowMovingDevice_type,IFC4_IfcFlowSegment_type,IFC4_IfcFlowStorageDevice_type,IFC4_IfcFlowTerminal_type,IFC4_IfcFlowTreatmentDevice_type
    });
    IFC4_IfcDistributionFlowElementType_type->set_subtypes({
        IFC4_IfcDistributionChamberElementType_type,IFC4_IfcEnergyConversionDeviceType_type,IFC4_IfcFlowControllerType_type,IFC4_IfcFlowFittingType_type,IFC4_IfcFlowMovingDeviceType_type,IFC4_IfcFlowSegmentType_type,IFC4_IfcFlowStorageDeviceType_type,IFC4_IfcFlowTerminalType_type,IFC4_IfcFlowTreatmentDeviceType_type
    });
    IFC4_IfcDistributionSystem_type->set_subtypes({
        IFC4_IfcDistributionCircuit_type
    });
    IFC4_IfcDistributionElement_type->set_subtypes({
        IFC4_IfcDistributionControlElement_type,IFC4_IfcDistributionFlowElement_type
    });
    IFC4_IfcDistributionElementType_type->set_subtypes({
        IFC4_IfcDistributionControlElementType_type,IFC4_IfcDistributionFlowElementType_type
    });
    IFC4_IfcPort_type->set_subtypes({
        IFC4_IfcDistributionPort_type
    });
    IFC4_IfcPreDefinedPropertySet_type->set_subtypes({
        IFC4_IfcDoorLiningProperties_type,IFC4_IfcDoorPanelProperties_type,IFC4_IfcPermeableCoveringProperties_type,IFC4_IfcReinforcementDefinitionProperties_type,IFC4_IfcWindowLiningProperties_type,IFC4_IfcWindowPanelProperties_type
    });
    IFC4_IfcDoor_type->set_subtypes({
        IFC4_IfcDoorStandardCase_type
    });
    IFC4_IfcTypeProduct_type->set_subtypes({
        IFC4_IfcDoorStyle_type,IFC4_IfcElementType_type,IFC4_IfcSpatialElementType_type,IFC4_IfcWindowStyle_type
    });
    IFC4_IfcPreDefinedColour_type->set_subtypes({
        IFC4_IfcDraughtingPreDefinedColour_type
    });
    IFC4_IfcPreDefinedCurveFont_type->set_subtypes({
        IFC4_IfcDraughtingPreDefinedCurveFont_type
    });
    IFC4_IfcFlowTreatmentDevice_type->set_subtypes({
        IFC4_IfcDuctSilencer_type,IFC4_IfcFilter_type,IFC4_IfcInterceptor_type
    });
    IFC4_IfcFlowTreatmentDeviceType_type->set_subtypes({
        IFC4_IfcDuctSilencerType_type,IFC4_IfcFilterType_type,IFC4_IfcInterceptorType_type
    });
    IFC4_IfcEdge_type->set_subtypes({
        IFC4_IfcEdgeCurve_type,IFC4_IfcOrientedEdge_type,IFC4_IfcSubedge_type
    });
    IFC4_IfcLoop_type->set_subtypes({
        IFC4_IfcEdgeLoop_type,IFC4_IfcPolyLoop_type,IFC4_IfcVertexLoop_type
    });
    IFC4_IfcFlowStorageDevice_type->set_subtypes({
        IFC4_IfcElectricFlowStorageDevice_type,IFC4_IfcTank_type
    });
    IFC4_IfcFlowStorageDeviceType_type->set_subtypes({
        IFC4_IfcElectricFlowStorageDeviceType_type,IFC4_IfcTankType_type
    });
    IFC4_IfcQuantitySet_type->set_subtypes({
        IFC4_IfcElementQuantity_type
    });
    IFC4_IfcProcess_type->set_subtypes({
        IFC4_IfcEvent_type,IFC4_IfcProcedure_type,IFC4_IfcTask_type
    });
    IFC4_IfcSchedulingTime_type->set_subtypes({
        IFC4_IfcEventTime_type,IFC4_IfcLagTime_type,IFC4_IfcResourceTime_type,IFC4_IfcTaskTime_type,IFC4_IfcWorkTime_type
    });
    IFC4_IfcTypeProcess_type->set_subtypes({
        IFC4_IfcEventType_type,IFC4_IfcProcedureType_type,IFC4_IfcTaskType_type
    });
    IFC4_IfcPropertyAbstraction_type->set_subtypes({
        IFC4_IfcExtendedProperties_type,IFC4_IfcPreDefinedProperties_type,IFC4_IfcProperty_type,IFC4_IfcPropertyEnumeration_type
    });
    IFC4_IfcExternalSpatialStructureElement_type->set_subtypes({
        IFC4_IfcExternalSpatialElement_type
    });
    IFC4_IfcSpatialElement_type->set_subtypes({
        IFC4_IfcExternalSpatialStructureElement_type,IFC4_IfcSpatialStructureElement_type,IFC4_IfcSpatialZone_type
    });
    IFC4_IfcSweptAreaSolid_type->set_subtypes({
        IFC4_IfcExtrudedAreaSolid_type,IFC4_IfcFixedReferenceSweptAreaSolid_type,IFC4_IfcRevolvedAreaSolid_type,IFC4_IfcSurfaceCurveSweptAreaSolid_type
    });
    IFC4_IfcExtrudedAreaSolid_type->set_subtypes({
        IFC4_IfcExtrudedAreaSolidTapered_type
    });
    IFC4_IfcFaceBound_type->set_subtypes({
        IFC4_IfcFaceOuterBound_type
    });
    IFC4_IfcFace_type->set_subtypes({
        IFC4_IfcFaceSurface_type
    });
    IFC4_IfcFacetedBrep_type->set_subtypes({
        IFC4_IfcFacetedBrepWithVoids_type
    });
    IFC4_IfcStructuralConnectionCondition_type->set_subtypes({
        IFC4_IfcFailureConnectionCondition_type,IFC4_IfcSlippageConnectionCondition_type
    });
    IFC4_IfcFeatureElement_type->set_subtypes({
        IFC4_IfcFeatureElementAddition_type,IFC4_IfcFeatureElementSubtraction_type,IFC4_IfcSurfaceFeature_type
    });
    IFC4_IfcFurnishingElement_type->set_subtypes({
        IFC4_IfcFurniture_type,IFC4_IfcSystemFurnitureElement_type
    });
    IFC4_IfcFurnishingElementType_type->set_subtypes({
        IFC4_IfcFurnitureType_type,IFC4_IfcSystemFurnitureElementType_type
    });
    IFC4_IfcGeometricSet_type->set_subtypes({
        IFC4_IfcGeometricCurveSet_type
    });
    IFC4_IfcRepresentationContext_type->set_subtypes({
        IFC4_IfcGeometricRepresentationContext_type
    });
    IFC4_IfcRepresentationItem_type->set_subtypes({
        IFC4_IfcGeometricRepresentationItem_type,IFC4_IfcMappedItem_type,IFC4_IfcStyledItem_type,IFC4_IfcTopologicalRepresentationItem_type
    });
    IFC4_IfcGeometricRepresentationContext_type->set_subtypes({
        IFC4_IfcGeometricRepresentationSubContext_type
    });
    IFC4_IfcObjectPlacement_type->set_subtypes({
        IFC4_IfcGridPlacement_type,IFC4_IfcLocalPlacement_type
    });
    IFC4_IfcTessellatedItem_type->set_subtypes({
        IFC4_IfcIndexedPolygonalFace_type,IFC4_IfcTessellatedFaceSet_type
    });
    IFC4_IfcIndexedPolygonalFace_type->set_subtypes({
        IFC4_IfcIndexedPolygonalFaceWithVoids_type
    });
    IFC4_IfcTextureCoordinate_type->set_subtypes({
        IFC4_IfcIndexedTextureMap_type,IFC4_IfcTextureCoordinateGenerator_type,IFC4_IfcTextureMap_type
    });
    IFC4_IfcIndexedTextureMap_type->set_subtypes({
        IFC4_IfcIndexedTriangleTextureMap_type
    });
    IFC4_IfcSurfaceCurve_type->set_subtypes({
        IFC4_IfcIntersectionCurve_type,IFC4_IfcSeamCurve_type
    });
    IFC4_IfcTimeSeries_type->set_subtypes({
        IFC4_IfcIrregularTimeSeries_type,IFC4_IfcRegularTimeSeries_type
    });
    IFC4_IfcLightSource_type->set_subtypes({
        IFC4_IfcLightSourceAmbient_type,IFC4_IfcLightSourceDirectional_type,IFC4_IfcLightSourceGoniometric_type,IFC4_IfcLightSourcePositional_type
    });
    IFC4_IfcLightSourcePositional_type->set_subtypes({
        IFC4_IfcLightSourceSpot_type
    });
    IFC4_IfcCoordinateOperation_type->set_subtypes({
        IFC4_IfcMapConversion_type
    });
    IFC4_IfcMaterialDefinition_type->set_subtypes({
        IFC4_IfcMaterial_type,IFC4_IfcMaterialConstituent_type,IFC4_IfcMaterialConstituentSet_type,IFC4_IfcMaterialLayer_type,IFC4_IfcMaterialLayerSet_type,IFC4_IfcMaterialProfile_type,IFC4_IfcMaterialProfileSet_type
    });
    IFC4_IfcProductRepresentation_type->set_subtypes({
        IFC4_IfcMaterialDefinitionRepresentation_type,IFC4_IfcProductDefinitionShape_type
    });
    IFC4_IfcMaterialUsageDefinition_type->set_subtypes({
        IFC4_IfcMaterialLayerSetUsage_type,IFC4_IfcMaterialProfileSetUsage_type
    });
    IFC4_IfcMaterialLayer_type->set_subtypes({
        IFC4_IfcMaterialLayerWithOffsets_type
    });
    IFC4_IfcMaterialProfileSetUsage_type->set_subtypes({
        IFC4_IfcMaterialProfileSetUsageTapering_type
    });
    IFC4_IfcMaterialProfile_type->set_subtypes({
        IFC4_IfcMaterialProfileWithOffsets_type
    });
    IFC4_IfcExtendedProperties_type->set_subtypes({
        IFC4_IfcMaterialProperties_type,IFC4_IfcProfileProperties_type
    });
    IFC4_IfcMember_type->set_subtypes({
        IFC4_IfcMemberStandardCase_type
    });
    IFC4_IfcConstraint_type->set_subtypes({
        IFC4_IfcMetric_type,IFC4_IfcObjective_type
    });
    IFC4_IfcDerivedProfileDef_type->set_subtypes({
        IFC4_IfcMirroredProfileDef_type
    });
    IFC4_IfcRoot_type->set_subtypes({
        IFC4_IfcObjectDefinition_type,IFC4_IfcPropertyDefinition_type,IFC4_IfcRelationship_type
    });
    IFC4_IfcActor_type->set_subtypes({
        IFC4_IfcOccupant_type
    });
    IFC4_IfcFeatureElementSubtraction_type->set_subtypes({
        IFC4_IfcOpeningElement_type,IFC4_IfcVoidingFeature_type
    });
    IFC4_IfcOpeningElement_type->set_subtypes({
        IFC4_IfcOpeningStandardCase_type
    });
    IFC4_IfcBoundaryCurve_type->set_subtypes({
        IFC4_IfcOuterBoundaryCurve_type
    });
    IFC4_IfcPhysicalQuantity_type->set_subtypes({
        IFC4_IfcPhysicalComplexQuantity_type,IFC4_IfcPhysicalSimpleQuantity_type
    });
    IFC4_IfcPlanarExtent_type->set_subtypes({
        IFC4_IfcPlanarBox_type
    });
    IFC4_IfcPlate_type->set_subtypes({
        IFC4_IfcPlateStandardCase_type
    });
    IFC4_IfcTessellatedFaceSet_type->set_subtypes({
        IFC4_IfcPolygonalFaceSet_type,IFC4_IfcTriangulatedFaceSet_type
    });
    IFC4_IfcAddress_type->set_subtypes({
        IFC4_IfcPostalAddress_type,IFC4_IfcTelecomAddress_type
    });
    IFC4_IfcPreDefinedItem_type->set_subtypes({
        IFC4_IfcPreDefinedColour_type,IFC4_IfcPreDefinedCurveFont_type,IFC4_IfcPreDefinedTextFont_type
    });
    IFC4_IfcPropertySetDefinition_type->set_subtypes({
        IFC4_IfcPreDefinedPropertySet_type,IFC4_IfcPropertySet_type,IFC4_IfcQuantitySet_type
    });
    IFC4_IfcPresentationLayerAssignment_type->set_subtypes({
        IFC4_IfcPresentationLayerWithStyle_type
    });
    IFC4_IfcContext_type->set_subtypes({
        IFC4_IfcProject_type,IFC4_IfcProjectLibrary_type
    });
    IFC4_IfcCoordinateReferenceSystem_type->set_subtypes({
        IFC4_IfcProjectedCRS_type
    });
    IFC4_IfcFeatureElementAddition_type->set_subtypes({
        IFC4_IfcProjectionElement_type
    });
    IFC4_IfcSimpleProperty_type->set_subtypes({
        IFC4_IfcPropertyBoundedValue_type,IFC4_IfcPropertyEnumeratedValue_type,IFC4_IfcPropertyListValue_type,IFC4_IfcPropertyReferenceValue_type,IFC4_IfcPropertySingleValue_type,IFC4_IfcPropertyTableValue_type
    });
    IFC4_IfcPropertyDefinition_type->set_subtypes({
        IFC4_IfcPropertySetDefinition_type,IFC4_IfcPropertyTemplateDefinition_type
    });
    IFC4_IfcPropertyTemplateDefinition_type->set_subtypes({
        IFC4_IfcPropertySetTemplate_type,IFC4_IfcPropertyTemplate_type
    });
    IFC4_IfcPhysicalSimpleQuantity_type->set_subtypes({
        IFC4_IfcQuantityArea_type,IFC4_IfcQuantityCount_type,IFC4_IfcQuantityLength_type,IFC4_IfcQuantityTime_type,IFC4_IfcQuantityVolume_type,IFC4_IfcQuantityWeight_type
    });
    IFC4_IfcBSplineCurveWithKnots_type->set_subtypes({
        IFC4_IfcRationalBSplineCurveWithKnots_type
    });
    IFC4_IfcBSplineSurfaceWithKnots_type->set_subtypes({
        IFC4_IfcRationalBSplineSurfaceWithKnots_type
    });
    IFC4_IfcRectangleProfileDef_type->set_subtypes({
        IFC4_IfcRectangleHollowProfileDef_type,IFC4_IfcRoundedRectangleProfileDef_type
    });
    IFC4_IfcPreDefinedProperties_type->set_subtypes({
        IFC4_IfcReinforcementBarProperties_type,IFC4_IfcSectionProperties_type,IFC4_IfcSectionReinforcementProperties_type
    });
    IFC4_IfcReinforcingElement_type->set_subtypes({
        IFC4_IfcReinforcingBar_type,IFC4_IfcReinforcingMesh_type,IFC4_IfcTendon_type,IFC4_IfcTendonAnchor_type
    });
    IFC4_IfcReinforcingElementType_type->set_subtypes({
        IFC4_IfcReinforcingBarType_type,IFC4_IfcReinforcingMeshType_type,IFC4_IfcTendonAnchorType_type,IFC4_IfcTendonType_type
    });
    IFC4_IfcRelDecomposes_type->set_subtypes({
        IFC4_IfcRelAggregates_type,IFC4_IfcRelNests_type,IFC4_IfcRelProjectsElement_type,IFC4_IfcRelVoidsElement_type
    });
    IFC4_IfcRelationship_type->set_subtypes({
        IFC4_IfcRelAssigns_type,IFC4_IfcRelAssociates_type,IFC4_IfcRelConnects_type,IFC4_IfcRelDeclares_type,IFC4_IfcRelDecomposes_type,IFC4_IfcRelDefines_type
    });
    IFC4_IfcRelAssigns_type->set_subtypes({
        IFC4_IfcRelAssignsToActor_type,IFC4_IfcRelAssignsToControl_type,IFC4_IfcRelAssignsToGroup_type,IFC4_IfcRelAssignsToProcess_type,IFC4_IfcRelAssignsToProduct_type,IFC4_IfcRelAssignsToResource_type
    });
    IFC4_IfcRelAssignsToGroup_type->set_subtypes({
        IFC4_IfcRelAssignsToGroupByFactor_type
    });
    IFC4_IfcRelAssociates_type->set_subtypes({
        IFC4_IfcRelAssociatesApproval_type,IFC4_IfcRelAssociatesClassification_type,IFC4_IfcRelAssociatesConstraint_type,IFC4_IfcRelAssociatesDocument_type,IFC4_IfcRelAssociatesLibrary_type,IFC4_IfcRelAssociatesMaterial_type
    });
    IFC4_IfcRelConnects_type->set_subtypes({
        IFC4_IfcRelConnectsElements_type,IFC4_IfcRelConnectsPortToElement_type,IFC4_IfcRelConnectsPorts_type,IFC4_IfcRelConnectsStructuralActivity_type,IFC4_IfcRelConnectsStructuralMember_type,IFC4_IfcRelContainedInSpatialStructure_type,IFC4_IfcRelCoversBldgElements_type,IFC4_IfcRelCoversSpaces_type,IFC4_IfcRelFillsElement_type,IFC4_IfcRelFlowControlElements_type,IFC4_IfcRelInterferesElements_type,IFC4_IfcRelReferencedInSpatialStructure_type,IFC4_IfcRelSequence_type,IFC4_IfcRelServicesBuildings_type,IFC4_IfcRelSpaceBoundary_type
    });
    IFC4_IfcRelConnectsElements_type->set_subtypes({
        IFC4_IfcRelConnectsPathElements_type,IFC4_IfcRelConnectsWithRealizingElements_type
    });
    IFC4_IfcRelConnectsStructuralMember_type->set_subtypes({
        IFC4_IfcRelConnectsWithEccentricity_type
    });
    IFC4_IfcRelDefines_type->set_subtypes({
        IFC4_IfcRelDefinesByObject_type,IFC4_IfcRelDefinesByProperties_type,IFC4_IfcRelDefinesByTemplate_type,IFC4_IfcRelDefinesByType_type
    });
    IFC4_IfcRelSpaceBoundary_type->set_subtypes({
        IFC4_IfcRelSpaceBoundary1stLevel_type
    });
    IFC4_IfcRelSpaceBoundary1stLevel_type->set_subtypes({
        IFC4_IfcRelSpaceBoundary2ndLevel_type
    });
    IFC4_IfcCompositeCurveSegment_type->set_subtypes({
        IFC4_IfcReparametrisedCompositeCurveSegment_type
    });
    IFC4_IfcRevolvedAreaSolid_type->set_subtypes({
        IFC4_IfcRevolvedAreaSolidTapered_type
    });
    IFC4_IfcRepresentation_type->set_subtypes({
        IFC4_IfcShapeModel_type,IFC4_IfcStyleModel_type
    });
    IFC4_IfcShapeModel_type->set_subtypes({
        IFC4_IfcShapeRepresentation_type,IFC4_IfcTopologyRepresentation_type
    });
    IFC4_IfcSlab_type->set_subtypes({
        IFC4_IfcSlabElementedCase_type,IFC4_IfcSlabStandardCase_type
    });
    IFC4_IfcSpatialStructureElementType_type->set_subtypes({
        IFC4_IfcSpaceType_type
    });
    IFC4_IfcSpatialElementType_type->set_subtypes({
        IFC4_IfcSpatialStructureElementType_type,IFC4_IfcSpatialZoneType_type
    });
    IFC4_IfcStructuralActivity_type->set_subtypes({
        IFC4_IfcStructuralAction_type,IFC4_IfcStructuralReaction_type
    });
    IFC4_IfcStructuralItem_type->set_subtypes({
        IFC4_IfcStructuralConnection_type,IFC4_IfcStructuralMember_type
    });
    IFC4_IfcStructuralAction_type->set_subtypes({
        IFC4_IfcStructuralCurveAction_type,IFC4_IfcStructuralPointAction_type,IFC4_IfcStructuralSurfaceAction_type
    });
    IFC4_IfcStructuralConnection_type->set_subtypes({
        IFC4_IfcStructuralCurveConnection_type,IFC4_IfcStructuralPointConnection_type,IFC4_IfcStructuralSurfaceConnection_type
    });
    IFC4_IfcStructuralMember_type->set_subtypes({
        IFC4_IfcStructuralCurveMember_type,IFC4_IfcStructuralSurfaceMember_type
    });
    IFC4_IfcStructuralCurveMember_type->set_subtypes({
        IFC4_IfcStructuralCurveMemberVarying_type
    });
    IFC4_IfcStructuralReaction_type->set_subtypes({
        IFC4_IfcStructuralCurveReaction_type,IFC4_IfcStructuralPointReaction_type,IFC4_IfcStructuralSurfaceReaction_type
    });
    IFC4_IfcStructuralCurveAction_type->set_subtypes({
        IFC4_IfcStructuralLinearAction_type
    });
    IFC4_IfcStructuralLoadGroup_type->set_subtypes({
        IFC4_IfcStructuralLoadCase_type
    });
    IFC4_IfcStructuralLoad_type->set_subtypes({
        IFC4_IfcStructuralLoadConfiguration_type,IFC4_IfcStructuralLoadOrResult_type
    });
    IFC4_IfcStructuralLoadStatic_type->set_subtypes({
        IFC4_IfcStructuralLoadLinearForce_type,IFC4_IfcStructuralLoadPlanarForce_type,IFC4_IfcStructuralLoadSingleDisplacement_type,IFC4_IfcStructuralLoadSingleForce_type,IFC4_IfcStructuralLoadTemperature_type
    });
    IFC4_IfcStructuralLoadSingleDisplacement_type->set_subtypes({
        IFC4_IfcStructuralLoadSingleDisplacementDistortion_type
    });
    IFC4_IfcStructuralLoadSingleForce_type->set_subtypes({
        IFC4_IfcStructuralLoadSingleForceWarping_type
    });
    IFC4_IfcStructuralLoadOrResult_type->set_subtypes({
        IFC4_IfcStructuralLoadStatic_type,IFC4_IfcSurfaceReinforcementArea_type
    });
    IFC4_IfcStructuralSurfaceAction_type->set_subtypes({
        IFC4_IfcStructuralPlanarAction_type
    });
    IFC4_IfcStructuralSurfaceMember_type->set_subtypes({
        IFC4_IfcStructuralSurfaceMemberVarying_type
    });
    IFC4_IfcStyleModel_type->set_subtypes({
        IFC4_IfcStyledRepresentation_type
    });
    IFC4_IfcSweptSurface_type->set_subtypes({
        IFC4_IfcSurfaceOfLinearExtrusion_type,IFC4_IfcSurfaceOfRevolution_type
    });
    IFC4_IfcSurfaceStyleShading_type->set_subtypes({
        IFC4_IfcSurfaceStyleRendering_type
    });
    IFC4_IfcSweptDiskSolid_type->set_subtypes({
        IFC4_IfcSweptDiskSolidPolygonal_type
    });
    IFC4_IfcTaskTime_type->set_subtypes({
        IFC4_IfcTaskTimeRecurring_type
    });
    IFC4_IfcTextLiteral_type->set_subtypes({
        IFC4_IfcTextLiteralWithExtent_type
    });
    IFC4_IfcPreDefinedTextFont_type->set_subtypes({
        IFC4_IfcTextStyleFontModel_type
    });
    IFC4_IfcTypeObject_type->set_subtypes({
        IFC4_IfcTypeProcess_type,IFC4_IfcTypeProduct_type,IFC4_IfcTypeResource_type
    });
    IFC4_IfcVertex_type->set_subtypes({
        IFC4_IfcVertexPoint_type
    });
    IFC4_IfcWall_type->set_subtypes({
        IFC4_IfcWallElementedCase_type,IFC4_IfcWallStandardCase_type
    });
    IFC4_IfcWindow_type->set_subtypes({
        IFC4_IfcWindowStandardCase_type
    });
    IFC4_IfcWorkControl_type->set_subtypes({
        IFC4_IfcWorkPlan_type,IFC4_IfcWorkSchedule_type
    });

    std::vector<const declaration*> declarations= {
    IFC4_IfcAbsorbedDoseMeasure_type,
    IFC4_IfcAccelerationMeasure_type,
    IFC4_IfcActionRequest_type,
    IFC4_IfcActionRequestTypeEnum_type,
    IFC4_IfcActionSourceTypeEnum_type,
    IFC4_IfcActionTypeEnum_type,
    IFC4_IfcActor_type,
    IFC4_IfcActorRole_type,
    IFC4_IfcActorSelect_type,
    IFC4_IfcActuator_type,
    IFC4_IfcActuatorType_type,
    IFC4_IfcActuatorTypeEnum_type,
    IFC4_IfcAddress_type,
    IFC4_IfcAddressTypeEnum_type,
    IFC4_IfcAdvancedBrep_type,
    IFC4_IfcAdvancedBrepWithVoids_type,
    IFC4_IfcAdvancedFace_type,
    IFC4_IfcAirTerminal_type,
    IFC4_IfcAirTerminalBox_type,
    IFC4_IfcAirTerminalBoxType_type,
    IFC4_IfcAirTerminalBoxTypeEnum_type,
    IFC4_IfcAirTerminalType_type,
    IFC4_IfcAirTerminalTypeEnum_type,
    IFC4_IfcAirToAirHeatRecovery_type,
    IFC4_IfcAirToAirHeatRecoveryType_type,
    IFC4_IfcAirToAirHeatRecoveryTypeEnum_type,
    IFC4_IfcAlarm_type,
    IFC4_IfcAlarmType_type,
    IFC4_IfcAlarmTypeEnum_type,
    IFC4_IfcAmountOfSubstanceMeasure_type,
    IFC4_IfcAnalysisModelTypeEnum_type,
    IFC4_IfcAnalysisTheoryTypeEnum_type,
    IFC4_IfcAngularVelocityMeasure_type,
    IFC4_IfcAnnotation_type,
    IFC4_IfcAnnotationFillArea_type,
    IFC4_IfcApplication_type,
    IFC4_IfcAppliedValue_type,
    IFC4_IfcAppliedValueSelect_type,
    IFC4_IfcApproval_type,
    IFC4_IfcApprovalRelationship_type,
    IFC4_IfcArbitraryClosedProfileDef_type,
    IFC4_IfcArbitraryOpenProfileDef_type,
    IFC4_IfcArbitraryProfileDefWithVoids_type,
    IFC4_IfcArcIndex_type,
    IFC4_IfcAreaDensityMeasure_type,
    IFC4_IfcAreaMeasure_type,
    IFC4_IfcArithmeticOperatorEnum_type,
    IFC4_IfcAssemblyPlaceEnum_type,
    IFC4_IfcAsset_type,
    IFC4_IfcAsymmetricIShapeProfileDef_type,
    IFC4_IfcAudioVisualAppliance_type,
    IFC4_IfcAudioVisualApplianceType_type,
    IFC4_IfcAudioVisualApplianceTypeEnum_type,
    IFC4_IfcAxis1Placement_type,
    IFC4_IfcAxis2Placement_type,
    IFC4_IfcAxis2Placement2D_type,
    IFC4_IfcAxis2Placement3D_type,
    IFC4_IfcBeam_type,
    IFC4_IfcBeamStandardCase_type,
    IFC4_IfcBeamType_type,
    IFC4_IfcBeamTypeEnum_type,
    IFC4_IfcBenchmarkEnum_type,
    IFC4_IfcBendingParameterSelect_type,
    IFC4_IfcBinary_type,
    IFC4_IfcBlobTexture_type,
    IFC4_IfcBlock_type,
    IFC4_IfcBoiler_type,
    IFC4_IfcBoilerType_type,
    IFC4_IfcBoilerTypeEnum_type,
    IFC4_IfcBoolean_type,
    IFC4_IfcBooleanClippingResult_type,
    IFC4_IfcBooleanOperand_type,
    IFC4_IfcBooleanOperator_type,
    IFC4_IfcBooleanResult_type,
    IFC4_IfcBoundaryCondition_type,
    IFC4_IfcBoundaryCurve_type,
    IFC4_IfcBoundaryEdgeCondition_type,
    IFC4_IfcBoundaryFaceCondition_type,
    IFC4_IfcBoundaryNodeCondition_type,
    IFC4_IfcBoundaryNodeConditionWarping_type,
    IFC4_IfcBoundedCurve_type,
    IFC4_IfcBoundedSurface_type,
    IFC4_IfcBoundingBox_type,
    IFC4_IfcBoxAlignment_type,
    IFC4_IfcBoxedHalfSpace_type,
    IFC4_IfcBSplineCurve_type,
    IFC4_IfcBSplineCurveForm_type,
    IFC4_IfcBSplineCurveWithKnots_type,
    IFC4_IfcBSplineSurface_type,
    IFC4_IfcBSplineSurfaceForm_type,
    IFC4_IfcBSplineSurfaceWithKnots_type,
    IFC4_IfcBuilding_type,
    IFC4_IfcBuildingElement_type,
    IFC4_IfcBuildingElementPart_type,
    IFC4_IfcBuildingElementPartType_type,
    IFC4_IfcBuildingElementPartTypeEnum_type,
    IFC4_IfcBuildingElementProxy_type,
    IFC4_IfcBuildingElementProxyType_type,
    IFC4_IfcBuildingElementProxyTypeEnum_type,
    IFC4_IfcBuildingElementType_type,
    IFC4_IfcBuildingStorey_type,
    IFC4_IfcBuildingSystem_type,
    IFC4_IfcBuildingSystemTypeEnum_type,
    IFC4_IfcBurner_type,
    IFC4_IfcBurnerType_type,
    IFC4_IfcBurnerTypeEnum_type,
    IFC4_IfcCableCarrierFitting_type,
    IFC4_IfcCableCarrierFittingType_type,
    IFC4_IfcCableCarrierFittingTypeEnum_type,
    IFC4_IfcCableCarrierSegment_type,
    IFC4_IfcCableCarrierSegmentType_type,
    IFC4_IfcCableCarrierSegmentTypeEnum_type,
    IFC4_IfcCableFitting_type,
    IFC4_IfcCableFittingType_type,
    IFC4_IfcCableFittingTypeEnum_type,
    IFC4_IfcCableSegment_type,
    IFC4_IfcCableSegmentType_type,
    IFC4_IfcCableSegmentTypeEnum_type,
    IFC4_IfcCardinalPointReference_type,
    IFC4_IfcCartesianPoint_type,
    IFC4_IfcCartesianPointList_type,
    IFC4_IfcCartesianPointList2D_type,
    IFC4_IfcCartesianPointList3D_type,
    IFC4_IfcCartesianTransformationOperator_type,
    IFC4_IfcCartesianTransformationOperator2D_type,
    IFC4_IfcCartesianTransformationOperator2DnonUniform_type,
    IFC4_IfcCartesianTransformationOperator3D_type,
    IFC4_IfcCartesianTransformationOperator3DnonUniform_type,
    IFC4_IfcCenterLineProfileDef_type,
    IFC4_IfcChangeActionEnum_type,
    IFC4_IfcChiller_type,
    IFC4_IfcChillerType_type,
    IFC4_IfcChillerTypeEnum_type,
    IFC4_IfcChimney_type,
    IFC4_IfcChimneyType_type,
    IFC4_IfcChimneyTypeEnum_type,
    IFC4_IfcCircle_type,
    IFC4_IfcCircleHollowProfileDef_type,
    IFC4_IfcCircleProfileDef_type,
    IFC4_IfcCivilElement_type,
    IFC4_IfcCivilElementType_type,
    IFC4_IfcClassification_type,
    IFC4_IfcClassificationReference_type,
    IFC4_IfcClassificationReferenceSelect_type,
    IFC4_IfcClassificationSelect_type,
    IFC4_IfcClosedShell_type,
    IFC4_IfcCoil_type,
    IFC4_IfcCoilType_type,
    IFC4_IfcCoilTypeEnum_type,
    IFC4_IfcColour_type,
    IFC4_IfcColourOrFactor_type,
    IFC4_IfcColourRgb_type,
    IFC4_IfcColourRgbList_type,
    IFC4_IfcColourSpecification_type,
    IFC4_IfcColumn_type,
    IFC4_IfcColumnStandardCase_type,
    IFC4_IfcColumnType_type,
    IFC4_IfcColumnTypeEnum_type,
    IFC4_IfcCommunicationsAppliance_type,
    IFC4_IfcCommunicationsApplianceType_type,
    IFC4_IfcCommunicationsApplianceTypeEnum_type,
    IFC4_IfcComplexNumber_type,
    IFC4_IfcComplexProperty_type,
    IFC4_IfcComplexPropertyTemplate_type,
    IFC4_IfcComplexPropertyTemplateTypeEnum_type,
    IFC4_IfcCompositeCurve_type,
    IFC4_IfcCompositeCurveOnSurface_type,
    IFC4_IfcCompositeCurveSegment_type,
    IFC4_IfcCompositeProfileDef_type,
    IFC4_IfcCompoundPlaneAngleMeasure_type,
    IFC4_IfcCompressor_type,
    IFC4_IfcCompressorType_type,
    IFC4_IfcCompressorTypeEnum_type,
    IFC4_IfcCondenser_type,
    IFC4_IfcCondenserType_type,
    IFC4_IfcCondenserTypeEnum_type,
    IFC4_IfcConic_type,
    IFC4_IfcConnectedFaceSet_type,
    IFC4_IfcConnectionCurveGeometry_type,
    IFC4_IfcConnectionGeometry_type,
    IFC4_IfcConnectionPointEccentricity_type,
    IFC4_IfcConnectionPointGeometry_type,
    IFC4_IfcConnectionSurfaceGeometry_type,
    IFC4_IfcConnectionTypeEnum_type,
    IFC4_IfcConnectionVolumeGeometry_type,
    IFC4_IfcConstraint_type,
    IFC4_IfcConstraintEnum_type,
    IFC4_IfcConstructionEquipmentResource_type,
    IFC4_IfcConstructionEquipmentResourceType_type,
    IFC4_IfcConstructionEquipmentResourceTypeEnum_type,
    IFC4_IfcConstructionMaterialResource_type,
    IFC4_IfcConstructionMaterialResourceType_type,
    IFC4_IfcConstructionMaterialResourceTypeEnum_type,
    IFC4_IfcConstructionProductResource_type,
    IFC4_IfcConstructionProductResourceType_type,
    IFC4_IfcConstructionProductResourceTypeEnum_type,
    IFC4_IfcConstructionResource_type,
    IFC4_IfcConstructionResourceType_type,
    IFC4_IfcContext_type,
    IFC4_IfcContextDependentMeasure_type,
    IFC4_IfcContextDependentUnit_type,
    IFC4_IfcControl_type,
    IFC4_IfcController_type,
    IFC4_IfcControllerType_type,
    IFC4_IfcControllerTypeEnum_type,
    IFC4_IfcConversionBasedUnit_type,
    IFC4_IfcConversionBasedUnitWithOffset_type,
    IFC4_IfcCooledBeam_type,
    IFC4_IfcCooledBeamType_type,
    IFC4_IfcCooledBeamTypeEnum_type,
    IFC4_IfcCoolingTower_type,
    IFC4_IfcCoolingTowerType_type,
    IFC4_IfcCoolingTowerTypeEnum_type,
    IFC4_IfcCoordinateOperation_type,
    IFC4_IfcCoordinateReferenceSystem_type,
    IFC4_IfcCoordinateReferenceSystemSelect_type,
    IFC4_IfcCostItem_type,
    IFC4_IfcCostItemTypeEnum_type,
    IFC4_IfcCostSchedule_type,
    IFC4_IfcCostScheduleTypeEnum_type,
    IFC4_IfcCostValue_type,
    IFC4_IfcCountMeasure_type,
    IFC4_IfcCovering_type,
    IFC4_IfcCoveringType_type,
    IFC4_IfcCoveringTypeEnum_type,
    IFC4_IfcCrewResource_type,
    IFC4_IfcCrewResourceType_type,
    IFC4_IfcCrewResourceTypeEnum_type,
    IFC4_IfcCsgPrimitive3D_type,
    IFC4_IfcCsgSelect_type,
    IFC4_IfcCsgSolid_type,
    IFC4_IfcCShapeProfileDef_type,
    IFC4_IfcCurrencyRelationship_type,
    IFC4_IfcCurtainWall_type,
    IFC4_IfcCurtainWallType_type,
    IFC4_IfcCurtainWallTypeEnum_type,
    IFC4_IfcCurvatureMeasure_type,
    IFC4_IfcCurve_type,
    IFC4_IfcCurveBoundedPlane_type,
    IFC4_IfcCurveBoundedSurface_type,
    IFC4_IfcCurveFontOrScaledCurveFontSelect_type,
    IFC4_IfcCurveInterpolationEnum_type,
    IFC4_IfcCurveOnSurface_type,
    IFC4_IfcCurveOrEdgeCurve_type,
    IFC4_IfcCurveStyle_type,
    IFC4_IfcCurveStyleFont_type,
    IFC4_IfcCurveStyleFontAndScaling_type,
    IFC4_IfcCurveStyleFontPattern_type,
    IFC4_IfcCurveStyleFontSelect_type,
    IFC4_IfcCylindricalSurface_type,
    IFC4_IfcDamper_type,
    IFC4_IfcDamperType_type,
    IFC4_IfcDamperTypeEnum_type,
    IFC4_IfcDataOriginEnum_type,
    IFC4_IfcDate_type,
    IFC4_IfcDateTime_type,
    IFC4_IfcDayInMonthNumber_type,
    IFC4_IfcDayInWeekNumber_type,
    IFC4_IfcDefinitionSelect_type,
    IFC4_IfcDerivedMeasureValue_type,
    IFC4_IfcDerivedProfileDef_type,
    IFC4_IfcDerivedUnit_type,
    IFC4_IfcDerivedUnitElement_type,
    IFC4_IfcDerivedUnitEnum_type,
    IFC4_IfcDescriptiveMeasure_type,
    IFC4_IfcDimensionalExponents_type,
    IFC4_IfcDimensionCount_type,
    IFC4_IfcDirection_type,
    IFC4_IfcDirectionSenseEnum_type,
    IFC4_IfcDiscreteAccessory_type,
    IFC4_IfcDiscreteAccessoryType_type,
    IFC4_IfcDiscreteAccessoryTypeEnum_type,
    IFC4_IfcDistributionChamberElement_type,
    IFC4_IfcDistributionChamberElementType_type,
    IFC4_IfcDistributionChamberElementTypeEnum_type,
    IFC4_IfcDistributionCircuit_type,
    IFC4_IfcDistributionControlElement_type,
    IFC4_IfcDistributionControlElementType_type,
    IFC4_IfcDistributionElement_type,
    IFC4_IfcDistributionElementType_type,
    IFC4_IfcDistributionFlowElement_type,
    IFC4_IfcDistributionFlowElementType_type,
    IFC4_IfcDistributionPort_type,
    IFC4_IfcDistributionPortTypeEnum_type,
    IFC4_IfcDistributionSystem_type,
    IFC4_IfcDistributionSystemEnum_type,
    IFC4_IfcDocumentConfidentialityEnum_type,
    IFC4_IfcDocumentInformation_type,
    IFC4_IfcDocumentInformationRelationship_type,
    IFC4_IfcDocumentReference_type,
    IFC4_IfcDocumentSelect_type,
    IFC4_IfcDocumentStatusEnum_type,
    IFC4_IfcDoor_type,
    IFC4_IfcDoorLiningProperties_type,
    IFC4_IfcDoorPanelOperationEnum_type,
    IFC4_IfcDoorPanelPositionEnum_type,
    IFC4_IfcDoorPanelProperties_type,
    IFC4_IfcDoorStandardCase_type,
    IFC4_IfcDoorStyle_type,
    IFC4_IfcDoorStyleConstructionEnum_type,
    IFC4_IfcDoorStyleOperationEnum_type,
    IFC4_IfcDoorType_type,
    IFC4_IfcDoorTypeEnum_type,
    IFC4_IfcDoorTypeOperationEnum_type,
    IFC4_IfcDoseEquivalentMeasure_type,
    IFC4_IfcDraughtingPreDefinedColour_type,
    IFC4_IfcDraughtingPreDefinedCurveFont_type,
    IFC4_IfcDuctFitting_type,
    IFC4_IfcDuctFittingType_type,
    IFC4_IfcDuctFittingTypeEnum_type,
    IFC4_IfcDuctSegment_type,
    IFC4_IfcDuctSegmentType_type,
    IFC4_IfcDuctSegmentTypeEnum_type,
    IFC4_IfcDuctSilencer_type,
    IFC4_IfcDuctSilencerType_type,
    IFC4_IfcDuctSilencerTypeEnum_type,
    IFC4_IfcDuration_type,
    IFC4_IfcDynamicViscosityMeasure_type,
    IFC4_IfcEdge_type,
    IFC4_IfcEdgeCurve_type,
    IFC4_IfcEdgeLoop_type,
    IFC4_IfcElectricAppliance_type,
    IFC4_IfcElectricApplianceType_type,
    IFC4_IfcElectricApplianceTypeEnum_type,
    IFC4_IfcElectricCapacitanceMeasure_type,
    IFC4_IfcElectricChargeMeasure_type,
    IFC4_IfcElectricConductanceMeasure_type,
    IFC4_IfcElectricCurrentMeasure_type,
    IFC4_IfcElectricDistributionBoard_type,
    IFC4_IfcElectricDistributionBoardType_type,
    IFC4_IfcElectricDistributionBoardTypeEnum_type,
    IFC4_IfcElectricFlowStorageDevice_type,
    IFC4_IfcElectricFlowStorageDeviceType_type,
    IFC4_IfcElectricFlowStorageDeviceTypeEnum_type,
    IFC4_IfcElectricGenerator_type,
    IFC4_IfcElectricGeneratorType_type,
    IFC4_IfcElectricGeneratorTypeEnum_type,
    IFC4_IfcElectricMotor_type,
    IFC4_IfcElectricMotorType_type,
    IFC4_IfcElectricMotorTypeEnum_type,
    IFC4_IfcElectricResistanceMeasure_type,
    IFC4_IfcElectricTimeControl_type,
    IFC4_IfcElectricTimeControlType_type,
    IFC4_IfcElectricTimeControlTypeEnum_type,
    IFC4_IfcElectricVoltageMeasure_type,
    IFC4_IfcElement_type,
    IFC4_IfcElementarySurface_type,
    IFC4_IfcElementAssembly_type,
    IFC4_IfcElementAssemblyType_type,
    IFC4_IfcElementAssemblyTypeEnum_type,
    IFC4_IfcElementComponent_type,
    IFC4_IfcElementComponentType_type,
    IFC4_IfcElementCompositionEnum_type,
    IFC4_IfcElementQuantity_type,
    IFC4_IfcElementType_type,
    IFC4_IfcEllipse_type,
    IFC4_IfcEllipseProfileDef_type,
    IFC4_IfcEnergyConversionDevice_type,
    IFC4_IfcEnergyConversionDeviceType_type,
    IFC4_IfcEnergyMeasure_type,
    IFC4_IfcEngine_type,
    IFC4_IfcEngineType_type,
    IFC4_IfcEngineTypeEnum_type,
    IFC4_IfcEvaporativeCooler_type,
    IFC4_IfcEvaporativeCoolerType_type,
    IFC4_IfcEvaporativeCoolerTypeEnum_type,
    IFC4_IfcEvaporator_type,
    IFC4_IfcEvaporatorType_type,
    IFC4_IfcEvaporatorTypeEnum_type,
    IFC4_IfcEvent_type,
    IFC4_IfcEventTime_type,
    IFC4_IfcEventTriggerTypeEnum_type,
    IFC4_IfcEventType_type,
    IFC4_IfcEventTypeEnum_type,
    IFC4_IfcExtendedProperties_type,
    IFC4_IfcExternalInformation_type,
    IFC4_IfcExternallyDefinedHatchStyle_type,
    IFC4_IfcExternallyDefinedSurfaceStyle_type,
    IFC4_IfcExternallyDefinedTextFont_type,
    IFC4_IfcExternalReference_type,
    IFC4_IfcExternalReferenceRelationship_type,
    IFC4_IfcExternalSpatialElement_type,
    IFC4_IfcExternalSpatialElementTypeEnum_type,
    IFC4_IfcExternalSpatialStructureElement_type,
    IFC4_IfcExtrudedAreaSolid_type,
    IFC4_IfcExtrudedAreaSolidTapered_type,
    IFC4_IfcFace_type,
    IFC4_IfcFaceBasedSurfaceModel_type,
    IFC4_IfcFaceBound_type,
    IFC4_IfcFaceOuterBound_type,
    IFC4_IfcFaceSurface_type,
    IFC4_IfcFacetedBrep_type,
    IFC4_IfcFacetedBrepWithVoids_type,
    IFC4_IfcFailureConnectionCondition_type,
    IFC4_IfcFan_type,
    IFC4_IfcFanType_type,
    IFC4_IfcFanTypeEnum_type,
    IFC4_IfcFastener_type,
    IFC4_IfcFastenerType_type,
    IFC4_IfcFastenerTypeEnum_type,
    IFC4_IfcFeatureElement_type,
    IFC4_IfcFeatureElementAddition_type,
    IFC4_IfcFeatureElementSubtraction_type,
    IFC4_IfcFillAreaStyle_type,
    IFC4_IfcFillAreaStyleHatching_type,
    IFC4_IfcFillAreaStyleTiles_type,
    IFC4_IfcFillStyleSelect_type,
    IFC4_IfcFilter_type,
    IFC4_IfcFilterType_type,
    IFC4_IfcFilterTypeEnum_type,
    IFC4_IfcFireSuppressionTerminal_type,
    IFC4_IfcFireSuppressionTerminalType_type,
    IFC4_IfcFireSuppressionTerminalTypeEnum_type,
    IFC4_IfcFixedReferenceSweptAreaSolid_type,
    IFC4_IfcFlowController_type,
    IFC4_IfcFlowControllerType_type,
    IFC4_IfcFlowDirectionEnum_type,
    IFC4_IfcFlowFitting_type,
    IFC4_IfcFlowFittingType_type,
    IFC4_IfcFlowInstrument_type,
    IFC4_IfcFlowInstrumentType_type,
    IFC4_IfcFlowInstrumentTypeEnum_type,
    IFC4_IfcFlowMeter_type,
    IFC4_IfcFlowMeterType_type,
    IFC4_IfcFlowMeterTypeEnum_type,
    IFC4_IfcFlowMovingDevice_type,
    IFC4_IfcFlowMovingDeviceType_type,
    IFC4_IfcFlowSegment_type,
    IFC4_IfcFlowSegmentType_type,
    IFC4_IfcFlowStorageDevice_type,
    IFC4_IfcFlowStorageDeviceType_type,
    IFC4_IfcFlowTerminal_type,
    IFC4_IfcFlowTerminalType_type,
    IFC4_IfcFlowTreatmentDevice_type,
    IFC4_IfcFlowTreatmentDeviceType_type,
    IFC4_IfcFontStyle_type,
    IFC4_IfcFontVariant_type,
    IFC4_IfcFontWeight_type,
    IFC4_IfcFooting_type,
    IFC4_IfcFootingType_type,
    IFC4_IfcFootingTypeEnum_type,
    IFC4_IfcForceMeasure_type,
    IFC4_IfcFrequencyMeasure_type,
    IFC4_IfcFurnishingElement_type,
    IFC4_IfcFurnishingElementType_type,
    IFC4_IfcFurniture_type,
    IFC4_IfcFurnitureType_type,
    IFC4_IfcFurnitureTypeEnum_type,
    IFC4_IfcGeographicElement_type,
    IFC4_IfcGeographicElementType_type,
    IFC4_IfcGeographicElementTypeEnum_type,
    IFC4_IfcGeometricCurveSet_type,
    IFC4_IfcGeometricProjectionEnum_type,
    IFC4_IfcGeometricRepresentationContext_type,
    IFC4_IfcGeometricRepresentationItem_type,
    IFC4_IfcGeometricRepresentationSubContext_type,
    IFC4_IfcGeometricSet_type,
    IFC4_IfcGeometricSetSelect_type,
    IFC4_IfcGloballyUniqueId_type,
    IFC4_IfcGlobalOrLocalEnum_type,
    IFC4_IfcGrid_type,
    IFC4_IfcGridAxis_type,
    IFC4_IfcGridPlacement_type,
    IFC4_IfcGridPlacementDirectionSelect_type,
    IFC4_IfcGridTypeEnum_type,
    IFC4_IfcGroup_type,
    IFC4_IfcHalfSpaceSolid_type,
    IFC4_IfcHatchLineDistanceSelect_type,
    IFC4_IfcHeatExchanger_type,
    IFC4_IfcHeatExchangerType_type,
    IFC4_IfcHeatExchangerTypeEnum_type,
    IFC4_IfcHeatFluxDensityMeasure_type,
    IFC4_IfcHeatingValueMeasure_type,
    IFC4_IfcHumidifier_type,
    IFC4_IfcHumidifierType_type,
    IFC4_IfcHumidifierTypeEnum_type,
    IFC4_IfcIdentifier_type,
    IFC4_IfcIlluminanceMeasure_type,
    IFC4_IfcImageTexture_type,
    IFC4_IfcIndexedColourMap_type,
    IFC4_IfcIndexedPolyCurve_type,
    IFC4_IfcIndexedPolygonalFace_type,
    IFC4_IfcIndexedPolygonalFaceWithVoids_type,
    IFC4_IfcIndexedTextureMap_type,
    IFC4_IfcIndexedTriangleTextureMap_type,
    IFC4_IfcInductanceMeasure_type,
    IFC4_IfcInteger_type,
    IFC4_IfcIntegerCountRateMeasure_type,
    IFC4_IfcInterceptor_type,
    IFC4_IfcInterceptorType_type,
    IFC4_IfcInterceptorTypeEnum_type,
    IFC4_IfcInternalOrExternalEnum_type,
    IFC4_IfcIntersectionCurve_type,
    IFC4_IfcInventory_type,
    IFC4_IfcInventoryTypeEnum_type,
    IFC4_IfcIonConcentrationMeasure_type,
    IFC4_IfcIrregularTimeSeries_type,
    IFC4_IfcIrregularTimeSeriesValue_type,
    IFC4_IfcIShapeProfileDef_type,
    IFC4_IfcIsothermalMoistureCapacityMeasure_type,
    IFC4_IfcJunctionBox_type,
    IFC4_IfcJunctionBoxType_type,
    IFC4_IfcJunctionBoxTypeEnum_type,
    IFC4_IfcKinematicViscosityMeasure_type,
    IFC4_IfcKnotType_type,
    IFC4_IfcLabel_type,
    IFC4_IfcLaborResource_type,
    IFC4_IfcLaborResourceType_type,
    IFC4_IfcLaborResourceTypeEnum_type,
    IFC4_IfcLagTime_type,
    IFC4_IfcLamp_type,
    IFC4_IfcLampType_type,
    IFC4_IfcLampTypeEnum_type,
    IFC4_IfcLanguageId_type,
    IFC4_IfcLayeredItem_type,
    IFC4_IfcLayerSetDirectionEnum_type,
    IFC4_IfcLengthMeasure_type,
    IFC4_IfcLibraryInformation_type,
    IFC4_IfcLibraryReference_type,
    IFC4_IfcLibrarySelect_type,
    IFC4_IfcLightDistributionCurveEnum_type,
    IFC4_IfcLightDistributionData_type,
    IFC4_IfcLightDistributionDataSourceSelect_type,
    IFC4_IfcLightEmissionSourceEnum_type,
    IFC4_IfcLightFixture_type,
    IFC4_IfcLightFixtureType_type,
    IFC4_IfcLightFixtureTypeEnum_type,
    IFC4_IfcLightIntensityDistribution_type,
    IFC4_IfcLightSource_type,
    IFC4_IfcLightSourceAmbient_type,
    IFC4_IfcLightSourceDirectional_type,
    IFC4_IfcLightSourceGoniometric_type,
    IFC4_IfcLightSourcePositional_type,
    IFC4_IfcLightSourceSpot_type,
    IFC4_IfcLine_type,
    IFC4_IfcLinearForceMeasure_type,
    IFC4_IfcLinearMomentMeasure_type,
    IFC4_IfcLinearStiffnessMeasure_type,
    IFC4_IfcLinearVelocityMeasure_type,
    IFC4_IfcLineIndex_type,
    IFC4_IfcLoadGroupTypeEnum_type,
    IFC4_IfcLocalPlacement_type,
    IFC4_IfcLogical_type,
    IFC4_IfcLogicalOperatorEnum_type,
    IFC4_IfcLoop_type,
    IFC4_IfcLShapeProfileDef_type,
    IFC4_IfcLuminousFluxMeasure_type,
    IFC4_IfcLuminousIntensityDistributionMeasure_type,
    IFC4_IfcLuminousIntensityMeasure_type,
    IFC4_IfcMagneticFluxDensityMeasure_type,
    IFC4_IfcMagneticFluxMeasure_type,
    IFC4_IfcManifoldSolidBrep_type,
    IFC4_IfcMapConversion_type,
    IFC4_IfcMappedItem_type,
    IFC4_IfcMassDensityMeasure_type,
    IFC4_IfcMassFlowRateMeasure_type,
    IFC4_IfcMassMeasure_type,
    IFC4_IfcMassPerLengthMeasure_type,
    IFC4_IfcMaterial_type,
    IFC4_IfcMaterialClassificationRelationship_type,
    IFC4_IfcMaterialConstituent_type,
    IFC4_IfcMaterialConstituentSet_type,
    IFC4_IfcMaterialDefinition_type,
    IFC4_IfcMaterialDefinitionRepresentation_type,
    IFC4_IfcMaterialLayer_type,
    IFC4_IfcMaterialLayerSet_type,
    IFC4_IfcMaterialLayerSetUsage_type,
    IFC4_IfcMaterialLayerWithOffsets_type,
    IFC4_IfcMaterialList_type,
    IFC4_IfcMaterialProfile_type,
    IFC4_IfcMaterialProfileSet_type,
    IFC4_IfcMaterialProfileSetUsage_type,
    IFC4_IfcMaterialProfileSetUsageTapering_type,
    IFC4_IfcMaterialProfileWithOffsets_type,
    IFC4_IfcMaterialProperties_type,
    IFC4_IfcMaterialRelationship_type,
    IFC4_IfcMaterialSelect_type,
    IFC4_IfcMaterialUsageDefinition_type,
    IFC4_IfcMeasureValue_type,
    IFC4_IfcMeasureWithUnit_type,
    IFC4_IfcMechanicalFastener_type,
    IFC4_IfcMechanicalFastenerType_type,
    IFC4_IfcMechanicalFastenerTypeEnum_type,
    IFC4_IfcMedicalDevice_type,
    IFC4_IfcMedicalDeviceType_type,
    IFC4_IfcMedicalDeviceTypeEnum_type,
    IFC4_IfcMember_type,
    IFC4_IfcMemberStandardCase_type,
    IFC4_IfcMemberType_type,
    IFC4_IfcMemberTypeEnum_type,
    IFC4_IfcMetric_type,
    IFC4_IfcMetricValueSelect_type,
    IFC4_IfcMirroredProfileDef_type,
    IFC4_IfcModulusOfElasticityMeasure_type,
    IFC4_IfcModulusOfLinearSubgradeReactionMeasure_type,
    IFC4_IfcModulusOfRotationalSubgradeReactionMeasure_type,
    IFC4_IfcModulusOfRotationalSubgradeReactionSelect_type,
    IFC4_IfcModulusOfSubgradeReactionMeasure_type,
    IFC4_IfcModulusOfSubgradeReactionSelect_type,
    IFC4_IfcModulusOfTranslationalSubgradeReactionSelect_type,
    IFC4_IfcMoistureDiffusivityMeasure_type,
    IFC4_IfcMolecularWeightMeasure_type,
    IFC4_IfcMomentOfInertiaMeasure_type,
    IFC4_IfcMonetaryMeasure_type,
    IFC4_IfcMonetaryUnit_type,
    IFC4_IfcMonthInYearNumber_type,
    IFC4_IfcMotorConnection_type,
    IFC4_IfcMotorConnectionType_type,
    IFC4_IfcMotorConnectionTypeEnum_type,
    IFC4_IfcNamedUnit_type,
    IFC4_IfcNonNegativeLengthMeasure_type,
    IFC4_IfcNormalisedRatioMeasure_type,
    IFC4_IfcNullStyle_type,
    IFC4_IfcNumericMeasure_type,
    IFC4_IfcObject_type,
    IFC4_IfcObjectDefinition_type,
    IFC4_IfcObjective_type,
    IFC4_IfcObjectiveEnum_type,
    IFC4_IfcObjectPlacement_type,
    IFC4_IfcObjectReferenceSelect_type,
    IFC4_IfcObjectTypeEnum_type,
    IFC4_IfcOccupant_type,
    IFC4_IfcOccupantTypeEnum_type,
    IFC4_IfcOffsetCurve2D_type,
    IFC4_IfcOffsetCurve3D_type,
    IFC4_IfcOpeningElement_type,
    IFC4_IfcOpeningElementTypeEnum_type,
    IFC4_IfcOpeningStandardCase_type,
    IFC4_IfcOpenShell_type,
    IFC4_IfcOrganization_type,
    IFC4_IfcOrganizationRelationship_type,
    IFC4_IfcOrientedEdge_type,
    IFC4_IfcOuterBoundaryCurve_type,
    IFC4_IfcOutlet_type,
    IFC4_IfcOutletType_type,
    IFC4_IfcOutletTypeEnum_type,
    IFC4_IfcOwnerHistory_type,
    IFC4_IfcParameterizedProfileDef_type,
    IFC4_IfcParameterValue_type,
    IFC4_IfcPath_type,
    IFC4_IfcPcurve_type,
    IFC4_IfcPerformanceHistory_type,
    IFC4_IfcPerformanceHistoryTypeEnum_type,
    IFC4_IfcPermeableCoveringOperationEnum_type,
    IFC4_IfcPermeableCoveringProperties_type,
    IFC4_IfcPermit_type,
    IFC4_IfcPermitTypeEnum_type,
    IFC4_IfcPerson_type,
    IFC4_IfcPersonAndOrganization_type,
    IFC4_IfcPHMeasure_type,
    IFC4_IfcPhysicalComplexQuantity_type,
    IFC4_IfcPhysicalOrVirtualEnum_type,
    IFC4_IfcPhysicalQuantity_type,
    IFC4_IfcPhysicalSimpleQuantity_type,
    IFC4_IfcPile_type,
    IFC4_IfcPileConstructionEnum_type,
    IFC4_IfcPileType_type,
    IFC4_IfcPileTypeEnum_type,
    IFC4_IfcPipeFitting_type,
    IFC4_IfcPipeFittingType_type,
    IFC4_IfcPipeFittingTypeEnum_type,
    IFC4_IfcPipeSegment_type,
    IFC4_IfcPipeSegmentType_type,
    IFC4_IfcPipeSegmentTypeEnum_type,
    IFC4_IfcPixelTexture_type,
    IFC4_IfcPlacement_type,
    IFC4_IfcPlanarBox_type,
    IFC4_IfcPlanarExtent_type,
    IFC4_IfcPlanarForceMeasure_type,
    IFC4_IfcPlane_type,
    IFC4_IfcPlaneAngleMeasure_type,
    IFC4_IfcPlate_type,
    IFC4_IfcPlateStandardCase_type,
    IFC4_IfcPlateType_type,
    IFC4_IfcPlateTypeEnum_type,
    IFC4_IfcPoint_type,
    IFC4_IfcPointOnCurve_type,
    IFC4_IfcPointOnSurface_type,
    IFC4_IfcPointOrVertexPoint_type,
    IFC4_IfcPolygonalBoundedHalfSpace_type,
    IFC4_IfcPolygonalFaceSet_type,
    IFC4_IfcPolyline_type,
    IFC4_IfcPolyLoop_type,
    IFC4_IfcPort_type,
    IFC4_IfcPositiveInteger_type,
    IFC4_IfcPositiveLengthMeasure_type,
    IFC4_IfcPositivePlaneAngleMeasure_type,
    IFC4_IfcPositiveRatioMeasure_type,
    IFC4_IfcPostalAddress_type,
    IFC4_IfcPowerMeasure_type,
    IFC4_IfcPreDefinedColour_type,
    IFC4_IfcPreDefinedCurveFont_type,
    IFC4_IfcPreDefinedItem_type,
    IFC4_IfcPreDefinedProperties_type,
    IFC4_IfcPreDefinedPropertySet_type,
    IFC4_IfcPreDefinedTextFont_type,
    IFC4_IfcPreferredSurfaceCurveRepresentation_type,
    IFC4_IfcPresentableText_type,
    IFC4_IfcPresentationItem_type,
    IFC4_IfcPresentationLayerAssignment_type,
    IFC4_IfcPresentationLayerWithStyle_type,
    IFC4_IfcPresentationStyle_type,
    IFC4_IfcPresentationStyleAssignment_type,
    IFC4_IfcPresentationStyleSelect_type,
    IFC4_IfcPressureMeasure_type,
    IFC4_IfcProcedure_type,
    IFC4_IfcProcedureType_type,
    IFC4_IfcProcedureTypeEnum_type,
    IFC4_IfcProcess_type,
    IFC4_IfcProcessSelect_type,
    IFC4_IfcProduct_type,
    IFC4_IfcProductDefinitionShape_type,
    IFC4_IfcProductRepresentation_type,
    IFC4_IfcProductRepresentationSelect_type,
    IFC4_IfcProductSelect_type,
    IFC4_IfcProfileDef_type,
    IFC4_IfcProfileProperties_type,
    IFC4_IfcProfileTypeEnum_type,
    IFC4_IfcProject_type,
    IFC4_IfcProjectedCRS_type,
    IFC4_IfcProjectedOrTrueLengthEnum_type,
    IFC4_IfcProjectionElement_type,
    IFC4_IfcProjectionElementTypeEnum_type,
    IFC4_IfcProjectLibrary_type,
    IFC4_IfcProjectOrder_type,
    IFC4_IfcProjectOrderTypeEnum_type,
    IFC4_IfcProperty_type,
    IFC4_IfcPropertyAbstraction_type,
    IFC4_IfcPropertyBoundedValue_type,
    IFC4_IfcPropertyDefinition_type,
    IFC4_IfcPropertyDependencyRelationship_type,
    IFC4_IfcPropertyEnumeratedValue_type,
    IFC4_IfcPropertyEnumeration_type,
    IFC4_IfcPropertyListValue_type,
    IFC4_IfcPropertyReferenceValue_type,
    IFC4_IfcPropertySet_type,
    IFC4_IfcPropertySetDefinition_type,
    IFC4_IfcPropertySetDefinitionSelect_type,
    IFC4_IfcPropertySetDefinitionSet_type,
    IFC4_IfcPropertySetTemplate_type,
    IFC4_IfcPropertySetTemplateTypeEnum_type,
    IFC4_IfcPropertySingleValue_type,
    IFC4_IfcPropertyTableValue_type,
    IFC4_IfcPropertyTemplate_type,
    IFC4_IfcPropertyTemplateDefinition_type,
    IFC4_IfcProtectiveDevice_type,
    IFC4_IfcProtectiveDeviceTrippingUnit_type,
    IFC4_IfcProtectiveDeviceTrippingUnitType_type,
    IFC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type,
    IFC4_IfcProtectiveDeviceType_type,
    IFC4_IfcProtectiveDeviceTypeEnum_type,
    IFC4_IfcProxy_type,
    IFC4_IfcPump_type,
    IFC4_IfcPumpType_type,
    IFC4_IfcPumpTypeEnum_type,
    IFC4_IfcQuantityArea_type,
    IFC4_IfcQuantityCount_type,
    IFC4_IfcQuantityLength_type,
    IFC4_IfcQuantitySet_type,
    IFC4_IfcQuantityTime_type,
    IFC4_IfcQuantityVolume_type,
    IFC4_IfcQuantityWeight_type,
    IFC4_IfcRadioActivityMeasure_type,
    IFC4_IfcRailing_type,
    IFC4_IfcRailingType_type,
    IFC4_IfcRailingTypeEnum_type,
    IFC4_IfcRamp_type,
    IFC4_IfcRampFlight_type,
    IFC4_IfcRampFlightType_type,
    IFC4_IfcRampFlightTypeEnum_type,
    IFC4_IfcRampType_type,
    IFC4_IfcRampTypeEnum_type,
    IFC4_IfcRatioMeasure_type,
    IFC4_IfcRationalBSplineCurveWithKnots_type,
    IFC4_IfcRationalBSplineSurfaceWithKnots_type,
    IFC4_IfcReal_type,
    IFC4_IfcRectangleHollowProfileDef_type,
    IFC4_IfcRectangleProfileDef_type,
    IFC4_IfcRectangularPyramid_type,
    IFC4_IfcRectangularTrimmedSurface_type,
    IFC4_IfcRecurrencePattern_type,
    IFC4_IfcRecurrenceTypeEnum_type,
    IFC4_IfcReference_type,
    IFC4_IfcReflectanceMethodEnum_type,
    IFC4_IfcRegularTimeSeries_type,
    IFC4_IfcReinforcementBarProperties_type,
    IFC4_IfcReinforcementDefinitionProperties_type,
    IFC4_IfcReinforcingBar_type,
    IFC4_IfcReinforcingBarRoleEnum_type,
    IFC4_IfcReinforcingBarSurfaceEnum_type,
    IFC4_IfcReinforcingBarType_type,
    IFC4_IfcReinforcingBarTypeEnum_type,
    IFC4_IfcReinforcingElement_type,
    IFC4_IfcReinforcingElementType_type,
    IFC4_IfcReinforcingMesh_type,
    IFC4_IfcReinforcingMeshType_type,
    IFC4_IfcReinforcingMeshTypeEnum_type,
    IFC4_IfcRelAggregates_type,
    IFC4_IfcRelAssigns_type,
    IFC4_IfcRelAssignsToActor_type,
    IFC4_IfcRelAssignsToControl_type,
    IFC4_IfcRelAssignsToGroup_type,
    IFC4_IfcRelAssignsToGroupByFactor_type,
    IFC4_IfcRelAssignsToProcess_type,
    IFC4_IfcRelAssignsToProduct_type,
    IFC4_IfcRelAssignsToResource_type,
    IFC4_IfcRelAssociates_type,
    IFC4_IfcRelAssociatesApproval_type,
    IFC4_IfcRelAssociatesClassification_type,
    IFC4_IfcRelAssociatesConstraint_type,
    IFC4_IfcRelAssociatesDocument_type,
    IFC4_IfcRelAssociatesLibrary_type,
    IFC4_IfcRelAssociatesMaterial_type,
    IFC4_IfcRelationship_type,
    IFC4_IfcRelConnects_type,
    IFC4_IfcRelConnectsElements_type,
    IFC4_IfcRelConnectsPathElements_type,
    IFC4_IfcRelConnectsPorts_type,
    IFC4_IfcRelConnectsPortToElement_type,
    IFC4_IfcRelConnectsStructuralActivity_type,
    IFC4_IfcRelConnectsStructuralMember_type,
    IFC4_IfcRelConnectsWithEccentricity_type,
    IFC4_IfcRelConnectsWithRealizingElements_type,
    IFC4_IfcRelContainedInSpatialStructure_type,
    IFC4_IfcRelCoversBldgElements_type,
    IFC4_IfcRelCoversSpaces_type,
    IFC4_IfcRelDeclares_type,
    IFC4_IfcRelDecomposes_type,
    IFC4_IfcRelDefines_type,
    IFC4_IfcRelDefinesByObject_type,
    IFC4_IfcRelDefinesByProperties_type,
    IFC4_IfcRelDefinesByTemplate_type,
    IFC4_IfcRelDefinesByType_type,
    IFC4_IfcRelFillsElement_type,
    IFC4_IfcRelFlowControlElements_type,
    IFC4_IfcRelInterferesElements_type,
    IFC4_IfcRelNests_type,
    IFC4_IfcRelProjectsElement_type,
    IFC4_IfcRelReferencedInSpatialStructure_type,
    IFC4_IfcRelSequence_type,
    IFC4_IfcRelServicesBuildings_type,
    IFC4_IfcRelSpaceBoundary_type,
    IFC4_IfcRelSpaceBoundary1stLevel_type,
    IFC4_IfcRelSpaceBoundary2ndLevel_type,
    IFC4_IfcRelVoidsElement_type,
    IFC4_IfcReparametrisedCompositeCurveSegment_type,
    IFC4_IfcRepresentation_type,
    IFC4_IfcRepresentationContext_type,
    IFC4_IfcRepresentationItem_type,
    IFC4_IfcRepresentationMap_type,
    IFC4_IfcResource_type,
    IFC4_IfcResourceApprovalRelationship_type,
    IFC4_IfcResourceConstraintRelationship_type,
    IFC4_IfcResourceLevelRelationship_type,
    IFC4_IfcResourceObjectSelect_type,
    IFC4_IfcResourceSelect_type,
    IFC4_IfcResourceTime_type,
    IFC4_IfcRevolvedAreaSolid_type,
    IFC4_IfcRevolvedAreaSolidTapered_type,
    IFC4_IfcRightCircularCone_type,
    IFC4_IfcRightCircularCylinder_type,
    IFC4_IfcRoleEnum_type,
    IFC4_IfcRoof_type,
    IFC4_IfcRoofType_type,
    IFC4_IfcRoofTypeEnum_type,
    IFC4_IfcRoot_type,
    IFC4_IfcRotationalFrequencyMeasure_type,
    IFC4_IfcRotationalMassMeasure_type,
    IFC4_IfcRotationalStiffnessMeasure_type,
    IFC4_IfcRotationalStiffnessSelect_type,
    IFC4_IfcRoundedRectangleProfileDef_type,
    IFC4_IfcSanitaryTerminal_type,
    IFC4_IfcSanitaryTerminalType_type,
    IFC4_IfcSanitaryTerminalTypeEnum_type,
    IFC4_IfcSchedulingTime_type,
    IFC4_IfcSeamCurve_type,
    IFC4_IfcSectionalAreaIntegralMeasure_type,
    IFC4_IfcSectionedSpine_type,
    IFC4_IfcSectionModulusMeasure_type,
    IFC4_IfcSectionProperties_type,
    IFC4_IfcSectionReinforcementProperties_type,
    IFC4_IfcSectionTypeEnum_type,
    IFC4_IfcSegmentIndexSelect_type,
    IFC4_IfcSensor_type,
    IFC4_IfcSensorType_type,
    IFC4_IfcSensorTypeEnum_type,
    IFC4_IfcSequenceEnum_type,
    IFC4_IfcShadingDevice_type,
    IFC4_IfcShadingDeviceType_type,
    IFC4_IfcShadingDeviceTypeEnum_type,
    IFC4_IfcShapeAspect_type,
    IFC4_IfcShapeModel_type,
    IFC4_IfcShapeRepresentation_type,
    IFC4_IfcShearModulusMeasure_type,
    IFC4_IfcShell_type,
    IFC4_IfcShellBasedSurfaceModel_type,
    IFC4_IfcSimpleProperty_type,
    IFC4_IfcSimplePropertyTemplate_type,
    IFC4_IfcSimplePropertyTemplateTypeEnum_type,
    IFC4_IfcSimpleValue_type,
    IFC4_IfcSIPrefix_type,
    IFC4_IfcSite_type,
    IFC4_IfcSIUnit_type,
    IFC4_IfcSIUnitName_type,
    IFC4_IfcSizeSelect_type,
    IFC4_IfcSlab_type,
    IFC4_IfcSlabElementedCase_type,
    IFC4_IfcSlabStandardCase_type,
    IFC4_IfcSlabType_type,
    IFC4_IfcSlabTypeEnum_type,
    IFC4_IfcSlippageConnectionCondition_type,
    IFC4_IfcSolarDevice_type,
    IFC4_IfcSolarDeviceType_type,
    IFC4_IfcSolarDeviceTypeEnum_type,
    IFC4_IfcSolidAngleMeasure_type,
    IFC4_IfcSolidModel_type,
    IFC4_IfcSolidOrShell_type,
    IFC4_IfcSoundPowerLevelMeasure_type,
    IFC4_IfcSoundPowerMeasure_type,
    IFC4_IfcSoundPressureLevelMeasure_type,
    IFC4_IfcSoundPressureMeasure_type,
    IFC4_IfcSpace_type,
    IFC4_IfcSpaceBoundarySelect_type,
    IFC4_IfcSpaceHeater_type,
    IFC4_IfcSpaceHeaterType_type,
    IFC4_IfcSpaceHeaterTypeEnum_type,
    IFC4_IfcSpaceType_type,
    IFC4_IfcSpaceTypeEnum_type,
    IFC4_IfcSpatialElement_type,
    IFC4_IfcSpatialElementType_type,
    IFC4_IfcSpatialStructureElement_type,
    IFC4_IfcSpatialStructureElementType_type,
    IFC4_IfcSpatialZone_type,
    IFC4_IfcSpatialZoneType_type,
    IFC4_IfcSpatialZoneTypeEnum_type,
    IFC4_IfcSpecificHeatCapacityMeasure_type,
    IFC4_IfcSpecularExponent_type,
    IFC4_IfcSpecularHighlightSelect_type,
    IFC4_IfcSpecularRoughness_type,
    IFC4_IfcSphere_type,
    IFC4_IfcSphericalSurface_type,
    IFC4_IfcStackTerminal_type,
    IFC4_IfcStackTerminalType_type,
    IFC4_IfcStackTerminalTypeEnum_type,
    IFC4_IfcStair_type,
    IFC4_IfcStairFlight_type,
    IFC4_IfcStairFlightType_type,
    IFC4_IfcStairFlightTypeEnum_type,
    IFC4_IfcStairType_type,
    IFC4_IfcStairTypeEnum_type,
    IFC4_IfcStateEnum_type,
    IFC4_IfcStructuralAction_type,
    IFC4_IfcStructuralActivity_type,
    IFC4_IfcStructuralActivityAssignmentSelect_type,
    IFC4_IfcStructuralAnalysisModel_type,
    IFC4_IfcStructuralConnection_type,
    IFC4_IfcStructuralConnectionCondition_type,
    IFC4_IfcStructuralCurveAction_type,
    IFC4_IfcStructuralCurveActivityTypeEnum_type,
    IFC4_IfcStructuralCurveConnection_type,
    IFC4_IfcStructuralCurveMember_type,
    IFC4_IfcStructuralCurveMemberTypeEnum_type,
    IFC4_IfcStructuralCurveMemberVarying_type,
    IFC4_IfcStructuralCurveReaction_type,
    IFC4_IfcStructuralItem_type,
    IFC4_IfcStructuralLinearAction_type,
    IFC4_IfcStructuralLoad_type,
    IFC4_IfcStructuralLoadCase_type,
    IFC4_IfcStructuralLoadConfiguration_type,
    IFC4_IfcStructuralLoadGroup_type,
    IFC4_IfcStructuralLoadLinearForce_type,
    IFC4_IfcStructuralLoadOrResult_type,
    IFC4_IfcStructuralLoadPlanarForce_type,
    IFC4_IfcStructuralLoadSingleDisplacement_type,
    IFC4_IfcStructuralLoadSingleDisplacementDistortion_type,
    IFC4_IfcStructuralLoadSingleForce_type,
    IFC4_IfcStructuralLoadSingleForceWarping_type,
    IFC4_IfcStructuralLoadStatic_type,
    IFC4_IfcStructuralLoadTemperature_type,
    IFC4_IfcStructuralMember_type,
    IFC4_IfcStructuralPlanarAction_type,
    IFC4_IfcStructuralPointAction_type,
    IFC4_IfcStructuralPointConnection_type,
    IFC4_IfcStructuralPointReaction_type,
    IFC4_IfcStructuralReaction_type,
    IFC4_IfcStructuralResultGroup_type,
    IFC4_IfcStructuralSurfaceAction_type,
    IFC4_IfcStructuralSurfaceActivityTypeEnum_type,
    IFC4_IfcStructuralSurfaceConnection_type,
    IFC4_IfcStructuralSurfaceMember_type,
    IFC4_IfcStructuralSurfaceMemberTypeEnum_type,
    IFC4_IfcStructuralSurfaceMemberVarying_type,
    IFC4_IfcStructuralSurfaceReaction_type,
    IFC4_IfcStyleAssignmentSelect_type,
    IFC4_IfcStyledItem_type,
    IFC4_IfcStyledRepresentation_type,
    IFC4_IfcStyleModel_type,
    IFC4_IfcSubContractResource_type,
    IFC4_IfcSubContractResourceType_type,
    IFC4_IfcSubContractResourceTypeEnum_type,
    IFC4_IfcSubedge_type,
    IFC4_IfcSurface_type,
    IFC4_IfcSurfaceCurve_type,
    IFC4_IfcSurfaceCurveSweptAreaSolid_type,
    IFC4_IfcSurfaceFeature_type,
    IFC4_IfcSurfaceFeatureTypeEnum_type,
    IFC4_IfcSurfaceOfLinearExtrusion_type,
    IFC4_IfcSurfaceOfRevolution_type,
    IFC4_IfcSurfaceOrFaceSurface_type,
    IFC4_IfcSurfaceReinforcementArea_type,
    IFC4_IfcSurfaceSide_type,
    IFC4_IfcSurfaceStyle_type,
    IFC4_IfcSurfaceStyleElementSelect_type,
    IFC4_IfcSurfaceStyleLighting_type,
    IFC4_IfcSurfaceStyleRefraction_type,
    IFC4_IfcSurfaceStyleRendering_type,
    IFC4_IfcSurfaceStyleShading_type,
    IFC4_IfcSurfaceStyleWithTextures_type,
    IFC4_IfcSurfaceTexture_type,
    IFC4_IfcSweptAreaSolid_type,
    IFC4_IfcSweptDiskSolid_type,
    IFC4_IfcSweptDiskSolidPolygonal_type,
    IFC4_IfcSweptSurface_type,
    IFC4_IfcSwitchingDevice_type,
    IFC4_IfcSwitchingDeviceType_type,
    IFC4_IfcSwitchingDeviceTypeEnum_type,
    IFC4_IfcSystem_type,
    IFC4_IfcSystemFurnitureElement_type,
    IFC4_IfcSystemFurnitureElementType_type,
    IFC4_IfcSystemFurnitureElementTypeEnum_type,
    IFC4_IfcTable_type,
    IFC4_IfcTableColumn_type,
    IFC4_IfcTableRow_type,
    IFC4_IfcTank_type,
    IFC4_IfcTankType_type,
    IFC4_IfcTankTypeEnum_type,
    IFC4_IfcTask_type,
    IFC4_IfcTaskDurationEnum_type,
    IFC4_IfcTaskTime_type,
    IFC4_IfcTaskTimeRecurring_type,
    IFC4_IfcTaskType_type,
    IFC4_IfcTaskTypeEnum_type,
    IFC4_IfcTelecomAddress_type,
    IFC4_IfcTemperatureGradientMeasure_type,
    IFC4_IfcTemperatureRateOfChangeMeasure_type,
    IFC4_IfcTendon_type,
    IFC4_IfcTendonAnchor_type,
    IFC4_IfcTendonAnchorType_type,
    IFC4_IfcTendonAnchorTypeEnum_type,
    IFC4_IfcTendonType_type,
    IFC4_IfcTendonTypeEnum_type,
    IFC4_IfcTessellatedFaceSet_type,
    IFC4_IfcTessellatedItem_type,
    IFC4_IfcText_type,
    IFC4_IfcTextAlignment_type,
    IFC4_IfcTextDecoration_type,
    IFC4_IfcTextFontName_type,
    IFC4_IfcTextFontSelect_type,
    IFC4_IfcTextLiteral_type,
    IFC4_IfcTextLiteralWithExtent_type,
    IFC4_IfcTextPath_type,
    IFC4_IfcTextStyle_type,
    IFC4_IfcTextStyleFontModel_type,
    IFC4_IfcTextStyleForDefinedFont_type,
    IFC4_IfcTextStyleTextModel_type,
    IFC4_IfcTextTransformation_type,
    IFC4_IfcTextureCoordinate_type,
    IFC4_IfcTextureCoordinateGenerator_type,
    IFC4_IfcTextureMap_type,
    IFC4_IfcTextureVertex_type,
    IFC4_IfcTextureVertexList_type,
    IFC4_IfcThermalAdmittanceMeasure_type,
    IFC4_IfcThermalConductivityMeasure_type,
    IFC4_IfcThermalExpansionCoefficientMeasure_type,
    IFC4_IfcThermalResistanceMeasure_type,
    IFC4_IfcThermalTransmittanceMeasure_type,
    IFC4_IfcThermodynamicTemperatureMeasure_type,
    IFC4_IfcTime_type,
    IFC4_IfcTimeMeasure_type,
    IFC4_IfcTimeOrRatioSelect_type,
    IFC4_IfcTimePeriod_type,
    IFC4_IfcTimeSeries_type,
    IFC4_IfcTimeSeriesDataTypeEnum_type,
    IFC4_IfcTimeSeriesValue_type,
    IFC4_IfcTimeStamp_type,
    IFC4_IfcTopologicalRepresentationItem_type,
    IFC4_IfcTopologyRepresentation_type,
    IFC4_IfcToroidalSurface_type,
    IFC4_IfcTorqueMeasure_type,
    IFC4_IfcTransformer_type,
    IFC4_IfcTransformerType_type,
    IFC4_IfcTransformerTypeEnum_type,
    IFC4_IfcTransitionCode_type,
    IFC4_IfcTranslationalStiffnessSelect_type,
    IFC4_IfcTransportElement_type,
    IFC4_IfcTransportElementType_type,
    IFC4_IfcTransportElementTypeEnum_type,
    IFC4_IfcTrapeziumProfileDef_type,
    IFC4_IfcTriangulatedFaceSet_type,
    IFC4_IfcTrimmedCurve_type,
    IFC4_IfcTrimmingPreference_type,
    IFC4_IfcTrimmingSelect_type,
    IFC4_IfcTShapeProfileDef_type,
    IFC4_IfcTubeBundle_type,
    IFC4_IfcTubeBundleType_type,
    IFC4_IfcTubeBundleTypeEnum_type,
    IFC4_IfcTypeObject_type,
    IFC4_IfcTypeProcess_type,
    IFC4_IfcTypeProduct_type,
    IFC4_IfcTypeResource_type,
    IFC4_IfcUnit_type,
    IFC4_IfcUnitaryControlElement_type,
    IFC4_IfcUnitaryControlElementType_type,
    IFC4_IfcUnitaryControlElementTypeEnum_type,
    IFC4_IfcUnitaryEquipment_type,
    IFC4_IfcUnitaryEquipmentType_type,
    IFC4_IfcUnitaryEquipmentTypeEnum_type,
    IFC4_IfcUnitAssignment_type,
    IFC4_IfcUnitEnum_type,
    IFC4_IfcURIReference_type,
    IFC4_IfcUShapeProfileDef_type,
    IFC4_IfcValue_type,
    IFC4_IfcValve_type,
    IFC4_IfcValveType_type,
    IFC4_IfcValveTypeEnum_type,
    IFC4_IfcVaporPermeabilityMeasure_type,
    IFC4_IfcVector_type,
    IFC4_IfcVectorOrDirection_type,
    IFC4_IfcVertex_type,
    IFC4_IfcVertexLoop_type,
    IFC4_IfcVertexPoint_type,
    IFC4_IfcVibrationIsolator_type,
    IFC4_IfcVibrationIsolatorType_type,
    IFC4_IfcVibrationIsolatorTypeEnum_type,
    IFC4_IfcVirtualElement_type,
    IFC4_IfcVirtualGridIntersection_type,
    IFC4_IfcVoidingFeature_type,
    IFC4_IfcVoidingFeatureTypeEnum_type,
    IFC4_IfcVolumeMeasure_type,
    IFC4_IfcVolumetricFlowRateMeasure_type,
    IFC4_IfcWall_type,
    IFC4_IfcWallElementedCase_type,
    IFC4_IfcWallStandardCase_type,
    IFC4_IfcWallType_type,
    IFC4_IfcWallTypeEnum_type,
    IFC4_IfcWarpingConstantMeasure_type,
    IFC4_IfcWarpingMomentMeasure_type,
    IFC4_IfcWarpingStiffnessSelect_type,
    IFC4_IfcWasteTerminal_type,
    IFC4_IfcWasteTerminalType_type,
    IFC4_IfcWasteTerminalTypeEnum_type,
    IFC4_IfcWindow_type,
    IFC4_IfcWindowLiningProperties_type,
    IFC4_IfcWindowPanelOperationEnum_type,
    IFC4_IfcWindowPanelPositionEnum_type,
    IFC4_IfcWindowPanelProperties_type,
    IFC4_IfcWindowStandardCase_type,
    IFC4_IfcWindowStyle_type,
    IFC4_IfcWindowStyleConstructionEnum_type,
    IFC4_IfcWindowStyleOperationEnum_type,
    IFC4_IfcWindowType_type,
    IFC4_IfcWindowTypeEnum_type,
    IFC4_IfcWindowTypePartitioningEnum_type,
    IFC4_IfcWorkCalendar_type,
    IFC4_IfcWorkCalendarTypeEnum_type,
    IFC4_IfcWorkControl_type,
    IFC4_IfcWorkPlan_type,
    IFC4_IfcWorkPlanTypeEnum_type,
    IFC4_IfcWorkSchedule_type,
    IFC4_IfcWorkScheduleTypeEnum_type,
    IFC4_IfcWorkTime_type,
    IFC4_IfcZone_type,
    IFC4_IfcZShapeProfileDef_type
        };
    return new schema_definition(strings[3306], declarations, new IFC4_instance_factory());
}


#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC pop_options
#elif defined(_MSC_VER)
#pragma optimize("", on)
#endif
        
static std::unique_ptr<schema_definition> schema;

void Ifc4::clear_schema() {
    schema.reset();
}

const schema_definition& Ifc4::get_schema() {
    if (!schema) {
        schema.reset(IFC4_populate_schema());
    }
    return *schema;
}

