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
 * This file has been generated from IFC4x1.exp. Do not make modifications      *
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/

#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/Ifc4x1.h"

using namespace IfcParse;

entity* IFC4X1_IfcActionRequest_type = 0;
entity* IFC4X1_IfcActor_type = 0;
entity* IFC4X1_IfcActorRole_type = 0;
entity* IFC4X1_IfcActuator_type = 0;
entity* IFC4X1_IfcActuatorType_type = 0;
entity* IFC4X1_IfcAddress_type = 0;
entity* IFC4X1_IfcAdvancedBrep_type = 0;
entity* IFC4X1_IfcAdvancedBrepWithVoids_type = 0;
entity* IFC4X1_IfcAdvancedFace_type = 0;
entity* IFC4X1_IfcAirTerminal_type = 0;
entity* IFC4X1_IfcAirTerminalBox_type = 0;
entity* IFC4X1_IfcAirTerminalBoxType_type = 0;
entity* IFC4X1_IfcAirTerminalType_type = 0;
entity* IFC4X1_IfcAirToAirHeatRecovery_type = 0;
entity* IFC4X1_IfcAirToAirHeatRecoveryType_type = 0;
entity* IFC4X1_IfcAlarm_type = 0;
entity* IFC4X1_IfcAlarmType_type = 0;
entity* IFC4X1_IfcAlignment_type = 0;
entity* IFC4X1_IfcAlignment2DHorizontal_type = 0;
entity* IFC4X1_IfcAlignment2DHorizontalSegment_type = 0;
entity* IFC4X1_IfcAlignment2DSegment_type = 0;
entity* IFC4X1_IfcAlignment2DVerSegCircularArc_type = 0;
entity* IFC4X1_IfcAlignment2DVerSegLine_type = 0;
entity* IFC4X1_IfcAlignment2DVerSegParabolicArc_type = 0;
entity* IFC4X1_IfcAlignment2DVertical_type = 0;
entity* IFC4X1_IfcAlignment2DVerticalSegment_type = 0;
entity* IFC4X1_IfcAlignmentCurve_type = 0;
entity* IFC4X1_IfcAnnotation_type = 0;
entity* IFC4X1_IfcAnnotationFillArea_type = 0;
entity* IFC4X1_IfcApplication_type = 0;
entity* IFC4X1_IfcAppliedValue_type = 0;
entity* IFC4X1_IfcApproval_type = 0;
entity* IFC4X1_IfcApprovalRelationship_type = 0;
entity* IFC4X1_IfcArbitraryClosedProfileDef_type = 0;
entity* IFC4X1_IfcArbitraryOpenProfileDef_type = 0;
entity* IFC4X1_IfcArbitraryProfileDefWithVoids_type = 0;
entity* IFC4X1_IfcAsset_type = 0;
entity* IFC4X1_IfcAsymmetricIShapeProfileDef_type = 0;
entity* IFC4X1_IfcAudioVisualAppliance_type = 0;
entity* IFC4X1_IfcAudioVisualApplianceType_type = 0;
entity* IFC4X1_IfcAxis1Placement_type = 0;
entity* IFC4X1_IfcAxis2Placement2D_type = 0;
entity* IFC4X1_IfcAxis2Placement3D_type = 0;
entity* IFC4X1_IfcBSplineCurve_type = 0;
entity* IFC4X1_IfcBSplineCurveWithKnots_type = 0;
entity* IFC4X1_IfcBSplineSurface_type = 0;
entity* IFC4X1_IfcBSplineSurfaceWithKnots_type = 0;
entity* IFC4X1_IfcBeam_type = 0;
entity* IFC4X1_IfcBeamStandardCase_type = 0;
entity* IFC4X1_IfcBeamType_type = 0;
entity* IFC4X1_IfcBlobTexture_type = 0;
entity* IFC4X1_IfcBlock_type = 0;
entity* IFC4X1_IfcBoiler_type = 0;
entity* IFC4X1_IfcBoilerType_type = 0;
entity* IFC4X1_IfcBooleanClippingResult_type = 0;
entity* IFC4X1_IfcBooleanResult_type = 0;
entity* IFC4X1_IfcBoundaryCondition_type = 0;
entity* IFC4X1_IfcBoundaryCurve_type = 0;
entity* IFC4X1_IfcBoundaryEdgeCondition_type = 0;
entity* IFC4X1_IfcBoundaryFaceCondition_type = 0;
entity* IFC4X1_IfcBoundaryNodeCondition_type = 0;
entity* IFC4X1_IfcBoundaryNodeConditionWarping_type = 0;
entity* IFC4X1_IfcBoundedCurve_type = 0;
entity* IFC4X1_IfcBoundedSurface_type = 0;
entity* IFC4X1_IfcBoundingBox_type = 0;
entity* IFC4X1_IfcBoxedHalfSpace_type = 0;
entity* IFC4X1_IfcBuilding_type = 0;
entity* IFC4X1_IfcBuildingElement_type = 0;
entity* IFC4X1_IfcBuildingElementPart_type = 0;
entity* IFC4X1_IfcBuildingElementPartType_type = 0;
entity* IFC4X1_IfcBuildingElementProxy_type = 0;
entity* IFC4X1_IfcBuildingElementProxyType_type = 0;
entity* IFC4X1_IfcBuildingElementType_type = 0;
entity* IFC4X1_IfcBuildingStorey_type = 0;
entity* IFC4X1_IfcBuildingSystem_type = 0;
entity* IFC4X1_IfcBurner_type = 0;
entity* IFC4X1_IfcBurnerType_type = 0;
entity* IFC4X1_IfcCShapeProfileDef_type = 0;
entity* IFC4X1_IfcCableCarrierFitting_type = 0;
entity* IFC4X1_IfcCableCarrierFittingType_type = 0;
entity* IFC4X1_IfcCableCarrierSegment_type = 0;
entity* IFC4X1_IfcCableCarrierSegmentType_type = 0;
entity* IFC4X1_IfcCableFitting_type = 0;
entity* IFC4X1_IfcCableFittingType_type = 0;
entity* IFC4X1_IfcCableSegment_type = 0;
entity* IFC4X1_IfcCableSegmentType_type = 0;
entity* IFC4X1_IfcCartesianPoint_type = 0;
entity* IFC4X1_IfcCartesianPointList_type = 0;
entity* IFC4X1_IfcCartesianPointList2D_type = 0;
entity* IFC4X1_IfcCartesianPointList3D_type = 0;
entity* IFC4X1_IfcCartesianTransformationOperator_type = 0;
entity* IFC4X1_IfcCartesianTransformationOperator2D_type = 0;
entity* IFC4X1_IfcCartesianTransformationOperator2DnonUniform_type = 0;
entity* IFC4X1_IfcCartesianTransformationOperator3D_type = 0;
entity* IFC4X1_IfcCartesianTransformationOperator3DnonUniform_type = 0;
entity* IFC4X1_IfcCenterLineProfileDef_type = 0;
entity* IFC4X1_IfcChiller_type = 0;
entity* IFC4X1_IfcChillerType_type = 0;
entity* IFC4X1_IfcChimney_type = 0;
entity* IFC4X1_IfcChimneyType_type = 0;
entity* IFC4X1_IfcCircle_type = 0;
entity* IFC4X1_IfcCircleHollowProfileDef_type = 0;
entity* IFC4X1_IfcCircleProfileDef_type = 0;
entity* IFC4X1_IfcCircularArcSegment2D_type = 0;
entity* IFC4X1_IfcCivilElement_type = 0;
entity* IFC4X1_IfcCivilElementType_type = 0;
entity* IFC4X1_IfcClassification_type = 0;
entity* IFC4X1_IfcClassificationReference_type = 0;
entity* IFC4X1_IfcClosedShell_type = 0;
entity* IFC4X1_IfcCoil_type = 0;
entity* IFC4X1_IfcCoilType_type = 0;
entity* IFC4X1_IfcColourRgb_type = 0;
entity* IFC4X1_IfcColourRgbList_type = 0;
entity* IFC4X1_IfcColourSpecification_type = 0;
entity* IFC4X1_IfcColumn_type = 0;
entity* IFC4X1_IfcColumnStandardCase_type = 0;
entity* IFC4X1_IfcColumnType_type = 0;
entity* IFC4X1_IfcCommunicationsAppliance_type = 0;
entity* IFC4X1_IfcCommunicationsApplianceType_type = 0;
entity* IFC4X1_IfcComplexProperty_type = 0;
entity* IFC4X1_IfcComplexPropertyTemplate_type = 0;
entity* IFC4X1_IfcCompositeCurve_type = 0;
entity* IFC4X1_IfcCompositeCurveOnSurface_type = 0;
entity* IFC4X1_IfcCompositeCurveSegment_type = 0;
entity* IFC4X1_IfcCompositeProfileDef_type = 0;
entity* IFC4X1_IfcCompressor_type = 0;
entity* IFC4X1_IfcCompressorType_type = 0;
entity* IFC4X1_IfcCondenser_type = 0;
entity* IFC4X1_IfcCondenserType_type = 0;
entity* IFC4X1_IfcConic_type = 0;
entity* IFC4X1_IfcConnectedFaceSet_type = 0;
entity* IFC4X1_IfcConnectionCurveGeometry_type = 0;
entity* IFC4X1_IfcConnectionGeometry_type = 0;
entity* IFC4X1_IfcConnectionPointEccentricity_type = 0;
entity* IFC4X1_IfcConnectionPointGeometry_type = 0;
entity* IFC4X1_IfcConnectionSurfaceGeometry_type = 0;
entity* IFC4X1_IfcConnectionVolumeGeometry_type = 0;
entity* IFC4X1_IfcConstraint_type = 0;
entity* IFC4X1_IfcConstructionEquipmentResource_type = 0;
entity* IFC4X1_IfcConstructionEquipmentResourceType_type = 0;
entity* IFC4X1_IfcConstructionMaterialResource_type = 0;
entity* IFC4X1_IfcConstructionMaterialResourceType_type = 0;
entity* IFC4X1_IfcConstructionProductResource_type = 0;
entity* IFC4X1_IfcConstructionProductResourceType_type = 0;
entity* IFC4X1_IfcConstructionResource_type = 0;
entity* IFC4X1_IfcConstructionResourceType_type = 0;
entity* IFC4X1_IfcContext_type = 0;
entity* IFC4X1_IfcContextDependentUnit_type = 0;
entity* IFC4X1_IfcControl_type = 0;
entity* IFC4X1_IfcController_type = 0;
entity* IFC4X1_IfcControllerType_type = 0;
entity* IFC4X1_IfcConversionBasedUnit_type = 0;
entity* IFC4X1_IfcConversionBasedUnitWithOffset_type = 0;
entity* IFC4X1_IfcCooledBeam_type = 0;
entity* IFC4X1_IfcCooledBeamType_type = 0;
entity* IFC4X1_IfcCoolingTower_type = 0;
entity* IFC4X1_IfcCoolingTowerType_type = 0;
entity* IFC4X1_IfcCoordinateOperation_type = 0;
entity* IFC4X1_IfcCoordinateReferenceSystem_type = 0;
entity* IFC4X1_IfcCostItem_type = 0;
entity* IFC4X1_IfcCostSchedule_type = 0;
entity* IFC4X1_IfcCostValue_type = 0;
entity* IFC4X1_IfcCovering_type = 0;
entity* IFC4X1_IfcCoveringType_type = 0;
entity* IFC4X1_IfcCrewResource_type = 0;
entity* IFC4X1_IfcCrewResourceType_type = 0;
entity* IFC4X1_IfcCsgPrimitive3D_type = 0;
entity* IFC4X1_IfcCsgSolid_type = 0;
entity* IFC4X1_IfcCurrencyRelationship_type = 0;
entity* IFC4X1_IfcCurtainWall_type = 0;
entity* IFC4X1_IfcCurtainWallType_type = 0;
entity* IFC4X1_IfcCurve_type = 0;
entity* IFC4X1_IfcCurveBoundedPlane_type = 0;
entity* IFC4X1_IfcCurveBoundedSurface_type = 0;
entity* IFC4X1_IfcCurveSegment2D_type = 0;
entity* IFC4X1_IfcCurveStyle_type = 0;
entity* IFC4X1_IfcCurveStyleFont_type = 0;
entity* IFC4X1_IfcCurveStyleFontAndScaling_type = 0;
entity* IFC4X1_IfcCurveStyleFontPattern_type = 0;
entity* IFC4X1_IfcCylindricalSurface_type = 0;
entity* IFC4X1_IfcDamper_type = 0;
entity* IFC4X1_IfcDamperType_type = 0;
entity* IFC4X1_IfcDerivedProfileDef_type = 0;
entity* IFC4X1_IfcDerivedUnit_type = 0;
entity* IFC4X1_IfcDerivedUnitElement_type = 0;
entity* IFC4X1_IfcDimensionalExponents_type = 0;
entity* IFC4X1_IfcDirection_type = 0;
entity* IFC4X1_IfcDiscreteAccessory_type = 0;
entity* IFC4X1_IfcDiscreteAccessoryType_type = 0;
entity* IFC4X1_IfcDistanceExpression_type = 0;
entity* IFC4X1_IfcDistributionChamberElement_type = 0;
entity* IFC4X1_IfcDistributionChamberElementType_type = 0;
entity* IFC4X1_IfcDistributionCircuit_type = 0;
entity* IFC4X1_IfcDistributionControlElement_type = 0;
entity* IFC4X1_IfcDistributionControlElementType_type = 0;
entity* IFC4X1_IfcDistributionElement_type = 0;
entity* IFC4X1_IfcDistributionElementType_type = 0;
entity* IFC4X1_IfcDistributionFlowElement_type = 0;
entity* IFC4X1_IfcDistributionFlowElementType_type = 0;
entity* IFC4X1_IfcDistributionPort_type = 0;
entity* IFC4X1_IfcDistributionSystem_type = 0;
entity* IFC4X1_IfcDocumentInformation_type = 0;
entity* IFC4X1_IfcDocumentInformationRelationship_type = 0;
entity* IFC4X1_IfcDocumentReference_type = 0;
entity* IFC4X1_IfcDoor_type = 0;
entity* IFC4X1_IfcDoorLiningProperties_type = 0;
entity* IFC4X1_IfcDoorPanelProperties_type = 0;
entity* IFC4X1_IfcDoorStandardCase_type = 0;
entity* IFC4X1_IfcDoorStyle_type = 0;
entity* IFC4X1_IfcDoorType_type = 0;
entity* IFC4X1_IfcDraughtingPreDefinedColour_type = 0;
entity* IFC4X1_IfcDraughtingPreDefinedCurveFont_type = 0;
entity* IFC4X1_IfcDuctFitting_type = 0;
entity* IFC4X1_IfcDuctFittingType_type = 0;
entity* IFC4X1_IfcDuctSegment_type = 0;
entity* IFC4X1_IfcDuctSegmentType_type = 0;
entity* IFC4X1_IfcDuctSilencer_type = 0;
entity* IFC4X1_IfcDuctSilencerType_type = 0;
entity* IFC4X1_IfcEdge_type = 0;
entity* IFC4X1_IfcEdgeCurve_type = 0;
entity* IFC4X1_IfcEdgeLoop_type = 0;
entity* IFC4X1_IfcElectricAppliance_type = 0;
entity* IFC4X1_IfcElectricApplianceType_type = 0;
entity* IFC4X1_IfcElectricDistributionBoard_type = 0;
entity* IFC4X1_IfcElectricDistributionBoardType_type = 0;
entity* IFC4X1_IfcElectricFlowStorageDevice_type = 0;
entity* IFC4X1_IfcElectricFlowStorageDeviceType_type = 0;
entity* IFC4X1_IfcElectricGenerator_type = 0;
entity* IFC4X1_IfcElectricGeneratorType_type = 0;
entity* IFC4X1_IfcElectricMotor_type = 0;
entity* IFC4X1_IfcElectricMotorType_type = 0;
entity* IFC4X1_IfcElectricTimeControl_type = 0;
entity* IFC4X1_IfcElectricTimeControlType_type = 0;
entity* IFC4X1_IfcElement_type = 0;
entity* IFC4X1_IfcElementAssembly_type = 0;
entity* IFC4X1_IfcElementAssemblyType_type = 0;
entity* IFC4X1_IfcElementComponent_type = 0;
entity* IFC4X1_IfcElementComponentType_type = 0;
entity* IFC4X1_IfcElementQuantity_type = 0;
entity* IFC4X1_IfcElementType_type = 0;
entity* IFC4X1_IfcElementarySurface_type = 0;
entity* IFC4X1_IfcEllipse_type = 0;
entity* IFC4X1_IfcEllipseProfileDef_type = 0;
entity* IFC4X1_IfcEnergyConversionDevice_type = 0;
entity* IFC4X1_IfcEnergyConversionDeviceType_type = 0;
entity* IFC4X1_IfcEngine_type = 0;
entity* IFC4X1_IfcEngineType_type = 0;
entity* IFC4X1_IfcEvaporativeCooler_type = 0;
entity* IFC4X1_IfcEvaporativeCoolerType_type = 0;
entity* IFC4X1_IfcEvaporator_type = 0;
entity* IFC4X1_IfcEvaporatorType_type = 0;
entity* IFC4X1_IfcEvent_type = 0;
entity* IFC4X1_IfcEventTime_type = 0;
entity* IFC4X1_IfcEventType_type = 0;
entity* IFC4X1_IfcExtendedProperties_type = 0;
entity* IFC4X1_IfcExternalInformation_type = 0;
entity* IFC4X1_IfcExternalReference_type = 0;
entity* IFC4X1_IfcExternalReferenceRelationship_type = 0;
entity* IFC4X1_IfcExternalSpatialElement_type = 0;
entity* IFC4X1_IfcExternalSpatialStructureElement_type = 0;
entity* IFC4X1_IfcExternallyDefinedHatchStyle_type = 0;
entity* IFC4X1_IfcExternallyDefinedSurfaceStyle_type = 0;
entity* IFC4X1_IfcExternallyDefinedTextFont_type = 0;
entity* IFC4X1_IfcExtrudedAreaSolid_type = 0;
entity* IFC4X1_IfcExtrudedAreaSolidTapered_type = 0;
entity* IFC4X1_IfcFace_type = 0;
entity* IFC4X1_IfcFaceBasedSurfaceModel_type = 0;
entity* IFC4X1_IfcFaceBound_type = 0;
entity* IFC4X1_IfcFaceOuterBound_type = 0;
entity* IFC4X1_IfcFaceSurface_type = 0;
entity* IFC4X1_IfcFacetedBrep_type = 0;
entity* IFC4X1_IfcFacetedBrepWithVoids_type = 0;
entity* IFC4X1_IfcFailureConnectionCondition_type = 0;
entity* IFC4X1_IfcFan_type = 0;
entity* IFC4X1_IfcFanType_type = 0;
entity* IFC4X1_IfcFastener_type = 0;
entity* IFC4X1_IfcFastenerType_type = 0;
entity* IFC4X1_IfcFeatureElement_type = 0;
entity* IFC4X1_IfcFeatureElementAddition_type = 0;
entity* IFC4X1_IfcFeatureElementSubtraction_type = 0;
entity* IFC4X1_IfcFillAreaStyle_type = 0;
entity* IFC4X1_IfcFillAreaStyleHatching_type = 0;
entity* IFC4X1_IfcFillAreaStyleTiles_type = 0;
entity* IFC4X1_IfcFilter_type = 0;
entity* IFC4X1_IfcFilterType_type = 0;
entity* IFC4X1_IfcFireSuppressionTerminal_type = 0;
entity* IFC4X1_IfcFireSuppressionTerminalType_type = 0;
entity* IFC4X1_IfcFixedReferenceSweptAreaSolid_type = 0;
entity* IFC4X1_IfcFlowController_type = 0;
entity* IFC4X1_IfcFlowControllerType_type = 0;
entity* IFC4X1_IfcFlowFitting_type = 0;
entity* IFC4X1_IfcFlowFittingType_type = 0;
entity* IFC4X1_IfcFlowInstrument_type = 0;
entity* IFC4X1_IfcFlowInstrumentType_type = 0;
entity* IFC4X1_IfcFlowMeter_type = 0;
entity* IFC4X1_IfcFlowMeterType_type = 0;
entity* IFC4X1_IfcFlowMovingDevice_type = 0;
entity* IFC4X1_IfcFlowMovingDeviceType_type = 0;
entity* IFC4X1_IfcFlowSegment_type = 0;
entity* IFC4X1_IfcFlowSegmentType_type = 0;
entity* IFC4X1_IfcFlowStorageDevice_type = 0;
entity* IFC4X1_IfcFlowStorageDeviceType_type = 0;
entity* IFC4X1_IfcFlowTerminal_type = 0;
entity* IFC4X1_IfcFlowTerminalType_type = 0;
entity* IFC4X1_IfcFlowTreatmentDevice_type = 0;
entity* IFC4X1_IfcFlowTreatmentDeviceType_type = 0;
entity* IFC4X1_IfcFooting_type = 0;
entity* IFC4X1_IfcFootingType_type = 0;
entity* IFC4X1_IfcFurnishingElement_type = 0;
entity* IFC4X1_IfcFurnishingElementType_type = 0;
entity* IFC4X1_IfcFurniture_type = 0;
entity* IFC4X1_IfcFurnitureType_type = 0;
entity* IFC4X1_IfcGeographicElement_type = 0;
entity* IFC4X1_IfcGeographicElementType_type = 0;
entity* IFC4X1_IfcGeometricCurveSet_type = 0;
entity* IFC4X1_IfcGeometricRepresentationContext_type = 0;
entity* IFC4X1_IfcGeometricRepresentationItem_type = 0;
entity* IFC4X1_IfcGeometricRepresentationSubContext_type = 0;
entity* IFC4X1_IfcGeometricSet_type = 0;
entity* IFC4X1_IfcGrid_type = 0;
entity* IFC4X1_IfcGridAxis_type = 0;
entity* IFC4X1_IfcGridPlacement_type = 0;
entity* IFC4X1_IfcGroup_type = 0;
entity* IFC4X1_IfcHalfSpaceSolid_type = 0;
entity* IFC4X1_IfcHeatExchanger_type = 0;
entity* IFC4X1_IfcHeatExchangerType_type = 0;
entity* IFC4X1_IfcHumidifier_type = 0;
entity* IFC4X1_IfcHumidifierType_type = 0;
entity* IFC4X1_IfcIShapeProfileDef_type = 0;
entity* IFC4X1_IfcImageTexture_type = 0;
entity* IFC4X1_IfcIndexedColourMap_type = 0;
entity* IFC4X1_IfcIndexedPolyCurve_type = 0;
entity* IFC4X1_IfcIndexedPolygonalFace_type = 0;
entity* IFC4X1_IfcIndexedPolygonalFaceWithVoids_type = 0;
entity* IFC4X1_IfcIndexedTextureMap_type = 0;
entity* IFC4X1_IfcIndexedTriangleTextureMap_type = 0;
entity* IFC4X1_IfcInterceptor_type = 0;
entity* IFC4X1_IfcInterceptorType_type = 0;
entity* IFC4X1_IfcIntersectionCurve_type = 0;
entity* IFC4X1_IfcInventory_type = 0;
entity* IFC4X1_IfcIrregularTimeSeries_type = 0;
entity* IFC4X1_IfcIrregularTimeSeriesValue_type = 0;
entity* IFC4X1_IfcJunctionBox_type = 0;
entity* IFC4X1_IfcJunctionBoxType_type = 0;
entity* IFC4X1_IfcLShapeProfileDef_type = 0;
entity* IFC4X1_IfcLaborResource_type = 0;
entity* IFC4X1_IfcLaborResourceType_type = 0;
entity* IFC4X1_IfcLagTime_type = 0;
entity* IFC4X1_IfcLamp_type = 0;
entity* IFC4X1_IfcLampType_type = 0;
entity* IFC4X1_IfcLibraryInformation_type = 0;
entity* IFC4X1_IfcLibraryReference_type = 0;
entity* IFC4X1_IfcLightDistributionData_type = 0;
entity* IFC4X1_IfcLightFixture_type = 0;
entity* IFC4X1_IfcLightFixtureType_type = 0;
entity* IFC4X1_IfcLightIntensityDistribution_type = 0;
entity* IFC4X1_IfcLightSource_type = 0;
entity* IFC4X1_IfcLightSourceAmbient_type = 0;
entity* IFC4X1_IfcLightSourceDirectional_type = 0;
entity* IFC4X1_IfcLightSourceGoniometric_type = 0;
entity* IFC4X1_IfcLightSourcePositional_type = 0;
entity* IFC4X1_IfcLightSourceSpot_type = 0;
entity* IFC4X1_IfcLine_type = 0;
entity* IFC4X1_IfcLineSegment2D_type = 0;
entity* IFC4X1_IfcLinearPlacement_type = 0;
entity* IFC4X1_IfcLinearPositioningElement_type = 0;
entity* IFC4X1_IfcLocalPlacement_type = 0;
entity* IFC4X1_IfcLoop_type = 0;
entity* IFC4X1_IfcManifoldSolidBrep_type = 0;
entity* IFC4X1_IfcMapConversion_type = 0;
entity* IFC4X1_IfcMappedItem_type = 0;
entity* IFC4X1_IfcMaterial_type = 0;
entity* IFC4X1_IfcMaterialClassificationRelationship_type = 0;
entity* IFC4X1_IfcMaterialConstituent_type = 0;
entity* IFC4X1_IfcMaterialConstituentSet_type = 0;
entity* IFC4X1_IfcMaterialDefinition_type = 0;
entity* IFC4X1_IfcMaterialDefinitionRepresentation_type = 0;
entity* IFC4X1_IfcMaterialLayer_type = 0;
entity* IFC4X1_IfcMaterialLayerSet_type = 0;
entity* IFC4X1_IfcMaterialLayerSetUsage_type = 0;
entity* IFC4X1_IfcMaterialLayerWithOffsets_type = 0;
entity* IFC4X1_IfcMaterialList_type = 0;
entity* IFC4X1_IfcMaterialProfile_type = 0;
entity* IFC4X1_IfcMaterialProfileSet_type = 0;
entity* IFC4X1_IfcMaterialProfileSetUsage_type = 0;
entity* IFC4X1_IfcMaterialProfileSetUsageTapering_type = 0;
entity* IFC4X1_IfcMaterialProfileWithOffsets_type = 0;
entity* IFC4X1_IfcMaterialProperties_type = 0;
entity* IFC4X1_IfcMaterialRelationship_type = 0;
entity* IFC4X1_IfcMaterialUsageDefinition_type = 0;
entity* IFC4X1_IfcMeasureWithUnit_type = 0;
entity* IFC4X1_IfcMechanicalFastener_type = 0;
entity* IFC4X1_IfcMechanicalFastenerType_type = 0;
entity* IFC4X1_IfcMedicalDevice_type = 0;
entity* IFC4X1_IfcMedicalDeviceType_type = 0;
entity* IFC4X1_IfcMember_type = 0;
entity* IFC4X1_IfcMemberStandardCase_type = 0;
entity* IFC4X1_IfcMemberType_type = 0;
entity* IFC4X1_IfcMetric_type = 0;
entity* IFC4X1_IfcMirroredProfileDef_type = 0;
entity* IFC4X1_IfcMonetaryUnit_type = 0;
entity* IFC4X1_IfcMotorConnection_type = 0;
entity* IFC4X1_IfcMotorConnectionType_type = 0;
entity* IFC4X1_IfcNamedUnit_type = 0;
entity* IFC4X1_IfcObject_type = 0;
entity* IFC4X1_IfcObjectDefinition_type = 0;
entity* IFC4X1_IfcObjectPlacement_type = 0;
entity* IFC4X1_IfcObjective_type = 0;
entity* IFC4X1_IfcOccupant_type = 0;
entity* IFC4X1_IfcOffsetCurve_type = 0;
entity* IFC4X1_IfcOffsetCurve2D_type = 0;
entity* IFC4X1_IfcOffsetCurve3D_type = 0;
entity* IFC4X1_IfcOffsetCurveByDistances_type = 0;
entity* IFC4X1_IfcOpenShell_type = 0;
entity* IFC4X1_IfcOpeningElement_type = 0;
entity* IFC4X1_IfcOpeningStandardCase_type = 0;
entity* IFC4X1_IfcOrganization_type = 0;
entity* IFC4X1_IfcOrganizationRelationship_type = 0;
entity* IFC4X1_IfcOrientationExpression_type = 0;
entity* IFC4X1_IfcOrientedEdge_type = 0;
entity* IFC4X1_IfcOuterBoundaryCurve_type = 0;
entity* IFC4X1_IfcOutlet_type = 0;
entity* IFC4X1_IfcOutletType_type = 0;
entity* IFC4X1_IfcOwnerHistory_type = 0;
entity* IFC4X1_IfcParameterizedProfileDef_type = 0;
entity* IFC4X1_IfcPath_type = 0;
entity* IFC4X1_IfcPcurve_type = 0;
entity* IFC4X1_IfcPerformanceHistory_type = 0;
entity* IFC4X1_IfcPermeableCoveringProperties_type = 0;
entity* IFC4X1_IfcPermit_type = 0;
entity* IFC4X1_IfcPerson_type = 0;
entity* IFC4X1_IfcPersonAndOrganization_type = 0;
entity* IFC4X1_IfcPhysicalComplexQuantity_type = 0;
entity* IFC4X1_IfcPhysicalQuantity_type = 0;
entity* IFC4X1_IfcPhysicalSimpleQuantity_type = 0;
entity* IFC4X1_IfcPile_type = 0;
entity* IFC4X1_IfcPileType_type = 0;
entity* IFC4X1_IfcPipeFitting_type = 0;
entity* IFC4X1_IfcPipeFittingType_type = 0;
entity* IFC4X1_IfcPipeSegment_type = 0;
entity* IFC4X1_IfcPipeSegmentType_type = 0;
entity* IFC4X1_IfcPixelTexture_type = 0;
entity* IFC4X1_IfcPlacement_type = 0;
entity* IFC4X1_IfcPlanarBox_type = 0;
entity* IFC4X1_IfcPlanarExtent_type = 0;
entity* IFC4X1_IfcPlane_type = 0;
entity* IFC4X1_IfcPlate_type = 0;
entity* IFC4X1_IfcPlateStandardCase_type = 0;
entity* IFC4X1_IfcPlateType_type = 0;
entity* IFC4X1_IfcPoint_type = 0;
entity* IFC4X1_IfcPointOnCurve_type = 0;
entity* IFC4X1_IfcPointOnSurface_type = 0;
entity* IFC4X1_IfcPolyLoop_type = 0;
entity* IFC4X1_IfcPolygonalBoundedHalfSpace_type = 0;
entity* IFC4X1_IfcPolygonalFaceSet_type = 0;
entity* IFC4X1_IfcPolyline_type = 0;
entity* IFC4X1_IfcPort_type = 0;
entity* IFC4X1_IfcPositioningElement_type = 0;
entity* IFC4X1_IfcPostalAddress_type = 0;
entity* IFC4X1_IfcPreDefinedColour_type = 0;
entity* IFC4X1_IfcPreDefinedCurveFont_type = 0;
entity* IFC4X1_IfcPreDefinedItem_type = 0;
entity* IFC4X1_IfcPreDefinedProperties_type = 0;
entity* IFC4X1_IfcPreDefinedPropertySet_type = 0;
entity* IFC4X1_IfcPreDefinedTextFont_type = 0;
entity* IFC4X1_IfcPresentationItem_type = 0;
entity* IFC4X1_IfcPresentationLayerAssignment_type = 0;
entity* IFC4X1_IfcPresentationLayerWithStyle_type = 0;
entity* IFC4X1_IfcPresentationStyle_type = 0;
entity* IFC4X1_IfcPresentationStyleAssignment_type = 0;
entity* IFC4X1_IfcProcedure_type = 0;
entity* IFC4X1_IfcProcedureType_type = 0;
entity* IFC4X1_IfcProcess_type = 0;
entity* IFC4X1_IfcProduct_type = 0;
entity* IFC4X1_IfcProductDefinitionShape_type = 0;
entity* IFC4X1_IfcProductRepresentation_type = 0;
entity* IFC4X1_IfcProfileDef_type = 0;
entity* IFC4X1_IfcProfileProperties_type = 0;
entity* IFC4X1_IfcProject_type = 0;
entity* IFC4X1_IfcProjectLibrary_type = 0;
entity* IFC4X1_IfcProjectOrder_type = 0;
entity* IFC4X1_IfcProjectedCRS_type = 0;
entity* IFC4X1_IfcProjectionElement_type = 0;
entity* IFC4X1_IfcProperty_type = 0;
entity* IFC4X1_IfcPropertyAbstraction_type = 0;
entity* IFC4X1_IfcPropertyBoundedValue_type = 0;
entity* IFC4X1_IfcPropertyDefinition_type = 0;
entity* IFC4X1_IfcPropertyDependencyRelationship_type = 0;
entity* IFC4X1_IfcPropertyEnumeratedValue_type = 0;
entity* IFC4X1_IfcPropertyEnumeration_type = 0;
entity* IFC4X1_IfcPropertyListValue_type = 0;
entity* IFC4X1_IfcPropertyReferenceValue_type = 0;
entity* IFC4X1_IfcPropertySet_type = 0;
entity* IFC4X1_IfcPropertySetDefinition_type = 0;
entity* IFC4X1_IfcPropertySetTemplate_type = 0;
entity* IFC4X1_IfcPropertySingleValue_type = 0;
entity* IFC4X1_IfcPropertyTableValue_type = 0;
entity* IFC4X1_IfcPropertyTemplate_type = 0;
entity* IFC4X1_IfcPropertyTemplateDefinition_type = 0;
entity* IFC4X1_IfcProtectiveDevice_type = 0;
entity* IFC4X1_IfcProtectiveDeviceTrippingUnit_type = 0;
entity* IFC4X1_IfcProtectiveDeviceTrippingUnitType_type = 0;
entity* IFC4X1_IfcProtectiveDeviceType_type = 0;
entity* IFC4X1_IfcProxy_type = 0;
entity* IFC4X1_IfcPump_type = 0;
entity* IFC4X1_IfcPumpType_type = 0;
entity* IFC4X1_IfcQuantityArea_type = 0;
entity* IFC4X1_IfcQuantityCount_type = 0;
entity* IFC4X1_IfcQuantityLength_type = 0;
entity* IFC4X1_IfcQuantitySet_type = 0;
entity* IFC4X1_IfcQuantityTime_type = 0;
entity* IFC4X1_IfcQuantityVolume_type = 0;
entity* IFC4X1_IfcQuantityWeight_type = 0;
entity* IFC4X1_IfcRailing_type = 0;
entity* IFC4X1_IfcRailingType_type = 0;
entity* IFC4X1_IfcRamp_type = 0;
entity* IFC4X1_IfcRampFlight_type = 0;
entity* IFC4X1_IfcRampFlightType_type = 0;
entity* IFC4X1_IfcRampType_type = 0;
entity* IFC4X1_IfcRationalBSplineCurveWithKnots_type = 0;
entity* IFC4X1_IfcRationalBSplineSurfaceWithKnots_type = 0;
entity* IFC4X1_IfcRectangleHollowProfileDef_type = 0;
entity* IFC4X1_IfcRectangleProfileDef_type = 0;
entity* IFC4X1_IfcRectangularPyramid_type = 0;
entity* IFC4X1_IfcRectangularTrimmedSurface_type = 0;
entity* IFC4X1_IfcRecurrencePattern_type = 0;
entity* IFC4X1_IfcReference_type = 0;
entity* IFC4X1_IfcReferent_type = 0;
entity* IFC4X1_IfcRegularTimeSeries_type = 0;
entity* IFC4X1_IfcReinforcementBarProperties_type = 0;
entity* IFC4X1_IfcReinforcementDefinitionProperties_type = 0;
entity* IFC4X1_IfcReinforcingBar_type = 0;
entity* IFC4X1_IfcReinforcingBarType_type = 0;
entity* IFC4X1_IfcReinforcingElement_type = 0;
entity* IFC4X1_IfcReinforcingElementType_type = 0;
entity* IFC4X1_IfcReinforcingMesh_type = 0;
entity* IFC4X1_IfcReinforcingMeshType_type = 0;
entity* IFC4X1_IfcRelAggregates_type = 0;
entity* IFC4X1_IfcRelAssigns_type = 0;
entity* IFC4X1_IfcRelAssignsToActor_type = 0;
entity* IFC4X1_IfcRelAssignsToControl_type = 0;
entity* IFC4X1_IfcRelAssignsToGroup_type = 0;
entity* IFC4X1_IfcRelAssignsToGroupByFactor_type = 0;
entity* IFC4X1_IfcRelAssignsToProcess_type = 0;
entity* IFC4X1_IfcRelAssignsToProduct_type = 0;
entity* IFC4X1_IfcRelAssignsToResource_type = 0;
entity* IFC4X1_IfcRelAssociates_type = 0;
entity* IFC4X1_IfcRelAssociatesApproval_type = 0;
entity* IFC4X1_IfcRelAssociatesClassification_type = 0;
entity* IFC4X1_IfcRelAssociatesConstraint_type = 0;
entity* IFC4X1_IfcRelAssociatesDocument_type = 0;
entity* IFC4X1_IfcRelAssociatesLibrary_type = 0;
entity* IFC4X1_IfcRelAssociatesMaterial_type = 0;
entity* IFC4X1_IfcRelConnects_type = 0;
entity* IFC4X1_IfcRelConnectsElements_type = 0;
entity* IFC4X1_IfcRelConnectsPathElements_type = 0;
entity* IFC4X1_IfcRelConnectsPortToElement_type = 0;
entity* IFC4X1_IfcRelConnectsPorts_type = 0;
entity* IFC4X1_IfcRelConnectsStructuralActivity_type = 0;
entity* IFC4X1_IfcRelConnectsStructuralMember_type = 0;
entity* IFC4X1_IfcRelConnectsWithEccentricity_type = 0;
entity* IFC4X1_IfcRelConnectsWithRealizingElements_type = 0;
entity* IFC4X1_IfcRelContainedInSpatialStructure_type = 0;
entity* IFC4X1_IfcRelCoversBldgElements_type = 0;
entity* IFC4X1_IfcRelCoversSpaces_type = 0;
entity* IFC4X1_IfcRelDeclares_type = 0;
entity* IFC4X1_IfcRelDecomposes_type = 0;
entity* IFC4X1_IfcRelDefines_type = 0;
entity* IFC4X1_IfcRelDefinesByObject_type = 0;
entity* IFC4X1_IfcRelDefinesByProperties_type = 0;
entity* IFC4X1_IfcRelDefinesByTemplate_type = 0;
entity* IFC4X1_IfcRelDefinesByType_type = 0;
entity* IFC4X1_IfcRelFillsElement_type = 0;
entity* IFC4X1_IfcRelFlowControlElements_type = 0;
entity* IFC4X1_IfcRelInterferesElements_type = 0;
entity* IFC4X1_IfcRelNests_type = 0;
entity* IFC4X1_IfcRelProjectsElement_type = 0;
entity* IFC4X1_IfcRelReferencedInSpatialStructure_type = 0;
entity* IFC4X1_IfcRelSequence_type = 0;
entity* IFC4X1_IfcRelServicesBuildings_type = 0;
entity* IFC4X1_IfcRelSpaceBoundary_type = 0;
entity* IFC4X1_IfcRelSpaceBoundary1stLevel_type = 0;
entity* IFC4X1_IfcRelSpaceBoundary2ndLevel_type = 0;
entity* IFC4X1_IfcRelVoidsElement_type = 0;
entity* IFC4X1_IfcRelationship_type = 0;
entity* IFC4X1_IfcReparametrisedCompositeCurveSegment_type = 0;
entity* IFC4X1_IfcRepresentation_type = 0;
entity* IFC4X1_IfcRepresentationContext_type = 0;
entity* IFC4X1_IfcRepresentationItem_type = 0;
entity* IFC4X1_IfcRepresentationMap_type = 0;
entity* IFC4X1_IfcResource_type = 0;
entity* IFC4X1_IfcResourceApprovalRelationship_type = 0;
entity* IFC4X1_IfcResourceConstraintRelationship_type = 0;
entity* IFC4X1_IfcResourceLevelRelationship_type = 0;
entity* IFC4X1_IfcResourceTime_type = 0;
entity* IFC4X1_IfcRevolvedAreaSolid_type = 0;
entity* IFC4X1_IfcRevolvedAreaSolidTapered_type = 0;
entity* IFC4X1_IfcRightCircularCone_type = 0;
entity* IFC4X1_IfcRightCircularCylinder_type = 0;
entity* IFC4X1_IfcRoof_type = 0;
entity* IFC4X1_IfcRoofType_type = 0;
entity* IFC4X1_IfcRoot_type = 0;
entity* IFC4X1_IfcRoundedRectangleProfileDef_type = 0;
entity* IFC4X1_IfcSIUnit_type = 0;
entity* IFC4X1_IfcSanitaryTerminal_type = 0;
entity* IFC4X1_IfcSanitaryTerminalType_type = 0;
entity* IFC4X1_IfcSchedulingTime_type = 0;
entity* IFC4X1_IfcSeamCurve_type = 0;
entity* IFC4X1_IfcSectionProperties_type = 0;
entity* IFC4X1_IfcSectionReinforcementProperties_type = 0;
entity* IFC4X1_IfcSectionedSolid_type = 0;
entity* IFC4X1_IfcSectionedSolidHorizontal_type = 0;
entity* IFC4X1_IfcSectionedSpine_type = 0;
entity* IFC4X1_IfcSensor_type = 0;
entity* IFC4X1_IfcSensorType_type = 0;
entity* IFC4X1_IfcShadingDevice_type = 0;
entity* IFC4X1_IfcShadingDeviceType_type = 0;
entity* IFC4X1_IfcShapeAspect_type = 0;
entity* IFC4X1_IfcShapeModel_type = 0;
entity* IFC4X1_IfcShapeRepresentation_type = 0;
entity* IFC4X1_IfcShellBasedSurfaceModel_type = 0;
entity* IFC4X1_IfcSimpleProperty_type = 0;
entity* IFC4X1_IfcSimplePropertyTemplate_type = 0;
entity* IFC4X1_IfcSite_type = 0;
entity* IFC4X1_IfcSlab_type = 0;
entity* IFC4X1_IfcSlabElementedCase_type = 0;
entity* IFC4X1_IfcSlabStandardCase_type = 0;
entity* IFC4X1_IfcSlabType_type = 0;
entity* IFC4X1_IfcSlippageConnectionCondition_type = 0;
entity* IFC4X1_IfcSolarDevice_type = 0;
entity* IFC4X1_IfcSolarDeviceType_type = 0;
entity* IFC4X1_IfcSolidModel_type = 0;
entity* IFC4X1_IfcSpace_type = 0;
entity* IFC4X1_IfcSpaceHeater_type = 0;
entity* IFC4X1_IfcSpaceHeaterType_type = 0;
entity* IFC4X1_IfcSpaceType_type = 0;
entity* IFC4X1_IfcSpatialElement_type = 0;
entity* IFC4X1_IfcSpatialElementType_type = 0;
entity* IFC4X1_IfcSpatialStructureElement_type = 0;
entity* IFC4X1_IfcSpatialStructureElementType_type = 0;
entity* IFC4X1_IfcSpatialZone_type = 0;
entity* IFC4X1_IfcSpatialZoneType_type = 0;
entity* IFC4X1_IfcSphere_type = 0;
entity* IFC4X1_IfcSphericalSurface_type = 0;
entity* IFC4X1_IfcStackTerminal_type = 0;
entity* IFC4X1_IfcStackTerminalType_type = 0;
entity* IFC4X1_IfcStair_type = 0;
entity* IFC4X1_IfcStairFlight_type = 0;
entity* IFC4X1_IfcStairFlightType_type = 0;
entity* IFC4X1_IfcStairType_type = 0;
entity* IFC4X1_IfcStructuralAction_type = 0;
entity* IFC4X1_IfcStructuralActivity_type = 0;
entity* IFC4X1_IfcStructuralAnalysisModel_type = 0;
entity* IFC4X1_IfcStructuralConnection_type = 0;
entity* IFC4X1_IfcStructuralConnectionCondition_type = 0;
entity* IFC4X1_IfcStructuralCurveAction_type = 0;
entity* IFC4X1_IfcStructuralCurveConnection_type = 0;
entity* IFC4X1_IfcStructuralCurveMember_type = 0;
entity* IFC4X1_IfcStructuralCurveMemberVarying_type = 0;
entity* IFC4X1_IfcStructuralCurveReaction_type = 0;
entity* IFC4X1_IfcStructuralItem_type = 0;
entity* IFC4X1_IfcStructuralLinearAction_type = 0;
entity* IFC4X1_IfcStructuralLoad_type = 0;
entity* IFC4X1_IfcStructuralLoadCase_type = 0;
entity* IFC4X1_IfcStructuralLoadConfiguration_type = 0;
entity* IFC4X1_IfcStructuralLoadGroup_type = 0;
entity* IFC4X1_IfcStructuralLoadLinearForce_type = 0;
entity* IFC4X1_IfcStructuralLoadOrResult_type = 0;
entity* IFC4X1_IfcStructuralLoadPlanarForce_type = 0;
entity* IFC4X1_IfcStructuralLoadSingleDisplacement_type = 0;
entity* IFC4X1_IfcStructuralLoadSingleDisplacementDistortion_type = 0;
entity* IFC4X1_IfcStructuralLoadSingleForce_type = 0;
entity* IFC4X1_IfcStructuralLoadSingleForceWarping_type = 0;
entity* IFC4X1_IfcStructuralLoadStatic_type = 0;
entity* IFC4X1_IfcStructuralLoadTemperature_type = 0;
entity* IFC4X1_IfcStructuralMember_type = 0;
entity* IFC4X1_IfcStructuralPlanarAction_type = 0;
entity* IFC4X1_IfcStructuralPointAction_type = 0;
entity* IFC4X1_IfcStructuralPointConnection_type = 0;
entity* IFC4X1_IfcStructuralPointReaction_type = 0;
entity* IFC4X1_IfcStructuralReaction_type = 0;
entity* IFC4X1_IfcStructuralResultGroup_type = 0;
entity* IFC4X1_IfcStructuralSurfaceAction_type = 0;
entity* IFC4X1_IfcStructuralSurfaceConnection_type = 0;
entity* IFC4X1_IfcStructuralSurfaceMember_type = 0;
entity* IFC4X1_IfcStructuralSurfaceMemberVarying_type = 0;
entity* IFC4X1_IfcStructuralSurfaceReaction_type = 0;
entity* IFC4X1_IfcStyleModel_type = 0;
entity* IFC4X1_IfcStyledItem_type = 0;
entity* IFC4X1_IfcStyledRepresentation_type = 0;
entity* IFC4X1_IfcSubContractResource_type = 0;
entity* IFC4X1_IfcSubContractResourceType_type = 0;
entity* IFC4X1_IfcSubedge_type = 0;
entity* IFC4X1_IfcSurface_type = 0;
entity* IFC4X1_IfcSurfaceCurve_type = 0;
entity* IFC4X1_IfcSurfaceCurveSweptAreaSolid_type = 0;
entity* IFC4X1_IfcSurfaceFeature_type = 0;
entity* IFC4X1_IfcSurfaceOfLinearExtrusion_type = 0;
entity* IFC4X1_IfcSurfaceOfRevolution_type = 0;
entity* IFC4X1_IfcSurfaceReinforcementArea_type = 0;
entity* IFC4X1_IfcSurfaceStyle_type = 0;
entity* IFC4X1_IfcSurfaceStyleLighting_type = 0;
entity* IFC4X1_IfcSurfaceStyleRefraction_type = 0;
entity* IFC4X1_IfcSurfaceStyleRendering_type = 0;
entity* IFC4X1_IfcSurfaceStyleShading_type = 0;
entity* IFC4X1_IfcSurfaceStyleWithTextures_type = 0;
entity* IFC4X1_IfcSurfaceTexture_type = 0;
entity* IFC4X1_IfcSweptAreaSolid_type = 0;
entity* IFC4X1_IfcSweptDiskSolid_type = 0;
entity* IFC4X1_IfcSweptDiskSolidPolygonal_type = 0;
entity* IFC4X1_IfcSweptSurface_type = 0;
entity* IFC4X1_IfcSwitchingDevice_type = 0;
entity* IFC4X1_IfcSwitchingDeviceType_type = 0;
entity* IFC4X1_IfcSystem_type = 0;
entity* IFC4X1_IfcSystemFurnitureElement_type = 0;
entity* IFC4X1_IfcSystemFurnitureElementType_type = 0;
entity* IFC4X1_IfcTShapeProfileDef_type = 0;
entity* IFC4X1_IfcTable_type = 0;
entity* IFC4X1_IfcTableColumn_type = 0;
entity* IFC4X1_IfcTableRow_type = 0;
entity* IFC4X1_IfcTank_type = 0;
entity* IFC4X1_IfcTankType_type = 0;
entity* IFC4X1_IfcTask_type = 0;
entity* IFC4X1_IfcTaskTime_type = 0;
entity* IFC4X1_IfcTaskTimeRecurring_type = 0;
entity* IFC4X1_IfcTaskType_type = 0;
entity* IFC4X1_IfcTelecomAddress_type = 0;
entity* IFC4X1_IfcTendon_type = 0;
entity* IFC4X1_IfcTendonAnchor_type = 0;
entity* IFC4X1_IfcTendonAnchorType_type = 0;
entity* IFC4X1_IfcTendonType_type = 0;
entity* IFC4X1_IfcTessellatedFaceSet_type = 0;
entity* IFC4X1_IfcTessellatedItem_type = 0;
entity* IFC4X1_IfcTextLiteral_type = 0;
entity* IFC4X1_IfcTextLiteralWithExtent_type = 0;
entity* IFC4X1_IfcTextStyle_type = 0;
entity* IFC4X1_IfcTextStyleFontModel_type = 0;
entity* IFC4X1_IfcTextStyleForDefinedFont_type = 0;
entity* IFC4X1_IfcTextStyleTextModel_type = 0;
entity* IFC4X1_IfcTextureCoordinate_type = 0;
entity* IFC4X1_IfcTextureCoordinateGenerator_type = 0;
entity* IFC4X1_IfcTextureMap_type = 0;
entity* IFC4X1_IfcTextureVertex_type = 0;
entity* IFC4X1_IfcTextureVertexList_type = 0;
entity* IFC4X1_IfcTimePeriod_type = 0;
entity* IFC4X1_IfcTimeSeries_type = 0;
entity* IFC4X1_IfcTimeSeriesValue_type = 0;
entity* IFC4X1_IfcTopologicalRepresentationItem_type = 0;
entity* IFC4X1_IfcTopologyRepresentation_type = 0;
entity* IFC4X1_IfcToroidalSurface_type = 0;
entity* IFC4X1_IfcTransformer_type = 0;
entity* IFC4X1_IfcTransformerType_type = 0;
entity* IFC4X1_IfcTransitionCurveSegment2D_type = 0;
entity* IFC4X1_IfcTransportElement_type = 0;
entity* IFC4X1_IfcTransportElementType_type = 0;
entity* IFC4X1_IfcTrapeziumProfileDef_type = 0;
entity* IFC4X1_IfcTriangulatedFaceSet_type = 0;
entity* IFC4X1_IfcTriangulatedIrregularNetwork_type = 0;
entity* IFC4X1_IfcTrimmedCurve_type = 0;
entity* IFC4X1_IfcTubeBundle_type = 0;
entity* IFC4X1_IfcTubeBundleType_type = 0;
entity* IFC4X1_IfcTypeObject_type = 0;
entity* IFC4X1_IfcTypeProcess_type = 0;
entity* IFC4X1_IfcTypeProduct_type = 0;
entity* IFC4X1_IfcTypeResource_type = 0;
entity* IFC4X1_IfcUShapeProfileDef_type = 0;
entity* IFC4X1_IfcUnitAssignment_type = 0;
entity* IFC4X1_IfcUnitaryControlElement_type = 0;
entity* IFC4X1_IfcUnitaryControlElementType_type = 0;
entity* IFC4X1_IfcUnitaryEquipment_type = 0;
entity* IFC4X1_IfcUnitaryEquipmentType_type = 0;
entity* IFC4X1_IfcValve_type = 0;
entity* IFC4X1_IfcValveType_type = 0;
entity* IFC4X1_IfcVector_type = 0;
entity* IFC4X1_IfcVertex_type = 0;
entity* IFC4X1_IfcVertexLoop_type = 0;
entity* IFC4X1_IfcVertexPoint_type = 0;
entity* IFC4X1_IfcVibrationIsolator_type = 0;
entity* IFC4X1_IfcVibrationIsolatorType_type = 0;
entity* IFC4X1_IfcVirtualElement_type = 0;
entity* IFC4X1_IfcVirtualGridIntersection_type = 0;
entity* IFC4X1_IfcVoidingFeature_type = 0;
entity* IFC4X1_IfcWall_type = 0;
entity* IFC4X1_IfcWallElementedCase_type = 0;
entity* IFC4X1_IfcWallStandardCase_type = 0;
entity* IFC4X1_IfcWallType_type = 0;
entity* IFC4X1_IfcWasteTerminal_type = 0;
entity* IFC4X1_IfcWasteTerminalType_type = 0;
entity* IFC4X1_IfcWindow_type = 0;
entity* IFC4X1_IfcWindowLiningProperties_type = 0;
entity* IFC4X1_IfcWindowPanelProperties_type = 0;
entity* IFC4X1_IfcWindowStandardCase_type = 0;
entity* IFC4X1_IfcWindowStyle_type = 0;
entity* IFC4X1_IfcWindowType_type = 0;
entity* IFC4X1_IfcWorkCalendar_type = 0;
entity* IFC4X1_IfcWorkControl_type = 0;
entity* IFC4X1_IfcWorkPlan_type = 0;
entity* IFC4X1_IfcWorkSchedule_type = 0;
entity* IFC4X1_IfcWorkTime_type = 0;
entity* IFC4X1_IfcZShapeProfileDef_type = 0;
entity* IFC4X1_IfcZone_type = 0;
type_declaration* IFC4X1_IfcAbsorbedDoseMeasure_type = 0;
type_declaration* IFC4X1_IfcAccelerationMeasure_type = 0;
type_declaration* IFC4X1_IfcAmountOfSubstanceMeasure_type = 0;
type_declaration* IFC4X1_IfcAngularVelocityMeasure_type = 0;
type_declaration* IFC4X1_IfcArcIndex_type = 0;
type_declaration* IFC4X1_IfcAreaDensityMeasure_type = 0;
type_declaration* IFC4X1_IfcAreaMeasure_type = 0;
type_declaration* IFC4X1_IfcBinary_type = 0;
type_declaration* IFC4X1_IfcBoolean_type = 0;
type_declaration* IFC4X1_IfcBoxAlignment_type = 0;
type_declaration* IFC4X1_IfcCardinalPointReference_type = 0;
type_declaration* IFC4X1_IfcComplexNumber_type = 0;
type_declaration* IFC4X1_IfcCompoundPlaneAngleMeasure_type = 0;
type_declaration* IFC4X1_IfcContextDependentMeasure_type = 0;
type_declaration* IFC4X1_IfcCountMeasure_type = 0;
type_declaration* IFC4X1_IfcCurvatureMeasure_type = 0;
type_declaration* IFC4X1_IfcDate_type = 0;
type_declaration* IFC4X1_IfcDateTime_type = 0;
type_declaration* IFC4X1_IfcDayInMonthNumber_type = 0;
type_declaration* IFC4X1_IfcDayInWeekNumber_type = 0;
type_declaration* IFC4X1_IfcDescriptiveMeasure_type = 0;
type_declaration* IFC4X1_IfcDimensionCount_type = 0;
type_declaration* IFC4X1_IfcDoseEquivalentMeasure_type = 0;
type_declaration* IFC4X1_IfcDuration_type = 0;
type_declaration* IFC4X1_IfcDynamicViscosityMeasure_type = 0;
type_declaration* IFC4X1_IfcElectricCapacitanceMeasure_type = 0;
type_declaration* IFC4X1_IfcElectricChargeMeasure_type = 0;
type_declaration* IFC4X1_IfcElectricConductanceMeasure_type = 0;
type_declaration* IFC4X1_IfcElectricCurrentMeasure_type = 0;
type_declaration* IFC4X1_IfcElectricResistanceMeasure_type = 0;
type_declaration* IFC4X1_IfcElectricVoltageMeasure_type = 0;
type_declaration* IFC4X1_IfcEnergyMeasure_type = 0;
type_declaration* IFC4X1_IfcFontStyle_type = 0;
type_declaration* IFC4X1_IfcFontVariant_type = 0;
type_declaration* IFC4X1_IfcFontWeight_type = 0;
type_declaration* IFC4X1_IfcForceMeasure_type = 0;
type_declaration* IFC4X1_IfcFrequencyMeasure_type = 0;
type_declaration* IFC4X1_IfcGloballyUniqueId_type = 0;
type_declaration* IFC4X1_IfcHeatFluxDensityMeasure_type = 0;
type_declaration* IFC4X1_IfcHeatingValueMeasure_type = 0;
type_declaration* IFC4X1_IfcIdentifier_type = 0;
type_declaration* IFC4X1_IfcIlluminanceMeasure_type = 0;
type_declaration* IFC4X1_IfcInductanceMeasure_type = 0;
type_declaration* IFC4X1_IfcInteger_type = 0;
type_declaration* IFC4X1_IfcIntegerCountRateMeasure_type = 0;
type_declaration* IFC4X1_IfcIonConcentrationMeasure_type = 0;
type_declaration* IFC4X1_IfcIsothermalMoistureCapacityMeasure_type = 0;
type_declaration* IFC4X1_IfcKinematicViscosityMeasure_type = 0;
type_declaration* IFC4X1_IfcLabel_type = 0;
type_declaration* IFC4X1_IfcLanguageId_type = 0;
type_declaration* IFC4X1_IfcLengthMeasure_type = 0;
type_declaration* IFC4X1_IfcLineIndex_type = 0;
type_declaration* IFC4X1_IfcLinearForceMeasure_type = 0;
type_declaration* IFC4X1_IfcLinearMomentMeasure_type = 0;
type_declaration* IFC4X1_IfcLinearStiffnessMeasure_type = 0;
type_declaration* IFC4X1_IfcLinearVelocityMeasure_type = 0;
type_declaration* IFC4X1_IfcLogical_type = 0;
type_declaration* IFC4X1_IfcLuminousFluxMeasure_type = 0;
type_declaration* IFC4X1_IfcLuminousIntensityDistributionMeasure_type = 0;
type_declaration* IFC4X1_IfcLuminousIntensityMeasure_type = 0;
type_declaration* IFC4X1_IfcMagneticFluxDensityMeasure_type = 0;
type_declaration* IFC4X1_IfcMagneticFluxMeasure_type = 0;
type_declaration* IFC4X1_IfcMassDensityMeasure_type = 0;
type_declaration* IFC4X1_IfcMassFlowRateMeasure_type = 0;
type_declaration* IFC4X1_IfcMassMeasure_type = 0;
type_declaration* IFC4X1_IfcMassPerLengthMeasure_type = 0;
type_declaration* IFC4X1_IfcModulusOfElasticityMeasure_type = 0;
type_declaration* IFC4X1_IfcModulusOfLinearSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X1_IfcModulusOfRotationalSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X1_IfcModulusOfSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X1_IfcMoistureDiffusivityMeasure_type = 0;
type_declaration* IFC4X1_IfcMolecularWeightMeasure_type = 0;
type_declaration* IFC4X1_IfcMomentOfInertiaMeasure_type = 0;
type_declaration* IFC4X1_IfcMonetaryMeasure_type = 0;
type_declaration* IFC4X1_IfcMonthInYearNumber_type = 0;
type_declaration* IFC4X1_IfcNonNegativeLengthMeasure_type = 0;
type_declaration* IFC4X1_IfcNormalisedRatioMeasure_type = 0;
type_declaration* IFC4X1_IfcNumericMeasure_type = 0;
type_declaration* IFC4X1_IfcPHMeasure_type = 0;
type_declaration* IFC4X1_IfcParameterValue_type = 0;
type_declaration* IFC4X1_IfcPlanarForceMeasure_type = 0;
type_declaration* IFC4X1_IfcPlaneAngleMeasure_type = 0;
type_declaration* IFC4X1_IfcPositiveInteger_type = 0;
type_declaration* IFC4X1_IfcPositiveLengthMeasure_type = 0;
type_declaration* IFC4X1_IfcPositivePlaneAngleMeasure_type = 0;
type_declaration* IFC4X1_IfcPositiveRatioMeasure_type = 0;
type_declaration* IFC4X1_IfcPowerMeasure_type = 0;
type_declaration* IFC4X1_IfcPresentableText_type = 0;
type_declaration* IFC4X1_IfcPressureMeasure_type = 0;
type_declaration* IFC4X1_IfcPropertySetDefinitionSet_type = 0;
type_declaration* IFC4X1_IfcRadioActivityMeasure_type = 0;
type_declaration* IFC4X1_IfcRatioMeasure_type = 0;
type_declaration* IFC4X1_IfcReal_type = 0;
type_declaration* IFC4X1_IfcRotationalFrequencyMeasure_type = 0;
type_declaration* IFC4X1_IfcRotationalMassMeasure_type = 0;
type_declaration* IFC4X1_IfcRotationalStiffnessMeasure_type = 0;
type_declaration* IFC4X1_IfcSectionModulusMeasure_type = 0;
type_declaration* IFC4X1_IfcSectionalAreaIntegralMeasure_type = 0;
type_declaration* IFC4X1_IfcShearModulusMeasure_type = 0;
type_declaration* IFC4X1_IfcSolidAngleMeasure_type = 0;
type_declaration* IFC4X1_IfcSoundPowerLevelMeasure_type = 0;
type_declaration* IFC4X1_IfcSoundPowerMeasure_type = 0;
type_declaration* IFC4X1_IfcSoundPressureLevelMeasure_type = 0;
type_declaration* IFC4X1_IfcSoundPressureMeasure_type = 0;
type_declaration* IFC4X1_IfcSpecificHeatCapacityMeasure_type = 0;
type_declaration* IFC4X1_IfcSpecularExponent_type = 0;
type_declaration* IFC4X1_IfcSpecularRoughness_type = 0;
type_declaration* IFC4X1_IfcTemperatureGradientMeasure_type = 0;
type_declaration* IFC4X1_IfcTemperatureRateOfChangeMeasure_type = 0;
type_declaration* IFC4X1_IfcText_type = 0;
type_declaration* IFC4X1_IfcTextAlignment_type = 0;
type_declaration* IFC4X1_IfcTextDecoration_type = 0;
type_declaration* IFC4X1_IfcTextFontName_type = 0;
type_declaration* IFC4X1_IfcTextTransformation_type = 0;
type_declaration* IFC4X1_IfcThermalAdmittanceMeasure_type = 0;
type_declaration* IFC4X1_IfcThermalConductivityMeasure_type = 0;
type_declaration* IFC4X1_IfcThermalExpansionCoefficientMeasure_type = 0;
type_declaration* IFC4X1_IfcThermalResistanceMeasure_type = 0;
type_declaration* IFC4X1_IfcThermalTransmittanceMeasure_type = 0;
type_declaration* IFC4X1_IfcThermodynamicTemperatureMeasure_type = 0;
type_declaration* IFC4X1_IfcTime_type = 0;
type_declaration* IFC4X1_IfcTimeMeasure_type = 0;
type_declaration* IFC4X1_IfcTimeStamp_type = 0;
type_declaration* IFC4X1_IfcTorqueMeasure_type = 0;
type_declaration* IFC4X1_IfcURIReference_type = 0;
type_declaration* IFC4X1_IfcVaporPermeabilityMeasure_type = 0;
type_declaration* IFC4X1_IfcVolumeMeasure_type = 0;
type_declaration* IFC4X1_IfcVolumetricFlowRateMeasure_type = 0;
type_declaration* IFC4X1_IfcWarpingConstantMeasure_type = 0;
type_declaration* IFC4X1_IfcWarpingMomentMeasure_type = 0;
select_type* IFC4X1_IfcActorSelect_type = 0;
select_type* IFC4X1_IfcAppliedValueSelect_type = 0;
select_type* IFC4X1_IfcAxis2Placement_type = 0;
select_type* IFC4X1_IfcBendingParameterSelect_type = 0;
select_type* IFC4X1_IfcBooleanOperand_type = 0;
select_type* IFC4X1_IfcClassificationReferenceSelect_type = 0;
select_type* IFC4X1_IfcClassificationSelect_type = 0;
select_type* IFC4X1_IfcColour_type = 0;
select_type* IFC4X1_IfcColourOrFactor_type = 0;
select_type* IFC4X1_IfcCoordinateReferenceSystemSelect_type = 0;
select_type* IFC4X1_IfcCsgSelect_type = 0;
select_type* IFC4X1_IfcCurveFontOrScaledCurveFontSelect_type = 0;
select_type* IFC4X1_IfcCurveOnSurface_type = 0;
select_type* IFC4X1_IfcCurveOrEdgeCurve_type = 0;
select_type* IFC4X1_IfcCurveStyleFontSelect_type = 0;
select_type* IFC4X1_IfcDefinitionSelect_type = 0;
select_type* IFC4X1_IfcDerivedMeasureValue_type = 0;
select_type* IFC4X1_IfcDocumentSelect_type = 0;
select_type* IFC4X1_IfcFillStyleSelect_type = 0;
select_type* IFC4X1_IfcGeometricSetSelect_type = 0;
select_type* IFC4X1_IfcGridPlacementDirectionSelect_type = 0;
select_type* IFC4X1_IfcHatchLineDistanceSelect_type = 0;
select_type* IFC4X1_IfcLayeredItem_type = 0;
select_type* IFC4X1_IfcLibrarySelect_type = 0;
select_type* IFC4X1_IfcLightDistributionDataSourceSelect_type = 0;
select_type* IFC4X1_IfcMaterialSelect_type = 0;
select_type* IFC4X1_IfcMeasureValue_type = 0;
select_type* IFC4X1_IfcMetricValueSelect_type = 0;
select_type* IFC4X1_IfcModulusOfRotationalSubgradeReactionSelect_type = 0;
select_type* IFC4X1_IfcModulusOfSubgradeReactionSelect_type = 0;
select_type* IFC4X1_IfcModulusOfTranslationalSubgradeReactionSelect_type = 0;
select_type* IFC4X1_IfcObjectReferenceSelect_type = 0;
select_type* IFC4X1_IfcPointOrVertexPoint_type = 0;
select_type* IFC4X1_IfcPresentationStyleSelect_type = 0;
select_type* IFC4X1_IfcProcessSelect_type = 0;
select_type* IFC4X1_IfcProductRepresentationSelect_type = 0;
select_type* IFC4X1_IfcProductSelect_type = 0;
select_type* IFC4X1_IfcPropertySetDefinitionSelect_type = 0;
select_type* IFC4X1_IfcResourceObjectSelect_type = 0;
select_type* IFC4X1_IfcResourceSelect_type = 0;
select_type* IFC4X1_IfcRotationalStiffnessSelect_type = 0;
select_type* IFC4X1_IfcSegmentIndexSelect_type = 0;
select_type* IFC4X1_IfcShell_type = 0;
select_type* IFC4X1_IfcSimpleValue_type = 0;
select_type* IFC4X1_IfcSizeSelect_type = 0;
select_type* IFC4X1_IfcSolidOrShell_type = 0;
select_type* IFC4X1_IfcSpaceBoundarySelect_type = 0;
select_type* IFC4X1_IfcSpecularHighlightSelect_type = 0;
select_type* IFC4X1_IfcStructuralActivityAssignmentSelect_type = 0;
select_type* IFC4X1_IfcStyleAssignmentSelect_type = 0;
select_type* IFC4X1_IfcSurfaceOrFaceSurface_type = 0;
select_type* IFC4X1_IfcSurfaceStyleElementSelect_type = 0;
select_type* IFC4X1_IfcTextFontSelect_type = 0;
select_type* IFC4X1_IfcTimeOrRatioSelect_type = 0;
select_type* IFC4X1_IfcTranslationalStiffnessSelect_type = 0;
select_type* IFC4X1_IfcTrimmingSelect_type = 0;
select_type* IFC4X1_IfcUnit_type = 0;
select_type* IFC4X1_IfcValue_type = 0;
select_type* IFC4X1_IfcVectorOrDirection_type = 0;
select_type* IFC4X1_IfcWarpingStiffnessSelect_type = 0;
enumeration_type* IFC4X1_IfcActionRequestTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcActionSourceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcActionTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcActuatorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcAddressTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcAirTerminalBoxTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcAirTerminalTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcAirToAirHeatRecoveryTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcAlarmTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcAlignmentTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcAnalysisModelTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcAnalysisTheoryTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcArithmeticOperatorEnum_type = 0;
enumeration_type* IFC4X1_IfcAssemblyPlaceEnum_type = 0;
enumeration_type* IFC4X1_IfcAudioVisualApplianceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcBSplineCurveForm_type = 0;
enumeration_type* IFC4X1_IfcBSplineSurfaceForm_type = 0;
enumeration_type* IFC4X1_IfcBeamTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcBenchmarkEnum_type = 0;
enumeration_type* IFC4X1_IfcBoilerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcBooleanOperator_type = 0;
enumeration_type* IFC4X1_IfcBuildingElementPartTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcBuildingElementProxyTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcBuildingSystemTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcBurnerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCableCarrierFittingTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCableCarrierSegmentTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCableFittingTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCableSegmentTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcChangeActionEnum_type = 0;
enumeration_type* IFC4X1_IfcChillerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcChimneyTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCoilTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcColumnTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCommunicationsApplianceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcComplexPropertyTemplateTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCompressorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCondenserTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcConnectionTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcConstraintEnum_type = 0;
enumeration_type* IFC4X1_IfcConstructionEquipmentResourceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcConstructionMaterialResourceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcConstructionProductResourceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcControllerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCooledBeamTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCoolingTowerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCostItemTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCostScheduleTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCoveringTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCrewResourceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCurtainWallTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcCurveInterpolationEnum_type = 0;
enumeration_type* IFC4X1_IfcDamperTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcDataOriginEnum_type = 0;
enumeration_type* IFC4X1_IfcDerivedUnitEnum_type = 0;
enumeration_type* IFC4X1_IfcDirectionSenseEnum_type = 0;
enumeration_type* IFC4X1_IfcDiscreteAccessoryTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcDistributionChamberElementTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcDistributionPortTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcDistributionSystemEnum_type = 0;
enumeration_type* IFC4X1_IfcDocumentConfidentialityEnum_type = 0;
enumeration_type* IFC4X1_IfcDocumentStatusEnum_type = 0;
enumeration_type* IFC4X1_IfcDoorPanelOperationEnum_type = 0;
enumeration_type* IFC4X1_IfcDoorPanelPositionEnum_type = 0;
enumeration_type* IFC4X1_IfcDoorStyleConstructionEnum_type = 0;
enumeration_type* IFC4X1_IfcDoorStyleOperationEnum_type = 0;
enumeration_type* IFC4X1_IfcDoorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcDoorTypeOperationEnum_type = 0;
enumeration_type* IFC4X1_IfcDuctFittingTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcDuctSegmentTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcDuctSilencerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcElectricApplianceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcElectricDistributionBoardTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcElectricFlowStorageDeviceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcElectricGeneratorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcElectricMotorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcElectricTimeControlTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcElementAssemblyTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcElementCompositionEnum_type = 0;
enumeration_type* IFC4X1_IfcEngineTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcEvaporativeCoolerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcEvaporatorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcEventTriggerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcEventTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcExternalSpatialElementTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcFanTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcFastenerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcFilterTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcFireSuppressionTerminalTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcFlowDirectionEnum_type = 0;
enumeration_type* IFC4X1_IfcFlowInstrumentTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcFlowMeterTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcFootingTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcFurnitureTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcGeographicElementTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcGeometricProjectionEnum_type = 0;
enumeration_type* IFC4X1_IfcGlobalOrLocalEnum_type = 0;
enumeration_type* IFC4X1_IfcGridTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcHeatExchangerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcHumidifierTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcInterceptorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcInternalOrExternalEnum_type = 0;
enumeration_type* IFC4X1_IfcInventoryTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcJunctionBoxTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcKnotType_type = 0;
enumeration_type* IFC4X1_IfcLaborResourceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcLampTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcLayerSetDirectionEnum_type = 0;
enumeration_type* IFC4X1_IfcLightDistributionCurveEnum_type = 0;
enumeration_type* IFC4X1_IfcLightEmissionSourceEnum_type = 0;
enumeration_type* IFC4X1_IfcLightFixtureTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcLoadGroupTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcLogicalOperatorEnum_type = 0;
enumeration_type* IFC4X1_IfcMechanicalFastenerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcMedicalDeviceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcMemberTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcMotorConnectionTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcNullStyle_type = 0;
enumeration_type* IFC4X1_IfcObjectTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcObjectiveEnum_type = 0;
enumeration_type* IFC4X1_IfcOccupantTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcOpeningElementTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcOutletTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPerformanceHistoryTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPermeableCoveringOperationEnum_type = 0;
enumeration_type* IFC4X1_IfcPermitTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPhysicalOrVirtualEnum_type = 0;
enumeration_type* IFC4X1_IfcPileConstructionEnum_type = 0;
enumeration_type* IFC4X1_IfcPileTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPipeFittingTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPipeSegmentTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPlateTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPreferredSurfaceCurveRepresentation_type = 0;
enumeration_type* IFC4X1_IfcProcedureTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcProfileTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcProjectOrderTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcProjectedOrTrueLengthEnum_type = 0;
enumeration_type* IFC4X1_IfcProjectionElementTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPropertySetTemplateTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcProtectiveDeviceTrippingUnitTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcProtectiveDeviceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcPumpTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcRailingTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcRampFlightTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcRampTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcRecurrenceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcReferentTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcReflectanceMethodEnum_type = 0;
enumeration_type* IFC4X1_IfcReinforcingBarRoleEnum_type = 0;
enumeration_type* IFC4X1_IfcReinforcingBarSurfaceEnum_type = 0;
enumeration_type* IFC4X1_IfcReinforcingBarTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcReinforcingMeshTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcRoleEnum_type = 0;
enumeration_type* IFC4X1_IfcRoofTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSIPrefix_type = 0;
enumeration_type* IFC4X1_IfcSIUnitName_type = 0;
enumeration_type* IFC4X1_IfcSanitaryTerminalTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSectionTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSensorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSequenceEnum_type = 0;
enumeration_type* IFC4X1_IfcShadingDeviceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSimplePropertyTemplateTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSlabTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSolarDeviceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSpaceHeaterTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSpaceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSpatialZoneTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcStackTerminalTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcStairFlightTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcStairTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcStateEnum_type = 0;
enumeration_type* IFC4X1_IfcStructuralCurveActivityTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcStructuralCurveMemberTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcStructuralSurfaceActivityTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcStructuralSurfaceMemberTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSubContractResourceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSurfaceFeatureTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSurfaceSide_type = 0;
enumeration_type* IFC4X1_IfcSwitchingDeviceTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcSystemFurnitureElementTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcTankTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcTaskDurationEnum_type = 0;
enumeration_type* IFC4X1_IfcTaskTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcTendonAnchorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcTendonTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcTextPath_type = 0;
enumeration_type* IFC4X1_IfcTimeSeriesDataTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcTransformerTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcTransitionCode_type = 0;
enumeration_type* IFC4X1_IfcTransitionCurveType_type = 0;
enumeration_type* IFC4X1_IfcTransportElementTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcTrimmingPreference_type = 0;
enumeration_type* IFC4X1_IfcTubeBundleTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcUnitEnum_type = 0;
enumeration_type* IFC4X1_IfcUnitaryControlElementTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcUnitaryEquipmentTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcValveTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcVibrationIsolatorTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcVoidingFeatureTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcWallTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcWasteTerminalTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcWindowPanelOperationEnum_type = 0;
enumeration_type* IFC4X1_IfcWindowPanelPositionEnum_type = 0;
enumeration_type* IFC4X1_IfcWindowStyleConstructionEnum_type = 0;
enumeration_type* IFC4X1_IfcWindowStyleOperationEnum_type = 0;
enumeration_type* IFC4X1_IfcWindowTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcWindowTypePartitioningEnum_type = 0;
enumeration_type* IFC4X1_IfcWorkCalendarTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcWorkPlanTypeEnum_type = 0;
enumeration_type* IFC4X1_IfcWorkScheduleTypeEnum_type = 0;

class IFC4X1_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        switch(data->type()->index_in_schema()) {
            case 0: return new ::Ifc4x1::IfcAbsorbedDoseMeasure(data);
            case 1: return new ::Ifc4x1::IfcAccelerationMeasure(data);
            case 2: return new ::Ifc4x1::IfcActionRequest(data);
            case 3: return new ::Ifc4x1::IfcActionRequestTypeEnum(data);
            case 4: return new ::Ifc4x1::IfcActionSourceTypeEnum(data);
            case 5: return new ::Ifc4x1::IfcActionTypeEnum(data);
            case 6: return new ::Ifc4x1::IfcActor(data);
            case 7: return new ::Ifc4x1::IfcActorRole(data);
            case 9: return new ::Ifc4x1::IfcActuator(data);
            case 10: return new ::Ifc4x1::IfcActuatorType(data);
            case 11: return new ::Ifc4x1::IfcActuatorTypeEnum(data);
            case 12: return new ::Ifc4x1::IfcAddress(data);
            case 13: return new ::Ifc4x1::IfcAddressTypeEnum(data);
            case 14: return new ::Ifc4x1::IfcAdvancedBrep(data);
            case 15: return new ::Ifc4x1::IfcAdvancedBrepWithVoids(data);
            case 16: return new ::Ifc4x1::IfcAdvancedFace(data);
            case 17: return new ::Ifc4x1::IfcAirTerminal(data);
            case 18: return new ::Ifc4x1::IfcAirTerminalBox(data);
            case 19: return new ::Ifc4x1::IfcAirTerminalBoxType(data);
            case 20: return new ::Ifc4x1::IfcAirTerminalBoxTypeEnum(data);
            case 21: return new ::Ifc4x1::IfcAirTerminalType(data);
            case 22: return new ::Ifc4x1::IfcAirTerminalTypeEnum(data);
            case 23: return new ::Ifc4x1::IfcAirToAirHeatRecovery(data);
            case 24: return new ::Ifc4x1::IfcAirToAirHeatRecoveryType(data);
            case 25: return new ::Ifc4x1::IfcAirToAirHeatRecoveryTypeEnum(data);
            case 26: return new ::Ifc4x1::IfcAlarm(data);
            case 27: return new ::Ifc4x1::IfcAlarmType(data);
            case 28: return new ::Ifc4x1::IfcAlarmTypeEnum(data);
            case 29: return new ::Ifc4x1::IfcAlignment(data);
            case 30: return new ::Ifc4x1::IfcAlignment2DHorizontal(data);
            case 31: return new ::Ifc4x1::IfcAlignment2DHorizontalSegment(data);
            case 32: return new ::Ifc4x1::IfcAlignment2DSegment(data);
            case 33: return new ::Ifc4x1::IfcAlignment2DVerSegCircularArc(data);
            case 34: return new ::Ifc4x1::IfcAlignment2DVerSegLine(data);
            case 35: return new ::Ifc4x1::IfcAlignment2DVerSegParabolicArc(data);
            case 36: return new ::Ifc4x1::IfcAlignment2DVertical(data);
            case 37: return new ::Ifc4x1::IfcAlignment2DVerticalSegment(data);
            case 38: return new ::Ifc4x1::IfcAlignmentCurve(data);
            case 39: return new ::Ifc4x1::IfcAlignmentTypeEnum(data);
            case 40: return new ::Ifc4x1::IfcAmountOfSubstanceMeasure(data);
            case 41: return new ::Ifc4x1::IfcAnalysisModelTypeEnum(data);
            case 42: return new ::Ifc4x1::IfcAnalysisTheoryTypeEnum(data);
            case 43: return new ::Ifc4x1::IfcAngularVelocityMeasure(data);
            case 44: return new ::Ifc4x1::IfcAnnotation(data);
            case 45: return new ::Ifc4x1::IfcAnnotationFillArea(data);
            case 46: return new ::Ifc4x1::IfcApplication(data);
            case 47: return new ::Ifc4x1::IfcAppliedValue(data);
            case 49: return new ::Ifc4x1::IfcApproval(data);
            case 50: return new ::Ifc4x1::IfcApprovalRelationship(data);
            case 51: return new ::Ifc4x1::IfcArbitraryClosedProfileDef(data);
            case 52: return new ::Ifc4x1::IfcArbitraryOpenProfileDef(data);
            case 53: return new ::Ifc4x1::IfcArbitraryProfileDefWithVoids(data);
            case 54: return new ::Ifc4x1::IfcArcIndex(data);
            case 55: return new ::Ifc4x1::IfcAreaDensityMeasure(data);
            case 56: return new ::Ifc4x1::IfcAreaMeasure(data);
            case 57: return new ::Ifc4x1::IfcArithmeticOperatorEnum(data);
            case 58: return new ::Ifc4x1::IfcAssemblyPlaceEnum(data);
            case 59: return new ::Ifc4x1::IfcAsset(data);
            case 60: return new ::Ifc4x1::IfcAsymmetricIShapeProfileDef(data);
            case 61: return new ::Ifc4x1::IfcAudioVisualAppliance(data);
            case 62: return new ::Ifc4x1::IfcAudioVisualApplianceType(data);
            case 63: return new ::Ifc4x1::IfcAudioVisualApplianceTypeEnum(data);
            case 64: return new ::Ifc4x1::IfcAxis1Placement(data);
            case 66: return new ::Ifc4x1::IfcAxis2Placement2D(data);
            case 67: return new ::Ifc4x1::IfcAxis2Placement3D(data);
            case 68: return new ::Ifc4x1::IfcBeam(data);
            case 69: return new ::Ifc4x1::IfcBeamStandardCase(data);
            case 70: return new ::Ifc4x1::IfcBeamType(data);
            case 71: return new ::Ifc4x1::IfcBeamTypeEnum(data);
            case 72: return new ::Ifc4x1::IfcBenchmarkEnum(data);
            case 74: return new ::Ifc4x1::IfcBinary(data);
            case 75: return new ::Ifc4x1::IfcBlobTexture(data);
            case 76: return new ::Ifc4x1::IfcBlock(data);
            case 77: return new ::Ifc4x1::IfcBoiler(data);
            case 78: return new ::Ifc4x1::IfcBoilerType(data);
            case 79: return new ::Ifc4x1::IfcBoilerTypeEnum(data);
            case 80: return new ::Ifc4x1::IfcBoolean(data);
            case 81: return new ::Ifc4x1::IfcBooleanClippingResult(data);
            case 83: return new ::Ifc4x1::IfcBooleanOperator(data);
            case 84: return new ::Ifc4x1::IfcBooleanResult(data);
            case 85: return new ::Ifc4x1::IfcBoundaryCondition(data);
            case 86: return new ::Ifc4x1::IfcBoundaryCurve(data);
            case 87: return new ::Ifc4x1::IfcBoundaryEdgeCondition(data);
            case 88: return new ::Ifc4x1::IfcBoundaryFaceCondition(data);
            case 89: return new ::Ifc4x1::IfcBoundaryNodeCondition(data);
            case 90: return new ::Ifc4x1::IfcBoundaryNodeConditionWarping(data);
            case 91: return new ::Ifc4x1::IfcBoundedCurve(data);
            case 92: return new ::Ifc4x1::IfcBoundedSurface(data);
            case 93: return new ::Ifc4x1::IfcBoundingBox(data);
            case 94: return new ::Ifc4x1::IfcBoxAlignment(data);
            case 95: return new ::Ifc4x1::IfcBoxedHalfSpace(data);
            case 96: return new ::Ifc4x1::IfcBSplineCurve(data);
            case 97: return new ::Ifc4x1::IfcBSplineCurveForm(data);
            case 98: return new ::Ifc4x1::IfcBSplineCurveWithKnots(data);
            case 99: return new ::Ifc4x1::IfcBSplineSurface(data);
            case 100: return new ::Ifc4x1::IfcBSplineSurfaceForm(data);
            case 101: return new ::Ifc4x1::IfcBSplineSurfaceWithKnots(data);
            case 102: return new ::Ifc4x1::IfcBuilding(data);
            case 103: return new ::Ifc4x1::IfcBuildingElement(data);
            case 104: return new ::Ifc4x1::IfcBuildingElementPart(data);
            case 105: return new ::Ifc4x1::IfcBuildingElementPartType(data);
            case 106: return new ::Ifc4x1::IfcBuildingElementPartTypeEnum(data);
            case 107: return new ::Ifc4x1::IfcBuildingElementProxy(data);
            case 108: return new ::Ifc4x1::IfcBuildingElementProxyType(data);
            case 109: return new ::Ifc4x1::IfcBuildingElementProxyTypeEnum(data);
            case 110: return new ::Ifc4x1::IfcBuildingElementType(data);
            case 111: return new ::Ifc4x1::IfcBuildingStorey(data);
            case 112: return new ::Ifc4x1::IfcBuildingSystem(data);
            case 113: return new ::Ifc4x1::IfcBuildingSystemTypeEnum(data);
            case 114: return new ::Ifc4x1::IfcBurner(data);
            case 115: return new ::Ifc4x1::IfcBurnerType(data);
            case 116: return new ::Ifc4x1::IfcBurnerTypeEnum(data);
            case 117: return new ::Ifc4x1::IfcCableCarrierFitting(data);
            case 118: return new ::Ifc4x1::IfcCableCarrierFittingType(data);
            case 119: return new ::Ifc4x1::IfcCableCarrierFittingTypeEnum(data);
            case 120: return new ::Ifc4x1::IfcCableCarrierSegment(data);
            case 121: return new ::Ifc4x1::IfcCableCarrierSegmentType(data);
            case 122: return new ::Ifc4x1::IfcCableCarrierSegmentTypeEnum(data);
            case 123: return new ::Ifc4x1::IfcCableFitting(data);
            case 124: return new ::Ifc4x1::IfcCableFittingType(data);
            case 125: return new ::Ifc4x1::IfcCableFittingTypeEnum(data);
            case 126: return new ::Ifc4x1::IfcCableSegment(data);
            case 127: return new ::Ifc4x1::IfcCableSegmentType(data);
            case 128: return new ::Ifc4x1::IfcCableSegmentTypeEnum(data);
            case 129: return new ::Ifc4x1::IfcCardinalPointReference(data);
            case 130: return new ::Ifc4x1::IfcCartesianPoint(data);
            case 131: return new ::Ifc4x1::IfcCartesianPointList(data);
            case 132: return new ::Ifc4x1::IfcCartesianPointList2D(data);
            case 133: return new ::Ifc4x1::IfcCartesianPointList3D(data);
            case 134: return new ::Ifc4x1::IfcCartesianTransformationOperator(data);
            case 135: return new ::Ifc4x1::IfcCartesianTransformationOperator2D(data);
            case 136: return new ::Ifc4x1::IfcCartesianTransformationOperator2DnonUniform(data);
            case 137: return new ::Ifc4x1::IfcCartesianTransformationOperator3D(data);
            case 138: return new ::Ifc4x1::IfcCartesianTransformationOperator3DnonUniform(data);
            case 139: return new ::Ifc4x1::IfcCenterLineProfileDef(data);
            case 140: return new ::Ifc4x1::IfcChangeActionEnum(data);
            case 141: return new ::Ifc4x1::IfcChiller(data);
            case 142: return new ::Ifc4x1::IfcChillerType(data);
            case 143: return new ::Ifc4x1::IfcChillerTypeEnum(data);
            case 144: return new ::Ifc4x1::IfcChimney(data);
            case 145: return new ::Ifc4x1::IfcChimneyType(data);
            case 146: return new ::Ifc4x1::IfcChimneyTypeEnum(data);
            case 147: return new ::Ifc4x1::IfcCircle(data);
            case 148: return new ::Ifc4x1::IfcCircleHollowProfileDef(data);
            case 149: return new ::Ifc4x1::IfcCircleProfileDef(data);
            case 150: return new ::Ifc4x1::IfcCircularArcSegment2D(data);
            case 151: return new ::Ifc4x1::IfcCivilElement(data);
            case 152: return new ::Ifc4x1::IfcCivilElementType(data);
            case 153: return new ::Ifc4x1::IfcClassification(data);
            case 154: return new ::Ifc4x1::IfcClassificationReference(data);
            case 157: return new ::Ifc4x1::IfcClosedShell(data);
            case 158: return new ::Ifc4x1::IfcCoil(data);
            case 159: return new ::Ifc4x1::IfcCoilType(data);
            case 160: return new ::Ifc4x1::IfcCoilTypeEnum(data);
            case 163: return new ::Ifc4x1::IfcColourRgb(data);
            case 164: return new ::Ifc4x1::IfcColourRgbList(data);
            case 165: return new ::Ifc4x1::IfcColourSpecification(data);
            case 166: return new ::Ifc4x1::IfcColumn(data);
            case 167: return new ::Ifc4x1::IfcColumnStandardCase(data);
            case 168: return new ::Ifc4x1::IfcColumnType(data);
            case 169: return new ::Ifc4x1::IfcColumnTypeEnum(data);
            case 170: return new ::Ifc4x1::IfcCommunicationsAppliance(data);
            case 171: return new ::Ifc4x1::IfcCommunicationsApplianceType(data);
            case 172: return new ::Ifc4x1::IfcCommunicationsApplianceTypeEnum(data);
            case 173: return new ::Ifc4x1::IfcComplexNumber(data);
            case 174: return new ::Ifc4x1::IfcComplexProperty(data);
            case 175: return new ::Ifc4x1::IfcComplexPropertyTemplate(data);
            case 176: return new ::Ifc4x1::IfcComplexPropertyTemplateTypeEnum(data);
            case 177: return new ::Ifc4x1::IfcCompositeCurve(data);
            case 178: return new ::Ifc4x1::IfcCompositeCurveOnSurface(data);
            case 179: return new ::Ifc4x1::IfcCompositeCurveSegment(data);
            case 180: return new ::Ifc4x1::IfcCompositeProfileDef(data);
            case 181: return new ::Ifc4x1::IfcCompoundPlaneAngleMeasure(data);
            case 182: return new ::Ifc4x1::IfcCompressor(data);
            case 183: return new ::Ifc4x1::IfcCompressorType(data);
            case 184: return new ::Ifc4x1::IfcCompressorTypeEnum(data);
            case 185: return new ::Ifc4x1::IfcCondenser(data);
            case 186: return new ::Ifc4x1::IfcCondenserType(data);
            case 187: return new ::Ifc4x1::IfcCondenserTypeEnum(data);
            case 188: return new ::Ifc4x1::IfcConic(data);
            case 189: return new ::Ifc4x1::IfcConnectedFaceSet(data);
            case 190: return new ::Ifc4x1::IfcConnectionCurveGeometry(data);
            case 191: return new ::Ifc4x1::IfcConnectionGeometry(data);
            case 192: return new ::Ifc4x1::IfcConnectionPointEccentricity(data);
            case 193: return new ::Ifc4x1::IfcConnectionPointGeometry(data);
            case 194: return new ::Ifc4x1::IfcConnectionSurfaceGeometry(data);
            case 195: return new ::Ifc4x1::IfcConnectionTypeEnum(data);
            case 196: return new ::Ifc4x1::IfcConnectionVolumeGeometry(data);
            case 197: return new ::Ifc4x1::IfcConstraint(data);
            case 198: return new ::Ifc4x1::IfcConstraintEnum(data);
            case 199: return new ::Ifc4x1::IfcConstructionEquipmentResource(data);
            case 200: return new ::Ifc4x1::IfcConstructionEquipmentResourceType(data);
            case 201: return new ::Ifc4x1::IfcConstructionEquipmentResourceTypeEnum(data);
            case 202: return new ::Ifc4x1::IfcConstructionMaterialResource(data);
            case 203: return new ::Ifc4x1::IfcConstructionMaterialResourceType(data);
            case 204: return new ::Ifc4x1::IfcConstructionMaterialResourceTypeEnum(data);
            case 205: return new ::Ifc4x1::IfcConstructionProductResource(data);
            case 206: return new ::Ifc4x1::IfcConstructionProductResourceType(data);
            case 207: return new ::Ifc4x1::IfcConstructionProductResourceTypeEnum(data);
            case 208: return new ::Ifc4x1::IfcConstructionResource(data);
            case 209: return new ::Ifc4x1::IfcConstructionResourceType(data);
            case 210: return new ::Ifc4x1::IfcContext(data);
            case 211: return new ::Ifc4x1::IfcContextDependentMeasure(data);
            case 212: return new ::Ifc4x1::IfcContextDependentUnit(data);
            case 213: return new ::Ifc4x1::IfcControl(data);
            case 214: return new ::Ifc4x1::IfcController(data);
            case 215: return new ::Ifc4x1::IfcControllerType(data);
            case 216: return new ::Ifc4x1::IfcControllerTypeEnum(data);
            case 217: return new ::Ifc4x1::IfcConversionBasedUnit(data);
            case 218: return new ::Ifc4x1::IfcConversionBasedUnitWithOffset(data);
            case 219: return new ::Ifc4x1::IfcCooledBeam(data);
            case 220: return new ::Ifc4x1::IfcCooledBeamType(data);
            case 221: return new ::Ifc4x1::IfcCooledBeamTypeEnum(data);
            case 222: return new ::Ifc4x1::IfcCoolingTower(data);
            case 223: return new ::Ifc4x1::IfcCoolingTowerType(data);
            case 224: return new ::Ifc4x1::IfcCoolingTowerTypeEnum(data);
            case 225: return new ::Ifc4x1::IfcCoordinateOperation(data);
            case 226: return new ::Ifc4x1::IfcCoordinateReferenceSystem(data);
            case 228: return new ::Ifc4x1::IfcCostItem(data);
            case 229: return new ::Ifc4x1::IfcCostItemTypeEnum(data);
            case 230: return new ::Ifc4x1::IfcCostSchedule(data);
            case 231: return new ::Ifc4x1::IfcCostScheduleTypeEnum(data);
            case 232: return new ::Ifc4x1::IfcCostValue(data);
            case 233: return new ::Ifc4x1::IfcCountMeasure(data);
            case 234: return new ::Ifc4x1::IfcCovering(data);
            case 235: return new ::Ifc4x1::IfcCoveringType(data);
            case 236: return new ::Ifc4x1::IfcCoveringTypeEnum(data);
            case 237: return new ::Ifc4x1::IfcCrewResource(data);
            case 238: return new ::Ifc4x1::IfcCrewResourceType(data);
            case 239: return new ::Ifc4x1::IfcCrewResourceTypeEnum(data);
            case 240: return new ::Ifc4x1::IfcCsgPrimitive3D(data);
            case 242: return new ::Ifc4x1::IfcCsgSolid(data);
            case 243: return new ::Ifc4x1::IfcCShapeProfileDef(data);
            case 244: return new ::Ifc4x1::IfcCurrencyRelationship(data);
            case 245: return new ::Ifc4x1::IfcCurtainWall(data);
            case 246: return new ::Ifc4x1::IfcCurtainWallType(data);
            case 247: return new ::Ifc4x1::IfcCurtainWallTypeEnum(data);
            case 248: return new ::Ifc4x1::IfcCurvatureMeasure(data);
            case 249: return new ::Ifc4x1::IfcCurve(data);
            case 250: return new ::Ifc4x1::IfcCurveBoundedPlane(data);
            case 251: return new ::Ifc4x1::IfcCurveBoundedSurface(data);
            case 253: return new ::Ifc4x1::IfcCurveInterpolationEnum(data);
            case 256: return new ::Ifc4x1::IfcCurveSegment2D(data);
            case 257: return new ::Ifc4x1::IfcCurveStyle(data);
            case 258: return new ::Ifc4x1::IfcCurveStyleFont(data);
            case 259: return new ::Ifc4x1::IfcCurveStyleFontAndScaling(data);
            case 260: return new ::Ifc4x1::IfcCurveStyleFontPattern(data);
            case 262: return new ::Ifc4x1::IfcCylindricalSurface(data);
            case 263: return new ::Ifc4x1::IfcDamper(data);
            case 264: return new ::Ifc4x1::IfcDamperType(data);
            case 265: return new ::Ifc4x1::IfcDamperTypeEnum(data);
            case 266: return new ::Ifc4x1::IfcDataOriginEnum(data);
            case 267: return new ::Ifc4x1::IfcDate(data);
            case 268: return new ::Ifc4x1::IfcDateTime(data);
            case 269: return new ::Ifc4x1::IfcDayInMonthNumber(data);
            case 270: return new ::Ifc4x1::IfcDayInWeekNumber(data);
            case 273: return new ::Ifc4x1::IfcDerivedProfileDef(data);
            case 274: return new ::Ifc4x1::IfcDerivedUnit(data);
            case 275: return new ::Ifc4x1::IfcDerivedUnitElement(data);
            case 276: return new ::Ifc4x1::IfcDerivedUnitEnum(data);
            case 277: return new ::Ifc4x1::IfcDescriptiveMeasure(data);
            case 278: return new ::Ifc4x1::IfcDimensionalExponents(data);
            case 279: return new ::Ifc4x1::IfcDimensionCount(data);
            case 280: return new ::Ifc4x1::IfcDirection(data);
            case 281: return new ::Ifc4x1::IfcDirectionSenseEnum(data);
            case 282: return new ::Ifc4x1::IfcDiscreteAccessory(data);
            case 283: return new ::Ifc4x1::IfcDiscreteAccessoryType(data);
            case 284: return new ::Ifc4x1::IfcDiscreteAccessoryTypeEnum(data);
            case 285: return new ::Ifc4x1::IfcDistanceExpression(data);
            case 286: return new ::Ifc4x1::IfcDistributionChamberElement(data);
            case 287: return new ::Ifc4x1::IfcDistributionChamberElementType(data);
            case 288: return new ::Ifc4x1::IfcDistributionChamberElementTypeEnum(data);
            case 289: return new ::Ifc4x1::IfcDistributionCircuit(data);
            case 290: return new ::Ifc4x1::IfcDistributionControlElement(data);
            case 291: return new ::Ifc4x1::IfcDistributionControlElementType(data);
            case 292: return new ::Ifc4x1::IfcDistributionElement(data);
            case 293: return new ::Ifc4x1::IfcDistributionElementType(data);
            case 294: return new ::Ifc4x1::IfcDistributionFlowElement(data);
            case 295: return new ::Ifc4x1::IfcDistributionFlowElementType(data);
            case 296: return new ::Ifc4x1::IfcDistributionPort(data);
            case 297: return new ::Ifc4x1::IfcDistributionPortTypeEnum(data);
            case 298: return new ::Ifc4x1::IfcDistributionSystem(data);
            case 299: return new ::Ifc4x1::IfcDistributionSystemEnum(data);
            case 300: return new ::Ifc4x1::IfcDocumentConfidentialityEnum(data);
            case 301: return new ::Ifc4x1::IfcDocumentInformation(data);
            case 302: return new ::Ifc4x1::IfcDocumentInformationRelationship(data);
            case 303: return new ::Ifc4x1::IfcDocumentReference(data);
            case 305: return new ::Ifc4x1::IfcDocumentStatusEnum(data);
            case 306: return new ::Ifc4x1::IfcDoor(data);
            case 307: return new ::Ifc4x1::IfcDoorLiningProperties(data);
            case 308: return new ::Ifc4x1::IfcDoorPanelOperationEnum(data);
            case 309: return new ::Ifc4x1::IfcDoorPanelPositionEnum(data);
            case 310: return new ::Ifc4x1::IfcDoorPanelProperties(data);
            case 311: return new ::Ifc4x1::IfcDoorStandardCase(data);
            case 312: return new ::Ifc4x1::IfcDoorStyle(data);
            case 313: return new ::Ifc4x1::IfcDoorStyleConstructionEnum(data);
            case 314: return new ::Ifc4x1::IfcDoorStyleOperationEnum(data);
            case 315: return new ::Ifc4x1::IfcDoorType(data);
            case 316: return new ::Ifc4x1::IfcDoorTypeEnum(data);
            case 317: return new ::Ifc4x1::IfcDoorTypeOperationEnum(data);
            case 318: return new ::Ifc4x1::IfcDoseEquivalentMeasure(data);
            case 319: return new ::Ifc4x1::IfcDraughtingPreDefinedColour(data);
            case 320: return new ::Ifc4x1::IfcDraughtingPreDefinedCurveFont(data);
            case 321: return new ::Ifc4x1::IfcDuctFitting(data);
            case 322: return new ::Ifc4x1::IfcDuctFittingType(data);
            case 323: return new ::Ifc4x1::IfcDuctFittingTypeEnum(data);
            case 324: return new ::Ifc4x1::IfcDuctSegment(data);
            case 325: return new ::Ifc4x1::IfcDuctSegmentType(data);
            case 326: return new ::Ifc4x1::IfcDuctSegmentTypeEnum(data);
            case 327: return new ::Ifc4x1::IfcDuctSilencer(data);
            case 328: return new ::Ifc4x1::IfcDuctSilencerType(data);
            case 329: return new ::Ifc4x1::IfcDuctSilencerTypeEnum(data);
            case 330: return new ::Ifc4x1::IfcDuration(data);
            case 331: return new ::Ifc4x1::IfcDynamicViscosityMeasure(data);
            case 332: return new ::Ifc4x1::IfcEdge(data);
            case 333: return new ::Ifc4x1::IfcEdgeCurve(data);
            case 334: return new ::Ifc4x1::IfcEdgeLoop(data);
            case 335: return new ::Ifc4x1::IfcElectricAppliance(data);
            case 336: return new ::Ifc4x1::IfcElectricApplianceType(data);
            case 337: return new ::Ifc4x1::IfcElectricApplianceTypeEnum(data);
            case 338: return new ::Ifc4x1::IfcElectricCapacitanceMeasure(data);
            case 339: return new ::Ifc4x1::IfcElectricChargeMeasure(data);
            case 340: return new ::Ifc4x1::IfcElectricConductanceMeasure(data);
            case 341: return new ::Ifc4x1::IfcElectricCurrentMeasure(data);
            case 342: return new ::Ifc4x1::IfcElectricDistributionBoard(data);
            case 343: return new ::Ifc4x1::IfcElectricDistributionBoardType(data);
            case 344: return new ::Ifc4x1::IfcElectricDistributionBoardTypeEnum(data);
            case 345: return new ::Ifc4x1::IfcElectricFlowStorageDevice(data);
            case 346: return new ::Ifc4x1::IfcElectricFlowStorageDeviceType(data);
            case 347: return new ::Ifc4x1::IfcElectricFlowStorageDeviceTypeEnum(data);
            case 348: return new ::Ifc4x1::IfcElectricGenerator(data);
            case 349: return new ::Ifc4x1::IfcElectricGeneratorType(data);
            case 350: return new ::Ifc4x1::IfcElectricGeneratorTypeEnum(data);
            case 351: return new ::Ifc4x1::IfcElectricMotor(data);
            case 352: return new ::Ifc4x1::IfcElectricMotorType(data);
            case 353: return new ::Ifc4x1::IfcElectricMotorTypeEnum(data);
            case 354: return new ::Ifc4x1::IfcElectricResistanceMeasure(data);
            case 355: return new ::Ifc4x1::IfcElectricTimeControl(data);
            case 356: return new ::Ifc4x1::IfcElectricTimeControlType(data);
            case 357: return new ::Ifc4x1::IfcElectricTimeControlTypeEnum(data);
            case 358: return new ::Ifc4x1::IfcElectricVoltageMeasure(data);
            case 359: return new ::Ifc4x1::IfcElement(data);
            case 360: return new ::Ifc4x1::IfcElementarySurface(data);
            case 361: return new ::Ifc4x1::IfcElementAssembly(data);
            case 362: return new ::Ifc4x1::IfcElementAssemblyType(data);
            case 363: return new ::Ifc4x1::IfcElementAssemblyTypeEnum(data);
            case 364: return new ::Ifc4x1::IfcElementComponent(data);
            case 365: return new ::Ifc4x1::IfcElementComponentType(data);
            case 366: return new ::Ifc4x1::IfcElementCompositionEnum(data);
            case 367: return new ::Ifc4x1::IfcElementQuantity(data);
            case 368: return new ::Ifc4x1::IfcElementType(data);
            case 369: return new ::Ifc4x1::IfcEllipse(data);
            case 370: return new ::Ifc4x1::IfcEllipseProfileDef(data);
            case 371: return new ::Ifc4x1::IfcEnergyConversionDevice(data);
            case 372: return new ::Ifc4x1::IfcEnergyConversionDeviceType(data);
            case 373: return new ::Ifc4x1::IfcEnergyMeasure(data);
            case 374: return new ::Ifc4x1::IfcEngine(data);
            case 375: return new ::Ifc4x1::IfcEngineType(data);
            case 376: return new ::Ifc4x1::IfcEngineTypeEnum(data);
            case 377: return new ::Ifc4x1::IfcEvaporativeCooler(data);
            case 378: return new ::Ifc4x1::IfcEvaporativeCoolerType(data);
            case 379: return new ::Ifc4x1::IfcEvaporativeCoolerTypeEnum(data);
            case 380: return new ::Ifc4x1::IfcEvaporator(data);
            case 381: return new ::Ifc4x1::IfcEvaporatorType(data);
            case 382: return new ::Ifc4x1::IfcEvaporatorTypeEnum(data);
            case 383: return new ::Ifc4x1::IfcEvent(data);
            case 384: return new ::Ifc4x1::IfcEventTime(data);
            case 385: return new ::Ifc4x1::IfcEventTriggerTypeEnum(data);
            case 386: return new ::Ifc4x1::IfcEventType(data);
            case 387: return new ::Ifc4x1::IfcEventTypeEnum(data);
            case 388: return new ::Ifc4x1::IfcExtendedProperties(data);
            case 389: return new ::Ifc4x1::IfcExternalInformation(data);
            case 390: return new ::Ifc4x1::IfcExternallyDefinedHatchStyle(data);
            case 391: return new ::Ifc4x1::IfcExternallyDefinedSurfaceStyle(data);
            case 392: return new ::Ifc4x1::IfcExternallyDefinedTextFont(data);
            case 393: return new ::Ifc4x1::IfcExternalReference(data);
            case 394: return new ::Ifc4x1::IfcExternalReferenceRelationship(data);
            case 395: return new ::Ifc4x1::IfcExternalSpatialElement(data);
            case 396: return new ::Ifc4x1::IfcExternalSpatialElementTypeEnum(data);
            case 397: return new ::Ifc4x1::IfcExternalSpatialStructureElement(data);
            case 398: return new ::Ifc4x1::IfcExtrudedAreaSolid(data);
            case 399: return new ::Ifc4x1::IfcExtrudedAreaSolidTapered(data);
            case 400: return new ::Ifc4x1::IfcFace(data);
            case 401: return new ::Ifc4x1::IfcFaceBasedSurfaceModel(data);
            case 402: return new ::Ifc4x1::IfcFaceBound(data);
            case 403: return new ::Ifc4x1::IfcFaceOuterBound(data);
            case 404: return new ::Ifc4x1::IfcFaceSurface(data);
            case 405: return new ::Ifc4x1::IfcFacetedBrep(data);
            case 406: return new ::Ifc4x1::IfcFacetedBrepWithVoids(data);
            case 407: return new ::Ifc4x1::IfcFailureConnectionCondition(data);
            case 408: return new ::Ifc4x1::IfcFan(data);
            case 409: return new ::Ifc4x1::IfcFanType(data);
            case 410: return new ::Ifc4x1::IfcFanTypeEnum(data);
            case 411: return new ::Ifc4x1::IfcFastener(data);
            case 412: return new ::Ifc4x1::IfcFastenerType(data);
            case 413: return new ::Ifc4x1::IfcFastenerTypeEnum(data);
            case 414: return new ::Ifc4x1::IfcFeatureElement(data);
            case 415: return new ::Ifc4x1::IfcFeatureElementAddition(data);
            case 416: return new ::Ifc4x1::IfcFeatureElementSubtraction(data);
            case 417: return new ::Ifc4x1::IfcFillAreaStyle(data);
            case 418: return new ::Ifc4x1::IfcFillAreaStyleHatching(data);
            case 419: return new ::Ifc4x1::IfcFillAreaStyleTiles(data);
            case 421: return new ::Ifc4x1::IfcFilter(data);
            case 422: return new ::Ifc4x1::IfcFilterType(data);
            case 423: return new ::Ifc4x1::IfcFilterTypeEnum(data);
            case 424: return new ::Ifc4x1::IfcFireSuppressionTerminal(data);
            case 425: return new ::Ifc4x1::IfcFireSuppressionTerminalType(data);
            case 426: return new ::Ifc4x1::IfcFireSuppressionTerminalTypeEnum(data);
            case 427: return new ::Ifc4x1::IfcFixedReferenceSweptAreaSolid(data);
            case 428: return new ::Ifc4x1::IfcFlowController(data);
            case 429: return new ::Ifc4x1::IfcFlowControllerType(data);
            case 430: return new ::Ifc4x1::IfcFlowDirectionEnum(data);
            case 431: return new ::Ifc4x1::IfcFlowFitting(data);
            case 432: return new ::Ifc4x1::IfcFlowFittingType(data);
            case 433: return new ::Ifc4x1::IfcFlowInstrument(data);
            case 434: return new ::Ifc4x1::IfcFlowInstrumentType(data);
            case 435: return new ::Ifc4x1::IfcFlowInstrumentTypeEnum(data);
            case 436: return new ::Ifc4x1::IfcFlowMeter(data);
            case 437: return new ::Ifc4x1::IfcFlowMeterType(data);
            case 438: return new ::Ifc4x1::IfcFlowMeterTypeEnum(data);
            case 439: return new ::Ifc4x1::IfcFlowMovingDevice(data);
            case 440: return new ::Ifc4x1::IfcFlowMovingDeviceType(data);
            case 441: return new ::Ifc4x1::IfcFlowSegment(data);
            case 442: return new ::Ifc4x1::IfcFlowSegmentType(data);
            case 443: return new ::Ifc4x1::IfcFlowStorageDevice(data);
            case 444: return new ::Ifc4x1::IfcFlowStorageDeviceType(data);
            case 445: return new ::Ifc4x1::IfcFlowTerminal(data);
            case 446: return new ::Ifc4x1::IfcFlowTerminalType(data);
            case 447: return new ::Ifc4x1::IfcFlowTreatmentDevice(data);
            case 448: return new ::Ifc4x1::IfcFlowTreatmentDeviceType(data);
            case 449: return new ::Ifc4x1::IfcFontStyle(data);
            case 450: return new ::Ifc4x1::IfcFontVariant(data);
            case 451: return new ::Ifc4x1::IfcFontWeight(data);
            case 452: return new ::Ifc4x1::IfcFooting(data);
            case 453: return new ::Ifc4x1::IfcFootingType(data);
            case 454: return new ::Ifc4x1::IfcFootingTypeEnum(data);
            case 455: return new ::Ifc4x1::IfcForceMeasure(data);
            case 456: return new ::Ifc4x1::IfcFrequencyMeasure(data);
            case 457: return new ::Ifc4x1::IfcFurnishingElement(data);
            case 458: return new ::Ifc4x1::IfcFurnishingElementType(data);
            case 459: return new ::Ifc4x1::IfcFurniture(data);
            case 460: return new ::Ifc4x1::IfcFurnitureType(data);
            case 461: return new ::Ifc4x1::IfcFurnitureTypeEnum(data);
            case 462: return new ::Ifc4x1::IfcGeographicElement(data);
            case 463: return new ::Ifc4x1::IfcGeographicElementType(data);
            case 464: return new ::Ifc4x1::IfcGeographicElementTypeEnum(data);
            case 465: return new ::Ifc4x1::IfcGeometricCurveSet(data);
            case 466: return new ::Ifc4x1::IfcGeometricProjectionEnum(data);
            case 467: return new ::Ifc4x1::IfcGeometricRepresentationContext(data);
            case 468: return new ::Ifc4x1::IfcGeometricRepresentationItem(data);
            case 469: return new ::Ifc4x1::IfcGeometricRepresentationSubContext(data);
            case 470: return new ::Ifc4x1::IfcGeometricSet(data);
            case 472: return new ::Ifc4x1::IfcGloballyUniqueId(data);
            case 473: return new ::Ifc4x1::IfcGlobalOrLocalEnum(data);
            case 474: return new ::Ifc4x1::IfcGrid(data);
            case 475: return new ::Ifc4x1::IfcGridAxis(data);
            case 476: return new ::Ifc4x1::IfcGridPlacement(data);
            case 478: return new ::Ifc4x1::IfcGridTypeEnum(data);
            case 479: return new ::Ifc4x1::IfcGroup(data);
            case 480: return new ::Ifc4x1::IfcHalfSpaceSolid(data);
            case 482: return new ::Ifc4x1::IfcHeatExchanger(data);
            case 483: return new ::Ifc4x1::IfcHeatExchangerType(data);
            case 484: return new ::Ifc4x1::IfcHeatExchangerTypeEnum(data);
            case 485: return new ::Ifc4x1::IfcHeatFluxDensityMeasure(data);
            case 486: return new ::Ifc4x1::IfcHeatingValueMeasure(data);
            case 487: return new ::Ifc4x1::IfcHumidifier(data);
            case 488: return new ::Ifc4x1::IfcHumidifierType(data);
            case 489: return new ::Ifc4x1::IfcHumidifierTypeEnum(data);
            case 490: return new ::Ifc4x1::IfcIdentifier(data);
            case 491: return new ::Ifc4x1::IfcIlluminanceMeasure(data);
            case 492: return new ::Ifc4x1::IfcImageTexture(data);
            case 493: return new ::Ifc4x1::IfcIndexedColourMap(data);
            case 494: return new ::Ifc4x1::IfcIndexedPolyCurve(data);
            case 495: return new ::Ifc4x1::IfcIndexedPolygonalFace(data);
            case 496: return new ::Ifc4x1::IfcIndexedPolygonalFaceWithVoids(data);
            case 497: return new ::Ifc4x1::IfcIndexedTextureMap(data);
            case 498: return new ::Ifc4x1::IfcIndexedTriangleTextureMap(data);
            case 499: return new ::Ifc4x1::IfcInductanceMeasure(data);
            case 500: return new ::Ifc4x1::IfcInteger(data);
            case 501: return new ::Ifc4x1::IfcIntegerCountRateMeasure(data);
            case 502: return new ::Ifc4x1::IfcInterceptor(data);
            case 503: return new ::Ifc4x1::IfcInterceptorType(data);
            case 504: return new ::Ifc4x1::IfcInterceptorTypeEnum(data);
            case 505: return new ::Ifc4x1::IfcInternalOrExternalEnum(data);
            case 506: return new ::Ifc4x1::IfcIntersectionCurve(data);
            case 507: return new ::Ifc4x1::IfcInventory(data);
            case 508: return new ::Ifc4x1::IfcInventoryTypeEnum(data);
            case 509: return new ::Ifc4x1::IfcIonConcentrationMeasure(data);
            case 510: return new ::Ifc4x1::IfcIrregularTimeSeries(data);
            case 511: return new ::Ifc4x1::IfcIrregularTimeSeriesValue(data);
            case 512: return new ::Ifc4x1::IfcIShapeProfileDef(data);
            case 513: return new ::Ifc4x1::IfcIsothermalMoistureCapacityMeasure(data);
            case 514: return new ::Ifc4x1::IfcJunctionBox(data);
            case 515: return new ::Ifc4x1::IfcJunctionBoxType(data);
            case 516: return new ::Ifc4x1::IfcJunctionBoxTypeEnum(data);
            case 517: return new ::Ifc4x1::IfcKinematicViscosityMeasure(data);
            case 518: return new ::Ifc4x1::IfcKnotType(data);
            case 519: return new ::Ifc4x1::IfcLabel(data);
            case 520: return new ::Ifc4x1::IfcLaborResource(data);
            case 521: return new ::Ifc4x1::IfcLaborResourceType(data);
            case 522: return new ::Ifc4x1::IfcLaborResourceTypeEnum(data);
            case 523: return new ::Ifc4x1::IfcLagTime(data);
            case 524: return new ::Ifc4x1::IfcLamp(data);
            case 525: return new ::Ifc4x1::IfcLampType(data);
            case 526: return new ::Ifc4x1::IfcLampTypeEnum(data);
            case 527: return new ::Ifc4x1::IfcLanguageId(data);
            case 529: return new ::Ifc4x1::IfcLayerSetDirectionEnum(data);
            case 530: return new ::Ifc4x1::IfcLengthMeasure(data);
            case 531: return new ::Ifc4x1::IfcLibraryInformation(data);
            case 532: return new ::Ifc4x1::IfcLibraryReference(data);
            case 534: return new ::Ifc4x1::IfcLightDistributionCurveEnum(data);
            case 535: return new ::Ifc4x1::IfcLightDistributionData(data);
            case 537: return new ::Ifc4x1::IfcLightEmissionSourceEnum(data);
            case 538: return new ::Ifc4x1::IfcLightFixture(data);
            case 539: return new ::Ifc4x1::IfcLightFixtureType(data);
            case 540: return new ::Ifc4x1::IfcLightFixtureTypeEnum(data);
            case 541: return new ::Ifc4x1::IfcLightIntensityDistribution(data);
            case 542: return new ::Ifc4x1::IfcLightSource(data);
            case 543: return new ::Ifc4x1::IfcLightSourceAmbient(data);
            case 544: return new ::Ifc4x1::IfcLightSourceDirectional(data);
            case 545: return new ::Ifc4x1::IfcLightSourceGoniometric(data);
            case 546: return new ::Ifc4x1::IfcLightSourcePositional(data);
            case 547: return new ::Ifc4x1::IfcLightSourceSpot(data);
            case 548: return new ::Ifc4x1::IfcLine(data);
            case 549: return new ::Ifc4x1::IfcLinearForceMeasure(data);
            case 550: return new ::Ifc4x1::IfcLinearMomentMeasure(data);
            case 551: return new ::Ifc4x1::IfcLinearPlacement(data);
            case 552: return new ::Ifc4x1::IfcLinearPositioningElement(data);
            case 553: return new ::Ifc4x1::IfcLinearStiffnessMeasure(data);
            case 554: return new ::Ifc4x1::IfcLinearVelocityMeasure(data);
            case 555: return new ::Ifc4x1::IfcLineIndex(data);
            case 556: return new ::Ifc4x1::IfcLineSegment2D(data);
            case 557: return new ::Ifc4x1::IfcLoadGroupTypeEnum(data);
            case 558: return new ::Ifc4x1::IfcLocalPlacement(data);
            case 559: return new ::Ifc4x1::IfcLogical(data);
            case 560: return new ::Ifc4x1::IfcLogicalOperatorEnum(data);
            case 561: return new ::Ifc4x1::IfcLoop(data);
            case 562: return new ::Ifc4x1::IfcLShapeProfileDef(data);
            case 563: return new ::Ifc4x1::IfcLuminousFluxMeasure(data);
            case 564: return new ::Ifc4x1::IfcLuminousIntensityDistributionMeasure(data);
            case 565: return new ::Ifc4x1::IfcLuminousIntensityMeasure(data);
            case 566: return new ::Ifc4x1::IfcMagneticFluxDensityMeasure(data);
            case 567: return new ::Ifc4x1::IfcMagneticFluxMeasure(data);
            case 568: return new ::Ifc4x1::IfcManifoldSolidBrep(data);
            case 569: return new ::Ifc4x1::IfcMapConversion(data);
            case 570: return new ::Ifc4x1::IfcMappedItem(data);
            case 571: return new ::Ifc4x1::IfcMassDensityMeasure(data);
            case 572: return new ::Ifc4x1::IfcMassFlowRateMeasure(data);
            case 573: return new ::Ifc4x1::IfcMassMeasure(data);
            case 574: return new ::Ifc4x1::IfcMassPerLengthMeasure(data);
            case 575: return new ::Ifc4x1::IfcMaterial(data);
            case 576: return new ::Ifc4x1::IfcMaterialClassificationRelationship(data);
            case 577: return new ::Ifc4x1::IfcMaterialConstituent(data);
            case 578: return new ::Ifc4x1::IfcMaterialConstituentSet(data);
            case 579: return new ::Ifc4x1::IfcMaterialDefinition(data);
            case 580: return new ::Ifc4x1::IfcMaterialDefinitionRepresentation(data);
            case 581: return new ::Ifc4x1::IfcMaterialLayer(data);
            case 582: return new ::Ifc4x1::IfcMaterialLayerSet(data);
            case 583: return new ::Ifc4x1::IfcMaterialLayerSetUsage(data);
            case 584: return new ::Ifc4x1::IfcMaterialLayerWithOffsets(data);
            case 585: return new ::Ifc4x1::IfcMaterialList(data);
            case 586: return new ::Ifc4x1::IfcMaterialProfile(data);
            case 587: return new ::Ifc4x1::IfcMaterialProfileSet(data);
            case 588: return new ::Ifc4x1::IfcMaterialProfileSetUsage(data);
            case 589: return new ::Ifc4x1::IfcMaterialProfileSetUsageTapering(data);
            case 590: return new ::Ifc4x1::IfcMaterialProfileWithOffsets(data);
            case 591: return new ::Ifc4x1::IfcMaterialProperties(data);
            case 592: return new ::Ifc4x1::IfcMaterialRelationship(data);
            case 594: return new ::Ifc4x1::IfcMaterialUsageDefinition(data);
            case 596: return new ::Ifc4x1::IfcMeasureWithUnit(data);
            case 597: return new ::Ifc4x1::IfcMechanicalFastener(data);
            case 598: return new ::Ifc4x1::IfcMechanicalFastenerType(data);
            case 599: return new ::Ifc4x1::IfcMechanicalFastenerTypeEnum(data);
            case 600: return new ::Ifc4x1::IfcMedicalDevice(data);
            case 601: return new ::Ifc4x1::IfcMedicalDeviceType(data);
            case 602: return new ::Ifc4x1::IfcMedicalDeviceTypeEnum(data);
            case 603: return new ::Ifc4x1::IfcMember(data);
            case 604: return new ::Ifc4x1::IfcMemberStandardCase(data);
            case 605: return new ::Ifc4x1::IfcMemberType(data);
            case 606: return new ::Ifc4x1::IfcMemberTypeEnum(data);
            case 607: return new ::Ifc4x1::IfcMetric(data);
            case 609: return new ::Ifc4x1::IfcMirroredProfileDef(data);
            case 610: return new ::Ifc4x1::IfcModulusOfElasticityMeasure(data);
            case 611: return new ::Ifc4x1::IfcModulusOfLinearSubgradeReactionMeasure(data);
            case 612: return new ::Ifc4x1::IfcModulusOfRotationalSubgradeReactionMeasure(data);
            case 614: return new ::Ifc4x1::IfcModulusOfSubgradeReactionMeasure(data);
            case 617: return new ::Ifc4x1::IfcMoistureDiffusivityMeasure(data);
            case 618: return new ::Ifc4x1::IfcMolecularWeightMeasure(data);
            case 619: return new ::Ifc4x1::IfcMomentOfInertiaMeasure(data);
            case 620: return new ::Ifc4x1::IfcMonetaryMeasure(data);
            case 621: return new ::Ifc4x1::IfcMonetaryUnit(data);
            case 622: return new ::Ifc4x1::IfcMonthInYearNumber(data);
            case 623: return new ::Ifc4x1::IfcMotorConnection(data);
            case 624: return new ::Ifc4x1::IfcMotorConnectionType(data);
            case 625: return new ::Ifc4x1::IfcMotorConnectionTypeEnum(data);
            case 626: return new ::Ifc4x1::IfcNamedUnit(data);
            case 627: return new ::Ifc4x1::IfcNonNegativeLengthMeasure(data);
            case 628: return new ::Ifc4x1::IfcNormalisedRatioMeasure(data);
            case 629: return new ::Ifc4x1::IfcNullStyle(data);
            case 630: return new ::Ifc4x1::IfcNumericMeasure(data);
            case 631: return new ::Ifc4x1::IfcObject(data);
            case 632: return new ::Ifc4x1::IfcObjectDefinition(data);
            case 633: return new ::Ifc4x1::IfcObjective(data);
            case 634: return new ::Ifc4x1::IfcObjectiveEnum(data);
            case 635: return new ::Ifc4x1::IfcObjectPlacement(data);
            case 637: return new ::Ifc4x1::IfcObjectTypeEnum(data);
            case 638: return new ::Ifc4x1::IfcOccupant(data);
            case 639: return new ::Ifc4x1::IfcOccupantTypeEnum(data);
            case 640: return new ::Ifc4x1::IfcOffsetCurve(data);
            case 641: return new ::Ifc4x1::IfcOffsetCurve2D(data);
            case 642: return new ::Ifc4x1::IfcOffsetCurve3D(data);
            case 643: return new ::Ifc4x1::IfcOffsetCurveByDistances(data);
            case 644: return new ::Ifc4x1::IfcOpeningElement(data);
            case 645: return new ::Ifc4x1::IfcOpeningElementTypeEnum(data);
            case 646: return new ::Ifc4x1::IfcOpeningStandardCase(data);
            case 647: return new ::Ifc4x1::IfcOpenShell(data);
            case 648: return new ::Ifc4x1::IfcOrganization(data);
            case 649: return new ::Ifc4x1::IfcOrganizationRelationship(data);
            case 650: return new ::Ifc4x1::IfcOrientationExpression(data);
            case 651: return new ::Ifc4x1::IfcOrientedEdge(data);
            case 652: return new ::Ifc4x1::IfcOuterBoundaryCurve(data);
            case 653: return new ::Ifc4x1::IfcOutlet(data);
            case 654: return new ::Ifc4x1::IfcOutletType(data);
            case 655: return new ::Ifc4x1::IfcOutletTypeEnum(data);
            case 656: return new ::Ifc4x1::IfcOwnerHistory(data);
            case 657: return new ::Ifc4x1::IfcParameterizedProfileDef(data);
            case 658: return new ::Ifc4x1::IfcParameterValue(data);
            case 659: return new ::Ifc4x1::IfcPath(data);
            case 660: return new ::Ifc4x1::IfcPcurve(data);
            case 661: return new ::Ifc4x1::IfcPerformanceHistory(data);
            case 662: return new ::Ifc4x1::IfcPerformanceHistoryTypeEnum(data);
            case 663: return new ::Ifc4x1::IfcPermeableCoveringOperationEnum(data);
            case 664: return new ::Ifc4x1::IfcPermeableCoveringProperties(data);
            case 665: return new ::Ifc4x1::IfcPermit(data);
            case 666: return new ::Ifc4x1::IfcPermitTypeEnum(data);
            case 667: return new ::Ifc4x1::IfcPerson(data);
            case 668: return new ::Ifc4x1::IfcPersonAndOrganization(data);
            case 669: return new ::Ifc4x1::IfcPHMeasure(data);
            case 670: return new ::Ifc4x1::IfcPhysicalComplexQuantity(data);
            case 671: return new ::Ifc4x1::IfcPhysicalOrVirtualEnum(data);
            case 672: return new ::Ifc4x1::IfcPhysicalQuantity(data);
            case 673: return new ::Ifc4x1::IfcPhysicalSimpleQuantity(data);
            case 674: return new ::Ifc4x1::IfcPile(data);
            case 675: return new ::Ifc4x1::IfcPileConstructionEnum(data);
            case 676: return new ::Ifc4x1::IfcPileType(data);
            case 677: return new ::Ifc4x1::IfcPileTypeEnum(data);
            case 678: return new ::Ifc4x1::IfcPipeFitting(data);
            case 679: return new ::Ifc4x1::IfcPipeFittingType(data);
            case 680: return new ::Ifc4x1::IfcPipeFittingTypeEnum(data);
            case 681: return new ::Ifc4x1::IfcPipeSegment(data);
            case 682: return new ::Ifc4x1::IfcPipeSegmentType(data);
            case 683: return new ::Ifc4x1::IfcPipeSegmentTypeEnum(data);
            case 684: return new ::Ifc4x1::IfcPixelTexture(data);
            case 685: return new ::Ifc4x1::IfcPlacement(data);
            case 686: return new ::Ifc4x1::IfcPlanarBox(data);
            case 687: return new ::Ifc4x1::IfcPlanarExtent(data);
            case 688: return new ::Ifc4x1::IfcPlanarForceMeasure(data);
            case 689: return new ::Ifc4x1::IfcPlane(data);
            case 690: return new ::Ifc4x1::IfcPlaneAngleMeasure(data);
            case 691: return new ::Ifc4x1::IfcPlate(data);
            case 692: return new ::Ifc4x1::IfcPlateStandardCase(data);
            case 693: return new ::Ifc4x1::IfcPlateType(data);
            case 694: return new ::Ifc4x1::IfcPlateTypeEnum(data);
            case 695: return new ::Ifc4x1::IfcPoint(data);
            case 696: return new ::Ifc4x1::IfcPointOnCurve(data);
            case 697: return new ::Ifc4x1::IfcPointOnSurface(data);
            case 699: return new ::Ifc4x1::IfcPolygonalBoundedHalfSpace(data);
            case 700: return new ::Ifc4x1::IfcPolygonalFaceSet(data);
            case 701: return new ::Ifc4x1::IfcPolyline(data);
            case 702: return new ::Ifc4x1::IfcPolyLoop(data);
            case 703: return new ::Ifc4x1::IfcPort(data);
            case 704: return new ::Ifc4x1::IfcPositioningElement(data);
            case 705: return new ::Ifc4x1::IfcPositiveInteger(data);
            case 706: return new ::Ifc4x1::IfcPositiveLengthMeasure(data);
            case 707: return new ::Ifc4x1::IfcPositivePlaneAngleMeasure(data);
            case 708: return new ::Ifc4x1::IfcPositiveRatioMeasure(data);
            case 709: return new ::Ifc4x1::IfcPostalAddress(data);
            case 710: return new ::Ifc4x1::IfcPowerMeasure(data);
            case 711: return new ::Ifc4x1::IfcPreDefinedColour(data);
            case 712: return new ::Ifc4x1::IfcPreDefinedCurveFont(data);
            case 713: return new ::Ifc4x1::IfcPreDefinedItem(data);
            case 714: return new ::Ifc4x1::IfcPreDefinedProperties(data);
            case 715: return new ::Ifc4x1::IfcPreDefinedPropertySet(data);
            case 716: return new ::Ifc4x1::IfcPreDefinedTextFont(data);
            case 717: return new ::Ifc4x1::IfcPreferredSurfaceCurveRepresentation(data);
            case 718: return new ::Ifc4x1::IfcPresentableText(data);
            case 719: return new ::Ifc4x1::IfcPresentationItem(data);
            case 720: return new ::Ifc4x1::IfcPresentationLayerAssignment(data);
            case 721: return new ::Ifc4x1::IfcPresentationLayerWithStyle(data);
            case 722: return new ::Ifc4x1::IfcPresentationStyle(data);
            case 723: return new ::Ifc4x1::IfcPresentationStyleAssignment(data);
            case 725: return new ::Ifc4x1::IfcPressureMeasure(data);
            case 726: return new ::Ifc4x1::IfcProcedure(data);
            case 727: return new ::Ifc4x1::IfcProcedureType(data);
            case 728: return new ::Ifc4x1::IfcProcedureTypeEnum(data);
            case 729: return new ::Ifc4x1::IfcProcess(data);
            case 731: return new ::Ifc4x1::IfcProduct(data);
            case 732: return new ::Ifc4x1::IfcProductDefinitionShape(data);
            case 733: return new ::Ifc4x1::IfcProductRepresentation(data);
            case 736: return new ::Ifc4x1::IfcProfileDef(data);
            case 737: return new ::Ifc4x1::IfcProfileProperties(data);
            case 738: return new ::Ifc4x1::IfcProfileTypeEnum(data);
            case 739: return new ::Ifc4x1::IfcProject(data);
            case 740: return new ::Ifc4x1::IfcProjectedCRS(data);
            case 741: return new ::Ifc4x1::IfcProjectedOrTrueLengthEnum(data);
            case 742: return new ::Ifc4x1::IfcProjectionElement(data);
            case 743: return new ::Ifc4x1::IfcProjectionElementTypeEnum(data);
            case 744: return new ::Ifc4x1::IfcProjectLibrary(data);
            case 745: return new ::Ifc4x1::IfcProjectOrder(data);
            case 746: return new ::Ifc4x1::IfcProjectOrderTypeEnum(data);
            case 747: return new ::Ifc4x1::IfcProperty(data);
            case 748: return new ::Ifc4x1::IfcPropertyAbstraction(data);
            case 749: return new ::Ifc4x1::IfcPropertyBoundedValue(data);
            case 750: return new ::Ifc4x1::IfcPropertyDefinition(data);
            case 751: return new ::Ifc4x1::IfcPropertyDependencyRelationship(data);
            case 752: return new ::Ifc4x1::IfcPropertyEnumeratedValue(data);
            case 753: return new ::Ifc4x1::IfcPropertyEnumeration(data);
            case 754: return new ::Ifc4x1::IfcPropertyListValue(data);
            case 755: return new ::Ifc4x1::IfcPropertyReferenceValue(data);
            case 756: return new ::Ifc4x1::IfcPropertySet(data);
            case 757: return new ::Ifc4x1::IfcPropertySetDefinition(data);
            case 759: return new ::Ifc4x1::IfcPropertySetDefinitionSet(data);
            case 760: return new ::Ifc4x1::IfcPropertySetTemplate(data);
            case 761: return new ::Ifc4x1::IfcPropertySetTemplateTypeEnum(data);
            case 762: return new ::Ifc4x1::IfcPropertySingleValue(data);
            case 763: return new ::Ifc4x1::IfcPropertyTableValue(data);
            case 764: return new ::Ifc4x1::IfcPropertyTemplate(data);
            case 765: return new ::Ifc4x1::IfcPropertyTemplateDefinition(data);
            case 766: return new ::Ifc4x1::IfcProtectiveDevice(data);
            case 767: return new ::Ifc4x1::IfcProtectiveDeviceTrippingUnit(data);
            case 768: return new ::Ifc4x1::IfcProtectiveDeviceTrippingUnitType(data);
            case 769: return new ::Ifc4x1::IfcProtectiveDeviceTrippingUnitTypeEnum(data);
            case 770: return new ::Ifc4x1::IfcProtectiveDeviceType(data);
            case 771: return new ::Ifc4x1::IfcProtectiveDeviceTypeEnum(data);
            case 772: return new ::Ifc4x1::IfcProxy(data);
            case 773: return new ::Ifc4x1::IfcPump(data);
            case 774: return new ::Ifc4x1::IfcPumpType(data);
            case 775: return new ::Ifc4x1::IfcPumpTypeEnum(data);
            case 776: return new ::Ifc4x1::IfcQuantityArea(data);
            case 777: return new ::Ifc4x1::IfcQuantityCount(data);
            case 778: return new ::Ifc4x1::IfcQuantityLength(data);
            case 779: return new ::Ifc4x1::IfcQuantitySet(data);
            case 780: return new ::Ifc4x1::IfcQuantityTime(data);
            case 781: return new ::Ifc4x1::IfcQuantityVolume(data);
            case 782: return new ::Ifc4x1::IfcQuantityWeight(data);
            case 783: return new ::Ifc4x1::IfcRadioActivityMeasure(data);
            case 784: return new ::Ifc4x1::IfcRailing(data);
            case 785: return new ::Ifc4x1::IfcRailingType(data);
            case 786: return new ::Ifc4x1::IfcRailingTypeEnum(data);
            case 787: return new ::Ifc4x1::IfcRamp(data);
            case 788: return new ::Ifc4x1::IfcRampFlight(data);
            case 789: return new ::Ifc4x1::IfcRampFlightType(data);
            case 790: return new ::Ifc4x1::IfcRampFlightTypeEnum(data);
            case 791: return new ::Ifc4x1::IfcRampType(data);
            case 792: return new ::Ifc4x1::IfcRampTypeEnum(data);
            case 793: return new ::Ifc4x1::IfcRatioMeasure(data);
            case 794: return new ::Ifc4x1::IfcRationalBSplineCurveWithKnots(data);
            case 795: return new ::Ifc4x1::IfcRationalBSplineSurfaceWithKnots(data);
            case 796: return new ::Ifc4x1::IfcReal(data);
            case 797: return new ::Ifc4x1::IfcRectangleHollowProfileDef(data);
            case 798: return new ::Ifc4x1::IfcRectangleProfileDef(data);
            case 799: return new ::Ifc4x1::IfcRectangularPyramid(data);
            case 800: return new ::Ifc4x1::IfcRectangularTrimmedSurface(data);
            case 801: return new ::Ifc4x1::IfcRecurrencePattern(data);
            case 802: return new ::Ifc4x1::IfcRecurrenceTypeEnum(data);
            case 803: return new ::Ifc4x1::IfcReference(data);
            case 804: return new ::Ifc4x1::IfcReferent(data);
            case 805: return new ::Ifc4x1::IfcReferentTypeEnum(data);
            case 806: return new ::Ifc4x1::IfcReflectanceMethodEnum(data);
            case 807: return new ::Ifc4x1::IfcRegularTimeSeries(data);
            case 808: return new ::Ifc4x1::IfcReinforcementBarProperties(data);
            case 809: return new ::Ifc4x1::IfcReinforcementDefinitionProperties(data);
            case 810: return new ::Ifc4x1::IfcReinforcingBar(data);
            case 811: return new ::Ifc4x1::IfcReinforcingBarRoleEnum(data);
            case 812: return new ::Ifc4x1::IfcReinforcingBarSurfaceEnum(data);
            case 813: return new ::Ifc4x1::IfcReinforcingBarType(data);
            case 814: return new ::Ifc4x1::IfcReinforcingBarTypeEnum(data);
            case 815: return new ::Ifc4x1::IfcReinforcingElement(data);
            case 816: return new ::Ifc4x1::IfcReinforcingElementType(data);
            case 817: return new ::Ifc4x1::IfcReinforcingMesh(data);
            case 818: return new ::Ifc4x1::IfcReinforcingMeshType(data);
            case 819: return new ::Ifc4x1::IfcReinforcingMeshTypeEnum(data);
            case 820: return new ::Ifc4x1::IfcRelAggregates(data);
            case 821: return new ::Ifc4x1::IfcRelAssigns(data);
            case 822: return new ::Ifc4x1::IfcRelAssignsToActor(data);
            case 823: return new ::Ifc4x1::IfcRelAssignsToControl(data);
            case 824: return new ::Ifc4x1::IfcRelAssignsToGroup(data);
            case 825: return new ::Ifc4x1::IfcRelAssignsToGroupByFactor(data);
            case 826: return new ::Ifc4x1::IfcRelAssignsToProcess(data);
            case 827: return new ::Ifc4x1::IfcRelAssignsToProduct(data);
            case 828: return new ::Ifc4x1::IfcRelAssignsToResource(data);
            case 829: return new ::Ifc4x1::IfcRelAssociates(data);
            case 830: return new ::Ifc4x1::IfcRelAssociatesApproval(data);
            case 831: return new ::Ifc4x1::IfcRelAssociatesClassification(data);
            case 832: return new ::Ifc4x1::IfcRelAssociatesConstraint(data);
            case 833: return new ::Ifc4x1::IfcRelAssociatesDocument(data);
            case 834: return new ::Ifc4x1::IfcRelAssociatesLibrary(data);
            case 835: return new ::Ifc4x1::IfcRelAssociatesMaterial(data);
            case 836: return new ::Ifc4x1::IfcRelationship(data);
            case 837: return new ::Ifc4x1::IfcRelConnects(data);
            case 838: return new ::Ifc4x1::IfcRelConnectsElements(data);
            case 839: return new ::Ifc4x1::IfcRelConnectsPathElements(data);
            case 840: return new ::Ifc4x1::IfcRelConnectsPorts(data);
            case 841: return new ::Ifc4x1::IfcRelConnectsPortToElement(data);
            case 842: return new ::Ifc4x1::IfcRelConnectsStructuralActivity(data);
            case 843: return new ::Ifc4x1::IfcRelConnectsStructuralMember(data);
            case 844: return new ::Ifc4x1::IfcRelConnectsWithEccentricity(data);
            case 845: return new ::Ifc4x1::IfcRelConnectsWithRealizingElements(data);
            case 846: return new ::Ifc4x1::IfcRelContainedInSpatialStructure(data);
            case 847: return new ::Ifc4x1::IfcRelCoversBldgElements(data);
            case 848: return new ::Ifc4x1::IfcRelCoversSpaces(data);
            case 849: return new ::Ifc4x1::IfcRelDeclares(data);
            case 850: return new ::Ifc4x1::IfcRelDecomposes(data);
            case 851: return new ::Ifc4x1::IfcRelDefines(data);
            case 852: return new ::Ifc4x1::IfcRelDefinesByObject(data);
            case 853: return new ::Ifc4x1::IfcRelDefinesByProperties(data);
            case 854: return new ::Ifc4x1::IfcRelDefinesByTemplate(data);
            case 855: return new ::Ifc4x1::IfcRelDefinesByType(data);
            case 856: return new ::Ifc4x1::IfcRelFillsElement(data);
            case 857: return new ::Ifc4x1::IfcRelFlowControlElements(data);
            case 858: return new ::Ifc4x1::IfcRelInterferesElements(data);
            case 859: return new ::Ifc4x1::IfcRelNests(data);
            case 860: return new ::Ifc4x1::IfcRelProjectsElement(data);
            case 861: return new ::Ifc4x1::IfcRelReferencedInSpatialStructure(data);
            case 862: return new ::Ifc4x1::IfcRelSequence(data);
            case 863: return new ::Ifc4x1::IfcRelServicesBuildings(data);
            case 864: return new ::Ifc4x1::IfcRelSpaceBoundary(data);
            case 865: return new ::Ifc4x1::IfcRelSpaceBoundary1stLevel(data);
            case 866: return new ::Ifc4x1::IfcRelSpaceBoundary2ndLevel(data);
            case 867: return new ::Ifc4x1::IfcRelVoidsElement(data);
            case 868: return new ::Ifc4x1::IfcReparametrisedCompositeCurveSegment(data);
            case 869: return new ::Ifc4x1::IfcRepresentation(data);
            case 870: return new ::Ifc4x1::IfcRepresentationContext(data);
            case 871: return new ::Ifc4x1::IfcRepresentationItem(data);
            case 872: return new ::Ifc4x1::IfcRepresentationMap(data);
            case 873: return new ::Ifc4x1::IfcResource(data);
            case 874: return new ::Ifc4x1::IfcResourceApprovalRelationship(data);
            case 875: return new ::Ifc4x1::IfcResourceConstraintRelationship(data);
            case 876: return new ::Ifc4x1::IfcResourceLevelRelationship(data);
            case 879: return new ::Ifc4x1::IfcResourceTime(data);
            case 880: return new ::Ifc4x1::IfcRevolvedAreaSolid(data);
            case 881: return new ::Ifc4x1::IfcRevolvedAreaSolidTapered(data);
            case 882: return new ::Ifc4x1::IfcRightCircularCone(data);
            case 883: return new ::Ifc4x1::IfcRightCircularCylinder(data);
            case 884: return new ::Ifc4x1::IfcRoleEnum(data);
            case 885: return new ::Ifc4x1::IfcRoof(data);
            case 886: return new ::Ifc4x1::IfcRoofType(data);
            case 887: return new ::Ifc4x1::IfcRoofTypeEnum(data);
            case 888: return new ::Ifc4x1::IfcRoot(data);
            case 889: return new ::Ifc4x1::IfcRotationalFrequencyMeasure(data);
            case 890: return new ::Ifc4x1::IfcRotationalMassMeasure(data);
            case 891: return new ::Ifc4x1::IfcRotationalStiffnessMeasure(data);
            case 893: return new ::Ifc4x1::IfcRoundedRectangleProfileDef(data);
            case 894: return new ::Ifc4x1::IfcSanitaryTerminal(data);
            case 895: return new ::Ifc4x1::IfcSanitaryTerminalType(data);
            case 896: return new ::Ifc4x1::IfcSanitaryTerminalTypeEnum(data);
            case 897: return new ::Ifc4x1::IfcSchedulingTime(data);
            case 898: return new ::Ifc4x1::IfcSeamCurve(data);
            case 899: return new ::Ifc4x1::IfcSectionalAreaIntegralMeasure(data);
            case 900: return new ::Ifc4x1::IfcSectionedSolid(data);
            case 901: return new ::Ifc4x1::IfcSectionedSolidHorizontal(data);
            case 902: return new ::Ifc4x1::IfcSectionedSpine(data);
            case 903: return new ::Ifc4x1::IfcSectionModulusMeasure(data);
            case 904: return new ::Ifc4x1::IfcSectionProperties(data);
            case 905: return new ::Ifc4x1::IfcSectionReinforcementProperties(data);
            case 906: return new ::Ifc4x1::IfcSectionTypeEnum(data);
            case 908: return new ::Ifc4x1::IfcSensor(data);
            case 909: return new ::Ifc4x1::IfcSensorType(data);
            case 910: return new ::Ifc4x1::IfcSensorTypeEnum(data);
            case 911: return new ::Ifc4x1::IfcSequenceEnum(data);
            case 912: return new ::Ifc4x1::IfcShadingDevice(data);
            case 913: return new ::Ifc4x1::IfcShadingDeviceType(data);
            case 914: return new ::Ifc4x1::IfcShadingDeviceTypeEnum(data);
            case 915: return new ::Ifc4x1::IfcShapeAspect(data);
            case 916: return new ::Ifc4x1::IfcShapeModel(data);
            case 917: return new ::Ifc4x1::IfcShapeRepresentation(data);
            case 918: return new ::Ifc4x1::IfcShearModulusMeasure(data);
            case 920: return new ::Ifc4x1::IfcShellBasedSurfaceModel(data);
            case 921: return new ::Ifc4x1::IfcSimpleProperty(data);
            case 922: return new ::Ifc4x1::IfcSimplePropertyTemplate(data);
            case 923: return new ::Ifc4x1::IfcSimplePropertyTemplateTypeEnum(data);
            case 925: return new ::Ifc4x1::IfcSIPrefix(data);
            case 926: return new ::Ifc4x1::IfcSite(data);
            case 927: return new ::Ifc4x1::IfcSIUnit(data);
            case 928: return new ::Ifc4x1::IfcSIUnitName(data);
            case 930: return new ::Ifc4x1::IfcSlab(data);
            case 931: return new ::Ifc4x1::IfcSlabElementedCase(data);
            case 932: return new ::Ifc4x1::IfcSlabStandardCase(data);
            case 933: return new ::Ifc4x1::IfcSlabType(data);
            case 934: return new ::Ifc4x1::IfcSlabTypeEnum(data);
            case 935: return new ::Ifc4x1::IfcSlippageConnectionCondition(data);
            case 936: return new ::Ifc4x1::IfcSolarDevice(data);
            case 937: return new ::Ifc4x1::IfcSolarDeviceType(data);
            case 938: return new ::Ifc4x1::IfcSolarDeviceTypeEnum(data);
            case 939: return new ::Ifc4x1::IfcSolidAngleMeasure(data);
            case 940: return new ::Ifc4x1::IfcSolidModel(data);
            case 942: return new ::Ifc4x1::IfcSoundPowerLevelMeasure(data);
            case 943: return new ::Ifc4x1::IfcSoundPowerMeasure(data);
            case 944: return new ::Ifc4x1::IfcSoundPressureLevelMeasure(data);
            case 945: return new ::Ifc4x1::IfcSoundPressureMeasure(data);
            case 946: return new ::Ifc4x1::IfcSpace(data);
            case 948: return new ::Ifc4x1::IfcSpaceHeater(data);
            case 949: return new ::Ifc4x1::IfcSpaceHeaterType(data);
            case 950: return new ::Ifc4x1::IfcSpaceHeaterTypeEnum(data);
            case 951: return new ::Ifc4x1::IfcSpaceType(data);
            case 952: return new ::Ifc4x1::IfcSpaceTypeEnum(data);
            case 953: return new ::Ifc4x1::IfcSpatialElement(data);
            case 954: return new ::Ifc4x1::IfcSpatialElementType(data);
            case 955: return new ::Ifc4x1::IfcSpatialStructureElement(data);
            case 956: return new ::Ifc4x1::IfcSpatialStructureElementType(data);
            case 957: return new ::Ifc4x1::IfcSpatialZone(data);
            case 958: return new ::Ifc4x1::IfcSpatialZoneType(data);
            case 959: return new ::Ifc4x1::IfcSpatialZoneTypeEnum(data);
            case 960: return new ::Ifc4x1::IfcSpecificHeatCapacityMeasure(data);
            case 961: return new ::Ifc4x1::IfcSpecularExponent(data);
            case 963: return new ::Ifc4x1::IfcSpecularRoughness(data);
            case 964: return new ::Ifc4x1::IfcSphere(data);
            case 965: return new ::Ifc4x1::IfcSphericalSurface(data);
            case 966: return new ::Ifc4x1::IfcStackTerminal(data);
            case 967: return new ::Ifc4x1::IfcStackTerminalType(data);
            case 968: return new ::Ifc4x1::IfcStackTerminalTypeEnum(data);
            case 969: return new ::Ifc4x1::IfcStair(data);
            case 970: return new ::Ifc4x1::IfcStairFlight(data);
            case 971: return new ::Ifc4x1::IfcStairFlightType(data);
            case 972: return new ::Ifc4x1::IfcStairFlightTypeEnum(data);
            case 973: return new ::Ifc4x1::IfcStairType(data);
            case 974: return new ::Ifc4x1::IfcStairTypeEnum(data);
            case 975: return new ::Ifc4x1::IfcStateEnum(data);
            case 976: return new ::Ifc4x1::IfcStructuralAction(data);
            case 977: return new ::Ifc4x1::IfcStructuralActivity(data);
            case 979: return new ::Ifc4x1::IfcStructuralAnalysisModel(data);
            case 980: return new ::Ifc4x1::IfcStructuralConnection(data);
            case 981: return new ::Ifc4x1::IfcStructuralConnectionCondition(data);
            case 982: return new ::Ifc4x1::IfcStructuralCurveAction(data);
            case 983: return new ::Ifc4x1::IfcStructuralCurveActivityTypeEnum(data);
            case 984: return new ::Ifc4x1::IfcStructuralCurveConnection(data);
            case 985: return new ::Ifc4x1::IfcStructuralCurveMember(data);
            case 986: return new ::Ifc4x1::IfcStructuralCurveMemberTypeEnum(data);
            case 987: return new ::Ifc4x1::IfcStructuralCurveMemberVarying(data);
            case 988: return new ::Ifc4x1::IfcStructuralCurveReaction(data);
            case 989: return new ::Ifc4x1::IfcStructuralItem(data);
            case 990: return new ::Ifc4x1::IfcStructuralLinearAction(data);
            case 991: return new ::Ifc4x1::IfcStructuralLoad(data);
            case 992: return new ::Ifc4x1::IfcStructuralLoadCase(data);
            case 993: return new ::Ifc4x1::IfcStructuralLoadConfiguration(data);
            case 994: return new ::Ifc4x1::IfcStructuralLoadGroup(data);
            case 995: return new ::Ifc4x1::IfcStructuralLoadLinearForce(data);
            case 996: return new ::Ifc4x1::IfcStructuralLoadOrResult(data);
            case 997: return new ::Ifc4x1::IfcStructuralLoadPlanarForce(data);
            case 998: return new ::Ifc4x1::IfcStructuralLoadSingleDisplacement(data);
            case 999: return new ::Ifc4x1::IfcStructuralLoadSingleDisplacementDistortion(data);
            case 1000: return new ::Ifc4x1::IfcStructuralLoadSingleForce(data);
            case 1001: return new ::Ifc4x1::IfcStructuralLoadSingleForceWarping(data);
            case 1002: return new ::Ifc4x1::IfcStructuralLoadStatic(data);
            case 1003: return new ::Ifc4x1::IfcStructuralLoadTemperature(data);
            case 1004: return new ::Ifc4x1::IfcStructuralMember(data);
            case 1005: return new ::Ifc4x1::IfcStructuralPlanarAction(data);
            case 1006: return new ::Ifc4x1::IfcStructuralPointAction(data);
            case 1007: return new ::Ifc4x1::IfcStructuralPointConnection(data);
            case 1008: return new ::Ifc4x1::IfcStructuralPointReaction(data);
            case 1009: return new ::Ifc4x1::IfcStructuralReaction(data);
            case 1010: return new ::Ifc4x1::IfcStructuralResultGroup(data);
            case 1011: return new ::Ifc4x1::IfcStructuralSurfaceAction(data);
            case 1012: return new ::Ifc4x1::IfcStructuralSurfaceActivityTypeEnum(data);
            case 1013: return new ::Ifc4x1::IfcStructuralSurfaceConnection(data);
            case 1014: return new ::Ifc4x1::IfcStructuralSurfaceMember(data);
            case 1015: return new ::Ifc4x1::IfcStructuralSurfaceMemberTypeEnum(data);
            case 1016: return new ::Ifc4x1::IfcStructuralSurfaceMemberVarying(data);
            case 1017: return new ::Ifc4x1::IfcStructuralSurfaceReaction(data);
            case 1019: return new ::Ifc4x1::IfcStyledItem(data);
            case 1020: return new ::Ifc4x1::IfcStyledRepresentation(data);
            case 1021: return new ::Ifc4x1::IfcStyleModel(data);
            case 1022: return new ::Ifc4x1::IfcSubContractResource(data);
            case 1023: return new ::Ifc4x1::IfcSubContractResourceType(data);
            case 1024: return new ::Ifc4x1::IfcSubContractResourceTypeEnum(data);
            case 1025: return new ::Ifc4x1::IfcSubedge(data);
            case 1026: return new ::Ifc4x1::IfcSurface(data);
            case 1027: return new ::Ifc4x1::IfcSurfaceCurve(data);
            case 1028: return new ::Ifc4x1::IfcSurfaceCurveSweptAreaSolid(data);
            case 1029: return new ::Ifc4x1::IfcSurfaceFeature(data);
            case 1030: return new ::Ifc4x1::IfcSurfaceFeatureTypeEnum(data);
            case 1031: return new ::Ifc4x1::IfcSurfaceOfLinearExtrusion(data);
            case 1032: return new ::Ifc4x1::IfcSurfaceOfRevolution(data);
            case 1034: return new ::Ifc4x1::IfcSurfaceReinforcementArea(data);
            case 1035: return new ::Ifc4x1::IfcSurfaceSide(data);
            case 1036: return new ::Ifc4x1::IfcSurfaceStyle(data);
            case 1038: return new ::Ifc4x1::IfcSurfaceStyleLighting(data);
            case 1039: return new ::Ifc4x1::IfcSurfaceStyleRefraction(data);
            case 1040: return new ::Ifc4x1::IfcSurfaceStyleRendering(data);
            case 1041: return new ::Ifc4x1::IfcSurfaceStyleShading(data);
            case 1042: return new ::Ifc4x1::IfcSurfaceStyleWithTextures(data);
            case 1043: return new ::Ifc4x1::IfcSurfaceTexture(data);
            case 1044: return new ::Ifc4x1::IfcSweptAreaSolid(data);
            case 1045: return new ::Ifc4x1::IfcSweptDiskSolid(data);
            case 1046: return new ::Ifc4x1::IfcSweptDiskSolidPolygonal(data);
            case 1047: return new ::Ifc4x1::IfcSweptSurface(data);
            case 1048: return new ::Ifc4x1::IfcSwitchingDevice(data);
            case 1049: return new ::Ifc4x1::IfcSwitchingDeviceType(data);
            case 1050: return new ::Ifc4x1::IfcSwitchingDeviceTypeEnum(data);
            case 1051: return new ::Ifc4x1::IfcSystem(data);
            case 1052: return new ::Ifc4x1::IfcSystemFurnitureElement(data);
            case 1053: return new ::Ifc4x1::IfcSystemFurnitureElementType(data);
            case 1054: return new ::Ifc4x1::IfcSystemFurnitureElementTypeEnum(data);
            case 1055: return new ::Ifc4x1::IfcTable(data);
            case 1056: return new ::Ifc4x1::IfcTableColumn(data);
            case 1057: return new ::Ifc4x1::IfcTableRow(data);
            case 1058: return new ::Ifc4x1::IfcTank(data);
            case 1059: return new ::Ifc4x1::IfcTankType(data);
            case 1060: return new ::Ifc4x1::IfcTankTypeEnum(data);
            case 1061: return new ::Ifc4x1::IfcTask(data);
            case 1062: return new ::Ifc4x1::IfcTaskDurationEnum(data);
            case 1063: return new ::Ifc4x1::IfcTaskTime(data);
            case 1064: return new ::Ifc4x1::IfcTaskTimeRecurring(data);
            case 1065: return new ::Ifc4x1::IfcTaskType(data);
            case 1066: return new ::Ifc4x1::IfcTaskTypeEnum(data);
            case 1067: return new ::Ifc4x1::IfcTelecomAddress(data);
            case 1068: return new ::Ifc4x1::IfcTemperatureGradientMeasure(data);
            case 1069: return new ::Ifc4x1::IfcTemperatureRateOfChangeMeasure(data);
            case 1070: return new ::Ifc4x1::IfcTendon(data);
            case 1071: return new ::Ifc4x1::IfcTendonAnchor(data);
            case 1072: return new ::Ifc4x1::IfcTendonAnchorType(data);
            case 1073: return new ::Ifc4x1::IfcTendonAnchorTypeEnum(data);
            case 1074: return new ::Ifc4x1::IfcTendonType(data);
            case 1075: return new ::Ifc4x1::IfcTendonTypeEnum(data);
            case 1076: return new ::Ifc4x1::IfcTessellatedFaceSet(data);
            case 1077: return new ::Ifc4x1::IfcTessellatedItem(data);
            case 1078: return new ::Ifc4x1::IfcText(data);
            case 1079: return new ::Ifc4x1::IfcTextAlignment(data);
            case 1080: return new ::Ifc4x1::IfcTextDecoration(data);
            case 1081: return new ::Ifc4x1::IfcTextFontName(data);
            case 1083: return new ::Ifc4x1::IfcTextLiteral(data);
            case 1084: return new ::Ifc4x1::IfcTextLiteralWithExtent(data);
            case 1085: return new ::Ifc4x1::IfcTextPath(data);
            case 1086: return new ::Ifc4x1::IfcTextStyle(data);
            case 1087: return new ::Ifc4x1::IfcTextStyleFontModel(data);
            case 1088: return new ::Ifc4x1::IfcTextStyleForDefinedFont(data);
            case 1089: return new ::Ifc4x1::IfcTextStyleTextModel(data);
            case 1090: return new ::Ifc4x1::IfcTextTransformation(data);
            case 1091: return new ::Ifc4x1::IfcTextureCoordinate(data);
            case 1092: return new ::Ifc4x1::IfcTextureCoordinateGenerator(data);
            case 1093: return new ::Ifc4x1::IfcTextureMap(data);
            case 1094: return new ::Ifc4x1::IfcTextureVertex(data);
            case 1095: return new ::Ifc4x1::IfcTextureVertexList(data);
            case 1096: return new ::Ifc4x1::IfcThermalAdmittanceMeasure(data);
            case 1097: return new ::Ifc4x1::IfcThermalConductivityMeasure(data);
            case 1098: return new ::Ifc4x1::IfcThermalExpansionCoefficientMeasure(data);
            case 1099: return new ::Ifc4x1::IfcThermalResistanceMeasure(data);
            case 1100: return new ::Ifc4x1::IfcThermalTransmittanceMeasure(data);
            case 1101: return new ::Ifc4x1::IfcThermodynamicTemperatureMeasure(data);
            case 1102: return new ::Ifc4x1::IfcTime(data);
            case 1103: return new ::Ifc4x1::IfcTimeMeasure(data);
            case 1105: return new ::Ifc4x1::IfcTimePeriod(data);
            case 1106: return new ::Ifc4x1::IfcTimeSeries(data);
            case 1107: return new ::Ifc4x1::IfcTimeSeriesDataTypeEnum(data);
            case 1108: return new ::Ifc4x1::IfcTimeSeriesValue(data);
            case 1109: return new ::Ifc4x1::IfcTimeStamp(data);
            case 1110: return new ::Ifc4x1::IfcTopologicalRepresentationItem(data);
            case 1111: return new ::Ifc4x1::IfcTopologyRepresentation(data);
            case 1112: return new ::Ifc4x1::IfcToroidalSurface(data);
            case 1113: return new ::Ifc4x1::IfcTorqueMeasure(data);
            case 1114: return new ::Ifc4x1::IfcTransformer(data);
            case 1115: return new ::Ifc4x1::IfcTransformerType(data);
            case 1116: return new ::Ifc4x1::IfcTransformerTypeEnum(data);
            case 1117: return new ::Ifc4x1::IfcTransitionCode(data);
            case 1118: return new ::Ifc4x1::IfcTransitionCurveSegment2D(data);
            case 1119: return new ::Ifc4x1::IfcTransitionCurveType(data);
            case 1121: return new ::Ifc4x1::IfcTransportElement(data);
            case 1122: return new ::Ifc4x1::IfcTransportElementType(data);
            case 1123: return new ::Ifc4x1::IfcTransportElementTypeEnum(data);
            case 1124: return new ::Ifc4x1::IfcTrapeziumProfileDef(data);
            case 1125: return new ::Ifc4x1::IfcTriangulatedFaceSet(data);
            case 1126: return new ::Ifc4x1::IfcTriangulatedIrregularNetwork(data);
            case 1127: return new ::Ifc4x1::IfcTrimmedCurve(data);
            case 1128: return new ::Ifc4x1::IfcTrimmingPreference(data);
            case 1130: return new ::Ifc4x1::IfcTShapeProfileDef(data);
            case 1131: return new ::Ifc4x1::IfcTubeBundle(data);
            case 1132: return new ::Ifc4x1::IfcTubeBundleType(data);
            case 1133: return new ::Ifc4x1::IfcTubeBundleTypeEnum(data);
            case 1134: return new ::Ifc4x1::IfcTypeObject(data);
            case 1135: return new ::Ifc4x1::IfcTypeProcess(data);
            case 1136: return new ::Ifc4x1::IfcTypeProduct(data);
            case 1137: return new ::Ifc4x1::IfcTypeResource(data);
            case 1139: return new ::Ifc4x1::IfcUnitaryControlElement(data);
            case 1140: return new ::Ifc4x1::IfcUnitaryControlElementType(data);
            case 1141: return new ::Ifc4x1::IfcUnitaryControlElementTypeEnum(data);
            case 1142: return new ::Ifc4x1::IfcUnitaryEquipment(data);
            case 1143: return new ::Ifc4x1::IfcUnitaryEquipmentType(data);
            case 1144: return new ::Ifc4x1::IfcUnitaryEquipmentTypeEnum(data);
            case 1145: return new ::Ifc4x1::IfcUnitAssignment(data);
            case 1146: return new ::Ifc4x1::IfcUnitEnum(data);
            case 1147: return new ::Ifc4x1::IfcURIReference(data);
            case 1148: return new ::Ifc4x1::IfcUShapeProfileDef(data);
            case 1150: return new ::Ifc4x1::IfcValve(data);
            case 1151: return new ::Ifc4x1::IfcValveType(data);
            case 1152: return new ::Ifc4x1::IfcValveTypeEnum(data);
            case 1153: return new ::Ifc4x1::IfcVaporPermeabilityMeasure(data);
            case 1154: return new ::Ifc4x1::IfcVector(data);
            case 1156: return new ::Ifc4x1::IfcVertex(data);
            case 1157: return new ::Ifc4x1::IfcVertexLoop(data);
            case 1158: return new ::Ifc4x1::IfcVertexPoint(data);
            case 1159: return new ::Ifc4x1::IfcVibrationIsolator(data);
            case 1160: return new ::Ifc4x1::IfcVibrationIsolatorType(data);
            case 1161: return new ::Ifc4x1::IfcVibrationIsolatorTypeEnum(data);
            case 1162: return new ::Ifc4x1::IfcVirtualElement(data);
            case 1163: return new ::Ifc4x1::IfcVirtualGridIntersection(data);
            case 1164: return new ::Ifc4x1::IfcVoidingFeature(data);
            case 1165: return new ::Ifc4x1::IfcVoidingFeatureTypeEnum(data);
            case 1166: return new ::Ifc4x1::IfcVolumeMeasure(data);
            case 1167: return new ::Ifc4x1::IfcVolumetricFlowRateMeasure(data);
            case 1168: return new ::Ifc4x1::IfcWall(data);
            case 1169: return new ::Ifc4x1::IfcWallElementedCase(data);
            case 1170: return new ::Ifc4x1::IfcWallStandardCase(data);
            case 1171: return new ::Ifc4x1::IfcWallType(data);
            case 1172: return new ::Ifc4x1::IfcWallTypeEnum(data);
            case 1173: return new ::Ifc4x1::IfcWarpingConstantMeasure(data);
            case 1174: return new ::Ifc4x1::IfcWarpingMomentMeasure(data);
            case 1176: return new ::Ifc4x1::IfcWasteTerminal(data);
            case 1177: return new ::Ifc4x1::IfcWasteTerminalType(data);
            case 1178: return new ::Ifc4x1::IfcWasteTerminalTypeEnum(data);
            case 1179: return new ::Ifc4x1::IfcWindow(data);
            case 1180: return new ::Ifc4x1::IfcWindowLiningProperties(data);
            case 1181: return new ::Ifc4x1::IfcWindowPanelOperationEnum(data);
            case 1182: return new ::Ifc4x1::IfcWindowPanelPositionEnum(data);
            case 1183: return new ::Ifc4x1::IfcWindowPanelProperties(data);
            case 1184: return new ::Ifc4x1::IfcWindowStandardCase(data);
            case 1185: return new ::Ifc4x1::IfcWindowStyle(data);
            case 1186: return new ::Ifc4x1::IfcWindowStyleConstructionEnum(data);
            case 1187: return new ::Ifc4x1::IfcWindowStyleOperationEnum(data);
            case 1188: return new ::Ifc4x1::IfcWindowType(data);
            case 1189: return new ::Ifc4x1::IfcWindowTypeEnum(data);
            case 1190: return new ::Ifc4x1::IfcWindowTypePartitioningEnum(data);
            case 1191: return new ::Ifc4x1::IfcWorkCalendar(data);
            case 1192: return new ::Ifc4x1::IfcWorkCalendarTypeEnum(data);
            case 1193: return new ::Ifc4x1::IfcWorkControl(data);
            case 1194: return new ::Ifc4x1::IfcWorkPlan(data);
            case 1195: return new ::Ifc4x1::IfcWorkPlanTypeEnum(data);
            case 1196: return new ::Ifc4x1::IfcWorkSchedule(data);
            case 1197: return new ::Ifc4x1::IfcWorkScheduleTypeEnum(data);
            case 1198: return new ::Ifc4x1::IfcWorkTime(data);
            case 1199: return new ::Ifc4x1::IfcZone(data);
            case 1200: return new ::Ifc4x1::IfcZShapeProfileDef(data);
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
"IfcAlignmentTypeEnum"s,
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
"IfcReferentTypeEnum"s,
"KILOPOINT"s,
"MILEPOINT"s,
"STATION"s,
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
"IfcTransitionCurveType"s,
"BIQUADRATICPARABOLA"s,
"BLOSSCURVE"s,
"CLOTHOIDCURVE"s,
"COSINECURVE"s,
"CUBICPARABOLA"s,
"SINECURVE"s,
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
"IfcLinearPlacement"s,
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
"IfcOrientationExpression"s,
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
"IfcAlignment2DHorizontal"s,
"IfcAlignment2DSegment"s,
"IfcAlignment2DVertical"s,
"IfcAlignment2DVerticalSegment"s,
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
"IfcDistanceExpression"s,
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
"IfcOffsetCurve"s,
"IfcOffsetCurve2D"s,
"IfcOffsetCurve3D"s,
"IfcOffsetCurveByDistances"s,
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
"IfcSectionedSolid"s,
"IfcSectionedSolidHorizontal"s,
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
"IfcTriangulatedIrregularNetwork"s,
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
"IfcAlignment2DHorizontalSegment"s,
"IfcAlignment2DVerSegCircularArc"s,
"IfcAlignment2DVerSegLine"s,
"IfcAlignment2DVerSegParabolicArc"s,
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
"IfcCurveSegment2D"s,
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
"IfcLineSegment2D"s,
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
"IfcPositioningElement"s,
"IfcProcedure"s,
"IfcProjectOrder"s,
"IfcProjectionElement"s,
"IfcProtectiveDeviceType"s,
"IfcPumpType"s,
"IfcRailingType"s,
"IfcRampFlightType"s,
"IfcRampType"s,
"IfcRationalBSplineSurfaceWithKnots"s,
"IfcReferent"s,
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
"IfcTransitionCurveSegment2D"s,
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
"IfcAlignmentCurve"s,
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
"IfcCircularArcSegment2D"s,
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
"IfcGrid"s,
"IfcHeatExchanger"s,
"IfcHumidifier"s,
"IfcInterceptor"s,
"IfcJunctionBox"s,
"IfcLamp"s,
"IfcLightFixture"s,
"IfcLinearPositioningElement"s,
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
"IfcAlignment"s,
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
"StartDistAlong"s,
"Segments"s,
"CurveGeometry"s,
"TangentialContinuity"s,
"StartTag"s,
"EndTag"s,
"Radius"s,
"IsConvex"s,
"ParabolaConstant"s,
"HorizontalLength"s,
"StartHeight"s,
"StartGradient"s,
"Horizontal"s,
"Vertical"s,
"Tag"s,
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
"TagList"s,
"Axis1"s,
"Axis2"s,
"LocalOrigin"s,
"Scale"s,
"Scale2"s,
"Axis3"s,
"Scale3"s,
"Thickness"s,
"IsCCW"s,
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
"StartPoint"s,
"StartDirection"s,
"SegmentLength"s,
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
"DistanceAlong"s,
"OffsetLateral"s,
"OffsetVertical"s,
"OffsetLongitudinal"s,
"AlongHorizontal"s,
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
"Distance"s,
"CartesianPosition"s,
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
"Roles"s,
"Addresses"s,
"RelatingOrganization"s,
"RelatedOrganizations"s,
"LateralAxisDirection"s,
"VerticalAxisDirection"s,
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
"RestartDistance"s,
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
"CrossSections"s,
"CrossSectionPositions"s,
"FixedAxisVertical"s,
"SpineCurve"s,
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
"StartRadius"s,
"EndRadius"s,
"IsStartRadiusCCW"s,
"IsEndRadiusCCW"s,
"TransitionCurveType"s,
"BottomXDim"s,
"TopXDim"s,
"TopXOffset"s,
"Normals"s,
"Flags"s,
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
"ToAlignmentCurve"s,
"ToHorizontal"s,
"ToVertical"s,
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
"IFC4X1"s};

#if defined(__clang__)
__attribute__((optnone))
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC4X1_populate_schema() {
    IFC4X1_IfcAbsorbedDoseMeasure_type = new type_declaration(strings[0], 0, new simple_type(simple_type::real_type));
    IFC4X1_IfcAccelerationMeasure_type = new type_declaration(strings[1], 1, new simple_type(simple_type::real_type));
    IFC4X1_IfcActionRequestTypeEnum_type = new enumeration_type(strings[2], 3, {
        strings[3],
        strings[4],
        strings[5],
        strings[6],
        strings[7],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcActionSourceTypeEnum_type = new enumeration_type(strings[10], 4, {
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
    IFC4X1_IfcActionTypeEnum_type = new enumeration_type(strings[36], 5, {
        strings[37],
        strings[38],
        strings[39],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcActuatorTypeEnum_type = new enumeration_type(strings[40], 11, {
        strings[41],
        strings[42],
        strings[43],
        strings[44],
        strings[45],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcAddressTypeEnum_type = new enumeration_type(strings[46], 13, {
        strings[47],
        strings[48],
        strings[49],
        strings[50],
        strings[8]
    });
    IFC4X1_IfcAirTerminalBoxTypeEnum_type = new enumeration_type(strings[51], 20, {
        strings[52],
        strings[53],
        strings[54],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcAirTerminalTypeEnum_type = new enumeration_type(strings[55], 22, {
        strings[56],
        strings[57],
        strings[58],
        strings[59],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type(strings[60], 25, {
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
    IFC4X1_IfcAlarmTypeEnum_type = new enumeration_type(strings[70], 28, {
        strings[71],
        strings[72],
        strings[73],
        strings[74],
        strings[75],
        strings[76],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcAlignmentTypeEnum_type = new enumeration_type(strings[77], 39, {
        strings[8],
        strings[9]
    });
    IFC4X1_IfcAmountOfSubstanceMeasure_type = new type_declaration(strings[78], 40, new simple_type(simple_type::real_type));
    IFC4X1_IfcAnalysisModelTypeEnum_type = new enumeration_type(strings[79], 41, {
        strings[80],
        strings[81],
        strings[82],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcAnalysisTheoryTypeEnum_type = new enumeration_type(strings[83], 42, {
        strings[84],
        strings[85],
        strings[86],
        strings[87],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcAngularVelocityMeasure_type = new type_declaration(strings[88], 43, new simple_type(simple_type::real_type));
    IFC4X1_IfcAreaDensityMeasure_type = new type_declaration(strings[89], 55, new simple_type(simple_type::real_type));
    IFC4X1_IfcAreaMeasure_type = new type_declaration(strings[90], 56, new simple_type(simple_type::real_type));
    IFC4X1_IfcArithmeticOperatorEnum_type = new enumeration_type(strings[91], 57, {
        strings[92],
        strings[93],
        strings[94],
        strings[95]
    });
    IFC4X1_IfcAssemblyPlaceEnum_type = new enumeration_type(strings[96], 58, {
        strings[48],
        strings[97],
        strings[9]
    });
    IFC4X1_IfcAudioVisualApplianceTypeEnum_type = new enumeration_type(strings[98], 63, {
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
        strings[109],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcBSplineCurveForm_type = new enumeration_type(strings[110], 97, {
        strings[111],
        strings[112],
        strings[113],
        strings[114],
        strings[115],
        strings[116]
    });
    IFC4X1_IfcBSplineSurfaceForm_type = new enumeration_type(strings[117], 100, {
        strings[118],
        strings[119],
        strings[120],
        strings[121],
        strings[122],
        strings[123],
        strings[124],
        strings[125],
        strings[126],
        strings[127],
        strings[116]
    });
    IFC4X1_IfcBeamTypeEnum_type = new enumeration_type(strings[128], 71, {
        strings[129],
        strings[130],
        strings[131],
        strings[132],
        strings[133],
        strings[134],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcBenchmarkEnum_type = new enumeration_type(strings[135], 72, {
        strings[136],
        strings[137],
        strings[138],
        strings[139],
        strings[140],
        strings[141],
        strings[142],
        strings[143],
        strings[144],
        strings[145]
    });
    IFC4X1_IfcBinary_type = new type_declaration(strings[146], 74, new simple_type(simple_type::binary_type));
    IFC4X1_IfcBoilerTypeEnum_type = new enumeration_type(strings[147], 79, {
        strings[148],
        strings[149],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcBoolean_type = new type_declaration(strings[150], 80, new simple_type(simple_type::boolean_type));
    IFC4X1_IfcBooleanOperator_type = new enumeration_type(strings[151], 83, {
        strings[152],
        strings[153],
        strings[154]
    });
    IFC4X1_IfcBuildingElementPartTypeEnum_type = new enumeration_type(strings[155], 106, {
        strings[156],
        strings[157],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcBuildingElementProxyTypeEnum_type = new enumeration_type(strings[158], 109, {
        strings[159],
        strings[160],
        strings[161],
        strings[162],
        strings[163],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcBuildingSystemTypeEnum_type = new enumeration_type(strings[164], 113, {
        strings[165],
        strings[166],
        strings[167],
        strings[168],
        strings[169],
        strings[23],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcBurnerTypeEnum_type = new enumeration_type(strings[170], 116, {
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCableCarrierFittingTypeEnum_type = new enumeration_type(strings[171], 119, {
        strings[172],
        strings[173],
        strings[174],
        strings[175],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCableCarrierSegmentTypeEnum_type = new enumeration_type(strings[176], 122, {
        strings[177],
        strings[178],
        strings[179],
        strings[180],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCableFittingTypeEnum_type = new enumeration_type(strings[181], 125, {
        strings[182],
        strings[183],
        strings[184],
        strings[185],
        strings[186],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCableSegmentTypeEnum_type = new enumeration_type(strings[187], 128, {
        strings[188],
        strings[189],
        strings[190],
        strings[191],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCardinalPointReference_type = new type_declaration(strings[192], 129, new simple_type(simple_type::integer_type));
    IFC4X1_IfcChangeActionEnum_type = new enumeration_type(strings[193], 140, {
        strings[194],
        strings[195],
        strings[196],
        strings[197],
        strings[9]
    });
    IFC4X1_IfcChillerTypeEnum_type = new enumeration_type(strings[198], 143, {
        strings[199],
        strings[200],
        strings[201],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcChimneyTypeEnum_type = new enumeration_type(strings[202], 146, {
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCoilTypeEnum_type = new enumeration_type(strings[203], 160, {
        strings[204],
        strings[205],
        strings[206],
        strings[207],
        strings[208],
        strings[209],
        strings[210],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcColumnTypeEnum_type = new enumeration_type(strings[211], 169, {
        strings[212],
        strings[213],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCommunicationsApplianceTypeEnum_type = new enumeration_type(strings[214], 172, {
        strings[215],
        strings[216],
        strings[4],
        strings[217],
        strings[218],
        strings[219],
        strings[220],
        strings[221],
        strings[222],
        strings[223],
        strings[224],
        strings[225],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcComplexNumber_type = new type_declaration(strings[226], 173, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IFC4X1_IfcComplexPropertyTemplateTypeEnum_type = new enumeration_type(strings[227], 176, {
        strings[228],
        strings[229]
    });
    IFC4X1_IfcCompoundPlaneAngleMeasure_type = new type_declaration(strings[230], 181, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
    IFC4X1_IfcCompressorTypeEnum_type = new enumeration_type(strings[231], 184, {
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
        strings[246],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCondenserTypeEnum_type = new enumeration_type(strings[247], 187, {
        strings[199],
        strings[248],
        strings[200],
        strings[249],
        strings[250],
        strings[251],
        strings[252],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcConnectionTypeEnum_type = new enumeration_type(strings[253], 195, {
        strings[254],
        strings[255],
        strings[256],
        strings[9]
    });
    IFC4X1_IfcConstraintEnum_type = new enumeration_type(strings[257], 198, {
        strings[258],
        strings[259],
        strings[260],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcConstructionEquipmentResourceTypeEnum_type = new enumeration_type(strings[261], 201, {
        strings[262],
        strings[263],
        strings[264],
        strings[265],
        strings[266],
        strings[267],
        strings[268],
        strings[269],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcConstructionMaterialResourceTypeEnum_type = new enumeration_type(strings[270], 204, {
        strings[271],
        strings[272],
        strings[273],
        strings[274],
        strings[275],
        strings[276],
        strings[277],
        strings[278],
        strings[279],
        strings[9],
        strings[8]
    });
    IFC4X1_IfcConstructionProductResourceTypeEnum_type = new enumeration_type(strings[280], 207, {
        strings[281],
        strings[282],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcContextDependentMeasure_type = new type_declaration(strings[283], 211, new simple_type(simple_type::real_type));
    IFC4X1_IfcControllerTypeEnum_type = new enumeration_type(strings[284], 216, {
        strings[285],
        strings[286],
        strings[287],
        strings[288],
        strings[289],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCooledBeamTypeEnum_type = new enumeration_type(strings[290], 221, {
        strings[291],
        strings[292],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCoolingTowerTypeEnum_type = new enumeration_type(strings[293], 224, {
        strings[294],
        strings[295],
        strings[296],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCostItemTypeEnum_type = new enumeration_type(strings[297], 229, {
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCostScheduleTypeEnum_type = new enumeration_type(strings[298], 231, {
        strings[299],
        strings[300],
        strings[301],
        strings[302],
        strings[303],
        strings[304],
        strings[305],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCountMeasure_type = new type_declaration(strings[306], 233, new simple_type(simple_type::number_type));
    IFC4X1_IfcCoveringTypeEnum_type = new enumeration_type(strings[307], 236, {
        strings[308],
        strings[309],
        strings[310],
        strings[311],
        strings[312],
        strings[313],
        strings[156],
        strings[314],
        strings[315],
        strings[316],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCrewResourceTypeEnum_type = new enumeration_type(strings[317], 239, {
        strings[47],
        strings[48],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCurtainWallTypeEnum_type = new enumeration_type(strings[318], 247, {
        strings[8],
        strings[9]
    });
    IFC4X1_IfcCurvatureMeasure_type = new type_declaration(strings[319], 248, new simple_type(simple_type::real_type));
    IFC4X1_IfcCurveInterpolationEnum_type = new enumeration_type(strings[320], 253, {
        strings[321],
        strings[322],
        strings[323],
        strings[9]
    });
    IFC4X1_IfcDamperTypeEnum_type = new enumeration_type(strings[324], 265, {
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
        strings[335],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDataOriginEnum_type = new enumeration_type(strings[336], 266, {
        strings[337],
        strings[338],
        strings[339],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDate_type = new type_declaration(strings[340], 267, new simple_type(simple_type::string_type));
    IFC4X1_IfcDateTime_type = new type_declaration(strings[341], 268, new simple_type(simple_type::string_type));
    IFC4X1_IfcDayInMonthNumber_type = new type_declaration(strings[342], 269, new simple_type(simple_type::integer_type));
    IFC4X1_IfcDayInWeekNumber_type = new type_declaration(strings[343], 270, new simple_type(simple_type::integer_type));
    IFC4X1_IfcDerivedUnitEnum_type = new enumeration_type(strings[344], 276, {
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
        strings[396],
        strings[8]
    });
    IFC4X1_IfcDescriptiveMeasure_type = new type_declaration(strings[397], 277, new simple_type(simple_type::string_type));
    IFC4X1_IfcDimensionCount_type = new type_declaration(strings[398], 279, new simple_type(simple_type::integer_type));
    IFC4X1_IfcDirectionSenseEnum_type = new enumeration_type(strings[399], 281, {
        strings[400],
        strings[401]
    });
    IFC4X1_IfcDiscreteAccessoryTypeEnum_type = new enumeration_type(strings[402], 284, {
        strings[403],
        strings[404],
        strings[405],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDistributionChamberElementTypeEnum_type = new enumeration_type(strings[406], 288, {
        strings[407],
        strings[408],
        strings[409],
        strings[410],
        strings[411],
        strings[412],
        strings[413],
        strings[414],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDistributionPortTypeEnum_type = new enumeration_type(strings[415], 297, {
        strings[416],
        strings[417],
        strings[418],
        strings[419],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDistributionSystemEnum_type = new enumeration_type(strings[420], 299, {
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
        strings[439],
        strings[274],
        strings[440],
        strings[441],
        strings[265],
        strings[266],
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
        strings[452],
        strings[108],
        strings[453],
        strings[454],
        strings[455],
        strings[456],
        strings[457],
        strings[458],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDocumentConfidentialityEnum_type = new enumeration_type(strings[459], 300, {
        strings[460],
        strings[461],
        strings[462],
        strings[463],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDocumentStatusEnum_type = new enumeration_type(strings[464], 305, {
        strings[465],
        strings[466],
        strings[467],
        strings[468],
        strings[9]
    });
    IFC4X1_IfcDoorPanelOperationEnum_type = new enumeration_type(strings[469], 308, {
        strings[470],
        strings[471],
        strings[472],
        strings[473],
        strings[474],
        strings[475],
        strings[476],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDoorPanelPositionEnum_type = new enumeration_type(strings[477], 309, {
        strings[478],
        strings[479],
        strings[480],
        strings[9]
    });
    IFC4X1_IfcDoorStyleConstructionEnum_type = new enumeration_type(strings[481], 313, {
        strings[482],
        strings[483],
        strings[484],
        strings[279],
        strings[485],
        strings[486],
        strings[278],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDoorStyleOperationEnum_type = new enumeration_type(strings[487], 314, {
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
        strings[501],
        strings[474],
        strings[475],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDoorTypeEnum_type = new enumeration_type(strings[502], 316, {
        strings[503],
        strings[504],
        strings[505],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDoorTypeOperationEnum_type = new enumeration_type(strings[506], 317, {
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
        strings[501],
        strings[474],
        strings[475],
        strings[507],
        strings[508],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDoseEquivalentMeasure_type = new type_declaration(strings[509], 318, new simple_type(simple_type::real_type));
    IFC4X1_IfcDuctFittingTypeEnum_type = new enumeration_type(strings[510], 323, {
        strings[172],
        strings[182],
        strings[183],
        strings[184],
        strings[185],
        strings[511],
        strings[186],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDuctSegmentTypeEnum_type = new enumeration_type(strings[512], 326, {
        strings[513],
        strings[514],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDuctSilencerTypeEnum_type = new enumeration_type(strings[515], 329, {
        strings[516],
        strings[517],
        strings[518],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcDuration_type = new type_declaration(strings[519], 330, new simple_type(simple_type::string_type));
    IFC4X1_IfcDynamicViscosityMeasure_type = new type_declaration(strings[520], 331, new simple_type(simple_type::real_type));
    IFC4X1_IfcElectricApplianceTypeEnum_type = new enumeration_type(strings[521], 337, {
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
        strings[537],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcElectricCapacitanceMeasure_type = new type_declaration(strings[538], 338, new simple_type(simple_type::real_type));
    IFC4X1_IfcElectricChargeMeasure_type = new type_declaration(strings[539], 339, new simple_type(simple_type::real_type));
    IFC4X1_IfcElectricConductanceMeasure_type = new type_declaration(strings[540], 340, new simple_type(simple_type::real_type));
    IFC4X1_IfcElectricCurrentMeasure_type = new type_declaration(strings[541], 341, new simple_type(simple_type::real_type));
    IFC4X1_IfcElectricDistributionBoardTypeEnum_type = new enumeration_type(strings[542], 344, {
        strings[543],
        strings[544],
        strings[545],
        strings[546],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type(strings[547], 347, {
        strings[548],
        strings[549],
        strings[550],
        strings[551],
        strings[552],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcElectricGeneratorTypeEnum_type = new enumeration_type(strings[553], 350, {
        strings[554],
        strings[555],
        strings[556],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcElectricMotorTypeEnum_type = new enumeration_type(strings[557], 353, {
        strings[558],
        strings[559],
        strings[560],
        strings[561],
        strings[562],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcElectricResistanceMeasure_type = new type_declaration(strings[563], 354, new simple_type(simple_type::real_type));
    IFC4X1_IfcElectricTimeControlTypeEnum_type = new enumeration_type(strings[564], 357, {
        strings[565],
        strings[566],
        strings[567],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcElectricVoltageMeasure_type = new type_declaration(strings[568], 358, new simple_type(simple_type::real_type));
    IFC4X1_IfcElementAssemblyTypeEnum_type = new enumeration_type(strings[569], 363, {
        strings[570],
        strings[571],
        strings[572],
        strings[573],
        strings[574],
        strings[575],
        strings[576],
        strings[577],
        strings[578],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcElementCompositionEnum_type = new enumeration_type(strings[579], 366, {
        strings[159],
        strings[160],
        strings[161]
    });
    IFC4X1_IfcEnergyMeasure_type = new type_declaration(strings[580], 373, new simple_type(simple_type::real_type));
    IFC4X1_IfcEngineTypeEnum_type = new enumeration_type(strings[581], 376, {
        strings[582],
        strings[583],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcEvaporativeCoolerTypeEnum_type = new enumeration_type(strings[584], 379, {
        strings[585],
        strings[586],
        strings[587],
        strings[588],
        strings[589],
        strings[590],
        strings[591],
        strings[592],
        strings[593],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcEvaporatorTypeEnum_type = new enumeration_type(strings[594], 382, {
        strings[595],
        strings[596],
        strings[597],
        strings[598],
        strings[599],
        strings[600],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcEventTriggerTypeEnum_type = new enumeration_type(strings[601], 385, {
        strings[602],
        strings[603],
        strings[604],
        strings[605],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcEventTypeEnum_type = new enumeration_type(strings[606], 387, {
        strings[607],
        strings[608],
        strings[609],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcExternalSpatialElementTypeEnum_type = new enumeration_type(strings[610], 396, {
        strings[611],
        strings[612],
        strings[613],
        strings[614],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcFanTypeEnum_type = new enumeration_type(strings[615], 410, {
        strings[616],
        strings[617],
        strings[618],
        strings[619],
        strings[620],
        strings[621],
        strings[622],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcFastenerTypeEnum_type = new enumeration_type(strings[623], 413, {
        strings[624],
        strings[625],
        strings[626],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcFilterTypeEnum_type = new enumeration_type(strings[627], 423, {
        strings[628],
        strings[629],
        strings[630],
        strings[631],
        strings[632],
        strings[633],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type(strings[634], 426, {
        strings[635],
        strings[636],
        strings[637],
        strings[638],
        strings[639],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcFlowDirectionEnum_type = new enumeration_type(strings[640], 430, {
        strings[641],
        strings[642],
        strings[643],
        strings[9]
    });
    IFC4X1_IfcFlowInstrumentTypeEnum_type = new enumeration_type(strings[644], 435, {
        strings[645],
        strings[646],
        strings[647],
        strings[648],
        strings[649],
        strings[650],
        strings[651],
        strings[652],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcFlowMeterTypeEnum_type = new enumeration_type(strings[653], 438, {
        strings[654],
        strings[655],
        strings[656],
        strings[657],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcFontStyle_type = new type_declaration(strings[658], 449, new simple_type(simple_type::string_type));
    IFC4X1_IfcFontVariant_type = new type_declaration(strings[659], 450, new simple_type(simple_type::string_type));
    IFC4X1_IfcFontWeight_type = new type_declaration(strings[660], 451, new simple_type(simple_type::string_type));
    IFC4X1_IfcFootingTypeEnum_type = new enumeration_type(strings[661], 454, {
        strings[662],
        strings[663],
        strings[664],
        strings[665],
        strings[666],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcForceMeasure_type = new type_declaration(strings[667], 455, new simple_type(simple_type::real_type));
    IFC4X1_IfcFrequencyMeasure_type = new type_declaration(strings[668], 456, new simple_type(simple_type::real_type));
    IFC4X1_IfcFurnitureTypeEnum_type = new enumeration_type(strings[669], 461, {
        strings[670],
        strings[671],
        strings[672],
        strings[673],
        strings[674],
        strings[675],
        strings[676],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcGeographicElementTypeEnum_type = new enumeration_type(strings[677], 464, {
        strings[678],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcGeometricProjectionEnum_type = new enumeration_type(strings[679], 466, {
        strings[680],
        strings[681],
        strings[682],
        strings[683],
        strings[684],
        strings[685],
        strings[686],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcGlobalOrLocalEnum_type = new enumeration_type(strings[687], 473, {
        strings[688],
        strings[689]
    });
    IFC4X1_IfcGloballyUniqueId_type = new type_declaration(strings[690], 472, new simple_type(simple_type::string_type));
    IFC4X1_IfcGridTypeEnum_type = new enumeration_type(strings[691], 478, {
        strings[517],
        strings[692],
        strings[693],
        strings[694],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcHeatExchangerTypeEnum_type = new enumeration_type(strings[695], 484, {
        strings[696],
        strings[697],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcHeatFluxDensityMeasure_type = new type_declaration(strings[698], 485, new simple_type(simple_type::real_type));
    IFC4X1_IfcHeatingValueMeasure_type = new type_declaration(strings[699], 486, new simple_type(simple_type::real_type));
    IFC4X1_IfcHumidifierTypeEnum_type = new enumeration_type(strings[700], 489, {
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
        strings[713],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcIdentifier_type = new type_declaration(strings[714], 490, new simple_type(simple_type::string_type));
    IFC4X1_IfcIlluminanceMeasure_type = new type_declaration(strings[715], 491, new simple_type(simple_type::real_type));
    IFC4X1_IfcInductanceMeasure_type = new type_declaration(strings[716], 499, new simple_type(simple_type::real_type));
    IFC4X1_IfcInteger_type = new type_declaration(strings[717], 500, new simple_type(simple_type::integer_type));
    IFC4X1_IfcIntegerCountRateMeasure_type = new type_declaration(strings[718], 501, new simple_type(simple_type::integer_type));
    IFC4X1_IfcInterceptorTypeEnum_type = new enumeration_type(strings[719], 504, {
        strings[720],
        strings[721],
        strings[444],
        strings[722],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcInternalOrExternalEnum_type = new enumeration_type(strings[723], 505, {
        strings[724],
        strings[611],
        strings[612],
        strings[613],
        strings[614],
        strings[9]
    });
    IFC4X1_IfcInventoryTypeEnum_type = new enumeration_type(strings[725], 508, {
        strings[726],
        strings[727],
        strings[728],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcIonConcentrationMeasure_type = new type_declaration(strings[729], 509, new simple_type(simple_type::real_type));
    IFC4X1_IfcIsothermalMoistureCapacityMeasure_type = new type_declaration(strings[730], 513, new simple_type(simple_type::real_type));
    IFC4X1_IfcJunctionBoxTypeEnum_type = new enumeration_type(strings[731], 516, {
        strings[430],
        strings[732],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcKinematicViscosityMeasure_type = new type_declaration(strings[733], 517, new simple_type(simple_type::real_type));
    IFC4X1_IfcKnotType_type = new enumeration_type(strings[734], 518, {
        strings[735],
        strings[736],
        strings[737],
        strings[116]
    });
    IFC4X1_IfcLabel_type = new type_declaration(strings[738], 519, new simple_type(simple_type::string_type));
    IFC4X1_IfcLaborResourceTypeEnum_type = new enumeration_type(strings[739], 522, {
        strings[740],
        strings[741],
        strings[742],
        strings[272],
        strings[273],
        strings[743],
        strings[744],
        strings[309],
        strings[745],
        strings[746],
        strings[747],
        strings[276],
        strings[748],
        strings[267],
        strings[749],
        strings[311],
        strings[750],
        strings[751],
        strings[752],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcLampTypeEnum_type = new enumeration_type(strings[753], 526, {
        strings[754],
        strings[755],
        strings[756],
        strings[757],
        strings[758],
        strings[759],
        strings[760],
        strings[761],
        strings[762],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcLanguageId_type = new type_declaration(strings[763], 527, new named_type(IFC4X1_IfcIdentifier_type));
    IFC4X1_IfcLayerSetDirectionEnum_type = new enumeration_type(strings[764], 529, {
        strings[765],
        strings[766],
        strings[767]
    });
    IFC4X1_IfcLengthMeasure_type = new type_declaration(strings[768], 530, new simple_type(simple_type::real_type));
    IFC4X1_IfcLightDistributionCurveEnum_type = new enumeration_type(strings[769], 534, {
        strings[770],
        strings[771],
        strings[772],
        strings[9]
    });
    IFC4X1_IfcLightEmissionSourceEnum_type = new enumeration_type(strings[773], 537, {
        strings[754],
        strings[755],
        strings[757],
        strings[758],
        strings[774],
        strings[775],
        strings[776],
        strings[777],
        strings[760],
        strings[762],
        strings[9]
    });
    IFC4X1_IfcLightFixtureTypeEnum_type = new enumeration_type(strings[778], 540, {
        strings[779],
        strings[780],
        strings[781],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcLinearForceMeasure_type = new type_declaration(strings[782], 549, new simple_type(simple_type::real_type));
    IFC4X1_IfcLinearMomentMeasure_type = new type_declaration(strings[783], 550, new simple_type(simple_type::real_type));
    IFC4X1_IfcLinearStiffnessMeasure_type = new type_declaration(strings[784], 553, new simple_type(simple_type::real_type));
    IFC4X1_IfcLinearVelocityMeasure_type = new type_declaration(strings[785], 554, new simple_type(simple_type::real_type));
    IFC4X1_IfcLoadGroupTypeEnum_type = new enumeration_type(strings[786], 557, {
        strings[787],
        strings[788],
        strings[789],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcLogical_type = new type_declaration(strings[790], 559, new simple_type(simple_type::logical_type));
    IFC4X1_IfcLogicalOperatorEnum_type = new enumeration_type(strings[791], 560, {
        strings[792],
        strings[793],
        strings[794],
        strings[795],
        strings[796]
    });
    IFC4X1_IfcLuminousFluxMeasure_type = new type_declaration(strings[797], 563, new simple_type(simple_type::real_type));
    IFC4X1_IfcLuminousIntensityDistributionMeasure_type = new type_declaration(strings[798], 564, new simple_type(simple_type::real_type));
    IFC4X1_IfcLuminousIntensityMeasure_type = new type_declaration(strings[799], 565, new simple_type(simple_type::real_type));
    IFC4X1_IfcMagneticFluxDensityMeasure_type = new type_declaration(strings[800], 566, new simple_type(simple_type::real_type));
    IFC4X1_IfcMagneticFluxMeasure_type = new type_declaration(strings[801], 567, new simple_type(simple_type::real_type));
    IFC4X1_IfcMassDensityMeasure_type = new type_declaration(strings[802], 571, new simple_type(simple_type::real_type));
    IFC4X1_IfcMassFlowRateMeasure_type = new type_declaration(strings[803], 572, new simple_type(simple_type::real_type));
    IFC4X1_IfcMassMeasure_type = new type_declaration(strings[804], 573, new simple_type(simple_type::real_type));
    IFC4X1_IfcMassPerLengthMeasure_type = new type_declaration(strings[805], 574, new simple_type(simple_type::real_type));
    IFC4X1_IfcMechanicalFastenerTypeEnum_type = new enumeration_type(strings[806], 599, {
        strings[807],
        strings[808],
        strings[809],
        strings[810],
        strings[811],
        strings[812],
        strings[813],
        strings[814],
        strings[815],
        strings[816],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcMedicalDeviceTypeEnum_type = new enumeration_type(strings[817], 602, {
        strings[818],
        strings[819],
        strings[820],
        strings[821],
        strings[822],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcMemberTypeEnum_type = new enumeration_type(strings[823], 606, {
        strings[824],
        strings[825],
        strings[826],
        strings[827],
        strings[828],
        strings[696],
        strings[6],
        strings[829],
        strings[830],
        strings[831],
        strings[832],
        strings[833],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcModulusOfElasticityMeasure_type = new type_declaration(strings[834], 610, new simple_type(simple_type::real_type));
    IFC4X1_IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration(strings[835], 611, new simple_type(simple_type::real_type));
    IFC4X1_IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration(strings[836], 612, new simple_type(simple_type::real_type));
    IFC4X1_IfcModulusOfRotationalSubgradeReactionSelect_type = new select_type(strings[837], 613, {
        IFC4X1_IfcBoolean_type,
        IFC4X1_IfcModulusOfRotationalSubgradeReactionMeasure_type
    });
    IFC4X1_IfcModulusOfSubgradeReactionMeasure_type = new type_declaration(strings[838], 614, new simple_type(simple_type::real_type));
    IFC4X1_IfcModulusOfSubgradeReactionSelect_type = new select_type(strings[839], 615, {
        IFC4X1_IfcBoolean_type,
        IFC4X1_IfcModulusOfSubgradeReactionMeasure_type
    });
    IFC4X1_IfcModulusOfTranslationalSubgradeReactionSelect_type = new select_type(strings[840], 616, {
        IFC4X1_IfcBoolean_type,
        IFC4X1_IfcModulusOfLinearSubgradeReactionMeasure_type
    });
    IFC4X1_IfcMoistureDiffusivityMeasure_type = new type_declaration(strings[841], 617, new simple_type(simple_type::real_type));
    IFC4X1_IfcMolecularWeightMeasure_type = new type_declaration(strings[842], 618, new simple_type(simple_type::real_type));
    IFC4X1_IfcMomentOfInertiaMeasure_type = new type_declaration(strings[843], 619, new simple_type(simple_type::real_type));
    IFC4X1_IfcMonetaryMeasure_type = new type_declaration(strings[844], 620, new simple_type(simple_type::real_type));
    IFC4X1_IfcMonthInYearNumber_type = new type_declaration(strings[845], 622, new simple_type(simple_type::integer_type));
    IFC4X1_IfcMotorConnectionTypeEnum_type = new enumeration_type(strings[846], 625, {
        strings[847],
        strings[848],
        strings[849],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcNonNegativeLengthMeasure_type = new type_declaration(strings[850], 627, new named_type(IFC4X1_IfcLengthMeasure_type));
    IFC4X1_IfcNullStyle_type = new enumeration_type(strings[851], 629, {
        strings[852]
    });
    IFC4X1_IfcNumericMeasure_type = new type_declaration(strings[853], 630, new simple_type(simple_type::number_type));
    IFC4X1_IfcObjectTypeEnum_type = new enumeration_type(strings[854], 637, {
        strings[855],
        strings[856],
        strings[428],
        strings[857],
        strings[858],
        strings[859],
        strings[860],
        strings[9]
    });
    IFC4X1_IfcObjectiveEnum_type = new enumeration_type(strings[861], 634, {
        strings[862],
        strings[863],
        strings[864],
        strings[611],
        strings[865],
        strings[866],
        strings[867],
        strings[868],
        strings[869],
        strings[870],
        strings[871],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcOccupantTypeEnum_type = new enumeration_type(strings[872], 639, {
        strings[873],
        strings[874],
        strings[875],
        strings[876],
        strings[877],
        strings[878],
        strings[879],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcOpeningElementTypeEnum_type = new enumeration_type(strings[880], 645, {
        strings[881],
        strings[882],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcOutletTypeEnum_type = new enumeration_type(strings[883], 655, {
        strings[884],
        strings[885],
        strings[886],
        strings[887],
        strings[888],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPHMeasure_type = new type_declaration(strings[889], 669, new simple_type(simple_type::real_type));
    IFC4X1_IfcParameterValue_type = new type_declaration(strings[890], 658, new simple_type(simple_type::real_type));
    IFC4X1_IfcPerformanceHistoryTypeEnum_type = new enumeration_type(strings[891], 662, {
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPermeableCoveringOperationEnum_type = new enumeration_type(strings[892], 663, {
        strings[893],
        strings[894],
        strings[895],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPermitTypeEnum_type = new enumeration_type(strings[896], 666, {
        strings[897],
        strings[898],
        strings[899],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPhysicalOrVirtualEnum_type = new enumeration_type(strings[900], 671, {
        strings[901],
        strings[902],
        strings[9]
    });
    IFC4X1_IfcPileConstructionEnum_type = new enumeration_type(strings[903], 675, {
        strings[904],
        strings[905],
        strings[906],
        strings[907],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPileTypeEnum_type = new enumeration_type(strings[908], 677, {
        strings[909],
        strings[910],
        strings[911],
        strings[912],
        strings[913],
        strings[914],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPipeFittingTypeEnum_type = new enumeration_type(strings[915], 680, {
        strings[172],
        strings[182],
        strings[183],
        strings[184],
        strings[185],
        strings[511],
        strings[186],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPipeSegmentTypeEnum_type = new enumeration_type(strings[916], 683, {
        strings[917],
        strings[514],
        strings[513],
        strings[918],
        strings[919],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPlanarForceMeasure_type = new type_declaration(strings[920], 688, new simple_type(simple_type::real_type));
    IFC4X1_IfcPlaneAngleMeasure_type = new type_declaration(strings[921], 690, new simple_type(simple_type::real_type));
    IFC4X1_IfcPlateTypeEnum_type = new enumeration_type(strings[922], 694, {
        strings[923],
        strings[924],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPositiveInteger_type = new type_declaration(strings[925], 705, new named_type(IFC4X1_IfcInteger_type));
    IFC4X1_IfcPositiveLengthMeasure_type = new type_declaration(strings[926], 706, new named_type(IFC4X1_IfcLengthMeasure_type));
    IFC4X1_IfcPositivePlaneAngleMeasure_type = new type_declaration(strings[927], 707, new named_type(IFC4X1_IfcPlaneAngleMeasure_type));
    IFC4X1_IfcPowerMeasure_type = new type_declaration(strings[928], 710, new simple_type(simple_type::real_type));
    IFC4X1_IfcPreferredSurfaceCurveRepresentation_type = new enumeration_type(strings[929], 717, {
        strings[930],
        strings[931],
        strings[932]
    });
    IFC4X1_IfcPresentableText_type = new type_declaration(strings[933], 718, new simple_type(simple_type::string_type));
    IFC4X1_IfcPressureMeasure_type = new type_declaration(strings[934], 725, new simple_type(simple_type::real_type));
    IFC4X1_IfcProcedureTypeEnum_type = new enumeration_type(strings[935], 728, {
        strings[936],
        strings[937],
        strings[938],
        strings[939],
        strings[940],
        strings[941],
        strings[942],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcProfileTypeEnum_type = new enumeration_type(strings[943], 738, {
        strings[944],
        strings[945]
    });
    IFC4X1_IfcProjectOrderTypeEnum_type = new enumeration_type(strings[946], 746, {
        strings[947],
        strings[948],
        strings[949],
        strings[950],
        strings[951],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcProjectedOrTrueLengthEnum_type = new enumeration_type(strings[952], 741, {
        strings[953],
        strings[954]
    });
    IFC4X1_IfcProjectionElementTypeEnum_type = new enumeration_type(strings[955], 743, {
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPropertySetTemplateTypeEnum_type = new enumeration_type(strings[956], 761, {
        strings[957],
        strings[958],
        strings[959],
        strings[960],
        strings[961],
        strings[962],
        strings[963],
        strings[9]
    });
    IFC4X1_IfcProtectiveDeviceTrippingUnitTypeEnum_type = new enumeration_type(strings[964], 769, {
        strings[965],
        strings[966],
        strings[967],
        strings[968],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcProtectiveDeviceTypeEnum_type = new enumeration_type(strings[969], 771, {
        strings[970],
        strings[971],
        strings[972],
        strings[973],
        strings[974],
        strings[975],
        strings[976],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcPumpTypeEnum_type = new enumeration_type(strings[977], 775, {
        strings[978],
        strings[979],
        strings[980],
        strings[981],
        strings[982],
        strings[983],
        strings[984],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcRadioActivityMeasure_type = new type_declaration(strings[985], 783, new simple_type(simple_type::real_type));
    IFC4X1_IfcRailingTypeEnum_type = new enumeration_type(strings[986], 786, {
        strings[987],
        strings[988],
        strings[989],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcRampFlightTypeEnum_type = new enumeration_type(strings[990], 790, {
        strings[991],
        strings[992],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcRampTypeEnum_type = new enumeration_type(strings[993], 792, {
        strings[994],
        strings[995],
        strings[996],
        strings[997],
        strings[998],
        strings[999],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcRatioMeasure_type = new type_declaration(strings[1000], 793, new simple_type(simple_type::real_type));
    IFC4X1_IfcReal_type = new type_declaration(strings[1001], 796, new simple_type(simple_type::real_type));
    IFC4X1_IfcRecurrenceTypeEnum_type = new enumeration_type(strings[1002], 802, {
        strings[1003],
        strings[1004],
        strings[1005],
        strings[1006],
        strings[1007],
        strings[1008],
        strings[1009],
        strings[1010]
    });
    IFC4X1_IfcReferentTypeEnum_type = new enumeration_type(strings[1011], 805, {
        strings[1012],
        strings[1013],
        strings[1014],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcReflectanceMethodEnum_type = new enumeration_type(strings[1015], 806, {
        strings[1016],
        strings[1017],
        strings[1018],
        strings[1019],
        strings[277],
        strings[1020],
        strings[1021],
        strings[278],
        strings[1022],
        strings[9]
    });
    IFC4X1_IfcReinforcingBarRoleEnum_type = new enumeration_type(strings[1023], 811, {
        strings[1024],
        strings[1025],
        strings[1026],
        strings[833],
        strings[1027],
        strings[1028],
        strings[1029],
        strings[1030],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcReinforcingBarSurfaceEnum_type = new enumeration_type(strings[1031], 812, {
        strings[1032],
        strings[1033]
    });
    IFC4X1_IfcReinforcingBarTypeEnum_type = new enumeration_type(strings[1034], 814, {
        strings[1030],
        strings[1028],
        strings[1026],
        strings[1024],
        strings[1027],
        strings[1029],
        strings[1025],
        strings[833],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcReinforcingMeshTypeEnum_type = new enumeration_type(strings[1035], 819, {
        strings[8],
        strings[9]
    });
    IFC4X1_IfcRoleEnum_type = new enumeration_type(strings[1036], 884, {
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
        strings[1049],
        strings[1050],
        strings[1051],
        strings[1052],
        strings[1053],
        strings[878],
        strings[1054],
        strings[1055],
        strings[1056],
        strings[1057],
        strings[8]
    });
    IFC4X1_IfcRoofTypeEnum_type = new enumeration_type(strings[1058], 887, {
        strings[1059],
        strings[1060],
        strings[1061],
        strings[1062],
        strings[1063],
        strings[1064],
        strings[1065],
        strings[1066],
        strings[1067],
        strings[1068],
        strings[1069],
        strings[1070],
        strings[1071],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcRotationalFrequencyMeasure_type = new type_declaration(strings[1072], 889, new simple_type(simple_type::real_type));
    IFC4X1_IfcRotationalMassMeasure_type = new type_declaration(strings[1073], 890, new simple_type(simple_type::real_type));
    IFC4X1_IfcRotationalStiffnessMeasure_type = new type_declaration(strings[1074], 891, new simple_type(simple_type::real_type));
    IFC4X1_IfcRotationalStiffnessSelect_type = new select_type(strings[1075], 892, {
        IFC4X1_IfcBoolean_type,
        IFC4X1_IfcRotationalStiffnessMeasure_type
    });
    IFC4X1_IfcSIPrefix_type = new enumeration_type(strings[1076], 925, {
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
        strings[1087],
        strings[1088],
        strings[1089],
        strings[1090],
        strings[1091],
        strings[1092]
    });
    IFC4X1_IfcSIUnitName_type = new enumeration_type(strings[1093], 928, {
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
        strings[1118],
        strings[1119],
        strings[1120],
        strings[1121],
        strings[1122],
        strings[1123]
    });
    IFC4X1_IfcSanitaryTerminalTypeEnum_type = new enumeration_type(strings[1124], 896, {
        strings[1125],
        strings[1126],
        strings[1127],
        strings[1128],
        strings[642],
        strings[1129],
        strings[1130],
        strings[1131],
        strings[1132],
        strings[1133],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSectionModulusMeasure_type = new type_declaration(strings[1134], 903, new simple_type(simple_type::real_type));
    IFC4X1_IfcSectionTypeEnum_type = new enumeration_type(strings[1135], 906, {
        strings[1136],
        strings[1137]
    });
    IFC4X1_IfcSectionalAreaIntegralMeasure_type = new type_declaration(strings[1138], 899, new simple_type(simple_type::real_type));
    IFC4X1_IfcSensorTypeEnum_type = new enumeration_type(strings[1139], 910, {
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
        strings[1159],
        strings[1160],
        strings[1161],
        strings[1162],
        strings[1163],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSequenceEnum_type = new enumeration_type(strings[1164], 911, {
        strings[1165],
        strings[1166],
        strings[1167],
        strings[1168],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcShadingDeviceTypeEnum_type = new enumeration_type(strings[1169], 914, {
        strings[1170],
        strings[1171],
        strings[1172],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcShearModulusMeasure_type = new type_declaration(strings[1173], 918, new simple_type(simple_type::real_type));
    IFC4X1_IfcSimplePropertyTemplateTypeEnum_type = new enumeration_type(strings[1174], 923, {
        strings[1175],
        strings[1176],
        strings[1177],
        strings[1178],
        strings[1179],
        strings[1180],
        strings[1181],
        strings[1182],
        strings[1183],
        strings[1184],
        strings[1185],
        strings[1186]
    });
    IFC4X1_IfcSlabTypeEnum_type = new enumeration_type(strings[1187], 934, {
        strings[1188],
        strings[1189],
        strings[1190],
        strings[1191],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSolarDeviceTypeEnum_type = new enumeration_type(strings[1192], 938, {
        strings[1193],
        strings[1194],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSolidAngleMeasure_type = new type_declaration(strings[1195], 939, new simple_type(simple_type::real_type));
    IFC4X1_IfcSoundPowerLevelMeasure_type = new type_declaration(strings[1196], 942, new simple_type(simple_type::real_type));
    IFC4X1_IfcSoundPowerMeasure_type = new type_declaration(strings[1197], 943, new simple_type(simple_type::real_type));
    IFC4X1_IfcSoundPressureLevelMeasure_type = new type_declaration(strings[1198], 944, new simple_type(simple_type::real_type));
    IFC4X1_IfcSoundPressureMeasure_type = new type_declaration(strings[1199], 945, new simple_type(simple_type::real_type));
    IFC4X1_IfcSpaceHeaterTypeEnum_type = new enumeration_type(strings[1200], 950, {
        strings[1201],
        strings[1202],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSpaceTypeEnum_type = new enumeration_type(strings[1203], 952, {
        strings[1204],
        strings[1205],
        strings[1206],
        strings[724],
        strings[611],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSpatialZoneTypeEnum_type = new enumeration_type(strings[1207], 959, {
        strings[1208],
        strings[1209],
        strings[266],
        strings[1210],
        strings[449],
        strings[968],
        strings[23],
        strings[456],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSpecificHeatCapacityMeasure_type = new type_declaration(strings[1211], 960, new simple_type(simple_type::real_type));
    IFC4X1_IfcSpecularExponent_type = new type_declaration(strings[1212], 961, new simple_type(simple_type::real_type));
    IFC4X1_IfcSpecularRoughness_type = new type_declaration(strings[1213], 963, new simple_type(simple_type::real_type));
    IFC4X1_IfcStackTerminalTypeEnum_type = new enumeration_type(strings[1214], 968, {
        strings[1215],
        strings[1216],
        strings[1217],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcStairFlightTypeEnum_type = new enumeration_type(strings[1218], 972, {
        strings[991],
        strings[1219],
        strings[992],
        strings[1220],
        strings[1071],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcStairTypeEnum_type = new enumeration_type(strings[1221], 974, {
        strings[1222],
        strings[1223],
        strings[1224],
        strings[1225],
        strings[1226],
        strings[1227],
        strings[1228],
        strings[1229],
        strings[1230],
        strings[1231],
        strings[1232],
        strings[1233],
        strings[1234],
        strings[1235],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcStateEnum_type = new enumeration_type(strings[1236], 975, {
        strings[1237],
        strings[1238],
        strings[1239],
        strings[1240],
        strings[1241]
    });
    IFC4X1_IfcStructuralCurveActivityTypeEnum_type = new enumeration_type(strings[1242], 983, {
        strings[1243],
        strings[321],
        strings[1244],
        strings[1245],
        strings[1246],
        strings[1247],
        strings[1248],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcStructuralCurveMemberTypeEnum_type = new enumeration_type(strings[1249], 986, {
        strings[1250],
        strings[1251],
        strings[416],
        strings[1252],
        strings[1253],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcStructuralSurfaceActivityTypeEnum_type = new enumeration_type(strings[1254], 1012, {
        strings[1243],
        strings[1255],
        strings[1248],
        strings[1256],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcStructuralSurfaceMemberTypeEnum_type = new enumeration_type(strings[1257], 1015, {
        strings[1258],
        strings[1259],
        strings[1260],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSubContractResourceTypeEnum_type = new enumeration_type(strings[1261], 1024, {
        strings[1262],
        strings[899],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSurfaceFeatureTypeEnum_type = new enumeration_type(strings[1263], 1030, {
        strings[1264],
        strings[1265],
        strings[1266],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSurfaceSide_type = new enumeration_type(strings[1267], 1035, {
        strings[400],
        strings[401],
        strings[1268]
    });
    IFC4X1_IfcSwitchingDeviceTypeEnum_type = new enumeration_type(strings[1269], 1050, {
        strings[1270],
        strings[1271],
        strings[1272],
        strings[1273],
        strings[1274],
        strings[1275],
        strings[1276],
        strings[1277],
        strings[1278],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcSystemFurnitureElementTypeEnum_type = new enumeration_type(strings[1279], 1054, {
        strings[1280],
        strings[1281],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcTankTypeEnum_type = new enumeration_type(strings[1282], 1060, {
        strings[1283],
        strings[1284],
        strings[1285],
        strings[1286],
        strings[1287],
        strings[1288],
        strings[1289],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcTaskDurationEnum_type = new enumeration_type(strings[1290], 1062, {
        strings[1291],
        strings[1292],
        strings[9]
    });
    IFC4X1_IfcTaskTypeEnum_type = new enumeration_type(strings[1293], 1066, {
        strings[1294],
        strings[1208],
        strings[1295],
        strings[1296],
        strings[431],
        strings[1297],
        strings[1298],
        strings[1299],
        strings[1300],
        strings[1301],
        strings[1302],
        strings[1303],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcTemperatureGradientMeasure_type = new type_declaration(strings[1304], 1068, new simple_type(simple_type::real_type));
    IFC4X1_IfcTemperatureRateOfChangeMeasure_type = new type_declaration(strings[1305], 1069, new simple_type(simple_type::real_type));
    IFC4X1_IfcTendonAnchorTypeEnum_type = new enumeration_type(strings[1306], 1073, {
        strings[1307],
        strings[1308],
        strings[1309],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcTendonTypeEnum_type = new enumeration_type(strings[1310], 1075, {
        strings[1311],
        strings[1312],
        strings[1313],
        strings[1314],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcText_type = new type_declaration(strings[1315], 1078, new simple_type(simple_type::string_type));
    IFC4X1_IfcTextAlignment_type = new type_declaration(strings[1316], 1079, new simple_type(simple_type::string_type));
    IFC4X1_IfcTextDecoration_type = new type_declaration(strings[1317], 1080, new simple_type(simple_type::string_type));
    IFC4X1_IfcTextFontName_type = new type_declaration(strings[1318], 1081, new simple_type(simple_type::string_type));
    IFC4X1_IfcTextPath_type = new enumeration_type(strings[1319], 1085, {
        strings[478],
        strings[480],
        strings[1320],
        strings[1321]
    });
    IFC4X1_IfcTextTransformation_type = new type_declaration(strings[1322], 1090, new simple_type(simple_type::string_type));
    IFC4X1_IfcThermalAdmittanceMeasure_type = new type_declaration(strings[1323], 1096, new simple_type(simple_type::real_type));
    IFC4X1_IfcThermalConductivityMeasure_type = new type_declaration(strings[1324], 1097, new simple_type(simple_type::real_type));
    IFC4X1_IfcThermalExpansionCoefficientMeasure_type = new type_declaration(strings[1325], 1098, new simple_type(simple_type::real_type));
    IFC4X1_IfcThermalResistanceMeasure_type = new type_declaration(strings[1326], 1099, new simple_type(simple_type::real_type));
    IFC4X1_IfcThermalTransmittanceMeasure_type = new type_declaration(strings[1327], 1100, new simple_type(simple_type::real_type));
    IFC4X1_IfcThermodynamicTemperatureMeasure_type = new type_declaration(strings[1328], 1101, new simple_type(simple_type::real_type));
    IFC4X1_IfcTime_type = new type_declaration(strings[1329], 1102, new simple_type(simple_type::string_type));
    IFC4X1_IfcTimeMeasure_type = new type_declaration(strings[1330], 1103, new simple_type(simple_type::real_type));
    IFC4X1_IfcTimeOrRatioSelect_type = new select_type(strings[1331], 1104, {
        IFC4X1_IfcDuration_type,
        IFC4X1_IfcRatioMeasure_type
    });
    IFC4X1_IfcTimeSeriesDataTypeEnum_type = new enumeration_type(strings[1332], 1107, {
        strings[1333],
        strings[1248],
        strings[1334],
        strings[1335],
        strings[1336],
        strings[1337],
        strings[9]
    });
    IFC4X1_IfcTimeStamp_type = new type_declaration(strings[1338], 1109, new simple_type(simple_type::integer_type));
    IFC4X1_IfcTorqueMeasure_type = new type_declaration(strings[1339], 1113, new simple_type(simple_type::real_type));
    IFC4X1_IfcTransformerTypeEnum_type = new enumeration_type(strings[1340], 1116, {
        strings[32],
        strings[1341],
        strings[1342],
        strings[1343],
        strings[1344],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcTransitionCode_type = new enumeration_type(strings[1345], 1117, {
        strings[1346],
        strings[1333],
        strings[1347],
        strings[1348]
    });
    IFC4X1_IfcTransitionCurveType_type = new enumeration_type(strings[1349], 1119, {
        strings[1350],
        strings[1351],
        strings[1352],
        strings[1353],
        strings[1354],
        strings[1355]
    });
    IFC4X1_IfcTranslationalStiffnessSelect_type = new select_type(strings[1356], 1120, {
        IFC4X1_IfcBoolean_type,
        IFC4X1_IfcLinearStiffnessMeasure_type
    });
    IFC4X1_IfcTransportElementTypeEnum_type = new enumeration_type(strings[1357], 1123, {
        strings[1358],
        strings[1359],
        strings[1360],
        strings[1361],
        strings[1362],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcTrimmingPreference_type = new enumeration_type(strings[1363], 1128, {
        strings[1364],
        strings[868],
        strings[116]
    });
    IFC4X1_IfcTubeBundleTypeEnum_type = new enumeration_type(strings[1365], 1133, {
        strings[1366],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcURIReference_type = new type_declaration(strings[1367], 1147, new simple_type(simple_type::string_type));
    IFC4X1_IfcUnitEnum_type = new enumeration_type(strings[1368], 1146, {
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
        strings[1386],
        strings[1387],
        strings[1388],
        strings[1389],
        strings[1390],
        strings[1391],
        strings[1392],
        strings[1393],
        strings[1394],
        strings[1395],
        strings[1396],
        strings[1397],
        strings[8]
    });
    IFC4X1_IfcUnitaryControlElementTypeEnum_type = new enumeration_type(strings[1398], 1141, {
        strings[1399],
        strings[1400],
        strings[1401],
        strings[1402],
        strings[1403],
        strings[1404],
        strings[1405],
        strings[1406],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcUnitaryEquipmentTypeEnum_type = new enumeration_type(strings[1407], 1144, {
        strings[1408],
        strings[1409],
        strings[1410],
        strings[1411],
        strings[1412],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcValveTypeEnum_type = new enumeration_type(strings[1413], 1152, {
        strings[1414],
        strings[1415],
        strings[1416],
        strings[1417],
        strings[1418],
        strings[1419],
        strings[1420],
        strings[1421],
        strings[1422],
        strings[1423],
        strings[1424],
        strings[1425],
        strings[1426],
        strings[1427],
        strings[1428],
        strings[1429],
        strings[1430],
        strings[1431],
        strings[1432],
        strings[1433],
        strings[1434],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcVaporPermeabilityMeasure_type = new type_declaration(strings[1435], 1153, new simple_type(simple_type::real_type));
    IFC4X1_IfcVibrationIsolatorTypeEnum_type = new enumeration_type(strings[1436], 1161, {
        strings[1437],
        strings[1438],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcVoidingFeatureTypeEnum_type = new enumeration_type(strings[1439], 1165, {
        strings[1440],
        strings[1441],
        strings[1442],
        strings[1443],
        strings[1444],
        strings[1028],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcVolumeMeasure_type = new type_declaration(strings[1445], 1166, new simple_type(simple_type::real_type));
    IFC4X1_IfcVolumetricFlowRateMeasure_type = new type_declaration(strings[1446], 1167, new simple_type(simple_type::real_type));
    IFC4X1_IfcWallTypeEnum_type = new enumeration_type(strings[1447], 1172, {
        strings[1448],
        strings[1449],
        strings[1450],
        strings[1451],
        strings[1025],
        strings[1452],
        strings[1453],
        strings[1244],
        strings[1454],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcWarpingConstantMeasure_type = new type_declaration(strings[1455], 1173, new simple_type(simple_type::real_type));
    IFC4X1_IfcWarpingMomentMeasure_type = new type_declaration(strings[1456], 1174, new simple_type(simple_type::real_type));
    IFC4X1_IfcWarpingStiffnessSelect_type = new select_type(strings[1457], 1175, {
        IFC4X1_IfcBoolean_type,
        IFC4X1_IfcWarpingMomentMeasure_type
    });
    IFC4X1_IfcWasteTerminalTypeEnum_type = new enumeration_type(strings[1458], 1178, {
        strings[1459],
        strings[1460],
        strings[1461],
        strings[1462],
        strings[1463],
        strings[1464],
        strings[1465],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcWindowPanelOperationEnum_type = new enumeration_type(strings[1466], 1181, {
        strings[1467],
        strings[1468],
        strings[1469],
        strings[1470],
        strings[1471],
        strings[1472],
        strings[1473],
        strings[1474],
        strings[1475],
        strings[1476],
        strings[1477],
        strings[1478],
        strings[1479],
        strings[9]
    });
    IFC4X1_IfcWindowPanelPositionEnum_type = new enumeration_type(strings[1480], 1182, {
        strings[478],
        strings[479],
        strings[480],
        strings[1481],
        strings[1482],
        strings[9]
    });
    IFC4X1_IfcWindowStyleConstructionEnum_type = new enumeration_type(strings[1483], 1186, {
        strings[482],
        strings[483],
        strings[484],
        strings[279],
        strings[485],
        strings[278],
        strings[1484],
        strings[9]
    });
    IFC4X1_IfcWindowStyleOperationEnum_type = new enumeration_type(strings[1485], 1187, {
        strings[1486],
        strings[1487],
        strings[1488],
        strings[1489],
        strings[1490],
        strings[1491],
        strings[1492],
        strings[1493],
        strings[1494],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcWindowTypeEnum_type = new enumeration_type(strings[1495], 1189, {
        strings[1496],
        strings[1497],
        strings[1498],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcWindowTypePartitioningEnum_type = new enumeration_type(strings[1499], 1190, {
        strings[1486],
        strings[1487],
        strings[1488],
        strings[1489],
        strings[1490],
        strings[1491],
        strings[1492],
        strings[1493],
        strings[1494],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcWorkCalendarTypeEnum_type = new enumeration_type(strings[1500], 1192, {
        strings[1501],
        strings[1502],
        strings[1503],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcWorkPlanTypeEnum_type = new enumeration_type(strings[1504], 1195, {
        strings[1505],
        strings[1506],
        strings[1507],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcWorkScheduleTypeEnum_type = new enumeration_type(strings[1508], 1197, {
        strings[1505],
        strings[1506],
        strings[1507],
        strings[8],
        strings[9]
    });
    IFC4X1_IfcActorRole_type = new entity(strings[1509], false, 7, 0);
    IFC4X1_IfcAddress_type = new entity(strings[1510], true, 12, 0);
    IFC4X1_IfcApplication_type = new entity(strings[1511], false, 46, 0);
    IFC4X1_IfcAppliedValue_type = new entity(strings[1512], false, 47, 0);
    IFC4X1_IfcApproval_type = new entity(strings[1513], false, 49, 0);
    IFC4X1_IfcBoundaryCondition_type = new entity(strings[1514], true, 85, 0);
    IFC4X1_IfcBoundaryEdgeCondition_type = new entity(strings[1515], false, 87, IFC4X1_IfcBoundaryCondition_type);
    IFC4X1_IfcBoundaryFaceCondition_type = new entity(strings[1516], false, 88, IFC4X1_IfcBoundaryCondition_type);
    IFC4X1_IfcBoundaryNodeCondition_type = new entity(strings[1517], false, 89, IFC4X1_IfcBoundaryCondition_type);
    IFC4X1_IfcBoundaryNodeConditionWarping_type = new entity(strings[1518], false, 90, IFC4X1_IfcBoundaryNodeCondition_type);
    IFC4X1_IfcConnectionGeometry_type = new entity(strings[1519], true, 191, 0);
    IFC4X1_IfcConnectionPointGeometry_type = new entity(strings[1520], false, 193, IFC4X1_IfcConnectionGeometry_type);
    IFC4X1_IfcConnectionSurfaceGeometry_type = new entity(strings[1521], false, 194, IFC4X1_IfcConnectionGeometry_type);
    IFC4X1_IfcConnectionVolumeGeometry_type = new entity(strings[1522], false, 196, IFC4X1_IfcConnectionGeometry_type);
    IFC4X1_IfcConstraint_type = new entity(strings[1523], true, 197, 0);
    IFC4X1_IfcCoordinateOperation_type = new entity(strings[1524], true, 225, 0);
    IFC4X1_IfcCoordinateReferenceSystem_type = new entity(strings[1525], true, 226, 0);
    IFC4X1_IfcCostValue_type = new entity(strings[1526], false, 232, IFC4X1_IfcAppliedValue_type);
    IFC4X1_IfcDerivedUnit_type = new entity(strings[1527], false, 274, 0);
    IFC4X1_IfcDerivedUnitElement_type = new entity(strings[1528], false, 275, 0);
    IFC4X1_IfcDimensionalExponents_type = new entity(strings[1529], false, 278, 0);
    IFC4X1_IfcExternalInformation_type = new entity(strings[1530], true, 389, 0);
    IFC4X1_IfcExternalReference_type = new entity(strings[1531], true, 393, 0);
    IFC4X1_IfcExternallyDefinedHatchStyle_type = new entity(strings[1532], false, 390, IFC4X1_IfcExternalReference_type);
    IFC4X1_IfcExternallyDefinedSurfaceStyle_type = new entity(strings[1533], false, 391, IFC4X1_IfcExternalReference_type);
    IFC4X1_IfcExternallyDefinedTextFont_type = new entity(strings[1534], false, 392, IFC4X1_IfcExternalReference_type);
    IFC4X1_IfcGridAxis_type = new entity(strings[1535], false, 475, 0);
    IFC4X1_IfcIrregularTimeSeriesValue_type = new entity(strings[1536], false, 511, 0);
    IFC4X1_IfcLibraryInformation_type = new entity(strings[1537], false, 531, IFC4X1_IfcExternalInformation_type);
    IFC4X1_IfcLibraryReference_type = new entity(strings[1538], false, 532, IFC4X1_IfcExternalReference_type);
    IFC4X1_IfcLightDistributionData_type = new entity(strings[1539], false, 535, 0);
    IFC4X1_IfcLightIntensityDistribution_type = new entity(strings[1540], false, 541, 0);
    IFC4X1_IfcMapConversion_type = new entity(strings[1541], false, 569, IFC4X1_IfcCoordinateOperation_type);
    IFC4X1_IfcMaterialClassificationRelationship_type = new entity(strings[1542], false, 576, 0);
    IFC4X1_IfcMaterialDefinition_type = new entity(strings[1543], true, 579, 0);
    IFC4X1_IfcMaterialLayer_type = new entity(strings[1544], false, 581, IFC4X1_IfcMaterialDefinition_type);
    IFC4X1_IfcMaterialLayerSet_type = new entity(strings[1545], false, 582, IFC4X1_IfcMaterialDefinition_type);
    IFC4X1_IfcMaterialLayerWithOffsets_type = new entity(strings[1546], false, 584, IFC4X1_IfcMaterialLayer_type);
    IFC4X1_IfcMaterialList_type = new entity(strings[1547], false, 585, 0);
    IFC4X1_IfcMaterialProfile_type = new entity(strings[1548], false, 586, IFC4X1_IfcMaterialDefinition_type);
    IFC4X1_IfcMaterialProfileSet_type = new entity(strings[1549], false, 587, IFC4X1_IfcMaterialDefinition_type);
    IFC4X1_IfcMaterialProfileWithOffsets_type = new entity(strings[1550], false, 590, IFC4X1_IfcMaterialProfile_type);
    IFC4X1_IfcMaterialUsageDefinition_type = new entity(strings[1551], true, 594, 0);
    IFC4X1_IfcMeasureWithUnit_type = new entity(strings[1552], false, 596, 0);
    IFC4X1_IfcMetric_type = new entity(strings[1553], false, 607, IFC4X1_IfcConstraint_type);
    IFC4X1_IfcMonetaryUnit_type = new entity(strings[1554], false, 621, 0);
    IFC4X1_IfcNamedUnit_type = new entity(strings[1555], true, 626, 0);
    IFC4X1_IfcObjectPlacement_type = new entity(strings[1556], true, 635, 0);
    IFC4X1_IfcObjective_type = new entity(strings[1557], false, 633, IFC4X1_IfcConstraint_type);
    IFC4X1_IfcOrganization_type = new entity(strings[1558], false, 648, 0);
    IFC4X1_IfcOwnerHistory_type = new entity(strings[1559], false, 656, 0);
    IFC4X1_IfcPerson_type = new entity(strings[1560], false, 667, 0);
    IFC4X1_IfcPersonAndOrganization_type = new entity(strings[1561], false, 668, 0);
    IFC4X1_IfcPhysicalQuantity_type = new entity(strings[1562], true, 672, 0);
    IFC4X1_IfcPhysicalSimpleQuantity_type = new entity(strings[1563], true, 673, IFC4X1_IfcPhysicalQuantity_type);
    IFC4X1_IfcPostalAddress_type = new entity(strings[1564], false, 709, IFC4X1_IfcAddress_type);
    IFC4X1_IfcPresentationItem_type = new entity(strings[1565], true, 719, 0);
    IFC4X1_IfcPresentationLayerAssignment_type = new entity(strings[1566], false, 720, 0);
    IFC4X1_IfcPresentationLayerWithStyle_type = new entity(strings[1567], false, 721, IFC4X1_IfcPresentationLayerAssignment_type);
    IFC4X1_IfcPresentationStyle_type = new entity(strings[1568], true, 722, 0);
    IFC4X1_IfcPresentationStyleAssignment_type = new entity(strings[1569], false, 723, 0);
    IFC4X1_IfcProductRepresentation_type = new entity(strings[1570], true, 733, 0);
    IFC4X1_IfcProfileDef_type = new entity(strings[1571], false, 736, 0);
    IFC4X1_IfcProjectedCRS_type = new entity(strings[1572], false, 740, IFC4X1_IfcCoordinateReferenceSystem_type);
    IFC4X1_IfcPropertyAbstraction_type = new entity(strings[1573], true, 748, 0);
    IFC4X1_IfcPropertyEnumeration_type = new entity(strings[1574], false, 753, IFC4X1_IfcPropertyAbstraction_type);
    IFC4X1_IfcQuantityArea_type = new entity(strings[1575], false, 776, IFC4X1_IfcPhysicalSimpleQuantity_type);
    IFC4X1_IfcQuantityCount_type = new entity(strings[1576], false, 777, IFC4X1_IfcPhysicalSimpleQuantity_type);
    IFC4X1_IfcQuantityLength_type = new entity(strings[1577], false, 778, IFC4X1_IfcPhysicalSimpleQuantity_type);
    IFC4X1_IfcQuantityTime_type = new entity(strings[1578], false, 780, IFC4X1_IfcPhysicalSimpleQuantity_type);
    IFC4X1_IfcQuantityVolume_type = new entity(strings[1579], false, 781, IFC4X1_IfcPhysicalSimpleQuantity_type);
    IFC4X1_IfcQuantityWeight_type = new entity(strings[1580], false, 782, IFC4X1_IfcPhysicalSimpleQuantity_type);
    IFC4X1_IfcRecurrencePattern_type = new entity(strings[1581], false, 801, 0);
    IFC4X1_IfcReference_type = new entity(strings[1582], false, 803, 0);
    IFC4X1_IfcRepresentation_type = new entity(strings[1583], true, 869, 0);
    IFC4X1_IfcRepresentationContext_type = new entity(strings[1584], true, 870, 0);
    IFC4X1_IfcRepresentationItem_type = new entity(strings[1585], true, 871, 0);
    IFC4X1_IfcRepresentationMap_type = new entity(strings[1586], false, 872, 0);
    IFC4X1_IfcResourceLevelRelationship_type = new entity(strings[1587], true, 876, 0);
    IFC4X1_IfcRoot_type = new entity(strings[1588], true, 888, 0);
    IFC4X1_IfcSIUnit_type = new entity(strings[1589], false, 927, IFC4X1_IfcNamedUnit_type);
    IFC4X1_IfcSchedulingTime_type = new entity(strings[1590], true, 897, 0);
    IFC4X1_IfcShapeAspect_type = new entity(strings[1591], false, 915, 0);
    IFC4X1_IfcShapeModel_type = new entity(strings[1592], true, 916, IFC4X1_IfcRepresentation_type);
    IFC4X1_IfcShapeRepresentation_type = new entity(strings[1593], false, 917, IFC4X1_IfcShapeModel_type);
    IFC4X1_IfcStructuralConnectionCondition_type = new entity(strings[1594], true, 981, 0);
    IFC4X1_IfcStructuralLoad_type = new entity(strings[1595], true, 991, 0);
    IFC4X1_IfcStructuralLoadConfiguration_type = new entity(strings[1596], false, 993, IFC4X1_IfcStructuralLoad_type);
    IFC4X1_IfcStructuralLoadOrResult_type = new entity(strings[1597], true, 996, IFC4X1_IfcStructuralLoad_type);
    IFC4X1_IfcStructuralLoadStatic_type = new entity(strings[1598], true, 1002, IFC4X1_IfcStructuralLoadOrResult_type);
    IFC4X1_IfcStructuralLoadTemperature_type = new entity(strings[1599], false, 1003, IFC4X1_IfcStructuralLoadStatic_type);
    IFC4X1_IfcStyleModel_type = new entity(strings[1600], true, 1021, IFC4X1_IfcRepresentation_type);
    IFC4X1_IfcStyledItem_type = new entity(strings[1601], false, 1019, IFC4X1_IfcRepresentationItem_type);
    IFC4X1_IfcStyledRepresentation_type = new entity(strings[1602], false, 1020, IFC4X1_IfcStyleModel_type);
    IFC4X1_IfcSurfaceReinforcementArea_type = new entity(strings[1603], false, 1034, IFC4X1_IfcStructuralLoadOrResult_type);
    IFC4X1_IfcSurfaceStyle_type = new entity(strings[1604], false, 1036, IFC4X1_IfcPresentationStyle_type);
    IFC4X1_IfcSurfaceStyleLighting_type = new entity(strings[1605], false, 1038, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcSurfaceStyleRefraction_type = new entity(strings[1606], false, 1039, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcSurfaceStyleShading_type = new entity(strings[1607], false, 1041, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcSurfaceStyleWithTextures_type = new entity(strings[1608], false, 1042, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcSurfaceTexture_type = new entity(strings[1609], true, 1043, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcTable_type = new entity(strings[1610], false, 1055, 0);
    IFC4X1_IfcTableColumn_type = new entity(strings[1611], false, 1056, 0);
    IFC4X1_IfcTableRow_type = new entity(strings[1612], false, 1057, 0);
    IFC4X1_IfcTaskTime_type = new entity(strings[1613], false, 1063, IFC4X1_IfcSchedulingTime_type);
    IFC4X1_IfcTaskTimeRecurring_type = new entity(strings[1614], false, 1064, IFC4X1_IfcTaskTime_type);
    IFC4X1_IfcTelecomAddress_type = new entity(strings[1615], false, 1067, IFC4X1_IfcAddress_type);
    IFC4X1_IfcTextStyle_type = new entity(strings[1616], false, 1086, IFC4X1_IfcPresentationStyle_type);
    IFC4X1_IfcTextStyleForDefinedFont_type = new entity(strings[1617], false, 1088, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcTextStyleTextModel_type = new entity(strings[1618], false, 1089, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcTextureCoordinate_type = new entity(strings[1619], true, 1091, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcTextureCoordinateGenerator_type = new entity(strings[1620], false, 1092, IFC4X1_IfcTextureCoordinate_type);
    IFC4X1_IfcTextureMap_type = new entity(strings[1621], false, 1093, IFC4X1_IfcTextureCoordinate_type);
    IFC4X1_IfcTextureVertex_type = new entity(strings[1622], false, 1094, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcTextureVertexList_type = new entity(strings[1623], false, 1095, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcTimePeriod_type = new entity(strings[1624], false, 1105, 0);
    IFC4X1_IfcTimeSeries_type = new entity(strings[1625], true, 1106, 0);
    IFC4X1_IfcTimeSeriesValue_type = new entity(strings[1626], false, 1108, 0);
    IFC4X1_IfcTopologicalRepresentationItem_type = new entity(strings[1627], true, 1110, IFC4X1_IfcRepresentationItem_type);
    IFC4X1_IfcTopologyRepresentation_type = new entity(strings[1628], false, 1111, IFC4X1_IfcShapeModel_type);
    IFC4X1_IfcUnitAssignment_type = new entity(strings[1629], false, 1145, 0);
    IFC4X1_IfcVertex_type = new entity(strings[1630], false, 1156, IFC4X1_IfcTopologicalRepresentationItem_type);
    IFC4X1_IfcVertexPoint_type = new entity(strings[1631], false, 1158, IFC4X1_IfcVertex_type);
    IFC4X1_IfcVirtualGridIntersection_type = new entity(strings[1632], false, 1163, 0);
    IFC4X1_IfcWorkTime_type = new entity(strings[1633], false, 1198, IFC4X1_IfcSchedulingTime_type);
    IFC4X1_IfcActorSelect_type = new select_type(strings[1634], 8, {
        IFC4X1_IfcOrganization_type,
        IFC4X1_IfcPerson_type,
        IFC4X1_IfcPersonAndOrganization_type
    });
    IFC4X1_IfcArcIndex_type = new type_declaration(strings[1635], 54, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_IfcPositiveInteger_type)));
    IFC4X1_IfcBendingParameterSelect_type = new select_type(strings[1636], 73, {
        IFC4X1_IfcLengthMeasure_type,
        IFC4X1_IfcPlaneAngleMeasure_type
    });
    IFC4X1_IfcBoxAlignment_type = new type_declaration(strings[1637], 94, new named_type(IFC4X1_IfcLabel_type));
    IFC4X1_IfcDerivedMeasureValue_type = new select_type(strings[1638], 272, {
        IFC4X1_IfcAbsorbedDoseMeasure_type,
        IFC4X1_IfcAccelerationMeasure_type,
        IFC4X1_IfcAngularVelocityMeasure_type,
        IFC4X1_IfcAreaDensityMeasure_type,
        IFC4X1_IfcCompoundPlaneAngleMeasure_type,
        IFC4X1_IfcCurvatureMeasure_type,
        IFC4X1_IfcDoseEquivalentMeasure_type,
        IFC4X1_IfcDynamicViscosityMeasure_type,
        IFC4X1_IfcElectricCapacitanceMeasure_type,
        IFC4X1_IfcElectricChargeMeasure_type,
        IFC4X1_IfcElectricConductanceMeasure_type,
        IFC4X1_IfcElectricResistanceMeasure_type,
        IFC4X1_IfcElectricVoltageMeasure_type,
        IFC4X1_IfcEnergyMeasure_type,
        IFC4X1_IfcForceMeasure_type,
        IFC4X1_IfcFrequencyMeasure_type,
        IFC4X1_IfcHeatFluxDensityMeasure_type,
        IFC4X1_IfcHeatingValueMeasure_type,
        IFC4X1_IfcIlluminanceMeasure_type,
        IFC4X1_IfcInductanceMeasure_type,
        IFC4X1_IfcIntegerCountRateMeasure_type,
        IFC4X1_IfcIonConcentrationMeasure_type,
        IFC4X1_IfcIsothermalMoistureCapacityMeasure_type,
        IFC4X1_IfcKinematicViscosityMeasure_type,
        IFC4X1_IfcLinearForceMeasure_type,
        IFC4X1_IfcLinearMomentMeasure_type,
        IFC4X1_IfcLinearStiffnessMeasure_type,
        IFC4X1_IfcLinearVelocityMeasure_type,
        IFC4X1_IfcLuminousFluxMeasure_type,
        IFC4X1_IfcLuminousIntensityDistributionMeasure_type,
        IFC4X1_IfcMagneticFluxDensityMeasure_type,
        IFC4X1_IfcMagneticFluxMeasure_type,
        IFC4X1_IfcMassDensityMeasure_type,
        IFC4X1_IfcMassFlowRateMeasure_type,
        IFC4X1_IfcMassPerLengthMeasure_type,
        IFC4X1_IfcModulusOfElasticityMeasure_type,
        IFC4X1_IfcModulusOfLinearSubgradeReactionMeasure_type,
        IFC4X1_IfcModulusOfRotationalSubgradeReactionMeasure_type,
        IFC4X1_IfcModulusOfSubgradeReactionMeasure_type,
        IFC4X1_IfcMoistureDiffusivityMeasure_type,
        IFC4X1_IfcMolecularWeightMeasure_type,
        IFC4X1_IfcMomentOfInertiaMeasure_type,
        IFC4X1_IfcMonetaryMeasure_type,
        IFC4X1_IfcPHMeasure_type,
        IFC4X1_IfcPlanarForceMeasure_type,
        IFC4X1_IfcPowerMeasure_type,
        IFC4X1_IfcPressureMeasure_type,
        IFC4X1_IfcRadioActivityMeasure_type,
        IFC4X1_IfcRotationalFrequencyMeasure_type,
        IFC4X1_IfcRotationalMassMeasure_type,
        IFC4X1_IfcRotationalStiffnessMeasure_type,
        IFC4X1_IfcSectionModulusMeasure_type,
        IFC4X1_IfcSectionalAreaIntegralMeasure_type,
        IFC4X1_IfcShearModulusMeasure_type,
        IFC4X1_IfcSoundPowerLevelMeasure_type,
        IFC4X1_IfcSoundPowerMeasure_type,
        IFC4X1_IfcSoundPressureLevelMeasure_type,
        IFC4X1_IfcSoundPressureMeasure_type,
        IFC4X1_IfcSpecificHeatCapacityMeasure_type,
        IFC4X1_IfcTemperatureGradientMeasure_type,
        IFC4X1_IfcTemperatureRateOfChangeMeasure_type,
        IFC4X1_IfcThermalAdmittanceMeasure_type,
        IFC4X1_IfcThermalConductivityMeasure_type,
        IFC4X1_IfcThermalExpansionCoefficientMeasure_type,
        IFC4X1_IfcThermalResistanceMeasure_type,
        IFC4X1_IfcThermalTransmittanceMeasure_type,
        IFC4X1_IfcTorqueMeasure_type,
        IFC4X1_IfcVaporPermeabilityMeasure_type,
        IFC4X1_IfcVolumetricFlowRateMeasure_type,
        IFC4X1_IfcWarpingConstantMeasure_type,
        IFC4X1_IfcWarpingMomentMeasure_type
    });
    IFC4X1_IfcLayeredItem_type = new select_type(strings[1639], 528, {
        IFC4X1_IfcRepresentation_type,
        IFC4X1_IfcRepresentationItem_type
    });
    IFC4X1_IfcLibrarySelect_type = new select_type(strings[1640], 533, {
        IFC4X1_IfcLibraryInformation_type,
        IFC4X1_IfcLibraryReference_type
    });
    IFC4X1_IfcLightDistributionDataSourceSelect_type = new select_type(strings[1641], 536, {
        IFC4X1_IfcExternalReference_type,
        IFC4X1_IfcLightIntensityDistribution_type
    });
    IFC4X1_IfcLineIndex_type = new type_declaration(strings[1642], 555, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcPositiveInteger_type)));
    IFC4X1_IfcMaterialSelect_type = new select_type(strings[1643], 593, {
        IFC4X1_IfcMaterialDefinition_type,
        IFC4X1_IfcMaterialList_type,
        IFC4X1_IfcMaterialUsageDefinition_type
    });
    IFC4X1_IfcNormalisedRatioMeasure_type = new type_declaration(strings[1644], 628, new named_type(IFC4X1_IfcRatioMeasure_type));
    IFC4X1_IfcObjectReferenceSelect_type = new select_type(strings[1645], 636, {
        IFC4X1_IfcAddress_type,
        IFC4X1_IfcAppliedValue_type,
        IFC4X1_IfcExternalReference_type,
        IFC4X1_IfcMaterialDefinition_type,
        IFC4X1_IfcOrganization_type,
        IFC4X1_IfcPerson_type,
        IFC4X1_IfcPersonAndOrganization_type,
        IFC4X1_IfcTable_type,
        IFC4X1_IfcTimeSeries_type
    });
    IFC4X1_IfcPositiveRatioMeasure_type = new type_declaration(strings[1646], 708, new named_type(IFC4X1_IfcRatioMeasure_type));
    IFC4X1_IfcSegmentIndexSelect_type = new select_type(strings[1647], 907, {
        IFC4X1_IfcArcIndex_type,
        IFC4X1_IfcLineIndex_type
    });
    IFC4X1_IfcSimpleValue_type = new select_type(strings[1648], 924, {
        IFC4X1_IfcBinary_type,
        IFC4X1_IfcBoolean_type,
        IFC4X1_IfcDate_type,
        IFC4X1_IfcDateTime_type,
        IFC4X1_IfcDuration_type,
        IFC4X1_IfcIdentifier_type,
        IFC4X1_IfcInteger_type,
        IFC4X1_IfcLabel_type,
        IFC4X1_IfcLogical_type,
        IFC4X1_IfcPositiveInteger_type,
        IFC4X1_IfcReal_type,
        IFC4X1_IfcText_type,
        IFC4X1_IfcTime_type,
        IFC4X1_IfcTimeStamp_type
    });
    IFC4X1_IfcSizeSelect_type = new select_type(strings[1649], 929, {
        IFC4X1_IfcDescriptiveMeasure_type,
        IFC4X1_IfcLengthMeasure_type,
        IFC4X1_IfcNormalisedRatioMeasure_type,
        IFC4X1_IfcPositiveLengthMeasure_type,
        IFC4X1_IfcPositiveRatioMeasure_type,
        IFC4X1_IfcRatioMeasure_type
    });
    IFC4X1_IfcSpecularHighlightSelect_type = new select_type(strings[1650], 962, {
        IFC4X1_IfcSpecularExponent_type,
        IFC4X1_IfcSpecularRoughness_type
    });
    IFC4X1_IfcStyleAssignmentSelect_type = new select_type(strings[1651], 1018, {
        IFC4X1_IfcPresentationStyle_type,
        IFC4X1_IfcPresentationStyleAssignment_type
    });
    IFC4X1_IfcSurfaceStyleElementSelect_type = new select_type(strings[1652], 1037, {
        IFC4X1_IfcExternallyDefinedSurfaceStyle_type,
        IFC4X1_IfcSurfaceStyleLighting_type,
        IFC4X1_IfcSurfaceStyleRefraction_type,
        IFC4X1_IfcSurfaceStyleShading_type,
        IFC4X1_IfcSurfaceStyleWithTextures_type
    });
    IFC4X1_IfcUnit_type = new select_type(strings[1653], 1138, {
        IFC4X1_IfcDerivedUnit_type,
        IFC4X1_IfcMonetaryUnit_type,
        IFC4X1_IfcNamedUnit_type
    });
    IFC4X1_IfcApprovalRelationship_type = new entity(strings[1654], false, 50, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcArbitraryClosedProfileDef_type = new entity(strings[1655], false, 51, IFC4X1_IfcProfileDef_type);
    IFC4X1_IfcArbitraryOpenProfileDef_type = new entity(strings[1656], false, 52, IFC4X1_IfcProfileDef_type);
    IFC4X1_IfcArbitraryProfileDefWithVoids_type = new entity(strings[1657], false, 53, IFC4X1_IfcArbitraryClosedProfileDef_type);
    IFC4X1_IfcBlobTexture_type = new entity(strings[1658], false, 75, IFC4X1_IfcSurfaceTexture_type);
    IFC4X1_IfcCenterLineProfileDef_type = new entity(strings[1659], false, 139, IFC4X1_IfcArbitraryOpenProfileDef_type);
    IFC4X1_IfcClassification_type = new entity(strings[1660], false, 153, IFC4X1_IfcExternalInformation_type);
    IFC4X1_IfcClassificationReference_type = new entity(strings[1661], false, 154, IFC4X1_IfcExternalReference_type);
    IFC4X1_IfcColourRgbList_type = new entity(strings[1662], false, 164, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcColourSpecification_type = new entity(strings[1663], true, 165, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcCompositeProfileDef_type = new entity(strings[1664], false, 180, IFC4X1_IfcProfileDef_type);
    IFC4X1_IfcConnectedFaceSet_type = new entity(strings[1665], false, 189, IFC4X1_IfcTopologicalRepresentationItem_type);
    IFC4X1_IfcConnectionCurveGeometry_type = new entity(strings[1666], false, 190, IFC4X1_IfcConnectionGeometry_type);
    IFC4X1_IfcConnectionPointEccentricity_type = new entity(strings[1667], false, 192, IFC4X1_IfcConnectionPointGeometry_type);
    IFC4X1_IfcContextDependentUnit_type = new entity(strings[1668], false, 212, IFC4X1_IfcNamedUnit_type);
    IFC4X1_IfcConversionBasedUnit_type = new entity(strings[1669], false, 217, IFC4X1_IfcNamedUnit_type);
    IFC4X1_IfcConversionBasedUnitWithOffset_type = new entity(strings[1670], false, 218, IFC4X1_IfcConversionBasedUnit_type);
    IFC4X1_IfcCurrencyRelationship_type = new entity(strings[1671], false, 244, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcCurveStyle_type = new entity(strings[1672], false, 257, IFC4X1_IfcPresentationStyle_type);
    IFC4X1_IfcCurveStyleFont_type = new entity(strings[1673], false, 258, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcCurveStyleFontAndScaling_type = new entity(strings[1674], false, 259, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcCurveStyleFontPattern_type = new entity(strings[1675], false, 260, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcDerivedProfileDef_type = new entity(strings[1676], false, 273, IFC4X1_IfcProfileDef_type);
    IFC4X1_IfcDocumentInformation_type = new entity(strings[1677], false, 301, IFC4X1_IfcExternalInformation_type);
    IFC4X1_IfcDocumentInformationRelationship_type = new entity(strings[1678], false, 302, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcDocumentReference_type = new entity(strings[1679], false, 303, IFC4X1_IfcExternalReference_type);
    IFC4X1_IfcEdge_type = new entity(strings[1680], false, 332, IFC4X1_IfcTopologicalRepresentationItem_type);
    IFC4X1_IfcEdgeCurve_type = new entity(strings[1681], false, 333, IFC4X1_IfcEdge_type);
    IFC4X1_IfcEventTime_type = new entity(strings[1682], false, 384, IFC4X1_IfcSchedulingTime_type);
    IFC4X1_IfcExtendedProperties_type = new entity(strings[1683], true, 388, IFC4X1_IfcPropertyAbstraction_type);
    IFC4X1_IfcExternalReferenceRelationship_type = new entity(strings[1684], false, 394, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcFace_type = new entity(strings[1685], false, 400, IFC4X1_IfcTopologicalRepresentationItem_type);
    IFC4X1_IfcFaceBound_type = new entity(strings[1686], false, 402, IFC4X1_IfcTopologicalRepresentationItem_type);
    IFC4X1_IfcFaceOuterBound_type = new entity(strings[1687], false, 403, IFC4X1_IfcFaceBound_type);
    IFC4X1_IfcFaceSurface_type = new entity(strings[1688], false, 404, IFC4X1_IfcFace_type);
    IFC4X1_IfcFailureConnectionCondition_type = new entity(strings[1689], false, 407, IFC4X1_IfcStructuralConnectionCondition_type);
    IFC4X1_IfcFillAreaStyle_type = new entity(strings[1690], false, 417, IFC4X1_IfcPresentationStyle_type);
    IFC4X1_IfcGeometricRepresentationContext_type = new entity(strings[1691], false, 467, IFC4X1_IfcRepresentationContext_type);
    IFC4X1_IfcGeometricRepresentationItem_type = new entity(strings[1692], true, 468, IFC4X1_IfcRepresentationItem_type);
    IFC4X1_IfcGeometricRepresentationSubContext_type = new entity(strings[1693], false, 469, IFC4X1_IfcGeometricRepresentationContext_type);
    IFC4X1_IfcGeometricSet_type = new entity(strings[1694], false, 470, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcGridPlacement_type = new entity(strings[1695], false, 476, IFC4X1_IfcObjectPlacement_type);
    IFC4X1_IfcHalfSpaceSolid_type = new entity(strings[1696], false, 480, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcImageTexture_type = new entity(strings[1697], false, 492, IFC4X1_IfcSurfaceTexture_type);
    IFC4X1_IfcIndexedColourMap_type = new entity(strings[1698], false, 493, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcIndexedTextureMap_type = new entity(strings[1699], true, 497, IFC4X1_IfcTextureCoordinate_type);
    IFC4X1_IfcIndexedTriangleTextureMap_type = new entity(strings[1700], false, 498, IFC4X1_IfcIndexedTextureMap_type);
    IFC4X1_IfcIrregularTimeSeries_type = new entity(strings[1701], false, 510, IFC4X1_IfcTimeSeries_type);
    IFC4X1_IfcLagTime_type = new entity(strings[1702], false, 523, IFC4X1_IfcSchedulingTime_type);
    IFC4X1_IfcLightSource_type = new entity(strings[1703], true, 542, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcLightSourceAmbient_type = new entity(strings[1704], false, 543, IFC4X1_IfcLightSource_type);
    IFC4X1_IfcLightSourceDirectional_type = new entity(strings[1705], false, 544, IFC4X1_IfcLightSource_type);
    IFC4X1_IfcLightSourceGoniometric_type = new entity(strings[1706], false, 545, IFC4X1_IfcLightSource_type);
    IFC4X1_IfcLightSourcePositional_type = new entity(strings[1707], false, 546, IFC4X1_IfcLightSource_type);
    IFC4X1_IfcLightSourceSpot_type = new entity(strings[1708], false, 547, IFC4X1_IfcLightSourcePositional_type);
    IFC4X1_IfcLinearPlacement_type = new entity(strings[1709], false, 551, IFC4X1_IfcObjectPlacement_type);
    IFC4X1_IfcLocalPlacement_type = new entity(strings[1710], false, 558, IFC4X1_IfcObjectPlacement_type);
    IFC4X1_IfcLoop_type = new entity(strings[1711], false, 561, IFC4X1_IfcTopologicalRepresentationItem_type);
    IFC4X1_IfcMappedItem_type = new entity(strings[1712], false, 570, IFC4X1_IfcRepresentationItem_type);
    IFC4X1_IfcMaterial_type = new entity(strings[1713], false, 575, IFC4X1_IfcMaterialDefinition_type);
    IFC4X1_IfcMaterialConstituent_type = new entity(strings[1714], false, 577, IFC4X1_IfcMaterialDefinition_type);
    IFC4X1_IfcMaterialConstituentSet_type = new entity(strings[1715], false, 578, IFC4X1_IfcMaterialDefinition_type);
    IFC4X1_IfcMaterialDefinitionRepresentation_type = new entity(strings[1716], false, 580, IFC4X1_IfcProductRepresentation_type);
    IFC4X1_IfcMaterialLayerSetUsage_type = new entity(strings[1717], false, 583, IFC4X1_IfcMaterialUsageDefinition_type);
    IFC4X1_IfcMaterialProfileSetUsage_type = new entity(strings[1718], false, 588, IFC4X1_IfcMaterialUsageDefinition_type);
    IFC4X1_IfcMaterialProfileSetUsageTapering_type = new entity(strings[1719], false, 589, IFC4X1_IfcMaterialProfileSetUsage_type);
    IFC4X1_IfcMaterialProperties_type = new entity(strings[1720], false, 591, IFC4X1_IfcExtendedProperties_type);
    IFC4X1_IfcMaterialRelationship_type = new entity(strings[1721], false, 592, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcMirroredProfileDef_type = new entity(strings[1722], false, 609, IFC4X1_IfcDerivedProfileDef_type);
    IFC4X1_IfcObjectDefinition_type = new entity(strings[1723], true, 632, IFC4X1_IfcRoot_type);
    IFC4X1_IfcOpenShell_type = new entity(strings[1724], false, 647, IFC4X1_IfcConnectedFaceSet_type);
    IFC4X1_IfcOrganizationRelationship_type = new entity(strings[1725], false, 649, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcOrientationExpression_type = new entity(strings[1726], false, 650, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcOrientedEdge_type = new entity(strings[1727], false, 651, IFC4X1_IfcEdge_type);
    IFC4X1_IfcParameterizedProfileDef_type = new entity(strings[1728], true, 657, IFC4X1_IfcProfileDef_type);
    IFC4X1_IfcPath_type = new entity(strings[1729], false, 659, IFC4X1_IfcTopologicalRepresentationItem_type);
    IFC4X1_IfcPhysicalComplexQuantity_type = new entity(strings[1730], false, 670, IFC4X1_IfcPhysicalQuantity_type);
    IFC4X1_IfcPixelTexture_type = new entity(strings[1731], false, 684, IFC4X1_IfcSurfaceTexture_type);
    IFC4X1_IfcPlacement_type = new entity(strings[1732], true, 685, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcPlanarExtent_type = new entity(strings[1733], false, 687, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcPoint_type = new entity(strings[1734], true, 695, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcPointOnCurve_type = new entity(strings[1735], false, 696, IFC4X1_IfcPoint_type);
    IFC4X1_IfcPointOnSurface_type = new entity(strings[1736], false, 697, IFC4X1_IfcPoint_type);
    IFC4X1_IfcPolyLoop_type = new entity(strings[1737], false, 702, IFC4X1_IfcLoop_type);
    IFC4X1_IfcPolygonalBoundedHalfSpace_type = new entity(strings[1738], false, 699, IFC4X1_IfcHalfSpaceSolid_type);
    IFC4X1_IfcPreDefinedItem_type = new entity(strings[1739], true, 713, IFC4X1_IfcPresentationItem_type);
    IFC4X1_IfcPreDefinedProperties_type = new entity(strings[1740], true, 714, IFC4X1_IfcPropertyAbstraction_type);
    IFC4X1_IfcPreDefinedTextFont_type = new entity(strings[1741], true, 716, IFC4X1_IfcPreDefinedItem_type);
    IFC4X1_IfcProductDefinitionShape_type = new entity(strings[1742], false, 732, IFC4X1_IfcProductRepresentation_type);
    IFC4X1_IfcProfileProperties_type = new entity(strings[1743], false, 737, IFC4X1_IfcExtendedProperties_type);
    IFC4X1_IfcProperty_type = new entity(strings[1744], true, 747, IFC4X1_IfcPropertyAbstraction_type);
    IFC4X1_IfcPropertyDefinition_type = new entity(strings[1745], true, 750, IFC4X1_IfcRoot_type);
    IFC4X1_IfcPropertyDependencyRelationship_type = new entity(strings[1746], false, 751, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcPropertySetDefinition_type = new entity(strings[1747], true, 757, IFC4X1_IfcPropertyDefinition_type);
    IFC4X1_IfcPropertyTemplateDefinition_type = new entity(strings[1748], true, 765, IFC4X1_IfcPropertyDefinition_type);
    IFC4X1_IfcQuantitySet_type = new entity(strings[1749], true, 779, IFC4X1_IfcPropertySetDefinition_type);
    IFC4X1_IfcRectangleProfileDef_type = new entity(strings[1750], false, 798, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcRegularTimeSeries_type = new entity(strings[1751], false, 807, IFC4X1_IfcTimeSeries_type);
    IFC4X1_IfcReinforcementBarProperties_type = new entity(strings[1752], false, 808, IFC4X1_IfcPreDefinedProperties_type);
    IFC4X1_IfcRelationship_type = new entity(strings[1753], true, 836, IFC4X1_IfcRoot_type);
    IFC4X1_IfcResourceApprovalRelationship_type = new entity(strings[1754], false, 874, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcResourceConstraintRelationship_type = new entity(strings[1755], false, 875, IFC4X1_IfcResourceLevelRelationship_type);
    IFC4X1_IfcResourceTime_type = new entity(strings[1756], false, 879, IFC4X1_IfcSchedulingTime_type);
    IFC4X1_IfcRoundedRectangleProfileDef_type = new entity(strings[1757], false, 893, IFC4X1_IfcRectangleProfileDef_type);
    IFC4X1_IfcSectionProperties_type = new entity(strings[1758], false, 904, IFC4X1_IfcPreDefinedProperties_type);
    IFC4X1_IfcSectionReinforcementProperties_type = new entity(strings[1759], false, 905, IFC4X1_IfcPreDefinedProperties_type);
    IFC4X1_IfcSectionedSpine_type = new entity(strings[1760], false, 902, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcShellBasedSurfaceModel_type = new entity(strings[1761], false, 920, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcSimpleProperty_type = new entity(strings[1762], true, 921, IFC4X1_IfcProperty_type);
    IFC4X1_IfcSlippageConnectionCondition_type = new entity(strings[1763], false, 935, IFC4X1_IfcStructuralConnectionCondition_type);
    IFC4X1_IfcSolidModel_type = new entity(strings[1764], true, 940, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcStructuralLoadLinearForce_type = new entity(strings[1765], false, 995, IFC4X1_IfcStructuralLoadStatic_type);
    IFC4X1_IfcStructuralLoadPlanarForce_type = new entity(strings[1766], false, 997, IFC4X1_IfcStructuralLoadStatic_type);
    IFC4X1_IfcStructuralLoadSingleDisplacement_type = new entity(strings[1767], false, 998, IFC4X1_IfcStructuralLoadStatic_type);
    IFC4X1_IfcStructuralLoadSingleDisplacementDistortion_type = new entity(strings[1768], false, 999, IFC4X1_IfcStructuralLoadSingleDisplacement_type);
    IFC4X1_IfcStructuralLoadSingleForce_type = new entity(strings[1769], false, 1000, IFC4X1_IfcStructuralLoadStatic_type);
    IFC4X1_IfcStructuralLoadSingleForceWarping_type = new entity(strings[1770], false, 1001, IFC4X1_IfcStructuralLoadSingleForce_type);
    IFC4X1_IfcSubedge_type = new entity(strings[1771], false, 1025, IFC4X1_IfcEdge_type);
    IFC4X1_IfcSurface_type = new entity(strings[1772], true, 1026, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcSurfaceStyleRendering_type = new entity(strings[1773], false, 1040, IFC4X1_IfcSurfaceStyleShading_type);
    IFC4X1_IfcSweptAreaSolid_type = new entity(strings[1774], true, 1044, IFC4X1_IfcSolidModel_type);
    IFC4X1_IfcSweptDiskSolid_type = new entity(strings[1775], false, 1045, IFC4X1_IfcSolidModel_type);
    IFC4X1_IfcSweptDiskSolidPolygonal_type = new entity(strings[1776], false, 1046, IFC4X1_IfcSweptDiskSolid_type);
    IFC4X1_IfcSweptSurface_type = new entity(strings[1777], true, 1047, IFC4X1_IfcSurface_type);
    IFC4X1_IfcTShapeProfileDef_type = new entity(strings[1778], false, 1130, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcTessellatedItem_type = new entity(strings[1779], true, 1077, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcTextLiteral_type = new entity(strings[1780], false, 1083, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcTextLiteralWithExtent_type = new entity(strings[1781], false, 1084, IFC4X1_IfcTextLiteral_type);
    IFC4X1_IfcTextStyleFontModel_type = new entity(strings[1782], false, 1087, IFC4X1_IfcPreDefinedTextFont_type);
    IFC4X1_IfcTrapeziumProfileDef_type = new entity(strings[1783], false, 1124, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcTypeObject_type = new entity(strings[1784], false, 1134, IFC4X1_IfcObjectDefinition_type);
    IFC4X1_IfcTypeProcess_type = new entity(strings[1785], true, 1135, IFC4X1_IfcTypeObject_type);
    IFC4X1_IfcTypeProduct_type = new entity(strings[1786], false, 1136, IFC4X1_IfcTypeObject_type);
    IFC4X1_IfcTypeResource_type = new entity(strings[1787], true, 1137, IFC4X1_IfcTypeObject_type);
    IFC4X1_IfcUShapeProfileDef_type = new entity(strings[1788], false, 1148, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcVector_type = new entity(strings[1789], false, 1154, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcVertexLoop_type = new entity(strings[1790], false, 1157, IFC4X1_IfcLoop_type);
    IFC4X1_IfcWindowStyle_type = new entity(strings[1791], false, 1185, IFC4X1_IfcTypeProduct_type);
    IFC4X1_IfcZShapeProfileDef_type = new entity(strings[1792], false, 1200, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcClassificationReferenceSelect_type = new select_type(strings[1793], 155, {
        IFC4X1_IfcClassification_type,
        IFC4X1_IfcClassificationReference_type
    });
    IFC4X1_IfcClassificationSelect_type = new select_type(strings[1794], 156, {
        IFC4X1_IfcClassification_type,
        IFC4X1_IfcClassificationReference_type
    });
    IFC4X1_IfcCoordinateReferenceSystemSelect_type = new select_type(strings[1795], 227, {
        IFC4X1_IfcCoordinateReferenceSystem_type,
        IFC4X1_IfcGeometricRepresentationContext_type
    });
    IFC4X1_IfcDefinitionSelect_type = new select_type(strings[1796], 271, {
        IFC4X1_IfcObjectDefinition_type,
        IFC4X1_IfcPropertyDefinition_type
    });
    IFC4X1_IfcDocumentSelect_type = new select_type(strings[1797], 304, {
        IFC4X1_IfcDocumentInformation_type,
        IFC4X1_IfcDocumentReference_type
    });
    IFC4X1_IfcHatchLineDistanceSelect_type = new select_type(strings[1798], 481, {
        IFC4X1_IfcPositiveLengthMeasure_type,
        IFC4X1_IfcVector_type
    });
    IFC4X1_IfcMeasureValue_type = new select_type(strings[1799], 595, {
        IFC4X1_IfcAmountOfSubstanceMeasure_type,
        IFC4X1_IfcAreaMeasure_type,
        IFC4X1_IfcComplexNumber_type,
        IFC4X1_IfcContextDependentMeasure_type,
        IFC4X1_IfcCountMeasure_type,
        IFC4X1_IfcDescriptiveMeasure_type,
        IFC4X1_IfcElectricCurrentMeasure_type,
        IFC4X1_IfcLengthMeasure_type,
        IFC4X1_IfcLuminousIntensityMeasure_type,
        IFC4X1_IfcMassMeasure_type,
        IFC4X1_IfcNonNegativeLengthMeasure_type,
        IFC4X1_IfcNormalisedRatioMeasure_type,
        IFC4X1_IfcNumericMeasure_type,
        IFC4X1_IfcParameterValue_type,
        IFC4X1_IfcPlaneAngleMeasure_type,
        IFC4X1_IfcPositiveLengthMeasure_type,
        IFC4X1_IfcPositivePlaneAngleMeasure_type,
        IFC4X1_IfcPositiveRatioMeasure_type,
        IFC4X1_IfcRatioMeasure_type,
        IFC4X1_IfcSolidAngleMeasure_type,
        IFC4X1_IfcThermodynamicTemperatureMeasure_type,
        IFC4X1_IfcTimeMeasure_type,
        IFC4X1_IfcVolumeMeasure_type
    });
    IFC4X1_IfcPointOrVertexPoint_type = new select_type(strings[1800], 698, {
        IFC4X1_IfcPoint_type,
        IFC4X1_IfcVertexPoint_type
    });
    IFC4X1_IfcPresentationStyleSelect_type = new select_type(strings[1801], 724, {
        IFC4X1_IfcCurveStyle_type,
        IFC4X1_IfcFillAreaStyle_type,
        IFC4X1_IfcNullStyle_type,
        IFC4X1_IfcSurfaceStyle_type,
        IFC4X1_IfcTextStyle_type
    });
    IFC4X1_IfcProductRepresentationSelect_type = new select_type(strings[1802], 734, {
        IFC4X1_IfcProductDefinitionShape_type,
        IFC4X1_IfcRepresentationMap_type
    });
    IFC4X1_IfcPropertySetDefinitionSet_type = new type_declaration(strings[1803], 759, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPropertySetDefinition_type)));
    IFC4X1_IfcResourceObjectSelect_type = new select_type(strings[1804], 877, {
        IFC4X1_IfcActorRole_type,
        IFC4X1_IfcAppliedValue_type,
        IFC4X1_IfcApproval_type,
        IFC4X1_IfcConstraint_type,
        IFC4X1_IfcContextDependentUnit_type,
        IFC4X1_IfcConversionBasedUnit_type,
        IFC4X1_IfcExternalInformation_type,
        IFC4X1_IfcExternalReference_type,
        IFC4X1_IfcMaterialDefinition_type,
        IFC4X1_IfcOrganization_type,
        IFC4X1_IfcPerson_type,
        IFC4X1_IfcPersonAndOrganization_type,
        IFC4X1_IfcPhysicalQuantity_type,
        IFC4X1_IfcProfileDef_type,
        IFC4X1_IfcPropertyAbstraction_type,
        IFC4X1_IfcShapeAspect_type,
        IFC4X1_IfcTimeSeries_type
    });
    IFC4X1_IfcTextFontSelect_type = new select_type(strings[1805], 1082, {
        IFC4X1_IfcExternallyDefinedTextFont_type,
        IFC4X1_IfcPreDefinedTextFont_type
    });
    IFC4X1_IfcValue_type = new select_type(strings[1806], 1149, {
        IFC4X1_IfcDerivedMeasureValue_type,
        IFC4X1_IfcMeasureValue_type,
        IFC4X1_IfcSimpleValue_type
    });
    IFC4X1_IfcAdvancedFace_type = new entity(strings[1807], false, 16, IFC4X1_IfcFaceSurface_type);
    IFC4X1_IfcAlignment2DHorizontal_type = new entity(strings[1808], false, 30, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcAlignment2DSegment_type = new entity(strings[1809], true, 32, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcAlignment2DVertical_type = new entity(strings[1810], false, 36, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcAlignment2DVerticalSegment_type = new entity(strings[1811], true, 37, IFC4X1_IfcAlignment2DSegment_type);
    IFC4X1_IfcAnnotationFillArea_type = new entity(strings[1812], false, 45, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcAsymmetricIShapeProfileDef_type = new entity(strings[1813], false, 60, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcAxis1Placement_type = new entity(strings[1814], false, 64, IFC4X1_IfcPlacement_type);
    IFC4X1_IfcAxis2Placement2D_type = new entity(strings[1815], false, 66, IFC4X1_IfcPlacement_type);
    IFC4X1_IfcAxis2Placement3D_type = new entity(strings[1816], false, 67, IFC4X1_IfcPlacement_type);
    IFC4X1_IfcBooleanResult_type = new entity(strings[1817], false, 84, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcBoundedSurface_type = new entity(strings[1818], true, 92, IFC4X1_IfcSurface_type);
    IFC4X1_IfcBoundingBox_type = new entity(strings[1819], false, 93, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcBoxedHalfSpace_type = new entity(strings[1820], false, 95, IFC4X1_IfcHalfSpaceSolid_type);
    IFC4X1_IfcCShapeProfileDef_type = new entity(strings[1821], false, 243, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcCartesianPoint_type = new entity(strings[1822], false, 130, IFC4X1_IfcPoint_type);
    IFC4X1_IfcCartesianPointList_type = new entity(strings[1823], true, 131, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcCartesianPointList2D_type = new entity(strings[1824], false, 132, IFC4X1_IfcCartesianPointList_type);
    IFC4X1_IfcCartesianPointList3D_type = new entity(strings[1825], false, 133, IFC4X1_IfcCartesianPointList_type);
    IFC4X1_IfcCartesianTransformationOperator_type = new entity(strings[1826], true, 134, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcCartesianTransformationOperator2D_type = new entity(strings[1827], false, 135, IFC4X1_IfcCartesianTransformationOperator_type);
    IFC4X1_IfcCartesianTransformationOperator2DnonUniform_type = new entity(strings[1828], false, 136, IFC4X1_IfcCartesianTransformationOperator2D_type);
    IFC4X1_IfcCartesianTransformationOperator3D_type = new entity(strings[1829], false, 137, IFC4X1_IfcCartesianTransformationOperator_type);
    IFC4X1_IfcCartesianTransformationOperator3DnonUniform_type = new entity(strings[1830], false, 138, IFC4X1_IfcCartesianTransformationOperator3D_type);
    IFC4X1_IfcCircleProfileDef_type = new entity(strings[1831], false, 149, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcClosedShell_type = new entity(strings[1832], false, 157, IFC4X1_IfcConnectedFaceSet_type);
    IFC4X1_IfcColourRgb_type = new entity(strings[1833], false, 163, IFC4X1_IfcColourSpecification_type);
    IFC4X1_IfcComplexProperty_type = new entity(strings[1834], false, 174, IFC4X1_IfcProperty_type);
    IFC4X1_IfcCompositeCurveSegment_type = new entity(strings[1835], false, 179, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcConstructionResourceType_type = new entity(strings[1836], true, 209, IFC4X1_IfcTypeResource_type);
    IFC4X1_IfcContext_type = new entity(strings[1837], true, 210, IFC4X1_IfcObjectDefinition_type);
    IFC4X1_IfcCrewResourceType_type = new entity(strings[1838], false, 238, IFC4X1_IfcConstructionResourceType_type);
    IFC4X1_IfcCsgPrimitive3D_type = new entity(strings[1839], true, 240, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcCsgSolid_type = new entity(strings[1840], false, 242, IFC4X1_IfcSolidModel_type);
    IFC4X1_IfcCurve_type = new entity(strings[1841], true, 249, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcCurveBoundedPlane_type = new entity(strings[1842], false, 250, IFC4X1_IfcBoundedSurface_type);
    IFC4X1_IfcCurveBoundedSurface_type = new entity(strings[1843], false, 251, IFC4X1_IfcBoundedSurface_type);
    IFC4X1_IfcDirection_type = new entity(strings[1844], false, 280, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcDistanceExpression_type = new entity(strings[1845], false, 285, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcDoorStyle_type = new entity(strings[1846], false, 312, IFC4X1_IfcTypeProduct_type);
    IFC4X1_IfcEdgeLoop_type = new entity(strings[1847], false, 334, IFC4X1_IfcLoop_type);
    IFC4X1_IfcElementQuantity_type = new entity(strings[1848], false, 367, IFC4X1_IfcQuantitySet_type);
    IFC4X1_IfcElementType_type = new entity(strings[1849], true, 368, IFC4X1_IfcTypeProduct_type);
    IFC4X1_IfcElementarySurface_type = new entity(strings[1850], true, 360, IFC4X1_IfcSurface_type);
    IFC4X1_IfcEllipseProfileDef_type = new entity(strings[1851], false, 370, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcEventType_type = new entity(strings[1852], false, 386, IFC4X1_IfcTypeProcess_type);
    IFC4X1_IfcExtrudedAreaSolid_type = new entity(strings[1853], false, 398, IFC4X1_IfcSweptAreaSolid_type);
    IFC4X1_IfcExtrudedAreaSolidTapered_type = new entity(strings[1854], false, 399, IFC4X1_IfcExtrudedAreaSolid_type);
    IFC4X1_IfcFaceBasedSurfaceModel_type = new entity(strings[1855], false, 401, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcFillAreaStyleHatching_type = new entity(strings[1856], false, 418, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcFillAreaStyleTiles_type = new entity(strings[1857], false, 419, IFC4X1_IfcGeometricRepresentationItem_type);
    IFC4X1_IfcFixedReferenceSweptAreaSolid_type = new entity(strings[1858], false, 427, IFC4X1_IfcSweptAreaSolid_type);
    IFC4X1_IfcFurnishingElementType_type = new entity(strings[1859], false, 458, IFC4X1_IfcElementType_type);
    IFC4X1_IfcFurnitureType_type = new entity(strings[1860], false, 460, IFC4X1_IfcFurnishingElementType_type);
    IFC4X1_IfcGeographicElementType_type = new entity(strings[1861], false, 463, IFC4X1_IfcElementType_type);
    IFC4X1_IfcGeometricCurveSet_type = new entity(strings[1862], false, 465, IFC4X1_IfcGeometricSet_type);
    IFC4X1_IfcIShapeProfileDef_type = new entity(strings[1863], false, 512, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcIndexedPolygonalFace_type = new entity(strings[1864], false, 495, IFC4X1_IfcTessellatedItem_type);
    IFC4X1_IfcIndexedPolygonalFaceWithVoids_type = new entity(strings[1865], false, 496, IFC4X1_IfcIndexedPolygonalFace_type);
    IFC4X1_IfcLShapeProfileDef_type = new entity(strings[1866], false, 562, IFC4X1_IfcParameterizedProfileDef_type);
    IFC4X1_IfcLaborResourceType_type = new entity(strings[1867], false, 521, IFC4X1_IfcConstructionResourceType_type);
    IFC4X1_IfcLine_type = new entity(strings[1868], false, 548, IFC4X1_IfcCurve_type);
    IFC4X1_IfcManifoldSolidBrep_type = new entity(strings[1869], true, 568, IFC4X1_IfcSolidModel_type);
    IFC4X1_IfcObject_type = new entity(strings[1870], true, 631, IFC4X1_IfcObjectDefinition_type);
    IFC4X1_IfcOffsetCurve_type = new entity(strings[1871], true, 640, IFC4X1_IfcCurve_type);
    IFC4X1_IfcOffsetCurve2D_type = new entity(strings[1872], false, 641, IFC4X1_IfcOffsetCurve_type);
    IFC4X1_IfcOffsetCurve3D_type = new entity(strings[1873], false, 642, IFC4X1_IfcOffsetCurve_type);
    IFC4X1_IfcOffsetCurveByDistances_type = new entity(strings[1874], false, 643, IFC4X1_IfcOffsetCurve_type);
    IFC4X1_IfcPcurve_type = new entity(strings[1875], false, 660, IFC4X1_IfcCurve_type);
    IFC4X1_IfcPlanarBox_type = new entity(strings[1876], false, 686, IFC4X1_IfcPlanarExtent_type);
    IFC4X1_IfcPlane_type = new entity(strings[1877], false, 689, IFC4X1_IfcElementarySurface_type);
    IFC4X1_IfcPreDefinedColour_type = new entity(strings[1878], true, 711, IFC4X1_IfcPreDefinedItem_type);
    IFC4X1_IfcPreDefinedCurveFont_type = new entity(strings[1879], true, 712, IFC4X1_IfcPreDefinedItem_type);
    IFC4X1_IfcPreDefinedPropertySet_type = new entity(strings[1880], true, 715, IFC4X1_IfcPropertySetDefinition_type);
    IFC4X1_IfcProcedureType_type = new entity(strings[1881], false, 727, IFC4X1_IfcTypeProcess_type);
    IFC4X1_IfcProcess_type = new entity(strings[1882], true, 729, IFC4X1_IfcObject_type);
    IFC4X1_IfcProduct_type = new entity(strings[1883], true, 731, IFC4X1_IfcObject_type);
    IFC4X1_IfcProject_type = new entity(strings[1884], false, 739, IFC4X1_IfcContext_type);
    IFC4X1_IfcProjectLibrary_type = new entity(strings[1885], false, 744, IFC4X1_IfcContext_type);
    IFC4X1_IfcPropertyBoundedValue_type = new entity(strings[1886], false, 749, IFC4X1_IfcSimpleProperty_type);
    IFC4X1_IfcPropertyEnumeratedValue_type = new entity(strings[1887], false, 752, IFC4X1_IfcSimpleProperty_type);
    IFC4X1_IfcPropertyListValue_type = new entity(strings[1888], false, 754, IFC4X1_IfcSimpleProperty_type);
    IFC4X1_IfcPropertyReferenceValue_type = new entity(strings[1889], false, 755, IFC4X1_IfcSimpleProperty_type);
    IFC4X1_IfcPropertySet_type = new entity(strings[1890], false, 756, IFC4X1_IfcPropertySetDefinition_type);
    IFC4X1_IfcPropertySetTemplate_type = new entity(strings[1891], false, 760, IFC4X1_IfcPropertyTemplateDefinition_type);
    IFC4X1_IfcPropertySingleValue_type = new entity(strings[1892], false, 762, IFC4X1_IfcSimpleProperty_type);
    IFC4X1_IfcPropertyTableValue_type = new entity(strings[1893], false, 763, IFC4X1_IfcSimpleProperty_type);
    IFC4X1_IfcPropertyTemplate_type = new entity(strings[1894], true, 764, IFC4X1_IfcPropertyTemplateDefinition_type);
    IFC4X1_IfcProxy_type = new entity(strings[1895], false, 772, IFC4X1_IfcProduct_type);
    IFC4X1_IfcRectangleHollowProfileDef_type = new entity(strings[1896], false, 797, IFC4X1_IfcRectangleProfileDef_type);
    IFC4X1_IfcRectangularPyramid_type = new entity(strings[1897], false, 799, IFC4X1_IfcCsgPrimitive3D_type);
    IFC4X1_IfcRectangularTrimmedSurface_type = new entity(strings[1898], false, 800, IFC4X1_IfcBoundedSurface_type);
    IFC4X1_IfcReinforcementDefinitionProperties_type = new entity(strings[1899], false, 809, IFC4X1_IfcPreDefinedPropertySet_type);
    IFC4X1_IfcRelAssigns_type = new entity(strings[1900], true, 821, IFC4X1_IfcRelationship_type);
    IFC4X1_IfcRelAssignsToActor_type = new entity(strings[1901], false, 822, IFC4X1_IfcRelAssigns_type);
    IFC4X1_IfcRelAssignsToControl_type = new entity(strings[1902], false, 823, IFC4X1_IfcRelAssigns_type);
    IFC4X1_IfcRelAssignsToGroup_type = new entity(strings[1903], false, 824, IFC4X1_IfcRelAssigns_type);
    IFC4X1_IfcRelAssignsToGroupByFactor_type = new entity(strings[1904], false, 825, IFC4X1_IfcRelAssignsToGroup_type);
    IFC4X1_IfcRelAssignsToProcess_type = new entity(strings[1905], false, 826, IFC4X1_IfcRelAssigns_type);
    IFC4X1_IfcRelAssignsToProduct_type = new entity(strings[1906], false, 827, IFC4X1_IfcRelAssigns_type);
    IFC4X1_IfcRelAssignsToResource_type = new entity(strings[1907], false, 828, IFC4X1_IfcRelAssigns_type);
    IFC4X1_IfcRelAssociates_type = new entity(strings[1908], true, 829, IFC4X1_IfcRelationship_type);
    IFC4X1_IfcRelAssociatesApproval_type = new entity(strings[1909], false, 830, IFC4X1_IfcRelAssociates_type);
    IFC4X1_IfcRelAssociatesClassification_type = new entity(strings[1910], false, 831, IFC4X1_IfcRelAssociates_type);
    IFC4X1_IfcRelAssociatesConstraint_type = new entity(strings[1911], false, 832, IFC4X1_IfcRelAssociates_type);
    IFC4X1_IfcRelAssociatesDocument_type = new entity(strings[1912], false, 833, IFC4X1_IfcRelAssociates_type);
    IFC4X1_IfcRelAssociatesLibrary_type = new entity(strings[1913], false, 834, IFC4X1_IfcRelAssociates_type);
    IFC4X1_IfcRelAssociatesMaterial_type = new entity(strings[1914], false, 835, IFC4X1_IfcRelAssociates_type);
    IFC4X1_IfcRelConnects_type = new entity(strings[1915], true, 837, IFC4X1_IfcRelationship_type);
    IFC4X1_IfcRelConnectsElements_type = new entity(strings[1916], false, 838, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelConnectsPathElements_type = new entity(strings[1917], false, 839, IFC4X1_IfcRelConnectsElements_type);
    IFC4X1_IfcRelConnectsPortToElement_type = new entity(strings[1918], false, 841, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelConnectsPorts_type = new entity(strings[1919], false, 840, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelConnectsStructuralActivity_type = new entity(strings[1920], false, 842, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelConnectsStructuralMember_type = new entity(strings[1921], false, 843, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelConnectsWithEccentricity_type = new entity(strings[1922], false, 844, IFC4X1_IfcRelConnectsStructuralMember_type);
    IFC4X1_IfcRelConnectsWithRealizingElements_type = new entity(strings[1923], false, 845, IFC4X1_IfcRelConnectsElements_type);
    IFC4X1_IfcRelContainedInSpatialStructure_type = new entity(strings[1924], false, 846, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelCoversBldgElements_type = new entity(strings[1925], false, 847, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelCoversSpaces_type = new entity(strings[1926], false, 848, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelDeclares_type = new entity(strings[1927], false, 849, IFC4X1_IfcRelationship_type);
    IFC4X1_IfcRelDecomposes_type = new entity(strings[1928], true, 850, IFC4X1_IfcRelationship_type);
    IFC4X1_IfcRelDefines_type = new entity(strings[1929], true, 851, IFC4X1_IfcRelationship_type);
    IFC4X1_IfcRelDefinesByObject_type = new entity(strings[1930], false, 852, IFC4X1_IfcRelDefines_type);
    IFC4X1_IfcRelDefinesByProperties_type = new entity(strings[1931], false, 853, IFC4X1_IfcRelDefines_type);
    IFC4X1_IfcRelDefinesByTemplate_type = new entity(strings[1932], false, 854, IFC4X1_IfcRelDefines_type);
    IFC4X1_IfcRelDefinesByType_type = new entity(strings[1933], false, 855, IFC4X1_IfcRelDefines_type);
    IFC4X1_IfcRelFillsElement_type = new entity(strings[1934], false, 856, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelFlowControlElements_type = new entity(strings[1935], false, 857, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelInterferesElements_type = new entity(strings[1936], false, 858, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelNests_type = new entity(strings[1937], false, 859, IFC4X1_IfcRelDecomposes_type);
    IFC4X1_IfcRelProjectsElement_type = new entity(strings[1938], false, 860, IFC4X1_IfcRelDecomposes_type);
    IFC4X1_IfcRelReferencedInSpatialStructure_type = new entity(strings[1939], false, 861, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelSequence_type = new entity(strings[1940], false, 862, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelServicesBuildings_type = new entity(strings[1941], false, 863, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelSpaceBoundary_type = new entity(strings[1942], false, 864, IFC4X1_IfcRelConnects_type);
    IFC4X1_IfcRelSpaceBoundary1stLevel_type = new entity(strings[1943], false, 865, IFC4X1_IfcRelSpaceBoundary_type);
    IFC4X1_IfcRelSpaceBoundary2ndLevel_type = new entity(strings[1944], false, 866, IFC4X1_IfcRelSpaceBoundary1stLevel_type);
    IFC4X1_IfcRelVoidsElement_type = new entity(strings[1945], false, 867, IFC4X1_IfcRelDecomposes_type);
    IFC4X1_IfcReparametrisedCompositeCurveSegment_type = new entity(strings[1946], false, 868, IFC4X1_IfcCompositeCurveSegment_type);
    IFC4X1_IfcResource_type = new entity(strings[1947], true, 873, IFC4X1_IfcObject_type);
    IFC4X1_IfcRevolvedAreaSolid_type = new entity(strings[1948], false, 880, IFC4X1_IfcSweptAreaSolid_type);
    IFC4X1_IfcRevolvedAreaSolidTapered_type = new entity(strings[1949], false, 881, IFC4X1_IfcRevolvedAreaSolid_type);
    IFC4X1_IfcRightCircularCone_type = new entity(strings[1950], false, 882, IFC4X1_IfcCsgPrimitive3D_type);
    IFC4X1_IfcRightCircularCylinder_type = new entity(strings[1951], false, 883, IFC4X1_IfcCsgPrimitive3D_type);
    IFC4X1_IfcSectionedSolid_type = new entity(strings[1952], true, 900, IFC4X1_IfcSolidModel_type);
    IFC4X1_IfcSectionedSolidHorizontal_type = new entity(strings[1953], false, 901, IFC4X1_IfcSectionedSolid_type);
    IFC4X1_IfcSimplePropertyTemplate_type = new entity(strings[1954], false, 922, IFC4X1_IfcPropertyTemplate_type);
    IFC4X1_IfcSpatialElement_type = new entity(strings[1955], true, 953, IFC4X1_IfcProduct_type);
    IFC4X1_IfcSpatialElementType_type = new entity(strings[1956], true, 954, IFC4X1_IfcTypeProduct_type);
    IFC4X1_IfcSpatialStructureElement_type = new entity(strings[1957], true, 955, IFC4X1_IfcSpatialElement_type);
    IFC4X1_IfcSpatialStructureElementType_type = new entity(strings[1958], true, 956, IFC4X1_IfcSpatialElementType_type);
    IFC4X1_IfcSpatialZone_type = new entity(strings[1959], false, 957, IFC4X1_IfcSpatialElement_type);
    IFC4X1_IfcSpatialZoneType_type = new entity(strings[1960], false, 958, IFC4X1_IfcSpatialElementType_type);
    IFC4X1_IfcSphere_type = new entity(strings[1961], false, 964, IFC4X1_IfcCsgPrimitive3D_type);
    IFC4X1_IfcSphericalSurface_type = new entity(strings[1962], false, 965, IFC4X1_IfcElementarySurface_type);
    IFC4X1_IfcStructuralActivity_type = new entity(strings[1963], true, 977, IFC4X1_IfcProduct_type);
    IFC4X1_IfcStructuralItem_type = new entity(strings[1964], true, 989, IFC4X1_IfcProduct_type);
    IFC4X1_IfcStructuralMember_type = new entity(strings[1965], true, 1004, IFC4X1_IfcStructuralItem_type);
    IFC4X1_IfcStructuralReaction_type = new entity(strings[1966], true, 1009, IFC4X1_IfcStructuralActivity_type);
    IFC4X1_IfcStructuralSurfaceMember_type = new entity(strings[1967], false, 1014, IFC4X1_IfcStructuralMember_type);
    IFC4X1_IfcStructuralSurfaceMemberVarying_type = new entity(strings[1968], false, 1016, IFC4X1_IfcStructuralSurfaceMember_type);
    IFC4X1_IfcStructuralSurfaceReaction_type = new entity(strings[1969], false, 1017, IFC4X1_IfcStructuralReaction_type);
    IFC4X1_IfcSubContractResourceType_type = new entity(strings[1970], false, 1023, IFC4X1_IfcConstructionResourceType_type);
    IFC4X1_IfcSurfaceCurve_type = new entity(strings[1971], false, 1027, IFC4X1_IfcCurve_type);
    IFC4X1_IfcSurfaceCurveSweptAreaSolid_type = new entity(strings[1972], false, 1028, IFC4X1_IfcSweptAreaSolid_type);
    IFC4X1_IfcSurfaceOfLinearExtrusion_type = new entity(strings[1973], false, 1031, IFC4X1_IfcSweptSurface_type);
    IFC4X1_IfcSurfaceOfRevolution_type = new entity(strings[1974], false, 1032, IFC4X1_IfcSweptSurface_type);
    IFC4X1_IfcSystemFurnitureElementType_type = new entity(strings[1975], false, 1053, IFC4X1_IfcFurnishingElementType_type);
    IFC4X1_IfcTask_type = new entity(strings[1976], false, 1061, IFC4X1_IfcProcess_type);
    IFC4X1_IfcTaskType_type = new entity(strings[1977], false, 1065, IFC4X1_IfcTypeProcess_type);
    IFC4X1_IfcTessellatedFaceSet_type = new entity(strings[1978], true, 1076, IFC4X1_IfcTessellatedItem_type);
    IFC4X1_IfcToroidalSurface_type = new entity(strings[1979], false, 1112, IFC4X1_IfcElementarySurface_type);
    IFC4X1_IfcTransportElementType_type = new entity(strings[1980], false, 1122, IFC4X1_IfcElementType_type);
    IFC4X1_IfcTriangulatedFaceSet_type = new entity(strings[1981], false, 1125, IFC4X1_IfcTessellatedFaceSet_type);
    IFC4X1_IfcTriangulatedIrregularNetwork_type = new entity(strings[1982], false, 1126, IFC4X1_IfcTriangulatedFaceSet_type);
    IFC4X1_IfcWindowLiningProperties_type = new entity(strings[1983], false, 1180, IFC4X1_IfcPreDefinedPropertySet_type);
    IFC4X1_IfcWindowPanelProperties_type = new entity(strings[1984], false, 1183, IFC4X1_IfcPreDefinedPropertySet_type);
    IFC4X1_IfcAppliedValueSelect_type = new select_type(strings[1985], 48, {
        IFC4X1_IfcMeasureWithUnit_type,
        IFC4X1_IfcReference_type,
        IFC4X1_IfcValue_type
    });
    IFC4X1_IfcAxis2Placement_type = new select_type(strings[1986], 65, {
        IFC4X1_IfcAxis2Placement2D_type,
        IFC4X1_IfcAxis2Placement3D_type
    });
    IFC4X1_IfcBooleanOperand_type = new select_type(strings[1987], 82, {
        IFC4X1_IfcBooleanResult_type,
        IFC4X1_IfcCsgPrimitive3D_type,
        IFC4X1_IfcHalfSpaceSolid_type,
        IFC4X1_IfcSolidModel_type,
        IFC4X1_IfcTessellatedFaceSet_type
    });
    IFC4X1_IfcColour_type = new select_type(strings[1988], 161, {
        IFC4X1_IfcColourSpecification_type,
        IFC4X1_IfcPreDefinedColour_type
    });
    IFC4X1_IfcColourOrFactor_type = new select_type(strings[1989], 162, {
        IFC4X1_IfcColourRgb_type,
        IFC4X1_IfcNormalisedRatioMeasure_type
    });
    IFC4X1_IfcCsgSelect_type = new select_type(strings[1990], 241, {
        IFC4X1_IfcBooleanResult_type,
        IFC4X1_IfcCsgPrimitive3D_type
    });
    IFC4X1_IfcCurveStyleFontSelect_type = new select_type(strings[1991], 261, {
        IFC4X1_IfcCurveStyleFont_type,
        IFC4X1_IfcPreDefinedCurveFont_type
    });
    IFC4X1_IfcFillStyleSelect_type = new select_type(strings[1992], 420, {
        IFC4X1_IfcColour_type,
        IFC4X1_IfcExternallyDefinedHatchStyle_type,
        IFC4X1_IfcFillAreaStyleHatching_type,
        IFC4X1_IfcFillAreaStyleTiles_type
    });
    IFC4X1_IfcGeometricSetSelect_type = new select_type(strings[1993], 471, {
        IFC4X1_IfcCurve_type,
        IFC4X1_IfcPoint_type,
        IFC4X1_IfcSurface_type
    });
    IFC4X1_IfcGridPlacementDirectionSelect_type = new select_type(strings[1994], 477, {
        IFC4X1_IfcDirection_type,
        IFC4X1_IfcVirtualGridIntersection_type
    });
    IFC4X1_IfcMetricValueSelect_type = new select_type(strings[1995], 608, {
        IFC4X1_IfcAppliedValue_type,
        IFC4X1_IfcMeasureWithUnit_type,
        IFC4X1_IfcReference_type,
        IFC4X1_IfcTable_type,
        IFC4X1_IfcTimeSeries_type,
        IFC4X1_IfcValue_type
    });
    IFC4X1_IfcProcessSelect_type = new select_type(strings[1996], 730, {
        IFC4X1_IfcProcess_type,
        IFC4X1_IfcTypeProcess_type
    });
    IFC4X1_IfcProductSelect_type = new select_type(strings[1997], 735, {
        IFC4X1_IfcProduct_type,
        IFC4X1_IfcTypeProduct_type
    });
    IFC4X1_IfcPropertySetDefinitionSelect_type = new select_type(strings[1998], 758, {
        IFC4X1_IfcPropertySetDefinition_type,
        IFC4X1_IfcPropertySetDefinitionSet_type
    });
    IFC4X1_IfcResourceSelect_type = new select_type(strings[1999], 878, {
        IFC4X1_IfcResource_type,
        IFC4X1_IfcTypeResource_type
    });
    IFC4X1_IfcShell_type = new select_type(strings[2000], 919, {
        IFC4X1_IfcClosedShell_type,
        IFC4X1_IfcOpenShell_type
    });
    IFC4X1_IfcSolidOrShell_type = new select_type(strings[2001], 941, {
        IFC4X1_IfcClosedShell_type,
        IFC4X1_IfcSolidModel_type
    });
    IFC4X1_IfcSurfaceOrFaceSurface_type = new select_type(strings[2002], 1033, {
        IFC4X1_IfcFaceBasedSurfaceModel_type,
        IFC4X1_IfcFaceSurface_type,
        IFC4X1_IfcSurface_type
    });
    IFC4X1_IfcTrimmingSelect_type = new select_type(strings[2003], 1129, {
        IFC4X1_IfcCartesianPoint_type,
        IFC4X1_IfcParameterValue_type
    });
    IFC4X1_IfcVectorOrDirection_type = new select_type(strings[2004], 1155, {
        IFC4X1_IfcDirection_type,
        IFC4X1_IfcVector_type
    });
    IFC4X1_IfcActor_type = new entity(strings[2005], false, 6, IFC4X1_IfcObject_type);
    IFC4X1_IfcAdvancedBrep_type = new entity(strings[2006], false, 14, IFC4X1_IfcManifoldSolidBrep_type);
    IFC4X1_IfcAdvancedBrepWithVoids_type = new entity(strings[2007], false, 15, IFC4X1_IfcAdvancedBrep_type);
    IFC4X1_IfcAlignment2DHorizontalSegment_type = new entity(strings[2008], false, 31, IFC4X1_IfcAlignment2DSegment_type);
    IFC4X1_IfcAlignment2DVerSegCircularArc_type = new entity(strings[2009], false, 33, IFC4X1_IfcAlignment2DVerticalSegment_type);
    IFC4X1_IfcAlignment2DVerSegLine_type = new entity(strings[2010], false, 34, IFC4X1_IfcAlignment2DVerticalSegment_type);
    IFC4X1_IfcAlignment2DVerSegParabolicArc_type = new entity(strings[2011], false, 35, IFC4X1_IfcAlignment2DVerticalSegment_type);
    IFC4X1_IfcAnnotation_type = new entity(strings[2012], false, 44, IFC4X1_IfcProduct_type);
    IFC4X1_IfcBSplineSurface_type = new entity(strings[2013], true, 99, IFC4X1_IfcBoundedSurface_type);
    IFC4X1_IfcBSplineSurfaceWithKnots_type = new entity(strings[2014], false, 101, IFC4X1_IfcBSplineSurface_type);
    IFC4X1_IfcBlock_type = new entity(strings[2015], false, 76, IFC4X1_IfcCsgPrimitive3D_type);
    IFC4X1_IfcBooleanClippingResult_type = new entity(strings[2016], false, 81, IFC4X1_IfcBooleanResult_type);
    IFC4X1_IfcBoundedCurve_type = new entity(strings[2017], true, 91, IFC4X1_IfcCurve_type);
    IFC4X1_IfcBuilding_type = new entity(strings[2018], false, 102, IFC4X1_IfcSpatialStructureElement_type);
    IFC4X1_IfcBuildingElementType_type = new entity(strings[2019], true, 110, IFC4X1_IfcElementType_type);
    IFC4X1_IfcBuildingStorey_type = new entity(strings[2020], false, 111, IFC4X1_IfcSpatialStructureElement_type);
    IFC4X1_IfcChimneyType_type = new entity(strings[2021], false, 145, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcCircleHollowProfileDef_type = new entity(strings[2022], false, 148, IFC4X1_IfcCircleProfileDef_type);
    IFC4X1_IfcCivilElementType_type = new entity(strings[2023], false, 152, IFC4X1_IfcElementType_type);
    IFC4X1_IfcColumnType_type = new entity(strings[2024], false, 168, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcComplexPropertyTemplate_type = new entity(strings[2025], false, 175, IFC4X1_IfcPropertyTemplate_type);
    IFC4X1_IfcCompositeCurve_type = new entity(strings[2026], false, 177, IFC4X1_IfcBoundedCurve_type);
    IFC4X1_IfcCompositeCurveOnSurface_type = new entity(strings[2027], false, 178, IFC4X1_IfcCompositeCurve_type);
    IFC4X1_IfcConic_type = new entity(strings[2028], true, 188, IFC4X1_IfcCurve_type);
    IFC4X1_IfcConstructionEquipmentResourceType_type = new entity(strings[2029], false, 200, IFC4X1_IfcConstructionResourceType_type);
    IFC4X1_IfcConstructionMaterialResourceType_type = new entity(strings[2030], false, 203, IFC4X1_IfcConstructionResourceType_type);
    IFC4X1_IfcConstructionProductResourceType_type = new entity(strings[2031], false, 206, IFC4X1_IfcConstructionResourceType_type);
    IFC4X1_IfcConstructionResource_type = new entity(strings[2032], true, 208, IFC4X1_IfcResource_type);
    IFC4X1_IfcControl_type = new entity(strings[2033], true, 213, IFC4X1_IfcObject_type);
    IFC4X1_IfcCostItem_type = new entity(strings[2034], false, 228, IFC4X1_IfcControl_type);
    IFC4X1_IfcCostSchedule_type = new entity(strings[2035], false, 230, IFC4X1_IfcControl_type);
    IFC4X1_IfcCoveringType_type = new entity(strings[2036], false, 235, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcCrewResource_type = new entity(strings[2037], false, 237, IFC4X1_IfcConstructionResource_type);
    IFC4X1_IfcCurtainWallType_type = new entity(strings[2038], false, 246, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcCurveSegment2D_type = new entity(strings[2039], true, 256, IFC4X1_IfcBoundedCurve_type);
    IFC4X1_IfcCylindricalSurface_type = new entity(strings[2040], false, 262, IFC4X1_IfcElementarySurface_type);
    IFC4X1_IfcDistributionElementType_type = new entity(strings[2041], false, 293, IFC4X1_IfcElementType_type);
    IFC4X1_IfcDistributionFlowElementType_type = new entity(strings[2042], true, 295, IFC4X1_IfcDistributionElementType_type);
    IFC4X1_IfcDoorLiningProperties_type = new entity(strings[2043], false, 307, IFC4X1_IfcPreDefinedPropertySet_type);
    IFC4X1_IfcDoorPanelProperties_type = new entity(strings[2044], false, 310, IFC4X1_IfcPreDefinedPropertySet_type);
    IFC4X1_IfcDoorType_type = new entity(strings[2045], false, 315, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcDraughtingPreDefinedColour_type = new entity(strings[2046], false, 319, IFC4X1_IfcPreDefinedColour_type);
    IFC4X1_IfcDraughtingPreDefinedCurveFont_type = new entity(strings[2047], false, 320, IFC4X1_IfcPreDefinedCurveFont_type);
    IFC4X1_IfcElement_type = new entity(strings[2048], true, 359, IFC4X1_IfcProduct_type);
    IFC4X1_IfcElementAssembly_type = new entity(strings[2049], false, 361, IFC4X1_IfcElement_type);
    IFC4X1_IfcElementAssemblyType_type = new entity(strings[2050], false, 362, IFC4X1_IfcElementType_type);
    IFC4X1_IfcElementComponent_type = new entity(strings[2051], true, 364, IFC4X1_IfcElement_type);
    IFC4X1_IfcElementComponentType_type = new entity(strings[2052], true, 365, IFC4X1_IfcElementType_type);
    IFC4X1_IfcEllipse_type = new entity(strings[2053], false, 369, IFC4X1_IfcConic_type);
    IFC4X1_IfcEnergyConversionDeviceType_type = new entity(strings[2054], true, 372, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcEngineType_type = new entity(strings[2055], false, 375, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcEvaporativeCoolerType_type = new entity(strings[2056], false, 378, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcEvaporatorType_type = new entity(strings[2057], false, 381, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcEvent_type = new entity(strings[2058], false, 383, IFC4X1_IfcProcess_type);
    IFC4X1_IfcExternalSpatialStructureElement_type = new entity(strings[2059], true, 397, IFC4X1_IfcSpatialElement_type);
    IFC4X1_IfcFacetedBrep_type = new entity(strings[2060], false, 405, IFC4X1_IfcManifoldSolidBrep_type);
    IFC4X1_IfcFacetedBrepWithVoids_type = new entity(strings[2061], false, 406, IFC4X1_IfcFacetedBrep_type);
    IFC4X1_IfcFastener_type = new entity(strings[2062], false, 411, IFC4X1_IfcElementComponent_type);
    IFC4X1_IfcFastenerType_type = new entity(strings[2063], false, 412, IFC4X1_IfcElementComponentType_type);
    IFC4X1_IfcFeatureElement_type = new entity(strings[2064], true, 414, IFC4X1_IfcElement_type);
    IFC4X1_IfcFeatureElementAddition_type = new entity(strings[2065], true, 415, IFC4X1_IfcFeatureElement_type);
    IFC4X1_IfcFeatureElementSubtraction_type = new entity(strings[2066], true, 416, IFC4X1_IfcFeatureElement_type);
    IFC4X1_IfcFlowControllerType_type = new entity(strings[2067], true, 429, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcFlowFittingType_type = new entity(strings[2068], true, 432, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcFlowMeterType_type = new entity(strings[2069], false, 437, IFC4X1_IfcFlowControllerType_type);
    IFC4X1_IfcFlowMovingDeviceType_type = new entity(strings[2070], true, 440, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcFlowSegmentType_type = new entity(strings[2071], true, 442, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcFlowStorageDeviceType_type = new entity(strings[2072], true, 444, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcFlowTerminalType_type = new entity(strings[2073], true, 446, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcFlowTreatmentDeviceType_type = new entity(strings[2074], true, 448, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcFootingType_type = new entity(strings[2075], false, 453, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcFurnishingElement_type = new entity(strings[2076], false, 457, IFC4X1_IfcElement_type);
    IFC4X1_IfcFurniture_type = new entity(strings[2077], false, 459, IFC4X1_IfcFurnishingElement_type);
    IFC4X1_IfcGeographicElement_type = new entity(strings[2078], false, 462, IFC4X1_IfcElement_type);
    IFC4X1_IfcGroup_type = new entity(strings[2079], false, 479, IFC4X1_IfcObject_type);
    IFC4X1_IfcHeatExchangerType_type = new entity(strings[2080], false, 483, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcHumidifierType_type = new entity(strings[2081], false, 488, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcIndexedPolyCurve_type = new entity(strings[2082], false, 494, IFC4X1_IfcBoundedCurve_type);
    IFC4X1_IfcInterceptorType_type = new entity(strings[2083], false, 503, IFC4X1_IfcFlowTreatmentDeviceType_type);
    IFC4X1_IfcIntersectionCurve_type = new entity(strings[2084], false, 506, IFC4X1_IfcSurfaceCurve_type);
    IFC4X1_IfcInventory_type = new entity(strings[2085], false, 507, IFC4X1_IfcGroup_type);
    IFC4X1_IfcJunctionBoxType_type = new entity(strings[2086], false, 515, IFC4X1_IfcFlowFittingType_type);
    IFC4X1_IfcLaborResource_type = new entity(strings[2087], false, 520, IFC4X1_IfcConstructionResource_type);
    IFC4X1_IfcLampType_type = new entity(strings[2088], false, 525, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcLightFixtureType_type = new entity(strings[2089], false, 539, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcLineSegment2D_type = new entity(strings[2090], false, 556, IFC4X1_IfcCurveSegment2D_type);
    IFC4X1_IfcMechanicalFastener_type = new entity(strings[2091], false, 597, IFC4X1_IfcElementComponent_type);
    IFC4X1_IfcMechanicalFastenerType_type = new entity(strings[2092], false, 598, IFC4X1_IfcElementComponentType_type);
    IFC4X1_IfcMedicalDeviceType_type = new entity(strings[2093], false, 601, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcMemberType_type = new entity(strings[2094], false, 605, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcMotorConnectionType_type = new entity(strings[2095], false, 624, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcOccupant_type = new entity(strings[2096], false, 638, IFC4X1_IfcActor_type);
    IFC4X1_IfcOpeningElement_type = new entity(strings[2097], false, 644, IFC4X1_IfcFeatureElementSubtraction_type);
    IFC4X1_IfcOpeningStandardCase_type = new entity(strings[2098], false, 646, IFC4X1_IfcOpeningElement_type);
    IFC4X1_IfcOutletType_type = new entity(strings[2099], false, 654, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcPerformanceHistory_type = new entity(strings[2100], false, 661, IFC4X1_IfcControl_type);
    IFC4X1_IfcPermeableCoveringProperties_type = new entity(strings[2101], false, 664, IFC4X1_IfcPreDefinedPropertySet_type);
    IFC4X1_IfcPermit_type = new entity(strings[2102], false, 665, IFC4X1_IfcControl_type);
    IFC4X1_IfcPileType_type = new entity(strings[2103], false, 676, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcPipeFittingType_type = new entity(strings[2104], false, 679, IFC4X1_IfcFlowFittingType_type);
    IFC4X1_IfcPipeSegmentType_type = new entity(strings[2105], false, 682, IFC4X1_IfcFlowSegmentType_type);
    IFC4X1_IfcPlateType_type = new entity(strings[2106], false, 693, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcPolygonalFaceSet_type = new entity(strings[2107], false, 700, IFC4X1_IfcTessellatedFaceSet_type);
    IFC4X1_IfcPolyline_type = new entity(strings[2108], false, 701, IFC4X1_IfcBoundedCurve_type);
    IFC4X1_IfcPort_type = new entity(strings[2109], true, 703, IFC4X1_IfcProduct_type);
    IFC4X1_IfcPositioningElement_type = new entity(strings[2110], true, 704, IFC4X1_IfcProduct_type);
    IFC4X1_IfcProcedure_type = new entity(strings[2111], false, 726, IFC4X1_IfcProcess_type);
    IFC4X1_IfcProjectOrder_type = new entity(strings[2112], false, 745, IFC4X1_IfcControl_type);
    IFC4X1_IfcProjectionElement_type = new entity(strings[2113], false, 742, IFC4X1_IfcFeatureElementAddition_type);
    IFC4X1_IfcProtectiveDeviceType_type = new entity(strings[2114], false, 770, IFC4X1_IfcFlowControllerType_type);
    IFC4X1_IfcPumpType_type = new entity(strings[2115], false, 774, IFC4X1_IfcFlowMovingDeviceType_type);
    IFC4X1_IfcRailingType_type = new entity(strings[2116], false, 785, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcRampFlightType_type = new entity(strings[2117], false, 789, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcRampType_type = new entity(strings[2118], false, 791, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcRationalBSplineSurfaceWithKnots_type = new entity(strings[2119], false, 795, IFC4X1_IfcBSplineSurfaceWithKnots_type);
    IFC4X1_IfcReferent_type = new entity(strings[2120], false, 804, IFC4X1_IfcPositioningElement_type);
    IFC4X1_IfcReinforcingElement_type = new entity(strings[2121], true, 815, IFC4X1_IfcElementComponent_type);
    IFC4X1_IfcReinforcingElementType_type = new entity(strings[2122], true, 816, IFC4X1_IfcElementComponentType_type);
    IFC4X1_IfcReinforcingMesh_type = new entity(strings[2123], false, 817, IFC4X1_IfcReinforcingElement_type);
    IFC4X1_IfcReinforcingMeshType_type = new entity(strings[2124], false, 818, IFC4X1_IfcReinforcingElementType_type);
    IFC4X1_IfcRelAggregates_type = new entity(strings[2125], false, 820, IFC4X1_IfcRelDecomposes_type);
    IFC4X1_IfcRoofType_type = new entity(strings[2126], false, 886, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcSanitaryTerminalType_type = new entity(strings[2127], false, 895, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcSeamCurve_type = new entity(strings[2128], false, 898, IFC4X1_IfcSurfaceCurve_type);
    IFC4X1_IfcShadingDeviceType_type = new entity(strings[2129], false, 913, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcSite_type = new entity(strings[2130], false, 926, IFC4X1_IfcSpatialStructureElement_type);
    IFC4X1_IfcSlabType_type = new entity(strings[2131], false, 933, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcSolarDeviceType_type = new entity(strings[2132], false, 937, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcSpace_type = new entity(strings[2133], false, 946, IFC4X1_IfcSpatialStructureElement_type);
    IFC4X1_IfcSpaceHeaterType_type = new entity(strings[2134], false, 949, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcSpaceType_type = new entity(strings[2135], false, 951, IFC4X1_IfcSpatialStructureElementType_type);
    IFC4X1_IfcStackTerminalType_type = new entity(strings[2136], false, 967, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcStairFlightType_type = new entity(strings[2137], false, 971, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcStairType_type = new entity(strings[2138], false, 973, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcStructuralAction_type = new entity(strings[2139], true, 976, IFC4X1_IfcStructuralActivity_type);
    IFC4X1_IfcStructuralConnection_type = new entity(strings[2140], true, 980, IFC4X1_IfcStructuralItem_type);
    IFC4X1_IfcStructuralCurveAction_type = new entity(strings[2141], false, 982, IFC4X1_IfcStructuralAction_type);
    IFC4X1_IfcStructuralCurveConnection_type = new entity(strings[2142], false, 984, IFC4X1_IfcStructuralConnection_type);
    IFC4X1_IfcStructuralCurveMember_type = new entity(strings[2143], false, 985, IFC4X1_IfcStructuralMember_type);
    IFC4X1_IfcStructuralCurveMemberVarying_type = new entity(strings[2144], false, 987, IFC4X1_IfcStructuralCurveMember_type);
    IFC4X1_IfcStructuralCurveReaction_type = new entity(strings[2145], false, 988, IFC4X1_IfcStructuralReaction_type);
    IFC4X1_IfcStructuralLinearAction_type = new entity(strings[2146], false, 990, IFC4X1_IfcStructuralCurveAction_type);
    IFC4X1_IfcStructuralLoadGroup_type = new entity(strings[2147], false, 994, IFC4X1_IfcGroup_type);
    IFC4X1_IfcStructuralPointAction_type = new entity(strings[2148], false, 1006, IFC4X1_IfcStructuralAction_type);
    IFC4X1_IfcStructuralPointConnection_type = new entity(strings[2149], false, 1007, IFC4X1_IfcStructuralConnection_type);
    IFC4X1_IfcStructuralPointReaction_type = new entity(strings[2150], false, 1008, IFC4X1_IfcStructuralReaction_type);
    IFC4X1_IfcStructuralResultGroup_type = new entity(strings[2151], false, 1010, IFC4X1_IfcGroup_type);
    IFC4X1_IfcStructuralSurfaceAction_type = new entity(strings[2152], false, 1011, IFC4X1_IfcStructuralAction_type);
    IFC4X1_IfcStructuralSurfaceConnection_type = new entity(strings[2153], false, 1013, IFC4X1_IfcStructuralConnection_type);
    IFC4X1_IfcSubContractResource_type = new entity(strings[2154], false, 1022, IFC4X1_IfcConstructionResource_type);
    IFC4X1_IfcSurfaceFeature_type = new entity(strings[2155], false, 1029, IFC4X1_IfcFeatureElement_type);
    IFC4X1_IfcSwitchingDeviceType_type = new entity(strings[2156], false, 1049, IFC4X1_IfcFlowControllerType_type);
    IFC4X1_IfcSystem_type = new entity(strings[2157], false, 1051, IFC4X1_IfcGroup_type);
    IFC4X1_IfcSystemFurnitureElement_type = new entity(strings[2158], false, 1052, IFC4X1_IfcFurnishingElement_type);
    IFC4X1_IfcTankType_type = new entity(strings[2159], false, 1059, IFC4X1_IfcFlowStorageDeviceType_type);
    IFC4X1_IfcTendon_type = new entity(strings[2160], false, 1070, IFC4X1_IfcReinforcingElement_type);
    IFC4X1_IfcTendonAnchor_type = new entity(strings[2161], false, 1071, IFC4X1_IfcReinforcingElement_type);
    IFC4X1_IfcTendonAnchorType_type = new entity(strings[2162], false, 1072, IFC4X1_IfcReinforcingElementType_type);
    IFC4X1_IfcTendonType_type = new entity(strings[2163], false, 1074, IFC4X1_IfcReinforcingElementType_type);
    IFC4X1_IfcTransformerType_type = new entity(strings[2164], false, 1115, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcTransitionCurveSegment2D_type = new entity(strings[2165], false, 1118, IFC4X1_IfcCurveSegment2D_type);
    IFC4X1_IfcTransportElement_type = new entity(strings[2166], false, 1121, IFC4X1_IfcElement_type);
    IFC4X1_IfcTrimmedCurve_type = new entity(strings[2167], false, 1127, IFC4X1_IfcBoundedCurve_type);
    IFC4X1_IfcTubeBundleType_type = new entity(strings[2168], false, 1132, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcUnitaryEquipmentType_type = new entity(strings[2169], false, 1143, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcValveType_type = new entity(strings[2170], false, 1151, IFC4X1_IfcFlowControllerType_type);
    IFC4X1_IfcVibrationIsolator_type = new entity(strings[2171], false, 1159, IFC4X1_IfcElementComponent_type);
    IFC4X1_IfcVibrationIsolatorType_type = new entity(strings[2172], false, 1160, IFC4X1_IfcElementComponentType_type);
    IFC4X1_IfcVirtualElement_type = new entity(strings[2173], false, 1162, IFC4X1_IfcElement_type);
    IFC4X1_IfcVoidingFeature_type = new entity(strings[2174], false, 1164, IFC4X1_IfcFeatureElementSubtraction_type);
    IFC4X1_IfcWallType_type = new entity(strings[2175], false, 1171, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcWasteTerminalType_type = new entity(strings[2176], false, 1177, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcWindowType_type = new entity(strings[2177], false, 1188, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcWorkCalendar_type = new entity(strings[2178], false, 1191, IFC4X1_IfcControl_type);
    IFC4X1_IfcWorkControl_type = new entity(strings[2179], true, 1193, IFC4X1_IfcControl_type);
    IFC4X1_IfcWorkPlan_type = new entity(strings[2180], false, 1194, IFC4X1_IfcWorkControl_type);
    IFC4X1_IfcWorkSchedule_type = new entity(strings[2181], false, 1196, IFC4X1_IfcWorkControl_type);
    IFC4X1_IfcZone_type = new entity(strings[2182], false, 1199, IFC4X1_IfcSystem_type);
    IFC4X1_IfcCurveFontOrScaledCurveFontSelect_type = new select_type(strings[2183], 252, {
        IFC4X1_IfcCurveStyleFontAndScaling_type,
        IFC4X1_IfcCurveStyleFontSelect_type
    });
    IFC4X1_IfcCurveOnSurface_type = new select_type(strings[2184], 254, {
        IFC4X1_IfcCompositeCurveOnSurface_type,
        IFC4X1_IfcPcurve_type,
        IFC4X1_IfcSurfaceCurve_type
    });
    IFC4X1_IfcCurveOrEdgeCurve_type = new select_type(strings[2185], 255, {
        IFC4X1_IfcBoundedCurve_type,
        IFC4X1_IfcEdgeCurve_type
    });
    IFC4X1_IfcStructuralActivityAssignmentSelect_type = new select_type(strings[2186], 978, {
        IFC4X1_IfcElement_type,
        IFC4X1_IfcStructuralItem_type
    });
    IFC4X1_IfcActionRequest_type = new entity(strings[2187], false, 2, IFC4X1_IfcControl_type);
    IFC4X1_IfcAirTerminalBoxType_type = new entity(strings[2188], false, 19, IFC4X1_IfcFlowControllerType_type);
    IFC4X1_IfcAirTerminalType_type = new entity(strings[2189], false, 21, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcAirToAirHeatRecoveryType_type = new entity(strings[2190], false, 24, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcAlignmentCurve_type = new entity(strings[2191], false, 38, IFC4X1_IfcBoundedCurve_type);
    IFC4X1_IfcAsset_type = new entity(strings[2192], false, 59, IFC4X1_IfcGroup_type);
    IFC4X1_IfcAudioVisualApplianceType_type = new entity(strings[2193], false, 62, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcBSplineCurve_type = new entity(strings[2194], true, 96, IFC4X1_IfcBoundedCurve_type);
    IFC4X1_IfcBSplineCurveWithKnots_type = new entity(strings[2195], false, 98, IFC4X1_IfcBSplineCurve_type);
    IFC4X1_IfcBeamType_type = new entity(strings[2196], false, 70, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcBoilerType_type = new entity(strings[2197], false, 78, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcBoundaryCurve_type = new entity(strings[2198], false, 86, IFC4X1_IfcCompositeCurveOnSurface_type);
    IFC4X1_IfcBuildingElement_type = new entity(strings[2199], true, 103, IFC4X1_IfcElement_type);
    IFC4X1_IfcBuildingElementPart_type = new entity(strings[2200], false, 104, IFC4X1_IfcElementComponent_type);
    IFC4X1_IfcBuildingElementPartType_type = new entity(strings[2201], false, 105, IFC4X1_IfcElementComponentType_type);
    IFC4X1_IfcBuildingElementProxy_type = new entity(strings[2202], false, 107, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcBuildingElementProxyType_type = new entity(strings[2203], false, 108, IFC4X1_IfcBuildingElementType_type);
    IFC4X1_IfcBuildingSystem_type = new entity(strings[2204], false, 112, IFC4X1_IfcSystem_type);
    IFC4X1_IfcBurnerType_type = new entity(strings[2205], false, 115, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcCableCarrierFittingType_type = new entity(strings[2206], false, 118, IFC4X1_IfcFlowFittingType_type);
    IFC4X1_IfcCableCarrierSegmentType_type = new entity(strings[2207], false, 121, IFC4X1_IfcFlowSegmentType_type);
    IFC4X1_IfcCableFittingType_type = new entity(strings[2208], false, 124, IFC4X1_IfcFlowFittingType_type);
    IFC4X1_IfcCableSegmentType_type = new entity(strings[2209], false, 127, IFC4X1_IfcFlowSegmentType_type);
    IFC4X1_IfcChillerType_type = new entity(strings[2210], false, 142, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcChimney_type = new entity(strings[2211], false, 144, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcCircle_type = new entity(strings[2212], false, 147, IFC4X1_IfcConic_type);
    IFC4X1_IfcCircularArcSegment2D_type = new entity(strings[2213], false, 150, IFC4X1_IfcCurveSegment2D_type);
    IFC4X1_IfcCivilElement_type = new entity(strings[2214], false, 151, IFC4X1_IfcElement_type);
    IFC4X1_IfcCoilType_type = new entity(strings[2215], false, 159, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcColumn_type = new entity(strings[2216], false, 166, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcColumnStandardCase_type = new entity(strings[2217], false, 167, IFC4X1_IfcColumn_type);
    IFC4X1_IfcCommunicationsApplianceType_type = new entity(strings[2218], false, 171, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcCompressorType_type = new entity(strings[2219], false, 183, IFC4X1_IfcFlowMovingDeviceType_type);
    IFC4X1_IfcCondenserType_type = new entity(strings[2220], false, 186, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcConstructionEquipmentResource_type = new entity(strings[2221], false, 199, IFC4X1_IfcConstructionResource_type);
    IFC4X1_IfcConstructionMaterialResource_type = new entity(strings[2222], false, 202, IFC4X1_IfcConstructionResource_type);
    IFC4X1_IfcConstructionProductResource_type = new entity(strings[2223], false, 205, IFC4X1_IfcConstructionResource_type);
    IFC4X1_IfcCooledBeamType_type = new entity(strings[2224], false, 220, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcCoolingTowerType_type = new entity(strings[2225], false, 223, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcCovering_type = new entity(strings[2226], false, 234, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcCurtainWall_type = new entity(strings[2227], false, 245, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcDamperType_type = new entity(strings[2228], false, 264, IFC4X1_IfcFlowControllerType_type);
    IFC4X1_IfcDiscreteAccessory_type = new entity(strings[2229], false, 282, IFC4X1_IfcElementComponent_type);
    IFC4X1_IfcDiscreteAccessoryType_type = new entity(strings[2230], false, 283, IFC4X1_IfcElementComponentType_type);
    IFC4X1_IfcDistributionChamberElementType_type = new entity(strings[2231], false, 287, IFC4X1_IfcDistributionFlowElementType_type);
    IFC4X1_IfcDistributionControlElementType_type = new entity(strings[2232], true, 291, IFC4X1_IfcDistributionElementType_type);
    IFC4X1_IfcDistributionElement_type = new entity(strings[2233], false, 292, IFC4X1_IfcElement_type);
    IFC4X1_IfcDistributionFlowElement_type = new entity(strings[2234], false, 294, IFC4X1_IfcDistributionElement_type);
    IFC4X1_IfcDistributionPort_type = new entity(strings[2235], false, 296, IFC4X1_IfcPort_type);
    IFC4X1_IfcDistributionSystem_type = new entity(strings[2236], false, 298, IFC4X1_IfcSystem_type);
    IFC4X1_IfcDoor_type = new entity(strings[2237], false, 306, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcDoorStandardCase_type = new entity(strings[2238], false, 311, IFC4X1_IfcDoor_type);
    IFC4X1_IfcDuctFittingType_type = new entity(strings[2239], false, 322, IFC4X1_IfcFlowFittingType_type);
    IFC4X1_IfcDuctSegmentType_type = new entity(strings[2240], false, 325, IFC4X1_IfcFlowSegmentType_type);
    IFC4X1_IfcDuctSilencerType_type = new entity(strings[2241], false, 328, IFC4X1_IfcFlowTreatmentDeviceType_type);
    IFC4X1_IfcElectricApplianceType_type = new entity(strings[2242], false, 336, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcElectricDistributionBoardType_type = new entity(strings[2243], false, 343, IFC4X1_IfcFlowControllerType_type);
    IFC4X1_IfcElectricFlowStorageDeviceType_type = new entity(strings[2244], false, 346, IFC4X1_IfcFlowStorageDeviceType_type);
    IFC4X1_IfcElectricGeneratorType_type = new entity(strings[2245], false, 349, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcElectricMotorType_type = new entity(strings[2246], false, 352, IFC4X1_IfcEnergyConversionDeviceType_type);
    IFC4X1_IfcElectricTimeControlType_type = new entity(strings[2247], false, 356, IFC4X1_IfcFlowControllerType_type);
    IFC4X1_IfcEnergyConversionDevice_type = new entity(strings[2248], false, 371, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcEngine_type = new entity(strings[2249], false, 374, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcEvaporativeCooler_type = new entity(strings[2250], false, 377, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcEvaporator_type = new entity(strings[2251], false, 380, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcExternalSpatialElement_type = new entity(strings[2252], false, 395, IFC4X1_IfcExternalSpatialStructureElement_type);
    IFC4X1_IfcFanType_type = new entity(strings[2253], false, 409, IFC4X1_IfcFlowMovingDeviceType_type);
    IFC4X1_IfcFilterType_type = new entity(strings[2254], false, 422, IFC4X1_IfcFlowTreatmentDeviceType_type);
    IFC4X1_IfcFireSuppressionTerminalType_type = new entity(strings[2255], false, 425, IFC4X1_IfcFlowTerminalType_type);
    IFC4X1_IfcFlowController_type = new entity(strings[2256], false, 428, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcFlowFitting_type = new entity(strings[2257], false, 431, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcFlowInstrumentType_type = new entity(strings[2258], false, 434, IFC4X1_IfcDistributionControlElementType_type);
    IFC4X1_IfcFlowMeter_type = new entity(strings[2259], false, 436, IFC4X1_IfcFlowController_type);
    IFC4X1_IfcFlowMovingDevice_type = new entity(strings[2260], false, 439, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcFlowSegment_type = new entity(strings[2261], false, 441, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcFlowStorageDevice_type = new entity(strings[2262], false, 443, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcFlowTerminal_type = new entity(strings[2263], false, 445, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcFlowTreatmentDevice_type = new entity(strings[2264], false, 447, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcFooting_type = new entity(strings[2265], false, 452, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcGrid_type = new entity(strings[2266], false, 474, IFC4X1_IfcPositioningElement_type);
    IFC4X1_IfcHeatExchanger_type = new entity(strings[2267], false, 482, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcHumidifier_type = new entity(strings[2268], false, 487, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcInterceptor_type = new entity(strings[2269], false, 502, IFC4X1_IfcFlowTreatmentDevice_type);
    IFC4X1_IfcJunctionBox_type = new entity(strings[2270], false, 514, IFC4X1_IfcFlowFitting_type);
    IFC4X1_IfcLamp_type = new entity(strings[2271], false, 524, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcLightFixture_type = new entity(strings[2272], false, 538, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcLinearPositioningElement_type = new entity(strings[2273], true, 552, IFC4X1_IfcPositioningElement_type);
    IFC4X1_IfcMedicalDevice_type = new entity(strings[2274], false, 600, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcMember_type = new entity(strings[2275], false, 603, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcMemberStandardCase_type = new entity(strings[2276], false, 604, IFC4X1_IfcMember_type);
    IFC4X1_IfcMotorConnection_type = new entity(strings[2277], false, 623, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcOuterBoundaryCurve_type = new entity(strings[2278], false, 652, IFC4X1_IfcBoundaryCurve_type);
    IFC4X1_IfcOutlet_type = new entity(strings[2279], false, 653, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcPile_type = new entity(strings[2280], false, 674, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcPipeFitting_type = new entity(strings[2281], false, 678, IFC4X1_IfcFlowFitting_type);
    IFC4X1_IfcPipeSegment_type = new entity(strings[2282], false, 681, IFC4X1_IfcFlowSegment_type);
    IFC4X1_IfcPlate_type = new entity(strings[2283], false, 691, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcPlateStandardCase_type = new entity(strings[2284], false, 692, IFC4X1_IfcPlate_type);
    IFC4X1_IfcProtectiveDevice_type = new entity(strings[2285], false, 766, IFC4X1_IfcFlowController_type);
    IFC4X1_IfcProtectiveDeviceTrippingUnitType_type = new entity(strings[2286], false, 768, IFC4X1_IfcDistributionControlElementType_type);
    IFC4X1_IfcPump_type = new entity(strings[2287], false, 773, IFC4X1_IfcFlowMovingDevice_type);
    IFC4X1_IfcRailing_type = new entity(strings[2288], false, 784, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcRamp_type = new entity(strings[2289], false, 787, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcRampFlight_type = new entity(strings[2290], false, 788, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcRationalBSplineCurveWithKnots_type = new entity(strings[2291], false, 794, IFC4X1_IfcBSplineCurveWithKnots_type);
    IFC4X1_IfcReinforcingBar_type = new entity(strings[2292], false, 810, IFC4X1_IfcReinforcingElement_type);
    IFC4X1_IfcReinforcingBarType_type = new entity(strings[2293], false, 813, IFC4X1_IfcReinforcingElementType_type);
    IFC4X1_IfcRoof_type = new entity(strings[2294], false, 885, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcSanitaryTerminal_type = new entity(strings[2295], false, 894, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcSensorType_type = new entity(strings[2296], false, 909, IFC4X1_IfcDistributionControlElementType_type);
    IFC4X1_IfcShadingDevice_type = new entity(strings[2297], false, 912, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcSlab_type = new entity(strings[2298], false, 930, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcSlabElementedCase_type = new entity(strings[2299], false, 931, IFC4X1_IfcSlab_type);
    IFC4X1_IfcSlabStandardCase_type = new entity(strings[2300], false, 932, IFC4X1_IfcSlab_type);
    IFC4X1_IfcSolarDevice_type = new entity(strings[2301], false, 936, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcSpaceHeater_type = new entity(strings[2302], false, 948, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcStackTerminal_type = new entity(strings[2303], false, 966, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcStair_type = new entity(strings[2304], false, 969, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcStairFlight_type = new entity(strings[2305], false, 970, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcStructuralAnalysisModel_type = new entity(strings[2306], false, 979, IFC4X1_IfcSystem_type);
    IFC4X1_IfcStructuralLoadCase_type = new entity(strings[2307], false, 992, IFC4X1_IfcStructuralLoadGroup_type);
    IFC4X1_IfcStructuralPlanarAction_type = new entity(strings[2308], false, 1005, IFC4X1_IfcStructuralSurfaceAction_type);
    IFC4X1_IfcSwitchingDevice_type = new entity(strings[2309], false, 1048, IFC4X1_IfcFlowController_type);
    IFC4X1_IfcTank_type = new entity(strings[2310], false, 1058, IFC4X1_IfcFlowStorageDevice_type);
    IFC4X1_IfcTransformer_type = new entity(strings[2311], false, 1114, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcTubeBundle_type = new entity(strings[2312], false, 1131, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcUnitaryControlElementType_type = new entity(strings[2313], false, 1140, IFC4X1_IfcDistributionControlElementType_type);
    IFC4X1_IfcUnitaryEquipment_type = new entity(strings[2314], false, 1142, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcValve_type = new entity(strings[2315], false, 1150, IFC4X1_IfcFlowController_type);
    IFC4X1_IfcWall_type = new entity(strings[2316], false, 1168, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcWallElementedCase_type = new entity(strings[2317], false, 1169, IFC4X1_IfcWall_type);
    IFC4X1_IfcWallStandardCase_type = new entity(strings[2318], false, 1170, IFC4X1_IfcWall_type);
    IFC4X1_IfcWasteTerminal_type = new entity(strings[2319], false, 1176, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcWindow_type = new entity(strings[2320], false, 1179, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcWindowStandardCase_type = new entity(strings[2321], false, 1184, IFC4X1_IfcWindow_type);
    IFC4X1_IfcSpaceBoundarySelect_type = new select_type(strings[2322], 947, {
        IFC4X1_IfcExternalSpatialElement_type,
        IFC4X1_IfcSpace_type
    });
    IFC4X1_IfcActuatorType_type = new entity(strings[2323], false, 10, IFC4X1_IfcDistributionControlElementType_type);
    IFC4X1_IfcAirTerminal_type = new entity(strings[2324], false, 17, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcAirTerminalBox_type = new entity(strings[2325], false, 18, IFC4X1_IfcFlowController_type);
    IFC4X1_IfcAirToAirHeatRecovery_type = new entity(strings[2326], false, 23, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcAlarmType_type = new entity(strings[2327], false, 27, IFC4X1_IfcDistributionControlElementType_type);
    IFC4X1_IfcAlignment_type = new entity(strings[2328], false, 29, IFC4X1_IfcLinearPositioningElement_type);
    IFC4X1_IfcAudioVisualAppliance_type = new entity(strings[2329], false, 61, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcBeam_type = new entity(strings[2330], false, 68, IFC4X1_IfcBuildingElement_type);
    IFC4X1_IfcBeamStandardCase_type = new entity(strings[2331], false, 69, IFC4X1_IfcBeam_type);
    IFC4X1_IfcBoiler_type = new entity(strings[2332], false, 77, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcBurner_type = new entity(strings[2333], false, 114, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcCableCarrierFitting_type = new entity(strings[2334], false, 117, IFC4X1_IfcFlowFitting_type);
    IFC4X1_IfcCableCarrierSegment_type = new entity(strings[2335], false, 120, IFC4X1_IfcFlowSegment_type);
    IFC4X1_IfcCableFitting_type = new entity(strings[2336], false, 123, IFC4X1_IfcFlowFitting_type);
    IFC4X1_IfcCableSegment_type = new entity(strings[2337], false, 126, IFC4X1_IfcFlowSegment_type);
    IFC4X1_IfcChiller_type = new entity(strings[2338], false, 141, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcCoil_type = new entity(strings[2339], false, 158, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcCommunicationsAppliance_type = new entity(strings[2340], false, 170, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcCompressor_type = new entity(strings[2341], false, 182, IFC4X1_IfcFlowMovingDevice_type);
    IFC4X1_IfcCondenser_type = new entity(strings[2342], false, 185, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcControllerType_type = new entity(strings[2343], false, 215, IFC4X1_IfcDistributionControlElementType_type);
    IFC4X1_IfcCooledBeam_type = new entity(strings[2344], false, 219, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcCoolingTower_type = new entity(strings[2345], false, 222, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcDamper_type = new entity(strings[2346], false, 263, IFC4X1_IfcFlowController_type);
    IFC4X1_IfcDistributionChamberElement_type = new entity(strings[2347], false, 286, IFC4X1_IfcDistributionFlowElement_type);
    IFC4X1_IfcDistributionCircuit_type = new entity(strings[2348], false, 289, IFC4X1_IfcDistributionSystem_type);
    IFC4X1_IfcDistributionControlElement_type = new entity(strings[2349], false, 290, IFC4X1_IfcDistributionElement_type);
    IFC4X1_IfcDuctFitting_type = new entity(strings[2350], false, 321, IFC4X1_IfcFlowFitting_type);
    IFC4X1_IfcDuctSegment_type = new entity(strings[2351], false, 324, IFC4X1_IfcFlowSegment_type);
    IFC4X1_IfcDuctSilencer_type = new entity(strings[2352], false, 327, IFC4X1_IfcFlowTreatmentDevice_type);
    IFC4X1_IfcElectricAppliance_type = new entity(strings[2353], false, 335, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcElectricDistributionBoard_type = new entity(strings[2354], false, 342, IFC4X1_IfcFlowController_type);
    IFC4X1_IfcElectricFlowStorageDevice_type = new entity(strings[2355], false, 345, IFC4X1_IfcFlowStorageDevice_type);
    IFC4X1_IfcElectricGenerator_type = new entity(strings[2356], false, 348, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcElectricMotor_type = new entity(strings[2357], false, 351, IFC4X1_IfcEnergyConversionDevice_type);
    IFC4X1_IfcElectricTimeControl_type = new entity(strings[2358], false, 355, IFC4X1_IfcFlowController_type);
    IFC4X1_IfcFan_type = new entity(strings[2359], false, 408, IFC4X1_IfcFlowMovingDevice_type);
    IFC4X1_IfcFilter_type = new entity(strings[2360], false, 421, IFC4X1_IfcFlowTreatmentDevice_type);
    IFC4X1_IfcFireSuppressionTerminal_type = new entity(strings[2361], false, 424, IFC4X1_IfcFlowTerminal_type);
    IFC4X1_IfcFlowInstrument_type = new entity(strings[2362], false, 433, IFC4X1_IfcDistributionControlElement_type);
    IFC4X1_IfcProtectiveDeviceTrippingUnit_type = new entity(strings[2363], false, 767, IFC4X1_IfcDistributionControlElement_type);
    IFC4X1_IfcSensor_type = new entity(strings[2364], false, 908, IFC4X1_IfcDistributionControlElement_type);
    IFC4X1_IfcUnitaryControlElement_type = new entity(strings[2365], false, 1139, IFC4X1_IfcDistributionControlElement_type);
    IFC4X1_IfcActuator_type = new entity(strings[2366], false, 9, IFC4X1_IfcDistributionControlElement_type);
    IFC4X1_IfcAlarm_type = new entity(strings[2367], false, 26, IFC4X1_IfcDistributionControlElement_type);
    IFC4X1_IfcController_type = new entity(strings[2368], false, 214, IFC4X1_IfcDistributionControlElement_type);
    IFC4X1_IfcActionRequest_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcActionRequestTypeEnum_type), true),
            new attribute(strings[2370], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2371], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcActor_type->set_attributes({
            new attribute(strings[2372], new named_type(IFC4X1_IfcActorSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcActorRole_type->set_attributes({
            new attribute(strings[2373], new named_type(IFC4X1_IfcRoleEnum_type), false),
            new attribute(strings[2374], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcActuator_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcActuatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcActuatorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcActuatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAddress_type->set_attributes({
            new attribute(strings[2376], new named_type(IFC4X1_IfcAddressTypeEnum_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2377], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcAdvancedBrep_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcAdvancedBrepWithVoids_type->set_attributes({
            new attribute(strings[2378], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcClosedShell_type)), false)
    },{
            false, false
    });
    IFC4X1_IfcAdvancedFace_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcAirTerminal_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAirTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAirTerminalBox_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAirTerminalBoxTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAirTerminalBoxType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAirTerminalBoxTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAirTerminalType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAirTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAirToAirHeatRecovery_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAirToAirHeatRecoveryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAirToAirHeatRecoveryType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAirToAirHeatRecoveryTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAlarm_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAlarmTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAlarmType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAlarmTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAlignment_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAlignmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAlignment2DHorizontal_type->set_attributes({
            new attribute(strings[2379], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2380], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcAlignment2DHorizontalSegment_type)), false)
    },{
            false, false
    });
    IFC4X1_IfcAlignment2DHorizontalSegment_type->set_attributes({
            new attribute(strings[2381], new named_type(IFC4X1_IfcCurveSegment2D_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcAlignment2DSegment_type->set_attributes({
            new attribute(strings[2382], new named_type(IFC4X1_IfcBoolean_type), true),
            new attribute(strings[2383], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2384], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcAlignment2DVerSegCircularArc_type->set_attributes({
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2386], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAlignment2DVerSegLine_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcAlignment2DVerSegParabolicArc_type->set_attributes({
            new attribute(strings[2387], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2386], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAlignment2DVertical_type->set_attributes({
            new attribute(strings[2380], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcAlignment2DVerticalSegment_type)), false)
    },{
            false
    });
    IFC4X1_IfcAlignment2DVerticalSegment_type->set_attributes({
            new attribute(strings[2379], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2388], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2389], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2390], new named_type(IFC4X1_IfcRatioMeasure_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcAlignmentCurve_type->set_attributes({
            new attribute(strings[2391], new named_type(IFC4X1_IfcAlignment2DHorizontal_type), false),
            new attribute(strings[2392], new named_type(IFC4X1_IfcAlignment2DVertical_type), true),
            new attribute(strings[2393], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcAnnotation_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcAnnotationFillArea_type->set_attributes({
            new attribute(strings[2394], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2395], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcCurve_type)), true)
    },{
            false, false
    });
    IFC4X1_IfcApplication_type->set_attributes({
            new attribute(strings[2396], new named_type(IFC4X1_IfcOrganization_type), false),
            new attribute(strings[2397], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2398], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2399], new named_type(IFC4X1_IfcIdentifier_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcAppliedValue_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2401], new named_type(IFC4X1_IfcAppliedValueSelect_type), true),
            new attribute(strings[2402], new named_type(IFC4X1_IfcMeasureWithUnit_type), true),
            new attribute(strings[2403], new named_type(IFC4X1_IfcDate_type), true),
            new attribute(strings[2404], new named_type(IFC4X1_IfcDate_type), true),
            new attribute(strings[2405], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2406], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2407], new named_type(IFC4X1_IfcArithmeticOperatorEnum_type), true),
            new attribute(strings[2408], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcAppliedValue_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcApproval_type->set_attributes({
            new attribute(strings[2409], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2410], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2370], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2411], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2412], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2413], new named_type(IFC4X1_IfcActorSelect_type), true),
            new attribute(strings[2414], new named_type(IFC4X1_IfcActorSelect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcApprovalRelationship_type->set_attributes({
            new attribute(strings[2415], new named_type(IFC4X1_IfcApproval_type), false),
            new attribute(strings[2416], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcApproval_type)), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcArbitraryClosedProfileDef_type->set_attributes({
            new attribute(strings[2417], new named_type(IFC4X1_IfcCurve_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcArbitraryOpenProfileDef_type->set_attributes({
            new attribute(strings[2418], new named_type(IFC4X1_IfcBoundedCurve_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcArbitraryProfileDefWithVoids_type->set_attributes({
            new attribute(strings[2419], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcCurve_type)), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcAsset_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2421], new named_type(IFC4X1_IfcCostValue_type), true),
            new attribute(strings[2422], new named_type(IFC4X1_IfcCostValue_type), true),
            new attribute(strings[2423], new named_type(IFC4X1_IfcCostValue_type), true),
            new attribute(strings[2424], new named_type(IFC4X1_IfcActorSelect_type), true),
            new attribute(strings[2425], new named_type(IFC4X1_IfcActorSelect_type), true),
            new attribute(strings[2426], new named_type(IFC4X1_IfcPerson_type), true),
            new attribute(strings[2427], new named_type(IFC4X1_IfcDate_type), true),
            new attribute(strings[2428], new named_type(IFC4X1_IfcCostValue_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAsymmetricIShapeProfileDef_type->set_attributes({
            new attribute(strings[2429], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2430], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2431], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2432], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2433], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2434], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2435], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2436], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2437], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2438], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[2439], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2440], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAudioVisualAppliance_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAudioVisualApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAudioVisualApplianceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAudioVisualApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcAxis1Placement_type->set_attributes({
            new attribute(strings[2441], new named_type(IFC4X1_IfcDirection_type), true)
    },{
            false, false
    });
    IFC4X1_IfcAxis2Placement2D_type->set_attributes({
            new attribute(strings[2442], new named_type(IFC4X1_IfcDirection_type), true)
    },{
            false, false
    });
    IFC4X1_IfcAxis2Placement3D_type->set_attributes({
            new attribute(strings[2441], new named_type(IFC4X1_IfcDirection_type), true),
            new attribute(strings[2442], new named_type(IFC4X1_IfcDirection_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcBSplineCurve_type->set_attributes({
            new attribute(strings[2443], new named_type(IFC4X1_IfcInteger_type), false),
            new attribute(strings[2444], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcCartesianPoint_type)), false),
            new attribute(strings[2445], new named_type(IFC4X1_IfcBSplineCurveForm_type), false),
            new attribute(strings[2446], new named_type(IFC4X1_IfcLogical_type), false),
            new attribute(strings[2447], new named_type(IFC4X1_IfcLogical_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcBSplineCurveWithKnots_type->set_attributes({
            new attribute(strings[2448], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcInteger_type)), false),
            new attribute(strings[2449], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcParameterValue_type)), false),
            new attribute(strings[2450], new named_type(IFC4X1_IfcKnotType_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBSplineSurface_type->set_attributes({
            new attribute(strings[2451], new named_type(IFC4X1_IfcInteger_type), false),
            new attribute(strings[2452], new named_type(IFC4X1_IfcInteger_type), false),
            new attribute(strings[2444], new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcCartesianPoint_type))), false),
            new attribute(strings[2453], new named_type(IFC4X1_IfcBSplineSurfaceForm_type), false),
            new attribute(strings[2454], new named_type(IFC4X1_IfcLogical_type), false),
            new attribute(strings[2455], new named_type(IFC4X1_IfcLogical_type), false),
            new attribute(strings[2447], new named_type(IFC4X1_IfcLogical_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcBSplineSurfaceWithKnots_type->set_attributes({
            new attribute(strings[2456], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcInteger_type)), false),
            new attribute(strings[2457], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcInteger_type)), false),
            new attribute(strings[2458], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcParameterValue_type)), false),
            new attribute(strings[2459], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcParameterValue_type)), false),
            new attribute(strings[2450], new named_type(IFC4X1_IfcKnotType_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBeam_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBeamTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBeamStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBeamType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBeamTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBlobTexture_type->set_attributes({
            new attribute(strings[2460], new named_type(IFC4X1_IfcIdentifier_type), false),
            new attribute(strings[2461], new named_type(IFC4X1_IfcBinary_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcBlock_type->set_attributes({
            new attribute(strings[2462], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2463], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2464], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcBoiler_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBoilerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBoilerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBoilerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBooleanClippingResult_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcBooleanResult_type->set_attributes({
            new attribute(strings[2465], new named_type(IFC4X1_IfcBooleanOperator_type), false),
            new attribute(strings[2466], new named_type(IFC4X1_IfcBooleanOperand_type), false),
            new attribute(strings[2467], new named_type(IFC4X1_IfcBooleanOperand_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcBoundaryCondition_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X1_IfcBoundaryCurve_type->set_attributes({
    },{
            false, false
    });
    IFC4X1_IfcBoundaryEdgeCondition_type->set_attributes({
            new attribute(strings[2468], new named_type(IFC4X1_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2469], new named_type(IFC4X1_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2470], new named_type(IFC4X1_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2471], new named_type(IFC4X1_IfcModulusOfRotationalSubgradeReactionSelect_type), true),
            new attribute(strings[2472], new named_type(IFC4X1_IfcModulusOfRotationalSubgradeReactionSelect_type), true),
            new attribute(strings[2473], new named_type(IFC4X1_IfcModulusOfRotationalSubgradeReactionSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcBoundaryFaceCondition_type->set_attributes({
            new attribute(strings[2474], new named_type(IFC4X1_IfcModulusOfSubgradeReactionSelect_type), true),
            new attribute(strings[2475], new named_type(IFC4X1_IfcModulusOfSubgradeReactionSelect_type), true),
            new attribute(strings[2476], new named_type(IFC4X1_IfcModulusOfSubgradeReactionSelect_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcBoundaryNodeCondition_type->set_attributes({
            new attribute(strings[2477], new named_type(IFC4X1_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2478], new named_type(IFC4X1_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2479], new named_type(IFC4X1_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2480], new named_type(IFC4X1_IfcRotationalStiffnessSelect_type), true),
            new attribute(strings[2481], new named_type(IFC4X1_IfcRotationalStiffnessSelect_type), true),
            new attribute(strings[2482], new named_type(IFC4X1_IfcRotationalStiffnessSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcBoundaryNodeConditionWarping_type->set_attributes({
            new attribute(strings[2483], new named_type(IFC4X1_IfcWarpingStiffnessSelect_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBoundedCurve_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcBoundedSurface_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcBoundingBox_type->set_attributes({
            new attribute(strings[2484], new named_type(IFC4X1_IfcCartesianPoint_type), false),
            new attribute(strings[2485], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2486], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2487], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcBoxedHalfSpace_type->set_attributes({
            new attribute(strings[2488], new named_type(IFC4X1_IfcBoundingBox_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcBuilding_type->set_attributes({
            new attribute(strings[2489], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2490], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2491], new named_type(IFC4X1_IfcPostalAddress_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBuildingElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBuildingElementPart_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBuildingElementPartTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBuildingElementPartType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBuildingElementPartTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBuildingElementProxy_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBuildingElementProxyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBuildingElementProxyType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBuildingElementProxyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBuildingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBuildingStorey_type->set_attributes({
            new attribute(strings[2492], new named_type(IFC4X1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBuildingSystem_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBuildingSystemTypeEnum_type), true),
            new attribute(strings[2493], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcBurner_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBurnerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcBurnerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcBurnerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCShapeProfileDef_type->set_attributes({
            new attribute(strings[2494], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2495], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2496], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2497], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2498], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCableCarrierFitting_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCableCarrierFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCableCarrierFittingType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCableCarrierFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCableCarrierSegment_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCableCarrierSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCableCarrierSegmentType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCableCarrierSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCableFitting_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCableFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCableFittingType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCableFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCableSegment_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCableSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCableSegmentType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCableSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCartesianPoint_type->set_attributes({
            new attribute(strings[2499], new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC4X1_IfcLengthMeasure_type)), false)
    },{
            false
    });
    IFC4X1_IfcCartesianPointList_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcCartesianPointList2D_type->set_attributes({
            new attribute(strings[2500], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_IfcLengthMeasure_type))), false),
            new attribute(strings[2501], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true)
    },{
            false, false
    });
    IFC4X1_IfcCartesianPointList3D_type->set_attributes({
            new attribute(strings[2500], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_IfcLengthMeasure_type))), false),
            new attribute(strings[2501], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true)
    },{
            false, false
    });
    IFC4X1_IfcCartesianTransformationOperator_type->set_attributes({
            new attribute(strings[2502], new named_type(IFC4X1_IfcDirection_type), true),
            new attribute(strings[2503], new named_type(IFC4X1_IfcDirection_type), true),
            new attribute(strings[2504], new named_type(IFC4X1_IfcCartesianPoint_type), false),
            new attribute(strings[2505], new named_type(IFC4X1_IfcReal_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcCartesianTransformationOperator2D_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcCartesianTransformationOperator2DnonUniform_type->set_attributes({
            new attribute(strings[2506], new named_type(IFC4X1_IfcReal_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcCartesianTransformationOperator3D_type->set_attributes({
            new attribute(strings[2507], new named_type(IFC4X1_IfcDirection_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcCartesianTransformationOperator3DnonUniform_type->set_attributes({
            new attribute(strings[2506], new named_type(IFC4X1_IfcReal_type), true),
            new attribute(strings[2508], new named_type(IFC4X1_IfcReal_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcCenterLineProfileDef_type->set_attributes({
            new attribute(strings[2509], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcChiller_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcChillerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcChillerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcChillerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcChimney_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcChimneyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcChimneyType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcChimneyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCircle_type->set_attributes({
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X1_IfcCircleHollowProfileDef_type->set_attributes({
            new attribute(strings[2496], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcCircleProfileDef_type->set_attributes({
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcCircularArcSegment2D_type->set_attributes({
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2510], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcCivilElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCivilElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcClassification_type->set_attributes({
            new attribute(strings[2511], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2512], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2513], new named_type(IFC4X1_IfcDate_type), true),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2514], new named_type(IFC4X1_IfcURIReference_type), true),
            new attribute(strings[2515], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcIdentifier_type)), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcClassificationReference_type->set_attributes({
            new attribute(strings[2516], new named_type(IFC4X1_IfcClassificationReferenceSelect_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2517], new named_type(IFC4X1_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcClosedShell_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcCoil_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCoilTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCoilType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCoilTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcColourRgb_type->set_attributes({
            new attribute(strings[2518], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), false),
            new attribute(strings[2519], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), false),
            new attribute(strings[2520], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcColourRgbList_type->set_attributes({
            new attribute(strings[2521], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_IfcNormalisedRatioMeasure_type))), false)
    },{
            false
    });
    IFC4X1_IfcColourSpecification_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X1_IfcColumn_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcColumnTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcColumnStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcColumnType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcColumnTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCommunicationsAppliance_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCommunicationsApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCommunicationsApplianceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCommunicationsApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcComplexProperty_type->set_attributes({
            new attribute(strings[2522], new named_type(IFC4X1_IfcIdentifier_type), false),
            new attribute(strings[2523], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcProperty_type)), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcComplexPropertyTemplate_type->set_attributes({
            new attribute(strings[2522], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2524], new named_type(IFC4X1_IfcComplexPropertyTemplateTypeEnum_type), true),
            new attribute(strings[2525], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPropertyTemplate_type)), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcCompositeCurve_type->set_attributes({
            new attribute(strings[2380], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcCompositeCurveSegment_type)), false),
            new attribute(strings[2447], new named_type(IFC4X1_IfcLogical_type), false)
    },{
            false, false
    });
    IFC4X1_IfcCompositeCurveOnSurface_type->set_attributes({
    },{
            false, false
    });
    IFC4X1_IfcCompositeCurveSegment_type->set_attributes({
            new attribute(strings[2526], new named_type(IFC4X1_IfcTransitionCode_type), false),
            new attribute(strings[2527], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[2528], new named_type(IFC4X1_IfcCurve_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcCompositeProfileDef_type->set_attributes({
            new attribute(strings[2529], new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC4X1_IfcProfileDef_type)), false),
            new attribute(strings[2530], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcCompressor_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCompressorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCompressorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCompressorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCondenser_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCondenserTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCondenserType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCondenserTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConic_type->set_attributes({
            new attribute(strings[2531], new named_type(IFC4X1_IfcAxis2Placement_type), false)
    },{
            false
    });
    IFC4X1_IfcConnectedFaceSet_type->set_attributes({
            new attribute(strings[2532], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcFace_type)), false)
    },{
            false
    });
    IFC4X1_IfcConnectionCurveGeometry_type->set_attributes({
            new attribute(strings[2533], new named_type(IFC4X1_IfcCurveOrEdgeCurve_type), false),
            new attribute(strings[2534], new named_type(IFC4X1_IfcCurveOrEdgeCurve_type), true)
    },{
            false, false
    });
    IFC4X1_IfcConnectionGeometry_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcConnectionPointEccentricity_type->set_attributes({
            new attribute(strings[2535], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2536], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2537], new named_type(IFC4X1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcConnectionPointGeometry_type->set_attributes({
            new attribute(strings[2538], new named_type(IFC4X1_IfcPointOrVertexPoint_type), false),
            new attribute(strings[2539], new named_type(IFC4X1_IfcPointOrVertexPoint_type), true)
    },{
            false, false
    });
    IFC4X1_IfcConnectionSurfaceGeometry_type->set_attributes({
            new attribute(strings[2540], new named_type(IFC4X1_IfcSurfaceOrFaceSurface_type), false),
            new attribute(strings[2541], new named_type(IFC4X1_IfcSurfaceOrFaceSurface_type), true)
    },{
            false, false
    });
    IFC4X1_IfcConnectionVolumeGeometry_type->set_attributes({
            new attribute(strings[2542], new named_type(IFC4X1_IfcSolidOrShell_type), false),
            new attribute(strings[2543], new named_type(IFC4X1_IfcSolidOrShell_type), true)
    },{
            false, false
    });
    IFC4X1_IfcConstraint_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2544], new named_type(IFC4X1_IfcConstraintEnum_type), false),
            new attribute(strings[2545], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2546], new named_type(IFC4X1_IfcActorSelect_type), true),
            new attribute(strings[2547], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2548], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcConstructionEquipmentResource_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcConstructionEquipmentResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConstructionEquipmentResourceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcConstructionEquipmentResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConstructionMaterialResource_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcConstructionMaterialResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConstructionMaterialResourceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcConstructionMaterialResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConstructionProductResource_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcConstructionProductResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConstructionProductResourceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcConstructionProductResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConstructionResource_type->set_attributes({
            new attribute(strings[2549], new named_type(IFC4X1_IfcResourceTime_type), true),
            new attribute(strings[2550], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcAppliedValue_type)), true),
            new attribute(strings[2551], new named_type(IFC4X1_IfcPhysicalQuantity_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConstructionResourceType_type->set_attributes({
            new attribute(strings[2550], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcAppliedValue_type)), true),
            new attribute(strings[2551], new named_type(IFC4X1_IfcPhysicalQuantity_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcContext_type->set_attributes({
            new attribute(strings[2552], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2493], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2553], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2554], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcRepresentationContext_type)), true),
            new attribute(strings[2555], new named_type(IFC4X1_IfcUnitAssignment_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcContextDependentUnit_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcControl_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcController_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcControllerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcControllerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcControllerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcConversionBasedUnit_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2556], new named_type(IFC4X1_IfcMeasureWithUnit_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcConversionBasedUnitWithOffset_type->set_attributes({
            new attribute(strings[2557], new named_type(IFC4X1_IfcReal_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcCooledBeam_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCooledBeamTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCooledBeamType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCooledBeamTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCoolingTower_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCoolingTowerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCoolingTowerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCoolingTowerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCoordinateOperation_type->set_attributes({
            new attribute(strings[2558], new named_type(IFC4X1_IfcCoordinateReferenceSystemSelect_type), false),
            new attribute(strings[2559], new named_type(IFC4X1_IfcCoordinateReferenceSystem_type), false)
    },{
            false, false
    });
    IFC4X1_IfcCoordinateReferenceSystem_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2560], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2561], new named_type(IFC4X1_IfcIdentifier_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcCostItem_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCostItemTypeEnum_type), true),
            new attribute(strings[2562], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcCostValue_type)), true),
            new attribute(strings[2563], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcPhysicalQuantity_type)), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCostSchedule_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCostScheduleTypeEnum_type), true),
            new attribute(strings[2370], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2564], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2565], new named_type(IFC4X1_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCostValue_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCovering_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCoveringTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCoveringType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCoveringTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCrewResource_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCrewResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCrewResourceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCrewResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCsgPrimitive3D_type->set_attributes({
            new attribute(strings[2531], new named_type(IFC4X1_IfcAxis2Placement3D_type), false)
    },{
            false
    });
    IFC4X1_IfcCsgSolid_type->set_attributes({
            new attribute(strings[2566], new named_type(IFC4X1_IfcCsgSelect_type), false)
    },{
            false
    });
    IFC4X1_IfcCurrencyRelationship_type->set_attributes({
            new attribute(strings[2567], new named_type(IFC4X1_IfcMonetaryUnit_type), false),
            new attribute(strings[2568], new named_type(IFC4X1_IfcMonetaryUnit_type), false),
            new attribute(strings[2569], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), false),
            new attribute(strings[2570], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2571], new named_type(IFC4X1_IfcLibraryInformation_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcCurtainWall_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCurtainWallTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCurtainWallType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcCurtainWallTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcCurve_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcCurveBoundedPlane_type->set_attributes({
            new attribute(strings[2572], new named_type(IFC4X1_IfcPlane_type), false),
            new attribute(strings[2394], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2395], new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X1_IfcCurve_type)), false)
    },{
            false, false, false
    });
    IFC4X1_IfcCurveBoundedSurface_type->set_attributes({
            new attribute(strings[2572], new named_type(IFC4X1_IfcSurface_type), false),
            new attribute(strings[2573], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcBoundaryCurve_type)), false),
            new attribute(strings[2574], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcCurveSegment2D_type->set_attributes({
            new attribute(strings[2575], new named_type(IFC4X1_IfcCartesianPoint_type), false),
            new attribute(strings[2576], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), false),
            new attribute(strings[2577], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcCurveStyle_type->set_attributes({
            new attribute(strings[2578], new named_type(IFC4X1_IfcCurveFontOrScaledCurveFontSelect_type), true),
            new attribute(strings[2579], new named_type(IFC4X1_IfcSizeSelect_type), true),
            new attribute(strings[2580], new named_type(IFC4X1_IfcColour_type), true),
            new attribute(strings[2581], new named_type(IFC4X1_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcCurveStyleFont_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2582], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcCurveStyleFontPattern_type)), false)
    },{
            false, false
    });
    IFC4X1_IfcCurveStyleFontAndScaling_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2578], new named_type(IFC4X1_IfcCurveStyleFontSelect_type), false),
            new attribute(strings[2583], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcCurveStyleFontPattern_type->set_attributes({
            new attribute(strings[2584], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2585], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X1_IfcCylindricalSurface_type->set_attributes({
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X1_IfcDamper_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDamperTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDamperType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDamperTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDerivedProfileDef_type->set_attributes({
            new attribute(strings[2586], new named_type(IFC4X1_IfcProfileDef_type), false),
            new attribute(strings[2465], new named_type(IFC4X1_IfcCartesianTransformationOperator2D_type), false),
            new attribute(strings[2530], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcDerivedUnit_type->set_attributes({
            new attribute(strings[2587], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcDerivedUnitElement_type)), false),
            new attribute(strings[2588], new named_type(IFC4X1_IfcDerivedUnitEnum_type), false),
            new attribute(strings[2589], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcDerivedUnitElement_type->set_attributes({
            new attribute(strings[2590], new named_type(IFC4X1_IfcNamedUnit_type), false),
            new attribute(strings[2591], new simple_type(simple_type::integer_type), false)
    },{
            false, false
    });
    IFC4X1_IfcDimensionalExponents_type->set_attributes({
            new attribute(strings[2592], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2593], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2594], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2595], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2596], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2597], new simple_type(simple_type::integer_type), false),
            new attribute(strings[2598], new simple_type(simple_type::integer_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcDirection_type->set_attributes({
            new attribute(strings[2599], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X1_IfcReal_type)), false)
    },{
            false
    });
    IFC4X1_IfcDiscreteAccessory_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDiscreteAccessoryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDiscreteAccessoryType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDiscreteAccessoryTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistanceExpression_type->set_attributes({
            new attribute(strings[2600], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2601], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2602], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2603], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2604], new named_type(IFC4X1_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcDistributionChamberElement_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDistributionChamberElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionChamberElementType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDistributionChamberElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionCircuit_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionControlElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionControlElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionFlowElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionFlowElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionPort_type->set_attributes({
            new attribute(strings[2605], new named_type(IFC4X1_IfcFlowDirectionEnum_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcDistributionPortTypeEnum_type), true),
            new attribute(strings[2606], new named_type(IFC4X1_IfcDistributionSystemEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDistributionSystem_type->set_attributes({
            new attribute(strings[2493], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcDistributionSystemEnum_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcDocumentInformation_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), false),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2514], new named_type(IFC4X1_IfcURIReference_type), true),
            new attribute(strings[2376], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2607], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2608], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2609], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2610], new named_type(IFC4X1_IfcActorSelect_type), true),
            new attribute(strings[2611], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcActorSelect_type)), true),
            new attribute(strings[2547], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2612], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2613], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2614], new named_type(IFC4X1_IfcDate_type), true),
            new attribute(strings[2615], new named_type(IFC4X1_IfcDate_type), true),
            new attribute(strings[2616], new named_type(IFC4X1_IfcDocumentConfidentialityEnum_type), true),
            new attribute(strings[2370], new named_type(IFC4X1_IfcDocumentStatusEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDocumentInformationRelationship_type->set_attributes({
            new attribute(strings[2617], new named_type(IFC4X1_IfcDocumentInformation_type), false),
            new attribute(strings[2618], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcDocumentInformation_type)), false),
            new attribute(strings[2619], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcDocumentReference_type->set_attributes({
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2620], new named_type(IFC4X1_IfcDocumentInformation_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcDoor_type->set_attributes({
            new attribute(strings[2621], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2622], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcDoorTypeEnum_type), true),
            new attribute(strings[2623], new named_type(IFC4X1_IfcDoorTypeOperationEnum_type), true),
            new attribute(strings[2624], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDoorLiningProperties_type->set_attributes({
            new attribute(strings[2625], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2626], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2627], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2628], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2629], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2630], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2631], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2632], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2633], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2634], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2635], new named_type(IFC4X1_IfcShapeAspect_type), true),
            new attribute(strings[2636], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2637], new named_type(IFC4X1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDoorPanelProperties_type->set_attributes({
            new attribute(strings[2638], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2639], new named_type(IFC4X1_IfcDoorPanelOperationEnum_type), false),
            new attribute(strings[2640], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2641], new named_type(IFC4X1_IfcDoorPanelPositionEnum_type), false),
            new attribute(strings[2635], new named_type(IFC4X1_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDoorStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDoorStyle_type->set_attributes({
            new attribute(strings[2623], new named_type(IFC4X1_IfcDoorStyleOperationEnum_type), false),
            new attribute(strings[2642], new named_type(IFC4X1_IfcDoorStyleConstructionEnum_type), false),
            new attribute(strings[2643], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[2644], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDoorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDoorTypeEnum_type), false),
            new attribute(strings[2623], new named_type(IFC4X1_IfcDoorTypeOperationEnum_type), false),
            new attribute(strings[2643], new named_type(IFC4X1_IfcBoolean_type), true),
            new attribute(strings[2624], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDraughtingPreDefinedColour_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcDraughtingPreDefinedCurveFont_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcDuctFitting_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDuctFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDuctFittingType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDuctFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDuctSegment_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDuctSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDuctSegmentType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDuctSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDuctSilencer_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDuctSilencerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcDuctSilencerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcDuctSilencerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEdge_type->set_attributes({
            new attribute(strings[2645], new named_type(IFC4X1_IfcVertex_type), false),
            new attribute(strings[2646], new named_type(IFC4X1_IfcVertex_type), false)
    },{
            false, false
    });
    IFC4X1_IfcEdgeCurve_type->set_attributes({
            new attribute(strings[2647], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2527], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcEdgeLoop_type->set_attributes({
            new attribute(strings[2648], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcOrientedEdge_type)), false)
    },{
            false
    });
    IFC4X1_IfcElectricAppliance_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricApplianceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricDistributionBoard_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricDistributionBoardTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricDistributionBoardType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricDistributionBoardTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricFlowStorageDevice_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricFlowStorageDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricFlowStorageDeviceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricFlowStorageDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricGenerator_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricGeneratorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricGeneratorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricGeneratorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricMotor_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricMotorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricMotorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricMotorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricTimeControl_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricTimeControlTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElectricTimeControlType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElectricTimeControlTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElement_type->set_attributes({
            new attribute(strings[2393], new named_type(IFC4X1_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElementAssembly_type->set_attributes({
            new attribute(strings[2649], new named_type(IFC4X1_IfcAssemblyPlaceEnum_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcElementAssemblyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElementAssemblyType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcElementAssemblyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElementComponent_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElementComponentType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElementQuantity_type->set_attributes({
            new attribute(strings[2650], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2651], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPhysicalQuantity_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcElementType_type->set_attributes({
            new attribute(strings[2652], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcElementarySurface_type->set_attributes({
            new attribute(strings[2531], new named_type(IFC4X1_IfcAxis2Placement3D_type), false)
    },{
            false
    });
    IFC4X1_IfcEllipse_type->set_attributes({
            new attribute(strings[2653], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2654], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcEllipseProfileDef_type->set_attributes({
            new attribute(strings[2653], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2654], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcEnergyConversionDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEnergyConversionDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEngine_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcEngineTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEngineType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcEngineTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEvaporativeCooler_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcEvaporativeCoolerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEvaporativeCoolerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcEvaporativeCoolerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEvaporator_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcEvaporatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEvaporatorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcEvaporatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEvent_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcEventTypeEnum_type), true),
            new attribute(strings[2655], new named_type(IFC4X1_IfcEventTriggerTypeEnum_type), true),
            new attribute(strings[2656], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2657], new named_type(IFC4X1_IfcEventTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcEventTime_type->set_attributes({
            new attribute(strings[2658], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2659], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2660], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2661], new named_type(IFC4X1_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcEventType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcEventTypeEnum_type), false),
            new attribute(strings[2655], new named_type(IFC4X1_IfcEventTriggerTypeEnum_type), false),
            new attribute(strings[2656], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcExtendedProperties_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2662], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcProperty_type)), false)
    },{
            false, false, false
    });
    IFC4X1_IfcExternalInformation_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcExternalReference_type->set_attributes({
            new attribute(strings[2514], new named_type(IFC4X1_IfcURIReference_type), true),
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcExternalReferenceRelationship_type->set_attributes({
            new attribute(strings[2663], new named_type(IFC4X1_IfcExternalReference_type), false),
            new attribute(strings[2664], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcResourceObjectSelect_type)), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcExternalSpatialElement_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcExternalSpatialElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcExternalSpatialStructureElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcExternallyDefinedHatchStyle_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcExternallyDefinedSurfaceStyle_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcExternallyDefinedTextFont_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcExtrudedAreaSolid_type->set_attributes({
            new attribute(strings[2665], new named_type(IFC4X1_IfcDirection_type), false),
            new attribute(strings[2494], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcExtrudedAreaSolidTapered_type->set_attributes({
            new attribute(strings[2666], new named_type(IFC4X1_IfcProfileDef_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcFace_type->set_attributes({
            new attribute(strings[2667], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcFaceBound_type)), false)
    },{
            false
    });
    IFC4X1_IfcFaceBasedSurfaceModel_type->set_attributes({
            new attribute(strings[2668], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcConnectedFaceSet_type)), false)
    },{
            false
    });
    IFC4X1_IfcFaceBound_type->set_attributes({
            new attribute(strings[2669], new named_type(IFC4X1_IfcLoop_type), false),
            new attribute(strings[2670], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false
    });
    IFC4X1_IfcFaceOuterBound_type->set_attributes({
    },{
            false, false
    });
    IFC4X1_IfcFaceSurface_type->set_attributes({
            new attribute(strings[2671], new named_type(IFC4X1_IfcSurface_type), false),
            new attribute(strings[2527], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcFacetedBrep_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcFacetedBrepWithVoids_type->set_attributes({
            new attribute(strings[2378], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcClosedShell_type)), false)
    },{
            false, false
    });
    IFC4X1_IfcFailureConnectionCondition_type->set_attributes({
            new attribute(strings[2672], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[2673], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[2674], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[2675], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[2676], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[2677], new named_type(IFC4X1_IfcForceMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcFan_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFanTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFanType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFanTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFastener_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFastenerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFastenerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFastenerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFeatureElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFeatureElementAddition_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFeatureElementSubtraction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFillAreaStyle_type->set_attributes({
            new attribute(strings[2678], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcFillStyleSelect_type)), false),
            new attribute(strings[2679], new named_type(IFC4X1_IfcBoolean_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcFillAreaStyleHatching_type->set_attributes({
            new attribute(strings[2680], new named_type(IFC4X1_IfcCurveStyle_type), false),
            new attribute(strings[2681], new named_type(IFC4X1_IfcHatchLineDistanceSelect_type), false),
            new attribute(strings[2682], new named_type(IFC4X1_IfcCartesianPoint_type), true),
            new attribute(strings[2683], new named_type(IFC4X1_IfcCartesianPoint_type), true),
            new attribute(strings[2684], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcFillAreaStyleTiles_type->set_attributes({
            new attribute(strings[2685], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_IfcVector_type)), false),
            new attribute(strings[2686], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcStyledItem_type)), false),
            new attribute(strings[2687], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcFilter_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFilterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFilterType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFilterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFireSuppressionTerminal_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFireSuppressionTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFireSuppressionTerminalType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFireSuppressionTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFixedReferenceSweptAreaSolid_type->set_attributes({
            new attribute(strings[2688], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2689], new named_type(IFC4X1_IfcParameterValue_type), true),
            new attribute(strings[2690], new named_type(IFC4X1_IfcParameterValue_type), true),
            new attribute(strings[2691], new named_type(IFC4X1_IfcDirection_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcFlowController_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowControllerType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowFitting_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowFittingType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowInstrument_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFlowInstrumentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowInstrumentType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFlowInstrumentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowMeter_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFlowMeterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowMeterType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFlowMeterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowMovingDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowMovingDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowSegment_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowSegmentType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowStorageDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowStorageDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowTerminal_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowTerminalType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowTreatmentDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFlowTreatmentDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFooting_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFootingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFootingType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFootingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFurnishingElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFurnishingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFurniture_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcFurnitureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcFurnitureType_type->set_attributes({
            new attribute(strings[2649], new named_type(IFC4X1_IfcAssemblyPlaceEnum_type), false),
            new attribute(strings[2369], new named_type(IFC4X1_IfcFurnitureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcGeographicElement_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcGeographicElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcGeographicElementType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcGeographicElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcGeometricCurveSet_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcGeometricRepresentationContext_type->set_attributes({
            new attribute(strings[2692], new named_type(IFC4X1_IfcDimensionCount_type), false),
            new attribute(strings[2693], new named_type(IFC4X1_IfcReal_type), true),
            new attribute(strings[2694], new named_type(IFC4X1_IfcAxis2Placement_type), false),
            new attribute(strings[2695], new named_type(IFC4X1_IfcDirection_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcGeometricRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcGeometricRepresentationSubContext_type->set_attributes({
            new attribute(strings[2696], new named_type(IFC4X1_IfcGeometricRepresentationContext_type), false),
            new attribute(strings[2697], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[2698], new named_type(IFC4X1_IfcGeometricProjectionEnum_type), false),
            new attribute(strings[2699], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, true, true, true, true, false, false, false, false
    });
    IFC4X1_IfcGeometricSet_type->set_attributes({
            new attribute(strings[2587], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcGeometricSetSelect_type)), false)
    },{
            false
    });
    IFC4X1_IfcGrid_type->set_attributes({
            new attribute(strings[2700], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcGridAxis_type)), false),
            new attribute(strings[2701], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcGridAxis_type)), false),
            new attribute(strings[2702], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcGridAxis_type)), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcGridTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcGridAxis_type->set_attributes({
            new attribute(strings[2703], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2704], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2527], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcGridPlacement_type->set_attributes({
            new attribute(strings[2705], new named_type(IFC4X1_IfcVirtualGridIntersection_type), false),
            new attribute(strings[2706], new named_type(IFC4X1_IfcGridPlacementDirectionSelect_type), true)
    },{
            false, false
    });
    IFC4X1_IfcGroup_type->set_attributes({
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcHalfSpaceSolid_type->set_attributes({
            new attribute(strings[2707], new named_type(IFC4X1_IfcSurface_type), false),
            new attribute(strings[2708], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false
    });
    IFC4X1_IfcHeatExchanger_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcHeatExchangerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcHeatExchangerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcHeatExchangerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcHumidifier_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcHumidifierTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcHumidifierType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcHumidifierTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcIShapeProfileDef_type->set_attributes({
            new attribute(strings[2622], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2430], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2431], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2709], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2710], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2711], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2712], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcImageTexture_type->set_attributes({
            new attribute(strings[2713], new named_type(IFC4X1_IfcURIReference_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcIndexedColourMap_type->set_attributes({
            new attribute(strings[2714], new named_type(IFC4X1_IfcTessellatedFaceSet_type), false),
            new attribute(strings[2715], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2716], new named_type(IFC4X1_IfcColourRgbList_type), false),
            new attribute(strings[2717], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcPositiveInteger_type)), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcIndexedPolyCurve_type->set_attributes({
            new attribute(strings[2718], new named_type(IFC4X1_IfcCartesianPointList_type), false),
            new attribute(strings[2380], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcSegmentIndexSelect_type)), true),
            new attribute(strings[2447], new named_type(IFC4X1_IfcBoolean_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcIndexedPolygonalFace_type->set_attributes({
            new attribute(strings[2719], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X1_IfcPositiveInteger_type)), false)
    },{
            false
    });
    IFC4X1_IfcIndexedPolygonalFaceWithVoids_type->set_attributes({
            new attribute(strings[2720], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X1_IfcPositiveInteger_type))), false)
    },{
            false, false
    });
    IFC4X1_IfcIndexedTextureMap_type->set_attributes({
            new attribute(strings[2714], new named_type(IFC4X1_IfcTessellatedFaceSet_type), false),
            new attribute(strings[2721], new named_type(IFC4X1_IfcTextureVertexList_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcIndexedTriangleTextureMap_type->set_attributes({
            new attribute(strings[2722], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_IfcPositiveInteger_type))), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcInterceptor_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcInterceptorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcInterceptorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcInterceptorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcIntersectionCurve_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcInventory_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcInventoryTypeEnum_type), true),
            new attribute(strings[2723], new named_type(IFC4X1_IfcActorSelect_type), true),
            new attribute(strings[2724], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPerson_type)), true),
            new attribute(strings[2725], new named_type(IFC4X1_IfcDate_type), true),
            new attribute(strings[2422], new named_type(IFC4X1_IfcCostValue_type), true),
            new attribute(strings[2421], new named_type(IFC4X1_IfcCostValue_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcIrregularTimeSeries_type->set_attributes({
            new attribute(strings[2726], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcIrregularTimeSeriesValue_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcIrregularTimeSeriesValue_type->set_attributes({
            new attribute(strings[2727], new named_type(IFC4X1_IfcDateTime_type), false),
            new attribute(strings[2728], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcValue_type)), false)
    },{
            false, false
    });
    IFC4X1_IfcJunctionBox_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcJunctionBoxTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcJunctionBoxType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcJunctionBoxTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLShapeProfileDef_type->set_attributes({
            new attribute(strings[2494], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2495], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2509], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2710], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2729], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2730], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLaborResource_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcLaborResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLaborResourceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcLaborResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLagTime_type->set_attributes({
            new attribute(strings[2731], new named_type(IFC4X1_IfcTimeOrRatioSelect_type), false),
            new attribute(strings[2732], new named_type(IFC4X1_IfcTaskDurationEnum_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcLamp_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcLampTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLampType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcLampTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLibraryInformation_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2397], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2733], new named_type(IFC4X1_IfcActorSelect_type), true),
            new attribute(strings[2734], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[2514], new named_type(IFC4X1_IfcURIReference_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcLibraryReference_type->set_attributes({
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2735], new named_type(IFC4X1_IfcLanguageId_type), true),
            new attribute(strings[2736], new named_type(IFC4X1_IfcLibraryInformation_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcLightDistributionData_type->set_attributes({
            new attribute(strings[2737], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), false),
            new attribute(strings[2738], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcPlaneAngleMeasure_type)), false),
            new attribute(strings[2739], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLuminousIntensityDistributionMeasure_type)), false)
    },{
            false, false, false
    });
    IFC4X1_IfcLightFixture_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcLightFixtureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLightFixtureType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcLightFixtureTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLightIntensityDistribution_type->set_attributes({
            new attribute(strings[2740], new named_type(IFC4X1_IfcLightDistributionCurveEnum_type), false),
            new attribute(strings[2741], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLightDistributionData_type)), false)
    },{
            false, false
    });
    IFC4X1_IfcLightSource_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2742], new named_type(IFC4X1_IfcColourRgb_type), false),
            new attribute(strings[2743], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2744], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcLightSourceAmbient_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcLightSourceDirectional_type->set_attributes({
            new attribute(strings[2670], new named_type(IFC4X1_IfcDirection_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcLightSourceGoniometric_type->set_attributes({
            new attribute(strings[2531], new named_type(IFC4X1_IfcAxis2Placement3D_type), false),
            new attribute(strings[2745], new named_type(IFC4X1_IfcColourRgb_type), true),
            new attribute(strings[2746], new named_type(IFC4X1_IfcThermodynamicTemperatureMeasure_type), false),
            new attribute(strings[2747], new named_type(IFC4X1_IfcLuminousFluxMeasure_type), false),
            new attribute(strings[2748], new named_type(IFC4X1_IfcLightEmissionSourceEnum_type), false),
            new attribute(strings[2749], new named_type(IFC4X1_IfcLightDistributionDataSourceSelect_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLightSourcePositional_type->set_attributes({
            new attribute(strings[2531], new named_type(IFC4X1_IfcCartesianPoint_type), false),
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2750], new named_type(IFC4X1_IfcReal_type), false),
            new attribute(strings[2751], new named_type(IFC4X1_IfcReal_type), false),
            new attribute(strings[2752], new named_type(IFC4X1_IfcReal_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLightSourceSpot_type->set_attributes({
            new attribute(strings[2670], new named_type(IFC4X1_IfcDirection_type), false),
            new attribute(strings[2753], new named_type(IFC4X1_IfcReal_type), true),
            new attribute(strings[2754], new named_type(IFC4X1_IfcPositivePlaneAngleMeasure_type), false),
            new attribute(strings[2755], new named_type(IFC4X1_IfcPositivePlaneAngleMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLine_type->set_attributes({
            new attribute(strings[2756], new named_type(IFC4X1_IfcCartesianPoint_type), false),
            new attribute(strings[2757], new named_type(IFC4X1_IfcVector_type), false)
    },{
            false, false
    });
    IFC4X1_IfcLineSegment2D_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcLinearPlacement_type->set_attributes({
            new attribute(strings[2758], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2759], new named_type(IFC4X1_IfcDistanceExpression_type), false),
            new attribute(strings[2670], new named_type(IFC4X1_IfcOrientationExpression_type), true),
            new attribute(strings[2760], new named_type(IFC4X1_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcLinearPositioningElement_type->set_attributes({
            new attribute(strings[2441], new named_type(IFC4X1_IfcCurve_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcLocalPlacement_type->set_attributes({
            new attribute(strings[2758], new named_type(IFC4X1_IfcObjectPlacement_type), true),
            new attribute(strings[2761], new named_type(IFC4X1_IfcAxis2Placement_type), false)
    },{
            false, false
    });
    IFC4X1_IfcLoop_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcManifoldSolidBrep_type->set_attributes({
            new attribute(strings[2762], new named_type(IFC4X1_IfcClosedShell_type), false)
    },{
            false
    });
    IFC4X1_IfcMapConversion_type->set_attributes({
            new attribute(strings[2763], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2764], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2765], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2766], new named_type(IFC4X1_IfcReal_type), true),
            new attribute(strings[2767], new named_type(IFC4X1_IfcReal_type), true),
            new attribute(strings[2505], new named_type(IFC4X1_IfcReal_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMappedItem_type->set_attributes({
            new attribute(strings[2768], new named_type(IFC4X1_IfcRepresentationMap_type), false),
            new attribute(strings[2769], new named_type(IFC4X1_IfcCartesianTransformationOperator_type), false)
    },{
            false, false
    });
    IFC4X1_IfcMaterial_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2405], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcMaterialClassificationRelationship_type->set_attributes({
            new attribute(strings[2770], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcClassificationSelect_type)), false),
            new attribute(strings[2771], new named_type(IFC4X1_IfcMaterial_type), false)
    },{
            false, false
    });
    IFC4X1_IfcMaterialConstituent_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2772], new named_type(IFC4X1_IfcMaterial_type), false),
            new attribute(strings[2773], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2405], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcMaterialConstituentSet_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2774], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcMaterialConstituent_type)), true)
    },{
            false, false, false
    });
    IFC4X1_IfcMaterialDefinition_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcMaterialDefinitionRepresentation_type->set_attributes({
            new attribute(strings[2775], new named_type(IFC4X1_IfcMaterial_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcMaterialLayer_type->set_attributes({
            new attribute(strings[2772], new named_type(IFC4X1_IfcMaterial_type), true),
            new attribute(strings[2776], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[2777], new named_type(IFC4X1_IfcLogical_type), true),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2405], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2778], new named_type(IFC4X1_IfcInteger_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcMaterialLayerSet_type->set_attributes({
            new attribute(strings[2779], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcMaterialLayer_type)), false),
            new attribute(strings[2780], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcMaterialLayerSetUsage_type->set_attributes({
            new attribute(strings[2781], new named_type(IFC4X1_IfcMaterialLayerSet_type), false),
            new attribute(strings[2782], new named_type(IFC4X1_IfcLayerSetDirectionEnum_type), false),
            new attribute(strings[2783], new named_type(IFC4X1_IfcDirectionSenseEnum_type), false),
            new attribute(strings[2784], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2785], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcMaterialLayerWithOffsets_type->set_attributes({
            new attribute(strings[2786], new named_type(IFC4X1_IfcLayerSetDirectionEnum_type), false),
            new attribute(strings[2787], new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X1_IfcLengthMeasure_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMaterialList_type->set_attributes({
            new attribute(strings[2788], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcMaterial_type)), false)
    },{
            false
    });
    IFC4X1_IfcMaterialProfile_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2772], new named_type(IFC4X1_IfcMaterial_type), true),
            new attribute(strings[2789], new named_type(IFC4X1_IfcProfileDef_type), false),
            new attribute(strings[2778], new named_type(IFC4X1_IfcInteger_type), true),
            new attribute(strings[2405], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcMaterialProfileSet_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2790], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcMaterialProfile_type)), false),
            new attribute(strings[2791], new named_type(IFC4X1_IfcCompositeProfileDef_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcMaterialProfileSetUsage_type->set_attributes({
            new attribute(strings[2792], new named_type(IFC4X1_IfcMaterialProfileSet_type), false),
            new attribute(strings[2793], new named_type(IFC4X1_IfcCardinalPointReference_type), true),
            new attribute(strings[2785], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcMaterialProfileSetUsageTapering_type->set_attributes({
            new attribute(strings[2794], new named_type(IFC4X1_IfcMaterialProfileSet_type), false),
            new attribute(strings[2795], new named_type(IFC4X1_IfcCardinalPointReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcMaterialProfileWithOffsets_type->set_attributes({
            new attribute(strings[2787], new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X1_IfcLengthMeasure_type)), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcMaterialProperties_type->set_attributes({
            new attribute(strings[2772], new named_type(IFC4X1_IfcMaterialDefinition_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcMaterialRelationship_type->set_attributes({
            new attribute(strings[2796], new named_type(IFC4X1_IfcMaterial_type), false),
            new attribute(strings[2797], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcMaterial_type)), false),
            new attribute(strings[2798], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcMaterialUsageDefinition_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcMeasureWithUnit_type->set_attributes({
            new attribute(strings[2799], new named_type(IFC4X1_IfcValue_type), false),
            new attribute(strings[2800], new named_type(IFC4X1_IfcUnit_type), false)
    },{
            false, false
    });
    IFC4X1_IfcMechanicalFastener_type->set_attributes({
            new attribute(strings[2801], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2802], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcMechanicalFastenerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMechanicalFastenerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcMechanicalFastenerTypeEnum_type), false),
            new attribute(strings[2801], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2802], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMedicalDevice_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcMedicalDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMedicalDeviceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcMedicalDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMember_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcMemberTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMemberStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMemberType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcMemberTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMetric_type->set_attributes({
            new attribute(strings[2803], new named_type(IFC4X1_IfcBenchmarkEnum_type), false),
            new attribute(strings[2804], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2805], new named_type(IFC4X1_IfcMetricValueSelect_type), true),
            new attribute(strings[2806], new named_type(IFC4X1_IfcReference_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMirroredProfileDef_type->set_attributes({
    },{
            false, false, false, true, false
    });
    IFC4X1_IfcMonetaryUnit_type->set_attributes({
            new attribute(strings[2807], new named_type(IFC4X1_IfcLabel_type), false)
    },{
            false
    });
    IFC4X1_IfcMotorConnection_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcMotorConnectionTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcMotorConnectionType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcMotorConnectionTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcNamedUnit_type->set_attributes({
            new attribute(strings[2808], new named_type(IFC4X1_IfcDimensionalExponents_type), false),
            new attribute(strings[2588], new named_type(IFC4X1_IfcUnitEnum_type), false)
    },{
            false, false
    });
    IFC4X1_IfcObject_type->set_attributes({
            new attribute(strings[2552], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcObjectDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcObjectPlacement_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcObjective_type->set_attributes({
            new attribute(strings[2809], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcConstraint_type)), true),
            new attribute(strings[2810], new named_type(IFC4X1_IfcLogicalOperatorEnum_type), true),
            new attribute(strings[2811], new named_type(IFC4X1_IfcObjectiveEnum_type), false),
            new attribute(strings[2812], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcOccupant_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcOccupantTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcOffsetCurve_type->set_attributes({
            new attribute(strings[2813], new named_type(IFC4X1_IfcCurve_type), false)
    },{
            false
    });
    IFC4X1_IfcOffsetCurve2D_type->set_attributes({
            new attribute(strings[2759], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2447], new named_type(IFC4X1_IfcLogical_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcOffsetCurve3D_type->set_attributes({
            new attribute(strings[2759], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2447], new named_type(IFC4X1_IfcLogical_type), false),
            new attribute(strings[2442], new named_type(IFC4X1_IfcDirection_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcOffsetCurveByDistances_type->set_attributes({
            new attribute(strings[2787], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcDistanceExpression_type)), false),
            new attribute(strings[2393], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcOpenShell_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcOpeningElement_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcOpeningElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcOpeningStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcOrganization_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2814], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcActorRole_type)), true),
            new attribute(strings[2815], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcAddress_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcOrganizationRelationship_type->set_attributes({
            new attribute(strings[2816], new named_type(IFC4X1_IfcOrganization_type), false),
            new attribute(strings[2817], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcOrganization_type)), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcOrientationExpression_type->set_attributes({
            new attribute(strings[2818], new named_type(IFC4X1_IfcDirection_type), false),
            new attribute(strings[2819], new named_type(IFC4X1_IfcDirection_type), false)
    },{
            false, false
    });
    IFC4X1_IfcOrientedEdge_type->set_attributes({
            new attribute(strings[2820], new named_type(IFC4X1_IfcEdge_type), false),
            new attribute(strings[2670], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            true, true, false, false
    });
    IFC4X1_IfcOuterBoundaryCurve_type->set_attributes({
    },{
            false, false
    });
    IFC4X1_IfcOutlet_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcOutletTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcOutletType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcOutletTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcOwnerHistory_type->set_attributes({
            new attribute(strings[2821], new named_type(IFC4X1_IfcPersonAndOrganization_type), false),
            new attribute(strings[2822], new named_type(IFC4X1_IfcApplication_type), false),
            new attribute(strings[2823], new named_type(IFC4X1_IfcStateEnum_type), true),
            new attribute(strings[2824], new named_type(IFC4X1_IfcChangeActionEnum_type), true),
            new attribute(strings[2825], new named_type(IFC4X1_IfcTimeStamp_type), true),
            new attribute(strings[2826], new named_type(IFC4X1_IfcPersonAndOrganization_type), true),
            new attribute(strings[2827], new named_type(IFC4X1_IfcApplication_type), true),
            new attribute(strings[2828], new named_type(IFC4X1_IfcTimeStamp_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcParameterizedProfileDef_type->set_attributes({
            new attribute(strings[2531], new named_type(IFC4X1_IfcAxis2Placement2D_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcPath_type->set_attributes({
            new attribute(strings[2648], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcOrientedEdge_type)), false)
    },{
            false
    });
    IFC4X1_IfcPcurve_type->set_attributes({
            new attribute(strings[2572], new named_type(IFC4X1_IfcSurface_type), false),
            new attribute(strings[2829], new named_type(IFC4X1_IfcCurve_type), false)
    },{
            false, false
    });
    IFC4X1_IfcPerformanceHistory_type->set_attributes({
            new attribute(strings[2830], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2369], new named_type(IFC4X1_IfcPerformanceHistoryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPermeableCoveringProperties_type->set_attributes({
            new attribute(strings[2623], new named_type(IFC4X1_IfcPermeableCoveringOperationEnum_type), false),
            new attribute(strings[2641], new named_type(IFC4X1_IfcWindowPanelPositionEnum_type), false),
            new attribute(strings[2831], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2832], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2635], new named_type(IFC4X1_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPermit_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPermitTypeEnum_type), true),
            new attribute(strings[2370], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2371], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPerson_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2833], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2834], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2835], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true),
            new attribute(strings[2836], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true),
            new attribute(strings[2837], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true),
            new attribute(strings[2814], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcActorRole_type)), true),
            new attribute(strings[2815], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcAddress_type)), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPersonAndOrganization_type->set_attributes({
            new attribute(strings[2838], new named_type(IFC4X1_IfcPerson_type), false),
            new attribute(strings[2839], new named_type(IFC4X1_IfcOrganization_type), false),
            new attribute(strings[2814], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcActorRole_type)), true)
    },{
            false, false, false
    });
    IFC4X1_IfcPhysicalComplexQuantity_type->set_attributes({
            new attribute(strings[2840], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPhysicalQuantity_type)), false),
            new attribute(strings[2841], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2842], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2549], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcPhysicalQuantity_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false
    });
    IFC4X1_IfcPhysicalSimpleQuantity_type->set_attributes({
            new attribute(strings[2590], new named_type(IFC4X1_IfcNamedUnit_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcPile_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPileTypeEnum_type), true),
            new attribute(strings[2642], new named_type(IFC4X1_IfcPileConstructionEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPileType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPileTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPipeFitting_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPipeFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPipeFittingType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPipeFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPipeSegment_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPipeSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPipeSegmentType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPipeSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPixelTexture_type->set_attributes({
            new attribute(strings[2495], new named_type(IFC4X1_IfcInteger_type), false),
            new attribute(strings[2843], new named_type(IFC4X1_IfcInteger_type), false),
            new attribute(strings[2844], new named_type(IFC4X1_IfcInteger_type), false),
            new attribute(strings[2845], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcBinary_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPlacement_type->set_attributes({
            new attribute(strings[2514], new named_type(IFC4X1_IfcCartesianPoint_type), false)
    },{
            false
    });
    IFC4X1_IfcPlanarBox_type->set_attributes({
            new attribute(strings[2846], new named_type(IFC4X1_IfcAxis2Placement_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcPlanarExtent_type->set_attributes({
            new attribute(strings[2847], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2848], new named_type(IFC4X1_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X1_IfcPlane_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcPlate_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPlateTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPlateStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPlateType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPlateTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPoint_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcPointOnCurve_type->set_attributes({
            new attribute(strings[2813], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2849], new named_type(IFC4X1_IfcParameterValue_type), false)
    },{
            false, false
    });
    IFC4X1_IfcPointOnSurface_type->set_attributes({
            new attribute(strings[2572], new named_type(IFC4X1_IfcSurface_type), false),
            new attribute(strings[2850], new named_type(IFC4X1_IfcParameterValue_type), false),
            new attribute(strings[2851], new named_type(IFC4X1_IfcParameterValue_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcPolyLoop_type->set_attributes({
            new attribute(strings[2852], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X1_IfcCartesianPoint_type)), false)
    },{
            false
    });
    IFC4X1_IfcPolygonalBoundedHalfSpace_type->set_attributes({
            new attribute(strings[2531], new named_type(IFC4X1_IfcAxis2Placement3D_type), false),
            new attribute(strings[2853], new named_type(IFC4X1_IfcBoundedCurve_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcPolygonalFaceSet_type->set_attributes({
            new attribute(strings[2854], new named_type(IFC4X1_IfcBoolean_type), true),
            new attribute(strings[2855], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcIndexedPolygonalFace_type)), false),
            new attribute(strings[2856], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcPositiveInteger_type)), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcPolyline_type->set_attributes({
            new attribute(strings[2718], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcCartesianPoint_type)), false)
    },{
            false
    });
    IFC4X1_IfcPort_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcPositioningElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcPostalAddress_type->set_attributes({
            new attribute(strings[2857], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2858], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true),
            new attribute(strings[2859], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2860], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2862], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2863], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPreDefinedColour_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcPreDefinedCurveFont_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcPreDefinedItem_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false)
    },{
            false
    });
    IFC4X1_IfcPreDefinedProperties_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcPreDefinedPropertySet_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcPreDefinedTextFont_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcPresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcPresentationLayerAssignment_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2864], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcLayeredItem_type)), false),
            new attribute(strings[2409], new named_type(IFC4X1_IfcIdentifier_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcPresentationLayerWithStyle_type->set_attributes({
            new attribute(strings[2865], new named_type(IFC4X1_IfcLogical_type), false),
            new attribute(strings[2866], new named_type(IFC4X1_IfcLogical_type), false),
            new attribute(strings[2867], new named_type(IFC4X1_IfcLogical_type), false),
            new attribute(strings[2868], new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X1_IfcPresentationStyle_type)), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPresentationStyle_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X1_IfcPresentationStyleAssignment_type->set_attributes({
            new attribute(strings[2869], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPresentationStyleSelect_type)), false)
    },{
            false
    });
    IFC4X1_IfcProcedure_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcProcedureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProcedureType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcProcedureTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProcess_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2371], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcProduct_type->set_attributes({
            new attribute(strings[2870], new named_type(IFC4X1_IfcObjectPlacement_type), true),
            new attribute(strings[2871], new named_type(IFC4X1_IfcProductRepresentation_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcProductDefinitionShape_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcProductRepresentation_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2872], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcRepresentation_type)), false)
    },{
            false, false, false
    });
    IFC4X1_IfcProfileDef_type->set_attributes({
            new attribute(strings[2873], new named_type(IFC4X1_IfcProfileTypeEnum_type), false),
            new attribute(strings[2874], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4X1_IfcProfileProperties_type->set_attributes({
            new attribute(strings[2875], new named_type(IFC4X1_IfcProfileDef_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcProject_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProjectLibrary_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProjectOrder_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcProjectOrderTypeEnum_type), true),
            new attribute(strings[2370], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2371], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProjectedCRS_type->set_attributes({
            new attribute(strings[2876], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2877], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2878], new named_type(IFC4X1_IfcNamedUnit_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcProjectionElement_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcProjectionElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProperty_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcIdentifier_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false
    });
    IFC4X1_IfcPropertyAbstraction_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcPropertyBoundedValue_type->set_attributes({
            new attribute(strings[2879], new named_type(IFC4X1_IfcValue_type), true),
            new attribute(strings[2880], new named_type(IFC4X1_IfcValue_type), true),
            new attribute(strings[2590], new named_type(IFC4X1_IfcUnit_type), true),
            new attribute(strings[2881], new named_type(IFC4X1_IfcValue_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcPropertyDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcPropertyDependencyRelationship_type->set_attributes({
            new attribute(strings[2882], new named_type(IFC4X1_IfcProperty_type), false),
            new attribute(strings[2883], new named_type(IFC4X1_IfcProperty_type), false),
            new attribute(strings[2798], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcPropertyEnumeratedValue_type->set_attributes({
            new attribute(strings[2884], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcValue_type)), true),
            new attribute(strings[2885], new named_type(IFC4X1_IfcPropertyEnumeration_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcPropertyEnumeration_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2884], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcValue_type)), false),
            new attribute(strings[2590], new named_type(IFC4X1_IfcUnit_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcPropertyListValue_type->set_attributes({
            new attribute(strings[2728], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcValue_type)), true),
            new attribute(strings[2590], new named_type(IFC4X1_IfcUnit_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcPropertyReferenceValue_type->set_attributes({
            new attribute(strings[2522], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2886], new named_type(IFC4X1_IfcObjectReferenceSelect_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcPropertySet_type->set_attributes({
            new attribute(strings[2523], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcProperty_type)), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcPropertySetDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcPropertySetTemplate_type->set_attributes({
            new attribute(strings[2524], new named_type(IFC4X1_IfcPropertySetTemplateTypeEnum_type), true),
            new attribute(strings[2887], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2525], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPropertyTemplate_type)), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcPropertySingleValue_type->set_attributes({
            new attribute(strings[2888], new named_type(IFC4X1_IfcValue_type), true),
            new attribute(strings[2590], new named_type(IFC4X1_IfcUnit_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcPropertyTableValue_type->set_attributes({
            new attribute(strings[2889], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcValue_type)), true),
            new attribute(strings[2890], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcValue_type)), true),
            new attribute(strings[2798], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2891], new named_type(IFC4X1_IfcUnit_type), true),
            new attribute(strings[2892], new named_type(IFC4X1_IfcUnit_type), true),
            new attribute(strings[2893], new named_type(IFC4X1_IfcCurveInterpolationEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPropertyTemplate_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcPropertyTemplateDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcProtectiveDevice_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcProtectiveDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProtectiveDeviceTrippingUnit_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcProtectiveDeviceTrippingUnitTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProtectiveDeviceTrippingUnitType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcProtectiveDeviceTrippingUnitTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProtectiveDeviceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcProtectiveDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcProxy_type->set_attributes({
            new attribute(strings[2894], new named_type(IFC4X1_IfcObjectTypeEnum_type), false),
            new attribute(strings[2393], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPump_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPumpTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcPumpType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcPumpTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcQuantityArea_type->set_attributes({
            new attribute(strings[2895], new named_type(IFC4X1_IfcAreaMeasure_type), false),
            new attribute(strings[2896], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcQuantityCount_type->set_attributes({
            new attribute(strings[2897], new named_type(IFC4X1_IfcCountMeasure_type), false),
            new attribute(strings[2896], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcQuantityLength_type->set_attributes({
            new attribute(strings[2898], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[2896], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcQuantitySet_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcQuantityTime_type->set_attributes({
            new attribute(strings[2899], new named_type(IFC4X1_IfcTimeMeasure_type), false),
            new attribute(strings[2896], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcQuantityVolume_type->set_attributes({
            new attribute(strings[2900], new named_type(IFC4X1_IfcVolumeMeasure_type), false),
            new attribute(strings[2896], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcQuantityWeight_type->set_attributes({
            new attribute(strings[2901], new named_type(IFC4X1_IfcMassMeasure_type), false),
            new attribute(strings[2896], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcRailing_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcRailingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRailingType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcRailingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRamp_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcRampTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRampFlight_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcRampFlightTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRampFlightType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcRampFlightTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRampType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcRampTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRationalBSplineCurveWithKnots_type->set_attributes({
            new attribute(strings[2902], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcReal_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRationalBSplineSurfaceWithKnots_type->set_attributes({
            new attribute(strings[2902], new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcReal_type))), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRectangleHollowProfileDef_type->set_attributes({
            new attribute(strings[2496], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2903], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2904], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRectangleProfileDef_type->set_attributes({
            new attribute(strings[2485], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2486], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcRectangularPyramid_type->set_attributes({
            new attribute(strings[2462], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2463], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2843], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcRectangularTrimmedSurface_type->set_attributes({
            new attribute(strings[2572], new named_type(IFC4X1_IfcSurface_type), false),
            new attribute(strings[2905], new named_type(IFC4X1_IfcParameterValue_type), false),
            new attribute(strings[2906], new named_type(IFC4X1_IfcParameterValue_type), false),
            new attribute(strings[2907], new named_type(IFC4X1_IfcParameterValue_type), false),
            new attribute(strings[2908], new named_type(IFC4X1_IfcParameterValue_type), false),
            new attribute(strings[2909], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[2910], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcRecurrencePattern_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X1_IfcRecurrenceTypeEnum_type), false),
            new attribute(strings[2912], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcDayInMonthNumber_type)), true),
            new attribute(strings[2913], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcDayInWeekNumber_type)), true),
            new attribute(strings[2914], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcMonthInYearNumber_type)), true),
            new attribute(strings[2531], new named_type(IFC4X1_IfcInteger_type), true),
            new attribute(strings[2915], new named_type(IFC4X1_IfcInteger_type), true),
            new attribute(strings[2916], new named_type(IFC4X1_IfcInteger_type), true),
            new attribute(strings[2917], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcTimePeriod_type)), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcReference_type->set_attributes({
            new attribute(strings[2918], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2919], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2920], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2921], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcInteger_type)), true),
            new attribute(strings[2922], new named_type(IFC4X1_IfcReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcReferent_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcReferentTypeEnum_type), true),
            new attribute(strings[2923], new named_type(IFC4X1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRegularTimeSeries_type->set_attributes({
            new attribute(strings[2924], new named_type(IFC4X1_IfcTimeMeasure_type), false),
            new attribute(strings[2726], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcTimeSeriesValue_type)), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcReinforcementBarProperties_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X1_IfcAreaMeasure_type), false),
            new attribute(strings[2926], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2927], new named_type(IFC4X1_IfcReinforcingBarSurfaceEnum_type), true),
            new attribute(strings[2928], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2929], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2930], new named_type(IFC4X1_IfcCountMeasure_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcReinforcementDefinitionProperties_type->set_attributes({
            new attribute(strings[2931], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2932], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcSectionReinforcementProperties_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcReinforcingBar_type->set_attributes({
            new attribute(strings[2801], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2933], new named_type(IFC4X1_IfcAreaMeasure_type), true),
            new attribute(strings[2934], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcReinforcingBarTypeEnum_type), true),
            new attribute(strings[2927], new named_type(IFC4X1_IfcReinforcingBarSurfaceEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcReinforcingBarType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcReinforcingBarTypeEnum_type), false),
            new attribute(strings[2801], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2933], new named_type(IFC4X1_IfcAreaMeasure_type), true),
            new attribute(strings[2934], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2927], new named_type(IFC4X1_IfcReinforcingBarSurfaceEnum_type), true),
            new attribute(strings[2935], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2936], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcBendingParameterSelect_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcReinforcingElement_type->set_attributes({
            new attribute(strings[2926], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcReinforcingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcReinforcingMesh_type->set_attributes({
            new attribute(strings[2937], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2938], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2939], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2940], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2941], new named_type(IFC4X1_IfcAreaMeasure_type), true),
            new attribute(strings[2942], new named_type(IFC4X1_IfcAreaMeasure_type), true),
            new attribute(strings[2943], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2944], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcReinforcingMeshTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcReinforcingMeshType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcReinforcingMeshTypeEnum_type), false),
            new attribute(strings[2937], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2938], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2939], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2940], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2941], new named_type(IFC4X1_IfcAreaMeasure_type), true),
            new attribute(strings[2942], new named_type(IFC4X1_IfcAreaMeasure_type), true),
            new attribute(strings[2943], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2944], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2935], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2936], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcBendingParameterSelect_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAggregates_type->set_attributes({
            new attribute(strings[2945], new named_type(IFC4X1_IfcObjectDefinition_type), false),
            new attribute(strings[2946], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcObjectDefinition_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssigns_type->set_attributes({
            new attribute(strings[2946], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcObjectDefinition_type)), false),
            new attribute(strings[2947], new named_type(IFC4X1_IfcObjectTypeEnum_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssignsToActor_type->set_attributes({
            new attribute(strings[2948], new named_type(IFC4X1_IfcActor_type), false),
            new attribute(strings[2949], new named_type(IFC4X1_IfcActorRole_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssignsToControl_type->set_attributes({
            new attribute(strings[2950], new named_type(IFC4X1_IfcControl_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssignsToGroup_type->set_attributes({
            new attribute(strings[2951], new named_type(IFC4X1_IfcGroup_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssignsToGroupByFactor_type->set_attributes({
            new attribute(strings[2952], new named_type(IFC4X1_IfcRatioMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssignsToProcess_type->set_attributes({
            new attribute(strings[2953], new named_type(IFC4X1_IfcProcessSelect_type), false),
            new attribute(strings[2954], new named_type(IFC4X1_IfcMeasureWithUnit_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssignsToProduct_type->set_attributes({
            new attribute(strings[2955], new named_type(IFC4X1_IfcProductSelect_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssignsToResource_type->set_attributes({
            new attribute(strings[2956], new named_type(IFC4X1_IfcResourceSelect_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssociates_type->set_attributes({
            new attribute(strings[2946], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcDefinitionSelect_type)), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcRelAssociatesApproval_type->set_attributes({
            new attribute(strings[2415], new named_type(IFC4X1_IfcApproval_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssociatesClassification_type->set_attributes({
            new attribute(strings[2957], new named_type(IFC4X1_IfcClassificationSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssociatesConstraint_type->set_attributes({
            new attribute(strings[2958], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2959], new named_type(IFC4X1_IfcConstraint_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssociatesDocument_type->set_attributes({
            new attribute(strings[2617], new named_type(IFC4X1_IfcDocumentSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssociatesLibrary_type->set_attributes({
            new attribute(strings[2960], new named_type(IFC4X1_IfcLibrarySelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelAssociatesMaterial_type->set_attributes({
            new attribute(strings[2796], new named_type(IFC4X1_IfcMaterialSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelConnects_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcRelConnectsElements_type->set_attributes({
            new attribute(strings[2961], new named_type(IFC4X1_IfcConnectionGeometry_type), true),
            new attribute(strings[2962], new named_type(IFC4X1_IfcElement_type), false),
            new attribute(strings[2963], new named_type(IFC4X1_IfcElement_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelConnectsPathElements_type->set_attributes({
            new attribute(strings[2964], new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X1_IfcInteger_type)), false),
            new attribute(strings[2965], new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X1_IfcInteger_type)), false),
            new attribute(strings[2966], new named_type(IFC4X1_IfcConnectionTypeEnum_type), false),
            new attribute(strings[2967], new named_type(IFC4X1_IfcConnectionTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelConnectsPortToElement_type->set_attributes({
            new attribute(strings[2968], new named_type(IFC4X1_IfcPort_type), false),
            new attribute(strings[2963], new named_type(IFC4X1_IfcDistributionElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelConnectsPorts_type->set_attributes({
            new attribute(strings[2968], new named_type(IFC4X1_IfcPort_type), false),
            new attribute(strings[2969], new named_type(IFC4X1_IfcPort_type), false),
            new attribute(strings[2970], new named_type(IFC4X1_IfcElement_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelConnectsStructuralActivity_type->set_attributes({
            new attribute(strings[2962], new named_type(IFC4X1_IfcStructuralActivityAssignmentSelect_type), false),
            new attribute(strings[2971], new named_type(IFC4X1_IfcStructuralActivity_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelConnectsStructuralMember_type->set_attributes({
            new attribute(strings[2972], new named_type(IFC4X1_IfcStructuralMember_type), false),
            new attribute(strings[2973], new named_type(IFC4X1_IfcStructuralConnection_type), false),
            new attribute(strings[2974], new named_type(IFC4X1_IfcBoundaryCondition_type), true),
            new attribute(strings[2975], new named_type(IFC4X1_IfcStructuralConnectionCondition_type), true),
            new attribute(strings[2976], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2977], new named_type(IFC4X1_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelConnectsWithEccentricity_type->set_attributes({
            new attribute(strings[2978], new named_type(IFC4X1_IfcConnectionGeometry_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelConnectsWithRealizingElements_type->set_attributes({
            new attribute(strings[2979], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcElement_type)), false),
            new attribute(strings[2980], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelContainedInSpatialStructure_type->set_attributes({
            new attribute(strings[2981], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcProduct_type)), false),
            new attribute(strings[2982], new named_type(IFC4X1_IfcSpatialElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelCoversBldgElements_type->set_attributes({
            new attribute(strings[2983], new named_type(IFC4X1_IfcElement_type), false),
            new attribute(strings[2984], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcCovering_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelCoversSpaces_type->set_attributes({
            new attribute(strings[2985], new named_type(IFC4X1_IfcSpace_type), false),
            new attribute(strings[2984], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcCovering_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelDeclares_type->set_attributes({
            new attribute(strings[2986], new named_type(IFC4X1_IfcContext_type), false),
            new attribute(strings[2987], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcDefinitionSelect_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelDecomposes_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcRelDefines_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcRelDefinesByObject_type->set_attributes({
            new attribute(strings[2946], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcObject_type)), false),
            new attribute(strings[2945], new named_type(IFC4X1_IfcObject_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelDefinesByProperties_type->set_attributes({
            new attribute(strings[2946], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcObjectDefinition_type)), false),
            new attribute(strings[2988], new named_type(IFC4X1_IfcPropertySetDefinitionSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelDefinesByTemplate_type->set_attributes({
            new attribute(strings[2989], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPropertySetDefinition_type)), false),
            new attribute(strings[2990], new named_type(IFC4X1_IfcPropertySetTemplate_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelDefinesByType_type->set_attributes({
            new attribute(strings[2946], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcObject_type)), false),
            new attribute(strings[2991], new named_type(IFC4X1_IfcTypeObject_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelFillsElement_type->set_attributes({
            new attribute(strings[2992], new named_type(IFC4X1_IfcOpeningElement_type), false),
            new attribute(strings[2993], new named_type(IFC4X1_IfcElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelFlowControlElements_type->set_attributes({
            new attribute(strings[2994], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcDistributionControlElement_type)), false),
            new attribute(strings[2995], new named_type(IFC4X1_IfcDistributionFlowElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelInterferesElements_type->set_attributes({
            new attribute(strings[2962], new named_type(IFC4X1_IfcElement_type), false),
            new attribute(strings[2963], new named_type(IFC4X1_IfcElement_type), false),
            new attribute(strings[2996], new named_type(IFC4X1_IfcConnectionGeometry_type), true),
            new attribute(strings[2997], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2998], new simple_type(simple_type::logical_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelNests_type->set_attributes({
            new attribute(strings[2945], new named_type(IFC4X1_IfcObjectDefinition_type), false),
            new attribute(strings[2946], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcObjectDefinition_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelProjectsElement_type->set_attributes({
            new attribute(strings[2962], new named_type(IFC4X1_IfcElement_type), false),
            new attribute(strings[2999], new named_type(IFC4X1_IfcFeatureElementAddition_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelReferencedInSpatialStructure_type->set_attributes({
            new attribute(strings[2981], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcProduct_type)), false),
            new attribute(strings[2982], new named_type(IFC4X1_IfcSpatialElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelSequence_type->set_attributes({
            new attribute(strings[2953], new named_type(IFC4X1_IfcProcess_type), false),
            new attribute(strings[3000], new named_type(IFC4X1_IfcProcess_type), false),
            new attribute(strings[3001], new named_type(IFC4X1_IfcLagTime_type), true),
            new attribute(strings[3002], new named_type(IFC4X1_IfcSequenceEnum_type), true),
            new attribute(strings[3003], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelServicesBuildings_type->set_attributes({
            new attribute(strings[3004], new named_type(IFC4X1_IfcSystem_type), false),
            new attribute(strings[3005], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcSpatialElement_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelSpaceBoundary_type->set_attributes({
            new attribute(strings[2985], new named_type(IFC4X1_IfcSpaceBoundarySelect_type), false),
            new attribute(strings[2993], new named_type(IFC4X1_IfcElement_type), false),
            new attribute(strings[2961], new named_type(IFC4X1_IfcConnectionGeometry_type), true),
            new attribute(strings[3006], new named_type(IFC4X1_IfcPhysicalOrVirtualEnum_type), false),
            new attribute(strings[3007], new named_type(IFC4X1_IfcInternalOrExternalEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelSpaceBoundary1stLevel_type->set_attributes({
            new attribute(strings[3008], new named_type(IFC4X1_IfcRelSpaceBoundary1stLevel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelSpaceBoundary2ndLevel_type->set_attributes({
            new attribute(strings[3009], new named_type(IFC4X1_IfcRelSpaceBoundary2ndLevel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRelVoidsElement_type->set_attributes({
            new attribute(strings[2983], new named_type(IFC4X1_IfcElement_type), false),
            new attribute(strings[3010], new named_type(IFC4X1_IfcFeatureElementSubtraction_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcRelationship_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcReparametrisedCompositeCurveSegment_type->set_attributes({
            new attribute(strings[3011], new named_type(IFC4X1_IfcParameterValue_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcRepresentation_type->set_attributes({
            new attribute(strings[3012], new named_type(IFC4X1_IfcRepresentationContext_type), false),
            new attribute(strings[3013], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3014], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3015], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcRepresentationItem_type)), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcRepresentationContext_type->set_attributes({
            new attribute(strings[3016], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3017], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4X1_IfcRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcRepresentationMap_type->set_attributes({
            new attribute(strings[3018], new named_type(IFC4X1_IfcAxis2Placement_type), false),
            new attribute(strings[3019], new named_type(IFC4X1_IfcRepresentation_type), false)
    },{
            false, false
    });
    IFC4X1_IfcResource_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2371], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcResourceApprovalRelationship_type->set_attributes({
            new attribute(strings[2664], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcResourceObjectSelect_type)), false),
            new attribute(strings[2415], new named_type(IFC4X1_IfcApproval_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcResourceConstraintRelationship_type->set_attributes({
            new attribute(strings[2959], new named_type(IFC4X1_IfcConstraint_type), false),
            new attribute(strings[2664], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcResourceObjectSelect_type)), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcResourceLevelRelationship_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false
    });
    IFC4X1_IfcResourceTime_type->set_attributes({
            new attribute(strings[3020], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3021], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3022], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3023], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3024], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3025], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3026], new named_type(IFC4X1_IfcBoolean_type), true),
            new attribute(strings[3027], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3028], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3029], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3030], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3031], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3032], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3033], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3034], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRevolvedAreaSolid_type->set_attributes({
            new attribute(strings[2441], new named_type(IFC4X1_IfcAxis1Placement_type), false),
            new attribute(strings[3035], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcRevolvedAreaSolidTapered_type->set_attributes({
            new attribute(strings[2666], new named_type(IFC4X1_IfcProfileDef_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcRightCircularCone_type->set_attributes({
            new attribute(strings[2843], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3036], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcRightCircularCylinder_type->set_attributes({
            new attribute(strings[2843], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcRoof_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcRoofTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRoofType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcRoofTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcRoot_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X1_IfcGloballyUniqueId_type), false),
            new attribute(strings[3038], new named_type(IFC4X1_IfcOwnerHistory_type), true),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcRoundedRectangleProfileDef_type->set_attributes({
            new attribute(strings[3039], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcSIUnit_type->set_attributes({
            new attribute(strings[3040], new named_type(IFC4X1_IfcSIPrefix_type), true),
            new attribute(strings[2400], new named_type(IFC4X1_IfcSIUnitName_type), false)
    },{
            true, false, false, false
    });
    IFC4X1_IfcSanitaryTerminal_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSanitaryTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSanitaryTerminalType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSanitaryTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSchedulingTime_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3041], new named_type(IFC4X1_IfcDataOriginEnum_type), true),
            new attribute(strings[3042], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcSeamCurve_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X1_IfcSectionProperties_type->set_attributes({
            new attribute(strings[3043], new named_type(IFC4X1_IfcSectionTypeEnum_type), false),
            new attribute(strings[3044], new named_type(IFC4X1_IfcProfileDef_type), false),
            new attribute(strings[3045], new named_type(IFC4X1_IfcProfileDef_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcSectionReinforcementProperties_type->set_attributes({
            new attribute(strings[3046], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[3047], new named_type(IFC4X1_IfcLengthMeasure_type), false),
            new attribute(strings[3048], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[3049], new named_type(IFC4X1_IfcReinforcingBarRoleEnum_type), false),
            new attribute(strings[3050], new named_type(IFC4X1_IfcSectionProperties_type), false),
            new attribute(strings[3051], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcReinforcementBarProperties_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcSectionedSolid_type->set_attributes({
            new attribute(strings[2688], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[3052], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcProfileDef_type)), false)
    },{
            false, false
    });
    IFC4X1_IfcSectionedSolidHorizontal_type->set_attributes({
            new attribute(strings[3053], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcDistanceExpression_type)), false),
            new attribute(strings[3054], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcSectionedSpine_type->set_attributes({
            new attribute(strings[3055], new named_type(IFC4X1_IfcCompositeCurve_type), false),
            new attribute(strings[3052], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcProfileDef_type)), false),
            new attribute(strings[3053], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_IfcAxis2Placement3D_type)), false)
    },{
            false, false, false
    });
    IFC4X1_IfcSensor_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSensorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSensorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSensorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcShadingDevice_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcShadingDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcShadingDeviceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcShadingDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcShapeAspect_type->set_attributes({
            new attribute(strings[3056], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcShapeModel_type)), false),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[3057], new named_type(IFC4X1_IfcLogical_type), false),
            new attribute(strings[3058], new named_type(IFC4X1_IfcProductRepresentationSelect_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcShapeModel_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcShapeRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcShellBasedSurfaceModel_type->set_attributes({
            new attribute(strings[3059], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcShell_type)), false)
    },{
            false
    });
    IFC4X1_IfcSimpleProperty_type->set_attributes({
    },{
            false, false
    });
    IFC4X1_IfcSimplePropertyTemplate_type->set_attributes({
            new attribute(strings[2524], new named_type(IFC4X1_IfcSimplePropertyTemplateTypeEnum_type), true),
            new attribute(strings[3060], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3061], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3062], new named_type(IFC4X1_IfcPropertyEnumeration_type), true),
            new attribute(strings[3063], new named_type(IFC4X1_IfcUnit_type), true),
            new attribute(strings[3064], new named_type(IFC4X1_IfcUnit_type), true),
            new attribute(strings[2798], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3065], new named_type(IFC4X1_IfcStateEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSite_type->set_attributes({
            new attribute(strings[3066], new named_type(IFC4X1_IfcCompoundPlaneAngleMeasure_type), true),
            new attribute(strings[3067], new named_type(IFC4X1_IfcCompoundPlaneAngleMeasure_type), true),
            new attribute(strings[3068], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[3069], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3070], new named_type(IFC4X1_IfcPostalAddress_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSlab_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSlabTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSlabElementedCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSlabStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSlabType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSlabTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSlippageConnectionCondition_type->set_attributes({
            new attribute(strings[3071], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[3072], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[3073], new named_type(IFC4X1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcSolarDevice_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSolarDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSolarDeviceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSolarDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSolidModel_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcSpace_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSpaceTypeEnum_type), true),
            new attribute(strings[3074], new named_type(IFC4X1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpaceHeater_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSpaceHeaterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpaceHeaterType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSpaceHeaterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpaceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSpaceTypeEnum_type), false),
            new attribute(strings[2493], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpatialElement_type->set_attributes({
            new attribute(strings[2493], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpatialElementType_type->set_attributes({
            new attribute(strings[2652], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpatialStructureElement_type->set_attributes({
            new attribute(strings[3075], new named_type(IFC4X1_IfcElementCompositionEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpatialStructureElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpatialZone_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSpatialZoneTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSpatialZoneType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSpatialZoneTypeEnum_type), false),
            new attribute(strings[2493], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSphere_type->set_attributes({
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X1_IfcSphericalSurface_type->set_attributes({
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X1_IfcStackTerminal_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStackTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStackTerminalType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStackTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStair_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStairTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStairFlight_type->set_attributes({
            new attribute(strings[3076], new named_type(IFC4X1_IfcInteger_type), true),
            new attribute(strings[3077], new named_type(IFC4X1_IfcInteger_type), true),
            new attribute(strings[3078], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3079], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcStairFlightTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStairFlightType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStairFlightTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStairType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStairTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralAction_type->set_attributes({
            new attribute(strings[3080], new named_type(IFC4X1_IfcBoolean_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralActivity_type->set_attributes({
            new attribute(strings[3081], new named_type(IFC4X1_IfcStructuralLoad_type), false),
            new attribute(strings[3082], new named_type(IFC4X1_IfcGlobalOrLocalEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralAnalysisModel_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcAnalysisModelTypeEnum_type), false),
            new attribute(strings[3083], new named_type(IFC4X1_IfcAxis2Placement3D_type), true),
            new attribute(strings[3084], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcStructuralLoadGroup_type)), true),
            new attribute(strings[3085], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcStructuralResultGroup_type)), true),
            new attribute(strings[3086], new named_type(IFC4X1_IfcObjectPlacement_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralConnection_type->set_attributes({
            new attribute(strings[2974], new named_type(IFC4X1_IfcBoundaryCondition_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralConnectionCondition_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X1_IfcStructuralCurveAction_type->set_attributes({
            new attribute(strings[3087], new named_type(IFC4X1_IfcProjectedOrTrueLengthEnum_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcStructuralCurveActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralCurveConnection_type->set_attributes({
            new attribute(strings[2441], new named_type(IFC4X1_IfcDirection_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralCurveMember_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStructuralCurveMemberTypeEnum_type), false),
            new attribute(strings[2441], new named_type(IFC4X1_IfcDirection_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralCurveMemberVarying_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralCurveReaction_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStructuralCurveActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralItem_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLinearAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLoad_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X1_IfcStructuralLoadCase_type->set_attributes({
            new attribute(strings[3088], new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_IfcRatioMeasure_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLoadConfiguration_type->set_attributes({
            new attribute(strings[2726], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcStructuralLoadOrResult_type)), false),
            new attribute(strings[3089], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X1_IfcLengthMeasure_type))), true)
    },{
            false, false, false
    });
    IFC4X1_IfcStructuralLoadGroup_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcLoadGroupTypeEnum_type), false),
            new attribute(strings[3090], new named_type(IFC4X1_IfcActionTypeEnum_type), false),
            new attribute(strings[3091], new named_type(IFC4X1_IfcActionSourceTypeEnum_type), false),
            new attribute(strings[3092], new named_type(IFC4X1_IfcRatioMeasure_type), true),
            new attribute(strings[2376], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLoadLinearForce_type->set_attributes({
            new attribute(strings[3093], new named_type(IFC4X1_IfcLinearForceMeasure_type), true),
            new attribute(strings[3094], new named_type(IFC4X1_IfcLinearForceMeasure_type), true),
            new attribute(strings[3095], new named_type(IFC4X1_IfcLinearForceMeasure_type), true),
            new attribute(strings[3096], new named_type(IFC4X1_IfcLinearMomentMeasure_type), true),
            new attribute(strings[3097], new named_type(IFC4X1_IfcLinearMomentMeasure_type), true),
            new attribute(strings[3098], new named_type(IFC4X1_IfcLinearMomentMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLoadOrResult_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcStructuralLoadPlanarForce_type->set_attributes({
            new attribute(strings[3099], new named_type(IFC4X1_IfcPlanarForceMeasure_type), true),
            new attribute(strings[3100], new named_type(IFC4X1_IfcPlanarForceMeasure_type), true),
            new attribute(strings[3101], new named_type(IFC4X1_IfcPlanarForceMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcStructuralLoadSingleDisplacement_type->set_attributes({
            new attribute(strings[3102], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[3103], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[3104], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[3105], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3106], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3107], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLoadSingleDisplacementDistortion_type->set_attributes({
            new attribute(strings[3108], new named_type(IFC4X1_IfcCurvatureMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLoadSingleForce_type->set_attributes({
            new attribute(strings[3109], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[3110], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[3111], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[3112], new named_type(IFC4X1_IfcTorqueMeasure_type), true),
            new attribute(strings[3113], new named_type(IFC4X1_IfcTorqueMeasure_type), true),
            new attribute(strings[3114], new named_type(IFC4X1_IfcTorqueMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLoadSingleForceWarping_type->set_attributes({
            new attribute(strings[3115], new named_type(IFC4X1_IfcWarpingMomentMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralLoadStatic_type->set_attributes({
    },{
            false
    });
    IFC4X1_IfcStructuralLoadTemperature_type->set_attributes({
            new attribute(strings[3116], new named_type(IFC4X1_IfcThermodynamicTemperatureMeasure_type), true),
            new attribute(strings[3117], new named_type(IFC4X1_IfcThermodynamicTemperatureMeasure_type), true),
            new attribute(strings[3118], new named_type(IFC4X1_IfcThermodynamicTemperatureMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcStructuralMember_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralPlanarAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralPointAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralPointConnection_type->set_attributes({
            new attribute(strings[2977], new named_type(IFC4X1_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralPointReaction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralReaction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralResultGroup_type->set_attributes({
            new attribute(strings[3119], new named_type(IFC4X1_IfcAnalysisTheoryTypeEnum_type), false),
            new attribute(strings[3120], new named_type(IFC4X1_IfcStructuralLoadGroup_type), true),
            new attribute(strings[3121], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralSurfaceAction_type->set_attributes({
            new attribute(strings[3087], new named_type(IFC4X1_IfcProjectedOrTrueLengthEnum_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcStructuralSurfaceActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralSurfaceConnection_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralSurfaceMember_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStructuralSurfaceMemberTypeEnum_type), false),
            new attribute(strings[2509], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralSurfaceMemberVarying_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStructuralSurfaceReaction_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcStructuralSurfaceActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcStyleModel_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcStyledItem_type->set_attributes({
            new attribute(strings[3122], new named_type(IFC4X1_IfcRepresentationItem_type), true),
            new attribute(strings[2869], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcStyleAssignmentSelect_type)), false),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X1_IfcStyledRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcSubContractResource_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSubContractResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSubContractResourceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSubContractResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSubedge_type->set_attributes({
            new attribute(strings[3123], new named_type(IFC4X1_IfcEdge_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcSurface_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcSurfaceCurve_type->set_attributes({
            new attribute(strings[3124], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[3125], new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X1_IfcPcurve_type)), false),
            new attribute(strings[3126], new named_type(IFC4X1_IfcPreferredSurfaceCurveRepresentation_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcSurfaceCurveSweptAreaSolid_type->set_attributes({
            new attribute(strings[2688], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2689], new named_type(IFC4X1_IfcParameterValue_type), true),
            new attribute(strings[2690], new named_type(IFC4X1_IfcParameterValue_type), true),
            new attribute(strings[3127], new named_type(IFC4X1_IfcSurface_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcSurfaceFeature_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSurfaceFeatureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSurfaceOfLinearExtrusion_type->set_attributes({
            new attribute(strings[2665], new named_type(IFC4X1_IfcDirection_type), false),
            new attribute(strings[2494], new named_type(IFC4X1_IfcLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcSurfaceOfRevolution_type->set_attributes({
            new attribute(strings[3128], new named_type(IFC4X1_IfcAxis1Placement_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcSurfaceReinforcementArea_type->set_attributes({
            new attribute(strings[3129], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X1_IfcLengthMeasure_type)), true),
            new attribute(strings[3130], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X1_IfcLengthMeasure_type)), true),
            new attribute(strings[3131], new named_type(IFC4X1_IfcRatioMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X1_IfcSurfaceStyle_type->set_attributes({
            new attribute(strings[3132], new named_type(IFC4X1_IfcSurfaceSide_type), false),
            new attribute(strings[2869], new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC4X1_IfcSurfaceStyleElementSelect_type)), false)
    },{
            false, false, false
    });
    IFC4X1_IfcSurfaceStyleLighting_type->set_attributes({
            new attribute(strings[3133], new named_type(IFC4X1_IfcColourRgb_type), false),
            new attribute(strings[3134], new named_type(IFC4X1_IfcColourRgb_type), false),
            new attribute(strings[3135], new named_type(IFC4X1_IfcColourRgb_type), false),
            new attribute(strings[3136], new named_type(IFC4X1_IfcColourRgb_type), false)
    },{
            false, false, false, false
    });
    IFC4X1_IfcSurfaceStyleRefraction_type->set_attributes({
            new attribute(strings[3137], new named_type(IFC4X1_IfcReal_type), true),
            new attribute(strings[3138], new named_type(IFC4X1_IfcReal_type), true)
    },{
            false, false
    });
    IFC4X1_IfcSurfaceStyleRendering_type->set_attributes({
            new attribute(strings[3139], new named_type(IFC4X1_IfcColourOrFactor_type), true),
            new attribute(strings[3135], new named_type(IFC4X1_IfcColourOrFactor_type), true),
            new attribute(strings[3133], new named_type(IFC4X1_IfcColourOrFactor_type), true),
            new attribute(strings[3140], new named_type(IFC4X1_IfcColourOrFactor_type), true),
            new attribute(strings[3141], new named_type(IFC4X1_IfcColourOrFactor_type), true),
            new attribute(strings[3142], new named_type(IFC4X1_IfcSpecularHighlightSelect_type), true),
            new attribute(strings[3143], new named_type(IFC4X1_IfcReflectanceMethodEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSurfaceStyleShading_type->set_attributes({
            new attribute(strings[3144], new named_type(IFC4X1_IfcColourRgb_type), false),
            new attribute(strings[3145], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true)
    },{
            false, false
    });
    IFC4X1_IfcSurfaceStyleWithTextures_type->set_attributes({
            new attribute(strings[3146], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcSurfaceTexture_type)), false)
    },{
            false
    });
    IFC4X1_IfcSurfaceTexture_type->set_attributes({
            new attribute(strings[3147], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[3148], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[3149], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[3150], new named_type(IFC4X1_IfcCartesianTransformationOperator2D_type), true),
            new attribute(strings[3151], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcIdentifier_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcSweptAreaSolid_type->set_attributes({
            new attribute(strings[3152], new named_type(IFC4X1_IfcProfileDef_type), false),
            new attribute(strings[2531], new named_type(IFC4X1_IfcAxis2Placement3D_type), true)
    },{
            false, false
    });
    IFC4X1_IfcSweptDiskSolid_type->set_attributes({
            new attribute(strings[2688], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[2385], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3153], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2689], new named_type(IFC4X1_IfcParameterValue_type), true),
            new attribute(strings[2690], new named_type(IFC4X1_IfcParameterValue_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcSweptDiskSolidPolygonal_type->set_attributes({
            new attribute(strings[2710], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcSweptSurface_type->set_attributes({
            new attribute(strings[3154], new named_type(IFC4X1_IfcProfileDef_type), false),
            new attribute(strings[2531], new named_type(IFC4X1_IfcAxis2Placement3D_type), true)
    },{
            false, false
    });
    IFC4X1_IfcSwitchingDevice_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSwitchingDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSwitchingDeviceType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSwitchingDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSystem_type->set_attributes({
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcSystemFurnitureElement_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSystemFurnitureElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcSystemFurnitureElementType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcSystemFurnitureElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTShapeProfileDef_type->set_attributes({
            new attribute(strings[2494], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3155], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2431], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2709], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2710], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2711], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3156], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3157], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[2712], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTable_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3158], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcTableRow_type)), true),
            new attribute(strings[3159], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcTableColumn_type)), true)
    },{
            false, false, false
    });
    IFC4X1_IfcTableColumn_type->set_attributes({
            new attribute(strings[2409], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[2590], new named_type(IFC4X1_IfcUnit_type), true),
            new attribute(strings[2806], new named_type(IFC4X1_IfcReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcTableRow_type->set_attributes({
            new attribute(strings[3160], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcValue_type)), true),
            new attribute(strings[3161], new named_type(IFC4X1_IfcBoolean_type), true)
    },{
            false, false
    });
    IFC4X1_IfcTank_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTankTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTankType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTankTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTask_type->set_attributes({
            new attribute(strings[2370], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3162], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3163], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[2778], new named_type(IFC4X1_IfcInteger_type), true),
            new attribute(strings[3164], new named_type(IFC4X1_IfcTaskTime_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcTaskTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTaskTime_type->set_attributes({
            new attribute(strings[2732], new named_type(IFC4X1_IfcTaskDurationEnum_type), true),
            new attribute(strings[3165], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3022], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3023], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3166], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3167], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3168], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3169], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3170], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3171], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3172], new named_type(IFC4X1_IfcBoolean_type), true),
            new attribute(strings[3027], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3173], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3030], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3031], new named_type(IFC4X1_IfcDateTime_type), true),
            new attribute(strings[3174], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3034], new named_type(IFC4X1_IfcPositiveRatioMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTaskTimeRecurring_type->set_attributes({
            new attribute(strings[3175], new named_type(IFC4X1_IfcRecurrencePattern_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTaskType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTaskTypeEnum_type), false),
            new attribute(strings[3162], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTelecomAddress_type->set_attributes({
            new attribute(strings[3176], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true),
            new attribute(strings[3177], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true),
            new attribute(strings[3178], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3179], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcLabel_type)), true),
            new attribute(strings[3180], new named_type(IFC4X1_IfcURIReference_type), true),
            new attribute(strings[3181], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcURIReference_type)), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTendon_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTendonTypeEnum_type), true),
            new attribute(strings[2801], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2933], new named_type(IFC4X1_IfcAreaMeasure_type), true),
            new attribute(strings[3182], new named_type(IFC4X1_IfcForceMeasure_type), true),
            new attribute(strings[3183], new named_type(IFC4X1_IfcPressureMeasure_type), true),
            new attribute(strings[3184], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3185], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3186], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTendonAnchor_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTendonAnchorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTendonAnchorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTendonAnchorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTendonType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTendonTypeEnum_type), false),
            new attribute(strings[2801], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2933], new named_type(IFC4X1_IfcAreaMeasure_type), true),
            new attribute(strings[3187], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTessellatedFaceSet_type->set_attributes({
            new attribute(strings[2499], new named_type(IFC4X1_IfcCartesianPointList3D_type), false)
    },{
            false
    });
    IFC4X1_IfcTessellatedItem_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcTextLiteral_type->set_attributes({
            new attribute(strings[3188], new named_type(IFC4X1_IfcPresentableText_type), false),
            new attribute(strings[2846], new named_type(IFC4X1_IfcAxis2Placement_type), false),
            new attribute(strings[3189], new named_type(IFC4X1_IfcTextPath_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcTextLiteralWithExtent_type->set_attributes({
            new attribute(strings[3190], new named_type(IFC4X1_IfcPlanarExtent_type), false),
            new attribute(strings[3191], new named_type(IFC4X1_IfcBoxAlignment_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcTextStyle_type->set_attributes({
            new attribute(strings[3192], new named_type(IFC4X1_IfcTextStyleForDefinedFont_type), true),
            new attribute(strings[3193], new named_type(IFC4X1_IfcTextStyleTextModel_type), true),
            new attribute(strings[3194], new named_type(IFC4X1_IfcTextFontSelect_type), false),
            new attribute(strings[2581], new named_type(IFC4X1_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcTextStyleFontModel_type->set_attributes({
            new attribute(strings[3195], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcTextFontName_type)), false),
            new attribute(strings[3196], new named_type(IFC4X1_IfcFontStyle_type), true),
            new attribute(strings[3197], new named_type(IFC4X1_IfcFontVariant_type), true),
            new attribute(strings[3198], new named_type(IFC4X1_IfcFontWeight_type), true),
            new attribute(strings[3199], new named_type(IFC4X1_IfcSizeSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcTextStyleForDefinedFont_type->set_attributes({
            new attribute(strings[3200], new named_type(IFC4X1_IfcColour_type), false),
            new attribute(strings[3201], new named_type(IFC4X1_IfcColour_type), true)
    },{
            false, false
    });
    IFC4X1_IfcTextStyleTextModel_type->set_attributes({
            new attribute(strings[3202], new named_type(IFC4X1_IfcSizeSelect_type), true),
            new attribute(strings[3203], new named_type(IFC4X1_IfcTextAlignment_type), true),
            new attribute(strings[3204], new named_type(IFC4X1_IfcTextDecoration_type), true),
            new attribute(strings[3205], new named_type(IFC4X1_IfcSizeSelect_type), true),
            new attribute(strings[3206], new named_type(IFC4X1_IfcSizeSelect_type), true),
            new attribute(strings[3207], new named_type(IFC4X1_IfcTextTransformation_type), true),
            new attribute(strings[3208], new named_type(IFC4X1_IfcSizeSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcTextureCoordinate_type->set_attributes({
            new attribute(strings[3209], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcSurfaceTexture_type)), false)
    },{
            false
    });
    IFC4X1_IfcTextureCoordinateGenerator_type->set_attributes({
            new attribute(strings[3149], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[3151], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcReal_type)), true)
    },{
            false, false, false
    });
    IFC4X1_IfcTextureMap_type->set_attributes({
            new attribute(strings[3210], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X1_IfcTextureVertex_type)), false),
            new attribute(strings[2714], new named_type(IFC4X1_IfcFace_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcTextureVertex_type->set_attributes({
            new attribute(strings[2499], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_IfcParameterValue_type)), false)
    },{
            false
    });
    IFC4X1_IfcTextureVertexList_type->set_attributes({
            new attribute(strings[3211], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_IfcParameterValue_type))), false)
    },{
            false
    });
    IFC4X1_IfcTimePeriod_type->set_attributes({
            new attribute(strings[3212], new named_type(IFC4X1_IfcTime_type), false),
            new attribute(strings[3213], new named_type(IFC4X1_IfcTime_type), false)
    },{
            false, false
    });
    IFC4X1_IfcTimeSeries_type->set_attributes({
            new attribute(strings[2400], new named_type(IFC4X1_IfcLabel_type), false),
            new attribute(strings[2375], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[3212], new named_type(IFC4X1_IfcDateTime_type), false),
            new attribute(strings[3213], new named_type(IFC4X1_IfcDateTime_type), false),
            new attribute(strings[3214], new named_type(IFC4X1_IfcTimeSeriesDataTypeEnum_type), false),
            new attribute(strings[3041], new named_type(IFC4X1_IfcDataOriginEnum_type), false),
            new attribute(strings[3042], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[2590], new named_type(IFC4X1_IfcUnit_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTimeSeriesValue_type->set_attributes({
            new attribute(strings[2728], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcValue_type)), false)
    },{
            false
    });
    IFC4X1_IfcTopologicalRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcTopologyRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X1_IfcToroidalSurface_type->set_attributes({
            new attribute(strings[3215], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3216], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X1_IfcTransformer_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTransformerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTransformerType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTransformerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTransitionCurveSegment2D_type->set_attributes({
            new attribute(strings[3217], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3218], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3219], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[3220], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[3221], new named_type(IFC4X1_IfcTransitionCurveType_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTransportElement_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTransportElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTransportElementType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTransportElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTrapeziumProfileDef_type->set_attributes({
            new attribute(strings[3222], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3223], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2486], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3224], new named_type(IFC4X1_IfcLengthMeasure_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X1_IfcTriangulatedFaceSet_type->set_attributes({
            new attribute(strings[3225], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_IfcParameterValue_type))), true),
            new attribute(strings[2854], new named_type(IFC4X1_IfcBoolean_type), true),
            new attribute(strings[2719], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_IfcPositiveInteger_type))), false),
            new attribute(strings[2856], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcPositiveInteger_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcTriangulatedIrregularNetwork_type->set_attributes({
            new attribute(strings[3226], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcInteger_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcTrimmedCurve_type->set_attributes({
            new attribute(strings[2813], new named_type(IFC4X1_IfcCurve_type), false),
            new attribute(strings[3227], new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X1_IfcTrimmingSelect_type)), false),
            new attribute(strings[3228], new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X1_IfcTrimmingSelect_type)), false),
            new attribute(strings[3229], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[3126], new named_type(IFC4X1_IfcTrimmingPreference_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X1_IfcTubeBundle_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTubeBundleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTubeBundleType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcTubeBundleTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTypeObject_type->set_attributes({
            new attribute(strings[3230], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[3231], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPropertySetDefinition_type)), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcTypeProcess_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2371], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[3232], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTypeProduct_type->set_attributes({
            new attribute(strings[3233], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_IfcRepresentationMap_type)), true),
            new attribute(strings[2393], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcTypeResource_type->set_attributes({
            new attribute(strings[2420], new named_type(IFC4X1_IfcIdentifier_type), true),
            new attribute(strings[2371], new named_type(IFC4X1_IfcText_type), true),
            new attribute(strings[3234], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcUShapeProfileDef_type->set_attributes({
            new attribute(strings[2494], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3155], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2431], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2709], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2710], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2729], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2712], new named_type(IFC4X1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcUnitAssignment_type->set_attributes({
            new attribute(strings[3235], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcUnit_type)), false)
    },{
            false
    });
    IFC4X1_IfcUnitaryControlElement_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcUnitaryControlElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcUnitaryControlElementType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcUnitaryControlElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcUnitaryEquipment_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcUnitaryEquipmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcUnitaryEquipmentType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcUnitaryEquipmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcValve_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcValveTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcValveType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcValveTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcVector_type->set_attributes({
            new attribute(strings[2670], new named_type(IFC4X1_IfcDirection_type), false),
            new attribute(strings[3236], new named_type(IFC4X1_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X1_IfcVertex_type->set_attributes({
    },{
            
    });
    IFC4X1_IfcVertexLoop_type->set_attributes({
            new attribute(strings[3237], new named_type(IFC4X1_IfcVertex_type), false)
    },{
            false
    });
    IFC4X1_IfcVertexPoint_type->set_attributes({
            new attribute(strings[3238], new named_type(IFC4X1_IfcPoint_type), false)
    },{
            false
    });
    IFC4X1_IfcVibrationIsolator_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcVibrationIsolatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcVibrationIsolatorType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcVibrationIsolatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcVirtualElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcVirtualGridIntersection_type->set_attributes({
            new attribute(strings[3239], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_IfcGridAxis_type)), false),
            new attribute(strings[3240], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X1_IfcLengthMeasure_type)), false)
    },{
            false, false
    });
    IFC4X1_IfcVoidingFeature_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcVoidingFeatureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWall_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcWallTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWallElementedCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWallStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWallType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcWallTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWasteTerminal_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcWasteTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWasteTerminalType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcWasteTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWindow_type->set_attributes({
            new attribute(strings[2621], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2622], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcWindowTypeEnum_type), true),
            new attribute(strings[3241], new named_type(IFC4X1_IfcWindowTypePartitioningEnum_type), true),
            new attribute(strings[3242], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWindowLiningProperties_type->set_attributes({
            new attribute(strings[2625], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2626], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2629], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3243], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3244], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3245], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3246], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3247], new named_type(IFC4X1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2635], new named_type(IFC4X1_IfcShapeAspect_type), true),
            new attribute(strings[2631], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2636], new named_type(IFC4X1_IfcLengthMeasure_type), true),
            new attribute(strings[2637], new named_type(IFC4X1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWindowPanelProperties_type->set_attributes({
            new attribute(strings[2623], new named_type(IFC4X1_IfcWindowPanelOperationEnum_type), false),
            new attribute(strings[2641], new named_type(IFC4X1_IfcWindowPanelPositionEnum_type), false),
            new attribute(strings[2831], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2832], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2635], new named_type(IFC4X1_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWindowStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWindowStyle_type->set_attributes({
            new attribute(strings[2642], new named_type(IFC4X1_IfcWindowStyleConstructionEnum_type), false),
            new attribute(strings[2623], new named_type(IFC4X1_IfcWindowStyleOperationEnum_type), false),
            new attribute(strings[2643], new named_type(IFC4X1_IfcBoolean_type), false),
            new attribute(strings[2644], new named_type(IFC4X1_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWindowType_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcWindowTypeEnum_type), false),
            new attribute(strings[3241], new named_type(IFC4X1_IfcWindowTypePartitioningEnum_type), false),
            new attribute(strings[2643], new named_type(IFC4X1_IfcBoolean_type), true),
            new attribute(strings[3242], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWorkCalendar_type->set_attributes({
            new attribute(strings[3248], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcWorkTime_type)), true),
            new attribute(strings[3249], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcWorkTime_type)), true),
            new attribute(strings[2369], new named_type(IFC4X1_IfcWorkCalendarTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWorkControl_type->set_attributes({
            new attribute(strings[2828], new named_type(IFC4X1_IfcDateTime_type), false),
            new attribute(strings[3250], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_IfcPerson_type)), true),
            new attribute(strings[2376], new named_type(IFC4X1_IfcLabel_type), true),
            new attribute(strings[3251], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3171], new named_type(IFC4X1_IfcDuration_type), true),
            new attribute(strings[3212], new named_type(IFC4X1_IfcDateTime_type), false),
            new attribute(strings[3252], new named_type(IFC4X1_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWorkPlan_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcWorkPlanTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWorkSchedule_type->set_attributes({
            new attribute(strings[2369], new named_type(IFC4X1_IfcWorkScheduleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcWorkTime_type->set_attributes({
            new attribute(strings[3253], new named_type(IFC4X1_IfcRecurrencePattern_type), true),
            new attribute(strings[3254], new named_type(IFC4X1_IfcDate_type), true),
            new attribute(strings[3255], new named_type(IFC4X1_IfcDate_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcZShapeProfileDef_type->set_attributes({
            new attribute(strings[2494], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3155], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2431], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2709], new named_type(IFC4X1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2710], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2729], new named_type(IFC4X1_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X1_IfcZone_type->set_attributes({
            new attribute(strings[2493], new named_type(IFC4X1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X1_IfcActor_type->set_inverse_attributes({
            new inverse_attribute(strings[3256], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToActor_type, IFC4X1_IfcRelAssignsToActor_type->attributes()[0])
    });
    IFC4X1_IfcActorRole_type->set_inverse_attributes({
            new inverse_attribute(strings[3257], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X1_IfcAddress_type->set_inverse_attributes({
            new inverse_attribute(strings[3258], inverse_attribute::set_type, 0, -1, IFC4X1_IfcPerson_type, IFC4X1_IfcPerson_type->attributes()[7]),
            new inverse_attribute(strings[3259], inverse_attribute::set_type, 0, -1, IFC4X1_IfcOrganization_type, IFC4X1_IfcOrganization_type->attributes()[4])
    });
    IFC4X1_IfcAlignment2DHorizontal_type->set_inverse_attributes({
            new inverse_attribute(strings[3260], inverse_attribute::set_type, 1, -1, IFC4X1_IfcAlignmentCurve_type, IFC4X1_IfcAlignmentCurve_type->attributes()[0])
    });
    IFC4X1_IfcAlignment2DHorizontalSegment_type->set_inverse_attributes({
            new inverse_attribute(strings[3261], inverse_attribute::set_type, 1, 1, IFC4X1_IfcAlignment2DHorizontal_type, IFC4X1_IfcAlignment2DHorizontal_type->attributes()[1])
    });
    IFC4X1_IfcAlignment2DVertical_type->set_inverse_attributes({
            new inverse_attribute(strings[3260], inverse_attribute::set_type, 1, 1, IFC4X1_IfcAlignmentCurve_type, IFC4X1_IfcAlignmentCurve_type->attributes()[1])
    });
    IFC4X1_IfcAlignment2DVerticalSegment_type->set_inverse_attributes({
            new inverse_attribute(strings[3262], inverse_attribute::set_type, 1, 1, IFC4X1_IfcAlignment2DVertical_type, IFC4X1_IfcAlignment2DVertical_type->attributes()[0])
    });
    IFC4X1_IfcAnnotation_type->set_inverse_attributes({
            new inverse_attribute(strings[3263], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelContainedInSpatialStructure_type, IFC4X1_IfcRelContainedInSpatialStructure_type->attributes()[0])
    });
    IFC4X1_IfcAppliedValue_type->set_inverse_attributes({
            new inverse_attribute(strings[3257], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X1_IfcApproval_type->set_inverse_attributes({
            new inverse_attribute(strings[3264], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3265], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociatesApproval_type, IFC4X1_IfcRelAssociatesApproval_type->attributes()[0]),
            new inverse_attribute(strings[3266], inverse_attribute::set_type, 0, -1, IFC4X1_IfcResourceApprovalRelationship_type, IFC4X1_IfcResourceApprovalRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3267], inverse_attribute::set_type, 0, -1, IFC4X1_IfcApprovalRelationship_type, IFC4X1_IfcApprovalRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3268], inverse_attribute::set_type, 0, -1, IFC4X1_IfcApprovalRelationship_type, IFC4X1_IfcApprovalRelationship_type->attributes()[0])
    });
    IFC4X1_IfcClassification_type->set_inverse_attributes({
            new inverse_attribute(strings[3269], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociatesClassification_type, IFC4X1_IfcRelAssociatesClassification_type->attributes()[0]),
            new inverse_attribute(strings[3270], inverse_attribute::set_type, 0, -1, IFC4X1_IfcClassificationReference_type, IFC4X1_IfcClassificationReference_type->attributes()[0])
    });
    IFC4X1_IfcClassificationReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3271], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociatesClassification_type, IFC4X1_IfcRelAssociatesClassification_type->attributes()[0]),
            new inverse_attribute(strings[3270], inverse_attribute::set_type, 0, -1, IFC4X1_IfcClassificationReference_type, IFC4X1_IfcClassificationReference_type->attributes()[0])
    });
    IFC4X1_IfcCompositeCurveSegment_type->set_inverse_attributes({
            new inverse_attribute(strings[3272], inverse_attribute::set_type, 1, -1, IFC4X1_IfcCompositeCurve_type, IFC4X1_IfcCompositeCurve_type->attributes()[0])
    });
    IFC4X1_IfcConstraint_type->set_inverse_attributes({
            new inverse_attribute(strings[3264], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3273], inverse_attribute::set_type, 0, -1, IFC4X1_IfcResourceConstraintRelationship_type, IFC4X1_IfcResourceConstraintRelationship_type->attributes()[0])
    });
    IFC4X1_IfcContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3274], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelDefinesByProperties_type, IFC4X1_IfcRelDefinesByProperties_type->attributes()[0]),
            new inverse_attribute(strings[3275], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelDeclares_type, IFC4X1_IfcRelDeclares_type->attributes()[0])
    });
    IFC4X1_IfcContextDependentUnit_type->set_inverse_attributes({
            new inverse_attribute(strings[3257], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X1_IfcControl_type->set_inverse_attributes({
            new inverse_attribute(strings[3276], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToControl_type, IFC4X1_IfcRelAssignsToControl_type->attributes()[0])
    });
    IFC4X1_IfcConversionBasedUnit_type->set_inverse_attributes({
            new inverse_attribute(strings[3257], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X1_IfcCoordinateReferenceSystem_type->set_inverse_attributes({
            new inverse_attribute(strings[3277], inverse_attribute::set_type, 0, 1, IFC4X1_IfcCoordinateOperation_type, IFC4X1_IfcCoordinateOperation_type->attributes()[0])
    });
    IFC4X1_IfcCovering_type->set_inverse_attributes({
            new inverse_attribute(strings[3278], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelCoversSpaces_type, IFC4X1_IfcRelCoversSpaces_type->attributes()[1]),
            new inverse_attribute(strings[3279], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelCoversBldgElements_type, IFC4X1_IfcRelCoversBldgElements_type->attributes()[1])
    });
    IFC4X1_IfcDistributionControlElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3280], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelFlowControlElements_type, IFC4X1_IfcRelFlowControlElements_type->attributes()[0])
    });
    IFC4X1_IfcDistributionElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3281], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelConnectsPortToElement_type, IFC4X1_IfcRelConnectsPortToElement_type->attributes()[1])
    });
    IFC4X1_IfcDistributionFlowElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3282], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelFlowControlElements_type, IFC4X1_IfcRelFlowControlElements_type->attributes()[1])
    });
    IFC4X1_IfcDocumentInformation_type->set_inverse_attributes({
            new inverse_attribute(strings[3283], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociatesDocument_type, IFC4X1_IfcRelAssociatesDocument_type->attributes()[0]),
            new inverse_attribute(strings[3284], inverse_attribute::set_type, 0, -1, IFC4X1_IfcDocumentReference_type, IFC4X1_IfcDocumentReference_type->attributes()[1]),
            new inverse_attribute(strings[3285], inverse_attribute::set_type, 0, -1, IFC4X1_IfcDocumentInformationRelationship_type, IFC4X1_IfcDocumentInformationRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3286], inverse_attribute::set_type, 0, 1, IFC4X1_IfcDocumentInformationRelationship_type, IFC4X1_IfcDocumentInformationRelationship_type->attributes()[0])
    });
    IFC4X1_IfcDocumentReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3287], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociatesDocument_type, IFC4X1_IfcRelAssociatesDocument_type->attributes()[0])
    });
    IFC4X1_IfcElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3288], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelFillsElement_type, IFC4X1_IfcRelFillsElement_type->attributes()[1]),
            new inverse_attribute(strings[3289], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelConnectsElements_type, IFC4X1_IfcRelConnectsElements_type->attributes()[1]),
            new inverse_attribute(strings[3290], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelInterferesElements_type, IFC4X1_IfcRelInterferesElements_type->attributes()[1]),
            new inverse_attribute(strings[3291], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelInterferesElements_type, IFC4X1_IfcRelInterferesElements_type->attributes()[0]),
            new inverse_attribute(strings[3292], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelProjectsElement_type, IFC4X1_IfcRelProjectsElement_type->attributes()[0]),
            new inverse_attribute(strings[3293], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelReferencedInSpatialStructure_type, IFC4X1_IfcRelReferencedInSpatialStructure_type->attributes()[0]),
            new inverse_attribute(strings[3294], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelVoidsElement_type, IFC4X1_IfcRelVoidsElement_type->attributes()[0]),
            new inverse_attribute(strings[3295], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelConnectsWithRealizingElements_type, IFC4X1_IfcRelConnectsWithRealizingElements_type->attributes()[0]),
            new inverse_attribute(strings[3296], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelSpaceBoundary_type, IFC4X1_IfcRelSpaceBoundary_type->attributes()[1]),
            new inverse_attribute(strings[3297], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelConnectsElements_type, IFC4X1_IfcRelConnectsElements_type->attributes()[2]),
            new inverse_attribute(strings[3263], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelContainedInSpatialStructure_type, IFC4X1_IfcRelContainedInSpatialStructure_type->attributes()[0]),
            new inverse_attribute(strings[3298], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelCoversBldgElements_type, IFC4X1_IfcRelCoversBldgElements_type->attributes()[0])
    });
    IFC4X1_IfcExternalReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3299], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[0])
    });
    IFC4X1_IfcExternalSpatialElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3300], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelSpaceBoundary_type, IFC4X1_IfcRelSpaceBoundary_type->attributes()[0])
    });
    IFC4X1_IfcFace_type->set_inverse_attributes({
            new inverse_attribute(strings[3301], inverse_attribute::set_type, 0, -1, IFC4X1_IfcTextureMap_type, IFC4X1_IfcTextureMap_type->attributes()[1])
    });
    IFC4X1_IfcFeatureElementAddition_type->set_inverse_attributes({
            new inverse_attribute(strings[3302], inverse_attribute::unspecified_type, -1, -1, IFC4X1_IfcRelProjectsElement_type, IFC4X1_IfcRelProjectsElement_type->attributes()[1])
    });
    IFC4X1_IfcFeatureElementSubtraction_type->set_inverse_attributes({
            new inverse_attribute(strings[3303], inverse_attribute::unspecified_type, -1, -1, IFC4X1_IfcRelVoidsElement_type, IFC4X1_IfcRelVoidsElement_type->attributes()[1])
    });
    IFC4X1_IfcGeometricRepresentationContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3304], inverse_attribute::set_type, 0, -1, IFC4X1_IfcGeometricRepresentationSubContext_type, IFC4X1_IfcGeometricRepresentationSubContext_type->attributes()[0]),
            new inverse_attribute(strings[3277], inverse_attribute::set_type, 0, 1, IFC4X1_IfcCoordinateOperation_type, IFC4X1_IfcCoordinateOperation_type->attributes()[0])
    });
    IFC4X1_IfcGridAxis_type->set_inverse_attributes({
            new inverse_attribute(strings[3305], inverse_attribute::set_type, 0, 1, IFC4X1_IfcGrid_type, IFC4X1_IfcGrid_type->attributes()[2]),
            new inverse_attribute(strings[3306], inverse_attribute::set_type, 0, 1, IFC4X1_IfcGrid_type, IFC4X1_IfcGrid_type->attributes()[1]),
            new inverse_attribute(strings[3307], inverse_attribute::set_type, 0, 1, IFC4X1_IfcGrid_type, IFC4X1_IfcGrid_type->attributes()[0]),
            new inverse_attribute(strings[3308], inverse_attribute::set_type, 0, -1, IFC4X1_IfcVirtualGridIntersection_type, IFC4X1_IfcVirtualGridIntersection_type->attributes()[0])
    });
    IFC4X1_IfcGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3309], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToGroup_type, IFC4X1_IfcRelAssignsToGroup_type->attributes()[0])
    });
    IFC4X1_IfcIndexedPolygonalFace_type->set_inverse_attributes({
            new inverse_attribute(strings[3310], inverse_attribute::set_type, 1, -1, IFC4X1_IfcPolygonalFaceSet_type, IFC4X1_IfcPolygonalFaceSet_type->attributes()[1])
    });
    IFC4X1_IfcLibraryInformation_type->set_inverse_attributes({
            new inverse_attribute(strings[3311], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociatesLibrary_type, IFC4X1_IfcRelAssociatesLibrary_type->attributes()[0]),
            new inverse_attribute(strings[3312], inverse_attribute::set_type, 0, -1, IFC4X1_IfcLibraryReference_type, IFC4X1_IfcLibraryReference_type->attributes()[2])
    });
    IFC4X1_IfcLibraryReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3313], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociatesLibrary_type, IFC4X1_IfcRelAssociatesLibrary_type->attributes()[0])
    });
    IFC4X1_IfcMaterial_type->set_inverse_attributes({
            new inverse_attribute(strings[3314], inverse_attribute::set_type, 0, 1, IFC4X1_IfcMaterialDefinitionRepresentation_type, IFC4X1_IfcMaterialDefinitionRepresentation_type->attributes()[0]),
            new inverse_attribute(strings[3267], inverse_attribute::set_type, 0, -1, IFC4X1_IfcMaterialRelationship_type, IFC4X1_IfcMaterialRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3315], inverse_attribute::set_type, 0, 1, IFC4X1_IfcMaterialRelationship_type, IFC4X1_IfcMaterialRelationship_type->attributes()[0])
    });
    IFC4X1_IfcMaterialConstituent_type->set_inverse_attributes({
            new inverse_attribute(strings[3316], inverse_attribute::unspecified_type, -1, -1, IFC4X1_IfcMaterialConstituentSet_type, IFC4X1_IfcMaterialConstituentSet_type->attributes()[2])
    });
    IFC4X1_IfcMaterialDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3317], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociatesMaterial_type, IFC4X1_IfcRelAssociatesMaterial_type->attributes()[0]),
            new inverse_attribute(strings[3264], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[2523], inverse_attribute::set_type, 0, -1, IFC4X1_IfcMaterialProperties_type, IFC4X1_IfcMaterialProperties_type->attributes()[0])
    });
    IFC4X1_IfcMaterialLayer_type->set_inverse_attributes({
            new inverse_attribute(strings[3318], inverse_attribute::unspecified_type, -1, -1, IFC4X1_IfcMaterialLayerSet_type, IFC4X1_IfcMaterialLayerSet_type->attributes()[0])
    });
    IFC4X1_IfcMaterialProfile_type->set_inverse_attributes({
            new inverse_attribute(strings[3319], inverse_attribute::unspecified_type, -1, -1, IFC4X1_IfcMaterialProfileSet_type, IFC4X1_IfcMaterialProfileSet_type->attributes()[2])
    });
    IFC4X1_IfcMaterialUsageDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3317], inverse_attribute::set_type, 1, -1, IFC4X1_IfcRelAssociatesMaterial_type, IFC4X1_IfcRelAssociatesMaterial_type->attributes()[0])
    });
    IFC4X1_IfcObject_type->set_inverse_attributes({
            new inverse_attribute(strings[3320], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelDefinesByObject_type, IFC4X1_IfcRelDefinesByObject_type->attributes()[0]),
            new inverse_attribute(strings[3275], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelDefinesByObject_type, IFC4X1_IfcRelDefinesByObject_type->attributes()[1]),
            new inverse_attribute(strings[3321], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelDefinesByType_type, IFC4X1_IfcRelDefinesByType_type->attributes()[0]),
            new inverse_attribute(strings[3274], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelDefinesByProperties_type, IFC4X1_IfcRelDefinesByProperties_type->attributes()[0])
    });
    IFC4X1_IfcObjectDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3322], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssigns_type, IFC4X1_IfcRelAssigns_type->attributes()[0]),
            new inverse_attribute(strings[3323], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelNests_type, IFC4X1_IfcRelNests_type->attributes()[1]),
            new inverse_attribute(strings[3324], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelNests_type, IFC4X1_IfcRelNests_type->attributes()[0]),
            new inverse_attribute(strings[3325], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelDeclares_type, IFC4X1_IfcRelDeclares_type->attributes()[1]),
            new inverse_attribute(strings[3326], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAggregates_type, IFC4X1_IfcRelAggregates_type->attributes()[0]),
            new inverse_attribute(strings[3327], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelAggregates_type, IFC4X1_IfcRelAggregates_type->attributes()[1]),
            new inverse_attribute(strings[3328], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociates_type, IFC4X1_IfcRelAssociates_type->attributes()[0])
    });
    IFC4X1_IfcObjectPlacement_type->set_inverse_attributes({
            new inverse_attribute(strings[3329], inverse_attribute::set_type, 0, -1, IFC4X1_IfcProduct_type, IFC4X1_IfcProduct_type->attributes()[0]),
            new inverse_attribute(strings[3330], inverse_attribute::set_type, 0, -1, IFC4X1_IfcLocalPlacement_type, IFC4X1_IfcLocalPlacement_type->attributes()[0])
    });
    IFC4X1_IfcOpeningElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3331], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelFillsElement_type, IFC4X1_IfcRelFillsElement_type->attributes()[0])
    });
    IFC4X1_IfcOrganization_type->set_inverse_attributes({
            new inverse_attribute(strings[3332], inverse_attribute::set_type, 0, -1, IFC4X1_IfcOrganizationRelationship_type, IFC4X1_IfcOrganizationRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3268], inverse_attribute::set_type, 0, -1, IFC4X1_IfcOrganizationRelationship_type, IFC4X1_IfcOrganizationRelationship_type->attributes()[0]),
            new inverse_attribute(strings[3333], inverse_attribute::set_type, 0, -1, IFC4X1_IfcPersonAndOrganization_type, IFC4X1_IfcPersonAndOrganization_type->attributes()[1])
    });
    IFC4X1_IfcPerson_type->set_inverse_attributes({
            new inverse_attribute(strings[3334], inverse_attribute::set_type, 0, -1, IFC4X1_IfcPersonAndOrganization_type, IFC4X1_IfcPersonAndOrganization_type->attributes()[0])
    });
    IFC4X1_IfcPhysicalQuantity_type->set_inverse_attributes({
            new inverse_attribute(strings[3264], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3335], inverse_attribute::set_type, 0, 1, IFC4X1_IfcPhysicalComplexQuantity_type, IFC4X1_IfcPhysicalComplexQuantity_type->attributes()[0])
    });
    IFC4X1_IfcPort_type->set_inverse_attributes({
            new inverse_attribute(strings[3336], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelConnectsPortToElement_type, IFC4X1_IfcRelConnectsPortToElement_type->attributes()[0]),
            new inverse_attribute(strings[3297], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelConnectsPorts_type, IFC4X1_IfcRelConnectsPorts_type->attributes()[1]),
            new inverse_attribute(strings[3289], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelConnectsPorts_type, IFC4X1_IfcRelConnectsPorts_type->attributes()[0])
    });
    IFC4X1_IfcPositioningElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3263], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelContainedInSpatialStructure_type, IFC4X1_IfcRelContainedInSpatialStructure_type->attributes()[0])
    });
    IFC4X1_IfcProcess_type->set_inverse_attributes({
            new inverse_attribute(strings[3337], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelSequence_type, IFC4X1_IfcRelSequence_type->attributes()[0]),
            new inverse_attribute(strings[3338], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelSequence_type, IFC4X1_IfcRelSequence_type->attributes()[1]),
            new inverse_attribute(strings[3339], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToProcess_type, IFC4X1_IfcRelAssignsToProcess_type->attributes()[0])
    });
    IFC4X1_IfcProduct_type->set_inverse_attributes({
            new inverse_attribute(strings[3340], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToProduct_type, IFC4X1_IfcRelAssignsToProduct_type->attributes()[0])
    });
    IFC4X1_IfcProductDefinitionShape_type->set_inverse_attributes({
            new inverse_attribute(strings[3341], inverse_attribute::set_type, 1, -1, IFC4X1_IfcProduct_type, IFC4X1_IfcProduct_type->attributes()[1]),
            new inverse_attribute(strings[3342], inverse_attribute::set_type, 0, -1, IFC4X1_IfcShapeAspect_type, IFC4X1_IfcShapeAspect_type->attributes()[4])
    });
    IFC4X1_IfcProfileDef_type->set_inverse_attributes({
            new inverse_attribute(strings[3257], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[2523], inverse_attribute::set_type, 0, -1, IFC4X1_IfcProfileProperties_type, IFC4X1_IfcProfileProperties_type->attributes()[0])
    });
    IFC4X1_IfcProperty_type->set_inverse_attributes({
            new inverse_attribute(strings[3343], inverse_attribute::set_type, 0, -1, IFC4X1_IfcPropertySet_type, IFC4X1_IfcPropertySet_type->attributes()[0]),
            new inverse_attribute(strings[3344], inverse_attribute::set_type, 0, -1, IFC4X1_IfcPropertyDependencyRelationship_type, IFC4X1_IfcPropertyDependencyRelationship_type->attributes()[0]),
            new inverse_attribute(strings[3345], inverse_attribute::set_type, 0, -1, IFC4X1_IfcPropertyDependencyRelationship_type, IFC4X1_IfcPropertyDependencyRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3335], inverse_attribute::set_type, 0, -1, IFC4X1_IfcComplexProperty_type, IFC4X1_IfcComplexProperty_type->attributes()[1]),
            new inverse_attribute(strings[3346], inverse_attribute::set_type, 0, -1, IFC4X1_IfcResourceConstraintRelationship_type, IFC4X1_IfcResourceConstraintRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3347], inverse_attribute::set_type, 0, -1, IFC4X1_IfcResourceApprovalRelationship_type, IFC4X1_IfcResourceApprovalRelationship_type->attributes()[0])
    });
    IFC4X1_IfcPropertyAbstraction_type->set_inverse_attributes({
            new inverse_attribute(strings[3264], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X1_IfcPropertyDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3325], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelDeclares_type, IFC4X1_IfcRelDeclares_type->attributes()[1]),
            new inverse_attribute(strings[3328], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssociates_type, IFC4X1_IfcRelAssociates_type->attributes()[0])
    });
    IFC4X1_IfcPropertySetDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3348], inverse_attribute::set_type, 0, -1, IFC4X1_IfcTypeObject_type, IFC4X1_IfcTypeObject_type->attributes()[1]),
            new inverse_attribute(strings[3274], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelDefinesByTemplate_type, IFC4X1_IfcRelDefinesByTemplate_type->attributes()[0]),
            new inverse_attribute(strings[3349], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelDefinesByProperties_type, IFC4X1_IfcRelDefinesByProperties_type->attributes()[1])
    });
    IFC4X1_IfcPropertySetTemplate_type->set_inverse_attributes({
            new inverse_attribute(strings[3350], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelDefinesByTemplate_type, IFC4X1_IfcRelDefinesByTemplate_type->attributes()[1])
    });
    IFC4X1_IfcPropertyTemplate_type->set_inverse_attributes({
            new inverse_attribute(strings[3351], inverse_attribute::set_type, 0, -1, IFC4X1_IfcComplexPropertyTemplate_type, IFC4X1_IfcComplexPropertyTemplate_type->attributes()[2]),
            new inverse_attribute(strings[3352], inverse_attribute::set_type, 0, -1, IFC4X1_IfcPropertySetTemplate_type, IFC4X1_IfcPropertySetTemplate_type->attributes()[2])
    });
    IFC4X1_IfcRelSpaceBoundary1stLevel_type->set_inverse_attributes({
            new inverse_attribute(strings[2395], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelSpaceBoundary1stLevel_type, IFC4X1_IfcRelSpaceBoundary1stLevel_type->attributes()[0])
    });
    IFC4X1_IfcRelSpaceBoundary2ndLevel_type->set_inverse_attributes({
            new inverse_attribute(strings[3353], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelSpaceBoundary2ndLevel_type, IFC4X1_IfcRelSpaceBoundary2ndLevel_type->attributes()[0])
    });
    IFC4X1_IfcRepresentation_type->set_inverse_attributes({
            new inverse_attribute(strings[3354], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRepresentationMap_type, IFC4X1_IfcRepresentationMap_type->attributes()[1]),
            new inverse_attribute(strings[3355], inverse_attribute::set_type, 0, -1, IFC4X1_IfcPresentationLayerAssignment_type, IFC4X1_IfcPresentationLayerAssignment_type->attributes()[2]),
            new inverse_attribute(strings[3356], inverse_attribute::set_type, 0, -1, IFC4X1_IfcProductRepresentation_type, IFC4X1_IfcProductRepresentation_type->attributes()[2])
    });
    IFC4X1_IfcRepresentationContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3357], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRepresentation_type, IFC4X1_IfcRepresentation_type->attributes()[0])
    });
    IFC4X1_IfcRepresentationItem_type->set_inverse_attributes({
            new inverse_attribute(strings[3358], inverse_attribute::set_type, 0, 1, IFC4X1_IfcPresentationLayerAssignment_type, IFC4X1_IfcPresentationLayerAssignment_type->attributes()[2]),
            new inverse_attribute(strings[3359], inverse_attribute::set_type, 0, 1, IFC4X1_IfcStyledItem_type, IFC4X1_IfcStyledItem_type->attributes()[0])
    });
    IFC4X1_IfcRepresentationMap_type->set_inverse_attributes({
            new inverse_attribute(strings[3342], inverse_attribute::set_type, 0, -1, IFC4X1_IfcShapeAspect_type, IFC4X1_IfcShapeAspect_type->attributes()[4]),
            new inverse_attribute(strings[3360], inverse_attribute::set_type, 0, -1, IFC4X1_IfcMappedItem_type, IFC4X1_IfcMappedItem_type->attributes()[0])
    });
    IFC4X1_IfcResource_type->set_inverse_attributes({
            new inverse_attribute(strings[3361], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToResource_type, IFC4X1_IfcRelAssignsToResource_type->attributes()[0])
    });
    IFC4X1_IfcShapeAspect_type->set_inverse_attributes({
            new inverse_attribute(strings[3264], inverse_attribute::set_type, 0, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X1_IfcShapeModel_type->set_inverse_attributes({
            new inverse_attribute(strings[3362], inverse_attribute::set_type, 0, 1, IFC4X1_IfcShapeAspect_type, IFC4X1_IfcShapeAspect_type->attributes()[0])
    });
    IFC4X1_IfcSpace_type->set_inverse_attributes({
            new inverse_attribute(strings[3298], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelCoversSpaces_type, IFC4X1_IfcRelCoversSpaces_type->attributes()[0]),
            new inverse_attribute(strings[3300], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelSpaceBoundary_type, IFC4X1_IfcRelSpaceBoundary_type->attributes()[0])
    });
    IFC4X1_IfcSpatialElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3363], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelContainedInSpatialStructure_type, IFC4X1_IfcRelContainedInSpatialStructure_type->attributes()[1]),
            new inverse_attribute(strings[3364], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelServicesBuildings_type, IFC4X1_IfcRelServicesBuildings_type->attributes()[1]),
            new inverse_attribute(strings[3365], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelReferencedInSpatialStructure_type, IFC4X1_IfcRelReferencedInSpatialStructure_type->attributes()[1])
    });
    IFC4X1_IfcStructuralActivity_type->set_inverse_attributes({
            new inverse_attribute(strings[3366], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelConnectsStructuralActivity_type, IFC4X1_IfcRelConnectsStructuralActivity_type->attributes()[1])
    });
    IFC4X1_IfcStructuralConnection_type->set_inverse_attributes({
            new inverse_attribute(strings[3367], inverse_attribute::set_type, 1, -1, IFC4X1_IfcRelConnectsStructuralMember_type, IFC4X1_IfcRelConnectsStructuralMember_type->attributes()[1])
    });
    IFC4X1_IfcStructuralItem_type->set_inverse_attributes({
            new inverse_attribute(strings[3368], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelConnectsStructuralActivity_type, IFC4X1_IfcRelConnectsStructuralActivity_type->attributes()[0])
    });
    IFC4X1_IfcStructuralLoadGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3369], inverse_attribute::set_type, 0, 1, IFC4X1_IfcStructuralResultGroup_type, IFC4X1_IfcStructuralResultGroup_type->attributes()[1]),
            new inverse_attribute(strings[3370], inverse_attribute::set_type, 0, -1, IFC4X1_IfcStructuralAnalysisModel_type, IFC4X1_IfcStructuralAnalysisModel_type->attributes()[2])
    });
    IFC4X1_IfcStructuralMember_type->set_inverse_attributes({
            new inverse_attribute(strings[3371], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelConnectsStructuralMember_type, IFC4X1_IfcRelConnectsStructuralMember_type->attributes()[0])
    });
    IFC4X1_IfcStructuralResultGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3372], inverse_attribute::set_type, 0, 1, IFC4X1_IfcStructuralAnalysisModel_type, IFC4X1_IfcStructuralAnalysisModel_type->attributes()[3])
    });
    IFC4X1_IfcSurfaceTexture_type->set_inverse_attributes({
            new inverse_attribute(strings[3373], inverse_attribute::set_type, 0, -1, IFC4X1_IfcTextureCoordinate_type, IFC4X1_IfcTextureCoordinate_type->attributes()[0]),
            new inverse_attribute(strings[3374], inverse_attribute::set_type, 0, -1, IFC4X1_IfcSurfaceStyleWithTextures_type, IFC4X1_IfcSurfaceStyleWithTextures_type->attributes()[0])
    });
    IFC4X1_IfcSystem_type->set_inverse_attributes({
            new inverse_attribute(strings[3375], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelServicesBuildings_type, IFC4X1_IfcRelServicesBuildings_type->attributes()[0])
    });
    IFC4X1_IfcTessellatedFaceSet_type->set_inverse_attributes({
            new inverse_attribute(strings[3376], inverse_attribute::set_type, 0, 1, IFC4X1_IfcIndexedColourMap_type, IFC4X1_IfcIndexedColourMap_type->attributes()[0]),
            new inverse_attribute(strings[3377], inverse_attribute::set_type, 0, -1, IFC4X1_IfcIndexedTextureMap_type, IFC4X1_IfcIndexedTextureMap_type->attributes()[0])
    });
    IFC4X1_IfcTimeSeries_type->set_inverse_attributes({
            new inverse_attribute(strings[3257], inverse_attribute::set_type, 1, -1, IFC4X1_IfcExternalReferenceRelationship_type, IFC4X1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X1_IfcTypeObject_type->set_inverse_attributes({
            new inverse_attribute(strings[3378], inverse_attribute::set_type, 0, 1, IFC4X1_IfcRelDefinesByType_type, IFC4X1_IfcRelDefinesByType_type->attributes()[1])
    });
    IFC4X1_IfcTypeProcess_type->set_inverse_attributes({
            new inverse_attribute(strings[3339], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToProcess_type, IFC4X1_IfcRelAssignsToProcess_type->attributes()[0])
    });
    IFC4X1_IfcTypeProduct_type->set_inverse_attributes({
            new inverse_attribute(strings[3340], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToProduct_type, IFC4X1_IfcRelAssignsToProduct_type->attributes()[0])
    });
    IFC4X1_IfcTypeResource_type->set_inverse_attributes({
            new inverse_attribute(strings[3361], inverse_attribute::set_type, 0, -1, IFC4X1_IfcRelAssignsToResource_type, IFC4X1_IfcRelAssignsToResource_type->attributes()[0])
    });
    IFC4X1_IfcControl_type->set_subtypes({
        IFC4X1_IfcActionRequest_type,IFC4X1_IfcCostItem_type,IFC4X1_IfcCostSchedule_type,IFC4X1_IfcPerformanceHistory_type,IFC4X1_IfcPermit_type,IFC4X1_IfcProjectOrder_type,IFC4X1_IfcWorkCalendar_type,IFC4X1_IfcWorkControl_type
    });
    IFC4X1_IfcObject_type->set_subtypes({
        IFC4X1_IfcActor_type,IFC4X1_IfcControl_type,IFC4X1_IfcGroup_type,IFC4X1_IfcProcess_type,IFC4X1_IfcProduct_type,IFC4X1_IfcResource_type
    });
    IFC4X1_IfcDistributionControlElement_type->set_subtypes({
        IFC4X1_IfcActuator_type,IFC4X1_IfcAlarm_type,IFC4X1_IfcController_type,IFC4X1_IfcFlowInstrument_type,IFC4X1_IfcProtectiveDeviceTrippingUnit_type,IFC4X1_IfcSensor_type,IFC4X1_IfcUnitaryControlElement_type
    });
    IFC4X1_IfcDistributionControlElementType_type->set_subtypes({
        IFC4X1_IfcActuatorType_type,IFC4X1_IfcAlarmType_type,IFC4X1_IfcControllerType_type,IFC4X1_IfcFlowInstrumentType_type,IFC4X1_IfcProtectiveDeviceTrippingUnitType_type,IFC4X1_IfcSensorType_type,IFC4X1_IfcUnitaryControlElementType_type
    });
    IFC4X1_IfcManifoldSolidBrep_type->set_subtypes({
        IFC4X1_IfcAdvancedBrep_type,IFC4X1_IfcFacetedBrep_type
    });
    IFC4X1_IfcAdvancedBrep_type->set_subtypes({
        IFC4X1_IfcAdvancedBrepWithVoids_type
    });
    IFC4X1_IfcFaceSurface_type->set_subtypes({
        IFC4X1_IfcAdvancedFace_type
    });
    IFC4X1_IfcFlowTerminal_type->set_subtypes({
        IFC4X1_IfcAirTerminal_type,IFC4X1_IfcAudioVisualAppliance_type,IFC4X1_IfcCommunicationsAppliance_type,IFC4X1_IfcElectricAppliance_type,IFC4X1_IfcFireSuppressionTerminal_type,IFC4X1_IfcLamp_type,IFC4X1_IfcLightFixture_type,IFC4X1_IfcMedicalDevice_type,IFC4X1_IfcOutlet_type,IFC4X1_IfcSanitaryTerminal_type,IFC4X1_IfcSpaceHeater_type,IFC4X1_IfcStackTerminal_type,IFC4X1_IfcWasteTerminal_type
    });
    IFC4X1_IfcFlowController_type->set_subtypes({
        IFC4X1_IfcAirTerminalBox_type,IFC4X1_IfcDamper_type,IFC4X1_IfcElectricDistributionBoard_type,IFC4X1_IfcElectricTimeControl_type,IFC4X1_IfcFlowMeter_type,IFC4X1_IfcProtectiveDevice_type,IFC4X1_IfcSwitchingDevice_type,IFC4X1_IfcValve_type
    });
    IFC4X1_IfcFlowControllerType_type->set_subtypes({
        IFC4X1_IfcAirTerminalBoxType_type,IFC4X1_IfcDamperType_type,IFC4X1_IfcElectricDistributionBoardType_type,IFC4X1_IfcElectricTimeControlType_type,IFC4X1_IfcFlowMeterType_type,IFC4X1_IfcProtectiveDeviceType_type,IFC4X1_IfcSwitchingDeviceType_type,IFC4X1_IfcValveType_type
    });
    IFC4X1_IfcFlowTerminalType_type->set_subtypes({
        IFC4X1_IfcAirTerminalType_type,IFC4X1_IfcAudioVisualApplianceType_type,IFC4X1_IfcCommunicationsApplianceType_type,IFC4X1_IfcElectricApplianceType_type,IFC4X1_IfcFireSuppressionTerminalType_type,IFC4X1_IfcLampType_type,IFC4X1_IfcLightFixtureType_type,IFC4X1_IfcMedicalDeviceType_type,IFC4X1_IfcOutletType_type,IFC4X1_IfcSanitaryTerminalType_type,IFC4X1_IfcSpaceHeaterType_type,IFC4X1_IfcStackTerminalType_type,IFC4X1_IfcWasteTerminalType_type
    });
    IFC4X1_IfcEnergyConversionDevice_type->set_subtypes({
        IFC4X1_IfcAirToAirHeatRecovery_type,IFC4X1_IfcBoiler_type,IFC4X1_IfcBurner_type,IFC4X1_IfcChiller_type,IFC4X1_IfcCoil_type,IFC4X1_IfcCondenser_type,IFC4X1_IfcCooledBeam_type,IFC4X1_IfcCoolingTower_type,IFC4X1_IfcElectricGenerator_type,IFC4X1_IfcElectricMotor_type,IFC4X1_IfcEngine_type,IFC4X1_IfcEvaporativeCooler_type,IFC4X1_IfcEvaporator_type,IFC4X1_IfcHeatExchanger_type,IFC4X1_IfcHumidifier_type,IFC4X1_IfcMotorConnection_type,IFC4X1_IfcSolarDevice_type,IFC4X1_IfcTransformer_type,IFC4X1_IfcTubeBundle_type,IFC4X1_IfcUnitaryEquipment_type
    });
    IFC4X1_IfcEnergyConversionDeviceType_type->set_subtypes({
        IFC4X1_IfcAirToAirHeatRecoveryType_type,IFC4X1_IfcBoilerType_type,IFC4X1_IfcBurnerType_type,IFC4X1_IfcChillerType_type,IFC4X1_IfcCoilType_type,IFC4X1_IfcCondenserType_type,IFC4X1_IfcCooledBeamType_type,IFC4X1_IfcCoolingTowerType_type,IFC4X1_IfcElectricGeneratorType_type,IFC4X1_IfcElectricMotorType_type,IFC4X1_IfcEngineType_type,IFC4X1_IfcEvaporativeCoolerType_type,IFC4X1_IfcEvaporatorType_type,IFC4X1_IfcHeatExchangerType_type,IFC4X1_IfcHumidifierType_type,IFC4X1_IfcMotorConnectionType_type,IFC4X1_IfcSolarDeviceType_type,IFC4X1_IfcTransformerType_type,IFC4X1_IfcTubeBundleType_type,IFC4X1_IfcUnitaryEquipmentType_type
    });
    IFC4X1_IfcLinearPositioningElement_type->set_subtypes({
        IFC4X1_IfcAlignment_type
    });
    IFC4X1_IfcGeometricRepresentationItem_type->set_subtypes({
        IFC4X1_IfcAlignment2DHorizontal_type,IFC4X1_IfcAlignment2DSegment_type,IFC4X1_IfcAlignment2DVertical_type,IFC4X1_IfcAnnotationFillArea_type,IFC4X1_IfcBooleanResult_type,IFC4X1_IfcBoundingBox_type,IFC4X1_IfcCartesianPointList_type,IFC4X1_IfcCartesianTransformationOperator_type,IFC4X1_IfcCompositeCurveSegment_type,IFC4X1_IfcCsgPrimitive3D_type,IFC4X1_IfcCurve_type,IFC4X1_IfcDirection_type,IFC4X1_IfcDistanceExpression_type,IFC4X1_IfcFaceBasedSurfaceModel_type,IFC4X1_IfcFillAreaStyleHatching_type,IFC4X1_IfcFillAreaStyleTiles_type,IFC4X1_IfcGeometricSet_type,IFC4X1_IfcHalfSpaceSolid_type,IFC4X1_IfcLightSource_type,IFC4X1_IfcOrientationExpression_type,IFC4X1_IfcPlacement_type,IFC4X1_IfcPlanarExtent_type,IFC4X1_IfcPoint_type,IFC4X1_IfcSectionedSpine_type,IFC4X1_IfcShellBasedSurfaceModel_type,IFC4X1_IfcSolidModel_type,IFC4X1_IfcSurface_type,IFC4X1_IfcTessellatedItem_type,IFC4X1_IfcTextLiteral_type,IFC4X1_IfcVector_type
    });
    IFC4X1_IfcAlignment2DSegment_type->set_subtypes({
        IFC4X1_IfcAlignment2DHorizontalSegment_type,IFC4X1_IfcAlignment2DVerticalSegment_type
    });
    IFC4X1_IfcAlignment2DVerticalSegment_type->set_subtypes({
        IFC4X1_IfcAlignment2DVerSegCircularArc_type,IFC4X1_IfcAlignment2DVerSegLine_type,IFC4X1_IfcAlignment2DVerSegParabolicArc_type
    });
    IFC4X1_IfcBoundedCurve_type->set_subtypes({
        IFC4X1_IfcAlignmentCurve_type,IFC4X1_IfcBSplineCurve_type,IFC4X1_IfcCompositeCurve_type,IFC4X1_IfcCurveSegment2D_type,IFC4X1_IfcIndexedPolyCurve_type,IFC4X1_IfcPolyline_type,IFC4X1_IfcTrimmedCurve_type
    });
    IFC4X1_IfcProduct_type->set_subtypes({
        IFC4X1_IfcAnnotation_type,IFC4X1_IfcElement_type,IFC4X1_IfcPort_type,IFC4X1_IfcPositioningElement_type,IFC4X1_IfcProxy_type,IFC4X1_IfcSpatialElement_type,IFC4X1_IfcStructuralActivity_type,IFC4X1_IfcStructuralItem_type
    });
    IFC4X1_IfcResourceLevelRelationship_type->set_subtypes({
        IFC4X1_IfcApprovalRelationship_type,IFC4X1_IfcCurrencyRelationship_type,IFC4X1_IfcDocumentInformationRelationship_type,IFC4X1_IfcExternalReferenceRelationship_type,IFC4X1_IfcMaterialRelationship_type,IFC4X1_IfcOrganizationRelationship_type,IFC4X1_IfcPropertyDependencyRelationship_type,IFC4X1_IfcResourceApprovalRelationship_type,IFC4X1_IfcResourceConstraintRelationship_type
    });
    IFC4X1_IfcProfileDef_type->set_subtypes({
        IFC4X1_IfcArbitraryClosedProfileDef_type,IFC4X1_IfcArbitraryOpenProfileDef_type,IFC4X1_IfcCompositeProfileDef_type,IFC4X1_IfcDerivedProfileDef_type,IFC4X1_IfcParameterizedProfileDef_type
    });
    IFC4X1_IfcArbitraryClosedProfileDef_type->set_subtypes({
        IFC4X1_IfcArbitraryProfileDefWithVoids_type
    });
    IFC4X1_IfcGroup_type->set_subtypes({
        IFC4X1_IfcAsset_type,IFC4X1_IfcInventory_type,IFC4X1_IfcStructuralLoadGroup_type,IFC4X1_IfcStructuralResultGroup_type,IFC4X1_IfcSystem_type
    });
    IFC4X1_IfcParameterizedProfileDef_type->set_subtypes({
        IFC4X1_IfcAsymmetricIShapeProfileDef_type,IFC4X1_IfcCShapeProfileDef_type,IFC4X1_IfcCircleProfileDef_type,IFC4X1_IfcEllipseProfileDef_type,IFC4X1_IfcIShapeProfileDef_type,IFC4X1_IfcLShapeProfileDef_type,IFC4X1_IfcRectangleProfileDef_type,IFC4X1_IfcTShapeProfileDef_type,IFC4X1_IfcTrapeziumProfileDef_type,IFC4X1_IfcUShapeProfileDef_type,IFC4X1_IfcZShapeProfileDef_type
    });
    IFC4X1_IfcPlacement_type->set_subtypes({
        IFC4X1_IfcAxis1Placement_type,IFC4X1_IfcAxis2Placement2D_type,IFC4X1_IfcAxis2Placement3D_type
    });
    IFC4X1_IfcBSplineCurve_type->set_subtypes({
        IFC4X1_IfcBSplineCurveWithKnots_type
    });
    IFC4X1_IfcBoundedSurface_type->set_subtypes({
        IFC4X1_IfcBSplineSurface_type,IFC4X1_IfcCurveBoundedPlane_type,IFC4X1_IfcCurveBoundedSurface_type,IFC4X1_IfcRectangularTrimmedSurface_type
    });
    IFC4X1_IfcBSplineSurface_type->set_subtypes({
        IFC4X1_IfcBSplineSurfaceWithKnots_type
    });
    IFC4X1_IfcBuildingElement_type->set_subtypes({
        IFC4X1_IfcBeam_type,IFC4X1_IfcBuildingElementProxy_type,IFC4X1_IfcChimney_type,IFC4X1_IfcColumn_type,IFC4X1_IfcCovering_type,IFC4X1_IfcCurtainWall_type,IFC4X1_IfcDoor_type,IFC4X1_IfcFooting_type,IFC4X1_IfcMember_type,IFC4X1_IfcPile_type,IFC4X1_IfcPlate_type,IFC4X1_IfcRailing_type,IFC4X1_IfcRamp_type,IFC4X1_IfcRampFlight_type,IFC4X1_IfcRoof_type,IFC4X1_IfcShadingDevice_type,IFC4X1_IfcSlab_type,IFC4X1_IfcStair_type,IFC4X1_IfcStairFlight_type,IFC4X1_IfcWall_type,IFC4X1_IfcWindow_type
    });
    IFC4X1_IfcBeam_type->set_subtypes({
        IFC4X1_IfcBeamStandardCase_type
    });
    IFC4X1_IfcBuildingElementType_type->set_subtypes({
        IFC4X1_IfcBeamType_type,IFC4X1_IfcBuildingElementProxyType_type,IFC4X1_IfcChimneyType_type,IFC4X1_IfcColumnType_type,IFC4X1_IfcCoveringType_type,IFC4X1_IfcCurtainWallType_type,IFC4X1_IfcDoorType_type,IFC4X1_IfcFootingType_type,IFC4X1_IfcMemberType_type,IFC4X1_IfcPileType_type,IFC4X1_IfcPlateType_type,IFC4X1_IfcRailingType_type,IFC4X1_IfcRampFlightType_type,IFC4X1_IfcRampType_type,IFC4X1_IfcRoofType_type,IFC4X1_IfcShadingDeviceType_type,IFC4X1_IfcSlabType_type,IFC4X1_IfcStairFlightType_type,IFC4X1_IfcStairType_type,IFC4X1_IfcWallType_type,IFC4X1_IfcWindowType_type
    });
    IFC4X1_IfcSurfaceTexture_type->set_subtypes({
        IFC4X1_IfcBlobTexture_type,IFC4X1_IfcImageTexture_type,IFC4X1_IfcPixelTexture_type
    });
    IFC4X1_IfcCsgPrimitive3D_type->set_subtypes({
        IFC4X1_IfcBlock_type,IFC4X1_IfcRectangularPyramid_type,IFC4X1_IfcRightCircularCone_type,IFC4X1_IfcRightCircularCylinder_type,IFC4X1_IfcSphere_type
    });
    IFC4X1_IfcBooleanResult_type->set_subtypes({
        IFC4X1_IfcBooleanClippingResult_type
    });
    IFC4X1_IfcCompositeCurveOnSurface_type->set_subtypes({
        IFC4X1_IfcBoundaryCurve_type
    });
    IFC4X1_IfcBoundaryCondition_type->set_subtypes({
        IFC4X1_IfcBoundaryEdgeCondition_type,IFC4X1_IfcBoundaryFaceCondition_type,IFC4X1_IfcBoundaryNodeCondition_type
    });
    IFC4X1_IfcBoundaryNodeCondition_type->set_subtypes({
        IFC4X1_IfcBoundaryNodeConditionWarping_type
    });
    IFC4X1_IfcCurve_type->set_subtypes({
        IFC4X1_IfcBoundedCurve_type,IFC4X1_IfcConic_type,IFC4X1_IfcLine_type,IFC4X1_IfcOffsetCurve_type,IFC4X1_IfcPcurve_type,IFC4X1_IfcSurfaceCurve_type
    });
    IFC4X1_IfcSurface_type->set_subtypes({
        IFC4X1_IfcBoundedSurface_type,IFC4X1_IfcElementarySurface_type,IFC4X1_IfcSweptSurface_type
    });
    IFC4X1_IfcHalfSpaceSolid_type->set_subtypes({
        IFC4X1_IfcBoxedHalfSpace_type,IFC4X1_IfcPolygonalBoundedHalfSpace_type
    });
    IFC4X1_IfcSpatialStructureElement_type->set_subtypes({
        IFC4X1_IfcBuilding_type,IFC4X1_IfcBuildingStorey_type,IFC4X1_IfcSite_type,IFC4X1_IfcSpace_type
    });
    IFC4X1_IfcElement_type->set_subtypes({
        IFC4X1_IfcBuildingElement_type,IFC4X1_IfcCivilElement_type,IFC4X1_IfcDistributionElement_type,IFC4X1_IfcElementAssembly_type,IFC4X1_IfcElementComponent_type,IFC4X1_IfcFeatureElement_type,IFC4X1_IfcFurnishingElement_type,IFC4X1_IfcGeographicElement_type,IFC4X1_IfcTransportElement_type,IFC4X1_IfcVirtualElement_type
    });
    IFC4X1_IfcElementComponent_type->set_subtypes({
        IFC4X1_IfcBuildingElementPart_type,IFC4X1_IfcDiscreteAccessory_type,IFC4X1_IfcFastener_type,IFC4X1_IfcMechanicalFastener_type,IFC4X1_IfcReinforcingElement_type,IFC4X1_IfcVibrationIsolator_type
    });
    IFC4X1_IfcElementComponentType_type->set_subtypes({
        IFC4X1_IfcBuildingElementPartType_type,IFC4X1_IfcDiscreteAccessoryType_type,IFC4X1_IfcFastenerType_type,IFC4X1_IfcMechanicalFastenerType_type,IFC4X1_IfcReinforcingElementType_type,IFC4X1_IfcVibrationIsolatorType_type
    });
    IFC4X1_IfcElementType_type->set_subtypes({
        IFC4X1_IfcBuildingElementType_type,IFC4X1_IfcCivilElementType_type,IFC4X1_IfcDistributionElementType_type,IFC4X1_IfcElementAssemblyType_type,IFC4X1_IfcElementComponentType_type,IFC4X1_IfcFurnishingElementType_type,IFC4X1_IfcGeographicElementType_type,IFC4X1_IfcTransportElementType_type
    });
    IFC4X1_IfcSystem_type->set_subtypes({
        IFC4X1_IfcBuildingSystem_type,IFC4X1_IfcDistributionSystem_type,IFC4X1_IfcStructuralAnalysisModel_type,IFC4X1_IfcZone_type
    });
    IFC4X1_IfcFlowFitting_type->set_subtypes({
        IFC4X1_IfcCableCarrierFitting_type,IFC4X1_IfcCableFitting_type,IFC4X1_IfcDuctFitting_type,IFC4X1_IfcJunctionBox_type,IFC4X1_IfcPipeFitting_type
    });
    IFC4X1_IfcFlowFittingType_type->set_subtypes({
        IFC4X1_IfcCableCarrierFittingType_type,IFC4X1_IfcCableFittingType_type,IFC4X1_IfcDuctFittingType_type,IFC4X1_IfcJunctionBoxType_type,IFC4X1_IfcPipeFittingType_type
    });
    IFC4X1_IfcFlowSegment_type->set_subtypes({
        IFC4X1_IfcCableCarrierSegment_type,IFC4X1_IfcCableSegment_type,IFC4X1_IfcDuctSegment_type,IFC4X1_IfcPipeSegment_type
    });
    IFC4X1_IfcFlowSegmentType_type->set_subtypes({
        IFC4X1_IfcCableCarrierSegmentType_type,IFC4X1_IfcCableSegmentType_type,IFC4X1_IfcDuctSegmentType_type,IFC4X1_IfcPipeSegmentType_type
    });
    IFC4X1_IfcPoint_type->set_subtypes({
        IFC4X1_IfcCartesianPoint_type,IFC4X1_IfcPointOnCurve_type,IFC4X1_IfcPointOnSurface_type
    });
    IFC4X1_IfcCartesianPointList_type->set_subtypes({
        IFC4X1_IfcCartesianPointList2D_type,IFC4X1_IfcCartesianPointList3D_type
    });
    IFC4X1_IfcCartesianTransformationOperator_type->set_subtypes({
        IFC4X1_IfcCartesianTransformationOperator2D_type,IFC4X1_IfcCartesianTransformationOperator3D_type
    });
    IFC4X1_IfcCartesianTransformationOperator2D_type->set_subtypes({
        IFC4X1_IfcCartesianTransformationOperator2DnonUniform_type
    });
    IFC4X1_IfcCartesianTransformationOperator3D_type->set_subtypes({
        IFC4X1_IfcCartesianTransformationOperator3DnonUniform_type
    });
    IFC4X1_IfcArbitraryOpenProfileDef_type->set_subtypes({
        IFC4X1_IfcCenterLineProfileDef_type
    });
    IFC4X1_IfcConic_type->set_subtypes({
        IFC4X1_IfcCircle_type,IFC4X1_IfcEllipse_type
    });
    IFC4X1_IfcCircleProfileDef_type->set_subtypes({
        IFC4X1_IfcCircleHollowProfileDef_type
    });
    IFC4X1_IfcCurveSegment2D_type->set_subtypes({
        IFC4X1_IfcCircularArcSegment2D_type,IFC4X1_IfcLineSegment2D_type,IFC4X1_IfcTransitionCurveSegment2D_type
    });
    IFC4X1_IfcExternalInformation_type->set_subtypes({
        IFC4X1_IfcClassification_type,IFC4X1_IfcDocumentInformation_type,IFC4X1_IfcLibraryInformation_type
    });
    IFC4X1_IfcExternalReference_type->set_subtypes({
        IFC4X1_IfcClassificationReference_type,IFC4X1_IfcDocumentReference_type,IFC4X1_IfcExternallyDefinedHatchStyle_type,IFC4X1_IfcExternallyDefinedSurfaceStyle_type,IFC4X1_IfcExternallyDefinedTextFont_type,IFC4X1_IfcLibraryReference_type
    });
    IFC4X1_IfcConnectedFaceSet_type->set_subtypes({
        IFC4X1_IfcClosedShell_type,IFC4X1_IfcOpenShell_type
    });
    IFC4X1_IfcColourSpecification_type->set_subtypes({
        IFC4X1_IfcColourRgb_type
    });
    IFC4X1_IfcPresentationItem_type->set_subtypes({
        IFC4X1_IfcColourRgbList_type,IFC4X1_IfcColourSpecification_type,IFC4X1_IfcCurveStyleFont_type,IFC4X1_IfcCurveStyleFontAndScaling_type,IFC4X1_IfcCurveStyleFontPattern_type,IFC4X1_IfcIndexedColourMap_type,IFC4X1_IfcPreDefinedItem_type,IFC4X1_IfcSurfaceStyleLighting_type,IFC4X1_IfcSurfaceStyleRefraction_type,IFC4X1_IfcSurfaceStyleShading_type,IFC4X1_IfcSurfaceStyleWithTextures_type,IFC4X1_IfcSurfaceTexture_type,IFC4X1_IfcTextStyleForDefinedFont_type,IFC4X1_IfcTextStyleTextModel_type,IFC4X1_IfcTextureCoordinate_type,IFC4X1_IfcTextureVertex_type,IFC4X1_IfcTextureVertexList_type
    });
    IFC4X1_IfcColumn_type->set_subtypes({
        IFC4X1_IfcColumnStandardCase_type
    });
    IFC4X1_IfcProperty_type->set_subtypes({
        IFC4X1_IfcComplexProperty_type,IFC4X1_IfcSimpleProperty_type
    });
    IFC4X1_IfcPropertyTemplate_type->set_subtypes({
        IFC4X1_IfcComplexPropertyTemplate_type,IFC4X1_IfcSimplePropertyTemplate_type
    });
    IFC4X1_IfcCompositeCurve_type->set_subtypes({
        IFC4X1_IfcCompositeCurveOnSurface_type
    });
    IFC4X1_IfcFlowMovingDevice_type->set_subtypes({
        IFC4X1_IfcCompressor_type,IFC4X1_IfcFan_type,IFC4X1_IfcPump_type
    });
    IFC4X1_IfcFlowMovingDeviceType_type->set_subtypes({
        IFC4X1_IfcCompressorType_type,IFC4X1_IfcFanType_type,IFC4X1_IfcPumpType_type
    });
    IFC4X1_IfcTopologicalRepresentationItem_type->set_subtypes({
        IFC4X1_IfcConnectedFaceSet_type,IFC4X1_IfcEdge_type,IFC4X1_IfcFace_type,IFC4X1_IfcFaceBound_type,IFC4X1_IfcLoop_type,IFC4X1_IfcPath_type,IFC4X1_IfcVertex_type
    });
    IFC4X1_IfcConnectionGeometry_type->set_subtypes({
        IFC4X1_IfcConnectionCurveGeometry_type,IFC4X1_IfcConnectionPointGeometry_type,IFC4X1_IfcConnectionSurfaceGeometry_type,IFC4X1_IfcConnectionVolumeGeometry_type
    });
    IFC4X1_IfcConnectionPointGeometry_type->set_subtypes({
        IFC4X1_IfcConnectionPointEccentricity_type
    });
    IFC4X1_IfcConstructionResource_type->set_subtypes({
        IFC4X1_IfcConstructionEquipmentResource_type,IFC4X1_IfcConstructionMaterialResource_type,IFC4X1_IfcConstructionProductResource_type,IFC4X1_IfcCrewResource_type,IFC4X1_IfcLaborResource_type,IFC4X1_IfcSubContractResource_type
    });
    IFC4X1_IfcConstructionResourceType_type->set_subtypes({
        IFC4X1_IfcConstructionEquipmentResourceType_type,IFC4X1_IfcConstructionMaterialResourceType_type,IFC4X1_IfcConstructionProductResourceType_type,IFC4X1_IfcCrewResourceType_type,IFC4X1_IfcLaborResourceType_type,IFC4X1_IfcSubContractResourceType_type
    });
    IFC4X1_IfcResource_type->set_subtypes({
        IFC4X1_IfcConstructionResource_type
    });
    IFC4X1_IfcTypeResource_type->set_subtypes({
        IFC4X1_IfcConstructionResourceType_type
    });
    IFC4X1_IfcObjectDefinition_type->set_subtypes({
        IFC4X1_IfcContext_type,IFC4X1_IfcObject_type,IFC4X1_IfcTypeObject_type
    });
    IFC4X1_IfcNamedUnit_type->set_subtypes({
        IFC4X1_IfcContextDependentUnit_type,IFC4X1_IfcConversionBasedUnit_type,IFC4X1_IfcSIUnit_type
    });
    IFC4X1_IfcConversionBasedUnit_type->set_subtypes({
        IFC4X1_IfcConversionBasedUnitWithOffset_type
    });
    IFC4X1_IfcAppliedValue_type->set_subtypes({
        IFC4X1_IfcCostValue_type
    });
    IFC4X1_IfcSolidModel_type->set_subtypes({
        IFC4X1_IfcCsgSolid_type,IFC4X1_IfcManifoldSolidBrep_type,IFC4X1_IfcSectionedSolid_type,IFC4X1_IfcSweptAreaSolid_type,IFC4X1_IfcSweptDiskSolid_type
    });
    IFC4X1_IfcPresentationStyle_type->set_subtypes({
        IFC4X1_IfcCurveStyle_type,IFC4X1_IfcFillAreaStyle_type,IFC4X1_IfcSurfaceStyle_type,IFC4X1_IfcTextStyle_type
    });
    IFC4X1_IfcElementarySurface_type->set_subtypes({
        IFC4X1_IfcCylindricalSurface_type,IFC4X1_IfcPlane_type,IFC4X1_IfcSphericalSurface_type,IFC4X1_IfcToroidalSurface_type
    });
    IFC4X1_IfcDistributionFlowElement_type->set_subtypes({
        IFC4X1_IfcDistributionChamberElement_type,IFC4X1_IfcEnergyConversionDevice_type,IFC4X1_IfcFlowController_type,IFC4X1_IfcFlowFitting_type,IFC4X1_IfcFlowMovingDevice_type,IFC4X1_IfcFlowSegment_type,IFC4X1_IfcFlowStorageDevice_type,IFC4X1_IfcFlowTerminal_type,IFC4X1_IfcFlowTreatmentDevice_type
    });
    IFC4X1_IfcDistributionFlowElementType_type->set_subtypes({
        IFC4X1_IfcDistributionChamberElementType_type,IFC4X1_IfcEnergyConversionDeviceType_type,IFC4X1_IfcFlowControllerType_type,IFC4X1_IfcFlowFittingType_type,IFC4X1_IfcFlowMovingDeviceType_type,IFC4X1_IfcFlowSegmentType_type,IFC4X1_IfcFlowStorageDeviceType_type,IFC4X1_IfcFlowTerminalType_type,IFC4X1_IfcFlowTreatmentDeviceType_type
    });
    IFC4X1_IfcDistributionSystem_type->set_subtypes({
        IFC4X1_IfcDistributionCircuit_type
    });
    IFC4X1_IfcDistributionElement_type->set_subtypes({
        IFC4X1_IfcDistributionControlElement_type,IFC4X1_IfcDistributionFlowElement_type
    });
    IFC4X1_IfcDistributionElementType_type->set_subtypes({
        IFC4X1_IfcDistributionControlElementType_type,IFC4X1_IfcDistributionFlowElementType_type
    });
    IFC4X1_IfcPort_type->set_subtypes({
        IFC4X1_IfcDistributionPort_type
    });
    IFC4X1_IfcPreDefinedPropertySet_type->set_subtypes({
        IFC4X1_IfcDoorLiningProperties_type,IFC4X1_IfcDoorPanelProperties_type,IFC4X1_IfcPermeableCoveringProperties_type,IFC4X1_IfcReinforcementDefinitionProperties_type,IFC4X1_IfcWindowLiningProperties_type,IFC4X1_IfcWindowPanelProperties_type
    });
    IFC4X1_IfcDoor_type->set_subtypes({
        IFC4X1_IfcDoorStandardCase_type
    });
    IFC4X1_IfcTypeProduct_type->set_subtypes({
        IFC4X1_IfcDoorStyle_type,IFC4X1_IfcElementType_type,IFC4X1_IfcSpatialElementType_type,IFC4X1_IfcWindowStyle_type
    });
    IFC4X1_IfcPreDefinedColour_type->set_subtypes({
        IFC4X1_IfcDraughtingPreDefinedColour_type
    });
    IFC4X1_IfcPreDefinedCurveFont_type->set_subtypes({
        IFC4X1_IfcDraughtingPreDefinedCurveFont_type
    });
    IFC4X1_IfcFlowTreatmentDevice_type->set_subtypes({
        IFC4X1_IfcDuctSilencer_type,IFC4X1_IfcFilter_type,IFC4X1_IfcInterceptor_type
    });
    IFC4X1_IfcFlowTreatmentDeviceType_type->set_subtypes({
        IFC4X1_IfcDuctSilencerType_type,IFC4X1_IfcFilterType_type,IFC4X1_IfcInterceptorType_type
    });
    IFC4X1_IfcEdge_type->set_subtypes({
        IFC4X1_IfcEdgeCurve_type,IFC4X1_IfcOrientedEdge_type,IFC4X1_IfcSubedge_type
    });
    IFC4X1_IfcLoop_type->set_subtypes({
        IFC4X1_IfcEdgeLoop_type,IFC4X1_IfcPolyLoop_type,IFC4X1_IfcVertexLoop_type
    });
    IFC4X1_IfcFlowStorageDevice_type->set_subtypes({
        IFC4X1_IfcElectricFlowStorageDevice_type,IFC4X1_IfcTank_type
    });
    IFC4X1_IfcFlowStorageDeviceType_type->set_subtypes({
        IFC4X1_IfcElectricFlowStorageDeviceType_type,IFC4X1_IfcTankType_type
    });
    IFC4X1_IfcQuantitySet_type->set_subtypes({
        IFC4X1_IfcElementQuantity_type
    });
    IFC4X1_IfcProcess_type->set_subtypes({
        IFC4X1_IfcEvent_type,IFC4X1_IfcProcedure_type,IFC4X1_IfcTask_type
    });
    IFC4X1_IfcSchedulingTime_type->set_subtypes({
        IFC4X1_IfcEventTime_type,IFC4X1_IfcLagTime_type,IFC4X1_IfcResourceTime_type,IFC4X1_IfcTaskTime_type,IFC4X1_IfcWorkTime_type
    });
    IFC4X1_IfcTypeProcess_type->set_subtypes({
        IFC4X1_IfcEventType_type,IFC4X1_IfcProcedureType_type,IFC4X1_IfcTaskType_type
    });
    IFC4X1_IfcPropertyAbstraction_type->set_subtypes({
        IFC4X1_IfcExtendedProperties_type,IFC4X1_IfcPreDefinedProperties_type,IFC4X1_IfcProperty_type,IFC4X1_IfcPropertyEnumeration_type
    });
    IFC4X1_IfcExternalSpatialStructureElement_type->set_subtypes({
        IFC4X1_IfcExternalSpatialElement_type
    });
    IFC4X1_IfcSpatialElement_type->set_subtypes({
        IFC4X1_IfcExternalSpatialStructureElement_type,IFC4X1_IfcSpatialStructureElement_type,IFC4X1_IfcSpatialZone_type
    });
    IFC4X1_IfcSweptAreaSolid_type->set_subtypes({
        IFC4X1_IfcExtrudedAreaSolid_type,IFC4X1_IfcFixedReferenceSweptAreaSolid_type,IFC4X1_IfcRevolvedAreaSolid_type,IFC4X1_IfcSurfaceCurveSweptAreaSolid_type
    });
    IFC4X1_IfcExtrudedAreaSolid_type->set_subtypes({
        IFC4X1_IfcExtrudedAreaSolidTapered_type
    });
    IFC4X1_IfcFaceBound_type->set_subtypes({
        IFC4X1_IfcFaceOuterBound_type
    });
    IFC4X1_IfcFace_type->set_subtypes({
        IFC4X1_IfcFaceSurface_type
    });
    IFC4X1_IfcFacetedBrep_type->set_subtypes({
        IFC4X1_IfcFacetedBrepWithVoids_type
    });
    IFC4X1_IfcStructuralConnectionCondition_type->set_subtypes({
        IFC4X1_IfcFailureConnectionCondition_type,IFC4X1_IfcSlippageConnectionCondition_type
    });
    IFC4X1_IfcFeatureElement_type->set_subtypes({
        IFC4X1_IfcFeatureElementAddition_type,IFC4X1_IfcFeatureElementSubtraction_type,IFC4X1_IfcSurfaceFeature_type
    });
    IFC4X1_IfcFurnishingElement_type->set_subtypes({
        IFC4X1_IfcFurniture_type,IFC4X1_IfcSystemFurnitureElement_type
    });
    IFC4X1_IfcFurnishingElementType_type->set_subtypes({
        IFC4X1_IfcFurnitureType_type,IFC4X1_IfcSystemFurnitureElementType_type
    });
    IFC4X1_IfcGeometricSet_type->set_subtypes({
        IFC4X1_IfcGeometricCurveSet_type
    });
    IFC4X1_IfcRepresentationContext_type->set_subtypes({
        IFC4X1_IfcGeometricRepresentationContext_type
    });
    IFC4X1_IfcRepresentationItem_type->set_subtypes({
        IFC4X1_IfcGeometricRepresentationItem_type,IFC4X1_IfcMappedItem_type,IFC4X1_IfcStyledItem_type,IFC4X1_IfcTopologicalRepresentationItem_type
    });
    IFC4X1_IfcGeometricRepresentationContext_type->set_subtypes({
        IFC4X1_IfcGeometricRepresentationSubContext_type
    });
    IFC4X1_IfcPositioningElement_type->set_subtypes({
        IFC4X1_IfcGrid_type,IFC4X1_IfcLinearPositioningElement_type,IFC4X1_IfcReferent_type
    });
    IFC4X1_IfcObjectPlacement_type->set_subtypes({
        IFC4X1_IfcGridPlacement_type,IFC4X1_IfcLinearPlacement_type,IFC4X1_IfcLocalPlacement_type
    });
    IFC4X1_IfcTessellatedItem_type->set_subtypes({
        IFC4X1_IfcIndexedPolygonalFace_type,IFC4X1_IfcTessellatedFaceSet_type
    });
    IFC4X1_IfcIndexedPolygonalFace_type->set_subtypes({
        IFC4X1_IfcIndexedPolygonalFaceWithVoids_type
    });
    IFC4X1_IfcTextureCoordinate_type->set_subtypes({
        IFC4X1_IfcIndexedTextureMap_type,IFC4X1_IfcTextureCoordinateGenerator_type,IFC4X1_IfcTextureMap_type
    });
    IFC4X1_IfcIndexedTextureMap_type->set_subtypes({
        IFC4X1_IfcIndexedTriangleTextureMap_type
    });
    IFC4X1_IfcSurfaceCurve_type->set_subtypes({
        IFC4X1_IfcIntersectionCurve_type,IFC4X1_IfcSeamCurve_type
    });
    IFC4X1_IfcTimeSeries_type->set_subtypes({
        IFC4X1_IfcIrregularTimeSeries_type,IFC4X1_IfcRegularTimeSeries_type
    });
    IFC4X1_IfcLightSource_type->set_subtypes({
        IFC4X1_IfcLightSourceAmbient_type,IFC4X1_IfcLightSourceDirectional_type,IFC4X1_IfcLightSourceGoniometric_type,IFC4X1_IfcLightSourcePositional_type
    });
    IFC4X1_IfcLightSourcePositional_type->set_subtypes({
        IFC4X1_IfcLightSourceSpot_type
    });
    IFC4X1_IfcCoordinateOperation_type->set_subtypes({
        IFC4X1_IfcMapConversion_type
    });
    IFC4X1_IfcMaterialDefinition_type->set_subtypes({
        IFC4X1_IfcMaterial_type,IFC4X1_IfcMaterialConstituent_type,IFC4X1_IfcMaterialConstituentSet_type,IFC4X1_IfcMaterialLayer_type,IFC4X1_IfcMaterialLayerSet_type,IFC4X1_IfcMaterialProfile_type,IFC4X1_IfcMaterialProfileSet_type
    });
    IFC4X1_IfcProductRepresentation_type->set_subtypes({
        IFC4X1_IfcMaterialDefinitionRepresentation_type,IFC4X1_IfcProductDefinitionShape_type
    });
    IFC4X1_IfcMaterialUsageDefinition_type->set_subtypes({
        IFC4X1_IfcMaterialLayerSetUsage_type,IFC4X1_IfcMaterialProfileSetUsage_type
    });
    IFC4X1_IfcMaterialLayer_type->set_subtypes({
        IFC4X1_IfcMaterialLayerWithOffsets_type
    });
    IFC4X1_IfcMaterialProfileSetUsage_type->set_subtypes({
        IFC4X1_IfcMaterialProfileSetUsageTapering_type
    });
    IFC4X1_IfcMaterialProfile_type->set_subtypes({
        IFC4X1_IfcMaterialProfileWithOffsets_type
    });
    IFC4X1_IfcExtendedProperties_type->set_subtypes({
        IFC4X1_IfcMaterialProperties_type,IFC4X1_IfcProfileProperties_type
    });
    IFC4X1_IfcMember_type->set_subtypes({
        IFC4X1_IfcMemberStandardCase_type
    });
    IFC4X1_IfcConstraint_type->set_subtypes({
        IFC4X1_IfcMetric_type,IFC4X1_IfcObjective_type
    });
    IFC4X1_IfcDerivedProfileDef_type->set_subtypes({
        IFC4X1_IfcMirroredProfileDef_type
    });
    IFC4X1_IfcRoot_type->set_subtypes({
        IFC4X1_IfcObjectDefinition_type,IFC4X1_IfcPropertyDefinition_type,IFC4X1_IfcRelationship_type
    });
    IFC4X1_IfcActor_type->set_subtypes({
        IFC4X1_IfcOccupant_type
    });
    IFC4X1_IfcOffsetCurve_type->set_subtypes({
        IFC4X1_IfcOffsetCurve2D_type,IFC4X1_IfcOffsetCurve3D_type,IFC4X1_IfcOffsetCurveByDistances_type
    });
    IFC4X1_IfcFeatureElementSubtraction_type->set_subtypes({
        IFC4X1_IfcOpeningElement_type,IFC4X1_IfcVoidingFeature_type
    });
    IFC4X1_IfcOpeningElement_type->set_subtypes({
        IFC4X1_IfcOpeningStandardCase_type
    });
    IFC4X1_IfcBoundaryCurve_type->set_subtypes({
        IFC4X1_IfcOuterBoundaryCurve_type
    });
    IFC4X1_IfcPhysicalQuantity_type->set_subtypes({
        IFC4X1_IfcPhysicalComplexQuantity_type,IFC4X1_IfcPhysicalSimpleQuantity_type
    });
    IFC4X1_IfcPlanarExtent_type->set_subtypes({
        IFC4X1_IfcPlanarBox_type
    });
    IFC4X1_IfcPlate_type->set_subtypes({
        IFC4X1_IfcPlateStandardCase_type
    });
    IFC4X1_IfcTessellatedFaceSet_type->set_subtypes({
        IFC4X1_IfcPolygonalFaceSet_type,IFC4X1_IfcTriangulatedFaceSet_type
    });
    IFC4X1_IfcAddress_type->set_subtypes({
        IFC4X1_IfcPostalAddress_type,IFC4X1_IfcTelecomAddress_type
    });
    IFC4X1_IfcPreDefinedItem_type->set_subtypes({
        IFC4X1_IfcPreDefinedColour_type,IFC4X1_IfcPreDefinedCurveFont_type,IFC4X1_IfcPreDefinedTextFont_type
    });
    IFC4X1_IfcPropertySetDefinition_type->set_subtypes({
        IFC4X1_IfcPreDefinedPropertySet_type,IFC4X1_IfcPropertySet_type,IFC4X1_IfcQuantitySet_type
    });
    IFC4X1_IfcPresentationLayerAssignment_type->set_subtypes({
        IFC4X1_IfcPresentationLayerWithStyle_type
    });
    IFC4X1_IfcContext_type->set_subtypes({
        IFC4X1_IfcProject_type,IFC4X1_IfcProjectLibrary_type
    });
    IFC4X1_IfcCoordinateReferenceSystem_type->set_subtypes({
        IFC4X1_IfcProjectedCRS_type
    });
    IFC4X1_IfcFeatureElementAddition_type->set_subtypes({
        IFC4X1_IfcProjectionElement_type
    });
    IFC4X1_IfcSimpleProperty_type->set_subtypes({
        IFC4X1_IfcPropertyBoundedValue_type,IFC4X1_IfcPropertyEnumeratedValue_type,IFC4X1_IfcPropertyListValue_type,IFC4X1_IfcPropertyReferenceValue_type,IFC4X1_IfcPropertySingleValue_type,IFC4X1_IfcPropertyTableValue_type
    });
    IFC4X1_IfcPropertyDefinition_type->set_subtypes({
        IFC4X1_IfcPropertySetDefinition_type,IFC4X1_IfcPropertyTemplateDefinition_type
    });
    IFC4X1_IfcPropertyTemplateDefinition_type->set_subtypes({
        IFC4X1_IfcPropertySetTemplate_type,IFC4X1_IfcPropertyTemplate_type
    });
    IFC4X1_IfcPhysicalSimpleQuantity_type->set_subtypes({
        IFC4X1_IfcQuantityArea_type,IFC4X1_IfcQuantityCount_type,IFC4X1_IfcQuantityLength_type,IFC4X1_IfcQuantityTime_type,IFC4X1_IfcQuantityVolume_type,IFC4X1_IfcQuantityWeight_type
    });
    IFC4X1_IfcBSplineCurveWithKnots_type->set_subtypes({
        IFC4X1_IfcRationalBSplineCurveWithKnots_type
    });
    IFC4X1_IfcBSplineSurfaceWithKnots_type->set_subtypes({
        IFC4X1_IfcRationalBSplineSurfaceWithKnots_type
    });
    IFC4X1_IfcRectangleProfileDef_type->set_subtypes({
        IFC4X1_IfcRectangleHollowProfileDef_type,IFC4X1_IfcRoundedRectangleProfileDef_type
    });
    IFC4X1_IfcPreDefinedProperties_type->set_subtypes({
        IFC4X1_IfcReinforcementBarProperties_type,IFC4X1_IfcSectionProperties_type,IFC4X1_IfcSectionReinforcementProperties_type
    });
    IFC4X1_IfcReinforcingElement_type->set_subtypes({
        IFC4X1_IfcReinforcingBar_type,IFC4X1_IfcReinforcingMesh_type,IFC4X1_IfcTendon_type,IFC4X1_IfcTendonAnchor_type
    });
    IFC4X1_IfcReinforcingElementType_type->set_subtypes({
        IFC4X1_IfcReinforcingBarType_type,IFC4X1_IfcReinforcingMeshType_type,IFC4X1_IfcTendonAnchorType_type,IFC4X1_IfcTendonType_type
    });
    IFC4X1_IfcRelDecomposes_type->set_subtypes({
        IFC4X1_IfcRelAggregates_type,IFC4X1_IfcRelNests_type,IFC4X1_IfcRelProjectsElement_type,IFC4X1_IfcRelVoidsElement_type
    });
    IFC4X1_IfcRelationship_type->set_subtypes({
        IFC4X1_IfcRelAssigns_type,IFC4X1_IfcRelAssociates_type,IFC4X1_IfcRelConnects_type,IFC4X1_IfcRelDeclares_type,IFC4X1_IfcRelDecomposes_type,IFC4X1_IfcRelDefines_type
    });
    IFC4X1_IfcRelAssigns_type->set_subtypes({
        IFC4X1_IfcRelAssignsToActor_type,IFC4X1_IfcRelAssignsToControl_type,IFC4X1_IfcRelAssignsToGroup_type,IFC4X1_IfcRelAssignsToProcess_type,IFC4X1_IfcRelAssignsToProduct_type,IFC4X1_IfcRelAssignsToResource_type
    });
    IFC4X1_IfcRelAssignsToGroup_type->set_subtypes({
        IFC4X1_IfcRelAssignsToGroupByFactor_type
    });
    IFC4X1_IfcRelAssociates_type->set_subtypes({
        IFC4X1_IfcRelAssociatesApproval_type,IFC4X1_IfcRelAssociatesClassification_type,IFC4X1_IfcRelAssociatesConstraint_type,IFC4X1_IfcRelAssociatesDocument_type,IFC4X1_IfcRelAssociatesLibrary_type,IFC4X1_IfcRelAssociatesMaterial_type
    });
    IFC4X1_IfcRelConnects_type->set_subtypes({
        IFC4X1_IfcRelConnectsElements_type,IFC4X1_IfcRelConnectsPortToElement_type,IFC4X1_IfcRelConnectsPorts_type,IFC4X1_IfcRelConnectsStructuralActivity_type,IFC4X1_IfcRelConnectsStructuralMember_type,IFC4X1_IfcRelContainedInSpatialStructure_type,IFC4X1_IfcRelCoversBldgElements_type,IFC4X1_IfcRelCoversSpaces_type,IFC4X1_IfcRelFillsElement_type,IFC4X1_IfcRelFlowControlElements_type,IFC4X1_IfcRelInterferesElements_type,IFC4X1_IfcRelReferencedInSpatialStructure_type,IFC4X1_IfcRelSequence_type,IFC4X1_IfcRelServicesBuildings_type,IFC4X1_IfcRelSpaceBoundary_type
    });
    IFC4X1_IfcRelConnectsElements_type->set_subtypes({
        IFC4X1_IfcRelConnectsPathElements_type,IFC4X1_IfcRelConnectsWithRealizingElements_type
    });
    IFC4X1_IfcRelConnectsStructuralMember_type->set_subtypes({
        IFC4X1_IfcRelConnectsWithEccentricity_type
    });
    IFC4X1_IfcRelDefines_type->set_subtypes({
        IFC4X1_IfcRelDefinesByObject_type,IFC4X1_IfcRelDefinesByProperties_type,IFC4X1_IfcRelDefinesByTemplate_type,IFC4X1_IfcRelDefinesByType_type
    });
    IFC4X1_IfcRelSpaceBoundary_type->set_subtypes({
        IFC4X1_IfcRelSpaceBoundary1stLevel_type
    });
    IFC4X1_IfcRelSpaceBoundary1stLevel_type->set_subtypes({
        IFC4X1_IfcRelSpaceBoundary2ndLevel_type
    });
    IFC4X1_IfcCompositeCurveSegment_type->set_subtypes({
        IFC4X1_IfcReparametrisedCompositeCurveSegment_type
    });
    IFC4X1_IfcRevolvedAreaSolid_type->set_subtypes({
        IFC4X1_IfcRevolvedAreaSolidTapered_type
    });
    IFC4X1_IfcSectionedSolid_type->set_subtypes({
        IFC4X1_IfcSectionedSolidHorizontal_type
    });
    IFC4X1_IfcRepresentation_type->set_subtypes({
        IFC4X1_IfcShapeModel_type,IFC4X1_IfcStyleModel_type
    });
    IFC4X1_IfcShapeModel_type->set_subtypes({
        IFC4X1_IfcShapeRepresentation_type,IFC4X1_IfcTopologyRepresentation_type
    });
    IFC4X1_IfcSlab_type->set_subtypes({
        IFC4X1_IfcSlabElementedCase_type,IFC4X1_IfcSlabStandardCase_type
    });
    IFC4X1_IfcSpatialStructureElementType_type->set_subtypes({
        IFC4X1_IfcSpaceType_type
    });
    IFC4X1_IfcSpatialElementType_type->set_subtypes({
        IFC4X1_IfcSpatialStructureElementType_type,IFC4X1_IfcSpatialZoneType_type
    });
    IFC4X1_IfcStructuralActivity_type->set_subtypes({
        IFC4X1_IfcStructuralAction_type,IFC4X1_IfcStructuralReaction_type
    });
    IFC4X1_IfcStructuralItem_type->set_subtypes({
        IFC4X1_IfcStructuralConnection_type,IFC4X1_IfcStructuralMember_type
    });
    IFC4X1_IfcStructuralAction_type->set_subtypes({
        IFC4X1_IfcStructuralCurveAction_type,IFC4X1_IfcStructuralPointAction_type,IFC4X1_IfcStructuralSurfaceAction_type
    });
    IFC4X1_IfcStructuralConnection_type->set_subtypes({
        IFC4X1_IfcStructuralCurveConnection_type,IFC4X1_IfcStructuralPointConnection_type,IFC4X1_IfcStructuralSurfaceConnection_type
    });
    IFC4X1_IfcStructuralMember_type->set_subtypes({
        IFC4X1_IfcStructuralCurveMember_type,IFC4X1_IfcStructuralSurfaceMember_type
    });
    IFC4X1_IfcStructuralCurveMember_type->set_subtypes({
        IFC4X1_IfcStructuralCurveMemberVarying_type
    });
    IFC4X1_IfcStructuralReaction_type->set_subtypes({
        IFC4X1_IfcStructuralCurveReaction_type,IFC4X1_IfcStructuralPointReaction_type,IFC4X1_IfcStructuralSurfaceReaction_type
    });
    IFC4X1_IfcStructuralCurveAction_type->set_subtypes({
        IFC4X1_IfcStructuralLinearAction_type
    });
    IFC4X1_IfcStructuralLoadGroup_type->set_subtypes({
        IFC4X1_IfcStructuralLoadCase_type
    });
    IFC4X1_IfcStructuralLoad_type->set_subtypes({
        IFC4X1_IfcStructuralLoadConfiguration_type,IFC4X1_IfcStructuralLoadOrResult_type
    });
    IFC4X1_IfcStructuralLoadStatic_type->set_subtypes({
        IFC4X1_IfcStructuralLoadLinearForce_type,IFC4X1_IfcStructuralLoadPlanarForce_type,IFC4X1_IfcStructuralLoadSingleDisplacement_type,IFC4X1_IfcStructuralLoadSingleForce_type,IFC4X1_IfcStructuralLoadTemperature_type
    });
    IFC4X1_IfcStructuralLoadSingleDisplacement_type->set_subtypes({
        IFC4X1_IfcStructuralLoadSingleDisplacementDistortion_type
    });
    IFC4X1_IfcStructuralLoadSingleForce_type->set_subtypes({
        IFC4X1_IfcStructuralLoadSingleForceWarping_type
    });
    IFC4X1_IfcStructuralLoadOrResult_type->set_subtypes({
        IFC4X1_IfcStructuralLoadStatic_type,IFC4X1_IfcSurfaceReinforcementArea_type
    });
    IFC4X1_IfcStructuralSurfaceAction_type->set_subtypes({
        IFC4X1_IfcStructuralPlanarAction_type
    });
    IFC4X1_IfcStructuralSurfaceMember_type->set_subtypes({
        IFC4X1_IfcStructuralSurfaceMemberVarying_type
    });
    IFC4X1_IfcStyleModel_type->set_subtypes({
        IFC4X1_IfcStyledRepresentation_type
    });
    IFC4X1_IfcSweptSurface_type->set_subtypes({
        IFC4X1_IfcSurfaceOfLinearExtrusion_type,IFC4X1_IfcSurfaceOfRevolution_type
    });
    IFC4X1_IfcSurfaceStyleShading_type->set_subtypes({
        IFC4X1_IfcSurfaceStyleRendering_type
    });
    IFC4X1_IfcSweptDiskSolid_type->set_subtypes({
        IFC4X1_IfcSweptDiskSolidPolygonal_type
    });
    IFC4X1_IfcTaskTime_type->set_subtypes({
        IFC4X1_IfcTaskTimeRecurring_type
    });
    IFC4X1_IfcTextLiteral_type->set_subtypes({
        IFC4X1_IfcTextLiteralWithExtent_type
    });
    IFC4X1_IfcPreDefinedTextFont_type->set_subtypes({
        IFC4X1_IfcTextStyleFontModel_type
    });
    IFC4X1_IfcTriangulatedFaceSet_type->set_subtypes({
        IFC4X1_IfcTriangulatedIrregularNetwork_type
    });
    IFC4X1_IfcTypeObject_type->set_subtypes({
        IFC4X1_IfcTypeProcess_type,IFC4X1_IfcTypeProduct_type,IFC4X1_IfcTypeResource_type
    });
    IFC4X1_IfcVertex_type->set_subtypes({
        IFC4X1_IfcVertexPoint_type
    });
    IFC4X1_IfcWall_type->set_subtypes({
        IFC4X1_IfcWallElementedCase_type,IFC4X1_IfcWallStandardCase_type
    });
    IFC4X1_IfcWindow_type->set_subtypes({
        IFC4X1_IfcWindowStandardCase_type
    });
    IFC4X1_IfcWorkControl_type->set_subtypes({
        IFC4X1_IfcWorkPlan_type,IFC4X1_IfcWorkSchedule_type
    });

    std::vector<const declaration*> declarations= {
    IFC4X1_IfcAbsorbedDoseMeasure_type,
    IFC4X1_IfcAccelerationMeasure_type,
    IFC4X1_IfcActionRequest_type,
    IFC4X1_IfcActionRequestTypeEnum_type,
    IFC4X1_IfcActionSourceTypeEnum_type,
    IFC4X1_IfcActionTypeEnum_type,
    IFC4X1_IfcActor_type,
    IFC4X1_IfcActorRole_type,
    IFC4X1_IfcActorSelect_type,
    IFC4X1_IfcActuator_type,
    IFC4X1_IfcActuatorType_type,
    IFC4X1_IfcActuatorTypeEnum_type,
    IFC4X1_IfcAddress_type,
    IFC4X1_IfcAddressTypeEnum_type,
    IFC4X1_IfcAdvancedBrep_type,
    IFC4X1_IfcAdvancedBrepWithVoids_type,
    IFC4X1_IfcAdvancedFace_type,
    IFC4X1_IfcAirTerminal_type,
    IFC4X1_IfcAirTerminalBox_type,
    IFC4X1_IfcAirTerminalBoxType_type,
    IFC4X1_IfcAirTerminalBoxTypeEnum_type,
    IFC4X1_IfcAirTerminalType_type,
    IFC4X1_IfcAirTerminalTypeEnum_type,
    IFC4X1_IfcAirToAirHeatRecovery_type,
    IFC4X1_IfcAirToAirHeatRecoveryType_type,
    IFC4X1_IfcAirToAirHeatRecoveryTypeEnum_type,
    IFC4X1_IfcAlarm_type,
    IFC4X1_IfcAlarmType_type,
    IFC4X1_IfcAlarmTypeEnum_type,
    IFC4X1_IfcAlignment_type,
    IFC4X1_IfcAlignment2DHorizontal_type,
    IFC4X1_IfcAlignment2DHorizontalSegment_type,
    IFC4X1_IfcAlignment2DSegment_type,
    IFC4X1_IfcAlignment2DVerSegCircularArc_type,
    IFC4X1_IfcAlignment2DVerSegLine_type,
    IFC4X1_IfcAlignment2DVerSegParabolicArc_type,
    IFC4X1_IfcAlignment2DVertical_type,
    IFC4X1_IfcAlignment2DVerticalSegment_type,
    IFC4X1_IfcAlignmentCurve_type,
    IFC4X1_IfcAlignmentTypeEnum_type,
    IFC4X1_IfcAmountOfSubstanceMeasure_type,
    IFC4X1_IfcAnalysisModelTypeEnum_type,
    IFC4X1_IfcAnalysisTheoryTypeEnum_type,
    IFC4X1_IfcAngularVelocityMeasure_type,
    IFC4X1_IfcAnnotation_type,
    IFC4X1_IfcAnnotationFillArea_type,
    IFC4X1_IfcApplication_type,
    IFC4X1_IfcAppliedValue_type,
    IFC4X1_IfcAppliedValueSelect_type,
    IFC4X1_IfcApproval_type,
    IFC4X1_IfcApprovalRelationship_type,
    IFC4X1_IfcArbitraryClosedProfileDef_type,
    IFC4X1_IfcArbitraryOpenProfileDef_type,
    IFC4X1_IfcArbitraryProfileDefWithVoids_type,
    IFC4X1_IfcArcIndex_type,
    IFC4X1_IfcAreaDensityMeasure_type,
    IFC4X1_IfcAreaMeasure_type,
    IFC4X1_IfcArithmeticOperatorEnum_type,
    IFC4X1_IfcAssemblyPlaceEnum_type,
    IFC4X1_IfcAsset_type,
    IFC4X1_IfcAsymmetricIShapeProfileDef_type,
    IFC4X1_IfcAudioVisualAppliance_type,
    IFC4X1_IfcAudioVisualApplianceType_type,
    IFC4X1_IfcAudioVisualApplianceTypeEnum_type,
    IFC4X1_IfcAxis1Placement_type,
    IFC4X1_IfcAxis2Placement_type,
    IFC4X1_IfcAxis2Placement2D_type,
    IFC4X1_IfcAxis2Placement3D_type,
    IFC4X1_IfcBeam_type,
    IFC4X1_IfcBeamStandardCase_type,
    IFC4X1_IfcBeamType_type,
    IFC4X1_IfcBeamTypeEnum_type,
    IFC4X1_IfcBenchmarkEnum_type,
    IFC4X1_IfcBendingParameterSelect_type,
    IFC4X1_IfcBinary_type,
    IFC4X1_IfcBlobTexture_type,
    IFC4X1_IfcBlock_type,
    IFC4X1_IfcBoiler_type,
    IFC4X1_IfcBoilerType_type,
    IFC4X1_IfcBoilerTypeEnum_type,
    IFC4X1_IfcBoolean_type,
    IFC4X1_IfcBooleanClippingResult_type,
    IFC4X1_IfcBooleanOperand_type,
    IFC4X1_IfcBooleanOperator_type,
    IFC4X1_IfcBooleanResult_type,
    IFC4X1_IfcBoundaryCondition_type,
    IFC4X1_IfcBoundaryCurve_type,
    IFC4X1_IfcBoundaryEdgeCondition_type,
    IFC4X1_IfcBoundaryFaceCondition_type,
    IFC4X1_IfcBoundaryNodeCondition_type,
    IFC4X1_IfcBoundaryNodeConditionWarping_type,
    IFC4X1_IfcBoundedCurve_type,
    IFC4X1_IfcBoundedSurface_type,
    IFC4X1_IfcBoundingBox_type,
    IFC4X1_IfcBoxAlignment_type,
    IFC4X1_IfcBoxedHalfSpace_type,
    IFC4X1_IfcBSplineCurve_type,
    IFC4X1_IfcBSplineCurveForm_type,
    IFC4X1_IfcBSplineCurveWithKnots_type,
    IFC4X1_IfcBSplineSurface_type,
    IFC4X1_IfcBSplineSurfaceForm_type,
    IFC4X1_IfcBSplineSurfaceWithKnots_type,
    IFC4X1_IfcBuilding_type,
    IFC4X1_IfcBuildingElement_type,
    IFC4X1_IfcBuildingElementPart_type,
    IFC4X1_IfcBuildingElementPartType_type,
    IFC4X1_IfcBuildingElementPartTypeEnum_type,
    IFC4X1_IfcBuildingElementProxy_type,
    IFC4X1_IfcBuildingElementProxyType_type,
    IFC4X1_IfcBuildingElementProxyTypeEnum_type,
    IFC4X1_IfcBuildingElementType_type,
    IFC4X1_IfcBuildingStorey_type,
    IFC4X1_IfcBuildingSystem_type,
    IFC4X1_IfcBuildingSystemTypeEnum_type,
    IFC4X1_IfcBurner_type,
    IFC4X1_IfcBurnerType_type,
    IFC4X1_IfcBurnerTypeEnum_type,
    IFC4X1_IfcCableCarrierFitting_type,
    IFC4X1_IfcCableCarrierFittingType_type,
    IFC4X1_IfcCableCarrierFittingTypeEnum_type,
    IFC4X1_IfcCableCarrierSegment_type,
    IFC4X1_IfcCableCarrierSegmentType_type,
    IFC4X1_IfcCableCarrierSegmentTypeEnum_type,
    IFC4X1_IfcCableFitting_type,
    IFC4X1_IfcCableFittingType_type,
    IFC4X1_IfcCableFittingTypeEnum_type,
    IFC4X1_IfcCableSegment_type,
    IFC4X1_IfcCableSegmentType_type,
    IFC4X1_IfcCableSegmentTypeEnum_type,
    IFC4X1_IfcCardinalPointReference_type,
    IFC4X1_IfcCartesianPoint_type,
    IFC4X1_IfcCartesianPointList_type,
    IFC4X1_IfcCartesianPointList2D_type,
    IFC4X1_IfcCartesianPointList3D_type,
    IFC4X1_IfcCartesianTransformationOperator_type,
    IFC4X1_IfcCartesianTransformationOperator2D_type,
    IFC4X1_IfcCartesianTransformationOperator2DnonUniform_type,
    IFC4X1_IfcCartesianTransformationOperator3D_type,
    IFC4X1_IfcCartesianTransformationOperator3DnonUniform_type,
    IFC4X1_IfcCenterLineProfileDef_type,
    IFC4X1_IfcChangeActionEnum_type,
    IFC4X1_IfcChiller_type,
    IFC4X1_IfcChillerType_type,
    IFC4X1_IfcChillerTypeEnum_type,
    IFC4X1_IfcChimney_type,
    IFC4X1_IfcChimneyType_type,
    IFC4X1_IfcChimneyTypeEnum_type,
    IFC4X1_IfcCircle_type,
    IFC4X1_IfcCircleHollowProfileDef_type,
    IFC4X1_IfcCircleProfileDef_type,
    IFC4X1_IfcCircularArcSegment2D_type,
    IFC4X1_IfcCivilElement_type,
    IFC4X1_IfcCivilElementType_type,
    IFC4X1_IfcClassification_type,
    IFC4X1_IfcClassificationReference_type,
    IFC4X1_IfcClassificationReferenceSelect_type,
    IFC4X1_IfcClassificationSelect_type,
    IFC4X1_IfcClosedShell_type,
    IFC4X1_IfcCoil_type,
    IFC4X1_IfcCoilType_type,
    IFC4X1_IfcCoilTypeEnum_type,
    IFC4X1_IfcColour_type,
    IFC4X1_IfcColourOrFactor_type,
    IFC4X1_IfcColourRgb_type,
    IFC4X1_IfcColourRgbList_type,
    IFC4X1_IfcColourSpecification_type,
    IFC4X1_IfcColumn_type,
    IFC4X1_IfcColumnStandardCase_type,
    IFC4X1_IfcColumnType_type,
    IFC4X1_IfcColumnTypeEnum_type,
    IFC4X1_IfcCommunicationsAppliance_type,
    IFC4X1_IfcCommunicationsApplianceType_type,
    IFC4X1_IfcCommunicationsApplianceTypeEnum_type,
    IFC4X1_IfcComplexNumber_type,
    IFC4X1_IfcComplexProperty_type,
    IFC4X1_IfcComplexPropertyTemplate_type,
    IFC4X1_IfcComplexPropertyTemplateTypeEnum_type,
    IFC4X1_IfcCompositeCurve_type,
    IFC4X1_IfcCompositeCurveOnSurface_type,
    IFC4X1_IfcCompositeCurveSegment_type,
    IFC4X1_IfcCompositeProfileDef_type,
    IFC4X1_IfcCompoundPlaneAngleMeasure_type,
    IFC4X1_IfcCompressor_type,
    IFC4X1_IfcCompressorType_type,
    IFC4X1_IfcCompressorTypeEnum_type,
    IFC4X1_IfcCondenser_type,
    IFC4X1_IfcCondenserType_type,
    IFC4X1_IfcCondenserTypeEnum_type,
    IFC4X1_IfcConic_type,
    IFC4X1_IfcConnectedFaceSet_type,
    IFC4X1_IfcConnectionCurveGeometry_type,
    IFC4X1_IfcConnectionGeometry_type,
    IFC4X1_IfcConnectionPointEccentricity_type,
    IFC4X1_IfcConnectionPointGeometry_type,
    IFC4X1_IfcConnectionSurfaceGeometry_type,
    IFC4X1_IfcConnectionTypeEnum_type,
    IFC4X1_IfcConnectionVolumeGeometry_type,
    IFC4X1_IfcConstraint_type,
    IFC4X1_IfcConstraintEnum_type,
    IFC4X1_IfcConstructionEquipmentResource_type,
    IFC4X1_IfcConstructionEquipmentResourceType_type,
    IFC4X1_IfcConstructionEquipmentResourceTypeEnum_type,
    IFC4X1_IfcConstructionMaterialResource_type,
    IFC4X1_IfcConstructionMaterialResourceType_type,
    IFC4X1_IfcConstructionMaterialResourceTypeEnum_type,
    IFC4X1_IfcConstructionProductResource_type,
    IFC4X1_IfcConstructionProductResourceType_type,
    IFC4X1_IfcConstructionProductResourceTypeEnum_type,
    IFC4X1_IfcConstructionResource_type,
    IFC4X1_IfcConstructionResourceType_type,
    IFC4X1_IfcContext_type,
    IFC4X1_IfcContextDependentMeasure_type,
    IFC4X1_IfcContextDependentUnit_type,
    IFC4X1_IfcControl_type,
    IFC4X1_IfcController_type,
    IFC4X1_IfcControllerType_type,
    IFC4X1_IfcControllerTypeEnum_type,
    IFC4X1_IfcConversionBasedUnit_type,
    IFC4X1_IfcConversionBasedUnitWithOffset_type,
    IFC4X1_IfcCooledBeam_type,
    IFC4X1_IfcCooledBeamType_type,
    IFC4X1_IfcCooledBeamTypeEnum_type,
    IFC4X1_IfcCoolingTower_type,
    IFC4X1_IfcCoolingTowerType_type,
    IFC4X1_IfcCoolingTowerTypeEnum_type,
    IFC4X1_IfcCoordinateOperation_type,
    IFC4X1_IfcCoordinateReferenceSystem_type,
    IFC4X1_IfcCoordinateReferenceSystemSelect_type,
    IFC4X1_IfcCostItem_type,
    IFC4X1_IfcCostItemTypeEnum_type,
    IFC4X1_IfcCostSchedule_type,
    IFC4X1_IfcCostScheduleTypeEnum_type,
    IFC4X1_IfcCostValue_type,
    IFC4X1_IfcCountMeasure_type,
    IFC4X1_IfcCovering_type,
    IFC4X1_IfcCoveringType_type,
    IFC4X1_IfcCoveringTypeEnum_type,
    IFC4X1_IfcCrewResource_type,
    IFC4X1_IfcCrewResourceType_type,
    IFC4X1_IfcCrewResourceTypeEnum_type,
    IFC4X1_IfcCsgPrimitive3D_type,
    IFC4X1_IfcCsgSelect_type,
    IFC4X1_IfcCsgSolid_type,
    IFC4X1_IfcCShapeProfileDef_type,
    IFC4X1_IfcCurrencyRelationship_type,
    IFC4X1_IfcCurtainWall_type,
    IFC4X1_IfcCurtainWallType_type,
    IFC4X1_IfcCurtainWallTypeEnum_type,
    IFC4X1_IfcCurvatureMeasure_type,
    IFC4X1_IfcCurve_type,
    IFC4X1_IfcCurveBoundedPlane_type,
    IFC4X1_IfcCurveBoundedSurface_type,
    IFC4X1_IfcCurveFontOrScaledCurveFontSelect_type,
    IFC4X1_IfcCurveInterpolationEnum_type,
    IFC4X1_IfcCurveOnSurface_type,
    IFC4X1_IfcCurveOrEdgeCurve_type,
    IFC4X1_IfcCurveSegment2D_type,
    IFC4X1_IfcCurveStyle_type,
    IFC4X1_IfcCurveStyleFont_type,
    IFC4X1_IfcCurveStyleFontAndScaling_type,
    IFC4X1_IfcCurveStyleFontPattern_type,
    IFC4X1_IfcCurveStyleFontSelect_type,
    IFC4X1_IfcCylindricalSurface_type,
    IFC4X1_IfcDamper_type,
    IFC4X1_IfcDamperType_type,
    IFC4X1_IfcDamperTypeEnum_type,
    IFC4X1_IfcDataOriginEnum_type,
    IFC4X1_IfcDate_type,
    IFC4X1_IfcDateTime_type,
    IFC4X1_IfcDayInMonthNumber_type,
    IFC4X1_IfcDayInWeekNumber_type,
    IFC4X1_IfcDefinitionSelect_type,
    IFC4X1_IfcDerivedMeasureValue_type,
    IFC4X1_IfcDerivedProfileDef_type,
    IFC4X1_IfcDerivedUnit_type,
    IFC4X1_IfcDerivedUnitElement_type,
    IFC4X1_IfcDerivedUnitEnum_type,
    IFC4X1_IfcDescriptiveMeasure_type,
    IFC4X1_IfcDimensionalExponents_type,
    IFC4X1_IfcDimensionCount_type,
    IFC4X1_IfcDirection_type,
    IFC4X1_IfcDirectionSenseEnum_type,
    IFC4X1_IfcDiscreteAccessory_type,
    IFC4X1_IfcDiscreteAccessoryType_type,
    IFC4X1_IfcDiscreteAccessoryTypeEnum_type,
    IFC4X1_IfcDistanceExpression_type,
    IFC4X1_IfcDistributionChamberElement_type,
    IFC4X1_IfcDistributionChamberElementType_type,
    IFC4X1_IfcDistributionChamberElementTypeEnum_type,
    IFC4X1_IfcDistributionCircuit_type,
    IFC4X1_IfcDistributionControlElement_type,
    IFC4X1_IfcDistributionControlElementType_type,
    IFC4X1_IfcDistributionElement_type,
    IFC4X1_IfcDistributionElementType_type,
    IFC4X1_IfcDistributionFlowElement_type,
    IFC4X1_IfcDistributionFlowElementType_type,
    IFC4X1_IfcDistributionPort_type,
    IFC4X1_IfcDistributionPortTypeEnum_type,
    IFC4X1_IfcDistributionSystem_type,
    IFC4X1_IfcDistributionSystemEnum_type,
    IFC4X1_IfcDocumentConfidentialityEnum_type,
    IFC4X1_IfcDocumentInformation_type,
    IFC4X1_IfcDocumentInformationRelationship_type,
    IFC4X1_IfcDocumentReference_type,
    IFC4X1_IfcDocumentSelect_type,
    IFC4X1_IfcDocumentStatusEnum_type,
    IFC4X1_IfcDoor_type,
    IFC4X1_IfcDoorLiningProperties_type,
    IFC4X1_IfcDoorPanelOperationEnum_type,
    IFC4X1_IfcDoorPanelPositionEnum_type,
    IFC4X1_IfcDoorPanelProperties_type,
    IFC4X1_IfcDoorStandardCase_type,
    IFC4X1_IfcDoorStyle_type,
    IFC4X1_IfcDoorStyleConstructionEnum_type,
    IFC4X1_IfcDoorStyleOperationEnum_type,
    IFC4X1_IfcDoorType_type,
    IFC4X1_IfcDoorTypeEnum_type,
    IFC4X1_IfcDoorTypeOperationEnum_type,
    IFC4X1_IfcDoseEquivalentMeasure_type,
    IFC4X1_IfcDraughtingPreDefinedColour_type,
    IFC4X1_IfcDraughtingPreDefinedCurveFont_type,
    IFC4X1_IfcDuctFitting_type,
    IFC4X1_IfcDuctFittingType_type,
    IFC4X1_IfcDuctFittingTypeEnum_type,
    IFC4X1_IfcDuctSegment_type,
    IFC4X1_IfcDuctSegmentType_type,
    IFC4X1_IfcDuctSegmentTypeEnum_type,
    IFC4X1_IfcDuctSilencer_type,
    IFC4X1_IfcDuctSilencerType_type,
    IFC4X1_IfcDuctSilencerTypeEnum_type,
    IFC4X1_IfcDuration_type,
    IFC4X1_IfcDynamicViscosityMeasure_type,
    IFC4X1_IfcEdge_type,
    IFC4X1_IfcEdgeCurve_type,
    IFC4X1_IfcEdgeLoop_type,
    IFC4X1_IfcElectricAppliance_type,
    IFC4X1_IfcElectricApplianceType_type,
    IFC4X1_IfcElectricApplianceTypeEnum_type,
    IFC4X1_IfcElectricCapacitanceMeasure_type,
    IFC4X1_IfcElectricChargeMeasure_type,
    IFC4X1_IfcElectricConductanceMeasure_type,
    IFC4X1_IfcElectricCurrentMeasure_type,
    IFC4X1_IfcElectricDistributionBoard_type,
    IFC4X1_IfcElectricDistributionBoardType_type,
    IFC4X1_IfcElectricDistributionBoardTypeEnum_type,
    IFC4X1_IfcElectricFlowStorageDevice_type,
    IFC4X1_IfcElectricFlowStorageDeviceType_type,
    IFC4X1_IfcElectricFlowStorageDeviceTypeEnum_type,
    IFC4X1_IfcElectricGenerator_type,
    IFC4X1_IfcElectricGeneratorType_type,
    IFC4X1_IfcElectricGeneratorTypeEnum_type,
    IFC4X1_IfcElectricMotor_type,
    IFC4X1_IfcElectricMotorType_type,
    IFC4X1_IfcElectricMotorTypeEnum_type,
    IFC4X1_IfcElectricResistanceMeasure_type,
    IFC4X1_IfcElectricTimeControl_type,
    IFC4X1_IfcElectricTimeControlType_type,
    IFC4X1_IfcElectricTimeControlTypeEnum_type,
    IFC4X1_IfcElectricVoltageMeasure_type,
    IFC4X1_IfcElement_type,
    IFC4X1_IfcElementarySurface_type,
    IFC4X1_IfcElementAssembly_type,
    IFC4X1_IfcElementAssemblyType_type,
    IFC4X1_IfcElementAssemblyTypeEnum_type,
    IFC4X1_IfcElementComponent_type,
    IFC4X1_IfcElementComponentType_type,
    IFC4X1_IfcElementCompositionEnum_type,
    IFC4X1_IfcElementQuantity_type,
    IFC4X1_IfcElementType_type,
    IFC4X1_IfcEllipse_type,
    IFC4X1_IfcEllipseProfileDef_type,
    IFC4X1_IfcEnergyConversionDevice_type,
    IFC4X1_IfcEnergyConversionDeviceType_type,
    IFC4X1_IfcEnergyMeasure_type,
    IFC4X1_IfcEngine_type,
    IFC4X1_IfcEngineType_type,
    IFC4X1_IfcEngineTypeEnum_type,
    IFC4X1_IfcEvaporativeCooler_type,
    IFC4X1_IfcEvaporativeCoolerType_type,
    IFC4X1_IfcEvaporativeCoolerTypeEnum_type,
    IFC4X1_IfcEvaporator_type,
    IFC4X1_IfcEvaporatorType_type,
    IFC4X1_IfcEvaporatorTypeEnum_type,
    IFC4X1_IfcEvent_type,
    IFC4X1_IfcEventTime_type,
    IFC4X1_IfcEventTriggerTypeEnum_type,
    IFC4X1_IfcEventType_type,
    IFC4X1_IfcEventTypeEnum_type,
    IFC4X1_IfcExtendedProperties_type,
    IFC4X1_IfcExternalInformation_type,
    IFC4X1_IfcExternallyDefinedHatchStyle_type,
    IFC4X1_IfcExternallyDefinedSurfaceStyle_type,
    IFC4X1_IfcExternallyDefinedTextFont_type,
    IFC4X1_IfcExternalReference_type,
    IFC4X1_IfcExternalReferenceRelationship_type,
    IFC4X1_IfcExternalSpatialElement_type,
    IFC4X1_IfcExternalSpatialElementTypeEnum_type,
    IFC4X1_IfcExternalSpatialStructureElement_type,
    IFC4X1_IfcExtrudedAreaSolid_type,
    IFC4X1_IfcExtrudedAreaSolidTapered_type,
    IFC4X1_IfcFace_type,
    IFC4X1_IfcFaceBasedSurfaceModel_type,
    IFC4X1_IfcFaceBound_type,
    IFC4X1_IfcFaceOuterBound_type,
    IFC4X1_IfcFaceSurface_type,
    IFC4X1_IfcFacetedBrep_type,
    IFC4X1_IfcFacetedBrepWithVoids_type,
    IFC4X1_IfcFailureConnectionCondition_type,
    IFC4X1_IfcFan_type,
    IFC4X1_IfcFanType_type,
    IFC4X1_IfcFanTypeEnum_type,
    IFC4X1_IfcFastener_type,
    IFC4X1_IfcFastenerType_type,
    IFC4X1_IfcFastenerTypeEnum_type,
    IFC4X1_IfcFeatureElement_type,
    IFC4X1_IfcFeatureElementAddition_type,
    IFC4X1_IfcFeatureElementSubtraction_type,
    IFC4X1_IfcFillAreaStyle_type,
    IFC4X1_IfcFillAreaStyleHatching_type,
    IFC4X1_IfcFillAreaStyleTiles_type,
    IFC4X1_IfcFillStyleSelect_type,
    IFC4X1_IfcFilter_type,
    IFC4X1_IfcFilterType_type,
    IFC4X1_IfcFilterTypeEnum_type,
    IFC4X1_IfcFireSuppressionTerminal_type,
    IFC4X1_IfcFireSuppressionTerminalType_type,
    IFC4X1_IfcFireSuppressionTerminalTypeEnum_type,
    IFC4X1_IfcFixedReferenceSweptAreaSolid_type,
    IFC4X1_IfcFlowController_type,
    IFC4X1_IfcFlowControllerType_type,
    IFC4X1_IfcFlowDirectionEnum_type,
    IFC4X1_IfcFlowFitting_type,
    IFC4X1_IfcFlowFittingType_type,
    IFC4X1_IfcFlowInstrument_type,
    IFC4X1_IfcFlowInstrumentType_type,
    IFC4X1_IfcFlowInstrumentTypeEnum_type,
    IFC4X1_IfcFlowMeter_type,
    IFC4X1_IfcFlowMeterType_type,
    IFC4X1_IfcFlowMeterTypeEnum_type,
    IFC4X1_IfcFlowMovingDevice_type,
    IFC4X1_IfcFlowMovingDeviceType_type,
    IFC4X1_IfcFlowSegment_type,
    IFC4X1_IfcFlowSegmentType_type,
    IFC4X1_IfcFlowStorageDevice_type,
    IFC4X1_IfcFlowStorageDeviceType_type,
    IFC4X1_IfcFlowTerminal_type,
    IFC4X1_IfcFlowTerminalType_type,
    IFC4X1_IfcFlowTreatmentDevice_type,
    IFC4X1_IfcFlowTreatmentDeviceType_type,
    IFC4X1_IfcFontStyle_type,
    IFC4X1_IfcFontVariant_type,
    IFC4X1_IfcFontWeight_type,
    IFC4X1_IfcFooting_type,
    IFC4X1_IfcFootingType_type,
    IFC4X1_IfcFootingTypeEnum_type,
    IFC4X1_IfcForceMeasure_type,
    IFC4X1_IfcFrequencyMeasure_type,
    IFC4X1_IfcFurnishingElement_type,
    IFC4X1_IfcFurnishingElementType_type,
    IFC4X1_IfcFurniture_type,
    IFC4X1_IfcFurnitureType_type,
    IFC4X1_IfcFurnitureTypeEnum_type,
    IFC4X1_IfcGeographicElement_type,
    IFC4X1_IfcGeographicElementType_type,
    IFC4X1_IfcGeographicElementTypeEnum_type,
    IFC4X1_IfcGeometricCurveSet_type,
    IFC4X1_IfcGeometricProjectionEnum_type,
    IFC4X1_IfcGeometricRepresentationContext_type,
    IFC4X1_IfcGeometricRepresentationItem_type,
    IFC4X1_IfcGeometricRepresentationSubContext_type,
    IFC4X1_IfcGeometricSet_type,
    IFC4X1_IfcGeometricSetSelect_type,
    IFC4X1_IfcGloballyUniqueId_type,
    IFC4X1_IfcGlobalOrLocalEnum_type,
    IFC4X1_IfcGrid_type,
    IFC4X1_IfcGridAxis_type,
    IFC4X1_IfcGridPlacement_type,
    IFC4X1_IfcGridPlacementDirectionSelect_type,
    IFC4X1_IfcGridTypeEnum_type,
    IFC4X1_IfcGroup_type,
    IFC4X1_IfcHalfSpaceSolid_type,
    IFC4X1_IfcHatchLineDistanceSelect_type,
    IFC4X1_IfcHeatExchanger_type,
    IFC4X1_IfcHeatExchangerType_type,
    IFC4X1_IfcHeatExchangerTypeEnum_type,
    IFC4X1_IfcHeatFluxDensityMeasure_type,
    IFC4X1_IfcHeatingValueMeasure_type,
    IFC4X1_IfcHumidifier_type,
    IFC4X1_IfcHumidifierType_type,
    IFC4X1_IfcHumidifierTypeEnum_type,
    IFC4X1_IfcIdentifier_type,
    IFC4X1_IfcIlluminanceMeasure_type,
    IFC4X1_IfcImageTexture_type,
    IFC4X1_IfcIndexedColourMap_type,
    IFC4X1_IfcIndexedPolyCurve_type,
    IFC4X1_IfcIndexedPolygonalFace_type,
    IFC4X1_IfcIndexedPolygonalFaceWithVoids_type,
    IFC4X1_IfcIndexedTextureMap_type,
    IFC4X1_IfcIndexedTriangleTextureMap_type,
    IFC4X1_IfcInductanceMeasure_type,
    IFC4X1_IfcInteger_type,
    IFC4X1_IfcIntegerCountRateMeasure_type,
    IFC4X1_IfcInterceptor_type,
    IFC4X1_IfcInterceptorType_type,
    IFC4X1_IfcInterceptorTypeEnum_type,
    IFC4X1_IfcInternalOrExternalEnum_type,
    IFC4X1_IfcIntersectionCurve_type,
    IFC4X1_IfcInventory_type,
    IFC4X1_IfcInventoryTypeEnum_type,
    IFC4X1_IfcIonConcentrationMeasure_type,
    IFC4X1_IfcIrregularTimeSeries_type,
    IFC4X1_IfcIrregularTimeSeriesValue_type,
    IFC4X1_IfcIShapeProfileDef_type,
    IFC4X1_IfcIsothermalMoistureCapacityMeasure_type,
    IFC4X1_IfcJunctionBox_type,
    IFC4X1_IfcJunctionBoxType_type,
    IFC4X1_IfcJunctionBoxTypeEnum_type,
    IFC4X1_IfcKinematicViscosityMeasure_type,
    IFC4X1_IfcKnotType_type,
    IFC4X1_IfcLabel_type,
    IFC4X1_IfcLaborResource_type,
    IFC4X1_IfcLaborResourceType_type,
    IFC4X1_IfcLaborResourceTypeEnum_type,
    IFC4X1_IfcLagTime_type,
    IFC4X1_IfcLamp_type,
    IFC4X1_IfcLampType_type,
    IFC4X1_IfcLampTypeEnum_type,
    IFC4X1_IfcLanguageId_type,
    IFC4X1_IfcLayeredItem_type,
    IFC4X1_IfcLayerSetDirectionEnum_type,
    IFC4X1_IfcLengthMeasure_type,
    IFC4X1_IfcLibraryInformation_type,
    IFC4X1_IfcLibraryReference_type,
    IFC4X1_IfcLibrarySelect_type,
    IFC4X1_IfcLightDistributionCurveEnum_type,
    IFC4X1_IfcLightDistributionData_type,
    IFC4X1_IfcLightDistributionDataSourceSelect_type,
    IFC4X1_IfcLightEmissionSourceEnum_type,
    IFC4X1_IfcLightFixture_type,
    IFC4X1_IfcLightFixtureType_type,
    IFC4X1_IfcLightFixtureTypeEnum_type,
    IFC4X1_IfcLightIntensityDistribution_type,
    IFC4X1_IfcLightSource_type,
    IFC4X1_IfcLightSourceAmbient_type,
    IFC4X1_IfcLightSourceDirectional_type,
    IFC4X1_IfcLightSourceGoniometric_type,
    IFC4X1_IfcLightSourcePositional_type,
    IFC4X1_IfcLightSourceSpot_type,
    IFC4X1_IfcLine_type,
    IFC4X1_IfcLinearForceMeasure_type,
    IFC4X1_IfcLinearMomentMeasure_type,
    IFC4X1_IfcLinearPlacement_type,
    IFC4X1_IfcLinearPositioningElement_type,
    IFC4X1_IfcLinearStiffnessMeasure_type,
    IFC4X1_IfcLinearVelocityMeasure_type,
    IFC4X1_IfcLineIndex_type,
    IFC4X1_IfcLineSegment2D_type,
    IFC4X1_IfcLoadGroupTypeEnum_type,
    IFC4X1_IfcLocalPlacement_type,
    IFC4X1_IfcLogical_type,
    IFC4X1_IfcLogicalOperatorEnum_type,
    IFC4X1_IfcLoop_type,
    IFC4X1_IfcLShapeProfileDef_type,
    IFC4X1_IfcLuminousFluxMeasure_type,
    IFC4X1_IfcLuminousIntensityDistributionMeasure_type,
    IFC4X1_IfcLuminousIntensityMeasure_type,
    IFC4X1_IfcMagneticFluxDensityMeasure_type,
    IFC4X1_IfcMagneticFluxMeasure_type,
    IFC4X1_IfcManifoldSolidBrep_type,
    IFC4X1_IfcMapConversion_type,
    IFC4X1_IfcMappedItem_type,
    IFC4X1_IfcMassDensityMeasure_type,
    IFC4X1_IfcMassFlowRateMeasure_type,
    IFC4X1_IfcMassMeasure_type,
    IFC4X1_IfcMassPerLengthMeasure_type,
    IFC4X1_IfcMaterial_type,
    IFC4X1_IfcMaterialClassificationRelationship_type,
    IFC4X1_IfcMaterialConstituent_type,
    IFC4X1_IfcMaterialConstituentSet_type,
    IFC4X1_IfcMaterialDefinition_type,
    IFC4X1_IfcMaterialDefinitionRepresentation_type,
    IFC4X1_IfcMaterialLayer_type,
    IFC4X1_IfcMaterialLayerSet_type,
    IFC4X1_IfcMaterialLayerSetUsage_type,
    IFC4X1_IfcMaterialLayerWithOffsets_type,
    IFC4X1_IfcMaterialList_type,
    IFC4X1_IfcMaterialProfile_type,
    IFC4X1_IfcMaterialProfileSet_type,
    IFC4X1_IfcMaterialProfileSetUsage_type,
    IFC4X1_IfcMaterialProfileSetUsageTapering_type,
    IFC4X1_IfcMaterialProfileWithOffsets_type,
    IFC4X1_IfcMaterialProperties_type,
    IFC4X1_IfcMaterialRelationship_type,
    IFC4X1_IfcMaterialSelect_type,
    IFC4X1_IfcMaterialUsageDefinition_type,
    IFC4X1_IfcMeasureValue_type,
    IFC4X1_IfcMeasureWithUnit_type,
    IFC4X1_IfcMechanicalFastener_type,
    IFC4X1_IfcMechanicalFastenerType_type,
    IFC4X1_IfcMechanicalFastenerTypeEnum_type,
    IFC4X1_IfcMedicalDevice_type,
    IFC4X1_IfcMedicalDeviceType_type,
    IFC4X1_IfcMedicalDeviceTypeEnum_type,
    IFC4X1_IfcMember_type,
    IFC4X1_IfcMemberStandardCase_type,
    IFC4X1_IfcMemberType_type,
    IFC4X1_IfcMemberTypeEnum_type,
    IFC4X1_IfcMetric_type,
    IFC4X1_IfcMetricValueSelect_type,
    IFC4X1_IfcMirroredProfileDef_type,
    IFC4X1_IfcModulusOfElasticityMeasure_type,
    IFC4X1_IfcModulusOfLinearSubgradeReactionMeasure_type,
    IFC4X1_IfcModulusOfRotationalSubgradeReactionMeasure_type,
    IFC4X1_IfcModulusOfRotationalSubgradeReactionSelect_type,
    IFC4X1_IfcModulusOfSubgradeReactionMeasure_type,
    IFC4X1_IfcModulusOfSubgradeReactionSelect_type,
    IFC4X1_IfcModulusOfTranslationalSubgradeReactionSelect_type,
    IFC4X1_IfcMoistureDiffusivityMeasure_type,
    IFC4X1_IfcMolecularWeightMeasure_type,
    IFC4X1_IfcMomentOfInertiaMeasure_type,
    IFC4X1_IfcMonetaryMeasure_type,
    IFC4X1_IfcMonetaryUnit_type,
    IFC4X1_IfcMonthInYearNumber_type,
    IFC4X1_IfcMotorConnection_type,
    IFC4X1_IfcMotorConnectionType_type,
    IFC4X1_IfcMotorConnectionTypeEnum_type,
    IFC4X1_IfcNamedUnit_type,
    IFC4X1_IfcNonNegativeLengthMeasure_type,
    IFC4X1_IfcNormalisedRatioMeasure_type,
    IFC4X1_IfcNullStyle_type,
    IFC4X1_IfcNumericMeasure_type,
    IFC4X1_IfcObject_type,
    IFC4X1_IfcObjectDefinition_type,
    IFC4X1_IfcObjective_type,
    IFC4X1_IfcObjectiveEnum_type,
    IFC4X1_IfcObjectPlacement_type,
    IFC4X1_IfcObjectReferenceSelect_type,
    IFC4X1_IfcObjectTypeEnum_type,
    IFC4X1_IfcOccupant_type,
    IFC4X1_IfcOccupantTypeEnum_type,
    IFC4X1_IfcOffsetCurve_type,
    IFC4X1_IfcOffsetCurve2D_type,
    IFC4X1_IfcOffsetCurve3D_type,
    IFC4X1_IfcOffsetCurveByDistances_type,
    IFC4X1_IfcOpeningElement_type,
    IFC4X1_IfcOpeningElementTypeEnum_type,
    IFC4X1_IfcOpeningStandardCase_type,
    IFC4X1_IfcOpenShell_type,
    IFC4X1_IfcOrganization_type,
    IFC4X1_IfcOrganizationRelationship_type,
    IFC4X1_IfcOrientationExpression_type,
    IFC4X1_IfcOrientedEdge_type,
    IFC4X1_IfcOuterBoundaryCurve_type,
    IFC4X1_IfcOutlet_type,
    IFC4X1_IfcOutletType_type,
    IFC4X1_IfcOutletTypeEnum_type,
    IFC4X1_IfcOwnerHistory_type,
    IFC4X1_IfcParameterizedProfileDef_type,
    IFC4X1_IfcParameterValue_type,
    IFC4X1_IfcPath_type,
    IFC4X1_IfcPcurve_type,
    IFC4X1_IfcPerformanceHistory_type,
    IFC4X1_IfcPerformanceHistoryTypeEnum_type,
    IFC4X1_IfcPermeableCoveringOperationEnum_type,
    IFC4X1_IfcPermeableCoveringProperties_type,
    IFC4X1_IfcPermit_type,
    IFC4X1_IfcPermitTypeEnum_type,
    IFC4X1_IfcPerson_type,
    IFC4X1_IfcPersonAndOrganization_type,
    IFC4X1_IfcPHMeasure_type,
    IFC4X1_IfcPhysicalComplexQuantity_type,
    IFC4X1_IfcPhysicalOrVirtualEnum_type,
    IFC4X1_IfcPhysicalQuantity_type,
    IFC4X1_IfcPhysicalSimpleQuantity_type,
    IFC4X1_IfcPile_type,
    IFC4X1_IfcPileConstructionEnum_type,
    IFC4X1_IfcPileType_type,
    IFC4X1_IfcPileTypeEnum_type,
    IFC4X1_IfcPipeFitting_type,
    IFC4X1_IfcPipeFittingType_type,
    IFC4X1_IfcPipeFittingTypeEnum_type,
    IFC4X1_IfcPipeSegment_type,
    IFC4X1_IfcPipeSegmentType_type,
    IFC4X1_IfcPipeSegmentTypeEnum_type,
    IFC4X1_IfcPixelTexture_type,
    IFC4X1_IfcPlacement_type,
    IFC4X1_IfcPlanarBox_type,
    IFC4X1_IfcPlanarExtent_type,
    IFC4X1_IfcPlanarForceMeasure_type,
    IFC4X1_IfcPlane_type,
    IFC4X1_IfcPlaneAngleMeasure_type,
    IFC4X1_IfcPlate_type,
    IFC4X1_IfcPlateStandardCase_type,
    IFC4X1_IfcPlateType_type,
    IFC4X1_IfcPlateTypeEnum_type,
    IFC4X1_IfcPoint_type,
    IFC4X1_IfcPointOnCurve_type,
    IFC4X1_IfcPointOnSurface_type,
    IFC4X1_IfcPointOrVertexPoint_type,
    IFC4X1_IfcPolygonalBoundedHalfSpace_type,
    IFC4X1_IfcPolygonalFaceSet_type,
    IFC4X1_IfcPolyline_type,
    IFC4X1_IfcPolyLoop_type,
    IFC4X1_IfcPort_type,
    IFC4X1_IfcPositioningElement_type,
    IFC4X1_IfcPositiveInteger_type,
    IFC4X1_IfcPositiveLengthMeasure_type,
    IFC4X1_IfcPositivePlaneAngleMeasure_type,
    IFC4X1_IfcPositiveRatioMeasure_type,
    IFC4X1_IfcPostalAddress_type,
    IFC4X1_IfcPowerMeasure_type,
    IFC4X1_IfcPreDefinedColour_type,
    IFC4X1_IfcPreDefinedCurveFont_type,
    IFC4X1_IfcPreDefinedItem_type,
    IFC4X1_IfcPreDefinedProperties_type,
    IFC4X1_IfcPreDefinedPropertySet_type,
    IFC4X1_IfcPreDefinedTextFont_type,
    IFC4X1_IfcPreferredSurfaceCurveRepresentation_type,
    IFC4X1_IfcPresentableText_type,
    IFC4X1_IfcPresentationItem_type,
    IFC4X1_IfcPresentationLayerAssignment_type,
    IFC4X1_IfcPresentationLayerWithStyle_type,
    IFC4X1_IfcPresentationStyle_type,
    IFC4X1_IfcPresentationStyleAssignment_type,
    IFC4X1_IfcPresentationStyleSelect_type,
    IFC4X1_IfcPressureMeasure_type,
    IFC4X1_IfcProcedure_type,
    IFC4X1_IfcProcedureType_type,
    IFC4X1_IfcProcedureTypeEnum_type,
    IFC4X1_IfcProcess_type,
    IFC4X1_IfcProcessSelect_type,
    IFC4X1_IfcProduct_type,
    IFC4X1_IfcProductDefinitionShape_type,
    IFC4X1_IfcProductRepresentation_type,
    IFC4X1_IfcProductRepresentationSelect_type,
    IFC4X1_IfcProductSelect_type,
    IFC4X1_IfcProfileDef_type,
    IFC4X1_IfcProfileProperties_type,
    IFC4X1_IfcProfileTypeEnum_type,
    IFC4X1_IfcProject_type,
    IFC4X1_IfcProjectedCRS_type,
    IFC4X1_IfcProjectedOrTrueLengthEnum_type,
    IFC4X1_IfcProjectionElement_type,
    IFC4X1_IfcProjectionElementTypeEnum_type,
    IFC4X1_IfcProjectLibrary_type,
    IFC4X1_IfcProjectOrder_type,
    IFC4X1_IfcProjectOrderTypeEnum_type,
    IFC4X1_IfcProperty_type,
    IFC4X1_IfcPropertyAbstraction_type,
    IFC4X1_IfcPropertyBoundedValue_type,
    IFC4X1_IfcPropertyDefinition_type,
    IFC4X1_IfcPropertyDependencyRelationship_type,
    IFC4X1_IfcPropertyEnumeratedValue_type,
    IFC4X1_IfcPropertyEnumeration_type,
    IFC4X1_IfcPropertyListValue_type,
    IFC4X1_IfcPropertyReferenceValue_type,
    IFC4X1_IfcPropertySet_type,
    IFC4X1_IfcPropertySetDefinition_type,
    IFC4X1_IfcPropertySetDefinitionSelect_type,
    IFC4X1_IfcPropertySetDefinitionSet_type,
    IFC4X1_IfcPropertySetTemplate_type,
    IFC4X1_IfcPropertySetTemplateTypeEnum_type,
    IFC4X1_IfcPropertySingleValue_type,
    IFC4X1_IfcPropertyTableValue_type,
    IFC4X1_IfcPropertyTemplate_type,
    IFC4X1_IfcPropertyTemplateDefinition_type,
    IFC4X1_IfcProtectiveDevice_type,
    IFC4X1_IfcProtectiveDeviceTrippingUnit_type,
    IFC4X1_IfcProtectiveDeviceTrippingUnitType_type,
    IFC4X1_IfcProtectiveDeviceTrippingUnitTypeEnum_type,
    IFC4X1_IfcProtectiveDeviceType_type,
    IFC4X1_IfcProtectiveDeviceTypeEnum_type,
    IFC4X1_IfcProxy_type,
    IFC4X1_IfcPump_type,
    IFC4X1_IfcPumpType_type,
    IFC4X1_IfcPumpTypeEnum_type,
    IFC4X1_IfcQuantityArea_type,
    IFC4X1_IfcQuantityCount_type,
    IFC4X1_IfcQuantityLength_type,
    IFC4X1_IfcQuantitySet_type,
    IFC4X1_IfcQuantityTime_type,
    IFC4X1_IfcQuantityVolume_type,
    IFC4X1_IfcQuantityWeight_type,
    IFC4X1_IfcRadioActivityMeasure_type,
    IFC4X1_IfcRailing_type,
    IFC4X1_IfcRailingType_type,
    IFC4X1_IfcRailingTypeEnum_type,
    IFC4X1_IfcRamp_type,
    IFC4X1_IfcRampFlight_type,
    IFC4X1_IfcRampFlightType_type,
    IFC4X1_IfcRampFlightTypeEnum_type,
    IFC4X1_IfcRampType_type,
    IFC4X1_IfcRampTypeEnum_type,
    IFC4X1_IfcRatioMeasure_type,
    IFC4X1_IfcRationalBSplineCurveWithKnots_type,
    IFC4X1_IfcRationalBSplineSurfaceWithKnots_type,
    IFC4X1_IfcReal_type,
    IFC4X1_IfcRectangleHollowProfileDef_type,
    IFC4X1_IfcRectangleProfileDef_type,
    IFC4X1_IfcRectangularPyramid_type,
    IFC4X1_IfcRectangularTrimmedSurface_type,
    IFC4X1_IfcRecurrencePattern_type,
    IFC4X1_IfcRecurrenceTypeEnum_type,
    IFC4X1_IfcReference_type,
    IFC4X1_IfcReferent_type,
    IFC4X1_IfcReferentTypeEnum_type,
    IFC4X1_IfcReflectanceMethodEnum_type,
    IFC4X1_IfcRegularTimeSeries_type,
    IFC4X1_IfcReinforcementBarProperties_type,
    IFC4X1_IfcReinforcementDefinitionProperties_type,
    IFC4X1_IfcReinforcingBar_type,
    IFC4X1_IfcReinforcingBarRoleEnum_type,
    IFC4X1_IfcReinforcingBarSurfaceEnum_type,
    IFC4X1_IfcReinforcingBarType_type,
    IFC4X1_IfcReinforcingBarTypeEnum_type,
    IFC4X1_IfcReinforcingElement_type,
    IFC4X1_IfcReinforcingElementType_type,
    IFC4X1_IfcReinforcingMesh_type,
    IFC4X1_IfcReinforcingMeshType_type,
    IFC4X1_IfcReinforcingMeshTypeEnum_type,
    IFC4X1_IfcRelAggregates_type,
    IFC4X1_IfcRelAssigns_type,
    IFC4X1_IfcRelAssignsToActor_type,
    IFC4X1_IfcRelAssignsToControl_type,
    IFC4X1_IfcRelAssignsToGroup_type,
    IFC4X1_IfcRelAssignsToGroupByFactor_type,
    IFC4X1_IfcRelAssignsToProcess_type,
    IFC4X1_IfcRelAssignsToProduct_type,
    IFC4X1_IfcRelAssignsToResource_type,
    IFC4X1_IfcRelAssociates_type,
    IFC4X1_IfcRelAssociatesApproval_type,
    IFC4X1_IfcRelAssociatesClassification_type,
    IFC4X1_IfcRelAssociatesConstraint_type,
    IFC4X1_IfcRelAssociatesDocument_type,
    IFC4X1_IfcRelAssociatesLibrary_type,
    IFC4X1_IfcRelAssociatesMaterial_type,
    IFC4X1_IfcRelationship_type,
    IFC4X1_IfcRelConnects_type,
    IFC4X1_IfcRelConnectsElements_type,
    IFC4X1_IfcRelConnectsPathElements_type,
    IFC4X1_IfcRelConnectsPorts_type,
    IFC4X1_IfcRelConnectsPortToElement_type,
    IFC4X1_IfcRelConnectsStructuralActivity_type,
    IFC4X1_IfcRelConnectsStructuralMember_type,
    IFC4X1_IfcRelConnectsWithEccentricity_type,
    IFC4X1_IfcRelConnectsWithRealizingElements_type,
    IFC4X1_IfcRelContainedInSpatialStructure_type,
    IFC4X1_IfcRelCoversBldgElements_type,
    IFC4X1_IfcRelCoversSpaces_type,
    IFC4X1_IfcRelDeclares_type,
    IFC4X1_IfcRelDecomposes_type,
    IFC4X1_IfcRelDefines_type,
    IFC4X1_IfcRelDefinesByObject_type,
    IFC4X1_IfcRelDefinesByProperties_type,
    IFC4X1_IfcRelDefinesByTemplate_type,
    IFC4X1_IfcRelDefinesByType_type,
    IFC4X1_IfcRelFillsElement_type,
    IFC4X1_IfcRelFlowControlElements_type,
    IFC4X1_IfcRelInterferesElements_type,
    IFC4X1_IfcRelNests_type,
    IFC4X1_IfcRelProjectsElement_type,
    IFC4X1_IfcRelReferencedInSpatialStructure_type,
    IFC4X1_IfcRelSequence_type,
    IFC4X1_IfcRelServicesBuildings_type,
    IFC4X1_IfcRelSpaceBoundary_type,
    IFC4X1_IfcRelSpaceBoundary1stLevel_type,
    IFC4X1_IfcRelSpaceBoundary2ndLevel_type,
    IFC4X1_IfcRelVoidsElement_type,
    IFC4X1_IfcReparametrisedCompositeCurveSegment_type,
    IFC4X1_IfcRepresentation_type,
    IFC4X1_IfcRepresentationContext_type,
    IFC4X1_IfcRepresentationItem_type,
    IFC4X1_IfcRepresentationMap_type,
    IFC4X1_IfcResource_type,
    IFC4X1_IfcResourceApprovalRelationship_type,
    IFC4X1_IfcResourceConstraintRelationship_type,
    IFC4X1_IfcResourceLevelRelationship_type,
    IFC4X1_IfcResourceObjectSelect_type,
    IFC4X1_IfcResourceSelect_type,
    IFC4X1_IfcResourceTime_type,
    IFC4X1_IfcRevolvedAreaSolid_type,
    IFC4X1_IfcRevolvedAreaSolidTapered_type,
    IFC4X1_IfcRightCircularCone_type,
    IFC4X1_IfcRightCircularCylinder_type,
    IFC4X1_IfcRoleEnum_type,
    IFC4X1_IfcRoof_type,
    IFC4X1_IfcRoofType_type,
    IFC4X1_IfcRoofTypeEnum_type,
    IFC4X1_IfcRoot_type,
    IFC4X1_IfcRotationalFrequencyMeasure_type,
    IFC4X1_IfcRotationalMassMeasure_type,
    IFC4X1_IfcRotationalStiffnessMeasure_type,
    IFC4X1_IfcRotationalStiffnessSelect_type,
    IFC4X1_IfcRoundedRectangleProfileDef_type,
    IFC4X1_IfcSanitaryTerminal_type,
    IFC4X1_IfcSanitaryTerminalType_type,
    IFC4X1_IfcSanitaryTerminalTypeEnum_type,
    IFC4X1_IfcSchedulingTime_type,
    IFC4X1_IfcSeamCurve_type,
    IFC4X1_IfcSectionalAreaIntegralMeasure_type,
    IFC4X1_IfcSectionedSolid_type,
    IFC4X1_IfcSectionedSolidHorizontal_type,
    IFC4X1_IfcSectionedSpine_type,
    IFC4X1_IfcSectionModulusMeasure_type,
    IFC4X1_IfcSectionProperties_type,
    IFC4X1_IfcSectionReinforcementProperties_type,
    IFC4X1_IfcSectionTypeEnum_type,
    IFC4X1_IfcSegmentIndexSelect_type,
    IFC4X1_IfcSensor_type,
    IFC4X1_IfcSensorType_type,
    IFC4X1_IfcSensorTypeEnum_type,
    IFC4X1_IfcSequenceEnum_type,
    IFC4X1_IfcShadingDevice_type,
    IFC4X1_IfcShadingDeviceType_type,
    IFC4X1_IfcShadingDeviceTypeEnum_type,
    IFC4X1_IfcShapeAspect_type,
    IFC4X1_IfcShapeModel_type,
    IFC4X1_IfcShapeRepresentation_type,
    IFC4X1_IfcShearModulusMeasure_type,
    IFC4X1_IfcShell_type,
    IFC4X1_IfcShellBasedSurfaceModel_type,
    IFC4X1_IfcSimpleProperty_type,
    IFC4X1_IfcSimplePropertyTemplate_type,
    IFC4X1_IfcSimplePropertyTemplateTypeEnum_type,
    IFC4X1_IfcSimpleValue_type,
    IFC4X1_IfcSIPrefix_type,
    IFC4X1_IfcSite_type,
    IFC4X1_IfcSIUnit_type,
    IFC4X1_IfcSIUnitName_type,
    IFC4X1_IfcSizeSelect_type,
    IFC4X1_IfcSlab_type,
    IFC4X1_IfcSlabElementedCase_type,
    IFC4X1_IfcSlabStandardCase_type,
    IFC4X1_IfcSlabType_type,
    IFC4X1_IfcSlabTypeEnum_type,
    IFC4X1_IfcSlippageConnectionCondition_type,
    IFC4X1_IfcSolarDevice_type,
    IFC4X1_IfcSolarDeviceType_type,
    IFC4X1_IfcSolarDeviceTypeEnum_type,
    IFC4X1_IfcSolidAngleMeasure_type,
    IFC4X1_IfcSolidModel_type,
    IFC4X1_IfcSolidOrShell_type,
    IFC4X1_IfcSoundPowerLevelMeasure_type,
    IFC4X1_IfcSoundPowerMeasure_type,
    IFC4X1_IfcSoundPressureLevelMeasure_type,
    IFC4X1_IfcSoundPressureMeasure_type,
    IFC4X1_IfcSpace_type,
    IFC4X1_IfcSpaceBoundarySelect_type,
    IFC4X1_IfcSpaceHeater_type,
    IFC4X1_IfcSpaceHeaterType_type,
    IFC4X1_IfcSpaceHeaterTypeEnum_type,
    IFC4X1_IfcSpaceType_type,
    IFC4X1_IfcSpaceTypeEnum_type,
    IFC4X1_IfcSpatialElement_type,
    IFC4X1_IfcSpatialElementType_type,
    IFC4X1_IfcSpatialStructureElement_type,
    IFC4X1_IfcSpatialStructureElementType_type,
    IFC4X1_IfcSpatialZone_type,
    IFC4X1_IfcSpatialZoneType_type,
    IFC4X1_IfcSpatialZoneTypeEnum_type,
    IFC4X1_IfcSpecificHeatCapacityMeasure_type,
    IFC4X1_IfcSpecularExponent_type,
    IFC4X1_IfcSpecularHighlightSelect_type,
    IFC4X1_IfcSpecularRoughness_type,
    IFC4X1_IfcSphere_type,
    IFC4X1_IfcSphericalSurface_type,
    IFC4X1_IfcStackTerminal_type,
    IFC4X1_IfcStackTerminalType_type,
    IFC4X1_IfcStackTerminalTypeEnum_type,
    IFC4X1_IfcStair_type,
    IFC4X1_IfcStairFlight_type,
    IFC4X1_IfcStairFlightType_type,
    IFC4X1_IfcStairFlightTypeEnum_type,
    IFC4X1_IfcStairType_type,
    IFC4X1_IfcStairTypeEnum_type,
    IFC4X1_IfcStateEnum_type,
    IFC4X1_IfcStructuralAction_type,
    IFC4X1_IfcStructuralActivity_type,
    IFC4X1_IfcStructuralActivityAssignmentSelect_type,
    IFC4X1_IfcStructuralAnalysisModel_type,
    IFC4X1_IfcStructuralConnection_type,
    IFC4X1_IfcStructuralConnectionCondition_type,
    IFC4X1_IfcStructuralCurveAction_type,
    IFC4X1_IfcStructuralCurveActivityTypeEnum_type,
    IFC4X1_IfcStructuralCurveConnection_type,
    IFC4X1_IfcStructuralCurveMember_type,
    IFC4X1_IfcStructuralCurveMemberTypeEnum_type,
    IFC4X1_IfcStructuralCurveMemberVarying_type,
    IFC4X1_IfcStructuralCurveReaction_type,
    IFC4X1_IfcStructuralItem_type,
    IFC4X1_IfcStructuralLinearAction_type,
    IFC4X1_IfcStructuralLoad_type,
    IFC4X1_IfcStructuralLoadCase_type,
    IFC4X1_IfcStructuralLoadConfiguration_type,
    IFC4X1_IfcStructuralLoadGroup_type,
    IFC4X1_IfcStructuralLoadLinearForce_type,
    IFC4X1_IfcStructuralLoadOrResult_type,
    IFC4X1_IfcStructuralLoadPlanarForce_type,
    IFC4X1_IfcStructuralLoadSingleDisplacement_type,
    IFC4X1_IfcStructuralLoadSingleDisplacementDistortion_type,
    IFC4X1_IfcStructuralLoadSingleForce_type,
    IFC4X1_IfcStructuralLoadSingleForceWarping_type,
    IFC4X1_IfcStructuralLoadStatic_type,
    IFC4X1_IfcStructuralLoadTemperature_type,
    IFC4X1_IfcStructuralMember_type,
    IFC4X1_IfcStructuralPlanarAction_type,
    IFC4X1_IfcStructuralPointAction_type,
    IFC4X1_IfcStructuralPointConnection_type,
    IFC4X1_IfcStructuralPointReaction_type,
    IFC4X1_IfcStructuralReaction_type,
    IFC4X1_IfcStructuralResultGroup_type,
    IFC4X1_IfcStructuralSurfaceAction_type,
    IFC4X1_IfcStructuralSurfaceActivityTypeEnum_type,
    IFC4X1_IfcStructuralSurfaceConnection_type,
    IFC4X1_IfcStructuralSurfaceMember_type,
    IFC4X1_IfcStructuralSurfaceMemberTypeEnum_type,
    IFC4X1_IfcStructuralSurfaceMemberVarying_type,
    IFC4X1_IfcStructuralSurfaceReaction_type,
    IFC4X1_IfcStyleAssignmentSelect_type,
    IFC4X1_IfcStyledItem_type,
    IFC4X1_IfcStyledRepresentation_type,
    IFC4X1_IfcStyleModel_type,
    IFC4X1_IfcSubContractResource_type,
    IFC4X1_IfcSubContractResourceType_type,
    IFC4X1_IfcSubContractResourceTypeEnum_type,
    IFC4X1_IfcSubedge_type,
    IFC4X1_IfcSurface_type,
    IFC4X1_IfcSurfaceCurve_type,
    IFC4X1_IfcSurfaceCurveSweptAreaSolid_type,
    IFC4X1_IfcSurfaceFeature_type,
    IFC4X1_IfcSurfaceFeatureTypeEnum_type,
    IFC4X1_IfcSurfaceOfLinearExtrusion_type,
    IFC4X1_IfcSurfaceOfRevolution_type,
    IFC4X1_IfcSurfaceOrFaceSurface_type,
    IFC4X1_IfcSurfaceReinforcementArea_type,
    IFC4X1_IfcSurfaceSide_type,
    IFC4X1_IfcSurfaceStyle_type,
    IFC4X1_IfcSurfaceStyleElementSelect_type,
    IFC4X1_IfcSurfaceStyleLighting_type,
    IFC4X1_IfcSurfaceStyleRefraction_type,
    IFC4X1_IfcSurfaceStyleRendering_type,
    IFC4X1_IfcSurfaceStyleShading_type,
    IFC4X1_IfcSurfaceStyleWithTextures_type,
    IFC4X1_IfcSurfaceTexture_type,
    IFC4X1_IfcSweptAreaSolid_type,
    IFC4X1_IfcSweptDiskSolid_type,
    IFC4X1_IfcSweptDiskSolidPolygonal_type,
    IFC4X1_IfcSweptSurface_type,
    IFC4X1_IfcSwitchingDevice_type,
    IFC4X1_IfcSwitchingDeviceType_type,
    IFC4X1_IfcSwitchingDeviceTypeEnum_type,
    IFC4X1_IfcSystem_type,
    IFC4X1_IfcSystemFurnitureElement_type,
    IFC4X1_IfcSystemFurnitureElementType_type,
    IFC4X1_IfcSystemFurnitureElementTypeEnum_type,
    IFC4X1_IfcTable_type,
    IFC4X1_IfcTableColumn_type,
    IFC4X1_IfcTableRow_type,
    IFC4X1_IfcTank_type,
    IFC4X1_IfcTankType_type,
    IFC4X1_IfcTankTypeEnum_type,
    IFC4X1_IfcTask_type,
    IFC4X1_IfcTaskDurationEnum_type,
    IFC4X1_IfcTaskTime_type,
    IFC4X1_IfcTaskTimeRecurring_type,
    IFC4X1_IfcTaskType_type,
    IFC4X1_IfcTaskTypeEnum_type,
    IFC4X1_IfcTelecomAddress_type,
    IFC4X1_IfcTemperatureGradientMeasure_type,
    IFC4X1_IfcTemperatureRateOfChangeMeasure_type,
    IFC4X1_IfcTendon_type,
    IFC4X1_IfcTendonAnchor_type,
    IFC4X1_IfcTendonAnchorType_type,
    IFC4X1_IfcTendonAnchorTypeEnum_type,
    IFC4X1_IfcTendonType_type,
    IFC4X1_IfcTendonTypeEnum_type,
    IFC4X1_IfcTessellatedFaceSet_type,
    IFC4X1_IfcTessellatedItem_type,
    IFC4X1_IfcText_type,
    IFC4X1_IfcTextAlignment_type,
    IFC4X1_IfcTextDecoration_type,
    IFC4X1_IfcTextFontName_type,
    IFC4X1_IfcTextFontSelect_type,
    IFC4X1_IfcTextLiteral_type,
    IFC4X1_IfcTextLiteralWithExtent_type,
    IFC4X1_IfcTextPath_type,
    IFC4X1_IfcTextStyle_type,
    IFC4X1_IfcTextStyleFontModel_type,
    IFC4X1_IfcTextStyleForDefinedFont_type,
    IFC4X1_IfcTextStyleTextModel_type,
    IFC4X1_IfcTextTransformation_type,
    IFC4X1_IfcTextureCoordinate_type,
    IFC4X1_IfcTextureCoordinateGenerator_type,
    IFC4X1_IfcTextureMap_type,
    IFC4X1_IfcTextureVertex_type,
    IFC4X1_IfcTextureVertexList_type,
    IFC4X1_IfcThermalAdmittanceMeasure_type,
    IFC4X1_IfcThermalConductivityMeasure_type,
    IFC4X1_IfcThermalExpansionCoefficientMeasure_type,
    IFC4X1_IfcThermalResistanceMeasure_type,
    IFC4X1_IfcThermalTransmittanceMeasure_type,
    IFC4X1_IfcThermodynamicTemperatureMeasure_type,
    IFC4X1_IfcTime_type,
    IFC4X1_IfcTimeMeasure_type,
    IFC4X1_IfcTimeOrRatioSelect_type,
    IFC4X1_IfcTimePeriod_type,
    IFC4X1_IfcTimeSeries_type,
    IFC4X1_IfcTimeSeriesDataTypeEnum_type,
    IFC4X1_IfcTimeSeriesValue_type,
    IFC4X1_IfcTimeStamp_type,
    IFC4X1_IfcTopologicalRepresentationItem_type,
    IFC4X1_IfcTopologyRepresentation_type,
    IFC4X1_IfcToroidalSurface_type,
    IFC4X1_IfcTorqueMeasure_type,
    IFC4X1_IfcTransformer_type,
    IFC4X1_IfcTransformerType_type,
    IFC4X1_IfcTransformerTypeEnum_type,
    IFC4X1_IfcTransitionCode_type,
    IFC4X1_IfcTransitionCurveSegment2D_type,
    IFC4X1_IfcTransitionCurveType_type,
    IFC4X1_IfcTranslationalStiffnessSelect_type,
    IFC4X1_IfcTransportElement_type,
    IFC4X1_IfcTransportElementType_type,
    IFC4X1_IfcTransportElementTypeEnum_type,
    IFC4X1_IfcTrapeziumProfileDef_type,
    IFC4X1_IfcTriangulatedFaceSet_type,
    IFC4X1_IfcTriangulatedIrregularNetwork_type,
    IFC4X1_IfcTrimmedCurve_type,
    IFC4X1_IfcTrimmingPreference_type,
    IFC4X1_IfcTrimmingSelect_type,
    IFC4X1_IfcTShapeProfileDef_type,
    IFC4X1_IfcTubeBundle_type,
    IFC4X1_IfcTubeBundleType_type,
    IFC4X1_IfcTubeBundleTypeEnum_type,
    IFC4X1_IfcTypeObject_type,
    IFC4X1_IfcTypeProcess_type,
    IFC4X1_IfcTypeProduct_type,
    IFC4X1_IfcTypeResource_type,
    IFC4X1_IfcUnit_type,
    IFC4X1_IfcUnitaryControlElement_type,
    IFC4X1_IfcUnitaryControlElementType_type,
    IFC4X1_IfcUnitaryControlElementTypeEnum_type,
    IFC4X1_IfcUnitaryEquipment_type,
    IFC4X1_IfcUnitaryEquipmentType_type,
    IFC4X1_IfcUnitaryEquipmentTypeEnum_type,
    IFC4X1_IfcUnitAssignment_type,
    IFC4X1_IfcUnitEnum_type,
    IFC4X1_IfcURIReference_type,
    IFC4X1_IfcUShapeProfileDef_type,
    IFC4X1_IfcValue_type,
    IFC4X1_IfcValve_type,
    IFC4X1_IfcValveType_type,
    IFC4X1_IfcValveTypeEnum_type,
    IFC4X1_IfcVaporPermeabilityMeasure_type,
    IFC4X1_IfcVector_type,
    IFC4X1_IfcVectorOrDirection_type,
    IFC4X1_IfcVertex_type,
    IFC4X1_IfcVertexLoop_type,
    IFC4X1_IfcVertexPoint_type,
    IFC4X1_IfcVibrationIsolator_type,
    IFC4X1_IfcVibrationIsolatorType_type,
    IFC4X1_IfcVibrationIsolatorTypeEnum_type,
    IFC4X1_IfcVirtualElement_type,
    IFC4X1_IfcVirtualGridIntersection_type,
    IFC4X1_IfcVoidingFeature_type,
    IFC4X1_IfcVoidingFeatureTypeEnum_type,
    IFC4X1_IfcVolumeMeasure_type,
    IFC4X1_IfcVolumetricFlowRateMeasure_type,
    IFC4X1_IfcWall_type,
    IFC4X1_IfcWallElementedCase_type,
    IFC4X1_IfcWallStandardCase_type,
    IFC4X1_IfcWallType_type,
    IFC4X1_IfcWallTypeEnum_type,
    IFC4X1_IfcWarpingConstantMeasure_type,
    IFC4X1_IfcWarpingMomentMeasure_type,
    IFC4X1_IfcWarpingStiffnessSelect_type,
    IFC4X1_IfcWasteTerminal_type,
    IFC4X1_IfcWasteTerminalType_type,
    IFC4X1_IfcWasteTerminalTypeEnum_type,
    IFC4X1_IfcWindow_type,
    IFC4X1_IfcWindowLiningProperties_type,
    IFC4X1_IfcWindowPanelOperationEnum_type,
    IFC4X1_IfcWindowPanelPositionEnum_type,
    IFC4X1_IfcWindowPanelProperties_type,
    IFC4X1_IfcWindowStandardCase_type,
    IFC4X1_IfcWindowStyle_type,
    IFC4X1_IfcWindowStyleConstructionEnum_type,
    IFC4X1_IfcWindowStyleOperationEnum_type,
    IFC4X1_IfcWindowType_type,
    IFC4X1_IfcWindowTypeEnum_type,
    IFC4X1_IfcWindowTypePartitioningEnum_type,
    IFC4X1_IfcWorkCalendar_type,
    IFC4X1_IfcWorkCalendarTypeEnum_type,
    IFC4X1_IfcWorkControl_type,
    IFC4X1_IfcWorkPlan_type,
    IFC4X1_IfcWorkPlanTypeEnum_type,
    IFC4X1_IfcWorkSchedule_type,
    IFC4X1_IfcWorkScheduleTypeEnum_type,
    IFC4X1_IfcWorkTime_type,
    IFC4X1_IfcZone_type,
    IFC4X1_IfcZShapeProfileDef_type
        };
    return new schema_definition(strings[3379], declarations, new IFC4X1_instance_factory());
}


#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC pop_options
#elif defined(_MSC_VER)
#pragma optimize("", on)
#endif
        
static std::unique_ptr<schema_definition> schema;

void Ifc4x1::clear_schema() {
    schema.reset();
}

const schema_definition& Ifc4x1::get_schema() {
    if (!schema) {
        schema.reset(IFC4X1_populate_schema());
    }
    return *schema;
}

