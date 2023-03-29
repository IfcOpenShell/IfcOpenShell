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
 * This file has been generated from IFC4X3_TC1.exp. Do not make modifications  *
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/

#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/Ifc4x3_tc1.h"

using namespace IfcParse;

entity* IFC4X3_TC1_IfcActionRequest_type = 0;
entity* IFC4X3_TC1_IfcActor_type = 0;
entity* IFC4X3_TC1_IfcActorRole_type = 0;
entity* IFC4X3_TC1_IfcActuator_type = 0;
entity* IFC4X3_TC1_IfcActuatorType_type = 0;
entity* IFC4X3_TC1_IfcAddress_type = 0;
entity* IFC4X3_TC1_IfcAdvancedBrep_type = 0;
entity* IFC4X3_TC1_IfcAdvancedBrepWithVoids_type = 0;
entity* IFC4X3_TC1_IfcAdvancedFace_type = 0;
entity* IFC4X3_TC1_IfcAirTerminal_type = 0;
entity* IFC4X3_TC1_IfcAirTerminalBox_type = 0;
entity* IFC4X3_TC1_IfcAirTerminalBoxType_type = 0;
entity* IFC4X3_TC1_IfcAirTerminalType_type = 0;
entity* IFC4X3_TC1_IfcAirToAirHeatRecovery_type = 0;
entity* IFC4X3_TC1_IfcAirToAirHeatRecoveryType_type = 0;
entity* IFC4X3_TC1_IfcAlarm_type = 0;
entity* IFC4X3_TC1_IfcAlarmType_type = 0;
entity* IFC4X3_TC1_IfcAlignment_type = 0;
entity* IFC4X3_TC1_IfcAlignmentCant_type = 0;
entity* IFC4X3_TC1_IfcAlignmentCantSegment_type = 0;
entity* IFC4X3_TC1_IfcAlignmentHorizontal_type = 0;
entity* IFC4X3_TC1_IfcAlignmentHorizontalSegment_type = 0;
entity* IFC4X3_TC1_IfcAlignmentParameterSegment_type = 0;
entity* IFC4X3_TC1_IfcAlignmentSegment_type = 0;
entity* IFC4X3_TC1_IfcAlignmentVertical_type = 0;
entity* IFC4X3_TC1_IfcAlignmentVerticalSegment_type = 0;
entity* IFC4X3_TC1_IfcAnnotation_type = 0;
entity* IFC4X3_TC1_IfcAnnotationFillArea_type = 0;
entity* IFC4X3_TC1_IfcApplication_type = 0;
entity* IFC4X3_TC1_IfcAppliedValue_type = 0;
entity* IFC4X3_TC1_IfcApproval_type = 0;
entity* IFC4X3_TC1_IfcApprovalRelationship_type = 0;
entity* IFC4X3_TC1_IfcArbitraryClosedProfileDef_type = 0;
entity* IFC4X3_TC1_IfcArbitraryOpenProfileDef_type = 0;
entity* IFC4X3_TC1_IfcArbitraryProfileDefWithVoids_type = 0;
entity* IFC4X3_TC1_IfcAsset_type = 0;
entity* IFC4X3_TC1_IfcAsymmetricIShapeProfileDef_type = 0;
entity* IFC4X3_TC1_IfcAudioVisualAppliance_type = 0;
entity* IFC4X3_TC1_IfcAudioVisualApplianceType_type = 0;
entity* IFC4X3_TC1_IfcAxis1Placement_type = 0;
entity* IFC4X3_TC1_IfcAxis2Placement2D_type = 0;
entity* IFC4X3_TC1_IfcAxis2Placement3D_type = 0;
entity* IFC4X3_TC1_IfcAxis2PlacementLinear_type = 0;
entity* IFC4X3_TC1_IfcBSplineCurve_type = 0;
entity* IFC4X3_TC1_IfcBSplineCurveWithKnots_type = 0;
entity* IFC4X3_TC1_IfcBSplineSurface_type = 0;
entity* IFC4X3_TC1_IfcBSplineSurfaceWithKnots_type = 0;
entity* IFC4X3_TC1_IfcBeam_type = 0;
entity* IFC4X3_TC1_IfcBeamType_type = 0;
entity* IFC4X3_TC1_IfcBearing_type = 0;
entity* IFC4X3_TC1_IfcBearingType_type = 0;
entity* IFC4X3_TC1_IfcBlobTexture_type = 0;
entity* IFC4X3_TC1_IfcBlock_type = 0;
entity* IFC4X3_TC1_IfcBoiler_type = 0;
entity* IFC4X3_TC1_IfcBoilerType_type = 0;
entity* IFC4X3_TC1_IfcBooleanClippingResult_type = 0;
entity* IFC4X3_TC1_IfcBooleanResult_type = 0;
entity* IFC4X3_TC1_IfcBorehole_type = 0;
entity* IFC4X3_TC1_IfcBoundaryCondition_type = 0;
entity* IFC4X3_TC1_IfcBoundaryCurve_type = 0;
entity* IFC4X3_TC1_IfcBoundaryEdgeCondition_type = 0;
entity* IFC4X3_TC1_IfcBoundaryFaceCondition_type = 0;
entity* IFC4X3_TC1_IfcBoundaryNodeCondition_type = 0;
entity* IFC4X3_TC1_IfcBoundaryNodeConditionWarping_type = 0;
entity* IFC4X3_TC1_IfcBoundedCurve_type = 0;
entity* IFC4X3_TC1_IfcBoundedSurface_type = 0;
entity* IFC4X3_TC1_IfcBoundingBox_type = 0;
entity* IFC4X3_TC1_IfcBoxedHalfSpace_type = 0;
entity* IFC4X3_TC1_IfcBridge_type = 0;
entity* IFC4X3_TC1_IfcBridgePart_type = 0;
entity* IFC4X3_TC1_IfcBuilding_type = 0;
entity* IFC4X3_TC1_IfcBuildingElementPart_type = 0;
entity* IFC4X3_TC1_IfcBuildingElementPartType_type = 0;
entity* IFC4X3_TC1_IfcBuildingElementProxy_type = 0;
entity* IFC4X3_TC1_IfcBuildingElementProxyType_type = 0;
entity* IFC4X3_TC1_IfcBuildingStorey_type = 0;
entity* IFC4X3_TC1_IfcBuildingSystem_type = 0;
entity* IFC4X3_TC1_IfcBuiltElement_type = 0;
entity* IFC4X3_TC1_IfcBuiltElementType_type = 0;
entity* IFC4X3_TC1_IfcBuiltSystem_type = 0;
entity* IFC4X3_TC1_IfcBurner_type = 0;
entity* IFC4X3_TC1_IfcBurnerType_type = 0;
entity* IFC4X3_TC1_IfcCShapeProfileDef_type = 0;
entity* IFC4X3_TC1_IfcCableCarrierFitting_type = 0;
entity* IFC4X3_TC1_IfcCableCarrierFittingType_type = 0;
entity* IFC4X3_TC1_IfcCableCarrierSegment_type = 0;
entity* IFC4X3_TC1_IfcCableCarrierSegmentType_type = 0;
entity* IFC4X3_TC1_IfcCableFitting_type = 0;
entity* IFC4X3_TC1_IfcCableFittingType_type = 0;
entity* IFC4X3_TC1_IfcCableSegment_type = 0;
entity* IFC4X3_TC1_IfcCableSegmentType_type = 0;
entity* IFC4X3_TC1_IfcCaissonFoundation_type = 0;
entity* IFC4X3_TC1_IfcCaissonFoundationType_type = 0;
entity* IFC4X3_TC1_IfcCartesianPoint_type = 0;
entity* IFC4X3_TC1_IfcCartesianPointList_type = 0;
entity* IFC4X3_TC1_IfcCartesianPointList2D_type = 0;
entity* IFC4X3_TC1_IfcCartesianPointList3D_type = 0;
entity* IFC4X3_TC1_IfcCartesianTransformationOperator_type = 0;
entity* IFC4X3_TC1_IfcCartesianTransformationOperator2D_type = 0;
entity* IFC4X3_TC1_IfcCartesianTransformationOperator2DnonUniform_type = 0;
entity* IFC4X3_TC1_IfcCartesianTransformationOperator3D_type = 0;
entity* IFC4X3_TC1_IfcCartesianTransformationOperator3DnonUniform_type = 0;
entity* IFC4X3_TC1_IfcCenterLineProfileDef_type = 0;
entity* IFC4X3_TC1_IfcChiller_type = 0;
entity* IFC4X3_TC1_IfcChillerType_type = 0;
entity* IFC4X3_TC1_IfcChimney_type = 0;
entity* IFC4X3_TC1_IfcChimneyType_type = 0;
entity* IFC4X3_TC1_IfcCircle_type = 0;
entity* IFC4X3_TC1_IfcCircleHollowProfileDef_type = 0;
entity* IFC4X3_TC1_IfcCircleProfileDef_type = 0;
entity* IFC4X3_TC1_IfcCivilElement_type = 0;
entity* IFC4X3_TC1_IfcCivilElementType_type = 0;
entity* IFC4X3_TC1_IfcClassification_type = 0;
entity* IFC4X3_TC1_IfcClassificationReference_type = 0;
entity* IFC4X3_TC1_IfcClosedShell_type = 0;
entity* IFC4X3_TC1_IfcClothoid_type = 0;
entity* IFC4X3_TC1_IfcCoil_type = 0;
entity* IFC4X3_TC1_IfcCoilType_type = 0;
entity* IFC4X3_TC1_IfcColourRgb_type = 0;
entity* IFC4X3_TC1_IfcColourRgbList_type = 0;
entity* IFC4X3_TC1_IfcColourSpecification_type = 0;
entity* IFC4X3_TC1_IfcColumn_type = 0;
entity* IFC4X3_TC1_IfcColumnType_type = 0;
entity* IFC4X3_TC1_IfcCommunicationsAppliance_type = 0;
entity* IFC4X3_TC1_IfcCommunicationsApplianceType_type = 0;
entity* IFC4X3_TC1_IfcComplexProperty_type = 0;
entity* IFC4X3_TC1_IfcComplexPropertyTemplate_type = 0;
entity* IFC4X3_TC1_IfcCompositeCurve_type = 0;
entity* IFC4X3_TC1_IfcCompositeCurveOnSurface_type = 0;
entity* IFC4X3_TC1_IfcCompositeCurveSegment_type = 0;
entity* IFC4X3_TC1_IfcCompositeProfileDef_type = 0;
entity* IFC4X3_TC1_IfcCompressor_type = 0;
entity* IFC4X3_TC1_IfcCompressorType_type = 0;
entity* IFC4X3_TC1_IfcCondenser_type = 0;
entity* IFC4X3_TC1_IfcCondenserType_type = 0;
entity* IFC4X3_TC1_IfcConic_type = 0;
entity* IFC4X3_TC1_IfcConnectedFaceSet_type = 0;
entity* IFC4X3_TC1_IfcConnectionCurveGeometry_type = 0;
entity* IFC4X3_TC1_IfcConnectionGeometry_type = 0;
entity* IFC4X3_TC1_IfcConnectionPointEccentricity_type = 0;
entity* IFC4X3_TC1_IfcConnectionPointGeometry_type = 0;
entity* IFC4X3_TC1_IfcConnectionSurfaceGeometry_type = 0;
entity* IFC4X3_TC1_IfcConnectionVolumeGeometry_type = 0;
entity* IFC4X3_TC1_IfcConstraint_type = 0;
entity* IFC4X3_TC1_IfcConstructionEquipmentResource_type = 0;
entity* IFC4X3_TC1_IfcConstructionEquipmentResourceType_type = 0;
entity* IFC4X3_TC1_IfcConstructionMaterialResource_type = 0;
entity* IFC4X3_TC1_IfcConstructionMaterialResourceType_type = 0;
entity* IFC4X3_TC1_IfcConstructionProductResource_type = 0;
entity* IFC4X3_TC1_IfcConstructionProductResourceType_type = 0;
entity* IFC4X3_TC1_IfcConstructionResource_type = 0;
entity* IFC4X3_TC1_IfcConstructionResourceType_type = 0;
entity* IFC4X3_TC1_IfcContext_type = 0;
entity* IFC4X3_TC1_IfcContextDependentUnit_type = 0;
entity* IFC4X3_TC1_IfcControl_type = 0;
entity* IFC4X3_TC1_IfcController_type = 0;
entity* IFC4X3_TC1_IfcControllerType_type = 0;
entity* IFC4X3_TC1_IfcConversionBasedUnit_type = 0;
entity* IFC4X3_TC1_IfcConversionBasedUnitWithOffset_type = 0;
entity* IFC4X3_TC1_IfcConveyorSegment_type = 0;
entity* IFC4X3_TC1_IfcConveyorSegmentType_type = 0;
entity* IFC4X3_TC1_IfcCooledBeam_type = 0;
entity* IFC4X3_TC1_IfcCooledBeamType_type = 0;
entity* IFC4X3_TC1_IfcCoolingTower_type = 0;
entity* IFC4X3_TC1_IfcCoolingTowerType_type = 0;
entity* IFC4X3_TC1_IfcCoordinateOperation_type = 0;
entity* IFC4X3_TC1_IfcCoordinateReferenceSystem_type = 0;
entity* IFC4X3_TC1_IfcCosineSpiral_type = 0;
entity* IFC4X3_TC1_IfcCostItem_type = 0;
entity* IFC4X3_TC1_IfcCostSchedule_type = 0;
entity* IFC4X3_TC1_IfcCostValue_type = 0;
entity* IFC4X3_TC1_IfcCourse_type = 0;
entity* IFC4X3_TC1_IfcCourseType_type = 0;
entity* IFC4X3_TC1_IfcCovering_type = 0;
entity* IFC4X3_TC1_IfcCoveringType_type = 0;
entity* IFC4X3_TC1_IfcCrewResource_type = 0;
entity* IFC4X3_TC1_IfcCrewResourceType_type = 0;
entity* IFC4X3_TC1_IfcCsgPrimitive3D_type = 0;
entity* IFC4X3_TC1_IfcCsgSolid_type = 0;
entity* IFC4X3_TC1_IfcCurrencyRelationship_type = 0;
entity* IFC4X3_TC1_IfcCurtainWall_type = 0;
entity* IFC4X3_TC1_IfcCurtainWallType_type = 0;
entity* IFC4X3_TC1_IfcCurve_type = 0;
entity* IFC4X3_TC1_IfcCurveBoundedPlane_type = 0;
entity* IFC4X3_TC1_IfcCurveBoundedSurface_type = 0;
entity* IFC4X3_TC1_IfcCurveSegment_type = 0;
entity* IFC4X3_TC1_IfcCurveStyle_type = 0;
entity* IFC4X3_TC1_IfcCurveStyleFont_type = 0;
entity* IFC4X3_TC1_IfcCurveStyleFontAndScaling_type = 0;
entity* IFC4X3_TC1_IfcCurveStyleFontPattern_type = 0;
entity* IFC4X3_TC1_IfcCylindricalSurface_type = 0;
entity* IFC4X3_TC1_IfcDamper_type = 0;
entity* IFC4X3_TC1_IfcDamperType_type = 0;
entity* IFC4X3_TC1_IfcDeepFoundation_type = 0;
entity* IFC4X3_TC1_IfcDeepFoundationType_type = 0;
entity* IFC4X3_TC1_IfcDerivedProfileDef_type = 0;
entity* IFC4X3_TC1_IfcDerivedUnit_type = 0;
entity* IFC4X3_TC1_IfcDerivedUnitElement_type = 0;
entity* IFC4X3_TC1_IfcDimensionalExponents_type = 0;
entity* IFC4X3_TC1_IfcDirection_type = 0;
entity* IFC4X3_TC1_IfcDirectrixCurveSweptAreaSolid_type = 0;
entity* IFC4X3_TC1_IfcDirectrixDerivedReferenceSweptAreaSolid_type = 0;
entity* IFC4X3_TC1_IfcDiscreteAccessory_type = 0;
entity* IFC4X3_TC1_IfcDiscreteAccessoryType_type = 0;
entity* IFC4X3_TC1_IfcDistributionBoard_type = 0;
entity* IFC4X3_TC1_IfcDistributionBoardType_type = 0;
entity* IFC4X3_TC1_IfcDistributionChamberElement_type = 0;
entity* IFC4X3_TC1_IfcDistributionChamberElementType_type = 0;
entity* IFC4X3_TC1_IfcDistributionCircuit_type = 0;
entity* IFC4X3_TC1_IfcDistributionControlElement_type = 0;
entity* IFC4X3_TC1_IfcDistributionControlElementType_type = 0;
entity* IFC4X3_TC1_IfcDistributionElement_type = 0;
entity* IFC4X3_TC1_IfcDistributionElementType_type = 0;
entity* IFC4X3_TC1_IfcDistributionFlowElement_type = 0;
entity* IFC4X3_TC1_IfcDistributionFlowElementType_type = 0;
entity* IFC4X3_TC1_IfcDistributionPort_type = 0;
entity* IFC4X3_TC1_IfcDistributionSystem_type = 0;
entity* IFC4X3_TC1_IfcDocumentInformation_type = 0;
entity* IFC4X3_TC1_IfcDocumentInformationRelationship_type = 0;
entity* IFC4X3_TC1_IfcDocumentReference_type = 0;
entity* IFC4X3_TC1_IfcDoor_type = 0;
entity* IFC4X3_TC1_IfcDoorLiningProperties_type = 0;
entity* IFC4X3_TC1_IfcDoorPanelProperties_type = 0;
entity* IFC4X3_TC1_IfcDoorType_type = 0;
entity* IFC4X3_TC1_IfcDraughtingPreDefinedColour_type = 0;
entity* IFC4X3_TC1_IfcDraughtingPreDefinedCurveFont_type = 0;
entity* IFC4X3_TC1_IfcDuctFitting_type = 0;
entity* IFC4X3_TC1_IfcDuctFittingType_type = 0;
entity* IFC4X3_TC1_IfcDuctSegment_type = 0;
entity* IFC4X3_TC1_IfcDuctSegmentType_type = 0;
entity* IFC4X3_TC1_IfcDuctSilencer_type = 0;
entity* IFC4X3_TC1_IfcDuctSilencerType_type = 0;
entity* IFC4X3_TC1_IfcEarthworksCut_type = 0;
entity* IFC4X3_TC1_IfcEarthworksElement_type = 0;
entity* IFC4X3_TC1_IfcEarthworksFill_type = 0;
entity* IFC4X3_TC1_IfcEdge_type = 0;
entity* IFC4X3_TC1_IfcEdgeCurve_type = 0;
entity* IFC4X3_TC1_IfcEdgeLoop_type = 0;
entity* IFC4X3_TC1_IfcElectricAppliance_type = 0;
entity* IFC4X3_TC1_IfcElectricApplianceType_type = 0;
entity* IFC4X3_TC1_IfcElectricDistributionBoard_type = 0;
entity* IFC4X3_TC1_IfcElectricDistributionBoardType_type = 0;
entity* IFC4X3_TC1_IfcElectricFlowStorageDevice_type = 0;
entity* IFC4X3_TC1_IfcElectricFlowStorageDeviceType_type = 0;
entity* IFC4X3_TC1_IfcElectricFlowTreatmentDevice_type = 0;
entity* IFC4X3_TC1_IfcElectricFlowTreatmentDeviceType_type = 0;
entity* IFC4X3_TC1_IfcElectricGenerator_type = 0;
entity* IFC4X3_TC1_IfcElectricGeneratorType_type = 0;
entity* IFC4X3_TC1_IfcElectricMotor_type = 0;
entity* IFC4X3_TC1_IfcElectricMotorType_type = 0;
entity* IFC4X3_TC1_IfcElectricTimeControl_type = 0;
entity* IFC4X3_TC1_IfcElectricTimeControlType_type = 0;
entity* IFC4X3_TC1_IfcElement_type = 0;
entity* IFC4X3_TC1_IfcElementAssembly_type = 0;
entity* IFC4X3_TC1_IfcElementAssemblyType_type = 0;
entity* IFC4X3_TC1_IfcElementComponent_type = 0;
entity* IFC4X3_TC1_IfcElementComponentType_type = 0;
entity* IFC4X3_TC1_IfcElementQuantity_type = 0;
entity* IFC4X3_TC1_IfcElementType_type = 0;
entity* IFC4X3_TC1_IfcElementarySurface_type = 0;
entity* IFC4X3_TC1_IfcEllipse_type = 0;
entity* IFC4X3_TC1_IfcEllipseProfileDef_type = 0;
entity* IFC4X3_TC1_IfcEnergyConversionDevice_type = 0;
entity* IFC4X3_TC1_IfcEnergyConversionDeviceType_type = 0;
entity* IFC4X3_TC1_IfcEngine_type = 0;
entity* IFC4X3_TC1_IfcEngineType_type = 0;
entity* IFC4X3_TC1_IfcEvaporativeCooler_type = 0;
entity* IFC4X3_TC1_IfcEvaporativeCoolerType_type = 0;
entity* IFC4X3_TC1_IfcEvaporator_type = 0;
entity* IFC4X3_TC1_IfcEvaporatorType_type = 0;
entity* IFC4X3_TC1_IfcEvent_type = 0;
entity* IFC4X3_TC1_IfcEventTime_type = 0;
entity* IFC4X3_TC1_IfcEventType_type = 0;
entity* IFC4X3_TC1_IfcExtendedProperties_type = 0;
entity* IFC4X3_TC1_IfcExternalInformation_type = 0;
entity* IFC4X3_TC1_IfcExternalReference_type = 0;
entity* IFC4X3_TC1_IfcExternalReferenceRelationship_type = 0;
entity* IFC4X3_TC1_IfcExternalSpatialElement_type = 0;
entity* IFC4X3_TC1_IfcExternalSpatialStructureElement_type = 0;
entity* IFC4X3_TC1_IfcExternallyDefinedHatchStyle_type = 0;
entity* IFC4X3_TC1_IfcExternallyDefinedSurfaceStyle_type = 0;
entity* IFC4X3_TC1_IfcExternallyDefinedTextFont_type = 0;
entity* IFC4X3_TC1_IfcExtrudedAreaSolid_type = 0;
entity* IFC4X3_TC1_IfcExtrudedAreaSolidTapered_type = 0;
entity* IFC4X3_TC1_IfcFace_type = 0;
entity* IFC4X3_TC1_IfcFaceBasedSurfaceModel_type = 0;
entity* IFC4X3_TC1_IfcFaceBound_type = 0;
entity* IFC4X3_TC1_IfcFaceOuterBound_type = 0;
entity* IFC4X3_TC1_IfcFaceSurface_type = 0;
entity* IFC4X3_TC1_IfcFacetedBrep_type = 0;
entity* IFC4X3_TC1_IfcFacetedBrepWithVoids_type = 0;
entity* IFC4X3_TC1_IfcFacility_type = 0;
entity* IFC4X3_TC1_IfcFacilityPart_type = 0;
entity* IFC4X3_TC1_IfcFacilityPartCommon_type = 0;
entity* IFC4X3_TC1_IfcFailureConnectionCondition_type = 0;
entity* IFC4X3_TC1_IfcFan_type = 0;
entity* IFC4X3_TC1_IfcFanType_type = 0;
entity* IFC4X3_TC1_IfcFastener_type = 0;
entity* IFC4X3_TC1_IfcFastenerType_type = 0;
entity* IFC4X3_TC1_IfcFeatureElement_type = 0;
entity* IFC4X3_TC1_IfcFeatureElementAddition_type = 0;
entity* IFC4X3_TC1_IfcFeatureElementSubtraction_type = 0;
entity* IFC4X3_TC1_IfcFillAreaStyle_type = 0;
entity* IFC4X3_TC1_IfcFillAreaStyleHatching_type = 0;
entity* IFC4X3_TC1_IfcFillAreaStyleTiles_type = 0;
entity* IFC4X3_TC1_IfcFilter_type = 0;
entity* IFC4X3_TC1_IfcFilterType_type = 0;
entity* IFC4X3_TC1_IfcFireSuppressionTerminal_type = 0;
entity* IFC4X3_TC1_IfcFireSuppressionTerminalType_type = 0;
entity* IFC4X3_TC1_IfcFixedReferenceSweptAreaSolid_type = 0;
entity* IFC4X3_TC1_IfcFlowController_type = 0;
entity* IFC4X3_TC1_IfcFlowControllerType_type = 0;
entity* IFC4X3_TC1_IfcFlowFitting_type = 0;
entity* IFC4X3_TC1_IfcFlowFittingType_type = 0;
entity* IFC4X3_TC1_IfcFlowInstrument_type = 0;
entity* IFC4X3_TC1_IfcFlowInstrumentType_type = 0;
entity* IFC4X3_TC1_IfcFlowMeter_type = 0;
entity* IFC4X3_TC1_IfcFlowMeterType_type = 0;
entity* IFC4X3_TC1_IfcFlowMovingDevice_type = 0;
entity* IFC4X3_TC1_IfcFlowMovingDeviceType_type = 0;
entity* IFC4X3_TC1_IfcFlowSegment_type = 0;
entity* IFC4X3_TC1_IfcFlowSegmentType_type = 0;
entity* IFC4X3_TC1_IfcFlowStorageDevice_type = 0;
entity* IFC4X3_TC1_IfcFlowStorageDeviceType_type = 0;
entity* IFC4X3_TC1_IfcFlowTerminal_type = 0;
entity* IFC4X3_TC1_IfcFlowTerminalType_type = 0;
entity* IFC4X3_TC1_IfcFlowTreatmentDevice_type = 0;
entity* IFC4X3_TC1_IfcFlowTreatmentDeviceType_type = 0;
entity* IFC4X3_TC1_IfcFooting_type = 0;
entity* IFC4X3_TC1_IfcFootingType_type = 0;
entity* IFC4X3_TC1_IfcFurnishingElement_type = 0;
entity* IFC4X3_TC1_IfcFurnishingElementType_type = 0;
entity* IFC4X3_TC1_IfcFurniture_type = 0;
entity* IFC4X3_TC1_IfcFurnitureType_type = 0;
entity* IFC4X3_TC1_IfcGeographicElement_type = 0;
entity* IFC4X3_TC1_IfcGeographicElementType_type = 0;
entity* IFC4X3_TC1_IfcGeometricCurveSet_type = 0;
entity* IFC4X3_TC1_IfcGeometricRepresentationContext_type = 0;
entity* IFC4X3_TC1_IfcGeometricRepresentationItem_type = 0;
entity* IFC4X3_TC1_IfcGeometricRepresentationSubContext_type = 0;
entity* IFC4X3_TC1_IfcGeometricSet_type = 0;
entity* IFC4X3_TC1_IfcGeomodel_type = 0;
entity* IFC4X3_TC1_IfcGeoslice_type = 0;
entity* IFC4X3_TC1_IfcGeotechnicalAssembly_type = 0;
entity* IFC4X3_TC1_IfcGeotechnicalElement_type = 0;
entity* IFC4X3_TC1_IfcGeotechnicalStratum_type = 0;
entity* IFC4X3_TC1_IfcGradientCurve_type = 0;
entity* IFC4X3_TC1_IfcGrid_type = 0;
entity* IFC4X3_TC1_IfcGridAxis_type = 0;
entity* IFC4X3_TC1_IfcGridPlacement_type = 0;
entity* IFC4X3_TC1_IfcGroup_type = 0;
entity* IFC4X3_TC1_IfcHalfSpaceSolid_type = 0;
entity* IFC4X3_TC1_IfcHeatExchanger_type = 0;
entity* IFC4X3_TC1_IfcHeatExchangerType_type = 0;
entity* IFC4X3_TC1_IfcHumidifier_type = 0;
entity* IFC4X3_TC1_IfcHumidifierType_type = 0;
entity* IFC4X3_TC1_IfcIShapeProfileDef_type = 0;
entity* IFC4X3_TC1_IfcImageTexture_type = 0;
entity* IFC4X3_TC1_IfcImpactProtectionDevice_type = 0;
entity* IFC4X3_TC1_IfcImpactProtectionDeviceType_type = 0;
entity* IFC4X3_TC1_IfcIndexedColourMap_type = 0;
entity* IFC4X3_TC1_IfcIndexedPolyCurve_type = 0;
entity* IFC4X3_TC1_IfcIndexedPolygonalFace_type = 0;
entity* IFC4X3_TC1_IfcIndexedPolygonalFaceWithVoids_type = 0;
entity* IFC4X3_TC1_IfcIndexedPolygonalTextureMap_type = 0;
entity* IFC4X3_TC1_IfcIndexedTextureMap_type = 0;
entity* IFC4X3_TC1_IfcIndexedTriangleTextureMap_type = 0;
entity* IFC4X3_TC1_IfcInterceptor_type = 0;
entity* IFC4X3_TC1_IfcInterceptorType_type = 0;
entity* IFC4X3_TC1_IfcIntersectionCurve_type = 0;
entity* IFC4X3_TC1_IfcInventory_type = 0;
entity* IFC4X3_TC1_IfcIrregularTimeSeries_type = 0;
entity* IFC4X3_TC1_IfcIrregularTimeSeriesValue_type = 0;
entity* IFC4X3_TC1_IfcJunctionBox_type = 0;
entity* IFC4X3_TC1_IfcJunctionBoxType_type = 0;
entity* IFC4X3_TC1_IfcKerb_type = 0;
entity* IFC4X3_TC1_IfcKerbType_type = 0;
entity* IFC4X3_TC1_IfcLShapeProfileDef_type = 0;
entity* IFC4X3_TC1_IfcLaborResource_type = 0;
entity* IFC4X3_TC1_IfcLaborResourceType_type = 0;
entity* IFC4X3_TC1_IfcLagTime_type = 0;
entity* IFC4X3_TC1_IfcLamp_type = 0;
entity* IFC4X3_TC1_IfcLampType_type = 0;
entity* IFC4X3_TC1_IfcLibraryInformation_type = 0;
entity* IFC4X3_TC1_IfcLibraryReference_type = 0;
entity* IFC4X3_TC1_IfcLightDistributionData_type = 0;
entity* IFC4X3_TC1_IfcLightFixture_type = 0;
entity* IFC4X3_TC1_IfcLightFixtureType_type = 0;
entity* IFC4X3_TC1_IfcLightIntensityDistribution_type = 0;
entity* IFC4X3_TC1_IfcLightSource_type = 0;
entity* IFC4X3_TC1_IfcLightSourceAmbient_type = 0;
entity* IFC4X3_TC1_IfcLightSourceDirectional_type = 0;
entity* IFC4X3_TC1_IfcLightSourceGoniometric_type = 0;
entity* IFC4X3_TC1_IfcLightSourcePositional_type = 0;
entity* IFC4X3_TC1_IfcLightSourceSpot_type = 0;
entity* IFC4X3_TC1_IfcLine_type = 0;
entity* IFC4X3_TC1_IfcLinearElement_type = 0;
entity* IFC4X3_TC1_IfcLinearPlacement_type = 0;
entity* IFC4X3_TC1_IfcLinearPositioningElement_type = 0;
entity* IFC4X3_TC1_IfcLiquidTerminal_type = 0;
entity* IFC4X3_TC1_IfcLiquidTerminalType_type = 0;
entity* IFC4X3_TC1_IfcLocalPlacement_type = 0;
entity* IFC4X3_TC1_IfcLoop_type = 0;
entity* IFC4X3_TC1_IfcManifoldSolidBrep_type = 0;
entity* IFC4X3_TC1_IfcMapConversion_type = 0;
entity* IFC4X3_TC1_IfcMappedItem_type = 0;
entity* IFC4X3_TC1_IfcMarineFacility_type = 0;
entity* IFC4X3_TC1_IfcMarinePart_type = 0;
entity* IFC4X3_TC1_IfcMaterial_type = 0;
entity* IFC4X3_TC1_IfcMaterialClassificationRelationship_type = 0;
entity* IFC4X3_TC1_IfcMaterialConstituent_type = 0;
entity* IFC4X3_TC1_IfcMaterialConstituentSet_type = 0;
entity* IFC4X3_TC1_IfcMaterialDefinition_type = 0;
entity* IFC4X3_TC1_IfcMaterialDefinitionRepresentation_type = 0;
entity* IFC4X3_TC1_IfcMaterialLayer_type = 0;
entity* IFC4X3_TC1_IfcMaterialLayerSet_type = 0;
entity* IFC4X3_TC1_IfcMaterialLayerSetUsage_type = 0;
entity* IFC4X3_TC1_IfcMaterialLayerWithOffsets_type = 0;
entity* IFC4X3_TC1_IfcMaterialList_type = 0;
entity* IFC4X3_TC1_IfcMaterialProfile_type = 0;
entity* IFC4X3_TC1_IfcMaterialProfileSet_type = 0;
entity* IFC4X3_TC1_IfcMaterialProfileSetUsage_type = 0;
entity* IFC4X3_TC1_IfcMaterialProfileSetUsageTapering_type = 0;
entity* IFC4X3_TC1_IfcMaterialProfileWithOffsets_type = 0;
entity* IFC4X3_TC1_IfcMaterialProperties_type = 0;
entity* IFC4X3_TC1_IfcMaterialRelationship_type = 0;
entity* IFC4X3_TC1_IfcMaterialUsageDefinition_type = 0;
entity* IFC4X3_TC1_IfcMeasureWithUnit_type = 0;
entity* IFC4X3_TC1_IfcMechanicalFastener_type = 0;
entity* IFC4X3_TC1_IfcMechanicalFastenerType_type = 0;
entity* IFC4X3_TC1_IfcMedicalDevice_type = 0;
entity* IFC4X3_TC1_IfcMedicalDeviceType_type = 0;
entity* IFC4X3_TC1_IfcMember_type = 0;
entity* IFC4X3_TC1_IfcMemberType_type = 0;
entity* IFC4X3_TC1_IfcMetric_type = 0;
entity* IFC4X3_TC1_IfcMirroredProfileDef_type = 0;
entity* IFC4X3_TC1_IfcMobileTelecommunicationsAppliance_type = 0;
entity* IFC4X3_TC1_IfcMobileTelecommunicationsApplianceType_type = 0;
entity* IFC4X3_TC1_IfcMonetaryUnit_type = 0;
entity* IFC4X3_TC1_IfcMooringDevice_type = 0;
entity* IFC4X3_TC1_IfcMooringDeviceType_type = 0;
entity* IFC4X3_TC1_IfcMotorConnection_type = 0;
entity* IFC4X3_TC1_IfcMotorConnectionType_type = 0;
entity* IFC4X3_TC1_IfcNamedUnit_type = 0;
entity* IFC4X3_TC1_IfcNavigationElement_type = 0;
entity* IFC4X3_TC1_IfcNavigationElementType_type = 0;
entity* IFC4X3_TC1_IfcObject_type = 0;
entity* IFC4X3_TC1_IfcObjectDefinition_type = 0;
entity* IFC4X3_TC1_IfcObjectPlacement_type = 0;
entity* IFC4X3_TC1_IfcObjective_type = 0;
entity* IFC4X3_TC1_IfcOccupant_type = 0;
entity* IFC4X3_TC1_IfcOffsetCurve_type = 0;
entity* IFC4X3_TC1_IfcOffsetCurve2D_type = 0;
entity* IFC4X3_TC1_IfcOffsetCurve3D_type = 0;
entity* IFC4X3_TC1_IfcOffsetCurveByDistances_type = 0;
entity* IFC4X3_TC1_IfcOpenCrossProfileDef_type = 0;
entity* IFC4X3_TC1_IfcOpenShell_type = 0;
entity* IFC4X3_TC1_IfcOpeningElement_type = 0;
entity* IFC4X3_TC1_IfcOrganization_type = 0;
entity* IFC4X3_TC1_IfcOrganizationRelationship_type = 0;
entity* IFC4X3_TC1_IfcOrientedEdge_type = 0;
entity* IFC4X3_TC1_IfcOuterBoundaryCurve_type = 0;
entity* IFC4X3_TC1_IfcOutlet_type = 0;
entity* IFC4X3_TC1_IfcOutletType_type = 0;
entity* IFC4X3_TC1_IfcOwnerHistory_type = 0;
entity* IFC4X3_TC1_IfcParameterizedProfileDef_type = 0;
entity* IFC4X3_TC1_IfcPath_type = 0;
entity* IFC4X3_TC1_IfcPavement_type = 0;
entity* IFC4X3_TC1_IfcPavementType_type = 0;
entity* IFC4X3_TC1_IfcPcurve_type = 0;
entity* IFC4X3_TC1_IfcPerformanceHistory_type = 0;
entity* IFC4X3_TC1_IfcPermeableCoveringProperties_type = 0;
entity* IFC4X3_TC1_IfcPermit_type = 0;
entity* IFC4X3_TC1_IfcPerson_type = 0;
entity* IFC4X3_TC1_IfcPersonAndOrganization_type = 0;
entity* IFC4X3_TC1_IfcPhysicalComplexQuantity_type = 0;
entity* IFC4X3_TC1_IfcPhysicalQuantity_type = 0;
entity* IFC4X3_TC1_IfcPhysicalSimpleQuantity_type = 0;
entity* IFC4X3_TC1_IfcPile_type = 0;
entity* IFC4X3_TC1_IfcPileType_type = 0;
entity* IFC4X3_TC1_IfcPipeFitting_type = 0;
entity* IFC4X3_TC1_IfcPipeFittingType_type = 0;
entity* IFC4X3_TC1_IfcPipeSegment_type = 0;
entity* IFC4X3_TC1_IfcPipeSegmentType_type = 0;
entity* IFC4X3_TC1_IfcPixelTexture_type = 0;
entity* IFC4X3_TC1_IfcPlacement_type = 0;
entity* IFC4X3_TC1_IfcPlanarBox_type = 0;
entity* IFC4X3_TC1_IfcPlanarExtent_type = 0;
entity* IFC4X3_TC1_IfcPlane_type = 0;
entity* IFC4X3_TC1_IfcPlate_type = 0;
entity* IFC4X3_TC1_IfcPlateType_type = 0;
entity* IFC4X3_TC1_IfcPoint_type = 0;
entity* IFC4X3_TC1_IfcPointByDistanceExpression_type = 0;
entity* IFC4X3_TC1_IfcPointOnCurve_type = 0;
entity* IFC4X3_TC1_IfcPointOnSurface_type = 0;
entity* IFC4X3_TC1_IfcPolyLoop_type = 0;
entity* IFC4X3_TC1_IfcPolygonalBoundedHalfSpace_type = 0;
entity* IFC4X3_TC1_IfcPolygonalFaceSet_type = 0;
entity* IFC4X3_TC1_IfcPolyline_type = 0;
entity* IFC4X3_TC1_IfcPolynomialCurve_type = 0;
entity* IFC4X3_TC1_IfcPort_type = 0;
entity* IFC4X3_TC1_IfcPositioningElement_type = 0;
entity* IFC4X3_TC1_IfcPostalAddress_type = 0;
entity* IFC4X3_TC1_IfcPreDefinedColour_type = 0;
entity* IFC4X3_TC1_IfcPreDefinedCurveFont_type = 0;
entity* IFC4X3_TC1_IfcPreDefinedItem_type = 0;
entity* IFC4X3_TC1_IfcPreDefinedProperties_type = 0;
entity* IFC4X3_TC1_IfcPreDefinedPropertySet_type = 0;
entity* IFC4X3_TC1_IfcPreDefinedTextFont_type = 0;
entity* IFC4X3_TC1_IfcPresentationItem_type = 0;
entity* IFC4X3_TC1_IfcPresentationLayerAssignment_type = 0;
entity* IFC4X3_TC1_IfcPresentationLayerWithStyle_type = 0;
entity* IFC4X3_TC1_IfcPresentationStyle_type = 0;
entity* IFC4X3_TC1_IfcProcedure_type = 0;
entity* IFC4X3_TC1_IfcProcedureType_type = 0;
entity* IFC4X3_TC1_IfcProcess_type = 0;
entity* IFC4X3_TC1_IfcProduct_type = 0;
entity* IFC4X3_TC1_IfcProductDefinitionShape_type = 0;
entity* IFC4X3_TC1_IfcProductRepresentation_type = 0;
entity* IFC4X3_TC1_IfcProfileDef_type = 0;
entity* IFC4X3_TC1_IfcProfileProperties_type = 0;
entity* IFC4X3_TC1_IfcProject_type = 0;
entity* IFC4X3_TC1_IfcProjectLibrary_type = 0;
entity* IFC4X3_TC1_IfcProjectOrder_type = 0;
entity* IFC4X3_TC1_IfcProjectedCRS_type = 0;
entity* IFC4X3_TC1_IfcProjectionElement_type = 0;
entity* IFC4X3_TC1_IfcProperty_type = 0;
entity* IFC4X3_TC1_IfcPropertyAbstraction_type = 0;
entity* IFC4X3_TC1_IfcPropertyBoundedValue_type = 0;
entity* IFC4X3_TC1_IfcPropertyDefinition_type = 0;
entity* IFC4X3_TC1_IfcPropertyDependencyRelationship_type = 0;
entity* IFC4X3_TC1_IfcPropertyEnumeratedValue_type = 0;
entity* IFC4X3_TC1_IfcPropertyEnumeration_type = 0;
entity* IFC4X3_TC1_IfcPropertyListValue_type = 0;
entity* IFC4X3_TC1_IfcPropertyReferenceValue_type = 0;
entity* IFC4X3_TC1_IfcPropertySet_type = 0;
entity* IFC4X3_TC1_IfcPropertySetDefinition_type = 0;
entity* IFC4X3_TC1_IfcPropertySetTemplate_type = 0;
entity* IFC4X3_TC1_IfcPropertySingleValue_type = 0;
entity* IFC4X3_TC1_IfcPropertyTableValue_type = 0;
entity* IFC4X3_TC1_IfcPropertyTemplate_type = 0;
entity* IFC4X3_TC1_IfcPropertyTemplateDefinition_type = 0;
entity* IFC4X3_TC1_IfcProtectiveDevice_type = 0;
entity* IFC4X3_TC1_IfcProtectiveDeviceTrippingUnit_type = 0;
entity* IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitType_type = 0;
entity* IFC4X3_TC1_IfcProtectiveDeviceType_type = 0;
entity* IFC4X3_TC1_IfcPump_type = 0;
entity* IFC4X3_TC1_IfcPumpType_type = 0;
entity* IFC4X3_TC1_IfcQuantityArea_type = 0;
entity* IFC4X3_TC1_IfcQuantityCount_type = 0;
entity* IFC4X3_TC1_IfcQuantityLength_type = 0;
entity* IFC4X3_TC1_IfcQuantityNumber_type = 0;
entity* IFC4X3_TC1_IfcQuantitySet_type = 0;
entity* IFC4X3_TC1_IfcQuantityTime_type = 0;
entity* IFC4X3_TC1_IfcQuantityVolume_type = 0;
entity* IFC4X3_TC1_IfcQuantityWeight_type = 0;
entity* IFC4X3_TC1_IfcRail_type = 0;
entity* IFC4X3_TC1_IfcRailType_type = 0;
entity* IFC4X3_TC1_IfcRailing_type = 0;
entity* IFC4X3_TC1_IfcRailingType_type = 0;
entity* IFC4X3_TC1_IfcRailway_type = 0;
entity* IFC4X3_TC1_IfcRailwayPart_type = 0;
entity* IFC4X3_TC1_IfcRamp_type = 0;
entity* IFC4X3_TC1_IfcRampFlight_type = 0;
entity* IFC4X3_TC1_IfcRampFlightType_type = 0;
entity* IFC4X3_TC1_IfcRampType_type = 0;
entity* IFC4X3_TC1_IfcRationalBSplineCurveWithKnots_type = 0;
entity* IFC4X3_TC1_IfcRationalBSplineSurfaceWithKnots_type = 0;
entity* IFC4X3_TC1_IfcRectangleHollowProfileDef_type = 0;
entity* IFC4X3_TC1_IfcRectangleProfileDef_type = 0;
entity* IFC4X3_TC1_IfcRectangularPyramid_type = 0;
entity* IFC4X3_TC1_IfcRectangularTrimmedSurface_type = 0;
entity* IFC4X3_TC1_IfcRecurrencePattern_type = 0;
entity* IFC4X3_TC1_IfcReference_type = 0;
entity* IFC4X3_TC1_IfcReferent_type = 0;
entity* IFC4X3_TC1_IfcRegularTimeSeries_type = 0;
entity* IFC4X3_TC1_IfcReinforcedSoil_type = 0;
entity* IFC4X3_TC1_IfcReinforcementBarProperties_type = 0;
entity* IFC4X3_TC1_IfcReinforcementDefinitionProperties_type = 0;
entity* IFC4X3_TC1_IfcReinforcingBar_type = 0;
entity* IFC4X3_TC1_IfcReinforcingBarType_type = 0;
entity* IFC4X3_TC1_IfcReinforcingElement_type = 0;
entity* IFC4X3_TC1_IfcReinforcingElementType_type = 0;
entity* IFC4X3_TC1_IfcReinforcingMesh_type = 0;
entity* IFC4X3_TC1_IfcReinforcingMeshType_type = 0;
entity* IFC4X3_TC1_IfcRelAdheresToElement_type = 0;
entity* IFC4X3_TC1_IfcRelAggregates_type = 0;
entity* IFC4X3_TC1_IfcRelAssigns_type = 0;
entity* IFC4X3_TC1_IfcRelAssignsToActor_type = 0;
entity* IFC4X3_TC1_IfcRelAssignsToControl_type = 0;
entity* IFC4X3_TC1_IfcRelAssignsToGroup_type = 0;
entity* IFC4X3_TC1_IfcRelAssignsToGroupByFactor_type = 0;
entity* IFC4X3_TC1_IfcRelAssignsToProcess_type = 0;
entity* IFC4X3_TC1_IfcRelAssignsToProduct_type = 0;
entity* IFC4X3_TC1_IfcRelAssignsToResource_type = 0;
entity* IFC4X3_TC1_IfcRelAssociates_type = 0;
entity* IFC4X3_TC1_IfcRelAssociatesApproval_type = 0;
entity* IFC4X3_TC1_IfcRelAssociatesClassification_type = 0;
entity* IFC4X3_TC1_IfcRelAssociatesConstraint_type = 0;
entity* IFC4X3_TC1_IfcRelAssociatesDocument_type = 0;
entity* IFC4X3_TC1_IfcRelAssociatesLibrary_type = 0;
entity* IFC4X3_TC1_IfcRelAssociatesMaterial_type = 0;
entity* IFC4X3_TC1_IfcRelAssociatesProfileDef_type = 0;
entity* IFC4X3_TC1_IfcRelConnects_type = 0;
entity* IFC4X3_TC1_IfcRelConnectsElements_type = 0;
entity* IFC4X3_TC1_IfcRelConnectsPathElements_type = 0;
entity* IFC4X3_TC1_IfcRelConnectsPortToElement_type = 0;
entity* IFC4X3_TC1_IfcRelConnectsPorts_type = 0;
entity* IFC4X3_TC1_IfcRelConnectsStructuralActivity_type = 0;
entity* IFC4X3_TC1_IfcRelConnectsStructuralMember_type = 0;
entity* IFC4X3_TC1_IfcRelConnectsWithEccentricity_type = 0;
entity* IFC4X3_TC1_IfcRelConnectsWithRealizingElements_type = 0;
entity* IFC4X3_TC1_IfcRelContainedInSpatialStructure_type = 0;
entity* IFC4X3_TC1_IfcRelCoversBldgElements_type = 0;
entity* IFC4X3_TC1_IfcRelCoversSpaces_type = 0;
entity* IFC4X3_TC1_IfcRelDeclares_type = 0;
entity* IFC4X3_TC1_IfcRelDecomposes_type = 0;
entity* IFC4X3_TC1_IfcRelDefines_type = 0;
entity* IFC4X3_TC1_IfcRelDefinesByObject_type = 0;
entity* IFC4X3_TC1_IfcRelDefinesByProperties_type = 0;
entity* IFC4X3_TC1_IfcRelDefinesByTemplate_type = 0;
entity* IFC4X3_TC1_IfcRelDefinesByType_type = 0;
entity* IFC4X3_TC1_IfcRelFillsElement_type = 0;
entity* IFC4X3_TC1_IfcRelFlowControlElements_type = 0;
entity* IFC4X3_TC1_IfcRelInterferesElements_type = 0;
entity* IFC4X3_TC1_IfcRelNests_type = 0;
entity* IFC4X3_TC1_IfcRelPositions_type = 0;
entity* IFC4X3_TC1_IfcRelProjectsElement_type = 0;
entity* IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type = 0;
entity* IFC4X3_TC1_IfcRelSequence_type = 0;
entity* IFC4X3_TC1_IfcRelServicesBuildings_type = 0;
entity* IFC4X3_TC1_IfcRelSpaceBoundary_type = 0;
entity* IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type = 0;
entity* IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type = 0;
entity* IFC4X3_TC1_IfcRelVoidsElement_type = 0;
entity* IFC4X3_TC1_IfcRelationship_type = 0;
entity* IFC4X3_TC1_IfcReparametrisedCompositeCurveSegment_type = 0;
entity* IFC4X3_TC1_IfcRepresentation_type = 0;
entity* IFC4X3_TC1_IfcRepresentationContext_type = 0;
entity* IFC4X3_TC1_IfcRepresentationItem_type = 0;
entity* IFC4X3_TC1_IfcRepresentationMap_type = 0;
entity* IFC4X3_TC1_IfcResource_type = 0;
entity* IFC4X3_TC1_IfcResourceApprovalRelationship_type = 0;
entity* IFC4X3_TC1_IfcResourceConstraintRelationship_type = 0;
entity* IFC4X3_TC1_IfcResourceLevelRelationship_type = 0;
entity* IFC4X3_TC1_IfcResourceTime_type = 0;
entity* IFC4X3_TC1_IfcRevolvedAreaSolid_type = 0;
entity* IFC4X3_TC1_IfcRevolvedAreaSolidTapered_type = 0;
entity* IFC4X3_TC1_IfcRightCircularCone_type = 0;
entity* IFC4X3_TC1_IfcRightCircularCylinder_type = 0;
entity* IFC4X3_TC1_IfcRoad_type = 0;
entity* IFC4X3_TC1_IfcRoadPart_type = 0;
entity* IFC4X3_TC1_IfcRoof_type = 0;
entity* IFC4X3_TC1_IfcRoofType_type = 0;
entity* IFC4X3_TC1_IfcRoot_type = 0;
entity* IFC4X3_TC1_IfcRoundedRectangleProfileDef_type = 0;
entity* IFC4X3_TC1_IfcSIUnit_type = 0;
entity* IFC4X3_TC1_IfcSanitaryTerminal_type = 0;
entity* IFC4X3_TC1_IfcSanitaryTerminalType_type = 0;
entity* IFC4X3_TC1_IfcSchedulingTime_type = 0;
entity* IFC4X3_TC1_IfcSeamCurve_type = 0;
entity* IFC4X3_TC1_IfcSecondOrderPolynomialSpiral_type = 0;
entity* IFC4X3_TC1_IfcSectionProperties_type = 0;
entity* IFC4X3_TC1_IfcSectionReinforcementProperties_type = 0;
entity* IFC4X3_TC1_IfcSectionedSolid_type = 0;
entity* IFC4X3_TC1_IfcSectionedSolidHorizontal_type = 0;
entity* IFC4X3_TC1_IfcSectionedSpine_type = 0;
entity* IFC4X3_TC1_IfcSectionedSurface_type = 0;
entity* IFC4X3_TC1_IfcSegment_type = 0;
entity* IFC4X3_TC1_IfcSegmentedReferenceCurve_type = 0;
entity* IFC4X3_TC1_IfcSensor_type = 0;
entity* IFC4X3_TC1_IfcSensorType_type = 0;
entity* IFC4X3_TC1_IfcSeventhOrderPolynomialSpiral_type = 0;
entity* IFC4X3_TC1_IfcShadingDevice_type = 0;
entity* IFC4X3_TC1_IfcShadingDeviceType_type = 0;
entity* IFC4X3_TC1_IfcShapeAspect_type = 0;
entity* IFC4X3_TC1_IfcShapeModel_type = 0;
entity* IFC4X3_TC1_IfcShapeRepresentation_type = 0;
entity* IFC4X3_TC1_IfcShellBasedSurfaceModel_type = 0;
entity* IFC4X3_TC1_IfcSign_type = 0;
entity* IFC4X3_TC1_IfcSignType_type = 0;
entity* IFC4X3_TC1_IfcSignal_type = 0;
entity* IFC4X3_TC1_IfcSignalType_type = 0;
entity* IFC4X3_TC1_IfcSimpleProperty_type = 0;
entity* IFC4X3_TC1_IfcSimplePropertyTemplate_type = 0;
entity* IFC4X3_TC1_IfcSineSpiral_type = 0;
entity* IFC4X3_TC1_IfcSite_type = 0;
entity* IFC4X3_TC1_IfcSlab_type = 0;
entity* IFC4X3_TC1_IfcSlabType_type = 0;
entity* IFC4X3_TC1_IfcSlippageConnectionCondition_type = 0;
entity* IFC4X3_TC1_IfcSolarDevice_type = 0;
entity* IFC4X3_TC1_IfcSolarDeviceType_type = 0;
entity* IFC4X3_TC1_IfcSolidModel_type = 0;
entity* IFC4X3_TC1_IfcSpace_type = 0;
entity* IFC4X3_TC1_IfcSpaceHeater_type = 0;
entity* IFC4X3_TC1_IfcSpaceHeaterType_type = 0;
entity* IFC4X3_TC1_IfcSpaceType_type = 0;
entity* IFC4X3_TC1_IfcSpatialElement_type = 0;
entity* IFC4X3_TC1_IfcSpatialElementType_type = 0;
entity* IFC4X3_TC1_IfcSpatialStructureElement_type = 0;
entity* IFC4X3_TC1_IfcSpatialStructureElementType_type = 0;
entity* IFC4X3_TC1_IfcSpatialZone_type = 0;
entity* IFC4X3_TC1_IfcSpatialZoneType_type = 0;
entity* IFC4X3_TC1_IfcSphere_type = 0;
entity* IFC4X3_TC1_IfcSphericalSurface_type = 0;
entity* IFC4X3_TC1_IfcSpiral_type = 0;
entity* IFC4X3_TC1_IfcStackTerminal_type = 0;
entity* IFC4X3_TC1_IfcStackTerminalType_type = 0;
entity* IFC4X3_TC1_IfcStair_type = 0;
entity* IFC4X3_TC1_IfcStairFlight_type = 0;
entity* IFC4X3_TC1_IfcStairFlightType_type = 0;
entity* IFC4X3_TC1_IfcStairType_type = 0;
entity* IFC4X3_TC1_IfcStructuralAction_type = 0;
entity* IFC4X3_TC1_IfcStructuralActivity_type = 0;
entity* IFC4X3_TC1_IfcStructuralAnalysisModel_type = 0;
entity* IFC4X3_TC1_IfcStructuralConnection_type = 0;
entity* IFC4X3_TC1_IfcStructuralConnectionCondition_type = 0;
entity* IFC4X3_TC1_IfcStructuralCurveAction_type = 0;
entity* IFC4X3_TC1_IfcStructuralCurveConnection_type = 0;
entity* IFC4X3_TC1_IfcStructuralCurveMember_type = 0;
entity* IFC4X3_TC1_IfcStructuralCurveMemberVarying_type = 0;
entity* IFC4X3_TC1_IfcStructuralCurveReaction_type = 0;
entity* IFC4X3_TC1_IfcStructuralItem_type = 0;
entity* IFC4X3_TC1_IfcStructuralLinearAction_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoad_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadCase_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadConfiguration_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadGroup_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadLinearForce_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadOrResult_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadPlanarForce_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadSingleDisplacement_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadSingleDisplacementDistortion_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadSingleForce_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadSingleForceWarping_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadStatic_type = 0;
entity* IFC4X3_TC1_IfcStructuralLoadTemperature_type = 0;
entity* IFC4X3_TC1_IfcStructuralMember_type = 0;
entity* IFC4X3_TC1_IfcStructuralPlanarAction_type = 0;
entity* IFC4X3_TC1_IfcStructuralPointAction_type = 0;
entity* IFC4X3_TC1_IfcStructuralPointConnection_type = 0;
entity* IFC4X3_TC1_IfcStructuralPointReaction_type = 0;
entity* IFC4X3_TC1_IfcStructuralReaction_type = 0;
entity* IFC4X3_TC1_IfcStructuralResultGroup_type = 0;
entity* IFC4X3_TC1_IfcStructuralSurfaceAction_type = 0;
entity* IFC4X3_TC1_IfcStructuralSurfaceConnection_type = 0;
entity* IFC4X3_TC1_IfcStructuralSurfaceMember_type = 0;
entity* IFC4X3_TC1_IfcStructuralSurfaceMemberVarying_type = 0;
entity* IFC4X3_TC1_IfcStructuralSurfaceReaction_type = 0;
entity* IFC4X3_TC1_IfcStyleModel_type = 0;
entity* IFC4X3_TC1_IfcStyledItem_type = 0;
entity* IFC4X3_TC1_IfcStyledRepresentation_type = 0;
entity* IFC4X3_TC1_IfcSubContractResource_type = 0;
entity* IFC4X3_TC1_IfcSubContractResourceType_type = 0;
entity* IFC4X3_TC1_IfcSubedge_type = 0;
entity* IFC4X3_TC1_IfcSurface_type = 0;
entity* IFC4X3_TC1_IfcSurfaceCurve_type = 0;
entity* IFC4X3_TC1_IfcSurfaceCurveSweptAreaSolid_type = 0;
entity* IFC4X3_TC1_IfcSurfaceFeature_type = 0;
entity* IFC4X3_TC1_IfcSurfaceOfLinearExtrusion_type = 0;
entity* IFC4X3_TC1_IfcSurfaceOfRevolution_type = 0;
entity* IFC4X3_TC1_IfcSurfaceReinforcementArea_type = 0;
entity* IFC4X3_TC1_IfcSurfaceStyle_type = 0;
entity* IFC4X3_TC1_IfcSurfaceStyleLighting_type = 0;
entity* IFC4X3_TC1_IfcSurfaceStyleRefraction_type = 0;
entity* IFC4X3_TC1_IfcSurfaceStyleRendering_type = 0;
entity* IFC4X3_TC1_IfcSurfaceStyleShading_type = 0;
entity* IFC4X3_TC1_IfcSurfaceStyleWithTextures_type = 0;
entity* IFC4X3_TC1_IfcSurfaceTexture_type = 0;
entity* IFC4X3_TC1_IfcSweptAreaSolid_type = 0;
entity* IFC4X3_TC1_IfcSweptDiskSolid_type = 0;
entity* IFC4X3_TC1_IfcSweptDiskSolidPolygonal_type = 0;
entity* IFC4X3_TC1_IfcSweptSurface_type = 0;
entity* IFC4X3_TC1_IfcSwitchingDevice_type = 0;
entity* IFC4X3_TC1_IfcSwitchingDeviceType_type = 0;
entity* IFC4X3_TC1_IfcSystem_type = 0;
entity* IFC4X3_TC1_IfcSystemFurnitureElement_type = 0;
entity* IFC4X3_TC1_IfcSystemFurnitureElementType_type = 0;
entity* IFC4X3_TC1_IfcTShapeProfileDef_type = 0;
entity* IFC4X3_TC1_IfcTable_type = 0;
entity* IFC4X3_TC1_IfcTableColumn_type = 0;
entity* IFC4X3_TC1_IfcTableRow_type = 0;
entity* IFC4X3_TC1_IfcTank_type = 0;
entity* IFC4X3_TC1_IfcTankType_type = 0;
entity* IFC4X3_TC1_IfcTask_type = 0;
entity* IFC4X3_TC1_IfcTaskTime_type = 0;
entity* IFC4X3_TC1_IfcTaskTimeRecurring_type = 0;
entity* IFC4X3_TC1_IfcTaskType_type = 0;
entity* IFC4X3_TC1_IfcTelecomAddress_type = 0;
entity* IFC4X3_TC1_IfcTendon_type = 0;
entity* IFC4X3_TC1_IfcTendonAnchor_type = 0;
entity* IFC4X3_TC1_IfcTendonAnchorType_type = 0;
entity* IFC4X3_TC1_IfcTendonConduit_type = 0;
entity* IFC4X3_TC1_IfcTendonConduitType_type = 0;
entity* IFC4X3_TC1_IfcTendonType_type = 0;
entity* IFC4X3_TC1_IfcTessellatedFaceSet_type = 0;
entity* IFC4X3_TC1_IfcTessellatedItem_type = 0;
entity* IFC4X3_TC1_IfcTextLiteral_type = 0;
entity* IFC4X3_TC1_IfcTextLiteralWithExtent_type = 0;
entity* IFC4X3_TC1_IfcTextStyle_type = 0;
entity* IFC4X3_TC1_IfcTextStyleFontModel_type = 0;
entity* IFC4X3_TC1_IfcTextStyleForDefinedFont_type = 0;
entity* IFC4X3_TC1_IfcTextStyleTextModel_type = 0;
entity* IFC4X3_TC1_IfcTextureCoordinate_type = 0;
entity* IFC4X3_TC1_IfcTextureCoordinateGenerator_type = 0;
entity* IFC4X3_TC1_IfcTextureCoordinateIndices_type = 0;
entity* IFC4X3_TC1_IfcTextureCoordinateIndicesWithVoids_type = 0;
entity* IFC4X3_TC1_IfcTextureMap_type = 0;
entity* IFC4X3_TC1_IfcTextureVertex_type = 0;
entity* IFC4X3_TC1_IfcTextureVertexList_type = 0;
entity* IFC4X3_TC1_IfcThirdOrderPolynomialSpiral_type = 0;
entity* IFC4X3_TC1_IfcTimePeriod_type = 0;
entity* IFC4X3_TC1_IfcTimeSeries_type = 0;
entity* IFC4X3_TC1_IfcTimeSeriesValue_type = 0;
entity* IFC4X3_TC1_IfcTopologicalRepresentationItem_type = 0;
entity* IFC4X3_TC1_IfcTopologyRepresentation_type = 0;
entity* IFC4X3_TC1_IfcToroidalSurface_type = 0;
entity* IFC4X3_TC1_IfcTrackElement_type = 0;
entity* IFC4X3_TC1_IfcTrackElementType_type = 0;
entity* IFC4X3_TC1_IfcTransformer_type = 0;
entity* IFC4X3_TC1_IfcTransformerType_type = 0;
entity* IFC4X3_TC1_IfcTransportElement_type = 0;
entity* IFC4X3_TC1_IfcTransportElementType_type = 0;
entity* IFC4X3_TC1_IfcTransportationDevice_type = 0;
entity* IFC4X3_TC1_IfcTransportationDeviceType_type = 0;
entity* IFC4X3_TC1_IfcTrapeziumProfileDef_type = 0;
entity* IFC4X3_TC1_IfcTriangulatedFaceSet_type = 0;
entity* IFC4X3_TC1_IfcTriangulatedIrregularNetwork_type = 0;
entity* IFC4X3_TC1_IfcTrimmedCurve_type = 0;
entity* IFC4X3_TC1_IfcTubeBundle_type = 0;
entity* IFC4X3_TC1_IfcTubeBundleType_type = 0;
entity* IFC4X3_TC1_IfcTypeObject_type = 0;
entity* IFC4X3_TC1_IfcTypeProcess_type = 0;
entity* IFC4X3_TC1_IfcTypeProduct_type = 0;
entity* IFC4X3_TC1_IfcTypeResource_type = 0;
entity* IFC4X3_TC1_IfcUShapeProfileDef_type = 0;
entity* IFC4X3_TC1_IfcUnitAssignment_type = 0;
entity* IFC4X3_TC1_IfcUnitaryControlElement_type = 0;
entity* IFC4X3_TC1_IfcUnitaryControlElementType_type = 0;
entity* IFC4X3_TC1_IfcUnitaryEquipment_type = 0;
entity* IFC4X3_TC1_IfcUnitaryEquipmentType_type = 0;
entity* IFC4X3_TC1_IfcValve_type = 0;
entity* IFC4X3_TC1_IfcValveType_type = 0;
entity* IFC4X3_TC1_IfcVector_type = 0;
entity* IFC4X3_TC1_IfcVehicle_type = 0;
entity* IFC4X3_TC1_IfcVehicleType_type = 0;
entity* IFC4X3_TC1_IfcVertex_type = 0;
entity* IFC4X3_TC1_IfcVertexLoop_type = 0;
entity* IFC4X3_TC1_IfcVertexPoint_type = 0;
entity* IFC4X3_TC1_IfcVibrationDamper_type = 0;
entity* IFC4X3_TC1_IfcVibrationDamperType_type = 0;
entity* IFC4X3_TC1_IfcVibrationIsolator_type = 0;
entity* IFC4X3_TC1_IfcVibrationIsolatorType_type = 0;
entity* IFC4X3_TC1_IfcVirtualElement_type = 0;
entity* IFC4X3_TC1_IfcVirtualGridIntersection_type = 0;
entity* IFC4X3_TC1_IfcVoidingFeature_type = 0;
entity* IFC4X3_TC1_IfcWall_type = 0;
entity* IFC4X3_TC1_IfcWallStandardCase_type = 0;
entity* IFC4X3_TC1_IfcWallType_type = 0;
entity* IFC4X3_TC1_IfcWasteTerminal_type = 0;
entity* IFC4X3_TC1_IfcWasteTerminalType_type = 0;
entity* IFC4X3_TC1_IfcWindow_type = 0;
entity* IFC4X3_TC1_IfcWindowLiningProperties_type = 0;
entity* IFC4X3_TC1_IfcWindowPanelProperties_type = 0;
entity* IFC4X3_TC1_IfcWindowType_type = 0;
entity* IFC4X3_TC1_IfcWorkCalendar_type = 0;
entity* IFC4X3_TC1_IfcWorkControl_type = 0;
entity* IFC4X3_TC1_IfcWorkPlan_type = 0;
entity* IFC4X3_TC1_IfcWorkSchedule_type = 0;
entity* IFC4X3_TC1_IfcWorkTime_type = 0;
entity* IFC4X3_TC1_IfcZShapeProfileDef_type = 0;
entity* IFC4X3_TC1_IfcZone_type = 0;
type_declaration* IFC4X3_TC1_IfcAbsorbedDoseMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcAccelerationMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcAmountOfSubstanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcAngularVelocityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcArcIndex_type = 0;
type_declaration* IFC4X3_TC1_IfcAreaDensityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcAreaMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcBinary_type = 0;
type_declaration* IFC4X3_TC1_IfcBoolean_type = 0;
type_declaration* IFC4X3_TC1_IfcBoxAlignment_type = 0;
type_declaration* IFC4X3_TC1_IfcCardinalPointReference_type = 0;
type_declaration* IFC4X3_TC1_IfcComplexNumber_type = 0;
type_declaration* IFC4X3_TC1_IfcCompoundPlaneAngleMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcContextDependentMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcCountMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcCurvatureMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcDate_type = 0;
type_declaration* IFC4X3_TC1_IfcDateTime_type = 0;
type_declaration* IFC4X3_TC1_IfcDayInMonthNumber_type = 0;
type_declaration* IFC4X3_TC1_IfcDayInWeekNumber_type = 0;
type_declaration* IFC4X3_TC1_IfcDescriptiveMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcDimensionCount_type = 0;
type_declaration* IFC4X3_TC1_IfcDoseEquivalentMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcDuration_type = 0;
type_declaration* IFC4X3_TC1_IfcDynamicViscosityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcElectricCapacitanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcElectricChargeMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcElectricConductanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcElectricCurrentMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcElectricResistanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcElectricVoltageMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcEnergyMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcFontStyle_type = 0;
type_declaration* IFC4X3_TC1_IfcFontVariant_type = 0;
type_declaration* IFC4X3_TC1_IfcFontWeight_type = 0;
type_declaration* IFC4X3_TC1_IfcForceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcFrequencyMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcGloballyUniqueId_type = 0;
type_declaration* IFC4X3_TC1_IfcHeatFluxDensityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcHeatingValueMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcIdentifier_type = 0;
type_declaration* IFC4X3_TC1_IfcIlluminanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcInductanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcInteger_type = 0;
type_declaration* IFC4X3_TC1_IfcIntegerCountRateMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcIonConcentrationMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcIsothermalMoistureCapacityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcKinematicViscosityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcLabel_type = 0;
type_declaration* IFC4X3_TC1_IfcLanguageId_type = 0;
type_declaration* IFC4X3_TC1_IfcLengthMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcLineIndex_type = 0;
type_declaration* IFC4X3_TC1_IfcLinearForceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcLinearMomentMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcLinearStiffnessMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcLinearVelocityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcLogical_type = 0;
type_declaration* IFC4X3_TC1_IfcLuminousFluxMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcLuminousIntensityDistributionMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcLuminousIntensityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMagneticFluxDensityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMagneticFluxMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMassDensityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMassFlowRateMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMassMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMassPerLengthMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcModulusOfElasticityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcModulusOfLinearSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcModulusOfSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMoistureDiffusivityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMolecularWeightMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMomentOfInertiaMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMonetaryMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcMonthInYearNumber_type = 0;
type_declaration* IFC4X3_TC1_IfcNonNegativeLengthMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcNormalisedRatioMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcNumericMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcPHMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcParameterValue_type = 0;
type_declaration* IFC4X3_TC1_IfcPlanarForceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcPlaneAngleMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcPositiveInteger_type = 0;
type_declaration* IFC4X3_TC1_IfcPositiveLengthMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcPositivePlaneAngleMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcPositiveRatioMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcPowerMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcPresentableText_type = 0;
type_declaration* IFC4X3_TC1_IfcPressureMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcPropertySetDefinitionSet_type = 0;
type_declaration* IFC4X3_TC1_IfcRadioActivityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcRatioMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcReal_type = 0;
type_declaration* IFC4X3_TC1_IfcRotationalFrequencyMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcRotationalMassMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcRotationalStiffnessMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSectionModulusMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSectionalAreaIntegralMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcShearModulusMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSolidAngleMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSoundPowerLevelMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSoundPowerMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSoundPressureLevelMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSoundPressureMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSpecificHeatCapacityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcSpecularExponent_type = 0;
type_declaration* IFC4X3_TC1_IfcSpecularRoughness_type = 0;
type_declaration* IFC4X3_TC1_IfcStrippedOptional_type = 0;
type_declaration* IFC4X3_TC1_IfcTemperatureGradientMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcTemperatureRateOfChangeMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcText_type = 0;
type_declaration* IFC4X3_TC1_IfcTextAlignment_type = 0;
type_declaration* IFC4X3_TC1_IfcTextDecoration_type = 0;
type_declaration* IFC4X3_TC1_IfcTextFontName_type = 0;
type_declaration* IFC4X3_TC1_IfcTextTransformation_type = 0;
type_declaration* IFC4X3_TC1_IfcThermalAdmittanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcThermalConductivityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcThermalExpansionCoefficientMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcThermalResistanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcThermalTransmittanceMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcThermodynamicTemperatureMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcTime_type = 0;
type_declaration* IFC4X3_TC1_IfcTimeMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcTimeStamp_type = 0;
type_declaration* IFC4X3_TC1_IfcTorqueMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcURIReference_type = 0;
type_declaration* IFC4X3_TC1_IfcVaporPermeabilityMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcVolumeMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcVolumetricFlowRateMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcWarpingConstantMeasure_type = 0;
type_declaration* IFC4X3_TC1_IfcWarpingMomentMeasure_type = 0;
select_type* IFC4X3_TC1_IfcActorSelect_type = 0;
select_type* IFC4X3_TC1_IfcAppliedValueSelect_type = 0;
select_type* IFC4X3_TC1_IfcAxis2Placement_type = 0;
select_type* IFC4X3_TC1_IfcBendingParameterSelect_type = 0;
select_type* IFC4X3_TC1_IfcBooleanOperand_type = 0;
select_type* IFC4X3_TC1_IfcClassificationReferenceSelect_type = 0;
select_type* IFC4X3_TC1_IfcClassificationSelect_type = 0;
select_type* IFC4X3_TC1_IfcColour_type = 0;
select_type* IFC4X3_TC1_IfcColourOrFactor_type = 0;
select_type* IFC4X3_TC1_IfcCoordinateReferenceSystemSelect_type = 0;
select_type* IFC4X3_TC1_IfcCsgSelect_type = 0;
select_type* IFC4X3_TC1_IfcCurveFontOrScaledCurveFontSelect_type = 0;
select_type* IFC4X3_TC1_IfcCurveMeasureSelect_type = 0;
select_type* IFC4X3_TC1_IfcCurveOnSurface_type = 0;
select_type* IFC4X3_TC1_IfcCurveOrEdgeCurve_type = 0;
select_type* IFC4X3_TC1_IfcCurveStyleFontSelect_type = 0;
select_type* IFC4X3_TC1_IfcDefinitionSelect_type = 0;
select_type* IFC4X3_TC1_IfcDerivedMeasureValue_type = 0;
select_type* IFC4X3_TC1_IfcDocumentSelect_type = 0;
select_type* IFC4X3_TC1_IfcFillStyleSelect_type = 0;
select_type* IFC4X3_TC1_IfcGeometricSetSelect_type = 0;
select_type* IFC4X3_TC1_IfcGridPlacementDirectionSelect_type = 0;
select_type* IFC4X3_TC1_IfcHatchLineDistanceSelect_type = 0;
select_type* IFC4X3_TC1_IfcInterferenceSelect_type = 0;
select_type* IFC4X3_TC1_IfcLayeredItem_type = 0;
select_type* IFC4X3_TC1_IfcLibrarySelect_type = 0;
select_type* IFC4X3_TC1_IfcLightDistributionDataSourceSelect_type = 0;
select_type* IFC4X3_TC1_IfcMaterialSelect_type = 0;
select_type* IFC4X3_TC1_IfcMeasureValue_type = 0;
select_type* IFC4X3_TC1_IfcMetricValueSelect_type = 0;
select_type* IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionSelect_type = 0;
select_type* IFC4X3_TC1_IfcModulusOfSubgradeReactionSelect_type = 0;
select_type* IFC4X3_TC1_IfcModulusOfTranslationalSubgradeReactionSelect_type = 0;
select_type* IFC4X3_TC1_IfcObjectReferenceSelect_type = 0;
select_type* IFC4X3_TC1_IfcPointOrVertexPoint_type = 0;
select_type* IFC4X3_TC1_IfcProcessSelect_type = 0;
select_type* IFC4X3_TC1_IfcProductRepresentationSelect_type = 0;
select_type* IFC4X3_TC1_IfcProductSelect_type = 0;
select_type* IFC4X3_TC1_IfcPropertySetDefinitionSelect_type = 0;
select_type* IFC4X3_TC1_IfcResourceObjectSelect_type = 0;
select_type* IFC4X3_TC1_IfcResourceSelect_type = 0;
select_type* IFC4X3_TC1_IfcRotationalStiffnessSelect_type = 0;
select_type* IFC4X3_TC1_IfcSegmentIndexSelect_type = 0;
select_type* IFC4X3_TC1_IfcShell_type = 0;
select_type* IFC4X3_TC1_IfcSimpleValue_type = 0;
select_type* IFC4X3_TC1_IfcSizeSelect_type = 0;
select_type* IFC4X3_TC1_IfcSolidOrShell_type = 0;
select_type* IFC4X3_TC1_IfcSpaceBoundarySelect_type = 0;
select_type* IFC4X3_TC1_IfcSpatialReferenceSelect_type = 0;
select_type* IFC4X3_TC1_IfcSpecularHighlightSelect_type = 0;
select_type* IFC4X3_TC1_IfcStructuralActivityAssignmentSelect_type = 0;
select_type* IFC4X3_TC1_IfcSurfaceOrFaceSurface_type = 0;
select_type* IFC4X3_TC1_IfcSurfaceStyleElementSelect_type = 0;
select_type* IFC4X3_TC1_IfcTextFontSelect_type = 0;
select_type* IFC4X3_TC1_IfcTimeOrRatioSelect_type = 0;
select_type* IFC4X3_TC1_IfcTranslationalStiffnessSelect_type = 0;
select_type* IFC4X3_TC1_IfcTrimmingSelect_type = 0;
select_type* IFC4X3_TC1_IfcUnit_type = 0;
select_type* IFC4X3_TC1_IfcValue_type = 0;
select_type* IFC4X3_TC1_IfcVectorOrDirection_type = 0;
select_type* IFC4X3_TC1_IfcWarpingStiffnessSelect_type = 0;
enumeration_type* IFC4X3_TC1_IfcActionRequestTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcActionSourceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcActionTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcActuatorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAddressTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAirTerminalBoxTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAirTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAirToAirHeatRecoveryTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAlarmTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAlignmentCantSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAlignmentHorizontalSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAlignmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAlignmentVerticalSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAnalysisModelTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAnalysisTheoryTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAnnotationTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcArithmeticOperatorEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAssemblyPlaceEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcAudioVisualApplianceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBSplineCurveForm_type = 0;
enumeration_type* IFC4X3_TC1_IfcBSplineSurfaceForm_type = 0;
enumeration_type* IFC4X3_TC1_IfcBeamTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBearingTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBenchmarkEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBoilerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBooleanOperator_type = 0;
enumeration_type* IFC4X3_TC1_IfcBridgePartTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBridgeTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBuildingElementPartTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBuildingElementProxyTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBuildingSystemTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBuiltSystemTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcBurnerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCableCarrierFittingTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCableCarrierSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCableFittingTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCableSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCaissonFoundationTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcChangeActionEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcChillerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcChimneyTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCoilTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcColumnTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCommunicationsApplianceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcComplexPropertyTemplateTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCompressorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCondenserTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcConnectionTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcConstraintEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcConstructionEquipmentResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcConstructionMaterialResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcConstructionProductResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcControllerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcConveyorSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCooledBeamTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCoolingTowerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCostItemTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCostScheduleTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCourseTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCoveringTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCrewResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCurtainWallTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcCurveInterpolationEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDamperTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDataOriginEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDerivedUnitEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDirectionSenseEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDiscreteAccessoryTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDistributionBoardTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDistributionChamberElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDistributionPortTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDistributionSystemEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDocumentConfidentialityEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDocumentStatusEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDoorPanelOperationEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDoorPanelPositionEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDoorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDoorTypeOperationEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDuctFittingTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDuctSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcDuctSilencerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcEarthworksCutTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcEarthworksFillTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElectricApplianceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElectricDistributionBoardTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElectricFlowStorageDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElectricFlowTreatmentDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElectricGeneratorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElectricMotorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElectricTimeControlTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElementAssemblyTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcElementCompositionEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcEngineTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcEvaporativeCoolerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcEvaporatorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcEventTriggerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcEventTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcExternalSpatialElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFacilityPartCommonTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFacilityUsageEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFanTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFastenerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFilterTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFireSuppressionTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFlowDirectionEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFlowInstrumentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFlowMeterTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFootingTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcFurnitureTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcGeographicElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcGeometricProjectionEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcGeotechnicalStratumTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcGlobalOrLocalEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcGridTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcHeatExchangerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcHumidifierTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcImpactProtectionDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcInterceptorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcInternalOrExternalEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcInventoryTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcJunctionBoxTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcKerbTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcKnotType_type = 0;
enumeration_type* IFC4X3_TC1_IfcLaborResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcLampTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcLayerSetDirectionEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcLightDistributionCurveEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcLightEmissionSourceEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcLightFixtureTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcLiquidTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcLoadGroupTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcLogicalOperatorEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcMarineFacilityTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcMarinePartTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcMechanicalFastenerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcMedicalDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcMemberTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcMobileTelecommunicationsApplianceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcMooringDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcMotorConnectionTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcNavigationElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcObjectiveEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcOccupantTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcOpeningElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcOutletTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPavementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPerformanceHistoryTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPermeableCoveringOperationEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPermitTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPhysicalOrVirtualEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPileConstructionEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPileTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPipeFittingTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPipeSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPlateTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPreferredSurfaceCurveRepresentation_type = 0;
enumeration_type* IFC4X3_TC1_IfcProcedureTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcProfileTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcProjectOrderTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcProjectedOrTrueLengthEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcProjectionElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPropertySetTemplateTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcProtectiveDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcPumpTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRailTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRailingTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRailwayPartTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRailwayTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRampFlightTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRampTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRecurrenceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcReferentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcReflectanceMethodEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcReinforcedSoilTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcReinforcingBarRoleEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcReinforcingBarSurfaceEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcReinforcingBarTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcReinforcingMeshTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRoadPartTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRoadTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRoleEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcRoofTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSIPrefix_type = 0;
enumeration_type* IFC4X3_TC1_IfcSIUnitName_type = 0;
enumeration_type* IFC4X3_TC1_IfcSanitaryTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSectionTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSensorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSequenceEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcShadingDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSignTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSignalTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSimplePropertyTemplateTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSlabTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSolarDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSpaceHeaterTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSpaceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSpatialZoneTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcStackTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcStairFlightTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcStairTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcStateEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcStructuralCurveActivityTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcStructuralCurveMemberTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcStructuralSurfaceActivityTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcStructuralSurfaceMemberTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSubContractResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSurfaceFeatureTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSurfaceSide_type = 0;
enumeration_type* IFC4X3_TC1_IfcSwitchingDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcSystemFurnitureElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTankTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTaskDurationEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTaskTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTendonAnchorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTendonConduitTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTendonTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTextPath_type = 0;
enumeration_type* IFC4X3_TC1_IfcTimeSeriesDataTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTrackElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTransformerTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTransitionCode_type = 0;
enumeration_type* IFC4X3_TC1_IfcTransportElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcTrimmingPreference_type = 0;
enumeration_type* IFC4X3_TC1_IfcTubeBundleTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcUnitEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcUnitaryControlElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcUnitaryEquipmentTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcValveTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcVehicleTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcVibrationDamperTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcVibrationIsolatorTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcVirtualElementTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcVoidingFeatureTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWallTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWasteTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWindowPanelOperationEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWindowPanelPositionEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWindowTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWindowTypePartitioningEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWorkCalendarTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWorkPlanTypeEnum_type = 0;
enumeration_type* IFC4X3_TC1_IfcWorkScheduleTypeEnum_type = 0;

class IFC4X3_TC1_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        switch(data->type()->index_in_schema()) {
            case 0: return new ::Ifc4x3_tc1::IfcAbsorbedDoseMeasure(data);
            case 1: return new ::Ifc4x3_tc1::IfcAccelerationMeasure(data);
            case 2: return new ::Ifc4x3_tc1::IfcActionRequest(data);
            case 3: return new ::Ifc4x3_tc1::IfcActionRequestTypeEnum(data);
            case 4: return new ::Ifc4x3_tc1::IfcActionSourceTypeEnum(data);
            case 5: return new ::Ifc4x3_tc1::IfcActionTypeEnum(data);
            case 6: return new ::Ifc4x3_tc1::IfcActor(data);
            case 7: return new ::Ifc4x3_tc1::IfcActorRole(data);
            case 9: return new ::Ifc4x3_tc1::IfcActuator(data);
            case 10: return new ::Ifc4x3_tc1::IfcActuatorType(data);
            case 11: return new ::Ifc4x3_tc1::IfcActuatorTypeEnum(data);
            case 12: return new ::Ifc4x3_tc1::IfcAddress(data);
            case 13: return new ::Ifc4x3_tc1::IfcAddressTypeEnum(data);
            case 14: return new ::Ifc4x3_tc1::IfcAdvancedBrep(data);
            case 15: return new ::Ifc4x3_tc1::IfcAdvancedBrepWithVoids(data);
            case 16: return new ::Ifc4x3_tc1::IfcAdvancedFace(data);
            case 17: return new ::Ifc4x3_tc1::IfcAirTerminal(data);
            case 18: return new ::Ifc4x3_tc1::IfcAirTerminalBox(data);
            case 19: return new ::Ifc4x3_tc1::IfcAirTerminalBoxType(data);
            case 20: return new ::Ifc4x3_tc1::IfcAirTerminalBoxTypeEnum(data);
            case 21: return new ::Ifc4x3_tc1::IfcAirTerminalType(data);
            case 22: return new ::Ifc4x3_tc1::IfcAirTerminalTypeEnum(data);
            case 23: return new ::Ifc4x3_tc1::IfcAirToAirHeatRecovery(data);
            case 24: return new ::Ifc4x3_tc1::IfcAirToAirHeatRecoveryType(data);
            case 25: return new ::Ifc4x3_tc1::IfcAirToAirHeatRecoveryTypeEnum(data);
            case 26: return new ::Ifc4x3_tc1::IfcAlarm(data);
            case 27: return new ::Ifc4x3_tc1::IfcAlarmType(data);
            case 28: return new ::Ifc4x3_tc1::IfcAlarmTypeEnum(data);
            case 29: return new ::Ifc4x3_tc1::IfcAlignment(data);
            case 30: return new ::Ifc4x3_tc1::IfcAlignmentCant(data);
            case 31: return new ::Ifc4x3_tc1::IfcAlignmentCantSegment(data);
            case 32: return new ::Ifc4x3_tc1::IfcAlignmentCantSegmentTypeEnum(data);
            case 33: return new ::Ifc4x3_tc1::IfcAlignmentHorizontal(data);
            case 34: return new ::Ifc4x3_tc1::IfcAlignmentHorizontalSegment(data);
            case 35: return new ::Ifc4x3_tc1::IfcAlignmentHorizontalSegmentTypeEnum(data);
            case 36: return new ::Ifc4x3_tc1::IfcAlignmentParameterSegment(data);
            case 37: return new ::Ifc4x3_tc1::IfcAlignmentSegment(data);
            case 38: return new ::Ifc4x3_tc1::IfcAlignmentTypeEnum(data);
            case 39: return new ::Ifc4x3_tc1::IfcAlignmentVertical(data);
            case 40: return new ::Ifc4x3_tc1::IfcAlignmentVerticalSegment(data);
            case 41: return new ::Ifc4x3_tc1::IfcAlignmentVerticalSegmentTypeEnum(data);
            case 42: return new ::Ifc4x3_tc1::IfcAmountOfSubstanceMeasure(data);
            case 43: return new ::Ifc4x3_tc1::IfcAnalysisModelTypeEnum(data);
            case 44: return new ::Ifc4x3_tc1::IfcAnalysisTheoryTypeEnum(data);
            case 45: return new ::Ifc4x3_tc1::IfcAngularVelocityMeasure(data);
            case 46: return new ::Ifc4x3_tc1::IfcAnnotation(data);
            case 47: return new ::Ifc4x3_tc1::IfcAnnotationFillArea(data);
            case 48: return new ::Ifc4x3_tc1::IfcAnnotationTypeEnum(data);
            case 49: return new ::Ifc4x3_tc1::IfcApplication(data);
            case 50: return new ::Ifc4x3_tc1::IfcAppliedValue(data);
            case 52: return new ::Ifc4x3_tc1::IfcApproval(data);
            case 53: return new ::Ifc4x3_tc1::IfcApprovalRelationship(data);
            case 54: return new ::Ifc4x3_tc1::IfcArbitraryClosedProfileDef(data);
            case 55: return new ::Ifc4x3_tc1::IfcArbitraryOpenProfileDef(data);
            case 56: return new ::Ifc4x3_tc1::IfcArbitraryProfileDefWithVoids(data);
            case 57: return new ::Ifc4x3_tc1::IfcArcIndex(data);
            case 58: return new ::Ifc4x3_tc1::IfcAreaDensityMeasure(data);
            case 59: return new ::Ifc4x3_tc1::IfcAreaMeasure(data);
            case 60: return new ::Ifc4x3_tc1::IfcArithmeticOperatorEnum(data);
            case 61: return new ::Ifc4x3_tc1::IfcAssemblyPlaceEnum(data);
            case 62: return new ::Ifc4x3_tc1::IfcAsset(data);
            case 63: return new ::Ifc4x3_tc1::IfcAsymmetricIShapeProfileDef(data);
            case 64: return new ::Ifc4x3_tc1::IfcAudioVisualAppliance(data);
            case 65: return new ::Ifc4x3_tc1::IfcAudioVisualApplianceType(data);
            case 66: return new ::Ifc4x3_tc1::IfcAudioVisualApplianceTypeEnum(data);
            case 67: return new ::Ifc4x3_tc1::IfcAxis1Placement(data);
            case 69: return new ::Ifc4x3_tc1::IfcAxis2Placement2D(data);
            case 70: return new ::Ifc4x3_tc1::IfcAxis2Placement3D(data);
            case 71: return new ::Ifc4x3_tc1::IfcAxis2PlacementLinear(data);
            case 72: return new ::Ifc4x3_tc1::IfcBeam(data);
            case 73: return new ::Ifc4x3_tc1::IfcBeamType(data);
            case 74: return new ::Ifc4x3_tc1::IfcBeamTypeEnum(data);
            case 75: return new ::Ifc4x3_tc1::IfcBearing(data);
            case 76: return new ::Ifc4x3_tc1::IfcBearingType(data);
            case 77: return new ::Ifc4x3_tc1::IfcBearingTypeEnum(data);
            case 78: return new ::Ifc4x3_tc1::IfcBenchmarkEnum(data);
            case 80: return new ::Ifc4x3_tc1::IfcBinary(data);
            case 81: return new ::Ifc4x3_tc1::IfcBlobTexture(data);
            case 82: return new ::Ifc4x3_tc1::IfcBlock(data);
            case 83: return new ::Ifc4x3_tc1::IfcBoiler(data);
            case 84: return new ::Ifc4x3_tc1::IfcBoilerType(data);
            case 85: return new ::Ifc4x3_tc1::IfcBoilerTypeEnum(data);
            case 86: return new ::Ifc4x3_tc1::IfcBoolean(data);
            case 87: return new ::Ifc4x3_tc1::IfcBooleanClippingResult(data);
            case 89: return new ::Ifc4x3_tc1::IfcBooleanOperator(data);
            case 90: return new ::Ifc4x3_tc1::IfcBooleanResult(data);
            case 91: return new ::Ifc4x3_tc1::IfcBorehole(data);
            case 92: return new ::Ifc4x3_tc1::IfcBoundaryCondition(data);
            case 93: return new ::Ifc4x3_tc1::IfcBoundaryCurve(data);
            case 94: return new ::Ifc4x3_tc1::IfcBoundaryEdgeCondition(data);
            case 95: return new ::Ifc4x3_tc1::IfcBoundaryFaceCondition(data);
            case 96: return new ::Ifc4x3_tc1::IfcBoundaryNodeCondition(data);
            case 97: return new ::Ifc4x3_tc1::IfcBoundaryNodeConditionWarping(data);
            case 98: return new ::Ifc4x3_tc1::IfcBoundedCurve(data);
            case 99: return new ::Ifc4x3_tc1::IfcBoundedSurface(data);
            case 100: return new ::Ifc4x3_tc1::IfcBoundingBox(data);
            case 101: return new ::Ifc4x3_tc1::IfcBoxAlignment(data);
            case 102: return new ::Ifc4x3_tc1::IfcBoxedHalfSpace(data);
            case 103: return new ::Ifc4x3_tc1::IfcBridge(data);
            case 104: return new ::Ifc4x3_tc1::IfcBridgePart(data);
            case 105: return new ::Ifc4x3_tc1::IfcBridgePartTypeEnum(data);
            case 106: return new ::Ifc4x3_tc1::IfcBridgeTypeEnum(data);
            case 107: return new ::Ifc4x3_tc1::IfcBSplineCurve(data);
            case 108: return new ::Ifc4x3_tc1::IfcBSplineCurveForm(data);
            case 109: return new ::Ifc4x3_tc1::IfcBSplineCurveWithKnots(data);
            case 110: return new ::Ifc4x3_tc1::IfcBSplineSurface(data);
            case 111: return new ::Ifc4x3_tc1::IfcBSplineSurfaceForm(data);
            case 112: return new ::Ifc4x3_tc1::IfcBSplineSurfaceWithKnots(data);
            case 113: return new ::Ifc4x3_tc1::IfcBuilding(data);
            case 114: return new ::Ifc4x3_tc1::IfcBuildingElementPart(data);
            case 115: return new ::Ifc4x3_tc1::IfcBuildingElementPartType(data);
            case 116: return new ::Ifc4x3_tc1::IfcBuildingElementPartTypeEnum(data);
            case 117: return new ::Ifc4x3_tc1::IfcBuildingElementProxy(data);
            case 118: return new ::Ifc4x3_tc1::IfcBuildingElementProxyType(data);
            case 119: return new ::Ifc4x3_tc1::IfcBuildingElementProxyTypeEnum(data);
            case 120: return new ::Ifc4x3_tc1::IfcBuildingStorey(data);
            case 121: return new ::Ifc4x3_tc1::IfcBuildingSystem(data);
            case 122: return new ::Ifc4x3_tc1::IfcBuildingSystemTypeEnum(data);
            case 123: return new ::Ifc4x3_tc1::IfcBuiltElement(data);
            case 124: return new ::Ifc4x3_tc1::IfcBuiltElementType(data);
            case 125: return new ::Ifc4x3_tc1::IfcBuiltSystem(data);
            case 126: return new ::Ifc4x3_tc1::IfcBuiltSystemTypeEnum(data);
            case 127: return new ::Ifc4x3_tc1::IfcBurner(data);
            case 128: return new ::Ifc4x3_tc1::IfcBurnerType(data);
            case 129: return new ::Ifc4x3_tc1::IfcBurnerTypeEnum(data);
            case 130: return new ::Ifc4x3_tc1::IfcCableCarrierFitting(data);
            case 131: return new ::Ifc4x3_tc1::IfcCableCarrierFittingType(data);
            case 132: return new ::Ifc4x3_tc1::IfcCableCarrierFittingTypeEnum(data);
            case 133: return new ::Ifc4x3_tc1::IfcCableCarrierSegment(data);
            case 134: return new ::Ifc4x3_tc1::IfcCableCarrierSegmentType(data);
            case 135: return new ::Ifc4x3_tc1::IfcCableCarrierSegmentTypeEnum(data);
            case 136: return new ::Ifc4x3_tc1::IfcCableFitting(data);
            case 137: return new ::Ifc4x3_tc1::IfcCableFittingType(data);
            case 138: return new ::Ifc4x3_tc1::IfcCableFittingTypeEnum(data);
            case 139: return new ::Ifc4x3_tc1::IfcCableSegment(data);
            case 140: return new ::Ifc4x3_tc1::IfcCableSegmentType(data);
            case 141: return new ::Ifc4x3_tc1::IfcCableSegmentTypeEnum(data);
            case 142: return new ::Ifc4x3_tc1::IfcCaissonFoundation(data);
            case 143: return new ::Ifc4x3_tc1::IfcCaissonFoundationType(data);
            case 144: return new ::Ifc4x3_tc1::IfcCaissonFoundationTypeEnum(data);
            case 145: return new ::Ifc4x3_tc1::IfcCardinalPointReference(data);
            case 146: return new ::Ifc4x3_tc1::IfcCartesianPoint(data);
            case 147: return new ::Ifc4x3_tc1::IfcCartesianPointList(data);
            case 148: return new ::Ifc4x3_tc1::IfcCartesianPointList2D(data);
            case 149: return new ::Ifc4x3_tc1::IfcCartesianPointList3D(data);
            case 150: return new ::Ifc4x3_tc1::IfcCartesianTransformationOperator(data);
            case 151: return new ::Ifc4x3_tc1::IfcCartesianTransformationOperator2D(data);
            case 152: return new ::Ifc4x3_tc1::IfcCartesianTransformationOperator2DnonUniform(data);
            case 153: return new ::Ifc4x3_tc1::IfcCartesianTransformationOperator3D(data);
            case 154: return new ::Ifc4x3_tc1::IfcCartesianTransformationOperator3DnonUniform(data);
            case 155: return new ::Ifc4x3_tc1::IfcCenterLineProfileDef(data);
            case 156: return new ::Ifc4x3_tc1::IfcChangeActionEnum(data);
            case 157: return new ::Ifc4x3_tc1::IfcChiller(data);
            case 158: return new ::Ifc4x3_tc1::IfcChillerType(data);
            case 159: return new ::Ifc4x3_tc1::IfcChillerTypeEnum(data);
            case 160: return new ::Ifc4x3_tc1::IfcChimney(data);
            case 161: return new ::Ifc4x3_tc1::IfcChimneyType(data);
            case 162: return new ::Ifc4x3_tc1::IfcChimneyTypeEnum(data);
            case 163: return new ::Ifc4x3_tc1::IfcCircle(data);
            case 164: return new ::Ifc4x3_tc1::IfcCircleHollowProfileDef(data);
            case 165: return new ::Ifc4x3_tc1::IfcCircleProfileDef(data);
            case 166: return new ::Ifc4x3_tc1::IfcCivilElement(data);
            case 167: return new ::Ifc4x3_tc1::IfcCivilElementType(data);
            case 168: return new ::Ifc4x3_tc1::IfcClassification(data);
            case 169: return new ::Ifc4x3_tc1::IfcClassificationReference(data);
            case 172: return new ::Ifc4x3_tc1::IfcClosedShell(data);
            case 173: return new ::Ifc4x3_tc1::IfcClothoid(data);
            case 174: return new ::Ifc4x3_tc1::IfcCoil(data);
            case 175: return new ::Ifc4x3_tc1::IfcCoilType(data);
            case 176: return new ::Ifc4x3_tc1::IfcCoilTypeEnum(data);
            case 179: return new ::Ifc4x3_tc1::IfcColourRgb(data);
            case 180: return new ::Ifc4x3_tc1::IfcColourRgbList(data);
            case 181: return new ::Ifc4x3_tc1::IfcColourSpecification(data);
            case 182: return new ::Ifc4x3_tc1::IfcColumn(data);
            case 183: return new ::Ifc4x3_tc1::IfcColumnType(data);
            case 184: return new ::Ifc4x3_tc1::IfcColumnTypeEnum(data);
            case 185: return new ::Ifc4x3_tc1::IfcCommunicationsAppliance(data);
            case 186: return new ::Ifc4x3_tc1::IfcCommunicationsApplianceType(data);
            case 187: return new ::Ifc4x3_tc1::IfcCommunicationsApplianceTypeEnum(data);
            case 188: return new ::Ifc4x3_tc1::IfcComplexNumber(data);
            case 189: return new ::Ifc4x3_tc1::IfcComplexProperty(data);
            case 190: return new ::Ifc4x3_tc1::IfcComplexPropertyTemplate(data);
            case 191: return new ::Ifc4x3_tc1::IfcComplexPropertyTemplateTypeEnum(data);
            case 192: return new ::Ifc4x3_tc1::IfcCompositeCurve(data);
            case 193: return new ::Ifc4x3_tc1::IfcCompositeCurveOnSurface(data);
            case 194: return new ::Ifc4x3_tc1::IfcCompositeCurveSegment(data);
            case 195: return new ::Ifc4x3_tc1::IfcCompositeProfileDef(data);
            case 196: return new ::Ifc4x3_tc1::IfcCompoundPlaneAngleMeasure(data);
            case 197: return new ::Ifc4x3_tc1::IfcCompressor(data);
            case 198: return new ::Ifc4x3_tc1::IfcCompressorType(data);
            case 199: return new ::Ifc4x3_tc1::IfcCompressorTypeEnum(data);
            case 200: return new ::Ifc4x3_tc1::IfcCondenser(data);
            case 201: return new ::Ifc4x3_tc1::IfcCondenserType(data);
            case 202: return new ::Ifc4x3_tc1::IfcCondenserTypeEnum(data);
            case 203: return new ::Ifc4x3_tc1::IfcConic(data);
            case 204: return new ::Ifc4x3_tc1::IfcConnectedFaceSet(data);
            case 205: return new ::Ifc4x3_tc1::IfcConnectionCurveGeometry(data);
            case 206: return new ::Ifc4x3_tc1::IfcConnectionGeometry(data);
            case 207: return new ::Ifc4x3_tc1::IfcConnectionPointEccentricity(data);
            case 208: return new ::Ifc4x3_tc1::IfcConnectionPointGeometry(data);
            case 209: return new ::Ifc4x3_tc1::IfcConnectionSurfaceGeometry(data);
            case 210: return new ::Ifc4x3_tc1::IfcConnectionTypeEnum(data);
            case 211: return new ::Ifc4x3_tc1::IfcConnectionVolumeGeometry(data);
            case 212: return new ::Ifc4x3_tc1::IfcConstraint(data);
            case 213: return new ::Ifc4x3_tc1::IfcConstraintEnum(data);
            case 214: return new ::Ifc4x3_tc1::IfcConstructionEquipmentResource(data);
            case 215: return new ::Ifc4x3_tc1::IfcConstructionEquipmentResourceType(data);
            case 216: return new ::Ifc4x3_tc1::IfcConstructionEquipmentResourceTypeEnum(data);
            case 217: return new ::Ifc4x3_tc1::IfcConstructionMaterialResource(data);
            case 218: return new ::Ifc4x3_tc1::IfcConstructionMaterialResourceType(data);
            case 219: return new ::Ifc4x3_tc1::IfcConstructionMaterialResourceTypeEnum(data);
            case 220: return new ::Ifc4x3_tc1::IfcConstructionProductResource(data);
            case 221: return new ::Ifc4x3_tc1::IfcConstructionProductResourceType(data);
            case 222: return new ::Ifc4x3_tc1::IfcConstructionProductResourceTypeEnum(data);
            case 223: return new ::Ifc4x3_tc1::IfcConstructionResource(data);
            case 224: return new ::Ifc4x3_tc1::IfcConstructionResourceType(data);
            case 225: return new ::Ifc4x3_tc1::IfcContext(data);
            case 226: return new ::Ifc4x3_tc1::IfcContextDependentMeasure(data);
            case 227: return new ::Ifc4x3_tc1::IfcContextDependentUnit(data);
            case 228: return new ::Ifc4x3_tc1::IfcControl(data);
            case 229: return new ::Ifc4x3_tc1::IfcController(data);
            case 230: return new ::Ifc4x3_tc1::IfcControllerType(data);
            case 231: return new ::Ifc4x3_tc1::IfcControllerTypeEnum(data);
            case 232: return new ::Ifc4x3_tc1::IfcConversionBasedUnit(data);
            case 233: return new ::Ifc4x3_tc1::IfcConversionBasedUnitWithOffset(data);
            case 234: return new ::Ifc4x3_tc1::IfcConveyorSegment(data);
            case 235: return new ::Ifc4x3_tc1::IfcConveyorSegmentType(data);
            case 236: return new ::Ifc4x3_tc1::IfcConveyorSegmentTypeEnum(data);
            case 237: return new ::Ifc4x3_tc1::IfcCooledBeam(data);
            case 238: return new ::Ifc4x3_tc1::IfcCooledBeamType(data);
            case 239: return new ::Ifc4x3_tc1::IfcCooledBeamTypeEnum(data);
            case 240: return new ::Ifc4x3_tc1::IfcCoolingTower(data);
            case 241: return new ::Ifc4x3_tc1::IfcCoolingTowerType(data);
            case 242: return new ::Ifc4x3_tc1::IfcCoolingTowerTypeEnum(data);
            case 243: return new ::Ifc4x3_tc1::IfcCoordinateOperation(data);
            case 244: return new ::Ifc4x3_tc1::IfcCoordinateReferenceSystem(data);
            case 246: return new ::Ifc4x3_tc1::IfcCosineSpiral(data);
            case 247: return new ::Ifc4x3_tc1::IfcCostItem(data);
            case 248: return new ::Ifc4x3_tc1::IfcCostItemTypeEnum(data);
            case 249: return new ::Ifc4x3_tc1::IfcCostSchedule(data);
            case 250: return new ::Ifc4x3_tc1::IfcCostScheduleTypeEnum(data);
            case 251: return new ::Ifc4x3_tc1::IfcCostValue(data);
            case 252: return new ::Ifc4x3_tc1::IfcCountMeasure(data);
            case 253: return new ::Ifc4x3_tc1::IfcCourse(data);
            case 254: return new ::Ifc4x3_tc1::IfcCourseType(data);
            case 255: return new ::Ifc4x3_tc1::IfcCourseTypeEnum(data);
            case 256: return new ::Ifc4x3_tc1::IfcCovering(data);
            case 257: return new ::Ifc4x3_tc1::IfcCoveringType(data);
            case 258: return new ::Ifc4x3_tc1::IfcCoveringTypeEnum(data);
            case 259: return new ::Ifc4x3_tc1::IfcCrewResource(data);
            case 260: return new ::Ifc4x3_tc1::IfcCrewResourceType(data);
            case 261: return new ::Ifc4x3_tc1::IfcCrewResourceTypeEnum(data);
            case 262: return new ::Ifc4x3_tc1::IfcCsgPrimitive3D(data);
            case 264: return new ::Ifc4x3_tc1::IfcCsgSolid(data);
            case 265: return new ::Ifc4x3_tc1::IfcCShapeProfileDef(data);
            case 266: return new ::Ifc4x3_tc1::IfcCurrencyRelationship(data);
            case 267: return new ::Ifc4x3_tc1::IfcCurtainWall(data);
            case 268: return new ::Ifc4x3_tc1::IfcCurtainWallType(data);
            case 269: return new ::Ifc4x3_tc1::IfcCurtainWallTypeEnum(data);
            case 270: return new ::Ifc4x3_tc1::IfcCurvatureMeasure(data);
            case 271: return new ::Ifc4x3_tc1::IfcCurve(data);
            case 272: return new ::Ifc4x3_tc1::IfcCurveBoundedPlane(data);
            case 273: return new ::Ifc4x3_tc1::IfcCurveBoundedSurface(data);
            case 275: return new ::Ifc4x3_tc1::IfcCurveInterpolationEnum(data);
            case 279: return new ::Ifc4x3_tc1::IfcCurveSegment(data);
            case 280: return new ::Ifc4x3_tc1::IfcCurveStyle(data);
            case 281: return new ::Ifc4x3_tc1::IfcCurveStyleFont(data);
            case 282: return new ::Ifc4x3_tc1::IfcCurveStyleFontAndScaling(data);
            case 283: return new ::Ifc4x3_tc1::IfcCurveStyleFontPattern(data);
            case 285: return new ::Ifc4x3_tc1::IfcCylindricalSurface(data);
            case 286: return new ::Ifc4x3_tc1::IfcDamper(data);
            case 287: return new ::Ifc4x3_tc1::IfcDamperType(data);
            case 288: return new ::Ifc4x3_tc1::IfcDamperTypeEnum(data);
            case 289: return new ::Ifc4x3_tc1::IfcDataOriginEnum(data);
            case 290: return new ::Ifc4x3_tc1::IfcDate(data);
            case 291: return new ::Ifc4x3_tc1::IfcDateTime(data);
            case 292: return new ::Ifc4x3_tc1::IfcDayInMonthNumber(data);
            case 293: return new ::Ifc4x3_tc1::IfcDayInWeekNumber(data);
            case 294: return new ::Ifc4x3_tc1::IfcDeepFoundation(data);
            case 295: return new ::Ifc4x3_tc1::IfcDeepFoundationType(data);
            case 298: return new ::Ifc4x3_tc1::IfcDerivedProfileDef(data);
            case 299: return new ::Ifc4x3_tc1::IfcDerivedUnit(data);
            case 300: return new ::Ifc4x3_tc1::IfcDerivedUnitElement(data);
            case 301: return new ::Ifc4x3_tc1::IfcDerivedUnitEnum(data);
            case 302: return new ::Ifc4x3_tc1::IfcDescriptiveMeasure(data);
            case 303: return new ::Ifc4x3_tc1::IfcDimensionalExponents(data);
            case 304: return new ::Ifc4x3_tc1::IfcDimensionCount(data);
            case 305: return new ::Ifc4x3_tc1::IfcDirection(data);
            case 306: return new ::Ifc4x3_tc1::IfcDirectionSenseEnum(data);
            case 307: return new ::Ifc4x3_tc1::IfcDirectrixCurveSweptAreaSolid(data);
            case 308: return new ::Ifc4x3_tc1::IfcDirectrixDerivedReferenceSweptAreaSolid(data);
            case 309: return new ::Ifc4x3_tc1::IfcDiscreteAccessory(data);
            case 310: return new ::Ifc4x3_tc1::IfcDiscreteAccessoryType(data);
            case 311: return new ::Ifc4x3_tc1::IfcDiscreteAccessoryTypeEnum(data);
            case 312: return new ::Ifc4x3_tc1::IfcDistributionBoard(data);
            case 313: return new ::Ifc4x3_tc1::IfcDistributionBoardType(data);
            case 314: return new ::Ifc4x3_tc1::IfcDistributionBoardTypeEnum(data);
            case 315: return new ::Ifc4x3_tc1::IfcDistributionChamberElement(data);
            case 316: return new ::Ifc4x3_tc1::IfcDistributionChamberElementType(data);
            case 317: return new ::Ifc4x3_tc1::IfcDistributionChamberElementTypeEnum(data);
            case 318: return new ::Ifc4x3_tc1::IfcDistributionCircuit(data);
            case 319: return new ::Ifc4x3_tc1::IfcDistributionControlElement(data);
            case 320: return new ::Ifc4x3_tc1::IfcDistributionControlElementType(data);
            case 321: return new ::Ifc4x3_tc1::IfcDistributionElement(data);
            case 322: return new ::Ifc4x3_tc1::IfcDistributionElementType(data);
            case 323: return new ::Ifc4x3_tc1::IfcDistributionFlowElement(data);
            case 324: return new ::Ifc4x3_tc1::IfcDistributionFlowElementType(data);
            case 325: return new ::Ifc4x3_tc1::IfcDistributionPort(data);
            case 326: return new ::Ifc4x3_tc1::IfcDistributionPortTypeEnum(data);
            case 327: return new ::Ifc4x3_tc1::IfcDistributionSystem(data);
            case 328: return new ::Ifc4x3_tc1::IfcDistributionSystemEnum(data);
            case 329: return new ::Ifc4x3_tc1::IfcDocumentConfidentialityEnum(data);
            case 330: return new ::Ifc4x3_tc1::IfcDocumentInformation(data);
            case 331: return new ::Ifc4x3_tc1::IfcDocumentInformationRelationship(data);
            case 332: return new ::Ifc4x3_tc1::IfcDocumentReference(data);
            case 334: return new ::Ifc4x3_tc1::IfcDocumentStatusEnum(data);
            case 335: return new ::Ifc4x3_tc1::IfcDoor(data);
            case 336: return new ::Ifc4x3_tc1::IfcDoorLiningProperties(data);
            case 337: return new ::Ifc4x3_tc1::IfcDoorPanelOperationEnum(data);
            case 338: return new ::Ifc4x3_tc1::IfcDoorPanelPositionEnum(data);
            case 339: return new ::Ifc4x3_tc1::IfcDoorPanelProperties(data);
            case 340: return new ::Ifc4x3_tc1::IfcDoorType(data);
            case 341: return new ::Ifc4x3_tc1::IfcDoorTypeEnum(data);
            case 342: return new ::Ifc4x3_tc1::IfcDoorTypeOperationEnum(data);
            case 343: return new ::Ifc4x3_tc1::IfcDoseEquivalentMeasure(data);
            case 344: return new ::Ifc4x3_tc1::IfcDraughtingPreDefinedColour(data);
            case 345: return new ::Ifc4x3_tc1::IfcDraughtingPreDefinedCurveFont(data);
            case 346: return new ::Ifc4x3_tc1::IfcDuctFitting(data);
            case 347: return new ::Ifc4x3_tc1::IfcDuctFittingType(data);
            case 348: return new ::Ifc4x3_tc1::IfcDuctFittingTypeEnum(data);
            case 349: return new ::Ifc4x3_tc1::IfcDuctSegment(data);
            case 350: return new ::Ifc4x3_tc1::IfcDuctSegmentType(data);
            case 351: return new ::Ifc4x3_tc1::IfcDuctSegmentTypeEnum(data);
            case 352: return new ::Ifc4x3_tc1::IfcDuctSilencer(data);
            case 353: return new ::Ifc4x3_tc1::IfcDuctSilencerType(data);
            case 354: return new ::Ifc4x3_tc1::IfcDuctSilencerTypeEnum(data);
            case 355: return new ::Ifc4x3_tc1::IfcDuration(data);
            case 356: return new ::Ifc4x3_tc1::IfcDynamicViscosityMeasure(data);
            case 357: return new ::Ifc4x3_tc1::IfcEarthworksCut(data);
            case 358: return new ::Ifc4x3_tc1::IfcEarthworksCutTypeEnum(data);
            case 359: return new ::Ifc4x3_tc1::IfcEarthworksElement(data);
            case 360: return new ::Ifc4x3_tc1::IfcEarthworksFill(data);
            case 361: return new ::Ifc4x3_tc1::IfcEarthworksFillTypeEnum(data);
            case 362: return new ::Ifc4x3_tc1::IfcEdge(data);
            case 363: return new ::Ifc4x3_tc1::IfcEdgeCurve(data);
            case 364: return new ::Ifc4x3_tc1::IfcEdgeLoop(data);
            case 365: return new ::Ifc4x3_tc1::IfcElectricAppliance(data);
            case 366: return new ::Ifc4x3_tc1::IfcElectricApplianceType(data);
            case 367: return new ::Ifc4x3_tc1::IfcElectricApplianceTypeEnum(data);
            case 368: return new ::Ifc4x3_tc1::IfcElectricCapacitanceMeasure(data);
            case 369: return new ::Ifc4x3_tc1::IfcElectricChargeMeasure(data);
            case 370: return new ::Ifc4x3_tc1::IfcElectricConductanceMeasure(data);
            case 371: return new ::Ifc4x3_tc1::IfcElectricCurrentMeasure(data);
            case 372: return new ::Ifc4x3_tc1::IfcElectricDistributionBoard(data);
            case 373: return new ::Ifc4x3_tc1::IfcElectricDistributionBoardType(data);
            case 374: return new ::Ifc4x3_tc1::IfcElectricDistributionBoardTypeEnum(data);
            case 375: return new ::Ifc4x3_tc1::IfcElectricFlowStorageDevice(data);
            case 376: return new ::Ifc4x3_tc1::IfcElectricFlowStorageDeviceType(data);
            case 377: return new ::Ifc4x3_tc1::IfcElectricFlowStorageDeviceTypeEnum(data);
            case 378: return new ::Ifc4x3_tc1::IfcElectricFlowTreatmentDevice(data);
            case 379: return new ::Ifc4x3_tc1::IfcElectricFlowTreatmentDeviceType(data);
            case 380: return new ::Ifc4x3_tc1::IfcElectricFlowTreatmentDeviceTypeEnum(data);
            case 381: return new ::Ifc4x3_tc1::IfcElectricGenerator(data);
            case 382: return new ::Ifc4x3_tc1::IfcElectricGeneratorType(data);
            case 383: return new ::Ifc4x3_tc1::IfcElectricGeneratorTypeEnum(data);
            case 384: return new ::Ifc4x3_tc1::IfcElectricMotor(data);
            case 385: return new ::Ifc4x3_tc1::IfcElectricMotorType(data);
            case 386: return new ::Ifc4x3_tc1::IfcElectricMotorTypeEnum(data);
            case 387: return new ::Ifc4x3_tc1::IfcElectricResistanceMeasure(data);
            case 388: return new ::Ifc4x3_tc1::IfcElectricTimeControl(data);
            case 389: return new ::Ifc4x3_tc1::IfcElectricTimeControlType(data);
            case 390: return new ::Ifc4x3_tc1::IfcElectricTimeControlTypeEnum(data);
            case 391: return new ::Ifc4x3_tc1::IfcElectricVoltageMeasure(data);
            case 392: return new ::Ifc4x3_tc1::IfcElement(data);
            case 393: return new ::Ifc4x3_tc1::IfcElementarySurface(data);
            case 394: return new ::Ifc4x3_tc1::IfcElementAssembly(data);
            case 395: return new ::Ifc4x3_tc1::IfcElementAssemblyType(data);
            case 396: return new ::Ifc4x3_tc1::IfcElementAssemblyTypeEnum(data);
            case 397: return new ::Ifc4x3_tc1::IfcElementComponent(data);
            case 398: return new ::Ifc4x3_tc1::IfcElementComponentType(data);
            case 399: return new ::Ifc4x3_tc1::IfcElementCompositionEnum(data);
            case 400: return new ::Ifc4x3_tc1::IfcElementQuantity(data);
            case 401: return new ::Ifc4x3_tc1::IfcElementType(data);
            case 402: return new ::Ifc4x3_tc1::IfcEllipse(data);
            case 403: return new ::Ifc4x3_tc1::IfcEllipseProfileDef(data);
            case 404: return new ::Ifc4x3_tc1::IfcEnergyConversionDevice(data);
            case 405: return new ::Ifc4x3_tc1::IfcEnergyConversionDeviceType(data);
            case 406: return new ::Ifc4x3_tc1::IfcEnergyMeasure(data);
            case 407: return new ::Ifc4x3_tc1::IfcEngine(data);
            case 408: return new ::Ifc4x3_tc1::IfcEngineType(data);
            case 409: return new ::Ifc4x3_tc1::IfcEngineTypeEnum(data);
            case 410: return new ::Ifc4x3_tc1::IfcEvaporativeCooler(data);
            case 411: return new ::Ifc4x3_tc1::IfcEvaporativeCoolerType(data);
            case 412: return new ::Ifc4x3_tc1::IfcEvaporativeCoolerTypeEnum(data);
            case 413: return new ::Ifc4x3_tc1::IfcEvaporator(data);
            case 414: return new ::Ifc4x3_tc1::IfcEvaporatorType(data);
            case 415: return new ::Ifc4x3_tc1::IfcEvaporatorTypeEnum(data);
            case 416: return new ::Ifc4x3_tc1::IfcEvent(data);
            case 417: return new ::Ifc4x3_tc1::IfcEventTime(data);
            case 418: return new ::Ifc4x3_tc1::IfcEventTriggerTypeEnum(data);
            case 419: return new ::Ifc4x3_tc1::IfcEventType(data);
            case 420: return new ::Ifc4x3_tc1::IfcEventTypeEnum(data);
            case 421: return new ::Ifc4x3_tc1::IfcExtendedProperties(data);
            case 422: return new ::Ifc4x3_tc1::IfcExternalInformation(data);
            case 423: return new ::Ifc4x3_tc1::IfcExternallyDefinedHatchStyle(data);
            case 424: return new ::Ifc4x3_tc1::IfcExternallyDefinedSurfaceStyle(data);
            case 425: return new ::Ifc4x3_tc1::IfcExternallyDefinedTextFont(data);
            case 426: return new ::Ifc4x3_tc1::IfcExternalReference(data);
            case 427: return new ::Ifc4x3_tc1::IfcExternalReferenceRelationship(data);
            case 428: return new ::Ifc4x3_tc1::IfcExternalSpatialElement(data);
            case 429: return new ::Ifc4x3_tc1::IfcExternalSpatialElementTypeEnum(data);
            case 430: return new ::Ifc4x3_tc1::IfcExternalSpatialStructureElement(data);
            case 431: return new ::Ifc4x3_tc1::IfcExtrudedAreaSolid(data);
            case 432: return new ::Ifc4x3_tc1::IfcExtrudedAreaSolidTapered(data);
            case 433: return new ::Ifc4x3_tc1::IfcFace(data);
            case 434: return new ::Ifc4x3_tc1::IfcFaceBasedSurfaceModel(data);
            case 435: return new ::Ifc4x3_tc1::IfcFaceBound(data);
            case 436: return new ::Ifc4x3_tc1::IfcFaceOuterBound(data);
            case 437: return new ::Ifc4x3_tc1::IfcFaceSurface(data);
            case 438: return new ::Ifc4x3_tc1::IfcFacetedBrep(data);
            case 439: return new ::Ifc4x3_tc1::IfcFacetedBrepWithVoids(data);
            case 440: return new ::Ifc4x3_tc1::IfcFacility(data);
            case 441: return new ::Ifc4x3_tc1::IfcFacilityPart(data);
            case 442: return new ::Ifc4x3_tc1::IfcFacilityPartCommon(data);
            case 443: return new ::Ifc4x3_tc1::IfcFacilityPartCommonTypeEnum(data);
            case 444: return new ::Ifc4x3_tc1::IfcFacilityUsageEnum(data);
            case 445: return new ::Ifc4x3_tc1::IfcFailureConnectionCondition(data);
            case 446: return new ::Ifc4x3_tc1::IfcFan(data);
            case 447: return new ::Ifc4x3_tc1::IfcFanType(data);
            case 448: return new ::Ifc4x3_tc1::IfcFanTypeEnum(data);
            case 449: return new ::Ifc4x3_tc1::IfcFastener(data);
            case 450: return new ::Ifc4x3_tc1::IfcFastenerType(data);
            case 451: return new ::Ifc4x3_tc1::IfcFastenerTypeEnum(data);
            case 452: return new ::Ifc4x3_tc1::IfcFeatureElement(data);
            case 453: return new ::Ifc4x3_tc1::IfcFeatureElementAddition(data);
            case 454: return new ::Ifc4x3_tc1::IfcFeatureElementSubtraction(data);
            case 455: return new ::Ifc4x3_tc1::IfcFillAreaStyle(data);
            case 456: return new ::Ifc4x3_tc1::IfcFillAreaStyleHatching(data);
            case 457: return new ::Ifc4x3_tc1::IfcFillAreaStyleTiles(data);
            case 459: return new ::Ifc4x3_tc1::IfcFilter(data);
            case 460: return new ::Ifc4x3_tc1::IfcFilterType(data);
            case 461: return new ::Ifc4x3_tc1::IfcFilterTypeEnum(data);
            case 462: return new ::Ifc4x3_tc1::IfcFireSuppressionTerminal(data);
            case 463: return new ::Ifc4x3_tc1::IfcFireSuppressionTerminalType(data);
            case 464: return new ::Ifc4x3_tc1::IfcFireSuppressionTerminalTypeEnum(data);
            case 465: return new ::Ifc4x3_tc1::IfcFixedReferenceSweptAreaSolid(data);
            case 466: return new ::Ifc4x3_tc1::IfcFlowController(data);
            case 467: return new ::Ifc4x3_tc1::IfcFlowControllerType(data);
            case 468: return new ::Ifc4x3_tc1::IfcFlowDirectionEnum(data);
            case 469: return new ::Ifc4x3_tc1::IfcFlowFitting(data);
            case 470: return new ::Ifc4x3_tc1::IfcFlowFittingType(data);
            case 471: return new ::Ifc4x3_tc1::IfcFlowInstrument(data);
            case 472: return new ::Ifc4x3_tc1::IfcFlowInstrumentType(data);
            case 473: return new ::Ifc4x3_tc1::IfcFlowInstrumentTypeEnum(data);
            case 474: return new ::Ifc4x3_tc1::IfcFlowMeter(data);
            case 475: return new ::Ifc4x3_tc1::IfcFlowMeterType(data);
            case 476: return new ::Ifc4x3_tc1::IfcFlowMeterTypeEnum(data);
            case 477: return new ::Ifc4x3_tc1::IfcFlowMovingDevice(data);
            case 478: return new ::Ifc4x3_tc1::IfcFlowMovingDeviceType(data);
            case 479: return new ::Ifc4x3_tc1::IfcFlowSegment(data);
            case 480: return new ::Ifc4x3_tc1::IfcFlowSegmentType(data);
            case 481: return new ::Ifc4x3_tc1::IfcFlowStorageDevice(data);
            case 482: return new ::Ifc4x3_tc1::IfcFlowStorageDeviceType(data);
            case 483: return new ::Ifc4x3_tc1::IfcFlowTerminal(data);
            case 484: return new ::Ifc4x3_tc1::IfcFlowTerminalType(data);
            case 485: return new ::Ifc4x3_tc1::IfcFlowTreatmentDevice(data);
            case 486: return new ::Ifc4x3_tc1::IfcFlowTreatmentDeviceType(data);
            case 487: return new ::Ifc4x3_tc1::IfcFontStyle(data);
            case 488: return new ::Ifc4x3_tc1::IfcFontVariant(data);
            case 489: return new ::Ifc4x3_tc1::IfcFontWeight(data);
            case 490: return new ::Ifc4x3_tc1::IfcFooting(data);
            case 491: return new ::Ifc4x3_tc1::IfcFootingType(data);
            case 492: return new ::Ifc4x3_tc1::IfcFootingTypeEnum(data);
            case 493: return new ::Ifc4x3_tc1::IfcForceMeasure(data);
            case 494: return new ::Ifc4x3_tc1::IfcFrequencyMeasure(data);
            case 495: return new ::Ifc4x3_tc1::IfcFurnishingElement(data);
            case 496: return new ::Ifc4x3_tc1::IfcFurnishingElementType(data);
            case 497: return new ::Ifc4x3_tc1::IfcFurniture(data);
            case 498: return new ::Ifc4x3_tc1::IfcFurnitureType(data);
            case 499: return new ::Ifc4x3_tc1::IfcFurnitureTypeEnum(data);
            case 500: return new ::Ifc4x3_tc1::IfcGeographicElement(data);
            case 501: return new ::Ifc4x3_tc1::IfcGeographicElementType(data);
            case 502: return new ::Ifc4x3_tc1::IfcGeographicElementTypeEnum(data);
            case 503: return new ::Ifc4x3_tc1::IfcGeometricCurveSet(data);
            case 504: return new ::Ifc4x3_tc1::IfcGeometricProjectionEnum(data);
            case 505: return new ::Ifc4x3_tc1::IfcGeometricRepresentationContext(data);
            case 506: return new ::Ifc4x3_tc1::IfcGeometricRepresentationItem(data);
            case 507: return new ::Ifc4x3_tc1::IfcGeometricRepresentationSubContext(data);
            case 508: return new ::Ifc4x3_tc1::IfcGeometricSet(data);
            case 510: return new ::Ifc4x3_tc1::IfcGeomodel(data);
            case 511: return new ::Ifc4x3_tc1::IfcGeoslice(data);
            case 512: return new ::Ifc4x3_tc1::IfcGeotechnicalAssembly(data);
            case 513: return new ::Ifc4x3_tc1::IfcGeotechnicalElement(data);
            case 514: return new ::Ifc4x3_tc1::IfcGeotechnicalStratum(data);
            case 515: return new ::Ifc4x3_tc1::IfcGeotechnicalStratumTypeEnum(data);
            case 516: return new ::Ifc4x3_tc1::IfcGloballyUniqueId(data);
            case 517: return new ::Ifc4x3_tc1::IfcGlobalOrLocalEnum(data);
            case 518: return new ::Ifc4x3_tc1::IfcGradientCurve(data);
            case 519: return new ::Ifc4x3_tc1::IfcGrid(data);
            case 520: return new ::Ifc4x3_tc1::IfcGridAxis(data);
            case 521: return new ::Ifc4x3_tc1::IfcGridPlacement(data);
            case 523: return new ::Ifc4x3_tc1::IfcGridTypeEnum(data);
            case 524: return new ::Ifc4x3_tc1::IfcGroup(data);
            case 525: return new ::Ifc4x3_tc1::IfcHalfSpaceSolid(data);
            case 527: return new ::Ifc4x3_tc1::IfcHeatExchanger(data);
            case 528: return new ::Ifc4x3_tc1::IfcHeatExchangerType(data);
            case 529: return new ::Ifc4x3_tc1::IfcHeatExchangerTypeEnum(data);
            case 530: return new ::Ifc4x3_tc1::IfcHeatFluxDensityMeasure(data);
            case 531: return new ::Ifc4x3_tc1::IfcHeatingValueMeasure(data);
            case 532: return new ::Ifc4x3_tc1::IfcHumidifier(data);
            case 533: return new ::Ifc4x3_tc1::IfcHumidifierType(data);
            case 534: return new ::Ifc4x3_tc1::IfcHumidifierTypeEnum(data);
            case 535: return new ::Ifc4x3_tc1::IfcIdentifier(data);
            case 536: return new ::Ifc4x3_tc1::IfcIlluminanceMeasure(data);
            case 537: return new ::Ifc4x3_tc1::IfcImageTexture(data);
            case 538: return new ::Ifc4x3_tc1::IfcImpactProtectionDevice(data);
            case 539: return new ::Ifc4x3_tc1::IfcImpactProtectionDeviceType(data);
            case 540: return new ::Ifc4x3_tc1::IfcImpactProtectionDeviceTypeEnum(data);
            case 541: return new ::Ifc4x3_tc1::IfcIndexedColourMap(data);
            case 542: return new ::Ifc4x3_tc1::IfcIndexedPolyCurve(data);
            case 543: return new ::Ifc4x3_tc1::IfcIndexedPolygonalFace(data);
            case 544: return new ::Ifc4x3_tc1::IfcIndexedPolygonalFaceWithVoids(data);
            case 545: return new ::Ifc4x3_tc1::IfcIndexedPolygonalTextureMap(data);
            case 546: return new ::Ifc4x3_tc1::IfcIndexedTextureMap(data);
            case 547: return new ::Ifc4x3_tc1::IfcIndexedTriangleTextureMap(data);
            case 548: return new ::Ifc4x3_tc1::IfcInductanceMeasure(data);
            case 549: return new ::Ifc4x3_tc1::IfcInteger(data);
            case 550: return new ::Ifc4x3_tc1::IfcIntegerCountRateMeasure(data);
            case 551: return new ::Ifc4x3_tc1::IfcInterceptor(data);
            case 552: return new ::Ifc4x3_tc1::IfcInterceptorType(data);
            case 553: return new ::Ifc4x3_tc1::IfcInterceptorTypeEnum(data);
            case 555: return new ::Ifc4x3_tc1::IfcInternalOrExternalEnum(data);
            case 556: return new ::Ifc4x3_tc1::IfcIntersectionCurve(data);
            case 557: return new ::Ifc4x3_tc1::IfcInventory(data);
            case 558: return new ::Ifc4x3_tc1::IfcInventoryTypeEnum(data);
            case 559: return new ::Ifc4x3_tc1::IfcIonConcentrationMeasure(data);
            case 560: return new ::Ifc4x3_tc1::IfcIrregularTimeSeries(data);
            case 561: return new ::Ifc4x3_tc1::IfcIrregularTimeSeriesValue(data);
            case 562: return new ::Ifc4x3_tc1::IfcIShapeProfileDef(data);
            case 563: return new ::Ifc4x3_tc1::IfcIsothermalMoistureCapacityMeasure(data);
            case 564: return new ::Ifc4x3_tc1::IfcJunctionBox(data);
            case 565: return new ::Ifc4x3_tc1::IfcJunctionBoxType(data);
            case 566: return new ::Ifc4x3_tc1::IfcJunctionBoxTypeEnum(data);
            case 567: return new ::Ifc4x3_tc1::IfcKerb(data);
            case 568: return new ::Ifc4x3_tc1::IfcKerbType(data);
            case 569: return new ::Ifc4x3_tc1::IfcKerbTypeEnum(data);
            case 570: return new ::Ifc4x3_tc1::IfcKinematicViscosityMeasure(data);
            case 571: return new ::Ifc4x3_tc1::IfcKnotType(data);
            case 572: return new ::Ifc4x3_tc1::IfcLabel(data);
            case 573: return new ::Ifc4x3_tc1::IfcLaborResource(data);
            case 574: return new ::Ifc4x3_tc1::IfcLaborResourceType(data);
            case 575: return new ::Ifc4x3_tc1::IfcLaborResourceTypeEnum(data);
            case 576: return new ::Ifc4x3_tc1::IfcLagTime(data);
            case 577: return new ::Ifc4x3_tc1::IfcLamp(data);
            case 578: return new ::Ifc4x3_tc1::IfcLampType(data);
            case 579: return new ::Ifc4x3_tc1::IfcLampTypeEnum(data);
            case 580: return new ::Ifc4x3_tc1::IfcLanguageId(data);
            case 582: return new ::Ifc4x3_tc1::IfcLayerSetDirectionEnum(data);
            case 583: return new ::Ifc4x3_tc1::IfcLengthMeasure(data);
            case 584: return new ::Ifc4x3_tc1::IfcLibraryInformation(data);
            case 585: return new ::Ifc4x3_tc1::IfcLibraryReference(data);
            case 587: return new ::Ifc4x3_tc1::IfcLightDistributionCurveEnum(data);
            case 588: return new ::Ifc4x3_tc1::IfcLightDistributionData(data);
            case 590: return new ::Ifc4x3_tc1::IfcLightEmissionSourceEnum(data);
            case 591: return new ::Ifc4x3_tc1::IfcLightFixture(data);
            case 592: return new ::Ifc4x3_tc1::IfcLightFixtureType(data);
            case 593: return new ::Ifc4x3_tc1::IfcLightFixtureTypeEnum(data);
            case 594: return new ::Ifc4x3_tc1::IfcLightIntensityDistribution(data);
            case 595: return new ::Ifc4x3_tc1::IfcLightSource(data);
            case 596: return new ::Ifc4x3_tc1::IfcLightSourceAmbient(data);
            case 597: return new ::Ifc4x3_tc1::IfcLightSourceDirectional(data);
            case 598: return new ::Ifc4x3_tc1::IfcLightSourceGoniometric(data);
            case 599: return new ::Ifc4x3_tc1::IfcLightSourcePositional(data);
            case 600: return new ::Ifc4x3_tc1::IfcLightSourceSpot(data);
            case 601: return new ::Ifc4x3_tc1::IfcLine(data);
            case 602: return new ::Ifc4x3_tc1::IfcLinearElement(data);
            case 603: return new ::Ifc4x3_tc1::IfcLinearForceMeasure(data);
            case 604: return new ::Ifc4x3_tc1::IfcLinearMomentMeasure(data);
            case 605: return new ::Ifc4x3_tc1::IfcLinearPlacement(data);
            case 606: return new ::Ifc4x3_tc1::IfcLinearPositioningElement(data);
            case 607: return new ::Ifc4x3_tc1::IfcLinearStiffnessMeasure(data);
            case 608: return new ::Ifc4x3_tc1::IfcLinearVelocityMeasure(data);
            case 609: return new ::Ifc4x3_tc1::IfcLineIndex(data);
            case 610: return new ::Ifc4x3_tc1::IfcLiquidTerminal(data);
            case 611: return new ::Ifc4x3_tc1::IfcLiquidTerminalType(data);
            case 612: return new ::Ifc4x3_tc1::IfcLiquidTerminalTypeEnum(data);
            case 613: return new ::Ifc4x3_tc1::IfcLoadGroupTypeEnum(data);
            case 614: return new ::Ifc4x3_tc1::IfcLocalPlacement(data);
            case 615: return new ::Ifc4x3_tc1::IfcLogical(data);
            case 616: return new ::Ifc4x3_tc1::IfcLogicalOperatorEnum(data);
            case 617: return new ::Ifc4x3_tc1::IfcLoop(data);
            case 618: return new ::Ifc4x3_tc1::IfcLShapeProfileDef(data);
            case 619: return new ::Ifc4x3_tc1::IfcLuminousFluxMeasure(data);
            case 620: return new ::Ifc4x3_tc1::IfcLuminousIntensityDistributionMeasure(data);
            case 621: return new ::Ifc4x3_tc1::IfcLuminousIntensityMeasure(data);
            case 622: return new ::Ifc4x3_tc1::IfcMagneticFluxDensityMeasure(data);
            case 623: return new ::Ifc4x3_tc1::IfcMagneticFluxMeasure(data);
            case 624: return new ::Ifc4x3_tc1::IfcManifoldSolidBrep(data);
            case 625: return new ::Ifc4x3_tc1::IfcMapConversion(data);
            case 626: return new ::Ifc4x3_tc1::IfcMappedItem(data);
            case 627: return new ::Ifc4x3_tc1::IfcMarineFacility(data);
            case 628: return new ::Ifc4x3_tc1::IfcMarineFacilityTypeEnum(data);
            case 629: return new ::Ifc4x3_tc1::IfcMarinePart(data);
            case 630: return new ::Ifc4x3_tc1::IfcMarinePartTypeEnum(data);
            case 631: return new ::Ifc4x3_tc1::IfcMassDensityMeasure(data);
            case 632: return new ::Ifc4x3_tc1::IfcMassFlowRateMeasure(data);
            case 633: return new ::Ifc4x3_tc1::IfcMassMeasure(data);
            case 634: return new ::Ifc4x3_tc1::IfcMassPerLengthMeasure(data);
            case 635: return new ::Ifc4x3_tc1::IfcMaterial(data);
            case 636: return new ::Ifc4x3_tc1::IfcMaterialClassificationRelationship(data);
            case 637: return new ::Ifc4x3_tc1::IfcMaterialConstituent(data);
            case 638: return new ::Ifc4x3_tc1::IfcMaterialConstituentSet(data);
            case 639: return new ::Ifc4x3_tc1::IfcMaterialDefinition(data);
            case 640: return new ::Ifc4x3_tc1::IfcMaterialDefinitionRepresentation(data);
            case 641: return new ::Ifc4x3_tc1::IfcMaterialLayer(data);
            case 642: return new ::Ifc4x3_tc1::IfcMaterialLayerSet(data);
            case 643: return new ::Ifc4x3_tc1::IfcMaterialLayerSetUsage(data);
            case 644: return new ::Ifc4x3_tc1::IfcMaterialLayerWithOffsets(data);
            case 645: return new ::Ifc4x3_tc1::IfcMaterialList(data);
            case 646: return new ::Ifc4x3_tc1::IfcMaterialProfile(data);
            case 647: return new ::Ifc4x3_tc1::IfcMaterialProfileSet(data);
            case 648: return new ::Ifc4x3_tc1::IfcMaterialProfileSetUsage(data);
            case 649: return new ::Ifc4x3_tc1::IfcMaterialProfileSetUsageTapering(data);
            case 650: return new ::Ifc4x3_tc1::IfcMaterialProfileWithOffsets(data);
            case 651: return new ::Ifc4x3_tc1::IfcMaterialProperties(data);
            case 652: return new ::Ifc4x3_tc1::IfcMaterialRelationship(data);
            case 654: return new ::Ifc4x3_tc1::IfcMaterialUsageDefinition(data);
            case 656: return new ::Ifc4x3_tc1::IfcMeasureWithUnit(data);
            case 657: return new ::Ifc4x3_tc1::IfcMechanicalFastener(data);
            case 658: return new ::Ifc4x3_tc1::IfcMechanicalFastenerType(data);
            case 659: return new ::Ifc4x3_tc1::IfcMechanicalFastenerTypeEnum(data);
            case 660: return new ::Ifc4x3_tc1::IfcMedicalDevice(data);
            case 661: return new ::Ifc4x3_tc1::IfcMedicalDeviceType(data);
            case 662: return new ::Ifc4x3_tc1::IfcMedicalDeviceTypeEnum(data);
            case 663: return new ::Ifc4x3_tc1::IfcMember(data);
            case 664: return new ::Ifc4x3_tc1::IfcMemberType(data);
            case 665: return new ::Ifc4x3_tc1::IfcMemberTypeEnum(data);
            case 666: return new ::Ifc4x3_tc1::IfcMetric(data);
            case 668: return new ::Ifc4x3_tc1::IfcMirroredProfileDef(data);
            case 669: return new ::Ifc4x3_tc1::IfcMobileTelecommunicationsAppliance(data);
            case 670: return new ::Ifc4x3_tc1::IfcMobileTelecommunicationsApplianceType(data);
            case 671: return new ::Ifc4x3_tc1::IfcMobileTelecommunicationsApplianceTypeEnum(data);
            case 672: return new ::Ifc4x3_tc1::IfcModulusOfElasticityMeasure(data);
            case 673: return new ::Ifc4x3_tc1::IfcModulusOfLinearSubgradeReactionMeasure(data);
            case 674: return new ::Ifc4x3_tc1::IfcModulusOfRotationalSubgradeReactionMeasure(data);
            case 676: return new ::Ifc4x3_tc1::IfcModulusOfSubgradeReactionMeasure(data);
            case 679: return new ::Ifc4x3_tc1::IfcMoistureDiffusivityMeasure(data);
            case 680: return new ::Ifc4x3_tc1::IfcMolecularWeightMeasure(data);
            case 681: return new ::Ifc4x3_tc1::IfcMomentOfInertiaMeasure(data);
            case 682: return new ::Ifc4x3_tc1::IfcMonetaryMeasure(data);
            case 683: return new ::Ifc4x3_tc1::IfcMonetaryUnit(data);
            case 684: return new ::Ifc4x3_tc1::IfcMonthInYearNumber(data);
            case 685: return new ::Ifc4x3_tc1::IfcMooringDevice(data);
            case 686: return new ::Ifc4x3_tc1::IfcMooringDeviceType(data);
            case 687: return new ::Ifc4x3_tc1::IfcMooringDeviceTypeEnum(data);
            case 688: return new ::Ifc4x3_tc1::IfcMotorConnection(data);
            case 689: return new ::Ifc4x3_tc1::IfcMotorConnectionType(data);
            case 690: return new ::Ifc4x3_tc1::IfcMotorConnectionTypeEnum(data);
            case 691: return new ::Ifc4x3_tc1::IfcNamedUnit(data);
            case 692: return new ::Ifc4x3_tc1::IfcNavigationElement(data);
            case 693: return new ::Ifc4x3_tc1::IfcNavigationElementType(data);
            case 694: return new ::Ifc4x3_tc1::IfcNavigationElementTypeEnum(data);
            case 695: return new ::Ifc4x3_tc1::IfcNonNegativeLengthMeasure(data);
            case 696: return new ::Ifc4x3_tc1::IfcNormalisedRatioMeasure(data);
            case 697: return new ::Ifc4x3_tc1::IfcNumericMeasure(data);
            case 698: return new ::Ifc4x3_tc1::IfcObject(data);
            case 699: return new ::Ifc4x3_tc1::IfcObjectDefinition(data);
            case 700: return new ::Ifc4x3_tc1::IfcObjective(data);
            case 701: return new ::Ifc4x3_tc1::IfcObjectiveEnum(data);
            case 702: return new ::Ifc4x3_tc1::IfcObjectPlacement(data);
            case 704: return new ::Ifc4x3_tc1::IfcOccupant(data);
            case 705: return new ::Ifc4x3_tc1::IfcOccupantTypeEnum(data);
            case 706: return new ::Ifc4x3_tc1::IfcOffsetCurve(data);
            case 707: return new ::Ifc4x3_tc1::IfcOffsetCurve2D(data);
            case 708: return new ::Ifc4x3_tc1::IfcOffsetCurve3D(data);
            case 709: return new ::Ifc4x3_tc1::IfcOffsetCurveByDistances(data);
            case 710: return new ::Ifc4x3_tc1::IfcOpenCrossProfileDef(data);
            case 711: return new ::Ifc4x3_tc1::IfcOpeningElement(data);
            case 712: return new ::Ifc4x3_tc1::IfcOpeningElementTypeEnum(data);
            case 713: return new ::Ifc4x3_tc1::IfcOpenShell(data);
            case 714: return new ::Ifc4x3_tc1::IfcOrganization(data);
            case 715: return new ::Ifc4x3_tc1::IfcOrganizationRelationship(data);
            case 716: return new ::Ifc4x3_tc1::IfcOrientedEdge(data);
            case 717: return new ::Ifc4x3_tc1::IfcOuterBoundaryCurve(data);
            case 718: return new ::Ifc4x3_tc1::IfcOutlet(data);
            case 719: return new ::Ifc4x3_tc1::IfcOutletType(data);
            case 720: return new ::Ifc4x3_tc1::IfcOutletTypeEnum(data);
            case 721: return new ::Ifc4x3_tc1::IfcOwnerHistory(data);
            case 722: return new ::Ifc4x3_tc1::IfcParameterizedProfileDef(data);
            case 723: return new ::Ifc4x3_tc1::IfcParameterValue(data);
            case 724: return new ::Ifc4x3_tc1::IfcPath(data);
            case 725: return new ::Ifc4x3_tc1::IfcPavement(data);
            case 726: return new ::Ifc4x3_tc1::IfcPavementType(data);
            case 727: return new ::Ifc4x3_tc1::IfcPavementTypeEnum(data);
            case 728: return new ::Ifc4x3_tc1::IfcPcurve(data);
            case 729: return new ::Ifc4x3_tc1::IfcPerformanceHistory(data);
            case 730: return new ::Ifc4x3_tc1::IfcPerformanceHistoryTypeEnum(data);
            case 731: return new ::Ifc4x3_tc1::IfcPermeableCoveringOperationEnum(data);
            case 732: return new ::Ifc4x3_tc1::IfcPermeableCoveringProperties(data);
            case 733: return new ::Ifc4x3_tc1::IfcPermit(data);
            case 734: return new ::Ifc4x3_tc1::IfcPermitTypeEnum(data);
            case 735: return new ::Ifc4x3_tc1::IfcPerson(data);
            case 736: return new ::Ifc4x3_tc1::IfcPersonAndOrganization(data);
            case 737: return new ::Ifc4x3_tc1::IfcPHMeasure(data);
            case 738: return new ::Ifc4x3_tc1::IfcPhysicalComplexQuantity(data);
            case 739: return new ::Ifc4x3_tc1::IfcPhysicalOrVirtualEnum(data);
            case 740: return new ::Ifc4x3_tc1::IfcPhysicalQuantity(data);
            case 741: return new ::Ifc4x3_tc1::IfcPhysicalSimpleQuantity(data);
            case 742: return new ::Ifc4x3_tc1::IfcPile(data);
            case 743: return new ::Ifc4x3_tc1::IfcPileConstructionEnum(data);
            case 744: return new ::Ifc4x3_tc1::IfcPileType(data);
            case 745: return new ::Ifc4x3_tc1::IfcPileTypeEnum(data);
            case 746: return new ::Ifc4x3_tc1::IfcPipeFitting(data);
            case 747: return new ::Ifc4x3_tc1::IfcPipeFittingType(data);
            case 748: return new ::Ifc4x3_tc1::IfcPipeFittingTypeEnum(data);
            case 749: return new ::Ifc4x3_tc1::IfcPipeSegment(data);
            case 750: return new ::Ifc4x3_tc1::IfcPipeSegmentType(data);
            case 751: return new ::Ifc4x3_tc1::IfcPipeSegmentTypeEnum(data);
            case 752: return new ::Ifc4x3_tc1::IfcPixelTexture(data);
            case 753: return new ::Ifc4x3_tc1::IfcPlacement(data);
            case 754: return new ::Ifc4x3_tc1::IfcPlanarBox(data);
            case 755: return new ::Ifc4x3_tc1::IfcPlanarExtent(data);
            case 756: return new ::Ifc4x3_tc1::IfcPlanarForceMeasure(data);
            case 757: return new ::Ifc4x3_tc1::IfcPlane(data);
            case 758: return new ::Ifc4x3_tc1::IfcPlaneAngleMeasure(data);
            case 759: return new ::Ifc4x3_tc1::IfcPlate(data);
            case 760: return new ::Ifc4x3_tc1::IfcPlateType(data);
            case 761: return new ::Ifc4x3_tc1::IfcPlateTypeEnum(data);
            case 762: return new ::Ifc4x3_tc1::IfcPoint(data);
            case 763: return new ::Ifc4x3_tc1::IfcPointByDistanceExpression(data);
            case 764: return new ::Ifc4x3_tc1::IfcPointOnCurve(data);
            case 765: return new ::Ifc4x3_tc1::IfcPointOnSurface(data);
            case 767: return new ::Ifc4x3_tc1::IfcPolygonalBoundedHalfSpace(data);
            case 768: return new ::Ifc4x3_tc1::IfcPolygonalFaceSet(data);
            case 769: return new ::Ifc4x3_tc1::IfcPolyline(data);
            case 770: return new ::Ifc4x3_tc1::IfcPolyLoop(data);
            case 771: return new ::Ifc4x3_tc1::IfcPolynomialCurve(data);
            case 772: return new ::Ifc4x3_tc1::IfcPort(data);
            case 773: return new ::Ifc4x3_tc1::IfcPositioningElement(data);
            case 774: return new ::Ifc4x3_tc1::IfcPositiveInteger(data);
            case 775: return new ::Ifc4x3_tc1::IfcPositiveLengthMeasure(data);
            case 776: return new ::Ifc4x3_tc1::IfcPositivePlaneAngleMeasure(data);
            case 777: return new ::Ifc4x3_tc1::IfcPositiveRatioMeasure(data);
            case 778: return new ::Ifc4x3_tc1::IfcPostalAddress(data);
            case 779: return new ::Ifc4x3_tc1::IfcPowerMeasure(data);
            case 780: return new ::Ifc4x3_tc1::IfcPreDefinedColour(data);
            case 781: return new ::Ifc4x3_tc1::IfcPreDefinedCurveFont(data);
            case 782: return new ::Ifc4x3_tc1::IfcPreDefinedItem(data);
            case 783: return new ::Ifc4x3_tc1::IfcPreDefinedProperties(data);
            case 784: return new ::Ifc4x3_tc1::IfcPreDefinedPropertySet(data);
            case 785: return new ::Ifc4x3_tc1::IfcPreDefinedTextFont(data);
            case 786: return new ::Ifc4x3_tc1::IfcPreferredSurfaceCurveRepresentation(data);
            case 787: return new ::Ifc4x3_tc1::IfcPresentableText(data);
            case 788: return new ::Ifc4x3_tc1::IfcPresentationItem(data);
            case 789: return new ::Ifc4x3_tc1::IfcPresentationLayerAssignment(data);
            case 790: return new ::Ifc4x3_tc1::IfcPresentationLayerWithStyle(data);
            case 791: return new ::Ifc4x3_tc1::IfcPresentationStyle(data);
            case 792: return new ::Ifc4x3_tc1::IfcPressureMeasure(data);
            case 793: return new ::Ifc4x3_tc1::IfcProcedure(data);
            case 794: return new ::Ifc4x3_tc1::IfcProcedureType(data);
            case 795: return new ::Ifc4x3_tc1::IfcProcedureTypeEnum(data);
            case 796: return new ::Ifc4x3_tc1::IfcProcess(data);
            case 798: return new ::Ifc4x3_tc1::IfcProduct(data);
            case 799: return new ::Ifc4x3_tc1::IfcProductDefinitionShape(data);
            case 800: return new ::Ifc4x3_tc1::IfcProductRepresentation(data);
            case 803: return new ::Ifc4x3_tc1::IfcProfileDef(data);
            case 804: return new ::Ifc4x3_tc1::IfcProfileProperties(data);
            case 805: return new ::Ifc4x3_tc1::IfcProfileTypeEnum(data);
            case 806: return new ::Ifc4x3_tc1::IfcProject(data);
            case 807: return new ::Ifc4x3_tc1::IfcProjectedCRS(data);
            case 808: return new ::Ifc4x3_tc1::IfcProjectedOrTrueLengthEnum(data);
            case 809: return new ::Ifc4x3_tc1::IfcProjectionElement(data);
            case 810: return new ::Ifc4x3_tc1::IfcProjectionElementTypeEnum(data);
            case 811: return new ::Ifc4x3_tc1::IfcProjectLibrary(data);
            case 812: return new ::Ifc4x3_tc1::IfcProjectOrder(data);
            case 813: return new ::Ifc4x3_tc1::IfcProjectOrderTypeEnum(data);
            case 814: return new ::Ifc4x3_tc1::IfcProperty(data);
            case 815: return new ::Ifc4x3_tc1::IfcPropertyAbstraction(data);
            case 816: return new ::Ifc4x3_tc1::IfcPropertyBoundedValue(data);
            case 817: return new ::Ifc4x3_tc1::IfcPropertyDefinition(data);
            case 818: return new ::Ifc4x3_tc1::IfcPropertyDependencyRelationship(data);
            case 819: return new ::Ifc4x3_tc1::IfcPropertyEnumeratedValue(data);
            case 820: return new ::Ifc4x3_tc1::IfcPropertyEnumeration(data);
            case 821: return new ::Ifc4x3_tc1::IfcPropertyListValue(data);
            case 822: return new ::Ifc4x3_tc1::IfcPropertyReferenceValue(data);
            case 823: return new ::Ifc4x3_tc1::IfcPropertySet(data);
            case 824: return new ::Ifc4x3_tc1::IfcPropertySetDefinition(data);
            case 826: return new ::Ifc4x3_tc1::IfcPropertySetDefinitionSet(data);
            case 827: return new ::Ifc4x3_tc1::IfcPropertySetTemplate(data);
            case 828: return new ::Ifc4x3_tc1::IfcPropertySetTemplateTypeEnum(data);
            case 829: return new ::Ifc4x3_tc1::IfcPropertySingleValue(data);
            case 830: return new ::Ifc4x3_tc1::IfcPropertyTableValue(data);
            case 831: return new ::Ifc4x3_tc1::IfcPropertyTemplate(data);
            case 832: return new ::Ifc4x3_tc1::IfcPropertyTemplateDefinition(data);
            case 833: return new ::Ifc4x3_tc1::IfcProtectiveDevice(data);
            case 834: return new ::Ifc4x3_tc1::IfcProtectiveDeviceTrippingUnit(data);
            case 835: return new ::Ifc4x3_tc1::IfcProtectiveDeviceTrippingUnitType(data);
            case 836: return new ::Ifc4x3_tc1::IfcProtectiveDeviceTrippingUnitTypeEnum(data);
            case 837: return new ::Ifc4x3_tc1::IfcProtectiveDeviceType(data);
            case 838: return new ::Ifc4x3_tc1::IfcProtectiveDeviceTypeEnum(data);
            case 839: return new ::Ifc4x3_tc1::IfcPump(data);
            case 840: return new ::Ifc4x3_tc1::IfcPumpType(data);
            case 841: return new ::Ifc4x3_tc1::IfcPumpTypeEnum(data);
            case 842: return new ::Ifc4x3_tc1::IfcQuantityArea(data);
            case 843: return new ::Ifc4x3_tc1::IfcQuantityCount(data);
            case 844: return new ::Ifc4x3_tc1::IfcQuantityLength(data);
            case 845: return new ::Ifc4x3_tc1::IfcQuantityNumber(data);
            case 846: return new ::Ifc4x3_tc1::IfcQuantitySet(data);
            case 847: return new ::Ifc4x3_tc1::IfcQuantityTime(data);
            case 848: return new ::Ifc4x3_tc1::IfcQuantityVolume(data);
            case 849: return new ::Ifc4x3_tc1::IfcQuantityWeight(data);
            case 850: return new ::Ifc4x3_tc1::IfcRadioActivityMeasure(data);
            case 851: return new ::Ifc4x3_tc1::IfcRail(data);
            case 852: return new ::Ifc4x3_tc1::IfcRailing(data);
            case 853: return new ::Ifc4x3_tc1::IfcRailingType(data);
            case 854: return new ::Ifc4x3_tc1::IfcRailingTypeEnum(data);
            case 855: return new ::Ifc4x3_tc1::IfcRailType(data);
            case 856: return new ::Ifc4x3_tc1::IfcRailTypeEnum(data);
            case 857: return new ::Ifc4x3_tc1::IfcRailway(data);
            case 858: return new ::Ifc4x3_tc1::IfcRailwayPart(data);
            case 859: return new ::Ifc4x3_tc1::IfcRailwayPartTypeEnum(data);
            case 860: return new ::Ifc4x3_tc1::IfcRailwayTypeEnum(data);
            case 861: return new ::Ifc4x3_tc1::IfcRamp(data);
            case 862: return new ::Ifc4x3_tc1::IfcRampFlight(data);
            case 863: return new ::Ifc4x3_tc1::IfcRampFlightType(data);
            case 864: return new ::Ifc4x3_tc1::IfcRampFlightTypeEnum(data);
            case 865: return new ::Ifc4x3_tc1::IfcRampType(data);
            case 866: return new ::Ifc4x3_tc1::IfcRampTypeEnum(data);
            case 867: return new ::Ifc4x3_tc1::IfcRatioMeasure(data);
            case 868: return new ::Ifc4x3_tc1::IfcRationalBSplineCurveWithKnots(data);
            case 869: return new ::Ifc4x3_tc1::IfcRationalBSplineSurfaceWithKnots(data);
            case 870: return new ::Ifc4x3_tc1::IfcReal(data);
            case 871: return new ::Ifc4x3_tc1::IfcRectangleHollowProfileDef(data);
            case 872: return new ::Ifc4x3_tc1::IfcRectangleProfileDef(data);
            case 873: return new ::Ifc4x3_tc1::IfcRectangularPyramid(data);
            case 874: return new ::Ifc4x3_tc1::IfcRectangularTrimmedSurface(data);
            case 875: return new ::Ifc4x3_tc1::IfcRecurrencePattern(data);
            case 876: return new ::Ifc4x3_tc1::IfcRecurrenceTypeEnum(data);
            case 877: return new ::Ifc4x3_tc1::IfcReference(data);
            case 878: return new ::Ifc4x3_tc1::IfcReferent(data);
            case 879: return new ::Ifc4x3_tc1::IfcReferentTypeEnum(data);
            case 880: return new ::Ifc4x3_tc1::IfcReflectanceMethodEnum(data);
            case 881: return new ::Ifc4x3_tc1::IfcRegularTimeSeries(data);
            case 882: return new ::Ifc4x3_tc1::IfcReinforcedSoil(data);
            case 883: return new ::Ifc4x3_tc1::IfcReinforcedSoilTypeEnum(data);
            case 884: return new ::Ifc4x3_tc1::IfcReinforcementBarProperties(data);
            case 885: return new ::Ifc4x3_tc1::IfcReinforcementDefinitionProperties(data);
            case 886: return new ::Ifc4x3_tc1::IfcReinforcingBar(data);
            case 887: return new ::Ifc4x3_tc1::IfcReinforcingBarRoleEnum(data);
            case 888: return new ::Ifc4x3_tc1::IfcReinforcingBarSurfaceEnum(data);
            case 889: return new ::Ifc4x3_tc1::IfcReinforcingBarType(data);
            case 890: return new ::Ifc4x3_tc1::IfcReinforcingBarTypeEnum(data);
            case 891: return new ::Ifc4x3_tc1::IfcReinforcingElement(data);
            case 892: return new ::Ifc4x3_tc1::IfcReinforcingElementType(data);
            case 893: return new ::Ifc4x3_tc1::IfcReinforcingMesh(data);
            case 894: return new ::Ifc4x3_tc1::IfcReinforcingMeshType(data);
            case 895: return new ::Ifc4x3_tc1::IfcReinforcingMeshTypeEnum(data);
            case 896: return new ::Ifc4x3_tc1::IfcRelAdheresToElement(data);
            case 897: return new ::Ifc4x3_tc1::IfcRelAggregates(data);
            case 898: return new ::Ifc4x3_tc1::IfcRelAssigns(data);
            case 899: return new ::Ifc4x3_tc1::IfcRelAssignsToActor(data);
            case 900: return new ::Ifc4x3_tc1::IfcRelAssignsToControl(data);
            case 901: return new ::Ifc4x3_tc1::IfcRelAssignsToGroup(data);
            case 902: return new ::Ifc4x3_tc1::IfcRelAssignsToGroupByFactor(data);
            case 903: return new ::Ifc4x3_tc1::IfcRelAssignsToProcess(data);
            case 904: return new ::Ifc4x3_tc1::IfcRelAssignsToProduct(data);
            case 905: return new ::Ifc4x3_tc1::IfcRelAssignsToResource(data);
            case 906: return new ::Ifc4x3_tc1::IfcRelAssociates(data);
            case 907: return new ::Ifc4x3_tc1::IfcRelAssociatesApproval(data);
            case 908: return new ::Ifc4x3_tc1::IfcRelAssociatesClassification(data);
            case 909: return new ::Ifc4x3_tc1::IfcRelAssociatesConstraint(data);
            case 910: return new ::Ifc4x3_tc1::IfcRelAssociatesDocument(data);
            case 911: return new ::Ifc4x3_tc1::IfcRelAssociatesLibrary(data);
            case 912: return new ::Ifc4x3_tc1::IfcRelAssociatesMaterial(data);
            case 913: return new ::Ifc4x3_tc1::IfcRelAssociatesProfileDef(data);
            case 914: return new ::Ifc4x3_tc1::IfcRelationship(data);
            case 915: return new ::Ifc4x3_tc1::IfcRelConnects(data);
            case 916: return new ::Ifc4x3_tc1::IfcRelConnectsElements(data);
            case 917: return new ::Ifc4x3_tc1::IfcRelConnectsPathElements(data);
            case 918: return new ::Ifc4x3_tc1::IfcRelConnectsPorts(data);
            case 919: return new ::Ifc4x3_tc1::IfcRelConnectsPortToElement(data);
            case 920: return new ::Ifc4x3_tc1::IfcRelConnectsStructuralActivity(data);
            case 921: return new ::Ifc4x3_tc1::IfcRelConnectsStructuralMember(data);
            case 922: return new ::Ifc4x3_tc1::IfcRelConnectsWithEccentricity(data);
            case 923: return new ::Ifc4x3_tc1::IfcRelConnectsWithRealizingElements(data);
            case 924: return new ::Ifc4x3_tc1::IfcRelContainedInSpatialStructure(data);
            case 925: return new ::Ifc4x3_tc1::IfcRelCoversBldgElements(data);
            case 926: return new ::Ifc4x3_tc1::IfcRelCoversSpaces(data);
            case 927: return new ::Ifc4x3_tc1::IfcRelDeclares(data);
            case 928: return new ::Ifc4x3_tc1::IfcRelDecomposes(data);
            case 929: return new ::Ifc4x3_tc1::IfcRelDefines(data);
            case 930: return new ::Ifc4x3_tc1::IfcRelDefinesByObject(data);
            case 931: return new ::Ifc4x3_tc1::IfcRelDefinesByProperties(data);
            case 932: return new ::Ifc4x3_tc1::IfcRelDefinesByTemplate(data);
            case 933: return new ::Ifc4x3_tc1::IfcRelDefinesByType(data);
            case 934: return new ::Ifc4x3_tc1::IfcRelFillsElement(data);
            case 935: return new ::Ifc4x3_tc1::IfcRelFlowControlElements(data);
            case 936: return new ::Ifc4x3_tc1::IfcRelInterferesElements(data);
            case 937: return new ::Ifc4x3_tc1::IfcRelNests(data);
            case 938: return new ::Ifc4x3_tc1::IfcRelPositions(data);
            case 939: return new ::Ifc4x3_tc1::IfcRelProjectsElement(data);
            case 940: return new ::Ifc4x3_tc1::IfcRelReferencedInSpatialStructure(data);
            case 941: return new ::Ifc4x3_tc1::IfcRelSequence(data);
            case 942: return new ::Ifc4x3_tc1::IfcRelServicesBuildings(data);
            case 943: return new ::Ifc4x3_tc1::IfcRelSpaceBoundary(data);
            case 944: return new ::Ifc4x3_tc1::IfcRelSpaceBoundary1stLevel(data);
            case 945: return new ::Ifc4x3_tc1::IfcRelSpaceBoundary2ndLevel(data);
            case 946: return new ::Ifc4x3_tc1::IfcRelVoidsElement(data);
            case 947: return new ::Ifc4x3_tc1::IfcReparametrisedCompositeCurveSegment(data);
            case 948: return new ::Ifc4x3_tc1::IfcRepresentation(data);
            case 949: return new ::Ifc4x3_tc1::IfcRepresentationContext(data);
            case 950: return new ::Ifc4x3_tc1::IfcRepresentationItem(data);
            case 951: return new ::Ifc4x3_tc1::IfcRepresentationMap(data);
            case 952: return new ::Ifc4x3_tc1::IfcResource(data);
            case 953: return new ::Ifc4x3_tc1::IfcResourceApprovalRelationship(data);
            case 954: return new ::Ifc4x3_tc1::IfcResourceConstraintRelationship(data);
            case 955: return new ::Ifc4x3_tc1::IfcResourceLevelRelationship(data);
            case 958: return new ::Ifc4x3_tc1::IfcResourceTime(data);
            case 959: return new ::Ifc4x3_tc1::IfcRevolvedAreaSolid(data);
            case 960: return new ::Ifc4x3_tc1::IfcRevolvedAreaSolidTapered(data);
            case 961: return new ::Ifc4x3_tc1::IfcRightCircularCone(data);
            case 962: return new ::Ifc4x3_tc1::IfcRightCircularCylinder(data);
            case 963: return new ::Ifc4x3_tc1::IfcRoad(data);
            case 964: return new ::Ifc4x3_tc1::IfcRoadPart(data);
            case 965: return new ::Ifc4x3_tc1::IfcRoadPartTypeEnum(data);
            case 966: return new ::Ifc4x3_tc1::IfcRoadTypeEnum(data);
            case 967: return new ::Ifc4x3_tc1::IfcRoleEnum(data);
            case 968: return new ::Ifc4x3_tc1::IfcRoof(data);
            case 969: return new ::Ifc4x3_tc1::IfcRoofType(data);
            case 970: return new ::Ifc4x3_tc1::IfcRoofTypeEnum(data);
            case 971: return new ::Ifc4x3_tc1::IfcRoot(data);
            case 972: return new ::Ifc4x3_tc1::IfcRotationalFrequencyMeasure(data);
            case 973: return new ::Ifc4x3_tc1::IfcRotationalMassMeasure(data);
            case 974: return new ::Ifc4x3_tc1::IfcRotationalStiffnessMeasure(data);
            case 976: return new ::Ifc4x3_tc1::IfcRoundedRectangleProfileDef(data);
            case 977: return new ::Ifc4x3_tc1::IfcSanitaryTerminal(data);
            case 978: return new ::Ifc4x3_tc1::IfcSanitaryTerminalType(data);
            case 979: return new ::Ifc4x3_tc1::IfcSanitaryTerminalTypeEnum(data);
            case 980: return new ::Ifc4x3_tc1::IfcSchedulingTime(data);
            case 981: return new ::Ifc4x3_tc1::IfcSeamCurve(data);
            case 982: return new ::Ifc4x3_tc1::IfcSecondOrderPolynomialSpiral(data);
            case 983: return new ::Ifc4x3_tc1::IfcSectionalAreaIntegralMeasure(data);
            case 984: return new ::Ifc4x3_tc1::IfcSectionedSolid(data);
            case 985: return new ::Ifc4x3_tc1::IfcSectionedSolidHorizontal(data);
            case 986: return new ::Ifc4x3_tc1::IfcSectionedSpine(data);
            case 987: return new ::Ifc4x3_tc1::IfcSectionedSurface(data);
            case 988: return new ::Ifc4x3_tc1::IfcSectionModulusMeasure(data);
            case 989: return new ::Ifc4x3_tc1::IfcSectionProperties(data);
            case 990: return new ::Ifc4x3_tc1::IfcSectionReinforcementProperties(data);
            case 991: return new ::Ifc4x3_tc1::IfcSectionTypeEnum(data);
            case 992: return new ::Ifc4x3_tc1::IfcSegment(data);
            case 993: return new ::Ifc4x3_tc1::IfcSegmentedReferenceCurve(data);
            case 995: return new ::Ifc4x3_tc1::IfcSensor(data);
            case 996: return new ::Ifc4x3_tc1::IfcSensorType(data);
            case 997: return new ::Ifc4x3_tc1::IfcSensorTypeEnum(data);
            case 998: return new ::Ifc4x3_tc1::IfcSequenceEnum(data);
            case 999: return new ::Ifc4x3_tc1::IfcSeventhOrderPolynomialSpiral(data);
            case 1000: return new ::Ifc4x3_tc1::IfcShadingDevice(data);
            case 1001: return new ::Ifc4x3_tc1::IfcShadingDeviceType(data);
            case 1002: return new ::Ifc4x3_tc1::IfcShadingDeviceTypeEnum(data);
            case 1003: return new ::Ifc4x3_tc1::IfcShapeAspect(data);
            case 1004: return new ::Ifc4x3_tc1::IfcShapeModel(data);
            case 1005: return new ::Ifc4x3_tc1::IfcShapeRepresentation(data);
            case 1006: return new ::Ifc4x3_tc1::IfcShearModulusMeasure(data);
            case 1008: return new ::Ifc4x3_tc1::IfcShellBasedSurfaceModel(data);
            case 1009: return new ::Ifc4x3_tc1::IfcSign(data);
            case 1010: return new ::Ifc4x3_tc1::IfcSignal(data);
            case 1011: return new ::Ifc4x3_tc1::IfcSignalType(data);
            case 1012: return new ::Ifc4x3_tc1::IfcSignalTypeEnum(data);
            case 1013: return new ::Ifc4x3_tc1::IfcSignType(data);
            case 1014: return new ::Ifc4x3_tc1::IfcSignTypeEnum(data);
            case 1015: return new ::Ifc4x3_tc1::IfcSimpleProperty(data);
            case 1016: return new ::Ifc4x3_tc1::IfcSimplePropertyTemplate(data);
            case 1017: return new ::Ifc4x3_tc1::IfcSimplePropertyTemplateTypeEnum(data);
            case 1019: return new ::Ifc4x3_tc1::IfcSineSpiral(data);
            case 1020: return new ::Ifc4x3_tc1::IfcSIPrefix(data);
            case 1021: return new ::Ifc4x3_tc1::IfcSite(data);
            case 1022: return new ::Ifc4x3_tc1::IfcSIUnit(data);
            case 1023: return new ::Ifc4x3_tc1::IfcSIUnitName(data);
            case 1025: return new ::Ifc4x3_tc1::IfcSlab(data);
            case 1026: return new ::Ifc4x3_tc1::IfcSlabType(data);
            case 1027: return new ::Ifc4x3_tc1::IfcSlabTypeEnum(data);
            case 1028: return new ::Ifc4x3_tc1::IfcSlippageConnectionCondition(data);
            case 1029: return new ::Ifc4x3_tc1::IfcSolarDevice(data);
            case 1030: return new ::Ifc4x3_tc1::IfcSolarDeviceType(data);
            case 1031: return new ::Ifc4x3_tc1::IfcSolarDeviceTypeEnum(data);
            case 1032: return new ::Ifc4x3_tc1::IfcSolidAngleMeasure(data);
            case 1033: return new ::Ifc4x3_tc1::IfcSolidModel(data);
            case 1035: return new ::Ifc4x3_tc1::IfcSoundPowerLevelMeasure(data);
            case 1036: return new ::Ifc4x3_tc1::IfcSoundPowerMeasure(data);
            case 1037: return new ::Ifc4x3_tc1::IfcSoundPressureLevelMeasure(data);
            case 1038: return new ::Ifc4x3_tc1::IfcSoundPressureMeasure(data);
            case 1039: return new ::Ifc4x3_tc1::IfcSpace(data);
            case 1041: return new ::Ifc4x3_tc1::IfcSpaceHeater(data);
            case 1042: return new ::Ifc4x3_tc1::IfcSpaceHeaterType(data);
            case 1043: return new ::Ifc4x3_tc1::IfcSpaceHeaterTypeEnum(data);
            case 1044: return new ::Ifc4x3_tc1::IfcSpaceType(data);
            case 1045: return new ::Ifc4x3_tc1::IfcSpaceTypeEnum(data);
            case 1046: return new ::Ifc4x3_tc1::IfcSpatialElement(data);
            case 1047: return new ::Ifc4x3_tc1::IfcSpatialElementType(data);
            case 1049: return new ::Ifc4x3_tc1::IfcSpatialStructureElement(data);
            case 1050: return new ::Ifc4x3_tc1::IfcSpatialStructureElementType(data);
            case 1051: return new ::Ifc4x3_tc1::IfcSpatialZone(data);
            case 1052: return new ::Ifc4x3_tc1::IfcSpatialZoneType(data);
            case 1053: return new ::Ifc4x3_tc1::IfcSpatialZoneTypeEnum(data);
            case 1054: return new ::Ifc4x3_tc1::IfcSpecificHeatCapacityMeasure(data);
            case 1055: return new ::Ifc4x3_tc1::IfcSpecularExponent(data);
            case 1057: return new ::Ifc4x3_tc1::IfcSpecularRoughness(data);
            case 1058: return new ::Ifc4x3_tc1::IfcSphere(data);
            case 1059: return new ::Ifc4x3_tc1::IfcSphericalSurface(data);
            case 1060: return new ::Ifc4x3_tc1::IfcSpiral(data);
            case 1061: return new ::Ifc4x3_tc1::IfcStackTerminal(data);
            case 1062: return new ::Ifc4x3_tc1::IfcStackTerminalType(data);
            case 1063: return new ::Ifc4x3_tc1::IfcStackTerminalTypeEnum(data);
            case 1064: return new ::Ifc4x3_tc1::IfcStair(data);
            case 1065: return new ::Ifc4x3_tc1::IfcStairFlight(data);
            case 1066: return new ::Ifc4x3_tc1::IfcStairFlightType(data);
            case 1067: return new ::Ifc4x3_tc1::IfcStairFlightTypeEnum(data);
            case 1068: return new ::Ifc4x3_tc1::IfcStairType(data);
            case 1069: return new ::Ifc4x3_tc1::IfcStairTypeEnum(data);
            case 1070: return new ::Ifc4x3_tc1::IfcStateEnum(data);
            case 1071: return new ::Ifc4x3_tc1::IfcStrippedOptional(data);
            case 1072: return new ::Ifc4x3_tc1::IfcStructuralAction(data);
            case 1073: return new ::Ifc4x3_tc1::IfcStructuralActivity(data);
            case 1075: return new ::Ifc4x3_tc1::IfcStructuralAnalysisModel(data);
            case 1076: return new ::Ifc4x3_tc1::IfcStructuralConnection(data);
            case 1077: return new ::Ifc4x3_tc1::IfcStructuralConnectionCondition(data);
            case 1078: return new ::Ifc4x3_tc1::IfcStructuralCurveAction(data);
            case 1079: return new ::Ifc4x3_tc1::IfcStructuralCurveActivityTypeEnum(data);
            case 1080: return new ::Ifc4x3_tc1::IfcStructuralCurveConnection(data);
            case 1081: return new ::Ifc4x3_tc1::IfcStructuralCurveMember(data);
            case 1082: return new ::Ifc4x3_tc1::IfcStructuralCurveMemberTypeEnum(data);
            case 1083: return new ::Ifc4x3_tc1::IfcStructuralCurveMemberVarying(data);
            case 1084: return new ::Ifc4x3_tc1::IfcStructuralCurveReaction(data);
            case 1085: return new ::Ifc4x3_tc1::IfcStructuralItem(data);
            case 1086: return new ::Ifc4x3_tc1::IfcStructuralLinearAction(data);
            case 1087: return new ::Ifc4x3_tc1::IfcStructuralLoad(data);
            case 1088: return new ::Ifc4x3_tc1::IfcStructuralLoadCase(data);
            case 1089: return new ::Ifc4x3_tc1::IfcStructuralLoadConfiguration(data);
            case 1090: return new ::Ifc4x3_tc1::IfcStructuralLoadGroup(data);
            case 1091: return new ::Ifc4x3_tc1::IfcStructuralLoadLinearForce(data);
            case 1092: return new ::Ifc4x3_tc1::IfcStructuralLoadOrResult(data);
            case 1093: return new ::Ifc4x3_tc1::IfcStructuralLoadPlanarForce(data);
            case 1094: return new ::Ifc4x3_tc1::IfcStructuralLoadSingleDisplacement(data);
            case 1095: return new ::Ifc4x3_tc1::IfcStructuralLoadSingleDisplacementDistortion(data);
            case 1096: return new ::Ifc4x3_tc1::IfcStructuralLoadSingleForce(data);
            case 1097: return new ::Ifc4x3_tc1::IfcStructuralLoadSingleForceWarping(data);
            case 1098: return new ::Ifc4x3_tc1::IfcStructuralLoadStatic(data);
            case 1099: return new ::Ifc4x3_tc1::IfcStructuralLoadTemperature(data);
            case 1100: return new ::Ifc4x3_tc1::IfcStructuralMember(data);
            case 1101: return new ::Ifc4x3_tc1::IfcStructuralPlanarAction(data);
            case 1102: return new ::Ifc4x3_tc1::IfcStructuralPointAction(data);
            case 1103: return new ::Ifc4x3_tc1::IfcStructuralPointConnection(data);
            case 1104: return new ::Ifc4x3_tc1::IfcStructuralPointReaction(data);
            case 1105: return new ::Ifc4x3_tc1::IfcStructuralReaction(data);
            case 1106: return new ::Ifc4x3_tc1::IfcStructuralResultGroup(data);
            case 1107: return new ::Ifc4x3_tc1::IfcStructuralSurfaceAction(data);
            case 1108: return new ::Ifc4x3_tc1::IfcStructuralSurfaceActivityTypeEnum(data);
            case 1109: return new ::Ifc4x3_tc1::IfcStructuralSurfaceConnection(data);
            case 1110: return new ::Ifc4x3_tc1::IfcStructuralSurfaceMember(data);
            case 1111: return new ::Ifc4x3_tc1::IfcStructuralSurfaceMemberTypeEnum(data);
            case 1112: return new ::Ifc4x3_tc1::IfcStructuralSurfaceMemberVarying(data);
            case 1113: return new ::Ifc4x3_tc1::IfcStructuralSurfaceReaction(data);
            case 1114: return new ::Ifc4x3_tc1::IfcStyledItem(data);
            case 1115: return new ::Ifc4x3_tc1::IfcStyledRepresentation(data);
            case 1116: return new ::Ifc4x3_tc1::IfcStyleModel(data);
            case 1117: return new ::Ifc4x3_tc1::IfcSubContractResource(data);
            case 1118: return new ::Ifc4x3_tc1::IfcSubContractResourceType(data);
            case 1119: return new ::Ifc4x3_tc1::IfcSubContractResourceTypeEnum(data);
            case 1120: return new ::Ifc4x3_tc1::IfcSubedge(data);
            case 1121: return new ::Ifc4x3_tc1::IfcSurface(data);
            case 1122: return new ::Ifc4x3_tc1::IfcSurfaceCurve(data);
            case 1123: return new ::Ifc4x3_tc1::IfcSurfaceCurveSweptAreaSolid(data);
            case 1124: return new ::Ifc4x3_tc1::IfcSurfaceFeature(data);
            case 1125: return new ::Ifc4x3_tc1::IfcSurfaceFeatureTypeEnum(data);
            case 1126: return new ::Ifc4x3_tc1::IfcSurfaceOfLinearExtrusion(data);
            case 1127: return new ::Ifc4x3_tc1::IfcSurfaceOfRevolution(data);
            case 1129: return new ::Ifc4x3_tc1::IfcSurfaceReinforcementArea(data);
            case 1130: return new ::Ifc4x3_tc1::IfcSurfaceSide(data);
            case 1131: return new ::Ifc4x3_tc1::IfcSurfaceStyle(data);
            case 1133: return new ::Ifc4x3_tc1::IfcSurfaceStyleLighting(data);
            case 1134: return new ::Ifc4x3_tc1::IfcSurfaceStyleRefraction(data);
            case 1135: return new ::Ifc4x3_tc1::IfcSurfaceStyleRendering(data);
            case 1136: return new ::Ifc4x3_tc1::IfcSurfaceStyleShading(data);
            case 1137: return new ::Ifc4x3_tc1::IfcSurfaceStyleWithTextures(data);
            case 1138: return new ::Ifc4x3_tc1::IfcSurfaceTexture(data);
            case 1139: return new ::Ifc4x3_tc1::IfcSweptAreaSolid(data);
            case 1140: return new ::Ifc4x3_tc1::IfcSweptDiskSolid(data);
            case 1141: return new ::Ifc4x3_tc1::IfcSweptDiskSolidPolygonal(data);
            case 1142: return new ::Ifc4x3_tc1::IfcSweptSurface(data);
            case 1143: return new ::Ifc4x3_tc1::IfcSwitchingDevice(data);
            case 1144: return new ::Ifc4x3_tc1::IfcSwitchingDeviceType(data);
            case 1145: return new ::Ifc4x3_tc1::IfcSwitchingDeviceTypeEnum(data);
            case 1146: return new ::Ifc4x3_tc1::IfcSystem(data);
            case 1147: return new ::Ifc4x3_tc1::IfcSystemFurnitureElement(data);
            case 1148: return new ::Ifc4x3_tc1::IfcSystemFurnitureElementType(data);
            case 1149: return new ::Ifc4x3_tc1::IfcSystemFurnitureElementTypeEnum(data);
            case 1150: return new ::Ifc4x3_tc1::IfcTable(data);
            case 1151: return new ::Ifc4x3_tc1::IfcTableColumn(data);
            case 1152: return new ::Ifc4x3_tc1::IfcTableRow(data);
            case 1153: return new ::Ifc4x3_tc1::IfcTank(data);
            case 1154: return new ::Ifc4x3_tc1::IfcTankType(data);
            case 1155: return new ::Ifc4x3_tc1::IfcTankTypeEnum(data);
            case 1156: return new ::Ifc4x3_tc1::IfcTask(data);
            case 1157: return new ::Ifc4x3_tc1::IfcTaskDurationEnum(data);
            case 1158: return new ::Ifc4x3_tc1::IfcTaskTime(data);
            case 1159: return new ::Ifc4x3_tc1::IfcTaskTimeRecurring(data);
            case 1160: return new ::Ifc4x3_tc1::IfcTaskType(data);
            case 1161: return new ::Ifc4x3_tc1::IfcTaskTypeEnum(data);
            case 1162: return new ::Ifc4x3_tc1::IfcTelecomAddress(data);
            case 1163: return new ::Ifc4x3_tc1::IfcTemperatureGradientMeasure(data);
            case 1164: return new ::Ifc4x3_tc1::IfcTemperatureRateOfChangeMeasure(data);
            case 1165: return new ::Ifc4x3_tc1::IfcTendon(data);
            case 1166: return new ::Ifc4x3_tc1::IfcTendonAnchor(data);
            case 1167: return new ::Ifc4x3_tc1::IfcTendonAnchorType(data);
            case 1168: return new ::Ifc4x3_tc1::IfcTendonAnchorTypeEnum(data);
            case 1169: return new ::Ifc4x3_tc1::IfcTendonConduit(data);
            case 1170: return new ::Ifc4x3_tc1::IfcTendonConduitType(data);
            case 1171: return new ::Ifc4x3_tc1::IfcTendonConduitTypeEnum(data);
            case 1172: return new ::Ifc4x3_tc1::IfcTendonType(data);
            case 1173: return new ::Ifc4x3_tc1::IfcTendonTypeEnum(data);
            case 1174: return new ::Ifc4x3_tc1::IfcTessellatedFaceSet(data);
            case 1175: return new ::Ifc4x3_tc1::IfcTessellatedItem(data);
            case 1176: return new ::Ifc4x3_tc1::IfcText(data);
            case 1177: return new ::Ifc4x3_tc1::IfcTextAlignment(data);
            case 1178: return new ::Ifc4x3_tc1::IfcTextDecoration(data);
            case 1179: return new ::Ifc4x3_tc1::IfcTextFontName(data);
            case 1181: return new ::Ifc4x3_tc1::IfcTextLiteral(data);
            case 1182: return new ::Ifc4x3_tc1::IfcTextLiteralWithExtent(data);
            case 1183: return new ::Ifc4x3_tc1::IfcTextPath(data);
            case 1184: return new ::Ifc4x3_tc1::IfcTextStyle(data);
            case 1185: return new ::Ifc4x3_tc1::IfcTextStyleFontModel(data);
            case 1186: return new ::Ifc4x3_tc1::IfcTextStyleForDefinedFont(data);
            case 1187: return new ::Ifc4x3_tc1::IfcTextStyleTextModel(data);
            case 1188: return new ::Ifc4x3_tc1::IfcTextTransformation(data);
            case 1189: return new ::Ifc4x3_tc1::IfcTextureCoordinate(data);
            case 1190: return new ::Ifc4x3_tc1::IfcTextureCoordinateGenerator(data);
            case 1191: return new ::Ifc4x3_tc1::IfcTextureCoordinateIndices(data);
            case 1192: return new ::Ifc4x3_tc1::IfcTextureCoordinateIndicesWithVoids(data);
            case 1193: return new ::Ifc4x3_tc1::IfcTextureMap(data);
            case 1194: return new ::Ifc4x3_tc1::IfcTextureVertex(data);
            case 1195: return new ::Ifc4x3_tc1::IfcTextureVertexList(data);
            case 1196: return new ::Ifc4x3_tc1::IfcThermalAdmittanceMeasure(data);
            case 1197: return new ::Ifc4x3_tc1::IfcThermalConductivityMeasure(data);
            case 1198: return new ::Ifc4x3_tc1::IfcThermalExpansionCoefficientMeasure(data);
            case 1199: return new ::Ifc4x3_tc1::IfcThermalResistanceMeasure(data);
            case 1200: return new ::Ifc4x3_tc1::IfcThermalTransmittanceMeasure(data);
            case 1201: return new ::Ifc4x3_tc1::IfcThermodynamicTemperatureMeasure(data);
            case 1202: return new ::Ifc4x3_tc1::IfcThirdOrderPolynomialSpiral(data);
            case 1203: return new ::Ifc4x3_tc1::IfcTime(data);
            case 1204: return new ::Ifc4x3_tc1::IfcTimeMeasure(data);
            case 1206: return new ::Ifc4x3_tc1::IfcTimePeriod(data);
            case 1207: return new ::Ifc4x3_tc1::IfcTimeSeries(data);
            case 1208: return new ::Ifc4x3_tc1::IfcTimeSeriesDataTypeEnum(data);
            case 1209: return new ::Ifc4x3_tc1::IfcTimeSeriesValue(data);
            case 1210: return new ::Ifc4x3_tc1::IfcTimeStamp(data);
            case 1211: return new ::Ifc4x3_tc1::IfcTopologicalRepresentationItem(data);
            case 1212: return new ::Ifc4x3_tc1::IfcTopologyRepresentation(data);
            case 1213: return new ::Ifc4x3_tc1::IfcToroidalSurface(data);
            case 1214: return new ::Ifc4x3_tc1::IfcTorqueMeasure(data);
            case 1215: return new ::Ifc4x3_tc1::IfcTrackElement(data);
            case 1216: return new ::Ifc4x3_tc1::IfcTrackElementType(data);
            case 1217: return new ::Ifc4x3_tc1::IfcTrackElementTypeEnum(data);
            case 1218: return new ::Ifc4x3_tc1::IfcTransformer(data);
            case 1219: return new ::Ifc4x3_tc1::IfcTransformerType(data);
            case 1220: return new ::Ifc4x3_tc1::IfcTransformerTypeEnum(data);
            case 1221: return new ::Ifc4x3_tc1::IfcTransitionCode(data);
            case 1223: return new ::Ifc4x3_tc1::IfcTransportationDevice(data);
            case 1224: return new ::Ifc4x3_tc1::IfcTransportationDeviceType(data);
            case 1225: return new ::Ifc4x3_tc1::IfcTransportElement(data);
            case 1226: return new ::Ifc4x3_tc1::IfcTransportElementType(data);
            case 1227: return new ::Ifc4x3_tc1::IfcTransportElementTypeEnum(data);
            case 1228: return new ::Ifc4x3_tc1::IfcTrapeziumProfileDef(data);
            case 1229: return new ::Ifc4x3_tc1::IfcTriangulatedFaceSet(data);
            case 1230: return new ::Ifc4x3_tc1::IfcTriangulatedIrregularNetwork(data);
            case 1231: return new ::Ifc4x3_tc1::IfcTrimmedCurve(data);
            case 1232: return new ::Ifc4x3_tc1::IfcTrimmingPreference(data);
            case 1234: return new ::Ifc4x3_tc1::IfcTShapeProfileDef(data);
            case 1235: return new ::Ifc4x3_tc1::IfcTubeBundle(data);
            case 1236: return new ::Ifc4x3_tc1::IfcTubeBundleType(data);
            case 1237: return new ::Ifc4x3_tc1::IfcTubeBundleTypeEnum(data);
            case 1238: return new ::Ifc4x3_tc1::IfcTypeObject(data);
            case 1239: return new ::Ifc4x3_tc1::IfcTypeProcess(data);
            case 1240: return new ::Ifc4x3_tc1::IfcTypeProduct(data);
            case 1241: return new ::Ifc4x3_tc1::IfcTypeResource(data);
            case 1243: return new ::Ifc4x3_tc1::IfcUnitaryControlElement(data);
            case 1244: return new ::Ifc4x3_tc1::IfcUnitaryControlElementType(data);
            case 1245: return new ::Ifc4x3_tc1::IfcUnitaryControlElementTypeEnum(data);
            case 1246: return new ::Ifc4x3_tc1::IfcUnitaryEquipment(data);
            case 1247: return new ::Ifc4x3_tc1::IfcUnitaryEquipmentType(data);
            case 1248: return new ::Ifc4x3_tc1::IfcUnitaryEquipmentTypeEnum(data);
            case 1249: return new ::Ifc4x3_tc1::IfcUnitAssignment(data);
            case 1250: return new ::Ifc4x3_tc1::IfcUnitEnum(data);
            case 1251: return new ::Ifc4x3_tc1::IfcURIReference(data);
            case 1252: return new ::Ifc4x3_tc1::IfcUShapeProfileDef(data);
            case 1254: return new ::Ifc4x3_tc1::IfcValve(data);
            case 1255: return new ::Ifc4x3_tc1::IfcValveType(data);
            case 1256: return new ::Ifc4x3_tc1::IfcValveTypeEnum(data);
            case 1257: return new ::Ifc4x3_tc1::IfcVaporPermeabilityMeasure(data);
            case 1258: return new ::Ifc4x3_tc1::IfcVector(data);
            case 1260: return new ::Ifc4x3_tc1::IfcVehicle(data);
            case 1261: return new ::Ifc4x3_tc1::IfcVehicleType(data);
            case 1262: return new ::Ifc4x3_tc1::IfcVehicleTypeEnum(data);
            case 1263: return new ::Ifc4x3_tc1::IfcVertex(data);
            case 1264: return new ::Ifc4x3_tc1::IfcVertexLoop(data);
            case 1265: return new ::Ifc4x3_tc1::IfcVertexPoint(data);
            case 1266: return new ::Ifc4x3_tc1::IfcVibrationDamper(data);
            case 1267: return new ::Ifc4x3_tc1::IfcVibrationDamperType(data);
            case 1268: return new ::Ifc4x3_tc1::IfcVibrationDamperTypeEnum(data);
            case 1269: return new ::Ifc4x3_tc1::IfcVibrationIsolator(data);
            case 1270: return new ::Ifc4x3_tc1::IfcVibrationIsolatorType(data);
            case 1271: return new ::Ifc4x3_tc1::IfcVibrationIsolatorTypeEnum(data);
            case 1272: return new ::Ifc4x3_tc1::IfcVirtualElement(data);
            case 1273: return new ::Ifc4x3_tc1::IfcVirtualElementTypeEnum(data);
            case 1274: return new ::Ifc4x3_tc1::IfcVirtualGridIntersection(data);
            case 1275: return new ::Ifc4x3_tc1::IfcVoidingFeature(data);
            case 1276: return new ::Ifc4x3_tc1::IfcVoidingFeatureTypeEnum(data);
            case 1277: return new ::Ifc4x3_tc1::IfcVolumeMeasure(data);
            case 1278: return new ::Ifc4x3_tc1::IfcVolumetricFlowRateMeasure(data);
            case 1279: return new ::Ifc4x3_tc1::IfcWall(data);
            case 1280: return new ::Ifc4x3_tc1::IfcWallStandardCase(data);
            case 1281: return new ::Ifc4x3_tc1::IfcWallType(data);
            case 1282: return new ::Ifc4x3_tc1::IfcWallTypeEnum(data);
            case 1283: return new ::Ifc4x3_tc1::IfcWarpingConstantMeasure(data);
            case 1284: return new ::Ifc4x3_tc1::IfcWarpingMomentMeasure(data);
            case 1286: return new ::Ifc4x3_tc1::IfcWasteTerminal(data);
            case 1287: return new ::Ifc4x3_tc1::IfcWasteTerminalType(data);
            case 1288: return new ::Ifc4x3_tc1::IfcWasteTerminalTypeEnum(data);
            case 1289: return new ::Ifc4x3_tc1::IfcWindow(data);
            case 1290: return new ::Ifc4x3_tc1::IfcWindowLiningProperties(data);
            case 1291: return new ::Ifc4x3_tc1::IfcWindowPanelOperationEnum(data);
            case 1292: return new ::Ifc4x3_tc1::IfcWindowPanelPositionEnum(data);
            case 1293: return new ::Ifc4x3_tc1::IfcWindowPanelProperties(data);
            case 1294: return new ::Ifc4x3_tc1::IfcWindowType(data);
            case 1295: return new ::Ifc4x3_tc1::IfcWindowTypeEnum(data);
            case 1296: return new ::Ifc4x3_tc1::IfcWindowTypePartitioningEnum(data);
            case 1297: return new ::Ifc4x3_tc1::IfcWorkCalendar(data);
            case 1298: return new ::Ifc4x3_tc1::IfcWorkCalendarTypeEnum(data);
            case 1299: return new ::Ifc4x3_tc1::IfcWorkControl(data);
            case 1300: return new ::Ifc4x3_tc1::IfcWorkPlan(data);
            case 1301: return new ::Ifc4x3_tc1::IfcWorkPlanTypeEnum(data);
            case 1302: return new ::Ifc4x3_tc1::IfcWorkSchedule(data);
            case 1303: return new ::Ifc4x3_tc1::IfcWorkScheduleTypeEnum(data);
            case 1304: return new ::Ifc4x3_tc1::IfcWorkTime(data);
            case 1305: return new ::Ifc4x3_tc1::IfcZone(data);
            case 1306: return new ::Ifc4x3_tc1::IfcZShapeProfileDef(data);
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
"BRAKES"s,
"BUOYANCY"s,
"COMPLETION_G1"s,
"CREEP"s,
"CURRENT"s,
"DEAD_LOAD_G"s,
"EARTHQUAKE_E"s,
"ERECTION"s,
"FIRE"s,
"ICE"s,
"IMPACT"s,
"IMPULSE"s,
"LACK_OF_FIT"s,
"LIVE_LOAD_Q"s,
"PRESTRESSING_P"s,
"PROPPING"s,
"RAIN"s,
"SETTLEMENT_U"s,
"SHRINKAGE"s,
"SNOW_S"s,
"SYSTEM_IMPERFECTION"s,
"TEMPERATURE_T"s,
"TRANSPORT"s,
"WAVE"s,
"WIND_W"s,
"IfcActionTypeEnum"s,
"EXTRAORDINARY_A"s,
"PERMANENT_G"s,
"VARIABLE_Q"s,
"IfcActuatorTypeEnum"s,
"ELECTRICACTUATOR"s,
"HANDOPERATEDACTUATOR"s,
"HYDRAULICACTUATOR"s,
"PNEUMATICACTUATOR"s,
"THERMOSTATICACTUATOR"s,
"IfcAddressTypeEnum"s,
"DISTRIBUTIONPOINT"s,
"HOME"s,
"OFFICE"s,
"SITE"s,
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
"HEATPIPE"s,
"ROTARYWHEEL"s,
"RUNAROUNDCOILLOOP"s,
"THERMOSIPHONCOILTYPEHEATEXCHANGERS"s,
"THERMOSIPHONSEALEDTUBEHEATEXCHANGERS"s,
"TWINTOWERENTHALPYRECOVERYLOOPS"s,
"IfcAlarmTypeEnum"s,
"BELL"s,
"BREAKGLASSBUTTON"s,
"LIGHT"s,
"MANUALPULLBOX"s,
"RAILWAYCROCODILE"s,
"RAILWAYDETONATOR"s,
"SIREN"s,
"WHISTLE"s,
"IfcAlignmentCantSegmentTypeEnum"s,
"BLOSSCURVE"s,
"CONSTANTCANT"s,
"COSINECURVE"s,
"HELMERTCURVE"s,
"LINEARTRANSITION"s,
"SINECURVE"s,
"VIENNESEBEND"s,
"IfcAlignmentHorizontalSegmentTypeEnum"s,
"CIRCULARARC"s,
"CLOTHOID"s,
"CUBIC"s,
"LINE"s,
"IfcAlignmentTypeEnum"s,
"IfcAlignmentVerticalSegmentTypeEnum"s,
"CONSTANTGRADIENT"s,
"PARABOLICARC"s,
"IfcAmountOfSubstanceMeasure"s,
"IfcAnalysisModelTypeEnum"s,
"IN_PLANE_LOADING_2D"s,
"LOADING_3D"s,
"OUT_PLANE_LOADING_2D"s,
"IfcAnalysisTheoryTypeEnum"s,
"FIRST_ORDER_THEORY"s,
"FULL_NONLINEAR_THEORY"s,
"SECOND_ORDER_THEORY"s,
"THIRD_ORDER_THEORY"s,
"IfcAngularVelocityMeasure"s,
"IfcAnnotationTypeEnum"s,
"ASBUILTAREA"s,
"ASBUILTLINE"s,
"ASBUILTPOINT"s,
"ASSUMEDAREA"s,
"ASSUMEDLINE"s,
"ASSUMEDPOINT"s,
"NON_PHYSICAL_SIGNAL"s,
"SUPERELEVATIONEVENT"s,
"WIDTHEVENT"s,
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
"COMMUNICATIONTERMINAL"s,
"DISPLAY"s,
"MICROPHONE"s,
"PLAYER"s,
"PROJECTOR"s,
"RECEIVER"s,
"RECORDINGEQUIPMENT"s,
"SPEAKER"s,
"SWITCHER"s,
"TELEPHONE"s,
"TUNER"s,
"IfcBSplineCurveForm"s,
"CIRCULAR_ARC"s,
"ELLIPTIC_ARC"s,
"HYPERBOLIC_ARC"s,
"PARABOLIC_ARC"s,
"POLYLINE_FORM"s,
"UNSPECIFIED"s,
"IfcBSplineSurfaceForm"s,
"CONICAL_SURF"s,
"CYLINDRICAL_SURF"s,
"GENERALISED_CONE"s,
"PLANE_SURF"s,
"QUADRIC_SURF"s,
"RULED_SURF"s,
"SPHERICAL_SURF"s,
"SURF_OF_LINEAR_EXTRUSION"s,
"SURF_OF_REVOLUTION"s,
"TOROIDAL_SURF"s,
"IfcBeamTypeEnum"s,
"BEAM"s,
"CORNICE"s,
"DIAPHRAGM"s,
"EDGEBEAM"s,
"GIRDER_SEGMENT"s,
"HATSTONE"s,
"HOLLOWCORE"s,
"JOIST"s,
"LINTEL"s,
"PIERCAP"s,
"SPANDREL"s,
"T_BEAM"s,
"IfcBearingTypeEnum"s,
"CYLINDRICAL"s,
"DISK"s,
"ELASTOMERIC"s,
"GUIDE"s,
"POT"s,
"ROCKER"s,
"ROLLER"s,
"SPHERICAL"s,
"IfcBenchmarkEnum"s,
"EQUALTO"s,
"GREATERTHAN"s,
"GREATERTHANOREQUALTO"s,
"INCLUDEDIN"s,
"INCLUDES"s,
"LESSTHAN"s,
"LESSTHANOREQUALTO"s,
"NOTEQUALTO"s,
"NOTINCLUDEDIN"s,
"NOTINCLUDES"s,
"IfcBinary"s,
"IfcBoilerTypeEnum"s,
"STEAM"s,
"WATER"s,
"IfcBoolean"s,
"IfcBooleanOperator"s,
"DIFFERENCE"s,
"INTERSECTION"s,
"UNION"s,
"IfcBridgePartTypeEnum"s,
"ABUTMENT"s,
"DECK"s,
"DECK_SEGMENT"s,
"FOUNDATION"s,
"PIER"s,
"PIER_SEGMENT"s,
"PYLON"s,
"SUBSTRUCTURE"s,
"SUPERSTRUCTURE"s,
"SURFACESTRUCTURE"s,
"IfcBridgeTypeEnum"s,
"ARCHED"s,
"CABLE_STAYED"s,
"CANTILEVER"s,
"CULVERT"s,
"FRAMEWORK"s,
"GIRDER"s,
"SUSPENSION"s,
"TRUSS"s,
"IfcBuildingElementPartTypeEnum"s,
"APRON"s,
"ARMOURUNIT"s,
"INSULATION"s,
"PRECASTPANEL"s,
"SAFETYCAGE"s,
"IfcBuildingElementProxyTypeEnum"s,
"COMPLEX"s,
"ELEMENT"s,
"PARTIAL"s,
"PROVISIONFORSPACE"s,
"PROVISIONFORVOID"s,
"IfcBuildingSystemTypeEnum"s,
"FENESTRATION"s,
"LOADBEARING"s,
"OUTERSHELL"s,
"SHADING"s,
"IfcBuiltSystemTypeEnum"s,
"EROSIONPREVENTION"s,
"MOORING"s,
"PRESTRESSING"s,
"RAILWAYLINE"s,
"RAILWAYTRACK"s,
"REINFORCING"s,
"TRACKCIRCUIT"s,
"IfcBurnerTypeEnum"s,
"IfcCableCarrierFittingTypeEnum"s,
"BEND"s,
"CONNECTOR"s,
"CROSS"s,
"JUNCTION"s,
"REDUCER"s,
"TEE"s,
"TRANSITION"s,
"IfcCableCarrierSegmentTypeEnum"s,
"CABLEBRACKET"s,
"CABLELADDERSEGMENT"s,
"CABLETRAYSEGMENT"s,
"CABLETRUNKINGSEGMENT"s,
"CATENARYWIRE"s,
"CONDUITSEGMENT"s,
"DROPPER"s,
"IfcCableFittingTypeEnum"s,
"ENTRY"s,
"EXIT"s,
"FANOUT"s,
"IfcCableSegmentTypeEnum"s,
"BUSBARSEGMENT"s,
"CABLESEGMENT"s,
"CONDUCTORSEGMENT"s,
"CONTACTWIRESEGMENT"s,
"CORESEGMENT"s,
"FIBERSEGMENT"s,
"FIBERTUBE"s,
"OPTICALCABLESEGMENT"s,
"STITCHWIRE"s,
"WIREPAIRSEGMENT"s,
"IfcCaissonFoundationTypeEnum"s,
"CAISSON"s,
"WELL"s,
"IfcCardinalPointReference"s,
"IfcChangeActionEnum"s,
"ADDED"s,
"DELETED"s,
"MODIFIED"s,
"NOCHANGE"s,
"IfcChillerTypeEnum"s,
"AIRCOOLED"s,
"HEATRECOVERY"s,
"WATERCOOLED"s,
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
"PIERSTEM"s,
"PIERSTEM_SEGMENT"s,
"PILASTER"s,
"STANDCOLUMN"s,
"IfcCommunicationsApplianceTypeEnum"s,
"ANTENNA"s,
"AUTOMATON"s,
"COMPUTER"s,
"GATEWAY"s,
"INTELLIGENTPERIPHERAL"s,
"IPNETWORKEQUIPMENT"s,
"LINESIDEELECTRONICUNIT"s,
"MODEM"s,
"NETWORKAPPLIANCE"s,
"NETWORKBRIDGE"s,
"NETWORKHUB"s,
"OPTICALLINETERMINAL"s,
"OPTICALNETWORKUNIT"s,
"PRINTER"s,
"RADIOBLOCKCENTER"s,
"REPEATER"s,
"ROUTER"s,
"SCANNER"s,
"TELECOMMAND"s,
"TELEPHONYEXCHANGE"s,
"TRANSITIONCOMPONENT"s,
"TRANSPONDER"s,
"TRANSPORTEQUIPMENT"s,
"IfcComplexNumber"s,
"IfcComplexPropertyTemplateTypeEnum"s,
"P_COMPLEX"s,
"Q_COMPLEX"s,
"IfcCompoundPlaneAngleMeasure"s,
"IfcCompressorTypeEnum"s,
"BOOSTER"s,
"DYNAMIC"s,
"HERMETIC"s,
"OPENTYPE"s,
"RECIPROCATING"s,
"ROLLINGPISTON"s,
"ROTARY"s,
"ROTARYVANE"s,
"SCROLL"s,
"SEMIHERMETIC"s,
"SINGLESCREW"s,
"SINGLESTAGE"s,
"TROCHOIDAL"s,
"TWINSCREW"s,
"WELDEDSHELLHERMETIC"s,
"IfcCondenserTypeEnum"s,
"EVAPORATIVECOOLED"s,
"WATERCOOLEDBRAZEDPLATE"s,
"WATERCOOLEDSHELLCOIL"s,
"WATERCOOLEDSHELLTUBE"s,
"WATERCOOLEDTUBEINTUBE"s,
"IfcConnectionTypeEnum"s,
"ATEND"s,
"ATPATH"s,
"ATSTART"s,
"IfcConstraintEnum"s,
"ADVISORY"s,
"HARD"s,
"SOFT"s,
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
"MULTIPOSITION"s,
"PROGRAMMABLE"s,
"PROPORTIONAL"s,
"TWOPOSITION"s,
"IfcConveyorSegmentTypeEnum"s,
"BELTCONVEYOR"s,
"BUCKETCONVEYOR"s,
"CHUTECONVEYOR"s,
"SCREWCONVEYOR"s,
"IfcCooledBeamTypeEnum"s,
"ACTIVE"s,
"PASSIVE"s,
"IfcCoolingTowerTypeEnum"s,
"MECHANICALFORCEDDRAFT"s,
"MECHANICALINDUCEDDRAFT"s,
"NATURALDRAFT"s,
"IfcCostItemTypeEnum"s,
"IfcCostScheduleTypeEnum"s,
"BUDGET"s,
"COSTPLAN"s,
"ESTIMATE"s,
"PRICEDBILLOFQUANTITIES"s,
"SCHEDULEOFRATES"s,
"TENDER"s,
"UNPRICEDBILLOFQUANTITIES"s,
"IfcCountMeasure"s,
"IfcCourseTypeEnum"s,
"ARMOUR"s,
"BALLASTBED"s,
"CORE"s,
"FILTER"s,
"PAVEMENT"s,
"PROTECTION"s,
"IfcCoveringTypeEnum"s,
"CEILING"s,
"CLADDING"s,
"COPING"s,
"FLOORING"s,
"MEMBRANE"s,
"MOLDING"s,
"ROOFING"s,
"SKIRTINGBOARD"s,
"SLEEVING"s,
"TOPPING"s,
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
"ACCELERATIONUNIT"s,
"ANGULARVELOCITYUNIT"s,
"AREADENSITYUNIT"s,
"COMPOUNDPLANEANGLEUNIT"s,
"CURVATUREUNIT"s,
"DYNAMICVISCOSITYUNIT"s,
"HEATFLUXDENSITYUNIT"s,
"HEATINGVALUEUNIT"s,
"INTEGERCOUNTRATEUNIT"s,
"IONCONCENTRATIONUNIT"s,
"ISOTHERMALMOISTURECAPACITYUNIT"s,
"KINEMATICVISCOSITYUNIT"s,
"LINEARFORCEUNIT"s,
"LINEARMOMENTUNIT"s,
"LINEARSTIFFNESSUNIT"s,
"LINEARVELOCITYUNIT"s,
"LUMINOUSINTENSITYDISTRIBUTIONUNIT"s,
"MASSDENSITYUNIT"s,
"MASSFLOWRATEUNIT"s,
"MASSPERLENGTHUNIT"s,
"MODULUSOFELASTICITYUNIT"s,
"MODULUSOFLINEARSUBGRADEREACTIONUNIT"s,
"MODULUSOFROTATIONALSUBGRADEREACTIONUNIT"s,
"MODULUSOFSUBGRADEREACTIONUNIT"s,
"MOISTUREDIFFUSIVITYUNIT"s,
"MOLECULARWEIGHTUNIT"s,
"MOMENTOFINERTIAUNIT"s,
"PHUNIT"s,
"PLANARFORCEUNIT"s,
"ROTATIONALFREQUENCYUNIT"s,
"ROTATIONALMASSUNIT"s,
"ROTATIONALSTIFFNESSUNIT"s,
"SECTIONAREAINTEGRALUNIT"s,
"SECTIONMODULUSUNIT"s,
"SHEARMODULUSUNIT"s,
"SOUNDPOWERLEVELUNIT"s,
"SOUNDPOWERUNIT"s,
"SOUNDPRESSURELEVELUNIT"s,
"SOUNDPRESSUREUNIT"s,
"SPECIFICHEATCAPACITYUNIT"s,
"TEMPERATUREGRADIENTUNIT"s,
"TEMPERATURERATEOFCHANGEUNIT"s,
"THERMALADMITTANCEUNIT"s,
"THERMALCONDUCTANCEUNIT"s,
"THERMALEXPANSIONCOEFFICIENTUNIT"s,
"THERMALRESISTANCEUNIT"s,
"THERMALTRANSMITTANCEUNIT"s,
"TORQUEUNIT"s,
"VAPORPERMEABILITYUNIT"s,
"VOLUMETRICFLOWRATEUNIT"s,
"WARPINGCONSTANTUNIT"s,
"WARPINGMOMENTUNIT"s,
"IfcDescriptiveMeasure"s,
"IfcDimensionCount"s,
"IfcDirectionSenseEnum"s,
"NEGATIVE"s,
"POSITIVE"s,
"IfcDiscreteAccessoryTypeEnum"s,
"ANCHORPLATE"s,
"BIRDPROTECTION"s,
"BRACKET"s,
"CABLEARRANGER"s,
"ELASTIC_CUSHION"s,
"EXPANSION_JOINT_DEVICE"s,
"FILLER"s,
"FLASHING"s,
"INSULATOR"s,
"LOCK"s,
"PANEL_STRENGTHENING"s,
"POINTMACHINEMOUNTINGDEVICE"s,
"POINT_MACHINE_LOCKING_DEVICE"s,
"RAILBRACE"s,
"RAILPAD"s,
"RAIL_LUBRICATION"s,
"RAIL_MECHANICAL_EQUIPMENT"s,
"SHOE"s,
"SLIDINGCHAIR"s,
"SOUNDABSORPTION"s,
"TENSIONINGEQUIPMENT"s,
"IfcDistributionBoardTypeEnum"s,
"CONSUMERUNIT"s,
"DISPATCHINGBOARD"s,
"DISTRIBUTIONBOARD"s,
"DISTRIBUTIONFRAME"s,
"MOTORCONTROLCENTRE"s,
"SWITCHBOARD"s,
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
"WIRELESS"s,
"IfcDistributionSystemEnum"s,
"AIRCONDITIONING"s,
"AUDIOVISUAL"s,
"CATENARY_SYSTEM"s,
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
"FIXEDTRANSMISSIONNETWORK"s,
"GAS"s,
"HAZARDOUS"s,
"LIGHTNINGPROTECTION"s,
"MOBILENETWORK"s,
"MONITORINGSYSTEM"s,
"MUNICIPALSOLIDWASTE"s,
"OIL"s,
"OPERATIONAL"s,
"OPERATIONALTELEPHONYSYSTEM"s,
"OVERHEAD_CONTACTLINE_SYSTEM"s,
"POWERGENERATION"s,
"RAINWATER"s,
"REFRIGERATION"s,
"RETURN_CIRCUIT"s,
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
"CONFIDENTIAL"s,
"PERSONAL"s,
"PUBLIC"s,
"RESTRICTED"s,
"IfcDocumentStatusEnum"s,
"DRAFT"s,
"FINAL"s,
"FINALDRAFT"s,
"REVISION"s,
"IfcDoorPanelOperationEnum"s,
"DOUBLE_ACTING"s,
"FIXEDPANEL"s,
"FOLDING"s,
"REVOLVING"s,
"ROLLINGUP"s,
"SLIDING"s,
"SWINGING"s,
"IfcDoorPanelPositionEnum"s,
"LEFT"s,
"MIDDLE"s,
"RIGHT"s,
"IfcDoorTypeEnum"s,
"BOOM_BARRIER"s,
"DOOR"s,
"GATE"s,
"TRAPDOOR"s,
"TURNSTILE"s,
"IfcDoorTypeOperationEnum"s,
"DOUBLE_DOOR_DOUBLE_SWING"s,
"DOUBLE_DOOR_FOLDING"s,
"DOUBLE_DOOR_LIFTING_VERTICAL"s,
"DOUBLE_DOOR_SINGLE_SWING"s,
"DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT"s,
"DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT"s,
"DOUBLE_DOOR_SLIDING"s,
"DOUBLE_SWING_LEFT"s,
"DOUBLE_SWING_RIGHT"s,
"FOLDING_TO_LEFT"s,
"FOLDING_TO_RIGHT"s,
"LIFTING_HORIZONTAL"s,
"LIFTING_VERTICAL_LEFT"s,
"LIFTING_VERTICAL_RIGHT"s,
"REVOLVING_VERTICAL"s,
"SINGLE_SWING_LEFT"s,
"SINGLE_SWING_RIGHT"s,
"SLIDING_TO_LEFT"s,
"SLIDING_TO_RIGHT"s,
"SWING_FIXED_LEFT"s,
"SWING_FIXED_RIGHT"s,
"IfcDoseEquivalentMeasure"s,
"IfcDuctFittingTypeEnum"s,
"OBSTRUCTION"s,
"IfcDuctSegmentTypeEnum"s,
"FLEXIBLESEGMENT"s,
"RIGIDSEGMENT"s,
"IfcDuctSilencerTypeEnum"s,
"FLATOVAL"s,
"RECTANGULAR"s,
"ROUND"s,
"IfcDuration"s,
"IfcDynamicViscosityMeasure"s,
"IfcEarthworksCutTypeEnum"s,
"BASE_EXCAVATION"s,
"CUT"s,
"DREDGING"s,
"EXCAVATION"s,
"OVEREXCAVATION"s,
"PAVEMENTMILLING"s,
"STEPEXCAVATION"s,
"TOPSOILREMOVAL"s,
"IfcEarthworksFillTypeEnum"s,
"BACKFILL"s,
"COUNTERWEIGHT"s,
"EMBANKMENT"s,
"SLOPEFILL"s,
"SUBGRADE"s,
"SUBGRADEBED"s,
"TRANSITIONSECTION"s,
"IfcElectricApplianceTypeEnum"s,
"DISHWASHER"s,
"ELECTRICCOOKER"s,
"FREESTANDINGELECTRICHEATER"s,
"FREESTANDINGFAN"s,
"FREESTANDINGWATERCOOLER"s,
"FREESTANDINGWATERHEATER"s,
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
"IfcElectricFlowStorageDeviceTypeEnum"s,
"BATTERY"s,
"CAPACITOR"s,
"CAPACITORBANK"s,
"COMPENSATOR"s,
"HARMONICFILTER"s,
"INDUCTOR"s,
"INDUCTORBANK"s,
"RECHARGER"s,
"UPS"s,
"IfcElectricFlowTreatmentDeviceTypeEnum"s,
"ELECTRONICFILTER"s,
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
"RELAY"s,
"TIMECLOCK"s,
"TIMEDELAY"s,
"IfcElectricVoltageMeasure"s,
"IfcElementAssemblyTypeEnum"s,
"ACCESSORY_ASSEMBLY"s,
"ARCH"s,
"BEAM_GRID"s,
"BRACED_FRAME"s,
"CROSS_BRACING"s,
"DILATATIONPANEL"s,
"ENTRANCEWORKS"s,
"GRID"s,
"MAST"s,
"RAIL_MECHANICAL_EQUIPMENT_ASSEMBLY"s,
"REINFORCEMENT_UNIT"s,
"RIGID_FRAME"s,
"SHELTER"s,
"SIGNALASSEMBLY"s,
"SLAB_FIELD"s,
"SUMPBUSTER"s,
"SUPPORTINGASSEMBLY"s,
"SUSPENSIONASSEMBLY"s,
"TRACKPANEL"s,
"TRACTION_SWITCHING_ASSEMBLY"s,
"TRAFFIC_CALMING_DEVICE"s,
"TURNOUTPANEL"s,
"IfcElementCompositionEnum"s,
"IfcEnergyMeasure"s,
"IfcEngineTypeEnum"s,
"EXTERNALCOMBUSTION"s,
"INTERNALCOMBUSTION"s,
"IfcEvaporativeCoolerTypeEnum"s,
"DIRECTEVAPORATIVEAIRWASHER"s,
"DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER"s,
"DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER"s,
"DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER"s,
"DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER"s,
"INDIRECTDIRECTCOMBINATION"s,
"INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER"s,
"INDIRECTEVAPORATIVEPACKAGEAIRCOOLER"s,
"INDIRECTEVAPORATIVEWETCOIL"s,
"IfcEvaporatorTypeEnum"s,
"DIRECTEXPANSION"s,
"DIRECTEXPANSIONBRAZEDPLATE"s,
"DIRECTEXPANSIONSHELLANDTUBE"s,
"DIRECTEXPANSIONTUBEINTUBE"s,
"FLOODEDSHELLANDTUBE"s,
"SHELLANDCOIL"s,
"IfcEventTriggerTypeEnum"s,
"EVENTCOMPLEX"s,
"EVENTMESSAGE"s,
"EVENTRULE"s,
"EVENTTIME"s,
"IfcEventTypeEnum"s,
"ENDEVENT"s,
"INTERMEDIATEEVENT"s,
"STARTEVENT"s,
"IfcExternalSpatialElementTypeEnum"s,
"EXTERNAL"s,
"EXTERNAL_EARTH"s,
"EXTERNAL_FIRE"s,
"EXTERNAL_WATER"s,
"IfcFacilityPartCommonTypeEnum"s,
"ABOVEGROUND"s,
"BELOWGROUND"s,
"LEVELCROSSING"s,
"SEGMENT"s,
"TERMINAL"s,
"IfcFacilityUsageEnum"s,
"LATERAL"s,
"LONGITUDINAL"s,
"REGION"s,
"VERTICAL"s,
"IfcFanTypeEnum"s,
"CENTRIFUGALAIRFOIL"s,
"CENTRIFUGALBACKWARDINCLINEDCURVED"s,
"CENTRIFUGALFORWARDCURVED"s,
"CENTRIFUGALRADIAL"s,
"PROPELLORAXIAL"s,
"TUBEAXIAL"s,
"VANEAXIAL"s,
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
"FIREMONITOR"s,
"HOSEREEL"s,
"SPRINKLER"s,
"SPRINKLERDEFLECTOR"s,
"IfcFlowDirectionEnum"s,
"SINK"s,
"SOURCE"s,
"SOURCEANDSINK"s,
"IfcFlowInstrumentTypeEnum"s,
"AMMETER"s,
"COMBINED"s,
"FREQUENCYMETER"s,
"PHASEANGLEMETER"s,
"POWERFACTORMETER"s,
"PRESSUREGAUGE"s,
"THERMOMETER"s,
"VOLTMETER"s,
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
"BED"s,
"CHAIR"s,
"DESK"s,
"FILECABINET"s,
"SHELF"s,
"SOFA"s,
"TABLE"s,
"TECHNICALCABINET"s,
"IfcGeographicElementTypeEnum"s,
"SOIL_BORING_POINT"s,
"TERRAIN"s,
"VEGETATION"s,
"IfcGeometricProjectionEnum"s,
"ELEVATION_VIEW"s,
"GRAPH_VIEW"s,
"MODEL_VIEW"s,
"PLAN_VIEW"s,
"REFLECTED_PLAN_VIEW"s,
"SECTION_VIEW"s,
"SKETCH_VIEW"s,
"IfcGeotechnicalStratumTypeEnum"s,
"SOLID"s,
"VOID"s,
"IfcGlobalOrLocalEnum"s,
"GLOBAL_COORDS"s,
"LOCAL_COORDS"s,
"IfcGloballyUniqueId"s,
"IfcGridTypeEnum"s,
"IRREGULAR"s,
"RADIAL"s,
"TRIANGULAR"s,
"IfcHeatExchangerTypeEnum"s,
"PLATE"s,
"SHELLANDTUBE"s,
"TURNOUTHEATING"s,
"IfcHeatFluxDensityMeasure"s,
"IfcHeatingValueMeasure"s,
"IfcHumidifierTypeEnum"s,
"ADIABATICAIRWASHER"s,
"ADIABATICATOMIZING"s,
"ADIABATICCOMPRESSEDAIRNOZZLE"s,
"ADIABATICPAN"s,
"ADIABATICRIGIDMEDIA"s,
"ADIABATICULTRASONIC"s,
"ADIABATICWETTEDELEMENT"s,
"ASSISTEDBUTANE"s,
"ASSISTEDELECTRIC"s,
"ASSISTEDNATURALGAS"s,
"ASSISTEDPROPANE"s,
"ASSISTEDSTEAM"s,
"STEAMINJECTION"s,
"IfcIdentifier"s,
"IfcIlluminanceMeasure"s,
"IfcImpactProtectionDeviceTypeEnum"s,
"BUMPER"s,
"CRASHCUSHION"s,
"DAMPINGSYSTEM"s,
"FENDER"s,
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
"FURNITUREINVENTORY"s,
"SPACEINVENTORY"s,
"IfcIonConcentrationMeasure"s,
"IfcIsothermalMoistureCapacityMeasure"s,
"IfcJunctionBoxTypeEnum"s,
"POWER"s,
"IfcKerbTypeEnum"s,
"IfcKinematicViscosityMeasure"s,
"IfcKnotType"s,
"PIECEWISE_BEZIER_KNOTS"s,
"QUASI_UNIFORM_KNOTS"s,
"UNIFORM_KNOTS"s,
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
"DIRECTIONSOURCE"s,
"POINTSOURCE"s,
"SECURITYLIGHTING"s,
"IfcLinearForceMeasure"s,
"IfcLinearMomentMeasure"s,
"IfcLinearStiffnessMeasure"s,
"IfcLinearVelocityMeasure"s,
"IfcLiquidTerminalTypeEnum"s,
"LOADINGARM"s,
"IfcLoadGroupTypeEnum"s,
"LOAD_CASE"s,
"LOAD_COMBINATION"s,
"LOAD_GROUP"s,
"IfcLogical"s,
"IfcLogicalOperatorEnum"s,
"LOGICALAND"s,
"LOGICALNOTAND"s,
"LOGICALNOTOR"s,
"LOGICALOR"s,
"LOGICALXOR"s,
"IfcLuminousFluxMeasure"s,
"IfcLuminousIntensityDistributionMeasure"s,
"IfcLuminousIntensityMeasure"s,
"IfcMagneticFluxDensityMeasure"s,
"IfcMagneticFluxMeasure"s,
"IfcMarineFacilityTypeEnum"s,
"BARRIERBEACH"s,
"BREAKWATER"s,
"CANAL"s,
"DRYDOCK"s,
"FLOATINGDOCK"s,
"HYDROLIFT"s,
"JETTY"s,
"LAUNCHRECOVERY"s,
"MARINEDEFENCE"s,
"NAVIGATIONALCHANNEL"s,
"PORT"s,
"QUAY"s,
"REVETMENT"s,
"SHIPLIFT"s,
"SHIPLOCK"s,
"SHIPYARD"s,
"SLIPWAY"s,
"WATERWAY"s,
"WATERWAYSHIPLIFT"s,
"IfcMarinePartTypeEnum"s,
"ABOVEWATERLINE"s,
"ANCHORAGE"s,
"APPROACHCHANNEL"s,
"BELOWWATERLINE"s,
"BERTHINGSTRUCTURE"s,
"CHAMBER"s,
"CILL_LEVEL"s,
"COPELEVEL"s,
"CREST"s,
"GATEHEAD"s,
"GUDINGSTRUCTURE"s,
"HIGHWATERLINE"s,
"LANDFIELD"s,
"LEEWARDSIDE"s,
"LOWWATERLINE"s,
"MANUFACTURING"s,
"NAVIGATIONALAREA"s,
"SHIPTRANSFER"s,
"STORAGEAREA"s,
"VEHICLESERVICING"s,
"WATERFIELD"s,
"WEATHERSIDE"s,
"IfcMassDensityMeasure"s,
"IfcMassFlowRateMeasure"s,
"IfcMassMeasure"s,
"IfcMassPerLengthMeasure"s,
"IfcMechanicalFastenerTypeEnum"s,
"ANCHORBOLT"s,
"BOLT"s,
"CHAIN"s,
"COUPLER"s,
"DOWEL"s,
"NAIL"s,
"NAILPLATE"s,
"RAILFASTENING"s,
"RAILJOINT"s,
"RIVET"s,
"ROPE"s,
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
"ARCH_SEGMENT"s,
"BRACE"s,
"CHORD"s,
"COLLAR"s,
"MEMBER"s,
"MULLION"s,
"PURLIN"s,
"RAFTER"s,
"STAY_CABLE"s,
"STIFFENING_RIB"s,
"STRINGER"s,
"STRUCTURALCABLE"s,
"STRUT"s,
"STUD"s,
"SUSPENDER"s,
"SUSPENSION_CABLE"s,
"TIEBAR"s,
"IfcMobileTelecommunicationsApplianceTypeEnum"s,
"ACCESSPOINT"s,
"BASEBANDUNIT"s,
"BASETRANSCEIVERSTATION"s,
"E_UTRAN_NODE_B"s,
"GATEWAY_GPRS_SUPPORT_NODE"s,
"MASTERUNIT"s,
"MOBILESWITCHINGCENTER"s,
"MSCSERVER"s,
"PACKETCONTROLUNIT"s,
"REMOTERADIOUNIT"s,
"REMOTEUNIT"s,
"SERVICE_GPRS_SUPPORT_NODE"s,
"SUBSCRIBERSERVER"s,
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
"IfcMooringDeviceTypeEnum"s,
"BOLLARD"s,
"LINETENSIONER"s,
"MAGNETICDEVICE"s,
"MOORINGHOOKS"s,
"VACUUMDEVICE"s,
"IfcMotorConnectionTypeEnum"s,
"BELTDRIVE"s,
"COUPLING"s,
"DIRECTDRIVE"s,
"IfcNavigationElementTypeEnum"s,
"BEACON"s,
"BUOY"s,
"IfcNonNegativeLengthMeasure"s,
"IfcNumericMeasure"s,
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
"DATAOUTLET"s,
"POWEROUTLET"s,
"TELEPHONEOUTLET"s,
"IfcPHMeasure"s,
"IfcParameterValue"s,
"IfcPavementTypeEnum"s,
"FLEXIBLE"s,
"RIGID"s,
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
"COHESION"s,
"DRIVEN"s,
"FRICTION"s,
"JETGROUTING"s,
"SUPPORT"s,
"IfcPipeFittingTypeEnum"s,
"IfcPipeSegmentTypeEnum"s,
"GUTTER"s,
"SPOOL"s,
"IfcPlanarForceMeasure"s,
"IfcPlaneAngleMeasure"s,
"IfcPlateTypeEnum"s,
"BASE_PLATE"s,
"COVER_PLATE"s,
"CURTAIN_PANEL"s,
"FLANGE_PLATE"s,
"GUSSET_PLATE"s,
"SHEET"s,
"SPLICE_PLATE"s,
"STIFFENER_PLATE"s,
"WEB_PLATE"s,
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
"AREA"s,
"CURVE"s,
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
"BLISTER"s,
"DEVIATOR"s,
"IfcPropertySetTemplateTypeEnum"s,
"PSET_MATERIALDRIVEN"s,
"PSET_OCCURRENCEDRIVEN"s,
"PSET_PERFORMANCEDRIVEN"s,
"PSET_PROFILEDRIVEN"s,
"PSET_TYPEDRIVENONLY"s,
"PSET_TYPEDRIVENOVERRIDE"s,
"QTO_OCCURRENCEDRIVEN"s,
"QTO_TYPEDRIVENONLY"s,
"QTO_TYPEDRIVENOVERRIDE"s,
"IfcProtectiveDeviceTrippingUnitTypeEnum"s,
"ELECTROMAGNETIC"s,
"ELECTRONIC"s,
"RESIDUALCURRENT"s,
"THERMAL"s,
"IfcProtectiveDeviceTypeEnum"s,
"ANTI_ARCING_DEVICE"s,
"CIRCUITBREAKER"s,
"EARTHINGSWITCH"s,
"EARTHLEAKAGECIRCUITBREAKER"s,
"FUSEDISCONNECTOR"s,
"RESIDUALCURRENTCIRCUITBREAKER"s,
"RESIDUALCURRENTSWITCH"s,
"SPARKGAP"s,
"VARISTOR"s,
"VOLTAGELIMITER"s,
"IfcPumpTypeEnum"s,
"CIRCULATOR"s,
"ENDSUCTION"s,
"SPLITCASE"s,
"SUBMERSIBLEPUMP"s,
"SUMPPUMP"s,
"VERTICALINLINE"s,
"VERTICALTURBINE"s,
"IfcRadioActivityMeasure"s,
"IfcRailTypeEnum"s,
"BLADE"s,
"CHECKRAIL"s,
"GUARDRAIL"s,
"RACKRAIL"s,
"RAIL"s,
"STOCKRAIL"s,
"IfcRailingTypeEnum"s,
"BALUSTRADE"s,
"FENCE"s,
"HANDRAIL"s,
"IfcRailwayPartTypeEnum"s,
"DILATATIONSUPERSTRUCTURE"s,
"LINESIDESTRUCTURE"s,
"LINESIDESTRUCTUREPART"s,
"PLAINTRACKSUPERSTRUCTURE"s,
"TRACKSTRUCTURE"s,
"TRACKSTRUCTUREPART"s,
"TURNOUTSUPERSTRUCTURE"s,
"IfcRailwayTypeEnum"s,
"IfcRampFlightTypeEnum"s,
"SPIRAL"s,
"STRAIGHT"s,
"IfcRampTypeEnum"s,
"HALF_TURN_RAMP"s,
"QUARTER_TURN_RAMP"s,
"SPIRAL_RAMP"s,
"STRAIGHT_RUN_RAMP"s,
"TWO_QUARTER_TURN_RAMP"s,
"TWO_STRAIGHT_RUN_RAMP"s,
"IfcRatioMeasure"s,
"IfcReal"s,
"IfcRecurrenceTypeEnum"s,
"BY_DAY_COUNT"s,
"BY_WEEKDAY_COUNT"s,
"DAILY"s,
"MONTHLY_BY_DAY_OF_MONTH"s,
"MONTHLY_BY_POSITION"s,
"WEEKLY"s,
"YEARLY_BY_DAY_OF_MONTH"s,
"YEARLY_BY_POSITION"s,
"IfcReferentTypeEnum"s,
"BOUNDARY"s,
"KILOPOINT"s,
"LANDMARK"s,
"MILEPOINT"s,
"POSITION"s,
"REFERENCEMARKER"s,
"STATION"s,
"IfcReflectanceMethodEnum"s,
"BLINN"s,
"FLAT"s,
"GLASS"s,
"MATT"s,
"MIRROR"s,
"PHONG"s,
"STRAUSS"s,
"IfcReinforcedSoilTypeEnum"s,
"DYNAMICALLYCOMPACTED"s,
"GROUTED"s,
"REPLACED"s,
"ROLLERCOMPACTED"s,
"SURCHARGEPRELOADED"s,
"VERTICALLYDRAINED"s,
"IfcReinforcingBarRoleEnum"s,
"ANCHORING"s,
"EDGE"s,
"LIGATURE"s,
"MAIN"s,
"PUNCHING"s,
"RING"s,
"SHEAR"s,
"IfcReinforcingBarSurfaceEnum"s,
"PLAIN"s,
"TEXTURED"s,
"IfcReinforcingBarTypeEnum"s,
"SPACEBAR"s,
"IfcReinforcingMeshTypeEnum"s,
"IfcRoadPartTypeEnum"s,
"BICYCLECROSSING"s,
"BUS_STOP"s,
"CARRIAGEWAY"s,
"CENTRALISLAND"s,
"CENTRALRESERVE"s,
"HARDSHOULDER"s,
"LAYBY"s,
"PARKINGBAY"s,
"PASSINGBAY"s,
"PEDESTRIAN_CROSSING"s,
"RAILWAYCROSSING"s,
"REFUGEISLAND"s,
"ROADSEGMENT"s,
"ROADSIDE"s,
"ROADSIDEPART"s,
"ROADWAYPLATEAU"s,
"ROUNDABOUT"s,
"SHOULDER"s,
"SIDEWALK"s,
"SOFTSHOULDER"s,
"TOLLPLAZA"s,
"TRAFFICISLAND"s,
"TRAFFICLANE"s,
"IfcRoadTypeEnum"s,
"IfcRoleEnum"s,
"ARCHITECT"s,
"BUILDINGOPERATOR"s,
"BUILDINGOWNER"s,
"CIVILENGINEER"s,
"CLIENT"s,
"COMMISSIONINGENGINEER"s,
"CONSTRUCTIONMANAGER"s,
"CONSULTANT"s,
"CONTRACTOR"s,
"COSTENGINEER"s,
"ELECTRICALENGINEER"s,
"ENGINEER"s,
"FACILITIESMANAGER"s,
"FIELDCONSTRUCTIONMANAGER"s,
"MANUFACTURER"s,
"MECHANICALENGINEER"s,
"PROJECTMANAGER"s,
"RESELLER"s,
"STRUCTURALENGINEER"s,
"SUBCONTRACTOR"s,
"SUPPLIER"s,
"IfcRoofTypeEnum"s,
"BARREL_ROOF"s,
"BUTTERFLY_ROOF"s,
"DOME_ROOF"s,
"FLAT_ROOF"s,
"FREEFORM"s,
"GABLE_ROOF"s,
"GAMBREL_ROOF"s,
"HIPPED_GABLE_ROOF"s,
"HIP_ROOF"s,
"MANSARD_ROOF"s,
"PAVILION_ROOF"s,
"RAINBOW_ROOF"s,
"SHED_ROOF"s,
"IfcRotationalFrequencyMeasure"s,
"IfcRotationalMassMeasure"s,
"IfcRotationalStiffnessMeasure"s,
"IfcRotationalStiffnessSelect"s,
"IfcSIPrefix"s,
"ATTO"s,
"CENTI"s,
"DECA"s,
"DECI"s,
"EXA"s,
"FEMTO"s,
"GIGA"s,
"HECTO"s,
"KILO"s,
"MEGA"s,
"MICRO"s,
"MILLI"s,
"NANO"s,
"PETA"s,
"PICO"s,
"TERA"s,
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
"SANITARYFOUNTAIN"s,
"SHOWER"s,
"TOILETPAN"s,
"URINAL"s,
"WASHHANDBASIN"s,
"WCSEAT"s,
"IfcSectionModulusMeasure"s,
"IfcSectionTypeEnum"s,
"TAPERED"s,
"UNIFORM"s,
"IfcSectionalAreaIntegralMeasure"s,
"IfcSensorTypeEnum"s,
"CO2SENSOR"s,
"CONDUCTANCESENSOR"s,
"CONTACTSENSOR"s,
"COSENSOR"s,
"EARTHQUAKESENSOR"s,
"FIRESENSOR"s,
"FLOWSENSOR"s,
"FOREIGNOBJECTDETECTIONSENSOR"s,
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
"OBSTACLESENSOR"s,
"PHSENSOR"s,
"PRESSURESENSOR"s,
"RADIATIONSENSOR"s,
"RADIOACTIVITYSENSOR"s,
"RAINSENSOR"s,
"SMOKESENSOR"s,
"SNOWDEPTHSENSOR"s,
"SOUNDSENSOR"s,
"TEMPERATURESENSOR"s,
"TRAINSENSOR"s,
"TURNOUTCLOSURESENSOR"s,
"WHEELSENSOR"s,
"WINDSENSOR"s,
"IfcSequenceEnum"s,
"FINISH_FINISH"s,
"FINISH_START"s,
"START_FINISH"s,
"START_START"s,
"IfcShadingDeviceTypeEnum"s,
"AWNING"s,
"JALOUSIE"s,
"SHUTTER"s,
"IfcShearModulusMeasure"s,
"IfcSignTypeEnum"s,
"MARKER"s,
"PICTORAL"s,
"IfcSignalTypeEnum"s,
"AUDIO"s,
"MIXED"s,
"VISUAL"s,
"IfcSimplePropertyTemplateTypeEnum"s,
"P_BOUNDEDVALUE"s,
"P_ENUMERATEDVALUE"s,
"P_LISTVALUE"s,
"P_REFERENCEVALUE"s,
"P_SINGLEVALUE"s,
"P_TABLEVALUE"s,
"Q_AREA"s,
"Q_COUNT"s,
"Q_LENGTH"s,
"Q_NUMBER"s,
"Q_TIME"s,
"Q_VOLUME"s,
"Q_WEIGHT"s,
"IfcSlabTypeEnum"s,
"APPROACH_SLAB"s,
"BASESLAB"s,
"FLOOR"s,
"LANDING"s,
"ROOF"s,
"TRACKSLAB"s,
"WEARING"s,
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
"BERTH"s,
"GFA"s,
"PARKING"s,
"SPACE"s,
"IfcSpatialZoneTypeEnum"s,
"CONSTRUCTION"s,
"FIRESAFETY"s,
"INTERFERENCE"s,
"OCCUPANCY"s,
"RESERVATION"s,
"IfcSpecificHeatCapacityMeasure"s,
"IfcSpecularExponent"s,
"IfcSpecularRoughness"s,
"IfcStackTerminalTypeEnum"s,
"BIRDCAGE"s,
"COWL"s,
"RAINWATERHOPPER"s,
"IfcStairFlightTypeEnum"s,
"CURVED"s,
"WINDER"s,
"IfcStairTypeEnum"s,
"CURVED_RUN_STAIR"s,
"DOUBLE_RETURN_STAIR"s,
"HALF_TURN_STAIR"s,
"HALF_WINDING_STAIR"s,
"LADDER"s,
"QUARTER_TURN_STAIR"s,
"QUARTER_WINDING_STAIR"s,
"SPIRAL_STAIR"s,
"STRAIGHT_RUN_STAIR"s,
"THREE_QUARTER_TURN_STAIR"s,
"THREE_QUARTER_WINDING_STAIR"s,
"TWO_CURVED_RUN_STAIR"s,
"TWO_QUARTER_TURN_STAIR"s,
"TWO_QUARTER_WINDING_STAIR"s,
"TWO_STRAIGHT_RUN_STAIR"s,
"IfcStateEnum"s,
"LOCKED"s,
"READONLY"s,
"READONLYLOCKED"s,
"READWRITE"s,
"READWRITELOCKED"s,
"IfcStrippedOptional"s,
"IfcStructuralCurveActivityTypeEnum"s,
"CONST"s,
"DISCRETE"s,
"EQUIDISTANT"s,
"PARABOLA"s,
"POLYGONAL"s,
"SINUS"s,
"IfcStructuralCurveMemberTypeEnum"s,
"COMPRESSION_MEMBER"s,
"PIN_JOINED_MEMBER"s,
"RIGID_JOINED_MEMBER"s,
"TENSION_MEMBER"s,
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
"DEFECT"s,
"HATCHMARKING"s,
"LINEMARKING"s,
"MARK"s,
"NONSKIDSURFACING"s,
"PAVEMENTSURFACEMARKING"s,
"RUMBLESTRIP"s,
"SYMBOLMARKING"s,
"TAG"s,
"TRANSVERSERUMBLESTRIP"s,
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
"START_AND_STOP_EQUIPMENT"s,
"SWITCHDISCONNECTOR"s,
"TOGGLESWITCH"s,
"IfcSystemFurnitureElementTypeEnum"s,
"PANEL"s,
"SUBRACK"s,
"WORKSURFACE"s,
"IfcTankTypeEnum"s,
"BASIN"s,
"BREAKPRESSURE"s,
"EXPANSION"s,
"FEEDANDEXPANSION"s,
"OILRETENTIONTRAY"s,
"PRESSUREVESSEL"s,
"STORAGE"s,
"VESSEL"s,
"IfcTaskDurationEnum"s,
"ELAPSEDTIME"s,
"WORKTIME"s,
"IfcTaskTypeEnum"s,
"ADJUSTMENT"s,
"ATTENDANCE"s,
"DEMOLITION"s,
"DISMANTLE"s,
"EMERGENCY"s,
"INSPECTION"s,
"INSTALLATION"s,
"LOGISTIC"s,
"MAINTENANCE"s,
"MOVE"s,
"OPERATION"s,
"REMOVAL"s,
"RENOVATION"s,
"SAFETY"s,
"TESTING"s,
"TROUBLESHOOTING"s,
"IfcTemperatureGradientMeasure"s,
"IfcTemperatureRateOfChangeMeasure"s,
"IfcTendonAnchorTypeEnum"s,
"FIXED_END"s,
"TENSIONING_END"s,
"IfcTendonConduitTypeEnum"s,
"DIABOLO"s,
"GROUTING_DUCT"s,
"TRUMPET"s,
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
"DOWN"s,
"UP"s,
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
"IfcTrackElementTypeEnum"s,
"BLOCKINGDEVICE"s,
"DERAILER"s,
"FROG"s,
"HALF_SET_OF_BLADES"s,
"SLEEPER"s,
"SPEEDREGULATOR"s,
"TRACKENDOFALIGNMENT"s,
"VEHICLESTOP"s,
"IfcTransformerTypeEnum"s,
"CHOPPER"s,
"FREQUENCY"s,
"INVERTER"s,
"RECTIFIER"s,
"VOLTAGE"s,
"IfcTransitionCode"s,
"CONTSAMEGRADIENT"s,
"CONTSAMEGRADIENTSAMECURVATURE"s,
"DISCONTINUOUS"s,
"IfcTranslationalStiffnessSelect"s,
"IfcTransportElementTypeEnum"s,
"CRANEWAY"s,
"ELEVATOR"s,
"ESCALATOR"s,
"HAULINGGEAR"s,
"LIFTINGGEAR"s,
"MOVINGWALKWAY"s,
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
"BASESTATIONCONTROLLER"s,
"CONTROLPANEL"s,
"GASDETECTIONPANEL"s,
"HUMIDISTAT"s,
"INDICATORPANEL"s,
"MIMICPANEL"s,
"THERMOSTAT"s,
"WEATHERSTATION"s,
"IfcUnitaryEquipmentTypeEnum"s,
"AIRCONDITIONINGUNIT"s,
"AIRHANDLER"s,
"DEHUMIDIFIER"s,
"ROOFTOPUNIT"s,
"SPLITSYSTEM"s,
"IfcValveTypeEnum"s,
"AIRRELEASE"s,
"ANTIVACUUM"s,
"CHANGEOVER"s,
"CHECK"s,
"COMMISSIONING"s,
"DIVERTING"s,
"DOUBLECHECK"s,
"DOUBLEREGULATING"s,
"DRAWOFFCOCK"s,
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
"IfcVehicleTypeEnum"s,
"CARGO"s,
"ROLLINGSTOCK"s,
"VEHICLE"s,
"VEHICLEAIR"s,
"VEHICLEMARINE"s,
"VEHICLETRACKED"s,
"VEHICLEWHEELED"s,
"IfcVibrationDamperTypeEnum"s,
"AXIAL_YIELD"s,
"BENDING_YIELD"s,
"RUBBER"s,
"SHEAR_YIELD"s,
"VISCOUS"s,
"IfcVibrationIsolatorTypeEnum"s,
"BASE"s,
"COMPRESSION"s,
"SPRING"s,
"IfcVirtualElementTypeEnum"s,
"CLEARANCE"s,
"IfcVoidingFeatureTypeEnum"s,
"CHAMFER"s,
"CUTOUT"s,
"HOLE"s,
"MITER"s,
"NOTCH"s,
"IfcVolumeMeasure"s,
"IfcVolumetricFlowRateMeasure"s,
"IfcWallTypeEnum"s,
"ELEMENTEDWALL"s,
"MOVABLE"s,
"PARAPET"s,
"PARTITIONING"s,
"PLUMBINGWALL"s,
"RETAININGWALL"s,
"SOLIDWALL"s,
"STANDARD"s,
"WAVEWALL"s,
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
"BOTTOMHUNG"s,
"FIXEDCASEMENT"s,
"OTHEROPERATION"s,
"PIVOTHORIZONTAL"s,
"PIVOTVERTICAL"s,
"REMOVABLECASEMENT"s,
"SIDEHUNGLEFTHAND"s,
"SIDEHUNGRIGHTHAND"s,
"SLIDINGHORIZONTAL"s,
"SLIDINGVERTICAL"s,
"TILTANDTURNLEFTHAND"s,
"TILTANDTURNRIGHTHAND"s,
"TOPHUNG"s,
"IfcWindowPanelPositionEnum"s,
"BOTTOM"s,
"TOP"s,
"IfcWindowTypeEnum"s,
"LIGHTDOME"s,
"SKYLIGHT"s,
"WINDOW"s,
"IfcWindowTypePartitioningEnum"s,
"DOUBLE_PANEL_HORIZONTAL"s,
"DOUBLE_PANEL_VERTICAL"s,
"SINGLE_PANEL"s,
"TRIPLE_PANEL_BOTTOM"s,
"TRIPLE_PANEL_HORIZONTAL"s,
"TRIPLE_PANEL_LEFT"s,
"TRIPLE_PANEL_RIGHT"s,
"TRIPLE_PANEL_TOP"s,
"TRIPLE_PANEL_VERTICAL"s,
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
"IfcAlignmentParameterSegment"s,
"IfcAlignmentVerticalSegment"s,
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
"IfcProductRepresentation"s,
"IfcProfileDef"s,
"IfcProjectedCRS"s,
"IfcPropertyAbstraction"s,
"IfcPropertyEnumeration"s,
"IfcQuantityArea"s,
"IfcQuantityCount"s,
"IfcQuantityLength"s,
"IfcQuantityNumber"s,
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
"IfcTextureCoordinateIndices"s,
"IfcTextureCoordinateIndicesWithVoids"s,
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
"IfcCurveMeasureSelect"s,
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
"IfcSurfaceStyleElementSelect"s,
"IfcUnit"s,
"IfcAlignmentCantSegment"s,
"IfcAlignmentHorizontalSegment"s,
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
"IfcOpenCrossProfileDef"s,
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
"IfcPointByDistanceExpression"s,
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
"IfcSegment"s,
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
"IfcZShapeProfileDef"s,
"IfcClassificationReferenceSelect"s,
"IfcClassificationSelect"s,
"IfcCoordinateReferenceSystemSelect"s,
"IfcDefinitionSelect"s,
"IfcDocumentSelect"s,
"IfcHatchLineDistanceSelect"s,
"IfcMeasureValue"s,
"IfcPointOrVertexPoint"s,
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
"IfcAxis2PlacementLinear"s,
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
"IfcCurveSegment"s,
"IfcDirection"s,
"IfcDirectrixCurveSweptAreaSolid"s,
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
"IfcIndexedPolygonalTextureMap"s,
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
"IfcPolynomialCurve"s,
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
"IfcRelAssociatesProfileDef"s,
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
"IfcRelPositions"s,
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
"IfcSectionedSurface"s,
"IfcSimplePropertyTemplate"s,
"IfcSpatialElement"s,
"IfcSpatialElementType"s,
"IfcSpatialStructureElement"s,
"IfcSpatialStructureElementType"s,
"IfcSpatialZone"s,
"IfcSpatialZoneType"s,
"IfcSphere"s,
"IfcSphericalSurface"s,
"IfcSpiral"s,
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
"IfcThirdOrderPolynomialSpiral"s,
"IfcToroidalSurface"s,
"IfcTransportationDeviceType"s,
"IfcTriangulatedFaceSet"s,
"IfcTriangulatedIrregularNetwork"s,
"IfcVehicleType"s,
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
"IfcBuildingStorey"s,
"IfcBuiltElementType"s,
"IfcChimneyType"s,
"IfcCircleHollowProfileDef"s,
"IfcCivilElementType"s,
"IfcClothoid"s,
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
"IfcCosineSpiral"s,
"IfcCostItem"s,
"IfcCostSchedule"s,
"IfcCourseType"s,
"IfcCoveringType"s,
"IfcCrewResource"s,
"IfcCurtainWallType"s,
"IfcCylindricalSurface"s,
"IfcDeepFoundationType"s,
"IfcDirectrixDerivedReferenceSweptAreaSolid"s,
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
"IfcFacility"s,
"IfcFacilityPart"s,
"IfcFacilityPartCommon"s,
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
"IfcGeotechnicalElement"s,
"IfcGeotechnicalStratum"s,
"IfcGradientCurve"s,
"IfcGroup"s,
"IfcHeatExchangerType"s,
"IfcHumidifierType"s,
"IfcImpactProtectionDevice"s,
"IfcImpactProtectionDeviceType"s,
"IfcIndexedPolyCurve"s,
"IfcInterceptorType"s,
"IfcIntersectionCurve"s,
"IfcInventory"s,
"IfcJunctionBoxType"s,
"IfcKerbType"s,
"IfcLaborResource"s,
"IfcLampType"s,
"IfcLightFixtureType"s,
"IfcLinearElement"s,
"IfcLiquidTerminalType"s,
"IfcMarineFacility"s,
"IfcMarinePart"s,
"IfcMechanicalFastener"s,
"IfcMechanicalFastenerType"s,
"IfcMedicalDeviceType"s,
"IfcMemberType"s,
"IfcMobileTelecommunicationsApplianceType"s,
"IfcMooringDeviceType"s,
"IfcMotorConnectionType"s,
"IfcNavigationElementType"s,
"IfcOccupant"s,
"IfcOpeningElement"s,
"IfcOutletType"s,
"IfcPavementType"s,
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
"IfcRailType"s,
"IfcRailingType"s,
"IfcRailway"s,
"IfcRailwayPart"s,
"IfcRampFlightType"s,
"IfcRampType"s,
"IfcRationalBSplineSurfaceWithKnots"s,
"IfcReferent"s,
"IfcReinforcingElement"s,
"IfcReinforcingElementType"s,
"IfcReinforcingMesh"s,
"IfcReinforcingMeshType"s,
"IfcRelAdheresToElement"s,
"IfcRelAggregates"s,
"IfcRoad"s,
"IfcRoadPart"s,
"IfcRoofType"s,
"IfcSanitaryTerminalType"s,
"IfcSeamCurve"s,
"IfcSecondOrderPolynomialSpiral"s,
"IfcSegmentedReferenceCurve"s,
"IfcSeventhOrderPolynomialSpiral"s,
"IfcShadingDeviceType"s,
"IfcSign"s,
"IfcSignType"s,
"IfcSignalType"s,
"IfcSineSpiral"s,
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
"IfcTendonConduit"s,
"IfcTendonConduitType"s,
"IfcTendonType"s,
"IfcTrackElementType"s,
"IfcTransformerType"s,
"IfcTransportElementType"s,
"IfcTransportationDevice"s,
"IfcTrimmedCurve"s,
"IfcTubeBundleType"s,
"IfcUnitaryEquipmentType"s,
"IfcValveType"s,
"IfcVehicle"s,
"IfcVibrationDamper"s,
"IfcVibrationDamperType"s,
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
"IfcInterferenceSelect"s,
"IfcSpatialReferenceSelect"s,
"IfcStructuralActivityAssignmentSelect"s,
"IfcActionRequest"s,
"IfcAirTerminalBoxType"s,
"IfcAirTerminalType"s,
"IfcAirToAirHeatRecoveryType"s,
"IfcAlignmentCant"s,
"IfcAlignmentHorizontal"s,
"IfcAlignmentSegment"s,
"IfcAlignmentVertical"s,
"IfcAsset"s,
"IfcAudioVisualApplianceType"s,
"IfcBSplineCurve"s,
"IfcBSplineCurveWithKnots"s,
"IfcBeamType"s,
"IfcBearingType"s,
"IfcBoilerType"s,
"IfcBoundaryCurve"s,
"IfcBridge"s,
"IfcBridgePart"s,
"IfcBuilding"s,
"IfcBuildingElementPart"s,
"IfcBuildingElementPartType"s,
"IfcBuildingElementProxyType"s,
"IfcBuildingSystem"s,
"IfcBuiltElement"s,
"IfcBuiltSystem"s,
"IfcBurnerType"s,
"IfcCableCarrierFittingType"s,
"IfcCableCarrierSegmentType"s,
"IfcCableFittingType"s,
"IfcCableSegmentType"s,
"IfcCaissonFoundationType"s,
"IfcChillerType"s,
"IfcChimney"s,
"IfcCircle"s,
"IfcCivilElement"s,
"IfcCoilType"s,
"IfcColumn"s,
"IfcCommunicationsApplianceType"s,
"IfcCompressorType"s,
"IfcCondenserType"s,
"IfcConstructionEquipmentResource"s,
"IfcConstructionMaterialResource"s,
"IfcConstructionProductResource"s,
"IfcConveyorSegmentType"s,
"IfcCooledBeamType"s,
"IfcCoolingTowerType"s,
"IfcCourse"s,
"IfcCovering"s,
"IfcCurtainWall"s,
"IfcDamperType"s,
"IfcDeepFoundation"s,
"IfcDiscreteAccessory"s,
"IfcDiscreteAccessoryType"s,
"IfcDistributionBoardType"s,
"IfcDistributionChamberElementType"s,
"IfcDistributionControlElementType"s,
"IfcDistributionElement"s,
"IfcDistributionFlowElement"s,
"IfcDistributionPort"s,
"IfcDistributionSystem"s,
"IfcDoor"s,
"IfcDuctFittingType"s,
"IfcDuctSegmentType"s,
"IfcDuctSilencerType"s,
"IfcEarthworksCut"s,
"IfcEarthworksElement"s,
"IfcEarthworksFill"s,
"IfcElectricApplianceType"s,
"IfcElectricDistributionBoardType"s,
"IfcElectricFlowStorageDeviceType"s,
"IfcElectricFlowTreatmentDeviceType"s,
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
"IfcGeotechnicalAssembly"s,
"IfcGrid"s,
"IfcHeatExchanger"s,
"IfcHumidifier"s,
"IfcInterceptor"s,
"IfcJunctionBox"s,
"IfcKerb"s,
"IfcLamp"s,
"IfcLightFixture"s,
"IfcLinearPositioningElement"s,
"IfcLiquidTerminal"s,
"IfcMedicalDevice"s,
"IfcMember"s,
"IfcMobileTelecommunicationsAppliance"s,
"IfcMooringDevice"s,
"IfcMotorConnection"s,
"IfcNavigationElement"s,
"IfcOuterBoundaryCurve"s,
"IfcOutlet"s,
"IfcPavement"s,
"IfcPile"s,
"IfcPipeFitting"s,
"IfcPipeSegment"s,
"IfcPlate"s,
"IfcProtectiveDevice"s,
"IfcProtectiveDeviceTrippingUnitType"s,
"IfcPump"s,
"IfcRail"s,
"IfcRailing"s,
"IfcRamp"s,
"IfcRampFlight"s,
"IfcRationalBSplineCurveWithKnots"s,
"IfcReinforcedSoil"s,
"IfcReinforcingBar"s,
"IfcReinforcingBarType"s,
"IfcRoof"s,
"IfcSanitaryTerminal"s,
"IfcSensorType"s,
"IfcShadingDevice"s,
"IfcSignal"s,
"IfcSlab"s,
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
"IfcTrackElement"s,
"IfcTransformer"s,
"IfcTransportElement"s,
"IfcTubeBundle"s,
"IfcUnitaryControlElementType"s,
"IfcUnitaryEquipment"s,
"IfcValve"s,
"IfcWall"s,
"IfcWallStandardCase"s,
"IfcWasteTerminal"s,
"IfcWindow"s,
"IfcSpaceBoundarySelect"s,
"IfcActuatorType"s,
"IfcAirTerminal"s,
"IfcAirTerminalBox"s,
"IfcAirToAirHeatRecovery"s,
"IfcAlarmType"s,
"IfcAlignment"s,
"IfcAudioVisualAppliance"s,
"IfcBeam"s,
"IfcBearing"s,
"IfcBoiler"s,
"IfcBorehole"s,
"IfcBuildingElementProxy"s,
"IfcBurner"s,
"IfcCableCarrierFitting"s,
"IfcCableCarrierSegment"s,
"IfcCableFitting"s,
"IfcCableSegment"s,
"IfcCaissonFoundation"s,
"IfcChiller"s,
"IfcCoil"s,
"IfcCommunicationsAppliance"s,
"IfcCompressor"s,
"IfcCondenser"s,
"IfcControllerType"s,
"IfcConveyorSegment"s,
"IfcCooledBeam"s,
"IfcCoolingTower"s,
"IfcDamper"s,
"IfcDistributionBoard"s,
"IfcDistributionChamberElement"s,
"IfcDistributionCircuit"s,
"IfcDistributionControlElement"s,
"IfcDuctFitting"s,
"IfcDuctSegment"s,
"IfcDuctSilencer"s,
"IfcElectricAppliance"s,
"IfcElectricDistributionBoard"s,
"IfcElectricFlowStorageDevice"s,
"IfcElectricFlowTreatmentDevice"s,
"IfcElectricGenerator"s,
"IfcElectricMotor"s,
"IfcElectricTimeControl"s,
"IfcFan"s,
"IfcFilter"s,
"IfcFireSuppressionTerminal"s,
"IfcFlowInstrument"s,
"IfcGeomodel"s,
"IfcGeoslice"s,
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
"RailHeadDistance"s,
"StartDistAlong"s,
"HorizontalLength"s,
"StartCantLeft"s,
"EndCantLeft"s,
"StartCantRight"s,
"EndCantRight"s,
"StartPoint"s,
"StartDirection"s,
"StartRadiusOfCurvature"s,
"EndRadiusOfCurvature"s,
"SegmentLength"s,
"GravityCenterLineHeight"s,
"StartTag"s,
"EndTag"s,
"DesignParameters"s,
"StartHeight"s,
"StartGradient"s,
"EndGradient"s,
"RadiusOfCurvature"s,
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
"Radius"s,
"Source"s,
"Edition"s,
"EditionDate"s,
"Specification"s,
"ReferenceTokens"s,
"ReferencedSource"s,
"Sort"s,
"ClothoidConstant"s,
"Red"s,
"Green"s,
"Blue"s,
"ColourList"s,
"UsageName"s,
"HasProperties"s,
"TemplateType"s,
"HasPropertyTemplates"s,
"Segments"s,
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
"CosineTerm"s,
"ConstantTerm"s,
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
"Placement"s,
"SegmentStart"s,
"CurveFont"s,
"CurveWidth"s,
"CurveColour"s,
"ModelOrDraughting"s,
"PatternList"s,
"CurveStyleFont"s,
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
"Directrix"s,
"StartParam"s,
"EndParam"s,
"FlowDirection"s,
"SystemType"s,
"Location"s,
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
"ParameterTakesPrecedence"s,
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
"UsageType"s,
"TensionFailureX"s,
"TensionFailureY"s,
"TensionFailureZ"s,
"CompressionFailureX"s,
"CompressionFailureY"s,
"CompressionFailureZ"s,
"FillStyles"s,
"HatchLineAppearance"s,
"StartOfNextHatchLine"s,
"PointOfReferenceHatchLine"s,
"PatternStart"s,
"HatchLineAngle"s,
"TilingPattern"s,
"Tiles"s,
"TilingScale"s,
"FixedReference"s,
"CoordinateSpaceDimension"s,
"Precision"s,
"WorldCoordinateSystem"s,
"TrueNorth"s,
"ParentContext"s,
"TargetScale"s,
"TargetView"s,
"UserDefinedTargetView"s,
"BaseCurve"s,
"EndPoint"s,
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
"TexCoordIndices"s,
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
"RelativePlacement"s,
"CartesianPosition"s,
"Outer"s,
"Eastings"s,
"Northings"s,
"OrthogonalHeight"s,
"XAxisAbscissa"s,
"XAxisOrdinate"s,
"ScaleY"s,
"ScaleZ"s,
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
"MaterialExpression"s,
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
"PlacementRelTo"s,
"BenchmarkValues"s,
"LogicalAggregator"s,
"ObjectiveQualifier"s,
"UserDefinedQualifier"s,
"BasisCurve"s,
"Distance"s,
"HorizontalWidths"s,
"Widths"s,
"Slopes"s,
"Tags"s,
"OffsetPoint"s,
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
"ConstructionType"s,
"Height"s,
"ColourComponents"s,
"Pixel"s,
"SizeInX"s,
"SizeInY"s,
"DistanceAlong"s,
"OffsetLateral"s,
"OffsetVertical"s,
"OffsetLongitudinal"s,
"PointParameter"s,
"PointParameterU"s,
"PointParameterV"s,
"Polygon"s,
"PolygonalBoundary"s,
"Closed"s,
"Faces"s,
"PnIndex"s,
"CoefficientsX"s,
"CoefficientsY"s,
"CoefficientsZ"s,
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
"Expression"s,
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
"AreaValue"s,
"Formula"s,
"CountValue"s,
"LengthValue"s,
"NumberValue"s,
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
"RelatingElement"s,
"RelatedSurfaceFeatures"s,
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
"RelatingProfileDef"s,
"ConnectionGeometry"s,
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
"InterferenceSpace"s,
"RelatingPositioningElement"s,
"RelatedProducts"s,
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
"QuadraticTerm"s,
"LinearTerm"s,
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
"SpineCurve"s,
"Transition"s,
"SepticTerm"s,
"SexticTerm"s,
"QuinticTerm"s,
"QuarticTerm"s,
"CubicTerm"s,
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
"SineTerm"s,
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
"AxisDirection"s,
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
"Styles"s,
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
"TexCoordsOf"s,
"InnerTexCoordIndices"s,
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
"StartDate"s,
"FinishDate"s,
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
"HasOpenings"s,
"IsConnectionRealization"s,
"ProvidesBoundaries"s,
"ConnectedFrom"s,
"HasCoverings"s,
"HasSurfaceFeatures"s,
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
"ReferencedInStructures"s,
"ToFaceSet"s,
"HasTexCoords"s,
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
"Positions"s,
"IsPredecessorTo"s,
"IsSuccessorFrom"s,
"OperatesOn"s,
"ReferencedBy"s,
"PositionedRelativeTo"s,
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
"UsingCurves"s,
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
"AdheresToElement"s,
"IsMappedBy"s,
"UsedInStyles"s,
"ServicesBuildings"s,
"ServicesFacilities"s,
"HasColours"s,
"HasTextures"s,
"ToTexMap"s,
"Types"s,
"IFC4X3_TC1"s};

#if defined(__clang__)
__attribute__((optnone))
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC4X3_TC1_populate_schema() {
    IFC4X3_TC1_IfcAbsorbedDoseMeasure_type = new type_declaration(strings[0], 0, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcAccelerationMeasure_type = new type_declaration(strings[1], 1, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcActionRequestTypeEnum_type = new enumeration_type(strings[2], 3, {
        strings[3],
        strings[4],
        strings[5],
        strings[6],
        strings[7],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcActionSourceTypeEnum_type = new enumeration_type(strings[10], 4, {
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
    IFC4X3_TC1_IfcActionTypeEnum_type = new enumeration_type(strings[36], 5, {
        strings[37],
        strings[38],
        strings[39],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcActuatorTypeEnum_type = new enumeration_type(strings[40], 11, {
        strings[41],
        strings[42],
        strings[43],
        strings[44],
        strings[45],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcAddressTypeEnum_type = new enumeration_type(strings[46], 13, {
        strings[47],
        strings[48],
        strings[49],
        strings[50],
        strings[8]
    });
    IFC4X3_TC1_IfcAirTerminalBoxTypeEnum_type = new enumeration_type(strings[51], 20, {
        strings[52],
        strings[53],
        strings[54],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcAirTerminalTypeEnum_type = new enumeration_type(strings[55], 22, {
        strings[56],
        strings[57],
        strings[58],
        strings[59],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type(strings[60], 25, {
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
    IFC4X3_TC1_IfcAlarmTypeEnum_type = new enumeration_type(strings[70], 28, {
        strings[71],
        strings[72],
        strings[73],
        strings[74],
        strings[75],
        strings[76],
        strings[77],
        strings[78],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcAlignmentCantSegmentTypeEnum_type = new enumeration_type(strings[79], 32, {
        strings[80],
        strings[81],
        strings[82],
        strings[83],
        strings[84],
        strings[85],
        strings[86]
    });
    IFC4X3_TC1_IfcAlignmentHorizontalSegmentTypeEnum_type = new enumeration_type(strings[87], 35, {
        strings[80],
        strings[88],
        strings[89],
        strings[82],
        strings[90],
        strings[83],
        strings[91],
        strings[85],
        strings[86]
    });
    IFC4X3_TC1_IfcAlignmentTypeEnum_type = new enumeration_type(strings[92], 38, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcAlignmentVerticalSegmentTypeEnum_type = new enumeration_type(strings[93], 41, {
        strings[88],
        strings[89],
        strings[94],
        strings[95]
    });
    IFC4X3_TC1_IfcAmountOfSubstanceMeasure_type = new type_declaration(strings[96], 42, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcAnalysisModelTypeEnum_type = new enumeration_type(strings[97], 43, {
        strings[98],
        strings[99],
        strings[100],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcAnalysisTheoryTypeEnum_type = new enumeration_type(strings[101], 44, {
        strings[102],
        strings[103],
        strings[104],
        strings[105],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcAngularVelocityMeasure_type = new type_declaration(strings[106], 45, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcAnnotationTypeEnum_type = new enumeration_type(strings[107], 48, {
        strings[108],
        strings[109],
        strings[110],
        strings[111],
        strings[112],
        strings[113],
        strings[114],
        strings[115],
        strings[116],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcAreaDensityMeasure_type = new type_declaration(strings[117], 58, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcAreaMeasure_type = new type_declaration(strings[118], 59, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcArithmeticOperatorEnum_type = new enumeration_type(strings[119], 60, {
        strings[120],
        strings[121],
        strings[122],
        strings[123]
    });
    IFC4X3_TC1_IfcAssemblyPlaceEnum_type = new enumeration_type(strings[124], 61, {
        strings[125],
        strings[50],
        strings[9]
    });
    IFC4X3_TC1_IfcAudioVisualApplianceTypeEnum_type = new enumeration_type(strings[126], 66, {
        strings[127],
        strings[128],
        strings[129],
        strings[130],
        strings[131],
        strings[132],
        strings[133],
        strings[134],
        strings[135],
        strings[136],
        strings[137],
        strings[138],
        strings[139],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBSplineCurveForm_type = new enumeration_type(strings[140], 108, {
        strings[141],
        strings[142],
        strings[143],
        strings[144],
        strings[145],
        strings[146]
    });
    IFC4X3_TC1_IfcBSplineSurfaceForm_type = new enumeration_type(strings[147], 111, {
        strings[148],
        strings[149],
        strings[150],
        strings[151],
        strings[152],
        strings[153],
        strings[154],
        strings[155],
        strings[156],
        strings[157],
        strings[146]
    });
    IFC4X3_TC1_IfcBeamTypeEnum_type = new enumeration_type(strings[158], 74, {
        strings[159],
        strings[160],
        strings[161],
        strings[162],
        strings[163],
        strings[164],
        strings[165],
        strings[166],
        strings[167],
        strings[168],
        strings[169],
        strings[170],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBearingTypeEnum_type = new enumeration_type(strings[171], 77, {
        strings[172],
        strings[173],
        strings[174],
        strings[175],
        strings[176],
        strings[177],
        strings[178],
        strings[179],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBenchmarkEnum_type = new enumeration_type(strings[180], 78, {
        strings[181],
        strings[182],
        strings[183],
        strings[184],
        strings[185],
        strings[186],
        strings[187],
        strings[188],
        strings[189],
        strings[190]
    });
    IFC4X3_TC1_IfcBinary_type = new type_declaration(strings[191], 80, new simple_type(simple_type::binary_type));
    IFC4X3_TC1_IfcBoilerTypeEnum_type = new enumeration_type(strings[192], 85, {
        strings[193],
        strings[194],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBoolean_type = new type_declaration(strings[195], 86, new simple_type(simple_type::boolean_type));
    IFC4X3_TC1_IfcBooleanOperator_type = new enumeration_type(strings[196], 89, {
        strings[197],
        strings[198],
        strings[199]
    });
    IFC4X3_TC1_IfcBridgePartTypeEnum_type = new enumeration_type(strings[200], 105, {
        strings[201],
        strings[202],
        strings[203],
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
    IFC4X3_TC1_IfcBridgeTypeEnum_type = new enumeration_type(strings[211], 106, {
        strings[212],
        strings[213],
        strings[214],
        strings[215],
        strings[216],
        strings[217],
        strings[218],
        strings[219],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBuildingElementPartTypeEnum_type = new enumeration_type(strings[220], 116, {
        strings[221],
        strings[222],
        strings[223],
        strings[224],
        strings[225],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBuildingElementProxyTypeEnum_type = new enumeration_type(strings[226], 119, {
        strings[227],
        strings[228],
        strings[229],
        strings[230],
        strings[231],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBuildingSystemTypeEnum_type = new enumeration_type(strings[232], 122, {
        strings[233],
        strings[204],
        strings[234],
        strings[235],
        strings[236],
        strings[33],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBuiltSystemTypeEnum_type = new enumeration_type(strings[237], 126, {
        strings[238],
        strings[233],
        strings[204],
        strings[234],
        strings[239],
        strings[235],
        strings[240],
        strings[241],
        strings[242],
        strings[243],
        strings[236],
        strings[244],
        strings[33],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcBurnerTypeEnum_type = new enumeration_type(strings[245], 129, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCableCarrierFittingTypeEnum_type = new enumeration_type(strings[246], 132, {
        strings[247],
        strings[248],
        strings[249],
        strings[250],
        strings[251],
        strings[252],
        strings[253],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCableCarrierSegmentTypeEnum_type = new enumeration_type(strings[254], 135, {
        strings[255],
        strings[256],
        strings[257],
        strings[258],
        strings[259],
        strings[260],
        strings[261],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCableFittingTypeEnum_type = new enumeration_type(strings[262], 138, {
        strings[248],
        strings[263],
        strings[264],
        strings[265],
        strings[250],
        strings[253],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCableSegmentTypeEnum_type = new enumeration_type(strings[266], 141, {
        strings[267],
        strings[268],
        strings[269],
        strings[270],
        strings[271],
        strings[272],
        strings[273],
        strings[274],
        strings[275],
        strings[276],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCaissonFoundationTypeEnum_type = new enumeration_type(strings[277], 144, {
        strings[278],
        strings[279],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCardinalPointReference_type = new type_declaration(strings[280], 145, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcChangeActionEnum_type = new enumeration_type(strings[281], 156, {
        strings[282],
        strings[283],
        strings[284],
        strings[285],
        strings[9]
    });
    IFC4X3_TC1_IfcChillerTypeEnum_type = new enumeration_type(strings[286], 159, {
        strings[287],
        strings[288],
        strings[289],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcChimneyTypeEnum_type = new enumeration_type(strings[290], 162, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCoilTypeEnum_type = new enumeration_type(strings[291], 176, {
        strings[292],
        strings[293],
        strings[294],
        strings[295],
        strings[296],
        strings[297],
        strings[298],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcColumnTypeEnum_type = new enumeration_type(strings[299], 184, {
        strings[300],
        strings[301],
        strings[302],
        strings[303],
        strings[304],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCommunicationsApplianceTypeEnum_type = new enumeration_type(strings[305], 187, {
        strings[306],
        strings[307],
        strings[308],
        strings[4],
        strings[309],
        strings[310],
        strings[311],
        strings[312],
        strings[313],
        strings[314],
        strings[315],
        strings[316],
        strings[317],
        strings[318],
        strings[319],
        strings[320],
        strings[321],
        strings[322],
        strings[323],
        strings[324],
        strings[325],
        strings[326],
        strings[327],
        strings[328],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcComplexNumber_type = new type_declaration(strings[329], 188, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IFC4X3_TC1_IfcComplexPropertyTemplateTypeEnum_type = new enumeration_type(strings[330], 191, {
        strings[331],
        strings[332]
    });
    IFC4X3_TC1_IfcCompoundPlaneAngleMeasure_type = new type_declaration(strings[333], 196, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
    IFC4X3_TC1_IfcCompressorTypeEnum_type = new enumeration_type(strings[334], 199, {
        strings[335],
        strings[336],
        strings[337],
        strings[338],
        strings[339],
        strings[340],
        strings[341],
        strings[342],
        strings[343],
        strings[344],
        strings[345],
        strings[346],
        strings[347],
        strings[348],
        strings[349],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCondenserTypeEnum_type = new enumeration_type(strings[350], 202, {
        strings[287],
        strings[351],
        strings[289],
        strings[352],
        strings[353],
        strings[354],
        strings[355],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcConnectionTypeEnum_type = new enumeration_type(strings[356], 210, {
        strings[357],
        strings[358],
        strings[359],
        strings[9]
    });
    IFC4X3_TC1_IfcConstraintEnum_type = new enumeration_type(strings[360], 213, {
        strings[361],
        strings[362],
        strings[363],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcConstructionEquipmentResourceTypeEnum_type = new enumeration_type(strings[364], 216, {
        strings[365],
        strings[366],
        strings[367],
        strings[368],
        strings[369],
        strings[370],
        strings[371],
        strings[372],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcConstructionMaterialResourceTypeEnum_type = new enumeration_type(strings[373], 219, {
        strings[374],
        strings[375],
        strings[376],
        strings[377],
        strings[378],
        strings[379],
        strings[380],
        strings[381],
        strings[382],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcConstructionProductResourceTypeEnum_type = new enumeration_type(strings[383], 222, {
        strings[384],
        strings[385],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcContextDependentMeasure_type = new type_declaration(strings[386], 226, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcControllerTypeEnum_type = new enumeration_type(strings[387], 231, {
        strings[388],
        strings[389],
        strings[390],
        strings[391],
        strings[392],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcConveyorSegmentTypeEnum_type = new enumeration_type(strings[393], 236, {
        strings[394],
        strings[395],
        strings[396],
        strings[397],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCooledBeamTypeEnum_type = new enumeration_type(strings[398], 239, {
        strings[399],
        strings[400],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCoolingTowerTypeEnum_type = new enumeration_type(strings[401], 242, {
        strings[402],
        strings[403],
        strings[404],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCostItemTypeEnum_type = new enumeration_type(strings[405], 248, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCostScheduleTypeEnum_type = new enumeration_type(strings[406], 250, {
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
    IFC4X3_TC1_IfcCountMeasure_type = new type_declaration(strings[414], 252, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcCourseTypeEnum_type = new enumeration_type(strings[415], 255, {
        strings[416],
        strings[417],
        strings[418],
        strings[419],
        strings[420],
        strings[421],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCoveringTypeEnum_type = new enumeration_type(strings[422], 258, {
        strings[423],
        strings[424],
        strings[425],
        strings[426],
        strings[223],
        strings[427],
        strings[428],
        strings[429],
        strings[430],
        strings[431],
        strings[432],
        strings[433],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCrewResourceTypeEnum_type = new enumeration_type(strings[434], 261, {
        strings[49],
        strings[50],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCurtainWallTypeEnum_type = new enumeration_type(strings[435], 269, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcCurvatureMeasure_type = new type_declaration(strings[436], 270, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcCurveInterpolationEnum_type = new enumeration_type(strings[437], 275, {
        strings[438],
        strings[439],
        strings[440],
        strings[9]
    });
    IFC4X3_TC1_IfcDamperTypeEnum_type = new enumeration_type(strings[441], 288, {
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
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDataOriginEnum_type = new enumeration_type(strings[453], 289, {
        strings[454],
        strings[455],
        strings[456],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDate_type = new type_declaration(strings[457], 290, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcDateTime_type = new type_declaration(strings[458], 291, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcDayInMonthNumber_type = new type_declaration(strings[459], 292, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcDayInWeekNumber_type = new type_declaration(strings[460], 293, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcDerivedUnitEnum_type = new enumeration_type(strings[461], 301, {
        strings[462],
        strings[463],
        strings[464],
        strings[465],
        strings[466],
        strings[467],
        strings[468],
        strings[469],
        strings[470],
        strings[471],
        strings[472],
        strings[473],
        strings[474],
        strings[475],
        strings[476],
        strings[477],
        strings[478],
        strings[479],
        strings[480],
        strings[481],
        strings[482],
        strings[483],
        strings[484],
        strings[485],
        strings[486],
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
        strings[501],
        strings[502],
        strings[503],
        strings[504],
        strings[505],
        strings[506],
        strings[507],
        strings[508],
        strings[509],
        strings[510],
        strings[511],
        strings[512],
        strings[513],
        strings[8]
    });
    IFC4X3_TC1_IfcDescriptiveMeasure_type = new type_declaration(strings[514], 302, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcDimensionCount_type = new type_declaration(strings[515], 304, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcDirectionSenseEnum_type = new enumeration_type(strings[516], 306, {
        strings[517],
        strings[518]
    });
    IFC4X3_TC1_IfcDiscreteAccessoryTypeEnum_type = new enumeration_type(strings[519], 311, {
        strings[520],
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
        strings[537],
        strings[538],
        strings[539],
        strings[540],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDistributionBoardTypeEnum_type = new enumeration_type(strings[541], 314, {
        strings[542],
        strings[543],
        strings[544],
        strings[545],
        strings[546],
        strings[547],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDistributionChamberElementTypeEnum_type = new enumeration_type(strings[548], 317, {
        strings[549],
        strings[550],
        strings[551],
        strings[552],
        strings[553],
        strings[554],
        strings[555],
        strings[556],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDistributionPortTypeEnum_type = new enumeration_type(strings[557], 326, {
        strings[558],
        strings[559],
        strings[560],
        strings[561],
        strings[562],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDistributionSystemEnum_type = new enumeration_type(strings[563], 328, {
        strings[564],
        strings[565],
        strings[566],
        strings[567],
        strings[568],
        strings[569],
        strings[570],
        strings[571],
        strings[572],
        strings[573],
        strings[574],
        strings[575],
        strings[576],
        strings[577],
        strings[578],
        strings[579],
        strings[580],
        strings[581],
        strings[582],
        strings[583],
        strings[584],
        strings[377],
        strings[585],
        strings[586],
        strings[368],
        strings[369],
        strings[587],
        strings[588],
        strings[589],
        strings[590],
        strings[591],
        strings[592],
        strings[593],
        strings[594],
        strings[595],
        strings[596],
        strings[597],
        strings[598],
        strings[599],
        strings[600],
        strings[601],
        strings[602],
        strings[138],
        strings[603],
        strings[604],
        strings[605],
        strings[606],
        strings[607],
        strings[608],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDocumentConfidentialityEnum_type = new enumeration_type(strings[609], 329, {
        strings[610],
        strings[611],
        strings[612],
        strings[613],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDocumentStatusEnum_type = new enumeration_type(strings[614], 334, {
        strings[615],
        strings[616],
        strings[617],
        strings[618],
        strings[9]
    });
    IFC4X3_TC1_IfcDoorPanelOperationEnum_type = new enumeration_type(strings[619], 337, {
        strings[620],
        strings[621],
        strings[622],
        strings[623],
        strings[624],
        strings[625],
        strings[626],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDoorPanelPositionEnum_type = new enumeration_type(strings[627], 338, {
        strings[628],
        strings[629],
        strings[630],
        strings[9]
    });
    IFC4X3_TC1_IfcDoorTypeEnum_type = new enumeration_type(strings[631], 341, {
        strings[632],
        strings[633],
        strings[634],
        strings[635],
        strings[636],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDoorTypeOperationEnum_type = new enumeration_type(strings[637], 342, {
        strings[638],
        strings[639],
        strings[640],
        strings[641],
        strings[642],
        strings[643],
        strings[644],
        strings[645],
        strings[646],
        strings[647],
        strings[648],
        strings[649],
        strings[650],
        strings[651],
        strings[623],
        strings[652],
        strings[624],
        strings[653],
        strings[654],
        strings[655],
        strings[656],
        strings[657],
        strings[658],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDoseEquivalentMeasure_type = new type_declaration(strings[659], 343, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcDuctFittingTypeEnum_type = new enumeration_type(strings[660], 348, {
        strings[247],
        strings[248],
        strings[263],
        strings[264],
        strings[250],
        strings[661],
        strings[253],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDuctSegmentTypeEnum_type = new enumeration_type(strings[662], 351, {
        strings[663],
        strings[664],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDuctSilencerTypeEnum_type = new enumeration_type(strings[665], 354, {
        strings[666],
        strings[667],
        strings[668],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcDuration_type = new type_declaration(strings[669], 355, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcDynamicViscosityMeasure_type = new type_declaration(strings[670], 356, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcEarthworksCutTypeEnum_type = new enumeration_type(strings[671], 358, {
        strings[672],
        strings[673],
        strings[674],
        strings[675],
        strings[676],
        strings[677],
        strings[678],
        strings[679],
        strings[555],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcEarthworksFillTypeEnum_type = new enumeration_type(strings[680], 361, {
        strings[681],
        strings[682],
        strings[683],
        strings[684],
        strings[685],
        strings[686],
        strings[687],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElectricApplianceTypeEnum_type = new enumeration_type(strings[688], 367, {
        strings[689],
        strings[690],
        strings[691],
        strings[692],
        strings[693],
        strings[694],
        strings[695],
        strings[696],
        strings[697],
        strings[698],
        strings[699],
        strings[700],
        strings[701],
        strings[702],
        strings[703],
        strings[704],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElectricCapacitanceMeasure_type = new type_declaration(strings[705], 368, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcElectricChargeMeasure_type = new type_declaration(strings[706], 369, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcElectricConductanceMeasure_type = new type_declaration(strings[707], 370, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcElectricCurrentMeasure_type = new type_declaration(strings[708], 371, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcElectricDistributionBoardTypeEnum_type = new enumeration_type(strings[709], 374, {
        strings[542],
        strings[544],
        strings[546],
        strings[547],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type(strings[710], 377, {
        strings[711],
        strings[712],
        strings[713],
        strings[714],
        strings[715],
        strings[716],
        strings[717],
        strings[718],
        strings[719],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElectricFlowTreatmentDeviceTypeEnum_type = new enumeration_type(strings[720], 380, {
        strings[721],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElectricGeneratorTypeEnum_type = new enumeration_type(strings[722], 383, {
        strings[723],
        strings[724],
        strings[725],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElectricMotorTypeEnum_type = new enumeration_type(strings[726], 386, {
        strings[727],
        strings[728],
        strings[729],
        strings[730],
        strings[731],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElectricResistanceMeasure_type = new type_declaration(strings[732], 387, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcElectricTimeControlTypeEnum_type = new enumeration_type(strings[733], 390, {
        strings[734],
        strings[735],
        strings[736],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElectricVoltageMeasure_type = new type_declaration(strings[737], 391, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcElementAssemblyTypeEnum_type = new enumeration_type(strings[738], 396, {
        strings[201],
        strings[739],
        strings[740],
        strings[741],
        strings[742],
        strings[743],
        strings[202],
        strings[744],
        strings[745],
        strings[217],
        strings[746],
        strings[747],
        strings[205],
        strings[207],
        strings[748],
        strings[749],
        strings[750],
        strings[751],
        strings[752],
        strings[753],
        strings[754],
        strings[755],
        strings[756],
        strings[757],
        strings[758],
        strings[759],
        strings[219],
        strings[760],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcElementCompositionEnum_type = new enumeration_type(strings[761], 399, {
        strings[227],
        strings[228],
        strings[229]
    });
    IFC4X3_TC1_IfcEnergyMeasure_type = new type_declaration(strings[762], 406, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcEngineTypeEnum_type = new enumeration_type(strings[763], 409, {
        strings[764],
        strings[765],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcEvaporativeCoolerTypeEnum_type = new enumeration_type(strings[766], 412, {
        strings[767],
        strings[768],
        strings[769],
        strings[770],
        strings[771],
        strings[772],
        strings[773],
        strings[774],
        strings[775],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcEvaporatorTypeEnum_type = new enumeration_type(strings[776], 415, {
        strings[777],
        strings[778],
        strings[779],
        strings[780],
        strings[781],
        strings[782],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcEventTriggerTypeEnum_type = new enumeration_type(strings[783], 418, {
        strings[784],
        strings[785],
        strings[786],
        strings[787],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcEventTypeEnum_type = new enumeration_type(strings[788], 420, {
        strings[789],
        strings[790],
        strings[791],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcExternalSpatialElementTypeEnum_type = new enumeration_type(strings[792], 429, {
        strings[793],
        strings[794],
        strings[795],
        strings[796],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcFacilityPartCommonTypeEnum_type = new enumeration_type(strings[797], 443, {
        strings[798],
        strings[799],
        strings[250],
        strings[800],
        strings[801],
        strings[208],
        strings[209],
        strings[802],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcFacilityUsageEnum_type = new enumeration_type(strings[803], 444, {
        strings[804],
        strings[805],
        strings[806],
        strings[807],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcFanTypeEnum_type = new enumeration_type(strings[808], 448, {
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
    IFC4X3_TC1_IfcFastenerTypeEnum_type = new enumeration_type(strings[816], 451, {
        strings[817],
        strings[818],
        strings[819],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcFilterTypeEnum_type = new enumeration_type(strings[820], 461, {
        strings[821],
        strings[822],
        strings[823],
        strings[824],
        strings[825],
        strings[826],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type(strings[827], 464, {
        strings[828],
        strings[829],
        strings[830],
        strings[831],
        strings[832],
        strings[833],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcFlowDirectionEnum_type = new enumeration_type(strings[834], 468, {
        strings[835],
        strings[836],
        strings[837],
        strings[9]
    });
    IFC4X3_TC1_IfcFlowInstrumentTypeEnum_type = new enumeration_type(strings[838], 473, {
        strings[839],
        strings[840],
        strings[841],
        strings[842],
        strings[843],
        strings[844],
        strings[845],
        strings[846],
        strings[847],
        strings[848],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcFlowMeterTypeEnum_type = new enumeration_type(strings[849], 476, {
        strings[850],
        strings[851],
        strings[852],
        strings[853],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcFontStyle_type = new type_declaration(strings[854], 487, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcFontVariant_type = new type_declaration(strings[855], 488, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcFontWeight_type = new type_declaration(strings[856], 489, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcFootingTypeEnum_type = new enumeration_type(strings[857], 492, {
        strings[858],
        strings[859],
        strings[860],
        strings[861],
        strings[862],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcForceMeasure_type = new type_declaration(strings[863], 493, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcFrequencyMeasure_type = new type_declaration(strings[864], 494, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcFurnitureTypeEnum_type = new enumeration_type(strings[865], 499, {
        strings[866],
        strings[867],
        strings[868],
        strings[869],
        strings[870],
        strings[871],
        strings[872],
        strings[873],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcGeographicElementTypeEnum_type = new enumeration_type(strings[874], 502, {
        strings[875],
        strings[876],
        strings[877],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcGeometricProjectionEnum_type = new enumeration_type(strings[878], 504, {
        strings[879],
        strings[880],
        strings[881],
        strings[882],
        strings[883],
        strings[884],
        strings[885],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcGeotechnicalStratumTypeEnum_type = new enumeration_type(strings[886], 515, {
        strings[887],
        strings[888],
        strings[194],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcGlobalOrLocalEnum_type = new enumeration_type(strings[889], 517, {
        strings[890],
        strings[891]
    });
    IFC4X3_TC1_IfcGloballyUniqueId_type = new type_declaration(strings[892], 516, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcGridTypeEnum_type = new enumeration_type(strings[893], 523, {
        strings[894],
        strings[895],
        strings[667],
        strings[896],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcHeatExchangerTypeEnum_type = new enumeration_type(strings[897], 529, {
        strings[898],
        strings[899],
        strings[900],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcHeatFluxDensityMeasure_type = new type_declaration(strings[901], 530, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcHeatingValueMeasure_type = new type_declaration(strings[902], 531, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcHumidifierTypeEnum_type = new enumeration_type(strings[903], 534, {
        strings[904],
        strings[905],
        strings[906],
        strings[907],
        strings[908],
        strings[909],
        strings[910],
        strings[911],
        strings[912],
        strings[913],
        strings[914],
        strings[915],
        strings[916],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcIdentifier_type = new type_declaration(strings[917], 535, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcIlluminanceMeasure_type = new type_declaration(strings[918], 536, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcImpactProtectionDeviceTypeEnum_type = new enumeration_type(strings[919], 540, {
        strings[920],
        strings[921],
        strings[922],
        strings[923],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcInductanceMeasure_type = new type_declaration(strings[924], 548, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcInteger_type = new type_declaration(strings[925], 549, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcIntegerCountRateMeasure_type = new type_declaration(strings[926], 550, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcInterceptorTypeEnum_type = new enumeration_type(strings[927], 553, {
        strings[928],
        strings[929],
        strings[591],
        strings[930],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcInternalOrExternalEnum_type = new enumeration_type(strings[931], 555, {
        strings[793],
        strings[794],
        strings[795],
        strings[796],
        strings[932],
        strings[9]
    });
    IFC4X3_TC1_IfcInventoryTypeEnum_type = new enumeration_type(strings[933], 558, {
        strings[934],
        strings[935],
        strings[936],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcIonConcentrationMeasure_type = new type_declaration(strings[937], 559, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcIsothermalMoistureCapacityMeasure_type = new type_declaration(strings[938], 563, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcJunctionBoxTypeEnum_type = new enumeration_type(strings[939], 566, {
        strings[574],
        strings[940],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcKerbTypeEnum_type = new enumeration_type(strings[941], 569, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcKinematicViscosityMeasure_type = new type_declaration(strings[942], 570, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcKnotType_type = new enumeration_type(strings[943], 571, {
        strings[944],
        strings[945],
        strings[946],
        strings[146]
    });
    IFC4X3_TC1_IfcLabel_type = new type_declaration(strings[947], 572, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcLaborResourceTypeEnum_type = new enumeration_type(strings[948], 575, {
        strings[949],
        strings[950],
        strings[951],
        strings[375],
        strings[376],
        strings[952],
        strings[953],
        strings[426],
        strings[954],
        strings[955],
        strings[956],
        strings[379],
        strings[957],
        strings[370],
        strings[958],
        strings[429],
        strings[959],
        strings[960],
        strings[961],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcLampTypeEnum_type = new enumeration_type(strings[962], 579, {
        strings[963],
        strings[964],
        strings[965],
        strings[966],
        strings[967],
        strings[968],
        strings[969],
        strings[970],
        strings[971],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcLanguageId_type = new type_declaration(strings[972], 580, new named_type(IFC4X3_TC1_IfcIdentifier_type));
    IFC4X3_TC1_IfcLayerSetDirectionEnum_type = new enumeration_type(strings[973], 582, {
        strings[974],
        strings[975],
        strings[976]
    });
    IFC4X3_TC1_IfcLengthMeasure_type = new type_declaration(strings[977], 583, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcLightDistributionCurveEnum_type = new enumeration_type(strings[978], 587, {
        strings[979],
        strings[980],
        strings[981],
        strings[9]
    });
    IFC4X3_TC1_IfcLightEmissionSourceEnum_type = new enumeration_type(strings[982], 590, {
        strings[963],
        strings[964],
        strings[966],
        strings[967],
        strings[983],
        strings[984],
        strings[985],
        strings[986],
        strings[969],
        strings[971],
        strings[9]
    });
    IFC4X3_TC1_IfcLightFixtureTypeEnum_type = new enumeration_type(strings[987], 593, {
        strings[988],
        strings[989],
        strings[990],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcLinearForceMeasure_type = new type_declaration(strings[991], 603, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcLinearMomentMeasure_type = new type_declaration(strings[992], 604, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcLinearStiffnessMeasure_type = new type_declaration(strings[993], 607, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcLinearVelocityMeasure_type = new type_declaration(strings[994], 608, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcLiquidTerminalTypeEnum_type = new enumeration_type(strings[995], 612, {
        strings[831],
        strings[996],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcLoadGroupTypeEnum_type = new enumeration_type(strings[997], 613, {
        strings[998],
        strings[999],
        strings[1000],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcLogical_type = new type_declaration(strings[1001], 615, new simple_type(simple_type::logical_type));
    IFC4X3_TC1_IfcLogicalOperatorEnum_type = new enumeration_type(strings[1002], 616, {
        strings[1003],
        strings[1004],
        strings[1005],
        strings[1006],
        strings[1007]
    });
    IFC4X3_TC1_IfcLuminousFluxMeasure_type = new type_declaration(strings[1008], 619, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcLuminousIntensityDistributionMeasure_type = new type_declaration(strings[1009], 620, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcLuminousIntensityMeasure_type = new type_declaration(strings[1010], 621, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMagneticFluxDensityMeasure_type = new type_declaration(strings[1011], 622, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMagneticFluxMeasure_type = new type_declaration(strings[1012], 623, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMarineFacilityTypeEnum_type = new enumeration_type(strings[1013], 628, {
        strings[1014],
        strings[1015],
        strings[1016],
        strings[1017],
        strings[1018],
        strings[1019],
        strings[1020],
        strings[1021],
        strings[1022],
        strings[1023],
        strings[1024],
        strings[1025],
        strings[1026],
        strings[1027],
        strings[1028],
        strings[1029],
        strings[1030],
        strings[1031],
        strings[1032],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcMarinePartTypeEnum_type = new enumeration_type(strings[1033], 630, {
        strings[1034],
        strings[1035],
        strings[1036],
        strings[1037],
        strings[1038],
        strings[1039],
        strings[1040],
        strings[1041],
        strings[418],
        strings[1042],
        strings[1043],
        strings[1044],
        strings[1045],
        strings[1046],
        strings[1047],
        strings[1048],
        strings[1049],
        strings[1050],
        strings[421],
        strings[1051],
        strings[1052],
        strings[1053],
        strings[1054],
        strings[1055],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcMassDensityMeasure_type = new type_declaration(strings[1056], 631, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMassFlowRateMeasure_type = new type_declaration(strings[1057], 632, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMassMeasure_type = new type_declaration(strings[1058], 633, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMassPerLengthMeasure_type = new type_declaration(strings[1059], 634, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMechanicalFastenerTypeEnum_type = new enumeration_type(strings[1060], 659, {
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
        strings[1072],
        strings[1073],
        strings[1074],
        strings[1075],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcMedicalDeviceTypeEnum_type = new enumeration_type(strings[1076], 662, {
        strings[1077],
        strings[1078],
        strings[1079],
        strings[1080],
        strings[1081],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcMemberTypeEnum_type = new enumeration_type(strings[1082], 665, {
        strings[1083],
        strings[1084],
        strings[1085],
        strings[1086],
        strings[1087],
        strings[1088],
        strings[898],
        strings[6],
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
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcMobileTelecommunicationsApplianceTypeEnum_type = new enumeration_type(strings[1100], 671, {
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
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcModulusOfElasticityMeasure_type = new type_declaration(strings[1114], 672, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration(strings[1115], 673, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration(strings[1116], 674, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionSelect_type = new select_type(strings[1117], 675, {
        IFC4X3_TC1_IfcBoolean_type,
        IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionMeasure_type
    });
    IFC4X3_TC1_IfcModulusOfSubgradeReactionMeasure_type = new type_declaration(strings[1118], 676, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcModulusOfSubgradeReactionSelect_type = new select_type(strings[1119], 677, {
        IFC4X3_TC1_IfcBoolean_type,
        IFC4X3_TC1_IfcModulusOfSubgradeReactionMeasure_type
    });
    IFC4X3_TC1_IfcModulusOfTranslationalSubgradeReactionSelect_type = new select_type(strings[1120], 678, {
        IFC4X3_TC1_IfcBoolean_type,
        IFC4X3_TC1_IfcModulusOfLinearSubgradeReactionMeasure_type
    });
    IFC4X3_TC1_IfcMoistureDiffusivityMeasure_type = new type_declaration(strings[1121], 679, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMolecularWeightMeasure_type = new type_declaration(strings[1122], 680, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMomentOfInertiaMeasure_type = new type_declaration(strings[1123], 681, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMonetaryMeasure_type = new type_declaration(strings[1124], 682, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcMonthInYearNumber_type = new type_declaration(strings[1125], 684, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcMooringDeviceTypeEnum_type = new enumeration_type(strings[1126], 687, {
        strings[1127],
        strings[1128],
        strings[1129],
        strings[1130],
        strings[1131],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcMotorConnectionTypeEnum_type = new enumeration_type(strings[1132], 690, {
        strings[1133],
        strings[1134],
        strings[1135],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcNavigationElementTypeEnum_type = new enumeration_type(strings[1136], 694, {
        strings[1137],
        strings[1138],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcNonNegativeLengthMeasure_type = new type_declaration(strings[1139], 695, new named_type(IFC4X3_TC1_IfcLengthMeasure_type));
    IFC4X3_TC1_IfcNumericMeasure_type = new type_declaration(strings[1140], 697, new simple_type(simple_type::number_type));
    IFC4X3_TC1_IfcObjectiveEnum_type = new enumeration_type(strings[1141], 701, {
        strings[1142],
        strings[1143],
        strings[1144],
        strings[793],
        strings[1145],
        strings[1146],
        strings[1147],
        strings[1148],
        strings[1149],
        strings[1150],
        strings[1151],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcOccupantTypeEnum_type = new enumeration_type(strings[1152], 705, {
        strings[1153],
        strings[1154],
        strings[1155],
        strings[1156],
        strings[1157],
        strings[1158],
        strings[1159],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcOpeningElementTypeEnum_type = new enumeration_type(strings[1160], 712, {
        strings[1161],
        strings[1162],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcOutletTypeEnum_type = new enumeration_type(strings[1163], 720, {
        strings[1164],
        strings[1165],
        strings[1166],
        strings[1167],
        strings[1168],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPHMeasure_type = new type_declaration(strings[1169], 737, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcParameterValue_type = new type_declaration(strings[1170], 723, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcPavementTypeEnum_type = new enumeration_type(strings[1171], 727, {
        strings[1172],
        strings[1173],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPerformanceHistoryTypeEnum_type = new enumeration_type(strings[1174], 730, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPermeableCoveringOperationEnum_type = new enumeration_type(strings[1175], 731, {
        strings[1176],
        strings[1177],
        strings[1178],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPermitTypeEnum_type = new enumeration_type(strings[1179], 734, {
        strings[1180],
        strings[1181],
        strings[1182],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPhysicalOrVirtualEnum_type = new enumeration_type(strings[1183], 739, {
        strings[1184],
        strings[1185],
        strings[9]
    });
    IFC4X3_TC1_IfcPileConstructionEnum_type = new enumeration_type(strings[1186], 743, {
        strings[1187],
        strings[1188],
        strings[1189],
        strings[1190],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPileTypeEnum_type = new enumeration_type(strings[1191], 745, {
        strings[1192],
        strings[1193],
        strings[1194],
        strings[1195],
        strings[1196],
        strings[1197],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPipeFittingTypeEnum_type = new enumeration_type(strings[1198], 748, {
        strings[247],
        strings[248],
        strings[263],
        strings[264],
        strings[250],
        strings[661],
        strings[253],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPipeSegmentTypeEnum_type = new enumeration_type(strings[1199], 751, {
        strings[215],
        strings[663],
        strings[1200],
        strings[664],
        strings[1201],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPlanarForceMeasure_type = new type_declaration(strings[1202], 756, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcPlaneAngleMeasure_type = new type_declaration(strings[1203], 758, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcPlateTypeEnum_type = new enumeration_type(strings[1204], 761, {
        strings[1205],
        strings[1206],
        strings[1207],
        strings[1208],
        strings[1209],
        strings[1210],
        strings[1211],
        strings[1212],
        strings[1213],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPositiveInteger_type = new type_declaration(strings[1214], 774, new named_type(IFC4X3_TC1_IfcInteger_type));
    IFC4X3_TC1_IfcPositiveLengthMeasure_type = new type_declaration(strings[1215], 775, new named_type(IFC4X3_TC1_IfcLengthMeasure_type));
    IFC4X3_TC1_IfcPositivePlaneAngleMeasure_type = new type_declaration(strings[1216], 776, new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type));
    IFC4X3_TC1_IfcPowerMeasure_type = new type_declaration(strings[1217], 779, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcPreferredSurfaceCurveRepresentation_type = new enumeration_type(strings[1218], 786, {
        strings[1219],
        strings[1220],
        strings[1221]
    });
    IFC4X3_TC1_IfcPresentableText_type = new type_declaration(strings[1222], 787, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcPressureMeasure_type = new type_declaration(strings[1223], 792, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcProcedureTypeEnum_type = new enumeration_type(strings[1224], 795, {
        strings[1225],
        strings[1226],
        strings[1227],
        strings[1228],
        strings[1229],
        strings[1230],
        strings[1231],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcProfileTypeEnum_type = new enumeration_type(strings[1232], 805, {
        strings[1233],
        strings[1234]
    });
    IFC4X3_TC1_IfcProjectOrderTypeEnum_type = new enumeration_type(strings[1235], 813, {
        strings[1236],
        strings[1237],
        strings[1238],
        strings[1239],
        strings[1240],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcProjectedOrTrueLengthEnum_type = new enumeration_type(strings[1241], 808, {
        strings[1242],
        strings[1243]
    });
    IFC4X3_TC1_IfcProjectionElementTypeEnum_type = new enumeration_type(strings[1244], 810, {
        strings[1245],
        strings[1246],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPropertySetTemplateTypeEnum_type = new enumeration_type(strings[1247], 828, {
        strings[1248],
        strings[1249],
        strings[1250],
        strings[1251],
        strings[1252],
        strings[1253],
        strings[1254],
        strings[1255],
        strings[1256],
        strings[9]
    });
    IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitTypeEnum_type = new enumeration_type(strings[1257], 836, {
        strings[1258],
        strings[1259],
        strings[1260],
        strings[1261],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcProtectiveDeviceTypeEnum_type = new enumeration_type(strings[1262], 838, {
        strings[1263],
        strings[1264],
        strings[1265],
        strings[1266],
        strings[1267],
        strings[1268],
        strings[1269],
        strings[1270],
        strings[1271],
        strings[1272],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcPumpTypeEnum_type = new enumeration_type(strings[1273], 841, {
        strings[1274],
        strings[1275],
        strings[1276],
        strings[1277],
        strings[1278],
        strings[1279],
        strings[1280],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRadioActivityMeasure_type = new type_declaration(strings[1281], 850, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcRailTypeEnum_type = new enumeration_type(strings[1282], 856, {
        strings[1283],
        strings[1284],
        strings[1285],
        strings[1286],
        strings[1287],
        strings[1288],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRailingTypeEnum_type = new enumeration_type(strings[1289], 854, {
        strings[1290],
        strings[1291],
        strings[1285],
        strings[1292],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRailwayPartTypeEnum_type = new enumeration_type(strings[1293], 859, {
        strings[1294],
        strings[1295],
        strings[1296],
        strings[1297],
        strings[209],
        strings[1298],
        strings[1299],
        strings[1300],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRailwayTypeEnum_type = new enumeration_type(strings[1301], 860, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRampFlightTypeEnum_type = new enumeration_type(strings[1302], 864, {
        strings[1303],
        strings[1304],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRampTypeEnum_type = new enumeration_type(strings[1305], 866, {
        strings[1306],
        strings[1307],
        strings[1308],
        strings[1309],
        strings[1310],
        strings[1311],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRatioMeasure_type = new type_declaration(strings[1312], 867, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcReal_type = new type_declaration(strings[1313], 870, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcRecurrenceTypeEnum_type = new enumeration_type(strings[1314], 876, {
        strings[1315],
        strings[1316],
        strings[1317],
        strings[1318],
        strings[1319],
        strings[1320],
        strings[1321],
        strings[1322]
    });
    IFC4X3_TC1_IfcReferentTypeEnum_type = new enumeration_type(strings[1323], 879, {
        strings[1324],
        strings[198],
        strings[1325],
        strings[1326],
        strings[1327],
        strings[1328],
        strings[1329],
        strings[1330],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcReflectanceMethodEnum_type = new enumeration_type(strings[1331], 880, {
        strings[1332],
        strings[1333],
        strings[1334],
        strings[1335],
        strings[380],
        strings[1336],
        strings[1337],
        strings[1184],
        strings[381],
        strings[1338],
        strings[9]
    });
    IFC4X3_TC1_IfcReinforcedSoilTypeEnum_type = new enumeration_type(strings[1339], 883, {
        strings[1340],
        strings[1341],
        strings[1342],
        strings[1343],
        strings[1344],
        strings[1345],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcReinforcingBarRoleEnum_type = new enumeration_type(strings[1346], 887, {
        strings[1347],
        strings[1348],
        strings[1349],
        strings[1350],
        strings[1351],
        strings[1352],
        strings[1353],
        strings[1096],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcReinforcingBarSurfaceEnum_type = new enumeration_type(strings[1354], 888, {
        strings[1355],
        strings[1356]
    });
    IFC4X3_TC1_IfcReinforcingBarTypeEnum_type = new enumeration_type(strings[1357], 890, {
        strings[1347],
        strings[1348],
        strings[1349],
        strings[1350],
        strings[1351],
        strings[1352],
        strings[1353],
        strings[1358],
        strings[1096],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcReinforcingMeshTypeEnum_type = new enumeration_type(strings[1359], 895, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRoadPartTypeEnum_type = new enumeration_type(strings[1360], 965, {
        strings[1361],
        strings[1362],
        strings[1363],
        strings[1364],
        strings[1365],
        strings[1366],
        strings[198],
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
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRoadTypeEnum_type = new enumeration_type(strings[1384], 966, {
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRoleEnum_type = new enumeration_type(strings[1385], 967, {
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
        strings[1398],
        strings[1399],
        strings[1400],
        strings[1401],
        strings[1158],
        strings[1402],
        strings[1403],
        strings[1404],
        strings[1405],
        strings[1406],
        strings[8]
    });
    IFC4X3_TC1_IfcRoofTypeEnum_type = new enumeration_type(strings[1407], 970, {
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
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcRotationalFrequencyMeasure_type = new type_declaration(strings[1421], 972, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcRotationalMassMeasure_type = new type_declaration(strings[1422], 973, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcRotationalStiffnessMeasure_type = new type_declaration(strings[1423], 974, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcRotationalStiffnessSelect_type = new select_type(strings[1424], 975, {
        IFC4X3_TC1_IfcBoolean_type,
        IFC4X3_TC1_IfcRotationalStiffnessMeasure_type
    });
    IFC4X3_TC1_IfcSIPrefix_type = new enumeration_type(strings[1425], 1020, {
        strings[1426],
        strings[1427],
        strings[1428],
        strings[1429],
        strings[1430],
        strings[1431],
        strings[1432],
        strings[1433],
        strings[1434],
        strings[1435],
        strings[1436],
        strings[1437],
        strings[1438],
        strings[1439],
        strings[1440],
        strings[1441]
    });
    IFC4X3_TC1_IfcSIUnitName_type = new enumeration_type(strings[1442], 1023, {
        strings[1443],
        strings[1444],
        strings[1445],
        strings[1446],
        strings[1447],
        strings[1448],
        strings[1449],
        strings[1450],
        strings[1451],
        strings[1452],
        strings[1453],
        strings[1454],
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
        strings[1468],
        strings[1469],
        strings[1470],
        strings[1471],
        strings[1472]
    });
    IFC4X3_TC1_IfcSanitaryTerminalTypeEnum_type = new enumeration_type(strings[1473], 979, {
        strings[1474],
        strings[1475],
        strings[1476],
        strings[1477],
        strings[1478],
        strings[835],
        strings[1479],
        strings[1480],
        strings[1481],
        strings[1482],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSectionModulusMeasure_type = new type_declaration(strings[1483], 988, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSectionTypeEnum_type = new enumeration_type(strings[1484], 991, {
        strings[1485],
        strings[1486]
    });
    IFC4X3_TC1_IfcSectionalAreaIntegralMeasure_type = new type_declaration(strings[1487], 983, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSensorTypeEnum_type = new enumeration_type(strings[1488], 997, {
        strings[1489],
        strings[1490],
        strings[1491],
        strings[1492],
        strings[1493],
        strings[1494],
        strings[1495],
        strings[1496],
        strings[1497],
        strings[1498],
        strings[1499],
        strings[1500],
        strings[1501],
        strings[1502],
        strings[1503],
        strings[1504],
        strings[1505],
        strings[1506],
        strings[1507],
        strings[1508],
        strings[1509],
        strings[1510],
        strings[1511],
        strings[1512],
        strings[1513],
        strings[1514],
        strings[1515],
        strings[1516],
        strings[1517],
        strings[1518],
        strings[1519],
        strings[1520],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSequenceEnum_type = new enumeration_type(strings[1521], 998, {
        strings[1522],
        strings[1523],
        strings[1524],
        strings[1525],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcShadingDeviceTypeEnum_type = new enumeration_type(strings[1526], 1002, {
        strings[1527],
        strings[1528],
        strings[1529],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcShearModulusMeasure_type = new type_declaration(strings[1530], 1006, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSignTypeEnum_type = new enumeration_type(strings[1531], 1014, {
        strings[1532],
        strings[1336],
        strings[1533],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSignalTypeEnum_type = new enumeration_type(strings[1534], 1012, {
        strings[1535],
        strings[1536],
        strings[1537],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSimplePropertyTemplateTypeEnum_type = new enumeration_type(strings[1538], 1017, {
        strings[1539],
        strings[1540],
        strings[1541],
        strings[1542],
        strings[1543],
        strings[1544],
        strings[1545],
        strings[1546],
        strings[1547],
        strings[1548],
        strings[1549],
        strings[1550],
        strings[1551]
    });
    IFC4X3_TC1_IfcSlabTypeEnum_type = new enumeration_type(strings[1552], 1027, {
        strings[1553],
        strings[1554],
        strings[1555],
        strings[1556],
        strings[370],
        strings[1557],
        strings[1379],
        strings[1558],
        strings[1559],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSolarDeviceTypeEnum_type = new enumeration_type(strings[1560], 1031, {
        strings[1561],
        strings[1562],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSolidAngleMeasure_type = new type_declaration(strings[1563], 1032, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSoundPowerLevelMeasure_type = new type_declaration(strings[1564], 1035, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSoundPowerMeasure_type = new type_declaration(strings[1565], 1036, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSoundPressureLevelMeasure_type = new type_declaration(strings[1566], 1037, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSoundPressureMeasure_type = new type_declaration(strings[1567], 1038, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSpaceHeaterTypeEnum_type = new enumeration_type(strings[1568], 1043, {
        strings[1569],
        strings[1570],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSpaceTypeEnum_type = new enumeration_type(strings[1571], 1045, {
        strings[1572],
        strings[793],
        strings[1573],
        strings[932],
        strings[1574],
        strings[1575],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSpatialZoneTypeEnum_type = new enumeration_type(strings[1576], 1053, {
        strings[1577],
        strings[1578],
        strings[1579],
        strings[369],
        strings[1580],
        strings[1581],
        strings[599],
        strings[1261],
        strings[33],
        strings[606],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSpecificHeatCapacityMeasure_type = new type_declaration(strings[1582], 1054, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSpecularExponent_type = new type_declaration(strings[1583], 1055, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcSpecularRoughness_type = new type_declaration(strings[1584], 1057, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcStackTerminalTypeEnum_type = new enumeration_type(strings[1585], 1063, {
        strings[1586],
        strings[1587],
        strings[1588],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcStairFlightTypeEnum_type = new enumeration_type(strings[1589], 1067, {
        strings[1590],
        strings[1412],
        strings[1303],
        strings[1304],
        strings[1591],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcStairTypeEnum_type = new enumeration_type(strings[1592], 1069, {
        strings[1593],
        strings[1594],
        strings[1595],
        strings[1596],
        strings[1597],
        strings[1598],
        strings[1599],
        strings[1600],
        strings[1601],
        strings[1602],
        strings[1603],
        strings[1604],
        strings[1605],
        strings[1606],
        strings[1607],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcStateEnum_type = new enumeration_type(strings[1608], 1070, {
        strings[1609],
        strings[1610],
        strings[1611],
        strings[1612],
        strings[1613]
    });
    IFC4X3_TC1_IfcStrippedOptional_type = new type_declaration(strings[1614], 1071, new simple_type(simple_type::boolean_type));
    IFC4X3_TC1_IfcStructuralCurveActivityTypeEnum_type = new enumeration_type(strings[1615], 1079, {
        strings[1616],
        strings[1617],
        strings[1618],
        strings[438],
        strings[1619],
        strings[1620],
        strings[1621],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcStructuralCurveMemberTypeEnum_type = new enumeration_type(strings[1622], 1082, {
        strings[558],
        strings[1623],
        strings[1624],
        strings[1625],
        strings[1626],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcStructuralSurfaceActivityTypeEnum_type = new enumeration_type(strings[1627], 1108, {
        strings[1628],
        strings[1616],
        strings[1617],
        strings[1629],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcStructuralSurfaceMemberTypeEnum_type = new enumeration_type(strings[1630], 1111, {
        strings[1631],
        strings[1632],
        strings[1633],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSubContractResourceTypeEnum_type = new enumeration_type(strings[1634], 1119, {
        strings[1635],
        strings[1182],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSurfaceFeatureTypeEnum_type = new enumeration_type(strings[1636], 1125, {
        strings[1637],
        strings[1638],
        strings[1639],
        strings[1640],
        strings[1641],
        strings[1642],
        strings[1643],
        strings[1644],
        strings[1645],
        strings[1646],
        strings[1647],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSurfaceSide_type = new enumeration_type(strings[1648], 1130, {
        strings[1649],
        strings[517],
        strings[518]
    });
    IFC4X3_TC1_IfcSwitchingDeviceTypeEnum_type = new enumeration_type(strings[1650], 1145, {
        strings[1651],
        strings[1652],
        strings[1653],
        strings[1654],
        strings[1655],
        strings[734],
        strings[1656],
        strings[1657],
        strings[1658],
        strings[1659],
        strings[1660],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcSystemFurnitureElementTypeEnum_type = new enumeration_type(strings[1661], 1149, {
        strings[1662],
        strings[1663],
        strings[1664],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcTankTypeEnum_type = new enumeration_type(strings[1665], 1155, {
        strings[1666],
        strings[1667],
        strings[1668],
        strings[1669],
        strings[1670],
        strings[1671],
        strings[1672],
        strings[1673],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcTaskDurationEnum_type = new enumeration_type(strings[1674], 1157, {
        strings[1675],
        strings[1676],
        strings[9]
    });
    IFC4X3_TC1_IfcTaskTypeEnum_type = new enumeration_type(strings[1677], 1161, {
        strings[1678],
        strings[1679],
        strings[1228],
        strings[1577],
        strings[1680],
        strings[1681],
        strings[575],
        strings[1682],
        strings[1683],
        strings[1684],
        strings[1685],
        strings[1686],
        strings[1687],
        strings[1688],
        strings[1689],
        strings[1690],
        strings[1691],
        strings[1230],
        strings[1231],
        strings[1692],
        strings[1693],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcTemperatureGradientMeasure_type = new type_declaration(strings[1694], 1163, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcTemperatureRateOfChangeMeasure_type = new type_declaration(strings[1695], 1164, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcTendonAnchorTypeEnum_type = new enumeration_type(strings[1696], 1168, {
        strings[1064],
        strings[1697],
        strings[1698],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcTendonConduitTypeEnum_type = new enumeration_type(strings[1699], 1171, {
        strings[1064],
        strings[1700],
        strings[560],
        strings[1701],
        strings[1702],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcTendonTypeEnum_type = new enumeration_type(strings[1703], 1173, {
        strings[1704],
        strings[1705],
        strings[1706],
        strings[1707],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcText_type = new type_declaration(strings[1708], 1176, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcTextAlignment_type = new type_declaration(strings[1709], 1177, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcTextDecoration_type = new type_declaration(strings[1710], 1178, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcTextFontName_type = new type_declaration(strings[1711], 1179, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcTextPath_type = new enumeration_type(strings[1712], 1183, {
        strings[1713],
        strings[628],
        strings[630],
        strings[1714]
    });
    IFC4X3_TC1_IfcTextTransformation_type = new type_declaration(strings[1715], 1188, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcThermalAdmittanceMeasure_type = new type_declaration(strings[1716], 1196, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcThermalConductivityMeasure_type = new type_declaration(strings[1717], 1197, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcThermalExpansionCoefficientMeasure_type = new type_declaration(strings[1718], 1198, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcThermalResistanceMeasure_type = new type_declaration(strings[1719], 1199, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcThermalTransmittanceMeasure_type = new type_declaration(strings[1720], 1200, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcThermodynamicTemperatureMeasure_type = new type_declaration(strings[1721], 1201, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcTime_type = new type_declaration(strings[1722], 1203, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcTimeMeasure_type = new type_declaration(strings[1723], 1204, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcTimeOrRatioSelect_type = new select_type(strings[1724], 1205, {
        IFC4X3_TC1_IfcDuration_type,
        IFC4X3_TC1_IfcRatioMeasure_type
    });
    IFC4X3_TC1_IfcTimeSeriesDataTypeEnum_type = new enumeration_type(strings[1725], 1208, {
        strings[1726],
        strings[1617],
        strings[1727],
        strings[1728],
        strings[1729],
        strings[1730],
        strings[9]
    });
    IFC4X3_TC1_IfcTimeStamp_type = new type_declaration(strings[1731], 1210, new simple_type(simple_type::integer_type));
    IFC4X3_TC1_IfcTorqueMeasure_type = new type_declaration(strings[1732], 1214, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcTrackElementTypeEnum_type = new enumeration_type(strings[1733], 1217, {
        strings[1734],
        strings[1735],
        strings[1736],
        strings[1737],
        strings[1738],
        strings[1739],
        strings[1740],
        strings[1741],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcTransformerTypeEnum_type = new enumeration_type(strings[1742], 1220, {
        strings[1743],
        strings[840],
        strings[15],
        strings[1744],
        strings[1745],
        strings[1746],
        strings[1747],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcTransitionCode_type = new enumeration_type(strings[1748], 1221, {
        strings[1726],
        strings[1749],
        strings[1750],
        strings[1751]
    });
    IFC4X3_TC1_IfcTranslationalStiffnessSelect_type = new select_type(strings[1752], 1222, {
        IFC4X3_TC1_IfcBoolean_type,
        IFC4X3_TC1_IfcLinearStiffnessMeasure_type
    });
    IFC4X3_TC1_IfcTransportElementTypeEnum_type = new enumeration_type(strings[1753], 1227, {
        strings[1754],
        strings[1755],
        strings[1756],
        strings[1757],
        strings[1758],
        strings[1759],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcTrimmingPreference_type = new enumeration_type(strings[1760], 1232, {
        strings[1761],
        strings[1148],
        strings[146]
    });
    IFC4X3_TC1_IfcTubeBundleTypeEnum_type = new enumeration_type(strings[1762], 1237, {
        strings[1763],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcURIReference_type = new type_declaration(strings[1764], 1251, new simple_type(simple_type::string_type));
    IFC4X3_TC1_IfcUnitEnum_type = new enumeration_type(strings[1765], 1250, {
        strings[1766],
        strings[1767],
        strings[1768],
        strings[1769],
        strings[1770],
        strings[1771],
        strings[1772],
        strings[1773],
        strings[1774],
        strings[1775],
        strings[1776],
        strings[1777],
        strings[1778],
        strings[1779],
        strings[1780],
        strings[1781],
        strings[1782],
        strings[1783],
        strings[1784],
        strings[1785],
        strings[1786],
        strings[1787],
        strings[1788],
        strings[1789],
        strings[1790],
        strings[1791],
        strings[1792],
        strings[1793],
        strings[1794],
        strings[8]
    });
    IFC4X3_TC1_IfcUnitaryControlElementTypeEnum_type = new enumeration_type(strings[1795], 1245, {
        strings[1796],
        strings[1797],
        strings[840],
        strings[1798],
        strings[1799],
        strings[1800],
        strings[1801],
        strings[1802],
        strings[1803],
        strings[1804],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcUnitaryEquipmentTypeEnum_type = new enumeration_type(strings[1805], 1248, {
        strings[1806],
        strings[1807],
        strings[1808],
        strings[1809],
        strings[1810],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcValveTypeEnum_type = new enumeration_type(strings[1811], 1256, {
        strings[1812],
        strings[1813],
        strings[1814],
        strings[1815],
        strings[1816],
        strings[1817],
        strings[1818],
        strings[1819],
        strings[1820],
        strings[1821],
        strings[1822],
        strings[1823],
        strings[1824],
        strings[1825],
        strings[1826],
        strings[1827],
        strings[1828],
        strings[1829],
        strings[1830],
        strings[1831],
        strings[1832],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcVaporPermeabilityMeasure_type = new type_declaration(strings[1833], 1257, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcVehicleTypeEnum_type = new enumeration_type(strings[1834], 1262, {
        strings[1835],
        strings[1836],
        strings[1837],
        strings[1838],
        strings[1839],
        strings[1840],
        strings[1841],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcVibrationDamperTypeEnum_type = new enumeration_type(strings[1842], 1268, {
        strings[1843],
        strings[1844],
        strings[1195],
        strings[1845],
        strings[1846],
        strings[1847],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcVibrationIsolatorTypeEnum_type = new enumeration_type(strings[1848], 1271, {
        strings[1849],
        strings[1850],
        strings[1851],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcVirtualElementTypeEnum_type = new enumeration_type(strings[1852], 1273, {
        strings[1324],
        strings[1853],
        strings[231],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcVoidingFeatureTypeEnum_type = new enumeration_type(strings[1854], 1276, {
        strings[1855],
        strings[1856],
        strings[1348],
        strings[1857],
        strings[1858],
        strings[1859],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcVolumeMeasure_type = new type_declaration(strings[1860], 1277, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcVolumetricFlowRateMeasure_type = new type_declaration(strings[1861], 1278, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcWallTypeEnum_type = new enumeration_type(strings[1862], 1282, {
        strings[1863],
        strings[1864],
        strings[1865],
        strings[1866],
        strings[1867],
        strings[1620],
        strings[1868],
        strings[1353],
        strings[1869],
        strings[1870],
        strings[1871],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcWarpingConstantMeasure_type = new type_declaration(strings[1872], 1283, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcWarpingMomentMeasure_type = new type_declaration(strings[1873], 1284, new simple_type(simple_type::real_type));
    IFC4X3_TC1_IfcWarpingStiffnessSelect_type = new select_type(strings[1874], 1285, {
        IFC4X3_TC1_IfcBoolean_type,
        IFC4X3_TC1_IfcWarpingMomentMeasure_type
    });
    IFC4X3_TC1_IfcWasteTerminalTypeEnum_type = new enumeration_type(strings[1875], 1288, {
        strings[1876],
        strings[1877],
        strings[1878],
        strings[1879],
        strings[1880],
        strings[1881],
        strings[1882],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcWindowPanelOperationEnum_type = new enumeration_type(strings[1883], 1291, {
        strings[1884],
        strings[1885],
        strings[1886],
        strings[1887],
        strings[1888],
        strings[1889],
        strings[1890],
        strings[1891],
        strings[1892],
        strings[1893],
        strings[1894],
        strings[1895],
        strings[1896],
        strings[9]
    });
    IFC4X3_TC1_IfcWindowPanelPositionEnum_type = new enumeration_type(strings[1897], 1292, {
        strings[1898],
        strings[628],
        strings[629],
        strings[630],
        strings[1899],
        strings[9]
    });
    IFC4X3_TC1_IfcWindowTypeEnum_type = new enumeration_type(strings[1900], 1295, {
        strings[1901],
        strings[1902],
        strings[1903],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcWindowTypePartitioningEnum_type = new enumeration_type(strings[1904], 1296, {
        strings[1905],
        strings[1906],
        strings[1907],
        strings[1908],
        strings[1909],
        strings[1910],
        strings[1911],
        strings[1912],
        strings[1913],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcWorkCalendarTypeEnum_type = new enumeration_type(strings[1914], 1298, {
        strings[1915],
        strings[1916],
        strings[1917],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcWorkPlanTypeEnum_type = new enumeration_type(strings[1918], 1301, {
        strings[1919],
        strings[1920],
        strings[1921],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcWorkScheduleTypeEnum_type = new enumeration_type(strings[1922], 1303, {
        strings[1919],
        strings[1920],
        strings[1921],
        strings[8],
        strings[9]
    });
    IFC4X3_TC1_IfcActorRole_type = new entity(strings[1923], false, 7, 0);
    IFC4X3_TC1_IfcAddress_type = new entity(strings[1924], true, 12, 0);
    IFC4X3_TC1_IfcAlignmentParameterSegment_type = new entity(strings[1925], true, 36, 0);
    IFC4X3_TC1_IfcAlignmentVerticalSegment_type = new entity(strings[1926], false, 40, IFC4X3_TC1_IfcAlignmentParameterSegment_type);
    IFC4X3_TC1_IfcApplication_type = new entity(strings[1927], false, 49, 0);
    IFC4X3_TC1_IfcAppliedValue_type = new entity(strings[1928], false, 50, 0);
    IFC4X3_TC1_IfcApproval_type = new entity(strings[1929], false, 52, 0);
    IFC4X3_TC1_IfcBoundaryCondition_type = new entity(strings[1930], true, 92, 0);
    IFC4X3_TC1_IfcBoundaryEdgeCondition_type = new entity(strings[1931], false, 94, IFC4X3_TC1_IfcBoundaryCondition_type);
    IFC4X3_TC1_IfcBoundaryFaceCondition_type = new entity(strings[1932], false, 95, IFC4X3_TC1_IfcBoundaryCondition_type);
    IFC4X3_TC1_IfcBoundaryNodeCondition_type = new entity(strings[1933], false, 96, IFC4X3_TC1_IfcBoundaryCondition_type);
    IFC4X3_TC1_IfcBoundaryNodeConditionWarping_type = new entity(strings[1934], false, 97, IFC4X3_TC1_IfcBoundaryNodeCondition_type);
    IFC4X3_TC1_IfcConnectionGeometry_type = new entity(strings[1935], true, 206, 0);
    IFC4X3_TC1_IfcConnectionPointGeometry_type = new entity(strings[1936], false, 208, IFC4X3_TC1_IfcConnectionGeometry_type);
    IFC4X3_TC1_IfcConnectionSurfaceGeometry_type = new entity(strings[1937], false, 209, IFC4X3_TC1_IfcConnectionGeometry_type);
    IFC4X3_TC1_IfcConnectionVolumeGeometry_type = new entity(strings[1938], false, 211, IFC4X3_TC1_IfcConnectionGeometry_type);
    IFC4X3_TC1_IfcConstraint_type = new entity(strings[1939], true, 212, 0);
    IFC4X3_TC1_IfcCoordinateOperation_type = new entity(strings[1940], true, 243, 0);
    IFC4X3_TC1_IfcCoordinateReferenceSystem_type = new entity(strings[1941], true, 244, 0);
    IFC4X3_TC1_IfcCostValue_type = new entity(strings[1942], false, 251, IFC4X3_TC1_IfcAppliedValue_type);
    IFC4X3_TC1_IfcDerivedUnit_type = new entity(strings[1943], false, 299, 0);
    IFC4X3_TC1_IfcDerivedUnitElement_type = new entity(strings[1944], false, 300, 0);
    IFC4X3_TC1_IfcDimensionalExponents_type = new entity(strings[1945], false, 303, 0);
    IFC4X3_TC1_IfcExternalInformation_type = new entity(strings[1946], true, 422, 0);
    IFC4X3_TC1_IfcExternalReference_type = new entity(strings[1947], true, 426, 0);
    IFC4X3_TC1_IfcExternallyDefinedHatchStyle_type = new entity(strings[1948], false, 423, IFC4X3_TC1_IfcExternalReference_type);
    IFC4X3_TC1_IfcExternallyDefinedSurfaceStyle_type = new entity(strings[1949], false, 424, IFC4X3_TC1_IfcExternalReference_type);
    IFC4X3_TC1_IfcExternallyDefinedTextFont_type = new entity(strings[1950], false, 425, IFC4X3_TC1_IfcExternalReference_type);
    IFC4X3_TC1_IfcGridAxis_type = new entity(strings[1951], false, 520, 0);
    IFC4X3_TC1_IfcIrregularTimeSeriesValue_type = new entity(strings[1952], false, 561, 0);
    IFC4X3_TC1_IfcLibraryInformation_type = new entity(strings[1953], false, 584, IFC4X3_TC1_IfcExternalInformation_type);
    IFC4X3_TC1_IfcLibraryReference_type = new entity(strings[1954], false, 585, IFC4X3_TC1_IfcExternalReference_type);
    IFC4X3_TC1_IfcLightDistributionData_type = new entity(strings[1955], false, 588, 0);
    IFC4X3_TC1_IfcLightIntensityDistribution_type = new entity(strings[1956], false, 594, 0);
    IFC4X3_TC1_IfcMapConversion_type = new entity(strings[1957], false, 625, IFC4X3_TC1_IfcCoordinateOperation_type);
    IFC4X3_TC1_IfcMaterialClassificationRelationship_type = new entity(strings[1958], false, 636, 0);
    IFC4X3_TC1_IfcMaterialDefinition_type = new entity(strings[1959], true, 639, 0);
    IFC4X3_TC1_IfcMaterialLayer_type = new entity(strings[1960], false, 641, IFC4X3_TC1_IfcMaterialDefinition_type);
    IFC4X3_TC1_IfcMaterialLayerSet_type = new entity(strings[1961], false, 642, IFC4X3_TC1_IfcMaterialDefinition_type);
    IFC4X3_TC1_IfcMaterialLayerWithOffsets_type = new entity(strings[1962], false, 644, IFC4X3_TC1_IfcMaterialLayer_type);
    IFC4X3_TC1_IfcMaterialList_type = new entity(strings[1963], false, 645, 0);
    IFC4X3_TC1_IfcMaterialProfile_type = new entity(strings[1964], false, 646, IFC4X3_TC1_IfcMaterialDefinition_type);
    IFC4X3_TC1_IfcMaterialProfileSet_type = new entity(strings[1965], false, 647, IFC4X3_TC1_IfcMaterialDefinition_type);
    IFC4X3_TC1_IfcMaterialProfileWithOffsets_type = new entity(strings[1966], false, 650, IFC4X3_TC1_IfcMaterialProfile_type);
    IFC4X3_TC1_IfcMaterialUsageDefinition_type = new entity(strings[1967], true, 654, 0);
    IFC4X3_TC1_IfcMeasureWithUnit_type = new entity(strings[1968], false, 656, 0);
    IFC4X3_TC1_IfcMetric_type = new entity(strings[1969], false, 666, IFC4X3_TC1_IfcConstraint_type);
    IFC4X3_TC1_IfcMonetaryUnit_type = new entity(strings[1970], false, 683, 0);
    IFC4X3_TC1_IfcNamedUnit_type = new entity(strings[1971], true, 691, 0);
    IFC4X3_TC1_IfcObjectPlacement_type = new entity(strings[1972], true, 702, 0);
    IFC4X3_TC1_IfcObjective_type = new entity(strings[1973], false, 700, IFC4X3_TC1_IfcConstraint_type);
    IFC4X3_TC1_IfcOrganization_type = new entity(strings[1974], false, 714, 0);
    IFC4X3_TC1_IfcOwnerHistory_type = new entity(strings[1975], false, 721, 0);
    IFC4X3_TC1_IfcPerson_type = new entity(strings[1976], false, 735, 0);
    IFC4X3_TC1_IfcPersonAndOrganization_type = new entity(strings[1977], false, 736, 0);
    IFC4X3_TC1_IfcPhysicalQuantity_type = new entity(strings[1978], true, 740, 0);
    IFC4X3_TC1_IfcPhysicalSimpleQuantity_type = new entity(strings[1979], true, 741, IFC4X3_TC1_IfcPhysicalQuantity_type);
    IFC4X3_TC1_IfcPostalAddress_type = new entity(strings[1980], false, 778, IFC4X3_TC1_IfcAddress_type);
    IFC4X3_TC1_IfcPresentationItem_type = new entity(strings[1981], true, 788, 0);
    IFC4X3_TC1_IfcPresentationLayerAssignment_type = new entity(strings[1982], false, 789, 0);
    IFC4X3_TC1_IfcPresentationLayerWithStyle_type = new entity(strings[1983], false, 790, IFC4X3_TC1_IfcPresentationLayerAssignment_type);
    IFC4X3_TC1_IfcPresentationStyle_type = new entity(strings[1984], true, 791, 0);
    IFC4X3_TC1_IfcProductRepresentation_type = new entity(strings[1985], true, 800, 0);
    IFC4X3_TC1_IfcProfileDef_type = new entity(strings[1986], false, 803, 0);
    IFC4X3_TC1_IfcProjectedCRS_type = new entity(strings[1987], false, 807, IFC4X3_TC1_IfcCoordinateReferenceSystem_type);
    IFC4X3_TC1_IfcPropertyAbstraction_type = new entity(strings[1988], true, 815, 0);
    IFC4X3_TC1_IfcPropertyEnumeration_type = new entity(strings[1989], false, 820, IFC4X3_TC1_IfcPropertyAbstraction_type);
    IFC4X3_TC1_IfcQuantityArea_type = new entity(strings[1990], false, 842, IFC4X3_TC1_IfcPhysicalSimpleQuantity_type);
    IFC4X3_TC1_IfcQuantityCount_type = new entity(strings[1991], false, 843, IFC4X3_TC1_IfcPhysicalSimpleQuantity_type);
    IFC4X3_TC1_IfcQuantityLength_type = new entity(strings[1992], false, 844, IFC4X3_TC1_IfcPhysicalSimpleQuantity_type);
    IFC4X3_TC1_IfcQuantityNumber_type = new entity(strings[1993], false, 845, IFC4X3_TC1_IfcPhysicalSimpleQuantity_type);
    IFC4X3_TC1_IfcQuantityTime_type = new entity(strings[1994], false, 847, IFC4X3_TC1_IfcPhysicalSimpleQuantity_type);
    IFC4X3_TC1_IfcQuantityVolume_type = new entity(strings[1995], false, 848, IFC4X3_TC1_IfcPhysicalSimpleQuantity_type);
    IFC4X3_TC1_IfcQuantityWeight_type = new entity(strings[1996], false, 849, IFC4X3_TC1_IfcPhysicalSimpleQuantity_type);
    IFC4X3_TC1_IfcRecurrencePattern_type = new entity(strings[1997], false, 875, 0);
    IFC4X3_TC1_IfcReference_type = new entity(strings[1998], false, 877, 0);
    IFC4X3_TC1_IfcRepresentation_type = new entity(strings[1999], true, 948, 0);
    IFC4X3_TC1_IfcRepresentationContext_type = new entity(strings[2000], true, 949, 0);
    IFC4X3_TC1_IfcRepresentationItem_type = new entity(strings[2001], true, 950, 0);
    IFC4X3_TC1_IfcRepresentationMap_type = new entity(strings[2002], false, 951, 0);
    IFC4X3_TC1_IfcResourceLevelRelationship_type = new entity(strings[2003], true, 955, 0);
    IFC4X3_TC1_IfcRoot_type = new entity(strings[2004], true, 971, 0);
    IFC4X3_TC1_IfcSIUnit_type = new entity(strings[2005], false, 1022, IFC4X3_TC1_IfcNamedUnit_type);
    IFC4X3_TC1_IfcSchedulingTime_type = new entity(strings[2006], true, 980, 0);
    IFC4X3_TC1_IfcShapeAspect_type = new entity(strings[2007], false, 1003, 0);
    IFC4X3_TC1_IfcShapeModel_type = new entity(strings[2008], true, 1004, IFC4X3_TC1_IfcRepresentation_type);
    IFC4X3_TC1_IfcShapeRepresentation_type = new entity(strings[2009], false, 1005, IFC4X3_TC1_IfcShapeModel_type);
    IFC4X3_TC1_IfcStructuralConnectionCondition_type = new entity(strings[2010], true, 1077, 0);
    IFC4X3_TC1_IfcStructuralLoad_type = new entity(strings[2011], true, 1087, 0);
    IFC4X3_TC1_IfcStructuralLoadConfiguration_type = new entity(strings[2012], false, 1089, IFC4X3_TC1_IfcStructuralLoad_type);
    IFC4X3_TC1_IfcStructuralLoadOrResult_type = new entity(strings[2013], true, 1092, IFC4X3_TC1_IfcStructuralLoad_type);
    IFC4X3_TC1_IfcStructuralLoadStatic_type = new entity(strings[2014], true, 1098, IFC4X3_TC1_IfcStructuralLoadOrResult_type);
    IFC4X3_TC1_IfcStructuralLoadTemperature_type = new entity(strings[2015], false, 1099, IFC4X3_TC1_IfcStructuralLoadStatic_type);
    IFC4X3_TC1_IfcStyleModel_type = new entity(strings[2016], true, 1116, IFC4X3_TC1_IfcRepresentation_type);
    IFC4X3_TC1_IfcStyledItem_type = new entity(strings[2017], false, 1114, IFC4X3_TC1_IfcRepresentationItem_type);
    IFC4X3_TC1_IfcStyledRepresentation_type = new entity(strings[2018], false, 1115, IFC4X3_TC1_IfcStyleModel_type);
    IFC4X3_TC1_IfcSurfaceReinforcementArea_type = new entity(strings[2019], false, 1129, IFC4X3_TC1_IfcStructuralLoadOrResult_type);
    IFC4X3_TC1_IfcSurfaceStyle_type = new entity(strings[2020], false, 1131, IFC4X3_TC1_IfcPresentationStyle_type);
    IFC4X3_TC1_IfcSurfaceStyleLighting_type = new entity(strings[2021], false, 1133, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcSurfaceStyleRefraction_type = new entity(strings[2022], false, 1134, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcSurfaceStyleShading_type = new entity(strings[2023], false, 1136, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcSurfaceStyleWithTextures_type = new entity(strings[2024], false, 1137, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcSurfaceTexture_type = new entity(strings[2025], true, 1138, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcTable_type = new entity(strings[2026], false, 1150, 0);
    IFC4X3_TC1_IfcTableColumn_type = new entity(strings[2027], false, 1151, 0);
    IFC4X3_TC1_IfcTableRow_type = new entity(strings[2028], false, 1152, 0);
    IFC4X3_TC1_IfcTaskTime_type = new entity(strings[2029], false, 1158, IFC4X3_TC1_IfcSchedulingTime_type);
    IFC4X3_TC1_IfcTaskTimeRecurring_type = new entity(strings[2030], false, 1159, IFC4X3_TC1_IfcTaskTime_type);
    IFC4X3_TC1_IfcTelecomAddress_type = new entity(strings[2031], false, 1162, IFC4X3_TC1_IfcAddress_type);
    IFC4X3_TC1_IfcTextStyle_type = new entity(strings[2032], false, 1184, IFC4X3_TC1_IfcPresentationStyle_type);
    IFC4X3_TC1_IfcTextStyleForDefinedFont_type = new entity(strings[2033], false, 1186, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcTextStyleTextModel_type = new entity(strings[2034], false, 1187, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcTextureCoordinate_type = new entity(strings[2035], true, 1189, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcTextureCoordinateGenerator_type = new entity(strings[2036], false, 1190, IFC4X3_TC1_IfcTextureCoordinate_type);
    IFC4X3_TC1_IfcTextureCoordinateIndices_type = new entity(strings[2037], false, 1191, 0);
    IFC4X3_TC1_IfcTextureCoordinateIndicesWithVoids_type = new entity(strings[2038], false, 1192, IFC4X3_TC1_IfcTextureCoordinateIndices_type);
    IFC4X3_TC1_IfcTextureMap_type = new entity(strings[2039], false, 1193, IFC4X3_TC1_IfcTextureCoordinate_type);
    IFC4X3_TC1_IfcTextureVertex_type = new entity(strings[2040], false, 1194, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcTextureVertexList_type = new entity(strings[2041], false, 1195, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcTimePeriod_type = new entity(strings[2042], false, 1206, 0);
    IFC4X3_TC1_IfcTimeSeries_type = new entity(strings[2043], true, 1207, 0);
    IFC4X3_TC1_IfcTimeSeriesValue_type = new entity(strings[2044], false, 1209, 0);
    IFC4X3_TC1_IfcTopologicalRepresentationItem_type = new entity(strings[2045], true, 1211, IFC4X3_TC1_IfcRepresentationItem_type);
    IFC4X3_TC1_IfcTopologyRepresentation_type = new entity(strings[2046], false, 1212, IFC4X3_TC1_IfcShapeModel_type);
    IFC4X3_TC1_IfcUnitAssignment_type = new entity(strings[2047], false, 1249, 0);
    IFC4X3_TC1_IfcVertex_type = new entity(strings[2048], false, 1263, IFC4X3_TC1_IfcTopologicalRepresentationItem_type);
    IFC4X3_TC1_IfcVertexPoint_type = new entity(strings[2049], false, 1265, IFC4X3_TC1_IfcVertex_type);
    IFC4X3_TC1_IfcVirtualGridIntersection_type = new entity(strings[2050], false, 1274, 0);
    IFC4X3_TC1_IfcWorkTime_type = new entity(strings[2051], false, 1304, IFC4X3_TC1_IfcSchedulingTime_type);
    IFC4X3_TC1_IfcActorSelect_type = new select_type(strings[2052], 8, {
        IFC4X3_TC1_IfcOrganization_type,
        IFC4X3_TC1_IfcPerson_type,
        IFC4X3_TC1_IfcPersonAndOrganization_type
    });
    IFC4X3_TC1_IfcArcIndex_type = new type_declaration(strings[2053], 57, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_TC1_IfcPositiveInteger_type)));
    IFC4X3_TC1_IfcBendingParameterSelect_type = new select_type(strings[2054], 79, {
        IFC4X3_TC1_IfcLengthMeasure_type,
        IFC4X3_TC1_IfcPlaneAngleMeasure_type
    });
    IFC4X3_TC1_IfcBoxAlignment_type = new type_declaration(strings[2055], 101, new named_type(IFC4X3_TC1_IfcLabel_type));
    IFC4X3_TC1_IfcCurveMeasureSelect_type = new select_type(strings[2056], 276, {
        IFC4X3_TC1_IfcNonNegativeLengthMeasure_type,
        IFC4X3_TC1_IfcParameterValue_type
    });
    IFC4X3_TC1_IfcDerivedMeasureValue_type = new select_type(strings[2057], 297, {
        IFC4X3_TC1_IfcAbsorbedDoseMeasure_type,
        IFC4X3_TC1_IfcAccelerationMeasure_type,
        IFC4X3_TC1_IfcAngularVelocityMeasure_type,
        IFC4X3_TC1_IfcAreaDensityMeasure_type,
        IFC4X3_TC1_IfcCompoundPlaneAngleMeasure_type,
        IFC4X3_TC1_IfcCurvatureMeasure_type,
        IFC4X3_TC1_IfcDoseEquivalentMeasure_type,
        IFC4X3_TC1_IfcDynamicViscosityMeasure_type,
        IFC4X3_TC1_IfcElectricCapacitanceMeasure_type,
        IFC4X3_TC1_IfcElectricChargeMeasure_type,
        IFC4X3_TC1_IfcElectricConductanceMeasure_type,
        IFC4X3_TC1_IfcElectricResistanceMeasure_type,
        IFC4X3_TC1_IfcElectricVoltageMeasure_type,
        IFC4X3_TC1_IfcEnergyMeasure_type,
        IFC4X3_TC1_IfcForceMeasure_type,
        IFC4X3_TC1_IfcFrequencyMeasure_type,
        IFC4X3_TC1_IfcHeatFluxDensityMeasure_type,
        IFC4X3_TC1_IfcHeatingValueMeasure_type,
        IFC4X3_TC1_IfcIlluminanceMeasure_type,
        IFC4X3_TC1_IfcInductanceMeasure_type,
        IFC4X3_TC1_IfcIntegerCountRateMeasure_type,
        IFC4X3_TC1_IfcIonConcentrationMeasure_type,
        IFC4X3_TC1_IfcIsothermalMoistureCapacityMeasure_type,
        IFC4X3_TC1_IfcKinematicViscosityMeasure_type,
        IFC4X3_TC1_IfcLinearForceMeasure_type,
        IFC4X3_TC1_IfcLinearMomentMeasure_type,
        IFC4X3_TC1_IfcLinearStiffnessMeasure_type,
        IFC4X3_TC1_IfcLinearVelocityMeasure_type,
        IFC4X3_TC1_IfcLuminousFluxMeasure_type,
        IFC4X3_TC1_IfcLuminousIntensityDistributionMeasure_type,
        IFC4X3_TC1_IfcMagneticFluxDensityMeasure_type,
        IFC4X3_TC1_IfcMagneticFluxMeasure_type,
        IFC4X3_TC1_IfcMassDensityMeasure_type,
        IFC4X3_TC1_IfcMassFlowRateMeasure_type,
        IFC4X3_TC1_IfcMassPerLengthMeasure_type,
        IFC4X3_TC1_IfcModulusOfElasticityMeasure_type,
        IFC4X3_TC1_IfcModulusOfLinearSubgradeReactionMeasure_type,
        IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionMeasure_type,
        IFC4X3_TC1_IfcModulusOfSubgradeReactionMeasure_type,
        IFC4X3_TC1_IfcMoistureDiffusivityMeasure_type,
        IFC4X3_TC1_IfcMolecularWeightMeasure_type,
        IFC4X3_TC1_IfcMomentOfInertiaMeasure_type,
        IFC4X3_TC1_IfcMonetaryMeasure_type,
        IFC4X3_TC1_IfcPHMeasure_type,
        IFC4X3_TC1_IfcPlanarForceMeasure_type,
        IFC4X3_TC1_IfcPowerMeasure_type,
        IFC4X3_TC1_IfcPressureMeasure_type,
        IFC4X3_TC1_IfcRadioActivityMeasure_type,
        IFC4X3_TC1_IfcRotationalFrequencyMeasure_type,
        IFC4X3_TC1_IfcRotationalMassMeasure_type,
        IFC4X3_TC1_IfcRotationalStiffnessMeasure_type,
        IFC4X3_TC1_IfcSectionModulusMeasure_type,
        IFC4X3_TC1_IfcSectionalAreaIntegralMeasure_type,
        IFC4X3_TC1_IfcShearModulusMeasure_type,
        IFC4X3_TC1_IfcSoundPowerLevelMeasure_type,
        IFC4X3_TC1_IfcSoundPowerMeasure_type,
        IFC4X3_TC1_IfcSoundPressureLevelMeasure_type,
        IFC4X3_TC1_IfcSoundPressureMeasure_type,
        IFC4X3_TC1_IfcSpecificHeatCapacityMeasure_type,
        IFC4X3_TC1_IfcTemperatureGradientMeasure_type,
        IFC4X3_TC1_IfcTemperatureRateOfChangeMeasure_type,
        IFC4X3_TC1_IfcThermalAdmittanceMeasure_type,
        IFC4X3_TC1_IfcThermalConductivityMeasure_type,
        IFC4X3_TC1_IfcThermalExpansionCoefficientMeasure_type,
        IFC4X3_TC1_IfcThermalResistanceMeasure_type,
        IFC4X3_TC1_IfcThermalTransmittanceMeasure_type,
        IFC4X3_TC1_IfcTorqueMeasure_type,
        IFC4X3_TC1_IfcVaporPermeabilityMeasure_type,
        IFC4X3_TC1_IfcVolumetricFlowRateMeasure_type,
        IFC4X3_TC1_IfcWarpingConstantMeasure_type,
        IFC4X3_TC1_IfcWarpingMomentMeasure_type
    });
    IFC4X3_TC1_IfcLayeredItem_type = new select_type(strings[2058], 581, {
        IFC4X3_TC1_IfcRepresentation_type,
        IFC4X3_TC1_IfcRepresentationItem_type
    });
    IFC4X3_TC1_IfcLibrarySelect_type = new select_type(strings[2059], 586, {
        IFC4X3_TC1_IfcLibraryInformation_type,
        IFC4X3_TC1_IfcLibraryReference_type
    });
    IFC4X3_TC1_IfcLightDistributionDataSourceSelect_type = new select_type(strings[2060], 589, {
        IFC4X3_TC1_IfcExternalReference_type,
        IFC4X3_TC1_IfcLightIntensityDistribution_type
    });
    IFC4X3_TC1_IfcLineIndex_type = new type_declaration(strings[2061], 609, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcPositiveInteger_type)));
    IFC4X3_TC1_IfcMaterialSelect_type = new select_type(strings[2062], 653, {
        IFC4X3_TC1_IfcMaterialDefinition_type,
        IFC4X3_TC1_IfcMaterialList_type,
        IFC4X3_TC1_IfcMaterialUsageDefinition_type
    });
    IFC4X3_TC1_IfcNormalisedRatioMeasure_type = new type_declaration(strings[2063], 696, new named_type(IFC4X3_TC1_IfcRatioMeasure_type));
    IFC4X3_TC1_IfcObjectReferenceSelect_type = new select_type(strings[2064], 703, {
        IFC4X3_TC1_IfcAddress_type,
        IFC4X3_TC1_IfcAppliedValue_type,
        IFC4X3_TC1_IfcExternalReference_type,
        IFC4X3_TC1_IfcMaterialDefinition_type,
        IFC4X3_TC1_IfcOrganization_type,
        IFC4X3_TC1_IfcPerson_type,
        IFC4X3_TC1_IfcPersonAndOrganization_type,
        IFC4X3_TC1_IfcTable_type,
        IFC4X3_TC1_IfcTimeSeries_type
    });
    IFC4X3_TC1_IfcPositiveRatioMeasure_type = new type_declaration(strings[2065], 777, new named_type(IFC4X3_TC1_IfcRatioMeasure_type));
    IFC4X3_TC1_IfcSegmentIndexSelect_type = new select_type(strings[2066], 994, {
        IFC4X3_TC1_IfcArcIndex_type,
        IFC4X3_TC1_IfcLineIndex_type
    });
    IFC4X3_TC1_IfcSimpleValue_type = new select_type(strings[2067], 1018, {
        IFC4X3_TC1_IfcBinary_type,
        IFC4X3_TC1_IfcBoolean_type,
        IFC4X3_TC1_IfcDate_type,
        IFC4X3_TC1_IfcDateTime_type,
        IFC4X3_TC1_IfcDuration_type,
        IFC4X3_TC1_IfcIdentifier_type,
        IFC4X3_TC1_IfcInteger_type,
        IFC4X3_TC1_IfcLabel_type,
        IFC4X3_TC1_IfcLogical_type,
        IFC4X3_TC1_IfcPositiveInteger_type,
        IFC4X3_TC1_IfcReal_type,
        IFC4X3_TC1_IfcText_type,
        IFC4X3_TC1_IfcTime_type,
        IFC4X3_TC1_IfcTimeStamp_type
    });
    IFC4X3_TC1_IfcSizeSelect_type = new select_type(strings[2068], 1024, {
        IFC4X3_TC1_IfcDescriptiveMeasure_type,
        IFC4X3_TC1_IfcLengthMeasure_type,
        IFC4X3_TC1_IfcNormalisedRatioMeasure_type,
        IFC4X3_TC1_IfcPositiveLengthMeasure_type,
        IFC4X3_TC1_IfcPositiveRatioMeasure_type,
        IFC4X3_TC1_IfcRatioMeasure_type
    });
    IFC4X3_TC1_IfcSpecularHighlightSelect_type = new select_type(strings[2069], 1056, {
        IFC4X3_TC1_IfcSpecularExponent_type,
        IFC4X3_TC1_IfcSpecularRoughness_type
    });
    IFC4X3_TC1_IfcSurfaceStyleElementSelect_type = new select_type(strings[2070], 1132, {
        IFC4X3_TC1_IfcExternallyDefinedSurfaceStyle_type,
        IFC4X3_TC1_IfcSurfaceStyleLighting_type,
        IFC4X3_TC1_IfcSurfaceStyleRefraction_type,
        IFC4X3_TC1_IfcSurfaceStyleShading_type,
        IFC4X3_TC1_IfcSurfaceStyleWithTextures_type
    });
    IFC4X3_TC1_IfcUnit_type = new select_type(strings[2071], 1242, {
        IFC4X3_TC1_IfcDerivedUnit_type,
        IFC4X3_TC1_IfcMonetaryUnit_type,
        IFC4X3_TC1_IfcNamedUnit_type
    });
    IFC4X3_TC1_IfcAlignmentCantSegment_type = new entity(strings[2072], false, 31, IFC4X3_TC1_IfcAlignmentParameterSegment_type);
    IFC4X3_TC1_IfcAlignmentHorizontalSegment_type = new entity(strings[2073], false, 34, IFC4X3_TC1_IfcAlignmentParameterSegment_type);
    IFC4X3_TC1_IfcApprovalRelationship_type = new entity(strings[2074], false, 53, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcArbitraryClosedProfileDef_type = new entity(strings[2075], false, 54, IFC4X3_TC1_IfcProfileDef_type);
    IFC4X3_TC1_IfcArbitraryOpenProfileDef_type = new entity(strings[2076], false, 55, IFC4X3_TC1_IfcProfileDef_type);
    IFC4X3_TC1_IfcArbitraryProfileDefWithVoids_type = new entity(strings[2077], false, 56, IFC4X3_TC1_IfcArbitraryClosedProfileDef_type);
    IFC4X3_TC1_IfcBlobTexture_type = new entity(strings[2078], false, 81, IFC4X3_TC1_IfcSurfaceTexture_type);
    IFC4X3_TC1_IfcCenterLineProfileDef_type = new entity(strings[2079], false, 155, IFC4X3_TC1_IfcArbitraryOpenProfileDef_type);
    IFC4X3_TC1_IfcClassification_type = new entity(strings[2080], false, 168, IFC4X3_TC1_IfcExternalInformation_type);
    IFC4X3_TC1_IfcClassificationReference_type = new entity(strings[2081], false, 169, IFC4X3_TC1_IfcExternalReference_type);
    IFC4X3_TC1_IfcColourRgbList_type = new entity(strings[2082], false, 180, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcColourSpecification_type = new entity(strings[2083], true, 181, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcCompositeProfileDef_type = new entity(strings[2084], false, 195, IFC4X3_TC1_IfcProfileDef_type);
    IFC4X3_TC1_IfcConnectedFaceSet_type = new entity(strings[2085], false, 204, IFC4X3_TC1_IfcTopologicalRepresentationItem_type);
    IFC4X3_TC1_IfcConnectionCurveGeometry_type = new entity(strings[2086], false, 205, IFC4X3_TC1_IfcConnectionGeometry_type);
    IFC4X3_TC1_IfcConnectionPointEccentricity_type = new entity(strings[2087], false, 207, IFC4X3_TC1_IfcConnectionPointGeometry_type);
    IFC4X3_TC1_IfcContextDependentUnit_type = new entity(strings[2088], false, 227, IFC4X3_TC1_IfcNamedUnit_type);
    IFC4X3_TC1_IfcConversionBasedUnit_type = new entity(strings[2089], false, 232, IFC4X3_TC1_IfcNamedUnit_type);
    IFC4X3_TC1_IfcConversionBasedUnitWithOffset_type = new entity(strings[2090], false, 233, IFC4X3_TC1_IfcConversionBasedUnit_type);
    IFC4X3_TC1_IfcCurrencyRelationship_type = new entity(strings[2091], false, 266, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcCurveStyle_type = new entity(strings[2092], false, 280, IFC4X3_TC1_IfcPresentationStyle_type);
    IFC4X3_TC1_IfcCurveStyleFont_type = new entity(strings[2093], false, 281, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcCurveStyleFontAndScaling_type = new entity(strings[2094], false, 282, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcCurveStyleFontPattern_type = new entity(strings[2095], false, 283, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcDerivedProfileDef_type = new entity(strings[2096], false, 298, IFC4X3_TC1_IfcProfileDef_type);
    IFC4X3_TC1_IfcDocumentInformation_type = new entity(strings[2097], false, 330, IFC4X3_TC1_IfcExternalInformation_type);
    IFC4X3_TC1_IfcDocumentInformationRelationship_type = new entity(strings[2098], false, 331, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcDocumentReference_type = new entity(strings[2099], false, 332, IFC4X3_TC1_IfcExternalReference_type);
    IFC4X3_TC1_IfcEdge_type = new entity(strings[2100], false, 362, IFC4X3_TC1_IfcTopologicalRepresentationItem_type);
    IFC4X3_TC1_IfcEdgeCurve_type = new entity(strings[2101], false, 363, IFC4X3_TC1_IfcEdge_type);
    IFC4X3_TC1_IfcEventTime_type = new entity(strings[2102], false, 417, IFC4X3_TC1_IfcSchedulingTime_type);
    IFC4X3_TC1_IfcExtendedProperties_type = new entity(strings[2103], true, 421, IFC4X3_TC1_IfcPropertyAbstraction_type);
    IFC4X3_TC1_IfcExternalReferenceRelationship_type = new entity(strings[2104], false, 427, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcFace_type = new entity(strings[2105], false, 433, IFC4X3_TC1_IfcTopologicalRepresentationItem_type);
    IFC4X3_TC1_IfcFaceBound_type = new entity(strings[2106], false, 435, IFC4X3_TC1_IfcTopologicalRepresentationItem_type);
    IFC4X3_TC1_IfcFaceOuterBound_type = new entity(strings[2107], false, 436, IFC4X3_TC1_IfcFaceBound_type);
    IFC4X3_TC1_IfcFaceSurface_type = new entity(strings[2108], false, 437, IFC4X3_TC1_IfcFace_type);
    IFC4X3_TC1_IfcFailureConnectionCondition_type = new entity(strings[2109], false, 445, IFC4X3_TC1_IfcStructuralConnectionCondition_type);
    IFC4X3_TC1_IfcFillAreaStyle_type = new entity(strings[2110], false, 455, IFC4X3_TC1_IfcPresentationStyle_type);
    IFC4X3_TC1_IfcGeometricRepresentationContext_type = new entity(strings[2111], false, 505, IFC4X3_TC1_IfcRepresentationContext_type);
    IFC4X3_TC1_IfcGeometricRepresentationItem_type = new entity(strings[2112], true, 506, IFC4X3_TC1_IfcRepresentationItem_type);
    IFC4X3_TC1_IfcGeometricRepresentationSubContext_type = new entity(strings[2113], false, 507, IFC4X3_TC1_IfcGeometricRepresentationContext_type);
    IFC4X3_TC1_IfcGeometricSet_type = new entity(strings[2114], false, 508, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcGridPlacement_type = new entity(strings[2115], false, 521, IFC4X3_TC1_IfcObjectPlacement_type);
    IFC4X3_TC1_IfcHalfSpaceSolid_type = new entity(strings[2116], false, 525, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcImageTexture_type = new entity(strings[2117], false, 537, IFC4X3_TC1_IfcSurfaceTexture_type);
    IFC4X3_TC1_IfcIndexedColourMap_type = new entity(strings[2118], false, 541, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcIndexedTextureMap_type = new entity(strings[2119], true, 546, IFC4X3_TC1_IfcTextureCoordinate_type);
    IFC4X3_TC1_IfcIndexedTriangleTextureMap_type = new entity(strings[2120], false, 547, IFC4X3_TC1_IfcIndexedTextureMap_type);
    IFC4X3_TC1_IfcIrregularTimeSeries_type = new entity(strings[2121], false, 560, IFC4X3_TC1_IfcTimeSeries_type);
    IFC4X3_TC1_IfcLagTime_type = new entity(strings[2122], false, 576, IFC4X3_TC1_IfcSchedulingTime_type);
    IFC4X3_TC1_IfcLightSource_type = new entity(strings[2123], true, 595, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcLightSourceAmbient_type = new entity(strings[2124], false, 596, IFC4X3_TC1_IfcLightSource_type);
    IFC4X3_TC1_IfcLightSourceDirectional_type = new entity(strings[2125], false, 597, IFC4X3_TC1_IfcLightSource_type);
    IFC4X3_TC1_IfcLightSourceGoniometric_type = new entity(strings[2126], false, 598, IFC4X3_TC1_IfcLightSource_type);
    IFC4X3_TC1_IfcLightSourcePositional_type = new entity(strings[2127], false, 599, IFC4X3_TC1_IfcLightSource_type);
    IFC4X3_TC1_IfcLightSourceSpot_type = new entity(strings[2128], false, 600, IFC4X3_TC1_IfcLightSourcePositional_type);
    IFC4X3_TC1_IfcLinearPlacement_type = new entity(strings[2129], false, 605, IFC4X3_TC1_IfcObjectPlacement_type);
    IFC4X3_TC1_IfcLocalPlacement_type = new entity(strings[2130], false, 614, IFC4X3_TC1_IfcObjectPlacement_type);
    IFC4X3_TC1_IfcLoop_type = new entity(strings[2131], false, 617, IFC4X3_TC1_IfcTopologicalRepresentationItem_type);
    IFC4X3_TC1_IfcMappedItem_type = new entity(strings[2132], false, 626, IFC4X3_TC1_IfcRepresentationItem_type);
    IFC4X3_TC1_IfcMaterial_type = new entity(strings[2133], false, 635, IFC4X3_TC1_IfcMaterialDefinition_type);
    IFC4X3_TC1_IfcMaterialConstituent_type = new entity(strings[2134], false, 637, IFC4X3_TC1_IfcMaterialDefinition_type);
    IFC4X3_TC1_IfcMaterialConstituentSet_type = new entity(strings[2135], false, 638, IFC4X3_TC1_IfcMaterialDefinition_type);
    IFC4X3_TC1_IfcMaterialDefinitionRepresentation_type = new entity(strings[2136], false, 640, IFC4X3_TC1_IfcProductRepresentation_type);
    IFC4X3_TC1_IfcMaterialLayerSetUsage_type = new entity(strings[2137], false, 643, IFC4X3_TC1_IfcMaterialUsageDefinition_type);
    IFC4X3_TC1_IfcMaterialProfileSetUsage_type = new entity(strings[2138], false, 648, IFC4X3_TC1_IfcMaterialUsageDefinition_type);
    IFC4X3_TC1_IfcMaterialProfileSetUsageTapering_type = new entity(strings[2139], false, 649, IFC4X3_TC1_IfcMaterialProfileSetUsage_type);
    IFC4X3_TC1_IfcMaterialProperties_type = new entity(strings[2140], false, 651, IFC4X3_TC1_IfcExtendedProperties_type);
    IFC4X3_TC1_IfcMaterialRelationship_type = new entity(strings[2141], false, 652, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcMirroredProfileDef_type = new entity(strings[2142], false, 668, IFC4X3_TC1_IfcDerivedProfileDef_type);
    IFC4X3_TC1_IfcObjectDefinition_type = new entity(strings[2143], true, 699, IFC4X3_TC1_IfcRoot_type);
    IFC4X3_TC1_IfcOpenCrossProfileDef_type = new entity(strings[2144], false, 710, IFC4X3_TC1_IfcProfileDef_type);
    IFC4X3_TC1_IfcOpenShell_type = new entity(strings[2145], false, 713, IFC4X3_TC1_IfcConnectedFaceSet_type);
    IFC4X3_TC1_IfcOrganizationRelationship_type = new entity(strings[2146], false, 715, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcOrientedEdge_type = new entity(strings[2147], false, 716, IFC4X3_TC1_IfcEdge_type);
    IFC4X3_TC1_IfcParameterizedProfileDef_type = new entity(strings[2148], true, 722, IFC4X3_TC1_IfcProfileDef_type);
    IFC4X3_TC1_IfcPath_type = new entity(strings[2149], false, 724, IFC4X3_TC1_IfcTopologicalRepresentationItem_type);
    IFC4X3_TC1_IfcPhysicalComplexQuantity_type = new entity(strings[2150], false, 738, IFC4X3_TC1_IfcPhysicalQuantity_type);
    IFC4X3_TC1_IfcPixelTexture_type = new entity(strings[2151], false, 752, IFC4X3_TC1_IfcSurfaceTexture_type);
    IFC4X3_TC1_IfcPlacement_type = new entity(strings[2152], true, 753, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcPlanarExtent_type = new entity(strings[2153], false, 755, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcPoint_type = new entity(strings[2154], true, 762, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcPointByDistanceExpression_type = new entity(strings[2155], false, 763, IFC4X3_TC1_IfcPoint_type);
    IFC4X3_TC1_IfcPointOnCurve_type = new entity(strings[2156], false, 764, IFC4X3_TC1_IfcPoint_type);
    IFC4X3_TC1_IfcPointOnSurface_type = new entity(strings[2157], false, 765, IFC4X3_TC1_IfcPoint_type);
    IFC4X3_TC1_IfcPolyLoop_type = new entity(strings[2158], false, 770, IFC4X3_TC1_IfcLoop_type);
    IFC4X3_TC1_IfcPolygonalBoundedHalfSpace_type = new entity(strings[2159], false, 767, IFC4X3_TC1_IfcHalfSpaceSolid_type);
    IFC4X3_TC1_IfcPreDefinedItem_type = new entity(strings[2160], true, 782, IFC4X3_TC1_IfcPresentationItem_type);
    IFC4X3_TC1_IfcPreDefinedProperties_type = new entity(strings[2161], true, 783, IFC4X3_TC1_IfcPropertyAbstraction_type);
    IFC4X3_TC1_IfcPreDefinedTextFont_type = new entity(strings[2162], true, 785, IFC4X3_TC1_IfcPreDefinedItem_type);
    IFC4X3_TC1_IfcProductDefinitionShape_type = new entity(strings[2163], false, 799, IFC4X3_TC1_IfcProductRepresentation_type);
    IFC4X3_TC1_IfcProfileProperties_type = new entity(strings[2164], false, 804, IFC4X3_TC1_IfcExtendedProperties_type);
    IFC4X3_TC1_IfcProperty_type = new entity(strings[2165], true, 814, IFC4X3_TC1_IfcPropertyAbstraction_type);
    IFC4X3_TC1_IfcPropertyDefinition_type = new entity(strings[2166], true, 817, IFC4X3_TC1_IfcRoot_type);
    IFC4X3_TC1_IfcPropertyDependencyRelationship_type = new entity(strings[2167], false, 818, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcPropertySetDefinition_type = new entity(strings[2168], true, 824, IFC4X3_TC1_IfcPropertyDefinition_type);
    IFC4X3_TC1_IfcPropertyTemplateDefinition_type = new entity(strings[2169], true, 832, IFC4X3_TC1_IfcPropertyDefinition_type);
    IFC4X3_TC1_IfcQuantitySet_type = new entity(strings[2170], true, 846, IFC4X3_TC1_IfcPropertySetDefinition_type);
    IFC4X3_TC1_IfcRectangleProfileDef_type = new entity(strings[2171], false, 872, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcRegularTimeSeries_type = new entity(strings[2172], false, 881, IFC4X3_TC1_IfcTimeSeries_type);
    IFC4X3_TC1_IfcReinforcementBarProperties_type = new entity(strings[2173], false, 884, IFC4X3_TC1_IfcPreDefinedProperties_type);
    IFC4X3_TC1_IfcRelationship_type = new entity(strings[2174], true, 914, IFC4X3_TC1_IfcRoot_type);
    IFC4X3_TC1_IfcResourceApprovalRelationship_type = new entity(strings[2175], false, 953, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcResourceConstraintRelationship_type = new entity(strings[2176], false, 954, IFC4X3_TC1_IfcResourceLevelRelationship_type);
    IFC4X3_TC1_IfcResourceTime_type = new entity(strings[2177], false, 958, IFC4X3_TC1_IfcSchedulingTime_type);
    IFC4X3_TC1_IfcRoundedRectangleProfileDef_type = new entity(strings[2178], false, 976, IFC4X3_TC1_IfcRectangleProfileDef_type);
    IFC4X3_TC1_IfcSectionProperties_type = new entity(strings[2179], false, 989, IFC4X3_TC1_IfcPreDefinedProperties_type);
    IFC4X3_TC1_IfcSectionReinforcementProperties_type = new entity(strings[2180], false, 990, IFC4X3_TC1_IfcPreDefinedProperties_type);
    IFC4X3_TC1_IfcSectionedSpine_type = new entity(strings[2181], false, 986, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcSegment_type = new entity(strings[2182], true, 992, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcShellBasedSurfaceModel_type = new entity(strings[2183], false, 1008, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcSimpleProperty_type = new entity(strings[2184], true, 1015, IFC4X3_TC1_IfcProperty_type);
    IFC4X3_TC1_IfcSlippageConnectionCondition_type = new entity(strings[2185], false, 1028, IFC4X3_TC1_IfcStructuralConnectionCondition_type);
    IFC4X3_TC1_IfcSolidModel_type = new entity(strings[2186], true, 1033, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcStructuralLoadLinearForce_type = new entity(strings[2187], false, 1091, IFC4X3_TC1_IfcStructuralLoadStatic_type);
    IFC4X3_TC1_IfcStructuralLoadPlanarForce_type = new entity(strings[2188], false, 1093, IFC4X3_TC1_IfcStructuralLoadStatic_type);
    IFC4X3_TC1_IfcStructuralLoadSingleDisplacement_type = new entity(strings[2189], false, 1094, IFC4X3_TC1_IfcStructuralLoadStatic_type);
    IFC4X3_TC1_IfcStructuralLoadSingleDisplacementDistortion_type = new entity(strings[2190], false, 1095, IFC4X3_TC1_IfcStructuralLoadSingleDisplacement_type);
    IFC4X3_TC1_IfcStructuralLoadSingleForce_type = new entity(strings[2191], false, 1096, IFC4X3_TC1_IfcStructuralLoadStatic_type);
    IFC4X3_TC1_IfcStructuralLoadSingleForceWarping_type = new entity(strings[2192], false, 1097, IFC4X3_TC1_IfcStructuralLoadSingleForce_type);
    IFC4X3_TC1_IfcSubedge_type = new entity(strings[2193], false, 1120, IFC4X3_TC1_IfcEdge_type);
    IFC4X3_TC1_IfcSurface_type = new entity(strings[2194], true, 1121, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcSurfaceStyleRendering_type = new entity(strings[2195], false, 1135, IFC4X3_TC1_IfcSurfaceStyleShading_type);
    IFC4X3_TC1_IfcSweptAreaSolid_type = new entity(strings[2196], true, 1139, IFC4X3_TC1_IfcSolidModel_type);
    IFC4X3_TC1_IfcSweptDiskSolid_type = new entity(strings[2197], false, 1140, IFC4X3_TC1_IfcSolidModel_type);
    IFC4X3_TC1_IfcSweptDiskSolidPolygonal_type = new entity(strings[2198], false, 1141, IFC4X3_TC1_IfcSweptDiskSolid_type);
    IFC4X3_TC1_IfcSweptSurface_type = new entity(strings[2199], true, 1142, IFC4X3_TC1_IfcSurface_type);
    IFC4X3_TC1_IfcTShapeProfileDef_type = new entity(strings[2200], false, 1234, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcTessellatedItem_type = new entity(strings[2201], true, 1175, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcTextLiteral_type = new entity(strings[2202], false, 1181, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcTextLiteralWithExtent_type = new entity(strings[2203], false, 1182, IFC4X3_TC1_IfcTextLiteral_type);
    IFC4X3_TC1_IfcTextStyleFontModel_type = new entity(strings[2204], false, 1185, IFC4X3_TC1_IfcPreDefinedTextFont_type);
    IFC4X3_TC1_IfcTrapeziumProfileDef_type = new entity(strings[2205], false, 1228, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcTypeObject_type = new entity(strings[2206], false, 1238, IFC4X3_TC1_IfcObjectDefinition_type);
    IFC4X3_TC1_IfcTypeProcess_type = new entity(strings[2207], true, 1239, IFC4X3_TC1_IfcTypeObject_type);
    IFC4X3_TC1_IfcTypeProduct_type = new entity(strings[2208], false, 1240, IFC4X3_TC1_IfcTypeObject_type);
    IFC4X3_TC1_IfcTypeResource_type = new entity(strings[2209], true, 1241, IFC4X3_TC1_IfcTypeObject_type);
    IFC4X3_TC1_IfcUShapeProfileDef_type = new entity(strings[2210], false, 1252, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcVector_type = new entity(strings[2211], false, 1258, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcVertexLoop_type = new entity(strings[2212], false, 1264, IFC4X3_TC1_IfcLoop_type);
    IFC4X3_TC1_IfcZShapeProfileDef_type = new entity(strings[2213], false, 1306, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcClassificationReferenceSelect_type = new select_type(strings[2214], 170, {
        IFC4X3_TC1_IfcClassification_type,
        IFC4X3_TC1_IfcClassificationReference_type
    });
    IFC4X3_TC1_IfcClassificationSelect_type = new select_type(strings[2215], 171, {
        IFC4X3_TC1_IfcClassification_type,
        IFC4X3_TC1_IfcClassificationReference_type
    });
    IFC4X3_TC1_IfcCoordinateReferenceSystemSelect_type = new select_type(strings[2216], 245, {
        IFC4X3_TC1_IfcCoordinateReferenceSystem_type,
        IFC4X3_TC1_IfcGeometricRepresentationContext_type
    });
    IFC4X3_TC1_IfcDefinitionSelect_type = new select_type(strings[2217], 296, {
        IFC4X3_TC1_IfcObjectDefinition_type,
        IFC4X3_TC1_IfcPropertyDefinition_type
    });
    IFC4X3_TC1_IfcDocumentSelect_type = new select_type(strings[2218], 333, {
        IFC4X3_TC1_IfcDocumentInformation_type,
        IFC4X3_TC1_IfcDocumentReference_type
    });
    IFC4X3_TC1_IfcHatchLineDistanceSelect_type = new select_type(strings[2219], 526, {
        IFC4X3_TC1_IfcPositiveLengthMeasure_type,
        IFC4X3_TC1_IfcVector_type
    });
    IFC4X3_TC1_IfcMeasureValue_type = new select_type(strings[2220], 655, {
        IFC4X3_TC1_IfcAmountOfSubstanceMeasure_type,
        IFC4X3_TC1_IfcAreaMeasure_type,
        IFC4X3_TC1_IfcComplexNumber_type,
        IFC4X3_TC1_IfcContextDependentMeasure_type,
        IFC4X3_TC1_IfcCountMeasure_type,
        IFC4X3_TC1_IfcDescriptiveMeasure_type,
        IFC4X3_TC1_IfcElectricCurrentMeasure_type,
        IFC4X3_TC1_IfcLengthMeasure_type,
        IFC4X3_TC1_IfcLuminousIntensityMeasure_type,
        IFC4X3_TC1_IfcMassMeasure_type,
        IFC4X3_TC1_IfcNonNegativeLengthMeasure_type,
        IFC4X3_TC1_IfcNormalisedRatioMeasure_type,
        IFC4X3_TC1_IfcNumericMeasure_type,
        IFC4X3_TC1_IfcParameterValue_type,
        IFC4X3_TC1_IfcPlaneAngleMeasure_type,
        IFC4X3_TC1_IfcPositiveLengthMeasure_type,
        IFC4X3_TC1_IfcPositivePlaneAngleMeasure_type,
        IFC4X3_TC1_IfcPositiveRatioMeasure_type,
        IFC4X3_TC1_IfcRatioMeasure_type,
        IFC4X3_TC1_IfcSolidAngleMeasure_type,
        IFC4X3_TC1_IfcThermodynamicTemperatureMeasure_type,
        IFC4X3_TC1_IfcTimeMeasure_type,
        IFC4X3_TC1_IfcVolumeMeasure_type
    });
    IFC4X3_TC1_IfcPointOrVertexPoint_type = new select_type(strings[2221], 766, {
        IFC4X3_TC1_IfcPoint_type,
        IFC4X3_TC1_IfcVertexPoint_type
    });
    IFC4X3_TC1_IfcProductRepresentationSelect_type = new select_type(strings[2222], 801, {
        IFC4X3_TC1_IfcProductDefinitionShape_type,
        IFC4X3_TC1_IfcRepresentationMap_type
    });
    IFC4X3_TC1_IfcPropertySetDefinitionSet_type = new type_declaration(strings[2223], 826, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPropertySetDefinition_type)));
    IFC4X3_TC1_IfcResourceObjectSelect_type = new select_type(strings[2224], 956, {
        IFC4X3_TC1_IfcActorRole_type,
        IFC4X3_TC1_IfcAppliedValue_type,
        IFC4X3_TC1_IfcApproval_type,
        IFC4X3_TC1_IfcConstraint_type,
        IFC4X3_TC1_IfcContextDependentUnit_type,
        IFC4X3_TC1_IfcConversionBasedUnit_type,
        IFC4X3_TC1_IfcExternalInformation_type,
        IFC4X3_TC1_IfcExternalReference_type,
        IFC4X3_TC1_IfcMaterialDefinition_type,
        IFC4X3_TC1_IfcOrganization_type,
        IFC4X3_TC1_IfcPerson_type,
        IFC4X3_TC1_IfcPersonAndOrganization_type,
        IFC4X3_TC1_IfcPhysicalQuantity_type,
        IFC4X3_TC1_IfcProfileDef_type,
        IFC4X3_TC1_IfcPropertyAbstraction_type,
        IFC4X3_TC1_IfcShapeAspect_type,
        IFC4X3_TC1_IfcTimeSeries_type
    });
    IFC4X3_TC1_IfcTextFontSelect_type = new select_type(strings[2225], 1180, {
        IFC4X3_TC1_IfcExternallyDefinedTextFont_type,
        IFC4X3_TC1_IfcPreDefinedTextFont_type
    });
    IFC4X3_TC1_IfcValue_type = new select_type(strings[2226], 1253, {
        IFC4X3_TC1_IfcDerivedMeasureValue_type,
        IFC4X3_TC1_IfcMeasureValue_type,
        IFC4X3_TC1_IfcSimpleValue_type
    });
    IFC4X3_TC1_IfcAdvancedFace_type = new entity(strings[2227], false, 16, IFC4X3_TC1_IfcFaceSurface_type);
    IFC4X3_TC1_IfcAnnotationFillArea_type = new entity(strings[2228], false, 47, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcAsymmetricIShapeProfileDef_type = new entity(strings[2229], false, 63, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcAxis1Placement_type = new entity(strings[2230], false, 67, IFC4X3_TC1_IfcPlacement_type);
    IFC4X3_TC1_IfcAxis2Placement2D_type = new entity(strings[2231], false, 69, IFC4X3_TC1_IfcPlacement_type);
    IFC4X3_TC1_IfcAxis2Placement3D_type = new entity(strings[2232], false, 70, IFC4X3_TC1_IfcPlacement_type);
    IFC4X3_TC1_IfcAxis2PlacementLinear_type = new entity(strings[2233], false, 71, IFC4X3_TC1_IfcPlacement_type);
    IFC4X3_TC1_IfcBooleanResult_type = new entity(strings[2234], false, 90, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcBoundedSurface_type = new entity(strings[2235], true, 99, IFC4X3_TC1_IfcSurface_type);
    IFC4X3_TC1_IfcBoundingBox_type = new entity(strings[2236], false, 100, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcBoxedHalfSpace_type = new entity(strings[2237], false, 102, IFC4X3_TC1_IfcHalfSpaceSolid_type);
    IFC4X3_TC1_IfcCShapeProfileDef_type = new entity(strings[2238], false, 265, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcCartesianPoint_type = new entity(strings[2239], false, 146, IFC4X3_TC1_IfcPoint_type);
    IFC4X3_TC1_IfcCartesianPointList_type = new entity(strings[2240], true, 147, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcCartesianPointList2D_type = new entity(strings[2241], false, 148, IFC4X3_TC1_IfcCartesianPointList_type);
    IFC4X3_TC1_IfcCartesianPointList3D_type = new entity(strings[2242], false, 149, IFC4X3_TC1_IfcCartesianPointList_type);
    IFC4X3_TC1_IfcCartesianTransformationOperator_type = new entity(strings[2243], true, 150, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcCartesianTransformationOperator2D_type = new entity(strings[2244], false, 151, IFC4X3_TC1_IfcCartesianTransformationOperator_type);
    IFC4X3_TC1_IfcCartesianTransformationOperator2DnonUniform_type = new entity(strings[2245], false, 152, IFC4X3_TC1_IfcCartesianTransformationOperator2D_type);
    IFC4X3_TC1_IfcCartesianTransformationOperator3D_type = new entity(strings[2246], false, 153, IFC4X3_TC1_IfcCartesianTransformationOperator_type);
    IFC4X3_TC1_IfcCartesianTransformationOperator3DnonUniform_type = new entity(strings[2247], false, 154, IFC4X3_TC1_IfcCartesianTransformationOperator3D_type);
    IFC4X3_TC1_IfcCircleProfileDef_type = new entity(strings[2248], false, 165, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcClosedShell_type = new entity(strings[2249], false, 172, IFC4X3_TC1_IfcConnectedFaceSet_type);
    IFC4X3_TC1_IfcColourRgb_type = new entity(strings[2250], false, 179, IFC4X3_TC1_IfcColourSpecification_type);
    IFC4X3_TC1_IfcComplexProperty_type = new entity(strings[2251], false, 189, IFC4X3_TC1_IfcProperty_type);
    IFC4X3_TC1_IfcCompositeCurveSegment_type = new entity(strings[2252], false, 194, IFC4X3_TC1_IfcSegment_type);
    IFC4X3_TC1_IfcConstructionResourceType_type = new entity(strings[2253], true, 224, IFC4X3_TC1_IfcTypeResource_type);
    IFC4X3_TC1_IfcContext_type = new entity(strings[2254], true, 225, IFC4X3_TC1_IfcObjectDefinition_type);
    IFC4X3_TC1_IfcCrewResourceType_type = new entity(strings[2255], false, 260, IFC4X3_TC1_IfcConstructionResourceType_type);
    IFC4X3_TC1_IfcCsgPrimitive3D_type = new entity(strings[2256], true, 262, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcCsgSolid_type = new entity(strings[2257], false, 264, IFC4X3_TC1_IfcSolidModel_type);
    IFC4X3_TC1_IfcCurve_type = new entity(strings[2258], true, 271, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcCurveBoundedPlane_type = new entity(strings[2259], false, 272, IFC4X3_TC1_IfcBoundedSurface_type);
    IFC4X3_TC1_IfcCurveBoundedSurface_type = new entity(strings[2260], false, 273, IFC4X3_TC1_IfcBoundedSurface_type);
    IFC4X3_TC1_IfcCurveSegment_type = new entity(strings[2261], false, 279, IFC4X3_TC1_IfcSegment_type);
    IFC4X3_TC1_IfcDirection_type = new entity(strings[2262], false, 305, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcDirectrixCurveSweptAreaSolid_type = new entity(strings[2263], true, 307, IFC4X3_TC1_IfcSweptAreaSolid_type);
    IFC4X3_TC1_IfcEdgeLoop_type = new entity(strings[2264], false, 364, IFC4X3_TC1_IfcLoop_type);
    IFC4X3_TC1_IfcElementQuantity_type = new entity(strings[2265], false, 400, IFC4X3_TC1_IfcQuantitySet_type);
    IFC4X3_TC1_IfcElementType_type = new entity(strings[2266], true, 401, IFC4X3_TC1_IfcTypeProduct_type);
    IFC4X3_TC1_IfcElementarySurface_type = new entity(strings[2267], true, 393, IFC4X3_TC1_IfcSurface_type);
    IFC4X3_TC1_IfcEllipseProfileDef_type = new entity(strings[2268], false, 403, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcEventType_type = new entity(strings[2269], false, 419, IFC4X3_TC1_IfcTypeProcess_type);
    IFC4X3_TC1_IfcExtrudedAreaSolid_type = new entity(strings[2270], false, 431, IFC4X3_TC1_IfcSweptAreaSolid_type);
    IFC4X3_TC1_IfcExtrudedAreaSolidTapered_type = new entity(strings[2271], false, 432, IFC4X3_TC1_IfcExtrudedAreaSolid_type);
    IFC4X3_TC1_IfcFaceBasedSurfaceModel_type = new entity(strings[2272], false, 434, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcFillAreaStyleHatching_type = new entity(strings[2273], false, 456, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcFillAreaStyleTiles_type = new entity(strings[2274], false, 457, IFC4X3_TC1_IfcGeometricRepresentationItem_type);
    IFC4X3_TC1_IfcFixedReferenceSweptAreaSolid_type = new entity(strings[2275], false, 465, IFC4X3_TC1_IfcDirectrixCurveSweptAreaSolid_type);
    IFC4X3_TC1_IfcFurnishingElementType_type = new entity(strings[2276], false, 496, IFC4X3_TC1_IfcElementType_type);
    IFC4X3_TC1_IfcFurnitureType_type = new entity(strings[2277], false, 498, IFC4X3_TC1_IfcFurnishingElementType_type);
    IFC4X3_TC1_IfcGeographicElementType_type = new entity(strings[2278], false, 501, IFC4X3_TC1_IfcElementType_type);
    IFC4X3_TC1_IfcGeometricCurveSet_type = new entity(strings[2279], false, 503, IFC4X3_TC1_IfcGeometricSet_type);
    IFC4X3_TC1_IfcIShapeProfileDef_type = new entity(strings[2280], false, 562, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcIndexedPolygonalFace_type = new entity(strings[2281], false, 543, IFC4X3_TC1_IfcTessellatedItem_type);
    IFC4X3_TC1_IfcIndexedPolygonalFaceWithVoids_type = new entity(strings[2282], false, 544, IFC4X3_TC1_IfcIndexedPolygonalFace_type);
    IFC4X3_TC1_IfcIndexedPolygonalTextureMap_type = new entity(strings[2283], false, 545, IFC4X3_TC1_IfcIndexedTextureMap_type);
    IFC4X3_TC1_IfcLShapeProfileDef_type = new entity(strings[2284], false, 618, IFC4X3_TC1_IfcParameterizedProfileDef_type);
    IFC4X3_TC1_IfcLaborResourceType_type = new entity(strings[2285], false, 574, IFC4X3_TC1_IfcConstructionResourceType_type);
    IFC4X3_TC1_IfcLine_type = new entity(strings[2286], false, 601, IFC4X3_TC1_IfcCurve_type);
    IFC4X3_TC1_IfcManifoldSolidBrep_type = new entity(strings[2287], true, 624, IFC4X3_TC1_IfcSolidModel_type);
    IFC4X3_TC1_IfcObject_type = new entity(strings[2288], true, 698, IFC4X3_TC1_IfcObjectDefinition_type);
    IFC4X3_TC1_IfcOffsetCurve_type = new entity(strings[2289], true, 706, IFC4X3_TC1_IfcCurve_type);
    IFC4X3_TC1_IfcOffsetCurve2D_type = new entity(strings[2290], false, 707, IFC4X3_TC1_IfcOffsetCurve_type);
    IFC4X3_TC1_IfcOffsetCurve3D_type = new entity(strings[2291], false, 708, IFC4X3_TC1_IfcOffsetCurve_type);
    IFC4X3_TC1_IfcOffsetCurveByDistances_type = new entity(strings[2292], false, 709, IFC4X3_TC1_IfcOffsetCurve_type);
    IFC4X3_TC1_IfcPcurve_type = new entity(strings[2293], false, 728, IFC4X3_TC1_IfcCurve_type);
    IFC4X3_TC1_IfcPlanarBox_type = new entity(strings[2294], false, 754, IFC4X3_TC1_IfcPlanarExtent_type);
    IFC4X3_TC1_IfcPlane_type = new entity(strings[2295], false, 757, IFC4X3_TC1_IfcElementarySurface_type);
    IFC4X3_TC1_IfcPolynomialCurve_type = new entity(strings[2296], false, 771, IFC4X3_TC1_IfcCurve_type);
    IFC4X3_TC1_IfcPreDefinedColour_type = new entity(strings[2297], true, 780, IFC4X3_TC1_IfcPreDefinedItem_type);
    IFC4X3_TC1_IfcPreDefinedCurveFont_type = new entity(strings[2298], true, 781, IFC4X3_TC1_IfcPreDefinedItem_type);
    IFC4X3_TC1_IfcPreDefinedPropertySet_type = new entity(strings[2299], true, 784, IFC4X3_TC1_IfcPropertySetDefinition_type);
    IFC4X3_TC1_IfcProcedureType_type = new entity(strings[2300], false, 794, IFC4X3_TC1_IfcTypeProcess_type);
    IFC4X3_TC1_IfcProcess_type = new entity(strings[2301], true, 796, IFC4X3_TC1_IfcObject_type);
    IFC4X3_TC1_IfcProduct_type = new entity(strings[2302], true, 798, IFC4X3_TC1_IfcObject_type);
    IFC4X3_TC1_IfcProject_type = new entity(strings[2303], false, 806, IFC4X3_TC1_IfcContext_type);
    IFC4X3_TC1_IfcProjectLibrary_type = new entity(strings[2304], false, 811, IFC4X3_TC1_IfcContext_type);
    IFC4X3_TC1_IfcPropertyBoundedValue_type = new entity(strings[2305], false, 816, IFC4X3_TC1_IfcSimpleProperty_type);
    IFC4X3_TC1_IfcPropertyEnumeratedValue_type = new entity(strings[2306], false, 819, IFC4X3_TC1_IfcSimpleProperty_type);
    IFC4X3_TC1_IfcPropertyListValue_type = new entity(strings[2307], false, 821, IFC4X3_TC1_IfcSimpleProperty_type);
    IFC4X3_TC1_IfcPropertyReferenceValue_type = new entity(strings[2308], false, 822, IFC4X3_TC1_IfcSimpleProperty_type);
    IFC4X3_TC1_IfcPropertySet_type = new entity(strings[2309], false, 823, IFC4X3_TC1_IfcPropertySetDefinition_type);
    IFC4X3_TC1_IfcPropertySetTemplate_type = new entity(strings[2310], false, 827, IFC4X3_TC1_IfcPropertyTemplateDefinition_type);
    IFC4X3_TC1_IfcPropertySingleValue_type = new entity(strings[2311], false, 829, IFC4X3_TC1_IfcSimpleProperty_type);
    IFC4X3_TC1_IfcPropertyTableValue_type = new entity(strings[2312], false, 830, IFC4X3_TC1_IfcSimpleProperty_type);
    IFC4X3_TC1_IfcPropertyTemplate_type = new entity(strings[2313], true, 831, IFC4X3_TC1_IfcPropertyTemplateDefinition_type);
    IFC4X3_TC1_IfcRectangleHollowProfileDef_type = new entity(strings[2314], false, 871, IFC4X3_TC1_IfcRectangleProfileDef_type);
    IFC4X3_TC1_IfcRectangularPyramid_type = new entity(strings[2315], false, 873, IFC4X3_TC1_IfcCsgPrimitive3D_type);
    IFC4X3_TC1_IfcRectangularTrimmedSurface_type = new entity(strings[2316], false, 874, IFC4X3_TC1_IfcBoundedSurface_type);
    IFC4X3_TC1_IfcReinforcementDefinitionProperties_type = new entity(strings[2317], false, 885, IFC4X3_TC1_IfcPreDefinedPropertySet_type);
    IFC4X3_TC1_IfcRelAssigns_type = new entity(strings[2318], true, 898, IFC4X3_TC1_IfcRelationship_type);
    IFC4X3_TC1_IfcRelAssignsToActor_type = new entity(strings[2319], false, 899, IFC4X3_TC1_IfcRelAssigns_type);
    IFC4X3_TC1_IfcRelAssignsToControl_type = new entity(strings[2320], false, 900, IFC4X3_TC1_IfcRelAssigns_type);
    IFC4X3_TC1_IfcRelAssignsToGroup_type = new entity(strings[2321], false, 901, IFC4X3_TC1_IfcRelAssigns_type);
    IFC4X3_TC1_IfcRelAssignsToGroupByFactor_type = new entity(strings[2322], false, 902, IFC4X3_TC1_IfcRelAssignsToGroup_type);
    IFC4X3_TC1_IfcRelAssignsToProcess_type = new entity(strings[2323], false, 903, IFC4X3_TC1_IfcRelAssigns_type);
    IFC4X3_TC1_IfcRelAssignsToProduct_type = new entity(strings[2324], false, 904, IFC4X3_TC1_IfcRelAssigns_type);
    IFC4X3_TC1_IfcRelAssignsToResource_type = new entity(strings[2325], false, 905, IFC4X3_TC1_IfcRelAssigns_type);
    IFC4X3_TC1_IfcRelAssociates_type = new entity(strings[2326], true, 906, IFC4X3_TC1_IfcRelationship_type);
    IFC4X3_TC1_IfcRelAssociatesApproval_type = new entity(strings[2327], false, 907, IFC4X3_TC1_IfcRelAssociates_type);
    IFC4X3_TC1_IfcRelAssociatesClassification_type = new entity(strings[2328], false, 908, IFC4X3_TC1_IfcRelAssociates_type);
    IFC4X3_TC1_IfcRelAssociatesConstraint_type = new entity(strings[2329], false, 909, IFC4X3_TC1_IfcRelAssociates_type);
    IFC4X3_TC1_IfcRelAssociatesDocument_type = new entity(strings[2330], false, 910, IFC4X3_TC1_IfcRelAssociates_type);
    IFC4X3_TC1_IfcRelAssociatesLibrary_type = new entity(strings[2331], false, 911, IFC4X3_TC1_IfcRelAssociates_type);
    IFC4X3_TC1_IfcRelAssociatesMaterial_type = new entity(strings[2332], false, 912, IFC4X3_TC1_IfcRelAssociates_type);
    IFC4X3_TC1_IfcRelAssociatesProfileDef_type = new entity(strings[2333], false, 913, IFC4X3_TC1_IfcRelAssociates_type);
    IFC4X3_TC1_IfcRelConnects_type = new entity(strings[2334], true, 915, IFC4X3_TC1_IfcRelationship_type);
    IFC4X3_TC1_IfcRelConnectsElements_type = new entity(strings[2335], false, 916, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelConnectsPathElements_type = new entity(strings[2336], false, 917, IFC4X3_TC1_IfcRelConnectsElements_type);
    IFC4X3_TC1_IfcRelConnectsPortToElement_type = new entity(strings[2337], false, 919, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelConnectsPorts_type = new entity(strings[2338], false, 918, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelConnectsStructuralActivity_type = new entity(strings[2339], false, 920, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelConnectsStructuralMember_type = new entity(strings[2340], false, 921, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelConnectsWithEccentricity_type = new entity(strings[2341], false, 922, IFC4X3_TC1_IfcRelConnectsStructuralMember_type);
    IFC4X3_TC1_IfcRelConnectsWithRealizingElements_type = new entity(strings[2342], false, 923, IFC4X3_TC1_IfcRelConnectsElements_type);
    IFC4X3_TC1_IfcRelContainedInSpatialStructure_type = new entity(strings[2343], false, 924, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelCoversBldgElements_type = new entity(strings[2344], false, 925, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelCoversSpaces_type = new entity(strings[2345], false, 926, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelDeclares_type = new entity(strings[2346], false, 927, IFC4X3_TC1_IfcRelationship_type);
    IFC4X3_TC1_IfcRelDecomposes_type = new entity(strings[2347], true, 928, IFC4X3_TC1_IfcRelationship_type);
    IFC4X3_TC1_IfcRelDefines_type = new entity(strings[2348], true, 929, IFC4X3_TC1_IfcRelationship_type);
    IFC4X3_TC1_IfcRelDefinesByObject_type = new entity(strings[2349], false, 930, IFC4X3_TC1_IfcRelDefines_type);
    IFC4X3_TC1_IfcRelDefinesByProperties_type = new entity(strings[2350], false, 931, IFC4X3_TC1_IfcRelDefines_type);
    IFC4X3_TC1_IfcRelDefinesByTemplate_type = new entity(strings[2351], false, 932, IFC4X3_TC1_IfcRelDefines_type);
    IFC4X3_TC1_IfcRelDefinesByType_type = new entity(strings[2352], false, 933, IFC4X3_TC1_IfcRelDefines_type);
    IFC4X3_TC1_IfcRelFillsElement_type = new entity(strings[2353], false, 934, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelFlowControlElements_type = new entity(strings[2354], false, 935, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelInterferesElements_type = new entity(strings[2355], false, 936, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelNests_type = new entity(strings[2356], false, 937, IFC4X3_TC1_IfcRelDecomposes_type);
    IFC4X3_TC1_IfcRelPositions_type = new entity(strings[2357], false, 938, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelProjectsElement_type = new entity(strings[2358], false, 939, IFC4X3_TC1_IfcRelDecomposes_type);
    IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type = new entity(strings[2359], false, 940, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelSequence_type = new entity(strings[2360], false, 941, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelServicesBuildings_type = new entity(strings[2361], false, 942, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelSpaceBoundary_type = new entity(strings[2362], false, 943, IFC4X3_TC1_IfcRelConnects_type);
    IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type = new entity(strings[2363], false, 944, IFC4X3_TC1_IfcRelSpaceBoundary_type);
    IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type = new entity(strings[2364], false, 945, IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type);
    IFC4X3_TC1_IfcRelVoidsElement_type = new entity(strings[2365], false, 946, IFC4X3_TC1_IfcRelDecomposes_type);
    IFC4X3_TC1_IfcReparametrisedCompositeCurveSegment_type = new entity(strings[2366], false, 947, IFC4X3_TC1_IfcCompositeCurveSegment_type);
    IFC4X3_TC1_IfcResource_type = new entity(strings[2367], true, 952, IFC4X3_TC1_IfcObject_type);
    IFC4X3_TC1_IfcRevolvedAreaSolid_type = new entity(strings[2368], false, 959, IFC4X3_TC1_IfcSweptAreaSolid_type);
    IFC4X3_TC1_IfcRevolvedAreaSolidTapered_type = new entity(strings[2369], false, 960, IFC4X3_TC1_IfcRevolvedAreaSolid_type);
    IFC4X3_TC1_IfcRightCircularCone_type = new entity(strings[2370], false, 961, IFC4X3_TC1_IfcCsgPrimitive3D_type);
    IFC4X3_TC1_IfcRightCircularCylinder_type = new entity(strings[2371], false, 962, IFC4X3_TC1_IfcCsgPrimitive3D_type);
    IFC4X3_TC1_IfcSectionedSolid_type = new entity(strings[2372], true, 984, IFC4X3_TC1_IfcSolidModel_type);
    IFC4X3_TC1_IfcSectionedSolidHorizontal_type = new entity(strings[2373], false, 985, IFC4X3_TC1_IfcSectionedSolid_type);
    IFC4X3_TC1_IfcSectionedSurface_type = new entity(strings[2374], false, 987, IFC4X3_TC1_IfcSurface_type);
    IFC4X3_TC1_IfcSimplePropertyTemplate_type = new entity(strings[2375], false, 1016, IFC4X3_TC1_IfcPropertyTemplate_type);
    IFC4X3_TC1_IfcSpatialElement_type = new entity(strings[2376], true, 1046, IFC4X3_TC1_IfcProduct_type);
    IFC4X3_TC1_IfcSpatialElementType_type = new entity(strings[2377], true, 1047, IFC4X3_TC1_IfcTypeProduct_type);
    IFC4X3_TC1_IfcSpatialStructureElement_type = new entity(strings[2378], true, 1049, IFC4X3_TC1_IfcSpatialElement_type);
    IFC4X3_TC1_IfcSpatialStructureElementType_type = new entity(strings[2379], true, 1050, IFC4X3_TC1_IfcSpatialElementType_type);
    IFC4X3_TC1_IfcSpatialZone_type = new entity(strings[2380], false, 1051, IFC4X3_TC1_IfcSpatialElement_type);
    IFC4X3_TC1_IfcSpatialZoneType_type = new entity(strings[2381], false, 1052, IFC4X3_TC1_IfcSpatialElementType_type);
    IFC4X3_TC1_IfcSphere_type = new entity(strings[2382], false, 1058, IFC4X3_TC1_IfcCsgPrimitive3D_type);
    IFC4X3_TC1_IfcSphericalSurface_type = new entity(strings[2383], false, 1059, IFC4X3_TC1_IfcElementarySurface_type);
    IFC4X3_TC1_IfcSpiral_type = new entity(strings[2384], true, 1060, IFC4X3_TC1_IfcCurve_type);
    IFC4X3_TC1_IfcStructuralActivity_type = new entity(strings[2385], true, 1073, IFC4X3_TC1_IfcProduct_type);
    IFC4X3_TC1_IfcStructuralItem_type = new entity(strings[2386], true, 1085, IFC4X3_TC1_IfcProduct_type);
    IFC4X3_TC1_IfcStructuralMember_type = new entity(strings[2387], true, 1100, IFC4X3_TC1_IfcStructuralItem_type);
    IFC4X3_TC1_IfcStructuralReaction_type = new entity(strings[2388], true, 1105, IFC4X3_TC1_IfcStructuralActivity_type);
    IFC4X3_TC1_IfcStructuralSurfaceMember_type = new entity(strings[2389], false, 1110, IFC4X3_TC1_IfcStructuralMember_type);
    IFC4X3_TC1_IfcStructuralSurfaceMemberVarying_type = new entity(strings[2390], false, 1112, IFC4X3_TC1_IfcStructuralSurfaceMember_type);
    IFC4X3_TC1_IfcStructuralSurfaceReaction_type = new entity(strings[2391], false, 1113, IFC4X3_TC1_IfcStructuralReaction_type);
    IFC4X3_TC1_IfcSubContractResourceType_type = new entity(strings[2392], false, 1118, IFC4X3_TC1_IfcConstructionResourceType_type);
    IFC4X3_TC1_IfcSurfaceCurve_type = new entity(strings[2393], false, 1122, IFC4X3_TC1_IfcCurve_type);
    IFC4X3_TC1_IfcSurfaceCurveSweptAreaSolid_type = new entity(strings[2394], false, 1123, IFC4X3_TC1_IfcDirectrixCurveSweptAreaSolid_type);
    IFC4X3_TC1_IfcSurfaceOfLinearExtrusion_type = new entity(strings[2395], false, 1126, IFC4X3_TC1_IfcSweptSurface_type);
    IFC4X3_TC1_IfcSurfaceOfRevolution_type = new entity(strings[2396], false, 1127, IFC4X3_TC1_IfcSweptSurface_type);
    IFC4X3_TC1_IfcSystemFurnitureElementType_type = new entity(strings[2397], false, 1148, IFC4X3_TC1_IfcFurnishingElementType_type);
    IFC4X3_TC1_IfcTask_type = new entity(strings[2398], false, 1156, IFC4X3_TC1_IfcProcess_type);
    IFC4X3_TC1_IfcTaskType_type = new entity(strings[2399], false, 1160, IFC4X3_TC1_IfcTypeProcess_type);
    IFC4X3_TC1_IfcTessellatedFaceSet_type = new entity(strings[2400], true, 1174, IFC4X3_TC1_IfcTessellatedItem_type);
    IFC4X3_TC1_IfcThirdOrderPolynomialSpiral_type = new entity(strings[2401], false, 1202, IFC4X3_TC1_IfcSpiral_type);
    IFC4X3_TC1_IfcToroidalSurface_type = new entity(strings[2402], false, 1213, IFC4X3_TC1_IfcElementarySurface_type);
    IFC4X3_TC1_IfcTransportationDeviceType_type = new entity(strings[2403], true, 1224, IFC4X3_TC1_IfcElementType_type);
    IFC4X3_TC1_IfcTriangulatedFaceSet_type = new entity(strings[2404], false, 1229, IFC4X3_TC1_IfcTessellatedFaceSet_type);
    IFC4X3_TC1_IfcTriangulatedIrregularNetwork_type = new entity(strings[2405], false, 1230, IFC4X3_TC1_IfcTriangulatedFaceSet_type);
    IFC4X3_TC1_IfcVehicleType_type = new entity(strings[2406], false, 1261, IFC4X3_TC1_IfcTransportationDeviceType_type);
    IFC4X3_TC1_IfcWindowLiningProperties_type = new entity(strings[2407], false, 1290, IFC4X3_TC1_IfcPreDefinedPropertySet_type);
    IFC4X3_TC1_IfcWindowPanelProperties_type = new entity(strings[2408], false, 1293, IFC4X3_TC1_IfcPreDefinedPropertySet_type);
    IFC4X3_TC1_IfcAppliedValueSelect_type = new select_type(strings[2409], 51, {
        IFC4X3_TC1_IfcMeasureWithUnit_type,
        IFC4X3_TC1_IfcReference_type,
        IFC4X3_TC1_IfcValue_type
    });
    IFC4X3_TC1_IfcAxis2Placement_type = new select_type(strings[2410], 68, {
        IFC4X3_TC1_IfcAxis2Placement2D_type,
        IFC4X3_TC1_IfcAxis2Placement3D_type
    });
    IFC4X3_TC1_IfcBooleanOperand_type = new select_type(strings[2411], 88, {
        IFC4X3_TC1_IfcBooleanResult_type,
        IFC4X3_TC1_IfcCsgPrimitive3D_type,
        IFC4X3_TC1_IfcHalfSpaceSolid_type,
        IFC4X3_TC1_IfcSolidModel_type,
        IFC4X3_TC1_IfcTessellatedFaceSet_type
    });
    IFC4X3_TC1_IfcColour_type = new select_type(strings[2412], 177, {
        IFC4X3_TC1_IfcColourSpecification_type,
        IFC4X3_TC1_IfcPreDefinedColour_type
    });
    IFC4X3_TC1_IfcColourOrFactor_type = new select_type(strings[2413], 178, {
        IFC4X3_TC1_IfcColourRgb_type,
        IFC4X3_TC1_IfcNormalisedRatioMeasure_type
    });
    IFC4X3_TC1_IfcCsgSelect_type = new select_type(strings[2414], 263, {
        IFC4X3_TC1_IfcBooleanResult_type,
        IFC4X3_TC1_IfcCsgPrimitive3D_type
    });
    IFC4X3_TC1_IfcCurveStyleFontSelect_type = new select_type(strings[2415], 284, {
        IFC4X3_TC1_IfcCurveStyleFont_type,
        IFC4X3_TC1_IfcPreDefinedCurveFont_type
    });
    IFC4X3_TC1_IfcFillStyleSelect_type = new select_type(strings[2416], 458, {
        IFC4X3_TC1_IfcColour_type,
        IFC4X3_TC1_IfcExternallyDefinedHatchStyle_type,
        IFC4X3_TC1_IfcFillAreaStyleHatching_type,
        IFC4X3_TC1_IfcFillAreaStyleTiles_type
    });
    IFC4X3_TC1_IfcGeometricSetSelect_type = new select_type(strings[2417], 509, {
        IFC4X3_TC1_IfcCurve_type,
        IFC4X3_TC1_IfcPoint_type,
        IFC4X3_TC1_IfcSurface_type
    });
    IFC4X3_TC1_IfcGridPlacementDirectionSelect_type = new select_type(strings[2418], 522, {
        IFC4X3_TC1_IfcDirection_type,
        IFC4X3_TC1_IfcVirtualGridIntersection_type
    });
    IFC4X3_TC1_IfcMetricValueSelect_type = new select_type(strings[2419], 667, {
        IFC4X3_TC1_IfcAppliedValue_type,
        IFC4X3_TC1_IfcMeasureWithUnit_type,
        IFC4X3_TC1_IfcReference_type,
        IFC4X3_TC1_IfcTable_type,
        IFC4X3_TC1_IfcTimeSeries_type,
        IFC4X3_TC1_IfcValue_type
    });
    IFC4X3_TC1_IfcProcessSelect_type = new select_type(strings[2420], 797, {
        IFC4X3_TC1_IfcProcess_type,
        IFC4X3_TC1_IfcTypeProcess_type
    });
    IFC4X3_TC1_IfcProductSelect_type = new select_type(strings[2421], 802, {
        IFC4X3_TC1_IfcProduct_type,
        IFC4X3_TC1_IfcTypeProduct_type
    });
    IFC4X3_TC1_IfcPropertySetDefinitionSelect_type = new select_type(strings[2422], 825, {
        IFC4X3_TC1_IfcPropertySetDefinition_type,
        IFC4X3_TC1_IfcPropertySetDefinitionSet_type
    });
    IFC4X3_TC1_IfcResourceSelect_type = new select_type(strings[2423], 957, {
        IFC4X3_TC1_IfcResource_type,
        IFC4X3_TC1_IfcTypeResource_type
    });
    IFC4X3_TC1_IfcShell_type = new select_type(strings[2424], 1007, {
        IFC4X3_TC1_IfcClosedShell_type,
        IFC4X3_TC1_IfcOpenShell_type
    });
    IFC4X3_TC1_IfcSolidOrShell_type = new select_type(strings[2425], 1034, {
        IFC4X3_TC1_IfcClosedShell_type,
        IFC4X3_TC1_IfcSolidModel_type
    });
    IFC4X3_TC1_IfcSurfaceOrFaceSurface_type = new select_type(strings[2426], 1128, {
        IFC4X3_TC1_IfcFaceBasedSurfaceModel_type,
        IFC4X3_TC1_IfcFaceSurface_type,
        IFC4X3_TC1_IfcSurface_type
    });
    IFC4X3_TC1_IfcTrimmingSelect_type = new select_type(strings[2427], 1233, {
        IFC4X3_TC1_IfcCartesianPoint_type,
        IFC4X3_TC1_IfcParameterValue_type
    });
    IFC4X3_TC1_IfcVectorOrDirection_type = new select_type(strings[2428], 1259, {
        IFC4X3_TC1_IfcDirection_type,
        IFC4X3_TC1_IfcVector_type
    });
    IFC4X3_TC1_IfcActor_type = new entity(strings[2429], false, 6, IFC4X3_TC1_IfcObject_type);
    IFC4X3_TC1_IfcAdvancedBrep_type = new entity(strings[2430], false, 14, IFC4X3_TC1_IfcManifoldSolidBrep_type);
    IFC4X3_TC1_IfcAdvancedBrepWithVoids_type = new entity(strings[2431], false, 15, IFC4X3_TC1_IfcAdvancedBrep_type);
    IFC4X3_TC1_IfcAnnotation_type = new entity(strings[2432], false, 46, IFC4X3_TC1_IfcProduct_type);
    IFC4X3_TC1_IfcBSplineSurface_type = new entity(strings[2433], true, 110, IFC4X3_TC1_IfcBoundedSurface_type);
    IFC4X3_TC1_IfcBSplineSurfaceWithKnots_type = new entity(strings[2434], false, 112, IFC4X3_TC1_IfcBSplineSurface_type);
    IFC4X3_TC1_IfcBlock_type = new entity(strings[2435], false, 82, IFC4X3_TC1_IfcCsgPrimitive3D_type);
    IFC4X3_TC1_IfcBooleanClippingResult_type = new entity(strings[2436], false, 87, IFC4X3_TC1_IfcBooleanResult_type);
    IFC4X3_TC1_IfcBoundedCurve_type = new entity(strings[2437], true, 98, IFC4X3_TC1_IfcCurve_type);
    IFC4X3_TC1_IfcBuildingStorey_type = new entity(strings[2438], false, 120, IFC4X3_TC1_IfcSpatialStructureElement_type);
    IFC4X3_TC1_IfcBuiltElementType_type = new entity(strings[2439], false, 124, IFC4X3_TC1_IfcElementType_type);
    IFC4X3_TC1_IfcChimneyType_type = new entity(strings[2440], false, 161, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcCircleHollowProfileDef_type = new entity(strings[2441], false, 164, IFC4X3_TC1_IfcCircleProfileDef_type);
    IFC4X3_TC1_IfcCivilElementType_type = new entity(strings[2442], false, 167, IFC4X3_TC1_IfcElementType_type);
    IFC4X3_TC1_IfcClothoid_type = new entity(strings[2443], false, 173, IFC4X3_TC1_IfcSpiral_type);
    IFC4X3_TC1_IfcColumnType_type = new entity(strings[2444], false, 183, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcComplexPropertyTemplate_type = new entity(strings[2445], false, 190, IFC4X3_TC1_IfcPropertyTemplate_type);
    IFC4X3_TC1_IfcCompositeCurve_type = new entity(strings[2446], false, 192, IFC4X3_TC1_IfcBoundedCurve_type);
    IFC4X3_TC1_IfcCompositeCurveOnSurface_type = new entity(strings[2447], false, 193, IFC4X3_TC1_IfcCompositeCurve_type);
    IFC4X3_TC1_IfcConic_type = new entity(strings[2448], true, 203, IFC4X3_TC1_IfcCurve_type);
    IFC4X3_TC1_IfcConstructionEquipmentResourceType_type = new entity(strings[2449], false, 215, IFC4X3_TC1_IfcConstructionResourceType_type);
    IFC4X3_TC1_IfcConstructionMaterialResourceType_type = new entity(strings[2450], false, 218, IFC4X3_TC1_IfcConstructionResourceType_type);
    IFC4X3_TC1_IfcConstructionProductResourceType_type = new entity(strings[2451], false, 221, IFC4X3_TC1_IfcConstructionResourceType_type);
    IFC4X3_TC1_IfcConstructionResource_type = new entity(strings[2452], true, 223, IFC4X3_TC1_IfcResource_type);
    IFC4X3_TC1_IfcControl_type = new entity(strings[2453], true, 228, IFC4X3_TC1_IfcObject_type);
    IFC4X3_TC1_IfcCosineSpiral_type = new entity(strings[2454], false, 246, IFC4X3_TC1_IfcSpiral_type);
    IFC4X3_TC1_IfcCostItem_type = new entity(strings[2455], false, 247, IFC4X3_TC1_IfcControl_type);
    IFC4X3_TC1_IfcCostSchedule_type = new entity(strings[2456], false, 249, IFC4X3_TC1_IfcControl_type);
    IFC4X3_TC1_IfcCourseType_type = new entity(strings[2457], false, 254, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcCoveringType_type = new entity(strings[2458], false, 257, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcCrewResource_type = new entity(strings[2459], false, 259, IFC4X3_TC1_IfcConstructionResource_type);
    IFC4X3_TC1_IfcCurtainWallType_type = new entity(strings[2460], false, 268, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcCylindricalSurface_type = new entity(strings[2461], false, 285, IFC4X3_TC1_IfcElementarySurface_type);
    IFC4X3_TC1_IfcDeepFoundationType_type = new entity(strings[2462], false, 295, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcDirectrixDerivedReferenceSweptAreaSolid_type = new entity(strings[2463], false, 308, IFC4X3_TC1_IfcFixedReferenceSweptAreaSolid_type);
    IFC4X3_TC1_IfcDistributionElementType_type = new entity(strings[2464], false, 322, IFC4X3_TC1_IfcElementType_type);
    IFC4X3_TC1_IfcDistributionFlowElementType_type = new entity(strings[2465], true, 324, IFC4X3_TC1_IfcDistributionElementType_type);
    IFC4X3_TC1_IfcDoorLiningProperties_type = new entity(strings[2466], false, 336, IFC4X3_TC1_IfcPreDefinedPropertySet_type);
    IFC4X3_TC1_IfcDoorPanelProperties_type = new entity(strings[2467], false, 339, IFC4X3_TC1_IfcPreDefinedPropertySet_type);
    IFC4X3_TC1_IfcDoorType_type = new entity(strings[2468], false, 340, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcDraughtingPreDefinedColour_type = new entity(strings[2469], false, 344, IFC4X3_TC1_IfcPreDefinedColour_type);
    IFC4X3_TC1_IfcDraughtingPreDefinedCurveFont_type = new entity(strings[2470], false, 345, IFC4X3_TC1_IfcPreDefinedCurveFont_type);
    IFC4X3_TC1_IfcElement_type = new entity(strings[2471], true, 392, IFC4X3_TC1_IfcProduct_type);
    IFC4X3_TC1_IfcElementAssembly_type = new entity(strings[2472], false, 394, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcElementAssemblyType_type = new entity(strings[2473], false, 395, IFC4X3_TC1_IfcElementType_type);
    IFC4X3_TC1_IfcElementComponent_type = new entity(strings[2474], true, 397, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcElementComponentType_type = new entity(strings[2475], true, 398, IFC4X3_TC1_IfcElementType_type);
    IFC4X3_TC1_IfcEllipse_type = new entity(strings[2476], false, 402, IFC4X3_TC1_IfcConic_type);
    IFC4X3_TC1_IfcEnergyConversionDeviceType_type = new entity(strings[2477], true, 405, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcEngineType_type = new entity(strings[2478], false, 408, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcEvaporativeCoolerType_type = new entity(strings[2479], false, 411, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcEvaporatorType_type = new entity(strings[2480], false, 414, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcEvent_type = new entity(strings[2481], false, 416, IFC4X3_TC1_IfcProcess_type);
    IFC4X3_TC1_IfcExternalSpatialStructureElement_type = new entity(strings[2482], true, 430, IFC4X3_TC1_IfcSpatialElement_type);
    IFC4X3_TC1_IfcFacetedBrep_type = new entity(strings[2483], false, 438, IFC4X3_TC1_IfcManifoldSolidBrep_type);
    IFC4X3_TC1_IfcFacetedBrepWithVoids_type = new entity(strings[2484], false, 439, IFC4X3_TC1_IfcFacetedBrep_type);
    IFC4X3_TC1_IfcFacility_type = new entity(strings[2485], false, 440, IFC4X3_TC1_IfcSpatialStructureElement_type);
    IFC4X3_TC1_IfcFacilityPart_type = new entity(strings[2486], true, 441, IFC4X3_TC1_IfcSpatialStructureElement_type);
    IFC4X3_TC1_IfcFacilityPartCommon_type = new entity(strings[2487], false, 442, IFC4X3_TC1_IfcFacilityPart_type);
    IFC4X3_TC1_IfcFastener_type = new entity(strings[2488], false, 449, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcFastenerType_type = new entity(strings[2489], false, 450, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcFeatureElement_type = new entity(strings[2490], true, 452, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcFeatureElementAddition_type = new entity(strings[2491], true, 453, IFC4X3_TC1_IfcFeatureElement_type);
    IFC4X3_TC1_IfcFeatureElementSubtraction_type = new entity(strings[2492], true, 454, IFC4X3_TC1_IfcFeatureElement_type);
    IFC4X3_TC1_IfcFlowControllerType_type = new entity(strings[2493], true, 467, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcFlowFittingType_type = new entity(strings[2494], true, 470, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcFlowMeterType_type = new entity(strings[2495], false, 475, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcFlowMovingDeviceType_type = new entity(strings[2496], true, 478, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcFlowSegmentType_type = new entity(strings[2497], true, 480, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcFlowStorageDeviceType_type = new entity(strings[2498], true, 482, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcFlowTerminalType_type = new entity(strings[2499], true, 484, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcFlowTreatmentDeviceType_type = new entity(strings[2500], true, 486, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcFootingType_type = new entity(strings[2501], false, 491, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcFurnishingElement_type = new entity(strings[2502], false, 495, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcFurniture_type = new entity(strings[2503], false, 497, IFC4X3_TC1_IfcFurnishingElement_type);
    IFC4X3_TC1_IfcGeographicElement_type = new entity(strings[2504], false, 500, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcGeotechnicalElement_type = new entity(strings[2505], true, 513, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcGeotechnicalStratum_type = new entity(strings[2506], false, 514, IFC4X3_TC1_IfcGeotechnicalElement_type);
    IFC4X3_TC1_IfcGradientCurve_type = new entity(strings[2507], false, 518, IFC4X3_TC1_IfcCompositeCurve_type);
    IFC4X3_TC1_IfcGroup_type = new entity(strings[2508], false, 524, IFC4X3_TC1_IfcObject_type);
    IFC4X3_TC1_IfcHeatExchangerType_type = new entity(strings[2509], false, 528, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcHumidifierType_type = new entity(strings[2510], false, 533, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcImpactProtectionDevice_type = new entity(strings[2511], false, 538, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcImpactProtectionDeviceType_type = new entity(strings[2512], false, 539, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcIndexedPolyCurve_type = new entity(strings[2513], false, 542, IFC4X3_TC1_IfcBoundedCurve_type);
    IFC4X3_TC1_IfcInterceptorType_type = new entity(strings[2514], false, 552, IFC4X3_TC1_IfcFlowTreatmentDeviceType_type);
    IFC4X3_TC1_IfcIntersectionCurve_type = new entity(strings[2515], false, 556, IFC4X3_TC1_IfcSurfaceCurve_type);
    IFC4X3_TC1_IfcInventory_type = new entity(strings[2516], false, 557, IFC4X3_TC1_IfcGroup_type);
    IFC4X3_TC1_IfcJunctionBoxType_type = new entity(strings[2517], false, 565, IFC4X3_TC1_IfcFlowFittingType_type);
    IFC4X3_TC1_IfcKerbType_type = new entity(strings[2518], false, 568, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcLaborResource_type = new entity(strings[2519], false, 573, IFC4X3_TC1_IfcConstructionResource_type);
    IFC4X3_TC1_IfcLampType_type = new entity(strings[2520], false, 578, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcLightFixtureType_type = new entity(strings[2521], false, 592, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcLinearElement_type = new entity(strings[2522], false, 602, IFC4X3_TC1_IfcProduct_type);
    IFC4X3_TC1_IfcLiquidTerminalType_type = new entity(strings[2523], false, 611, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcMarineFacility_type = new entity(strings[2524], false, 627, IFC4X3_TC1_IfcFacility_type);
    IFC4X3_TC1_IfcMarinePart_type = new entity(strings[2525], false, 629, IFC4X3_TC1_IfcFacilityPart_type);
    IFC4X3_TC1_IfcMechanicalFastener_type = new entity(strings[2526], false, 657, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcMechanicalFastenerType_type = new entity(strings[2527], false, 658, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcMedicalDeviceType_type = new entity(strings[2528], false, 661, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcMemberType_type = new entity(strings[2529], false, 664, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcMobileTelecommunicationsApplianceType_type = new entity(strings[2530], false, 670, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcMooringDeviceType_type = new entity(strings[2531], false, 686, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcMotorConnectionType_type = new entity(strings[2532], false, 689, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcNavigationElementType_type = new entity(strings[2533], false, 693, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcOccupant_type = new entity(strings[2534], false, 704, IFC4X3_TC1_IfcActor_type);
    IFC4X3_TC1_IfcOpeningElement_type = new entity(strings[2535], false, 711, IFC4X3_TC1_IfcFeatureElementSubtraction_type);
    IFC4X3_TC1_IfcOutletType_type = new entity(strings[2536], false, 719, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcPavementType_type = new entity(strings[2537], false, 726, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcPerformanceHistory_type = new entity(strings[2538], false, 729, IFC4X3_TC1_IfcControl_type);
    IFC4X3_TC1_IfcPermeableCoveringProperties_type = new entity(strings[2539], false, 732, IFC4X3_TC1_IfcPreDefinedPropertySet_type);
    IFC4X3_TC1_IfcPermit_type = new entity(strings[2540], false, 733, IFC4X3_TC1_IfcControl_type);
    IFC4X3_TC1_IfcPileType_type = new entity(strings[2541], false, 744, IFC4X3_TC1_IfcDeepFoundationType_type);
    IFC4X3_TC1_IfcPipeFittingType_type = new entity(strings[2542], false, 747, IFC4X3_TC1_IfcFlowFittingType_type);
    IFC4X3_TC1_IfcPipeSegmentType_type = new entity(strings[2543], false, 750, IFC4X3_TC1_IfcFlowSegmentType_type);
    IFC4X3_TC1_IfcPlateType_type = new entity(strings[2544], false, 760, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcPolygonalFaceSet_type = new entity(strings[2545], false, 768, IFC4X3_TC1_IfcTessellatedFaceSet_type);
    IFC4X3_TC1_IfcPolyline_type = new entity(strings[2546], false, 769, IFC4X3_TC1_IfcBoundedCurve_type);
    IFC4X3_TC1_IfcPort_type = new entity(strings[2547], true, 772, IFC4X3_TC1_IfcProduct_type);
    IFC4X3_TC1_IfcPositioningElement_type = new entity(strings[2548], true, 773, IFC4X3_TC1_IfcProduct_type);
    IFC4X3_TC1_IfcProcedure_type = new entity(strings[2549], false, 793, IFC4X3_TC1_IfcProcess_type);
    IFC4X3_TC1_IfcProjectOrder_type = new entity(strings[2550], false, 812, IFC4X3_TC1_IfcControl_type);
    IFC4X3_TC1_IfcProjectionElement_type = new entity(strings[2551], false, 809, IFC4X3_TC1_IfcFeatureElementAddition_type);
    IFC4X3_TC1_IfcProtectiveDeviceType_type = new entity(strings[2552], false, 837, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcPumpType_type = new entity(strings[2553], false, 840, IFC4X3_TC1_IfcFlowMovingDeviceType_type);
    IFC4X3_TC1_IfcRailType_type = new entity(strings[2554], false, 855, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcRailingType_type = new entity(strings[2555], false, 853, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcRailway_type = new entity(strings[2556], false, 857, IFC4X3_TC1_IfcFacility_type);
    IFC4X3_TC1_IfcRailwayPart_type = new entity(strings[2557], false, 858, IFC4X3_TC1_IfcFacilityPart_type);
    IFC4X3_TC1_IfcRampFlightType_type = new entity(strings[2558], false, 863, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcRampType_type = new entity(strings[2559], false, 865, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcRationalBSplineSurfaceWithKnots_type = new entity(strings[2560], false, 869, IFC4X3_TC1_IfcBSplineSurfaceWithKnots_type);
    IFC4X3_TC1_IfcReferent_type = new entity(strings[2561], false, 878, IFC4X3_TC1_IfcPositioningElement_type);
    IFC4X3_TC1_IfcReinforcingElement_type = new entity(strings[2562], true, 891, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcReinforcingElementType_type = new entity(strings[2563], true, 892, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcReinforcingMesh_type = new entity(strings[2564], false, 893, IFC4X3_TC1_IfcReinforcingElement_type);
    IFC4X3_TC1_IfcReinforcingMeshType_type = new entity(strings[2565], false, 894, IFC4X3_TC1_IfcReinforcingElementType_type);
    IFC4X3_TC1_IfcRelAdheresToElement_type = new entity(strings[2566], false, 896, IFC4X3_TC1_IfcRelDecomposes_type);
    IFC4X3_TC1_IfcRelAggregates_type = new entity(strings[2567], false, 897, IFC4X3_TC1_IfcRelDecomposes_type);
    IFC4X3_TC1_IfcRoad_type = new entity(strings[2568], false, 963, IFC4X3_TC1_IfcFacility_type);
    IFC4X3_TC1_IfcRoadPart_type = new entity(strings[2569], false, 964, IFC4X3_TC1_IfcFacilityPart_type);
    IFC4X3_TC1_IfcRoofType_type = new entity(strings[2570], false, 969, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcSanitaryTerminalType_type = new entity(strings[2571], false, 978, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcSeamCurve_type = new entity(strings[2572], false, 981, IFC4X3_TC1_IfcSurfaceCurve_type);
    IFC4X3_TC1_IfcSecondOrderPolynomialSpiral_type = new entity(strings[2573], false, 982, IFC4X3_TC1_IfcSpiral_type);
    IFC4X3_TC1_IfcSegmentedReferenceCurve_type = new entity(strings[2574], false, 993, IFC4X3_TC1_IfcCompositeCurve_type);
    IFC4X3_TC1_IfcSeventhOrderPolynomialSpiral_type = new entity(strings[2575], false, 999, IFC4X3_TC1_IfcSpiral_type);
    IFC4X3_TC1_IfcShadingDeviceType_type = new entity(strings[2576], false, 1001, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcSign_type = new entity(strings[2577], false, 1009, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcSignType_type = new entity(strings[2578], false, 1013, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcSignalType_type = new entity(strings[2579], false, 1011, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcSineSpiral_type = new entity(strings[2580], false, 1019, IFC4X3_TC1_IfcSpiral_type);
    IFC4X3_TC1_IfcSite_type = new entity(strings[2581], false, 1021, IFC4X3_TC1_IfcSpatialStructureElement_type);
    IFC4X3_TC1_IfcSlabType_type = new entity(strings[2582], false, 1026, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcSolarDeviceType_type = new entity(strings[2583], false, 1030, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcSpace_type = new entity(strings[2584], false, 1039, IFC4X3_TC1_IfcSpatialStructureElement_type);
    IFC4X3_TC1_IfcSpaceHeaterType_type = new entity(strings[2585], false, 1042, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcSpaceType_type = new entity(strings[2586], false, 1044, IFC4X3_TC1_IfcSpatialStructureElementType_type);
    IFC4X3_TC1_IfcStackTerminalType_type = new entity(strings[2587], false, 1062, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcStairFlightType_type = new entity(strings[2588], false, 1066, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcStairType_type = new entity(strings[2589], false, 1068, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcStructuralAction_type = new entity(strings[2590], true, 1072, IFC4X3_TC1_IfcStructuralActivity_type);
    IFC4X3_TC1_IfcStructuralConnection_type = new entity(strings[2591], true, 1076, IFC4X3_TC1_IfcStructuralItem_type);
    IFC4X3_TC1_IfcStructuralCurveAction_type = new entity(strings[2592], false, 1078, IFC4X3_TC1_IfcStructuralAction_type);
    IFC4X3_TC1_IfcStructuralCurveConnection_type = new entity(strings[2593], false, 1080, IFC4X3_TC1_IfcStructuralConnection_type);
    IFC4X3_TC1_IfcStructuralCurveMember_type = new entity(strings[2594], false, 1081, IFC4X3_TC1_IfcStructuralMember_type);
    IFC4X3_TC1_IfcStructuralCurveMemberVarying_type = new entity(strings[2595], false, 1083, IFC4X3_TC1_IfcStructuralCurveMember_type);
    IFC4X3_TC1_IfcStructuralCurveReaction_type = new entity(strings[2596], false, 1084, IFC4X3_TC1_IfcStructuralReaction_type);
    IFC4X3_TC1_IfcStructuralLinearAction_type = new entity(strings[2597], false, 1086, IFC4X3_TC1_IfcStructuralCurveAction_type);
    IFC4X3_TC1_IfcStructuralLoadGroup_type = new entity(strings[2598], false, 1090, IFC4X3_TC1_IfcGroup_type);
    IFC4X3_TC1_IfcStructuralPointAction_type = new entity(strings[2599], false, 1102, IFC4X3_TC1_IfcStructuralAction_type);
    IFC4X3_TC1_IfcStructuralPointConnection_type = new entity(strings[2600], false, 1103, IFC4X3_TC1_IfcStructuralConnection_type);
    IFC4X3_TC1_IfcStructuralPointReaction_type = new entity(strings[2601], false, 1104, IFC4X3_TC1_IfcStructuralReaction_type);
    IFC4X3_TC1_IfcStructuralResultGroup_type = new entity(strings[2602], false, 1106, IFC4X3_TC1_IfcGroup_type);
    IFC4X3_TC1_IfcStructuralSurfaceAction_type = new entity(strings[2603], false, 1107, IFC4X3_TC1_IfcStructuralAction_type);
    IFC4X3_TC1_IfcStructuralSurfaceConnection_type = new entity(strings[2604], false, 1109, IFC4X3_TC1_IfcStructuralConnection_type);
    IFC4X3_TC1_IfcSubContractResource_type = new entity(strings[2605], false, 1117, IFC4X3_TC1_IfcConstructionResource_type);
    IFC4X3_TC1_IfcSurfaceFeature_type = new entity(strings[2606], false, 1124, IFC4X3_TC1_IfcFeatureElement_type);
    IFC4X3_TC1_IfcSwitchingDeviceType_type = new entity(strings[2607], false, 1144, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcSystem_type = new entity(strings[2608], false, 1146, IFC4X3_TC1_IfcGroup_type);
    IFC4X3_TC1_IfcSystemFurnitureElement_type = new entity(strings[2609], false, 1147, IFC4X3_TC1_IfcFurnishingElement_type);
    IFC4X3_TC1_IfcTankType_type = new entity(strings[2610], false, 1154, IFC4X3_TC1_IfcFlowStorageDeviceType_type);
    IFC4X3_TC1_IfcTendon_type = new entity(strings[2611], false, 1165, IFC4X3_TC1_IfcReinforcingElement_type);
    IFC4X3_TC1_IfcTendonAnchor_type = new entity(strings[2612], false, 1166, IFC4X3_TC1_IfcReinforcingElement_type);
    IFC4X3_TC1_IfcTendonAnchorType_type = new entity(strings[2613], false, 1167, IFC4X3_TC1_IfcReinforcingElementType_type);
    IFC4X3_TC1_IfcTendonConduit_type = new entity(strings[2614], false, 1169, IFC4X3_TC1_IfcReinforcingElement_type);
    IFC4X3_TC1_IfcTendonConduitType_type = new entity(strings[2615], false, 1170, IFC4X3_TC1_IfcReinforcingElementType_type);
    IFC4X3_TC1_IfcTendonType_type = new entity(strings[2616], false, 1172, IFC4X3_TC1_IfcReinforcingElementType_type);
    IFC4X3_TC1_IfcTrackElementType_type = new entity(strings[2617], false, 1216, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcTransformerType_type = new entity(strings[2618], false, 1219, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcTransportElementType_type = new entity(strings[2619], false, 1226, IFC4X3_TC1_IfcTransportationDeviceType_type);
    IFC4X3_TC1_IfcTransportationDevice_type = new entity(strings[2620], true, 1223, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcTrimmedCurve_type = new entity(strings[2621], false, 1231, IFC4X3_TC1_IfcBoundedCurve_type);
    IFC4X3_TC1_IfcTubeBundleType_type = new entity(strings[2622], false, 1236, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcUnitaryEquipmentType_type = new entity(strings[2623], false, 1247, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcValveType_type = new entity(strings[2624], false, 1255, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcVehicle_type = new entity(strings[2625], false, 1260, IFC4X3_TC1_IfcTransportationDevice_type);
    IFC4X3_TC1_IfcVibrationDamper_type = new entity(strings[2626], false, 1266, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcVibrationDamperType_type = new entity(strings[2627], false, 1267, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcVibrationIsolator_type = new entity(strings[2628], false, 1269, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcVibrationIsolatorType_type = new entity(strings[2629], false, 1270, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcVirtualElement_type = new entity(strings[2630], false, 1272, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcVoidingFeature_type = new entity(strings[2631], false, 1275, IFC4X3_TC1_IfcFeatureElementSubtraction_type);
    IFC4X3_TC1_IfcWallType_type = new entity(strings[2632], false, 1281, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcWasteTerminalType_type = new entity(strings[2633], false, 1287, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcWindowType_type = new entity(strings[2634], false, 1294, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcWorkCalendar_type = new entity(strings[2635], false, 1297, IFC4X3_TC1_IfcControl_type);
    IFC4X3_TC1_IfcWorkControl_type = new entity(strings[2636], true, 1299, IFC4X3_TC1_IfcControl_type);
    IFC4X3_TC1_IfcWorkPlan_type = new entity(strings[2637], false, 1300, IFC4X3_TC1_IfcWorkControl_type);
    IFC4X3_TC1_IfcWorkSchedule_type = new entity(strings[2638], false, 1302, IFC4X3_TC1_IfcWorkControl_type);
    IFC4X3_TC1_IfcZone_type = new entity(strings[2639], false, 1305, IFC4X3_TC1_IfcSystem_type);
    IFC4X3_TC1_IfcCurveFontOrScaledCurveFontSelect_type = new select_type(strings[2640], 274, {
        IFC4X3_TC1_IfcCurveStyleFontAndScaling_type,
        IFC4X3_TC1_IfcCurveStyleFontSelect_type
    });
    IFC4X3_TC1_IfcCurveOnSurface_type = new select_type(strings[2641], 277, {
        IFC4X3_TC1_IfcCompositeCurveOnSurface_type,
        IFC4X3_TC1_IfcPcurve_type,
        IFC4X3_TC1_IfcSurfaceCurve_type
    });
    IFC4X3_TC1_IfcCurveOrEdgeCurve_type = new select_type(strings[2642], 278, {
        IFC4X3_TC1_IfcBoundedCurve_type,
        IFC4X3_TC1_IfcEdgeCurve_type
    });
    IFC4X3_TC1_IfcInterferenceSelect_type = new select_type(strings[2643], 554, {
        IFC4X3_TC1_IfcElement_type,
        IFC4X3_TC1_IfcSpatialElement_type
    });
    IFC4X3_TC1_IfcSpatialReferenceSelect_type = new select_type(strings[2644], 1048, {
        IFC4X3_TC1_IfcGroup_type,
        IFC4X3_TC1_IfcProduct_type
    });
    IFC4X3_TC1_IfcStructuralActivityAssignmentSelect_type = new select_type(strings[2645], 1074, {
        IFC4X3_TC1_IfcElement_type,
        IFC4X3_TC1_IfcStructuralItem_type
    });
    IFC4X3_TC1_IfcActionRequest_type = new entity(strings[2646], false, 2, IFC4X3_TC1_IfcControl_type);
    IFC4X3_TC1_IfcAirTerminalBoxType_type = new entity(strings[2647], false, 19, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcAirTerminalType_type = new entity(strings[2648], false, 21, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcAirToAirHeatRecoveryType_type = new entity(strings[2649], false, 24, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcAlignmentCant_type = new entity(strings[2650], false, 30, IFC4X3_TC1_IfcLinearElement_type);
    IFC4X3_TC1_IfcAlignmentHorizontal_type = new entity(strings[2651], false, 33, IFC4X3_TC1_IfcLinearElement_type);
    IFC4X3_TC1_IfcAlignmentSegment_type = new entity(strings[2652], false, 37, IFC4X3_TC1_IfcLinearElement_type);
    IFC4X3_TC1_IfcAlignmentVertical_type = new entity(strings[2653], false, 39, IFC4X3_TC1_IfcLinearElement_type);
    IFC4X3_TC1_IfcAsset_type = new entity(strings[2654], false, 62, IFC4X3_TC1_IfcGroup_type);
    IFC4X3_TC1_IfcAudioVisualApplianceType_type = new entity(strings[2655], false, 65, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcBSplineCurve_type = new entity(strings[2656], true, 107, IFC4X3_TC1_IfcBoundedCurve_type);
    IFC4X3_TC1_IfcBSplineCurveWithKnots_type = new entity(strings[2657], false, 109, IFC4X3_TC1_IfcBSplineCurve_type);
    IFC4X3_TC1_IfcBeamType_type = new entity(strings[2658], false, 73, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcBearingType_type = new entity(strings[2659], false, 76, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcBoilerType_type = new entity(strings[2660], false, 84, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcBoundaryCurve_type = new entity(strings[2661], false, 93, IFC4X3_TC1_IfcCompositeCurveOnSurface_type);
    IFC4X3_TC1_IfcBridge_type = new entity(strings[2662], false, 103, IFC4X3_TC1_IfcFacility_type);
    IFC4X3_TC1_IfcBridgePart_type = new entity(strings[2663], false, 104, IFC4X3_TC1_IfcFacilityPart_type);
    IFC4X3_TC1_IfcBuilding_type = new entity(strings[2664], false, 113, IFC4X3_TC1_IfcFacility_type);
    IFC4X3_TC1_IfcBuildingElementPart_type = new entity(strings[2665], false, 114, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcBuildingElementPartType_type = new entity(strings[2666], false, 115, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcBuildingElementProxyType_type = new entity(strings[2667], false, 118, IFC4X3_TC1_IfcBuiltElementType_type);
    IFC4X3_TC1_IfcBuildingSystem_type = new entity(strings[2668], false, 121, IFC4X3_TC1_IfcSystem_type);
    IFC4X3_TC1_IfcBuiltElement_type = new entity(strings[2669], false, 123, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcBuiltSystem_type = new entity(strings[2670], false, 125, IFC4X3_TC1_IfcSystem_type);
    IFC4X3_TC1_IfcBurnerType_type = new entity(strings[2671], false, 128, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcCableCarrierFittingType_type = new entity(strings[2672], false, 131, IFC4X3_TC1_IfcFlowFittingType_type);
    IFC4X3_TC1_IfcCableCarrierSegmentType_type = new entity(strings[2673], false, 134, IFC4X3_TC1_IfcFlowSegmentType_type);
    IFC4X3_TC1_IfcCableFittingType_type = new entity(strings[2674], false, 137, IFC4X3_TC1_IfcFlowFittingType_type);
    IFC4X3_TC1_IfcCableSegmentType_type = new entity(strings[2675], false, 140, IFC4X3_TC1_IfcFlowSegmentType_type);
    IFC4X3_TC1_IfcCaissonFoundationType_type = new entity(strings[2676], false, 143, IFC4X3_TC1_IfcDeepFoundationType_type);
    IFC4X3_TC1_IfcChillerType_type = new entity(strings[2677], false, 158, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcChimney_type = new entity(strings[2678], false, 160, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcCircle_type = new entity(strings[2679], false, 163, IFC4X3_TC1_IfcConic_type);
    IFC4X3_TC1_IfcCivilElement_type = new entity(strings[2680], false, 166, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcCoilType_type = new entity(strings[2681], false, 175, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcColumn_type = new entity(strings[2682], false, 182, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcCommunicationsApplianceType_type = new entity(strings[2683], false, 186, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcCompressorType_type = new entity(strings[2684], false, 198, IFC4X3_TC1_IfcFlowMovingDeviceType_type);
    IFC4X3_TC1_IfcCondenserType_type = new entity(strings[2685], false, 201, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcConstructionEquipmentResource_type = new entity(strings[2686], false, 214, IFC4X3_TC1_IfcConstructionResource_type);
    IFC4X3_TC1_IfcConstructionMaterialResource_type = new entity(strings[2687], false, 217, IFC4X3_TC1_IfcConstructionResource_type);
    IFC4X3_TC1_IfcConstructionProductResource_type = new entity(strings[2688], false, 220, IFC4X3_TC1_IfcConstructionResource_type);
    IFC4X3_TC1_IfcConveyorSegmentType_type = new entity(strings[2689], false, 235, IFC4X3_TC1_IfcFlowSegmentType_type);
    IFC4X3_TC1_IfcCooledBeamType_type = new entity(strings[2690], false, 238, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcCoolingTowerType_type = new entity(strings[2691], false, 241, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcCourse_type = new entity(strings[2692], false, 253, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcCovering_type = new entity(strings[2693], false, 256, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcCurtainWall_type = new entity(strings[2694], false, 267, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcDamperType_type = new entity(strings[2695], false, 287, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcDeepFoundation_type = new entity(strings[2696], false, 294, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcDiscreteAccessory_type = new entity(strings[2697], false, 309, IFC4X3_TC1_IfcElementComponent_type);
    IFC4X3_TC1_IfcDiscreteAccessoryType_type = new entity(strings[2698], false, 310, IFC4X3_TC1_IfcElementComponentType_type);
    IFC4X3_TC1_IfcDistributionBoardType_type = new entity(strings[2699], false, 313, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcDistributionChamberElementType_type = new entity(strings[2700], false, 316, IFC4X3_TC1_IfcDistributionFlowElementType_type);
    IFC4X3_TC1_IfcDistributionControlElementType_type = new entity(strings[2701], true, 320, IFC4X3_TC1_IfcDistributionElementType_type);
    IFC4X3_TC1_IfcDistributionElement_type = new entity(strings[2702], false, 321, IFC4X3_TC1_IfcElement_type);
    IFC4X3_TC1_IfcDistributionFlowElement_type = new entity(strings[2703], false, 323, IFC4X3_TC1_IfcDistributionElement_type);
    IFC4X3_TC1_IfcDistributionPort_type = new entity(strings[2704], false, 325, IFC4X3_TC1_IfcPort_type);
    IFC4X3_TC1_IfcDistributionSystem_type = new entity(strings[2705], false, 327, IFC4X3_TC1_IfcSystem_type);
    IFC4X3_TC1_IfcDoor_type = new entity(strings[2706], false, 335, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcDuctFittingType_type = new entity(strings[2707], false, 347, IFC4X3_TC1_IfcFlowFittingType_type);
    IFC4X3_TC1_IfcDuctSegmentType_type = new entity(strings[2708], false, 350, IFC4X3_TC1_IfcFlowSegmentType_type);
    IFC4X3_TC1_IfcDuctSilencerType_type = new entity(strings[2709], false, 353, IFC4X3_TC1_IfcFlowTreatmentDeviceType_type);
    IFC4X3_TC1_IfcEarthworksCut_type = new entity(strings[2710], false, 357, IFC4X3_TC1_IfcFeatureElementSubtraction_type);
    IFC4X3_TC1_IfcEarthworksElement_type = new entity(strings[2711], false, 359, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcEarthworksFill_type = new entity(strings[2712], false, 360, IFC4X3_TC1_IfcEarthworksElement_type);
    IFC4X3_TC1_IfcElectricApplianceType_type = new entity(strings[2713], false, 366, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcElectricDistributionBoardType_type = new entity(strings[2714], false, 373, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcElectricFlowStorageDeviceType_type = new entity(strings[2715], false, 376, IFC4X3_TC1_IfcFlowStorageDeviceType_type);
    IFC4X3_TC1_IfcElectricFlowTreatmentDeviceType_type = new entity(strings[2716], false, 379, IFC4X3_TC1_IfcFlowTreatmentDeviceType_type);
    IFC4X3_TC1_IfcElectricGeneratorType_type = new entity(strings[2717], false, 382, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcElectricMotorType_type = new entity(strings[2718], false, 385, IFC4X3_TC1_IfcEnergyConversionDeviceType_type);
    IFC4X3_TC1_IfcElectricTimeControlType_type = new entity(strings[2719], false, 389, IFC4X3_TC1_IfcFlowControllerType_type);
    IFC4X3_TC1_IfcEnergyConversionDevice_type = new entity(strings[2720], false, 404, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcEngine_type = new entity(strings[2721], false, 407, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcEvaporativeCooler_type = new entity(strings[2722], false, 410, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcEvaporator_type = new entity(strings[2723], false, 413, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcExternalSpatialElement_type = new entity(strings[2724], false, 428, IFC4X3_TC1_IfcExternalSpatialStructureElement_type);
    IFC4X3_TC1_IfcFanType_type = new entity(strings[2725], false, 447, IFC4X3_TC1_IfcFlowMovingDeviceType_type);
    IFC4X3_TC1_IfcFilterType_type = new entity(strings[2726], false, 460, IFC4X3_TC1_IfcFlowTreatmentDeviceType_type);
    IFC4X3_TC1_IfcFireSuppressionTerminalType_type = new entity(strings[2727], false, 463, IFC4X3_TC1_IfcFlowTerminalType_type);
    IFC4X3_TC1_IfcFlowController_type = new entity(strings[2728], false, 466, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcFlowFitting_type = new entity(strings[2729], false, 469, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcFlowInstrumentType_type = new entity(strings[2730], false, 472, IFC4X3_TC1_IfcDistributionControlElementType_type);
    IFC4X3_TC1_IfcFlowMeter_type = new entity(strings[2731], false, 474, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcFlowMovingDevice_type = new entity(strings[2732], false, 477, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcFlowSegment_type = new entity(strings[2733], false, 479, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcFlowStorageDevice_type = new entity(strings[2734], false, 481, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcFlowTerminal_type = new entity(strings[2735], false, 483, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcFlowTreatmentDevice_type = new entity(strings[2736], false, 485, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcFooting_type = new entity(strings[2737], false, 490, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcGeotechnicalAssembly_type = new entity(strings[2738], true, 512, IFC4X3_TC1_IfcGeotechnicalElement_type);
    IFC4X3_TC1_IfcGrid_type = new entity(strings[2739], false, 519, IFC4X3_TC1_IfcPositioningElement_type);
    IFC4X3_TC1_IfcHeatExchanger_type = new entity(strings[2740], false, 527, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcHumidifier_type = new entity(strings[2741], false, 532, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcInterceptor_type = new entity(strings[2742], false, 551, IFC4X3_TC1_IfcFlowTreatmentDevice_type);
    IFC4X3_TC1_IfcJunctionBox_type = new entity(strings[2743], false, 564, IFC4X3_TC1_IfcFlowFitting_type);
    IFC4X3_TC1_IfcKerb_type = new entity(strings[2744], false, 567, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcLamp_type = new entity(strings[2745], false, 577, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcLightFixture_type = new entity(strings[2746], false, 591, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcLinearPositioningElement_type = new entity(strings[2747], false, 606, IFC4X3_TC1_IfcPositioningElement_type);
    IFC4X3_TC1_IfcLiquidTerminal_type = new entity(strings[2748], false, 610, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcMedicalDevice_type = new entity(strings[2749], false, 660, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcMember_type = new entity(strings[2750], false, 663, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcMobileTelecommunicationsAppliance_type = new entity(strings[2751], false, 669, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcMooringDevice_type = new entity(strings[2752], false, 685, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcMotorConnection_type = new entity(strings[2753], false, 688, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcNavigationElement_type = new entity(strings[2754], false, 692, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcOuterBoundaryCurve_type = new entity(strings[2755], false, 717, IFC4X3_TC1_IfcBoundaryCurve_type);
    IFC4X3_TC1_IfcOutlet_type = new entity(strings[2756], false, 718, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcPavement_type = new entity(strings[2757], false, 725, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcPile_type = new entity(strings[2758], false, 742, IFC4X3_TC1_IfcDeepFoundation_type);
    IFC4X3_TC1_IfcPipeFitting_type = new entity(strings[2759], false, 746, IFC4X3_TC1_IfcFlowFitting_type);
    IFC4X3_TC1_IfcPipeSegment_type = new entity(strings[2760], false, 749, IFC4X3_TC1_IfcFlowSegment_type);
    IFC4X3_TC1_IfcPlate_type = new entity(strings[2761], false, 759, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcProtectiveDevice_type = new entity(strings[2762], false, 833, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitType_type = new entity(strings[2763], false, 835, IFC4X3_TC1_IfcDistributionControlElementType_type);
    IFC4X3_TC1_IfcPump_type = new entity(strings[2764], false, 839, IFC4X3_TC1_IfcFlowMovingDevice_type);
    IFC4X3_TC1_IfcRail_type = new entity(strings[2765], false, 851, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcRailing_type = new entity(strings[2766], false, 852, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcRamp_type = new entity(strings[2767], false, 861, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcRampFlight_type = new entity(strings[2768], false, 862, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcRationalBSplineCurveWithKnots_type = new entity(strings[2769], false, 868, IFC4X3_TC1_IfcBSplineCurveWithKnots_type);
    IFC4X3_TC1_IfcReinforcedSoil_type = new entity(strings[2770], false, 882, IFC4X3_TC1_IfcEarthworksElement_type);
    IFC4X3_TC1_IfcReinforcingBar_type = new entity(strings[2771], false, 886, IFC4X3_TC1_IfcReinforcingElement_type);
    IFC4X3_TC1_IfcReinforcingBarType_type = new entity(strings[2772], false, 889, IFC4X3_TC1_IfcReinforcingElementType_type);
    IFC4X3_TC1_IfcRoof_type = new entity(strings[2773], false, 968, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcSanitaryTerminal_type = new entity(strings[2774], false, 977, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcSensorType_type = new entity(strings[2775], false, 996, IFC4X3_TC1_IfcDistributionControlElementType_type);
    IFC4X3_TC1_IfcShadingDevice_type = new entity(strings[2776], false, 1000, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcSignal_type = new entity(strings[2777], false, 1010, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcSlab_type = new entity(strings[2778], false, 1025, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcSolarDevice_type = new entity(strings[2779], false, 1029, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcSpaceHeater_type = new entity(strings[2780], false, 1041, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcStackTerminal_type = new entity(strings[2781], false, 1061, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcStair_type = new entity(strings[2782], false, 1064, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcStairFlight_type = new entity(strings[2783], false, 1065, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcStructuralAnalysisModel_type = new entity(strings[2784], false, 1075, IFC4X3_TC1_IfcSystem_type);
    IFC4X3_TC1_IfcStructuralLoadCase_type = new entity(strings[2785], false, 1088, IFC4X3_TC1_IfcStructuralLoadGroup_type);
    IFC4X3_TC1_IfcStructuralPlanarAction_type = new entity(strings[2786], false, 1101, IFC4X3_TC1_IfcStructuralSurfaceAction_type);
    IFC4X3_TC1_IfcSwitchingDevice_type = new entity(strings[2787], false, 1143, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcTank_type = new entity(strings[2788], false, 1153, IFC4X3_TC1_IfcFlowStorageDevice_type);
    IFC4X3_TC1_IfcTrackElement_type = new entity(strings[2789], false, 1215, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcTransformer_type = new entity(strings[2790], false, 1218, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcTransportElement_type = new entity(strings[2791], false, 1225, IFC4X3_TC1_IfcTransportationDevice_type);
    IFC4X3_TC1_IfcTubeBundle_type = new entity(strings[2792], false, 1235, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcUnitaryControlElementType_type = new entity(strings[2793], false, 1244, IFC4X3_TC1_IfcDistributionControlElementType_type);
    IFC4X3_TC1_IfcUnitaryEquipment_type = new entity(strings[2794], false, 1246, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcValve_type = new entity(strings[2795], false, 1254, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcWall_type = new entity(strings[2796], false, 1279, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcWallStandardCase_type = new entity(strings[2797], false, 1280, IFC4X3_TC1_IfcWall_type);
    IFC4X3_TC1_IfcWasteTerminal_type = new entity(strings[2798], false, 1286, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcWindow_type = new entity(strings[2799], false, 1289, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcSpaceBoundarySelect_type = new select_type(strings[2800], 1040, {
        IFC4X3_TC1_IfcExternalSpatialElement_type,
        IFC4X3_TC1_IfcSpace_type
    });
    IFC4X3_TC1_IfcActuatorType_type = new entity(strings[2801], false, 10, IFC4X3_TC1_IfcDistributionControlElementType_type);
    IFC4X3_TC1_IfcAirTerminal_type = new entity(strings[2802], false, 17, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcAirTerminalBox_type = new entity(strings[2803], false, 18, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcAirToAirHeatRecovery_type = new entity(strings[2804], false, 23, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcAlarmType_type = new entity(strings[2805], false, 27, IFC4X3_TC1_IfcDistributionControlElementType_type);
    IFC4X3_TC1_IfcAlignment_type = new entity(strings[2806], false, 29, IFC4X3_TC1_IfcLinearPositioningElement_type);
    IFC4X3_TC1_IfcAudioVisualAppliance_type = new entity(strings[2807], false, 64, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcBeam_type = new entity(strings[2808], false, 72, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcBearing_type = new entity(strings[2809], false, 75, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcBoiler_type = new entity(strings[2810], false, 83, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcBorehole_type = new entity(strings[2811], false, 91, IFC4X3_TC1_IfcGeotechnicalAssembly_type);
    IFC4X3_TC1_IfcBuildingElementProxy_type = new entity(strings[2812], false, 117, IFC4X3_TC1_IfcBuiltElement_type);
    IFC4X3_TC1_IfcBurner_type = new entity(strings[2813], false, 127, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcCableCarrierFitting_type = new entity(strings[2814], false, 130, IFC4X3_TC1_IfcFlowFitting_type);
    IFC4X3_TC1_IfcCableCarrierSegment_type = new entity(strings[2815], false, 133, IFC4X3_TC1_IfcFlowSegment_type);
    IFC4X3_TC1_IfcCableFitting_type = new entity(strings[2816], false, 136, IFC4X3_TC1_IfcFlowFitting_type);
    IFC4X3_TC1_IfcCableSegment_type = new entity(strings[2817], false, 139, IFC4X3_TC1_IfcFlowSegment_type);
    IFC4X3_TC1_IfcCaissonFoundation_type = new entity(strings[2818], false, 142, IFC4X3_TC1_IfcDeepFoundation_type);
    IFC4X3_TC1_IfcChiller_type = new entity(strings[2819], false, 157, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcCoil_type = new entity(strings[2820], false, 174, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcCommunicationsAppliance_type = new entity(strings[2821], false, 185, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcCompressor_type = new entity(strings[2822], false, 197, IFC4X3_TC1_IfcFlowMovingDevice_type);
    IFC4X3_TC1_IfcCondenser_type = new entity(strings[2823], false, 200, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcControllerType_type = new entity(strings[2824], false, 230, IFC4X3_TC1_IfcDistributionControlElementType_type);
    IFC4X3_TC1_IfcConveyorSegment_type = new entity(strings[2825], false, 234, IFC4X3_TC1_IfcFlowSegment_type);
    IFC4X3_TC1_IfcCooledBeam_type = new entity(strings[2826], false, 237, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcCoolingTower_type = new entity(strings[2827], false, 240, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcDamper_type = new entity(strings[2828], false, 286, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcDistributionBoard_type = new entity(strings[2829], false, 312, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcDistributionChamberElement_type = new entity(strings[2830], false, 315, IFC4X3_TC1_IfcDistributionFlowElement_type);
    IFC4X3_TC1_IfcDistributionCircuit_type = new entity(strings[2831], false, 318, IFC4X3_TC1_IfcDistributionSystem_type);
    IFC4X3_TC1_IfcDistributionControlElement_type = new entity(strings[2832], false, 319, IFC4X3_TC1_IfcDistributionElement_type);
    IFC4X3_TC1_IfcDuctFitting_type = new entity(strings[2833], false, 346, IFC4X3_TC1_IfcFlowFitting_type);
    IFC4X3_TC1_IfcDuctSegment_type = new entity(strings[2834], false, 349, IFC4X3_TC1_IfcFlowSegment_type);
    IFC4X3_TC1_IfcDuctSilencer_type = new entity(strings[2835], false, 352, IFC4X3_TC1_IfcFlowTreatmentDevice_type);
    IFC4X3_TC1_IfcElectricAppliance_type = new entity(strings[2836], false, 365, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcElectricDistributionBoard_type = new entity(strings[2837], false, 372, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcElectricFlowStorageDevice_type = new entity(strings[2838], false, 375, IFC4X3_TC1_IfcFlowStorageDevice_type);
    IFC4X3_TC1_IfcElectricFlowTreatmentDevice_type = new entity(strings[2839], false, 378, IFC4X3_TC1_IfcFlowTreatmentDevice_type);
    IFC4X3_TC1_IfcElectricGenerator_type = new entity(strings[2840], false, 381, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcElectricMotor_type = new entity(strings[2841], false, 384, IFC4X3_TC1_IfcEnergyConversionDevice_type);
    IFC4X3_TC1_IfcElectricTimeControl_type = new entity(strings[2842], false, 388, IFC4X3_TC1_IfcFlowController_type);
    IFC4X3_TC1_IfcFan_type = new entity(strings[2843], false, 446, IFC4X3_TC1_IfcFlowMovingDevice_type);
    IFC4X3_TC1_IfcFilter_type = new entity(strings[2844], false, 459, IFC4X3_TC1_IfcFlowTreatmentDevice_type);
    IFC4X3_TC1_IfcFireSuppressionTerminal_type = new entity(strings[2845], false, 462, IFC4X3_TC1_IfcFlowTerminal_type);
    IFC4X3_TC1_IfcFlowInstrument_type = new entity(strings[2846], false, 471, IFC4X3_TC1_IfcDistributionControlElement_type);
    IFC4X3_TC1_IfcGeomodel_type = new entity(strings[2847], false, 510, IFC4X3_TC1_IfcGeotechnicalAssembly_type);
    IFC4X3_TC1_IfcGeoslice_type = new entity(strings[2848], false, 511, IFC4X3_TC1_IfcGeotechnicalAssembly_type);
    IFC4X3_TC1_IfcProtectiveDeviceTrippingUnit_type = new entity(strings[2849], false, 834, IFC4X3_TC1_IfcDistributionControlElement_type);
    IFC4X3_TC1_IfcSensor_type = new entity(strings[2850], false, 995, IFC4X3_TC1_IfcDistributionControlElement_type);
    IFC4X3_TC1_IfcUnitaryControlElement_type = new entity(strings[2851], false, 1243, IFC4X3_TC1_IfcDistributionControlElement_type);
    IFC4X3_TC1_IfcActuator_type = new entity(strings[2852], false, 9, IFC4X3_TC1_IfcDistributionControlElement_type);
    IFC4X3_TC1_IfcAlarm_type = new entity(strings[2853], false, 26, IFC4X3_TC1_IfcDistributionControlElement_type);
    IFC4X3_TC1_IfcController_type = new entity(strings[2854], false, 229, IFC4X3_TC1_IfcDistributionControlElement_type);
    IFC4X3_TC1_IfcActionRequest_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcActionRequestTypeEnum_type), true),
            new attribute(strings[2856], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2857], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcActor_type->set_attributes({
            new attribute(strings[2858], new named_type(IFC4X3_TC1_IfcActorSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcActorRole_type->set_attributes({
            new attribute(strings[2859], new named_type(IFC4X3_TC1_IfcRoleEnum_type), false),
            new attribute(strings[2860], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcActuator_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcActuatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcActuatorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcActuatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAddress_type->set_attributes({
            new attribute(strings[2862], new named_type(IFC4X3_TC1_IfcAddressTypeEnum_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[2863], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcAdvancedBrep_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcAdvancedBrepWithVoids_type->set_attributes({
            new attribute(strings[2864], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcClosedShell_type)), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcAdvancedFace_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcAirTerminal_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAirTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAirTerminalBox_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAirTerminalBoxTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAirTerminalBoxType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAirTerminalBoxTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAirTerminalType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAirTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAirToAirHeatRecovery_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAirToAirHeatRecoveryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAirToAirHeatRecoveryType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAirToAirHeatRecoveryTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlarm_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAlarmTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlarmType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAlarmTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlignment_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAlignmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlignmentCant_type->set_attributes({
            new attribute(strings[2865], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlignmentCantSegment_type->set_attributes({
            new attribute(strings[2866], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2867], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[2868], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2869], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[2870], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2871], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAlignmentCantSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlignmentHorizontal_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlignmentHorizontalSegment_type->set_attributes({
            new attribute(strings[2872], new named_type(IFC4X3_TC1_IfcCartesianPoint_type), false),
            new attribute(strings[2873], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), false),
            new attribute(strings[2874], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2876], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[2877], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAlignmentHorizontalSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlignmentParameterSegment_type->set_attributes({
            new attribute(strings[2878], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2879], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcAlignmentSegment_type->set_attributes({
            new attribute(strings[2880], new named_type(IFC4X3_TC1_IfcAlignmentParameterSegment_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlignmentVertical_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAlignmentVerticalSegment_type->set_attributes({
            new attribute(strings[2866], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2867], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[2881], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2882], new named_type(IFC4X3_TC1_IfcRatioMeasure_type), false),
            new attribute(strings[2883], new named_type(IFC4X3_TC1_IfcRatioMeasure_type), false),
            new attribute(strings[2884], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAlignmentVerticalSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAnnotation_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAnnotationTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAnnotationFillArea_type->set_attributes({
            new attribute(strings[2885], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[2886], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcCurve_type)), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcApplication_type->set_attributes({
            new attribute(strings[2887], new named_type(IFC4X3_TC1_IfcOrganization_type), false),
            new attribute(strings[2888], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2889], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2890], new named_type(IFC4X3_TC1_IfcIdentifier_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcAppliedValue_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[2892], new named_type(IFC4X3_TC1_IfcAppliedValueSelect_type), true),
            new attribute(strings[2893], new named_type(IFC4X3_TC1_IfcMeasureWithUnit_type), true),
            new attribute(strings[2894], new named_type(IFC4X3_TC1_IfcDate_type), true),
            new attribute(strings[2895], new named_type(IFC4X3_TC1_IfcDate_type), true),
            new attribute(strings[2896], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2897], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2898], new named_type(IFC4X3_TC1_IfcArithmeticOperatorEnum_type), true),
            new attribute(strings[2899], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcAppliedValue_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcApproval_type->set_attributes({
            new attribute(strings[2900], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[2901], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[2856], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2902], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2903], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[2904], new named_type(IFC4X3_TC1_IfcActorSelect_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_TC1_IfcActorSelect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcApprovalRelationship_type->set_attributes({
            new attribute(strings[2906], new named_type(IFC4X3_TC1_IfcApproval_type), false),
            new attribute(strings[2907], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcApproval_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcArbitraryClosedProfileDef_type->set_attributes({
            new attribute(strings[2908], new named_type(IFC4X3_TC1_IfcCurve_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcArbitraryOpenProfileDef_type->set_attributes({
            new attribute(strings[2909], new named_type(IFC4X3_TC1_IfcBoundedCurve_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcArbitraryProfileDefWithVoids_type->set_attributes({
            new attribute(strings[2910], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcCurve_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcAsset_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2912], new named_type(IFC4X3_TC1_IfcCostValue_type), true),
            new attribute(strings[2913], new named_type(IFC4X3_TC1_IfcCostValue_type), true),
            new attribute(strings[2914], new named_type(IFC4X3_TC1_IfcCostValue_type), true),
            new attribute(strings[2915], new named_type(IFC4X3_TC1_IfcActorSelect_type), true),
            new attribute(strings[2916], new named_type(IFC4X3_TC1_IfcActorSelect_type), true),
            new attribute(strings[2917], new named_type(IFC4X3_TC1_IfcPerson_type), true),
            new attribute(strings[2918], new named_type(IFC4X3_TC1_IfcDate_type), true),
            new attribute(strings[2919], new named_type(IFC4X3_TC1_IfcCostValue_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAsymmetricIShapeProfileDef_type->set_attributes({
            new attribute(strings[2920], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2921], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2922], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2923], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2924], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2925], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2926], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2927], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2928], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2929], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[2930], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2931], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAudioVisualAppliance_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAudioVisualApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAudioVisualApplianceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAudioVisualApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcAxis1Placement_type->set_attributes({
            new attribute(strings[2932], new named_type(IFC4X3_TC1_IfcDirection_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcAxis2Placement2D_type->set_attributes({
            new attribute(strings[2933], new named_type(IFC4X3_TC1_IfcDirection_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcAxis2Placement3D_type->set_attributes({
            new attribute(strings[2932], new named_type(IFC4X3_TC1_IfcDirection_type), true),
            new attribute(strings[2933], new named_type(IFC4X3_TC1_IfcDirection_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcAxis2PlacementLinear_type->set_attributes({
            new attribute(strings[2932], new named_type(IFC4X3_TC1_IfcDirection_type), true),
            new attribute(strings[2933], new named_type(IFC4X3_TC1_IfcDirection_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcBSplineCurve_type->set_attributes({
            new attribute(strings[2934], new named_type(IFC4X3_TC1_IfcInteger_type), false),
            new attribute(strings[2935], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcCartesianPoint_type)), false),
            new attribute(strings[2936], new named_type(IFC4X3_TC1_IfcBSplineCurveForm_type), false),
            new attribute(strings[2937], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[2938], new named_type(IFC4X3_TC1_IfcLogical_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcBSplineCurveWithKnots_type->set_attributes({
            new attribute(strings[2939], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcInteger_type)), false),
            new attribute(strings[2940], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcParameterValue_type)), false),
            new attribute(strings[2941], new named_type(IFC4X3_TC1_IfcKnotType_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBSplineSurface_type->set_attributes({
            new attribute(strings[2942], new named_type(IFC4X3_TC1_IfcInteger_type), false),
            new attribute(strings[2943], new named_type(IFC4X3_TC1_IfcInteger_type), false),
            new attribute(strings[2935], new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcCartesianPoint_type))), false),
            new attribute(strings[2944], new named_type(IFC4X3_TC1_IfcBSplineSurfaceForm_type), false),
            new attribute(strings[2945], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[2946], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[2938], new named_type(IFC4X3_TC1_IfcLogical_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBSplineSurfaceWithKnots_type->set_attributes({
            new attribute(strings[2947], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcInteger_type)), false),
            new attribute(strings[2948], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcInteger_type)), false),
            new attribute(strings[2949], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcParameterValue_type)), false),
            new attribute(strings[2950], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcParameterValue_type)), false),
            new attribute(strings[2941], new named_type(IFC4X3_TC1_IfcKnotType_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBeam_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBeamTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBeamType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBeamTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBearing_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBearingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBearingType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBearingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBlobTexture_type->set_attributes({
            new attribute(strings[2951], new named_type(IFC4X3_TC1_IfcIdentifier_type), false),
            new attribute(strings[2952], new named_type(IFC4X3_TC1_IfcBinary_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBlock_type->set_attributes({
            new attribute(strings[2953], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2954], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2955], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcBoiler_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBoilerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBoilerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBoilerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBooleanClippingResult_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcBooleanResult_type->set_attributes({
            new attribute(strings[2956], new named_type(IFC4X3_TC1_IfcBooleanOperator_type), false),
            new attribute(strings[2957], new named_type(IFC4X3_TC1_IfcBooleanOperand_type), false),
            new attribute(strings[2958], new named_type(IFC4X3_TC1_IfcBooleanOperand_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcBorehole_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBoundaryCondition_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_TC1_IfcBoundaryCurve_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_TC1_IfcBoundaryEdgeCondition_type->set_attributes({
            new attribute(strings[2959], new named_type(IFC4X3_TC1_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2960], new named_type(IFC4X3_TC1_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2961], new named_type(IFC4X3_TC1_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2962], new named_type(IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionSelect_type), true),
            new attribute(strings[2963], new named_type(IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionSelect_type), true),
            new attribute(strings[2964], new named_type(IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBoundaryFaceCondition_type->set_attributes({
            new attribute(strings[2965], new named_type(IFC4X3_TC1_IfcModulusOfSubgradeReactionSelect_type), true),
            new attribute(strings[2966], new named_type(IFC4X3_TC1_IfcModulusOfSubgradeReactionSelect_type), true),
            new attribute(strings[2967], new named_type(IFC4X3_TC1_IfcModulusOfSubgradeReactionSelect_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcBoundaryNodeCondition_type->set_attributes({
            new attribute(strings[2968], new named_type(IFC4X3_TC1_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2969], new named_type(IFC4X3_TC1_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2970], new named_type(IFC4X3_TC1_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2971], new named_type(IFC4X3_TC1_IfcRotationalStiffnessSelect_type), true),
            new attribute(strings[2972], new named_type(IFC4X3_TC1_IfcRotationalStiffnessSelect_type), true),
            new attribute(strings[2973], new named_type(IFC4X3_TC1_IfcRotationalStiffnessSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBoundaryNodeConditionWarping_type->set_attributes({
            new attribute(strings[2974], new named_type(IFC4X3_TC1_IfcWarpingStiffnessSelect_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBoundedCurve_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcBoundedSurface_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcBoundingBox_type->set_attributes({
            new attribute(strings[2975], new named_type(IFC4X3_TC1_IfcCartesianPoint_type), false),
            new attribute(strings[2976], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2977], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2978], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcBoxedHalfSpace_type->set_attributes({
            new attribute(strings[2979], new named_type(IFC4X3_TC1_IfcBoundingBox_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcBridge_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBridgeTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBridgePart_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBridgePartTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuilding_type->set_attributes({
            new attribute(strings[2980], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[2981], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[2982], new named_type(IFC4X3_TC1_IfcPostalAddress_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuildingElementPart_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBuildingElementPartTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuildingElementPartType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBuildingElementPartTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuildingElementProxy_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBuildingElementProxyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuildingElementProxyType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBuildingElementProxyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuildingStorey_type->set_attributes({
            new attribute(strings[2983], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuildingSystem_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBuildingSystemTypeEnum_type), true),
            new attribute(strings[2984], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuiltElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuiltElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBuiltSystem_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBuiltSystemTypeEnum_type), true),
            new attribute(strings[2984], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBurner_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBurnerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcBurnerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcBurnerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCShapeProfileDef_type->set_attributes({
            new attribute(strings[2985], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2986], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2987], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2988], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2989], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCableCarrierFitting_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCableCarrierFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCableCarrierFittingType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCableCarrierFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCableCarrierSegment_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCableCarrierSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCableCarrierSegmentType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCableCarrierSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCableFitting_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCableFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCableFittingType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCableFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCableSegment_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCableSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCableSegmentType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCableSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCaissonFoundation_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCaissonFoundationTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCaissonFoundationType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCaissonFoundationTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCartesianPoint_type->set_attributes({
            new attribute(strings[2990], new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC4X3_TC1_IfcLengthMeasure_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcCartesianPointList_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcCartesianPointList2D_type->set_attributes({
            new attribute(strings[2991], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_TC1_IfcLengthMeasure_type))), false),
            new attribute(strings[2992], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcCartesianPointList3D_type->set_attributes({
            new attribute(strings[2991], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_TC1_IfcLengthMeasure_type))), false),
            new attribute(strings[2992], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcCartesianTransformationOperator_type->set_attributes({
            new attribute(strings[2993], new named_type(IFC4X3_TC1_IfcDirection_type), true),
            new attribute(strings[2994], new named_type(IFC4X3_TC1_IfcDirection_type), true),
            new attribute(strings[2995], new named_type(IFC4X3_TC1_IfcCartesianPoint_type), false),
            new attribute(strings[2996], new named_type(IFC4X3_TC1_IfcReal_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcCartesianTransformationOperator2D_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcCartesianTransformationOperator2DnonUniform_type->set_attributes({
            new attribute(strings[2997], new named_type(IFC4X3_TC1_IfcReal_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcCartesianTransformationOperator3D_type->set_attributes({
            new attribute(strings[2998], new named_type(IFC4X3_TC1_IfcDirection_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcCartesianTransformationOperator3DnonUniform_type->set_attributes({
            new attribute(strings[2997], new named_type(IFC4X3_TC1_IfcReal_type), true),
            new attribute(strings[2999], new named_type(IFC4X3_TC1_IfcReal_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCenterLineProfileDef_type->set_attributes({
            new attribute(strings[3000], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcChiller_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcChillerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcChillerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcChillerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcChimney_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcChimneyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcChimneyType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcChimneyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCircle_type->set_attributes({
            new attribute(strings[3001], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcCircleHollowProfileDef_type->set_attributes({
            new attribute(strings[2987], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcCircleProfileDef_type->set_attributes({
            new attribute(strings[3001], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcCivilElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCivilElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcClassification_type->set_attributes({
            new attribute(strings[3002], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3003], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3004], new named_type(IFC4X3_TC1_IfcDate_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3005], new named_type(IFC4X3_TC1_IfcURIReference_type), true),
            new attribute(strings[3006], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcIdentifier_type)), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcClassificationReference_type->set_attributes({
            new attribute(strings[3007], new named_type(IFC4X3_TC1_IfcClassificationReferenceSelect_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3008], new named_type(IFC4X3_TC1_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcClosedShell_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcClothoid_type->set_attributes({
            new attribute(strings[3009], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcCoil_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCoilTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCoilType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCoilTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcColourRgb_type->set_attributes({
            new attribute(strings[3010], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), false),
            new attribute(strings[3011], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), false),
            new attribute(strings[3012], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcColourRgbList_type->set_attributes({
            new attribute(strings[3013], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type))), false)
    },{
            false
    });
    IFC4X3_TC1_IfcColourSpecification_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_TC1_IfcColumn_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcColumnTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcColumnType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcColumnTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCommunicationsAppliance_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCommunicationsApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCommunicationsApplianceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCommunicationsApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcComplexProperty_type->set_attributes({
            new attribute(strings[3014], new named_type(IFC4X3_TC1_IfcIdentifier_type), false),
            new attribute(strings[3015], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcProperty_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcComplexPropertyTemplate_type->set_attributes({
            new attribute(strings[3014], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3016], new named_type(IFC4X3_TC1_IfcComplexPropertyTemplateTypeEnum_type), true),
            new attribute(strings[3017], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPropertyTemplate_type)), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCompositeCurve_type->set_attributes({
            new attribute(strings[3018], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcSegment_type)), false),
            new attribute(strings[2938], new named_type(IFC4X3_TC1_IfcLogical_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcCompositeCurveOnSurface_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_TC1_IfcCompositeCurveSegment_type->set_attributes({
            new attribute(strings[3019], new named_type(IFC4X3_TC1_IfcBoolean_type), false),
            new attribute(strings[3020], new named_type(IFC4X3_TC1_IfcCurve_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcCompositeProfileDef_type->set_attributes({
            new attribute(strings[3021], new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC4X3_TC1_IfcProfileDef_type)), false),
            new attribute(strings[3022], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcCompressor_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCompressorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCompressorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCompressorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCondenser_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCondenserTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCondenserType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCondenserTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConic_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcConnectedFaceSet_type->set_attributes({
            new attribute(strings[3024], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcFace_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcConnectionCurveGeometry_type->set_attributes({
            new attribute(strings[3025], new named_type(IFC4X3_TC1_IfcCurveOrEdgeCurve_type), false),
            new attribute(strings[3026], new named_type(IFC4X3_TC1_IfcCurveOrEdgeCurve_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcConnectionGeometry_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcConnectionPointEccentricity_type->set_attributes({
            new attribute(strings[3027], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3028], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3029], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcConnectionPointGeometry_type->set_attributes({
            new attribute(strings[3030], new named_type(IFC4X3_TC1_IfcPointOrVertexPoint_type), false),
            new attribute(strings[3031], new named_type(IFC4X3_TC1_IfcPointOrVertexPoint_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcConnectionSurfaceGeometry_type->set_attributes({
            new attribute(strings[3032], new named_type(IFC4X3_TC1_IfcSurfaceOrFaceSurface_type), false),
            new attribute(strings[3033], new named_type(IFC4X3_TC1_IfcSurfaceOrFaceSurface_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcConnectionVolumeGeometry_type->set_attributes({
            new attribute(strings[3034], new named_type(IFC4X3_TC1_IfcSolidOrShell_type), false),
            new attribute(strings[3035], new named_type(IFC4X3_TC1_IfcSolidOrShell_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcConstraint_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3036], new named_type(IFC4X3_TC1_IfcConstraintEnum_type), false),
            new attribute(strings[3037], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3038], new named_type(IFC4X3_TC1_IfcActorSelect_type), true),
            new attribute(strings[3039], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3040], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConstructionEquipmentResource_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcConstructionEquipmentResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConstructionEquipmentResourceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcConstructionEquipmentResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConstructionMaterialResource_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcConstructionMaterialResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConstructionMaterialResourceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcConstructionMaterialResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConstructionProductResource_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcConstructionProductResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConstructionProductResourceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcConstructionProductResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConstructionResource_type->set_attributes({
            new attribute(strings[3041], new named_type(IFC4X3_TC1_IfcResourceTime_type), true),
            new attribute(strings[3042], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcAppliedValue_type)), true),
            new attribute(strings[3043], new named_type(IFC4X3_TC1_IfcPhysicalQuantity_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConstructionResourceType_type->set_attributes({
            new attribute(strings[3042], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcAppliedValue_type)), true),
            new attribute(strings[3043], new named_type(IFC4X3_TC1_IfcPhysicalQuantity_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcContext_type->set_attributes({
            new attribute(strings[3044], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2984], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3045], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3046], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcRepresentationContext_type)), true),
            new attribute(strings[3047], new named_type(IFC4X3_TC1_IfcUnitAssignment_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcContextDependentUnit_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcControl_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcController_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcControllerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcControllerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcControllerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConversionBasedUnit_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[3048], new named_type(IFC4X3_TC1_IfcMeasureWithUnit_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcConversionBasedUnitWithOffset_type->set_attributes({
            new attribute(strings[3049], new named_type(IFC4X3_TC1_IfcReal_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcConveyorSegment_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcConveyorSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcConveyorSegmentType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcConveyorSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCooledBeam_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCooledBeamTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCooledBeamType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCooledBeamTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCoolingTower_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCoolingTowerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCoolingTowerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCoolingTowerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCoordinateOperation_type->set_attributes({
            new attribute(strings[3050], new named_type(IFC4X3_TC1_IfcCoordinateReferenceSystemSelect_type), false),
            new attribute(strings[3051], new named_type(IFC4X3_TC1_IfcCoordinateReferenceSystem_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcCoordinateReferenceSystem_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3052], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3053], new named_type(IFC4X3_TC1_IfcIdentifier_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcCosineSpiral_type->set_attributes({
            new attribute(strings[3054], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3055], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcCostItem_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCostItemTypeEnum_type), true),
            new attribute(strings[3056], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcCostValue_type)), true),
            new attribute(strings[3057], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcPhysicalQuantity_type)), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCostSchedule_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCostScheduleTypeEnum_type), true),
            new attribute(strings[2856], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3058], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3059], new named_type(IFC4X3_TC1_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCostValue_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCourse_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCourseTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCourseType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCourseTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCovering_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCoveringTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCoveringType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCoveringTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCrewResource_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCrewResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCrewResourceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCrewResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCsgPrimitive3D_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcCsgSolid_type->set_attributes({
            new attribute(strings[3060], new named_type(IFC4X3_TC1_IfcCsgSelect_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcCurrencyRelationship_type->set_attributes({
            new attribute(strings[3061], new named_type(IFC4X3_TC1_IfcMonetaryUnit_type), false),
            new attribute(strings[3062], new named_type(IFC4X3_TC1_IfcMonetaryUnit_type), false),
            new attribute(strings[3063], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), false),
            new attribute(strings[3064], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3065], new named_type(IFC4X3_TC1_IfcLibraryInformation_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCurtainWall_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCurtainWallTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCurtainWallType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcCurtainWallTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcCurve_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcCurveBoundedPlane_type->set_attributes({
            new attribute(strings[3066], new named_type(IFC4X3_TC1_IfcPlane_type), false),
            new attribute(strings[2885], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[2886], new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X3_TC1_IfcCurve_type)), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcCurveBoundedSurface_type->set_attributes({
            new attribute(strings[3066], new named_type(IFC4X3_TC1_IfcSurface_type), false),
            new attribute(strings[3067], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcBoundaryCurve_type)), false),
            new attribute(strings[3068], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcCurveSegment_type->set_attributes({
            new attribute(strings[3069], new named_type(IFC4X3_TC1_IfcPlacement_type), false),
            new attribute(strings[3070], new named_type(IFC4X3_TC1_IfcCurveMeasureSelect_type), false),
            new attribute(strings[2876], new named_type(IFC4X3_TC1_IfcCurveMeasureSelect_type), false),
            new attribute(strings[3020], new named_type(IFC4X3_TC1_IfcCurve_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcCurveStyle_type->set_attributes({
            new attribute(strings[3071], new named_type(IFC4X3_TC1_IfcCurveFontOrScaledCurveFontSelect_type), true),
            new attribute(strings[3072], new named_type(IFC4X3_TC1_IfcSizeSelect_type), true),
            new attribute(strings[3073], new named_type(IFC4X3_TC1_IfcColour_type), true),
            new attribute(strings[3074], new named_type(IFC4X3_TC1_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcCurveStyleFont_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3075], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcCurveStyleFontPattern_type)), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcCurveStyleFontAndScaling_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3076], new named_type(IFC4X3_TC1_IfcCurveStyleFontSelect_type), false),
            new attribute(strings[3077], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcCurveStyleFontPattern_type->set_attributes({
            new attribute(strings[3078], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3079], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcCylindricalSurface_type->set_attributes({
            new attribute(strings[3001], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcDamper_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDamperTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDamperType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDamperTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDeepFoundation_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDeepFoundationType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDerivedProfileDef_type->set_attributes({
            new attribute(strings[3080], new named_type(IFC4X3_TC1_IfcProfileDef_type), false),
            new attribute(strings[2956], new named_type(IFC4X3_TC1_IfcCartesianTransformationOperator2D_type), false),
            new attribute(strings[3022], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcDerivedUnit_type->set_attributes({
            new attribute(strings[3081], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcDerivedUnitElement_type)), false),
            new attribute(strings[3082], new named_type(IFC4X3_TC1_IfcDerivedUnitEnum_type), false),
            new attribute(strings[3083], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcDerivedUnitElement_type->set_attributes({
            new attribute(strings[3084], new named_type(IFC4X3_TC1_IfcNamedUnit_type), false),
            new attribute(strings[3085], new simple_type(simple_type::integer_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcDimensionalExponents_type->set_attributes({
            new attribute(strings[3086], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3087], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3088], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3089], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3090], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3091], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3092], new simple_type(simple_type::integer_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDirection_type->set_attributes({
            new attribute(strings[3093], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X3_TC1_IfcReal_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcDirectrixCurveSweptAreaSolid_type->set_attributes({
            new attribute(strings[3094], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3095], new named_type(IFC4X3_TC1_IfcCurveMeasureSelect_type), true),
            new attribute(strings[3096], new named_type(IFC4X3_TC1_IfcCurveMeasureSelect_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcDirectrixDerivedReferenceSweptAreaSolid_type->set_attributes({
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDiscreteAccessory_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDiscreteAccessoryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDiscreteAccessoryType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDiscreteAccessoryTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionBoard_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDistributionBoardTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionBoardType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDistributionBoardTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionChamberElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDistributionChamberElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionChamberElementType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDistributionChamberElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionCircuit_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionControlElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionControlElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionFlowElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionFlowElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionPort_type->set_attributes({
            new attribute(strings[3097], new named_type(IFC4X3_TC1_IfcFlowDirectionEnum_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDistributionPortTypeEnum_type), true),
            new attribute(strings[3098], new named_type(IFC4X3_TC1_IfcDistributionSystemEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDistributionSystem_type->set_attributes({
            new attribute(strings[2984], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDistributionSystemEnum_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDocumentInformation_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), false),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3099], new named_type(IFC4X3_TC1_IfcURIReference_type), true),
            new attribute(strings[2862], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3100], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3101], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3102], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3103], new named_type(IFC4X3_TC1_IfcActorSelect_type), true),
            new attribute(strings[3104], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcActorSelect_type)), true),
            new attribute(strings[3039], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3105], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3106], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3107], new named_type(IFC4X3_TC1_IfcDate_type), true),
            new attribute(strings[3108], new named_type(IFC4X3_TC1_IfcDate_type), true),
            new attribute(strings[3109], new named_type(IFC4X3_TC1_IfcDocumentConfidentialityEnum_type), true),
            new attribute(strings[2856], new named_type(IFC4X3_TC1_IfcDocumentStatusEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDocumentInformationRelationship_type->set_attributes({
            new attribute(strings[3110], new named_type(IFC4X3_TC1_IfcDocumentInformation_type), false),
            new attribute(strings[3111], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcDocumentInformation_type)), false),
            new attribute(strings[3112], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcDocumentReference_type->set_attributes({
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3113], new named_type(IFC4X3_TC1_IfcDocumentInformation_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcDoor_type->set_attributes({
            new attribute(strings[3114], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3115], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDoorTypeEnum_type), true),
            new attribute(strings[3116], new named_type(IFC4X3_TC1_IfcDoorTypeOperationEnum_type), true),
            new attribute(strings[3117], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDoorLiningProperties_type->set_attributes({
            new attribute(strings[3118], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3119], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3120], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3121], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3122], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3123], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3124], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3125], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3126], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3127], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3128], new named_type(IFC4X3_TC1_IfcShapeAspect_type), true),
            new attribute(strings[3129], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3130], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDoorPanelProperties_type->set_attributes({
            new attribute(strings[3131], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3132], new named_type(IFC4X3_TC1_IfcDoorPanelOperationEnum_type), false),
            new attribute(strings[3133], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3134], new named_type(IFC4X3_TC1_IfcDoorPanelPositionEnum_type), false),
            new attribute(strings[3128], new named_type(IFC4X3_TC1_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDoorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDoorTypeEnum_type), false),
            new attribute(strings[3116], new named_type(IFC4X3_TC1_IfcDoorTypeOperationEnum_type), false),
            new attribute(strings[3135], new named_type(IFC4X3_TC1_IfcBoolean_type), true),
            new attribute(strings[3117], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDraughtingPreDefinedColour_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcDraughtingPreDefinedCurveFont_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcDuctFitting_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDuctFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDuctFittingType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDuctFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDuctSegment_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDuctSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDuctSegmentType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDuctSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDuctSilencer_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDuctSilencerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcDuctSilencerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcDuctSilencerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEarthworksCut_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEarthworksCutTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEarthworksElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEarthworksFill_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEarthworksFillTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEdge_type->set_attributes({
            new attribute(strings[3136], new named_type(IFC4X3_TC1_IfcVertex_type), false),
            new attribute(strings[3137], new named_type(IFC4X3_TC1_IfcVertex_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcEdgeCurve_type->set_attributes({
            new attribute(strings[3138], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3019], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcEdgeLoop_type->set_attributes({
            new attribute(strings[3139], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcOrientedEdge_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcElectricAppliance_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricApplianceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricDistributionBoard_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricDistributionBoardTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricDistributionBoardType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricDistributionBoardTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricFlowStorageDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricFlowStorageDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricFlowStorageDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricFlowStorageDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricFlowTreatmentDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricFlowTreatmentDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricFlowTreatmentDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricFlowTreatmentDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricGenerator_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricGeneratorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricGeneratorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricGeneratorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricMotor_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricMotorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricMotorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricMotorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricTimeControl_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricTimeControlTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElectricTimeControlType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElectricTimeControlTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElement_type->set_attributes({
            new attribute(strings[3140], new named_type(IFC4X3_TC1_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElementAssembly_type->set_attributes({
            new attribute(strings[3141], new named_type(IFC4X3_TC1_IfcAssemblyPlaceEnum_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElementAssemblyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElementAssemblyType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcElementAssemblyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElementComponent_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElementComponentType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElementQuantity_type->set_attributes({
            new attribute(strings[3142], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3143], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPhysicalQuantity_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElementType_type->set_attributes({
            new attribute(strings[3144], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcElementarySurface_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcEllipse_type->set_attributes({
            new attribute(strings[3145], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3146], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcEllipseProfileDef_type->set_attributes({
            new attribute(strings[3145], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3146], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcEnergyConversionDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEnergyConversionDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEngine_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEngineTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEngineType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEngineTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEvaporativeCooler_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEvaporativeCoolerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEvaporativeCoolerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEvaporativeCoolerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEvaporator_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEvaporatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEvaporatorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEvaporatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEvent_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEventTypeEnum_type), true),
            new attribute(strings[3147], new named_type(IFC4X3_TC1_IfcEventTriggerTypeEnum_type), true),
            new attribute(strings[3148], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3149], new named_type(IFC4X3_TC1_IfcEventTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEventTime_type->set_attributes({
            new attribute(strings[3150], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3151], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3152], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3153], new named_type(IFC4X3_TC1_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcEventType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcEventTypeEnum_type), false),
            new attribute(strings[3147], new named_type(IFC4X3_TC1_IfcEventTriggerTypeEnum_type), false),
            new attribute(strings[3148], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcExtendedProperties_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3154], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcProperty_type)), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcExternalInformation_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcExternalReference_type->set_attributes({
            new attribute(strings[3099], new named_type(IFC4X3_TC1_IfcURIReference_type), true),
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcExternalReferenceRelationship_type->set_attributes({
            new attribute(strings[3155], new named_type(IFC4X3_TC1_IfcExternalReference_type), false),
            new attribute(strings[3156], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcResourceObjectSelect_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcExternalSpatialElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcExternalSpatialElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcExternalSpatialStructureElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcExternallyDefinedHatchStyle_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcExternallyDefinedSurfaceStyle_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcExternallyDefinedTextFont_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcExtrudedAreaSolid_type->set_attributes({
            new attribute(strings[3157], new named_type(IFC4X3_TC1_IfcDirection_type), false),
            new attribute(strings[2985], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcExtrudedAreaSolidTapered_type->set_attributes({
            new attribute(strings[3158], new named_type(IFC4X3_TC1_IfcProfileDef_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcFace_type->set_attributes({
            new attribute(strings[3159], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcFaceBound_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcFaceBasedSurfaceModel_type->set_attributes({
            new attribute(strings[3160], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcConnectedFaceSet_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcFaceBound_type->set_attributes({
            new attribute(strings[3161], new named_type(IFC4X3_TC1_IfcLoop_type), false),
            new attribute(strings[3162], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcFaceOuterBound_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_TC1_IfcFaceSurface_type->set_attributes({
            new attribute(strings[3163], new named_type(IFC4X3_TC1_IfcSurface_type), false),
            new attribute(strings[3019], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcFacetedBrep_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcFacetedBrepWithVoids_type->set_attributes({
            new attribute(strings[2864], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcClosedShell_type)), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcFacility_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFacilityPart_type->set_attributes({
            new attribute(strings[3164], new named_type(IFC4X3_TC1_IfcFacilityUsageEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFacilityPartCommon_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFacilityPartCommonTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFailureConnectionCondition_type->set_attributes({
            new attribute(strings[3165], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3166], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3167], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3168], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3169], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3170], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFan_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFanTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFanType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFanTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFastener_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFastenerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFastenerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFastenerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFeatureElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFeatureElementAddition_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFeatureElementSubtraction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFillAreaStyle_type->set_attributes({
            new attribute(strings[3171], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcFillStyleSelect_type)), false),
            new attribute(strings[3074], new named_type(IFC4X3_TC1_IfcBoolean_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcFillAreaStyleHatching_type->set_attributes({
            new attribute(strings[3172], new named_type(IFC4X3_TC1_IfcCurveStyle_type), false),
            new attribute(strings[3173], new named_type(IFC4X3_TC1_IfcHatchLineDistanceSelect_type), false),
            new attribute(strings[3174], new named_type(IFC4X3_TC1_IfcCartesianPoint_type), true),
            new attribute(strings[3175], new named_type(IFC4X3_TC1_IfcCartesianPoint_type), true),
            new attribute(strings[3176], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcFillAreaStyleTiles_type->set_attributes({
            new attribute(strings[3177], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_TC1_IfcVector_type)), false),
            new attribute(strings[3178], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcStyledItem_type)), false),
            new attribute(strings[3179], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcFilter_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFilterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFilterType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFilterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFireSuppressionTerminal_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFireSuppressionTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFireSuppressionTerminalType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFireSuppressionTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFixedReferenceSweptAreaSolid_type->set_attributes({
            new attribute(strings[3180], new named_type(IFC4X3_TC1_IfcDirection_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowController_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowControllerType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowFitting_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowFittingType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowInstrument_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFlowInstrumentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowInstrumentType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFlowInstrumentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowMeter_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFlowMeterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowMeterType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFlowMeterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowMovingDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowMovingDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowSegment_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowSegmentType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowStorageDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowStorageDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowTerminal_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowTerminalType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowTreatmentDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFlowTreatmentDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFooting_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFootingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFootingType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFootingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFurnishingElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFurnishingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFurniture_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFurnitureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcFurnitureType_type->set_attributes({
            new attribute(strings[3141], new named_type(IFC4X3_TC1_IfcAssemblyPlaceEnum_type), false),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcFurnitureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGeographicElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcGeographicElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGeographicElementType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcGeographicElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGeometricCurveSet_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcGeometricRepresentationContext_type->set_attributes({
            new attribute(strings[3181], new named_type(IFC4X3_TC1_IfcDimensionCount_type), false),
            new attribute(strings[3182], new named_type(IFC4X3_TC1_IfcReal_type), true),
            new attribute(strings[3183], new named_type(IFC4X3_TC1_IfcAxis2Placement_type), false),
            new attribute(strings[3184], new named_type(IFC4X3_TC1_IfcDirection_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGeometricRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcGeometricRepresentationSubContext_type->set_attributes({
            new attribute(strings[3185], new named_type(IFC4X3_TC1_IfcGeometricRepresentationContext_type), false),
            new attribute(strings[3186], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3187], new named_type(IFC4X3_TC1_IfcGeometricProjectionEnum_type), false),
            new attribute(strings[3188], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, true, true, true, true, false, false, false, false
    });
    IFC4X3_TC1_IfcGeometricSet_type->set_attributes({
            new attribute(strings[3081], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcGeometricSetSelect_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcGeomodel_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGeoslice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGeotechnicalAssembly_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGeotechnicalElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGeotechnicalStratum_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcGeotechnicalStratumTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGradientCurve_type->set_attributes({
            new attribute(strings[3189], new named_type(IFC4X3_TC1_IfcBoundedCurve_type), false),
            new attribute(strings[3190], new named_type(IFC4X3_TC1_IfcPlacement_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcGrid_type->set_attributes({
            new attribute(strings[3191], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcGridAxis_type)), false),
            new attribute(strings[3192], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcGridAxis_type)), false),
            new attribute(strings[3193], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcGridAxis_type)), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcGridTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcGridAxis_type->set_attributes({
            new attribute(strings[3194], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3195], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3019], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcGridPlacement_type->set_attributes({
            new attribute(strings[3196], new named_type(IFC4X3_TC1_IfcVirtualGridIntersection_type), false),
            new attribute(strings[3197], new named_type(IFC4X3_TC1_IfcGridPlacementDirectionSelect_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcGroup_type->set_attributes({
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcHalfSpaceSolid_type->set_attributes({
            new attribute(strings[3198], new named_type(IFC4X3_TC1_IfcSurface_type), false),
            new attribute(strings[3199], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcHeatExchanger_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcHeatExchangerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcHeatExchangerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcHeatExchangerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcHumidifier_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcHumidifierTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcHumidifierType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcHumidifierTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcIShapeProfileDef_type->set_attributes({
            new attribute(strings[3115], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2921], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2922], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3200], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3201], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3202], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3203], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcImageTexture_type->set_attributes({
            new attribute(strings[3204], new named_type(IFC4X3_TC1_IfcURIReference_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcImpactProtectionDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcImpactProtectionDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcImpactProtectionDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcImpactProtectionDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcIndexedColourMap_type->set_attributes({
            new attribute(strings[3205], new named_type(IFC4X3_TC1_IfcTessellatedFaceSet_type), false),
            new attribute(strings[3206], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3207], new named_type(IFC4X3_TC1_IfcColourRgbList_type), false),
            new attribute(strings[3208], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcPositiveInteger_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcIndexedPolyCurve_type->set_attributes({
            new attribute(strings[3209], new named_type(IFC4X3_TC1_IfcCartesianPointList_type), false),
            new attribute(strings[3018], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcSegmentIndexSelect_type)), true),
            new attribute(strings[2938], new named_type(IFC4X3_TC1_IfcBoolean_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcIndexedPolygonalFace_type->set_attributes({
            new attribute(strings[3210], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_TC1_IfcPositiveInteger_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcIndexedPolygonalFaceWithVoids_type->set_attributes({
            new attribute(strings[3211], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_TC1_IfcPositiveInteger_type))), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcIndexedPolygonalTextureMap_type->set_attributes({
            new attribute(strings[3212], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcTextureCoordinateIndices_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcIndexedTextureMap_type->set_attributes({
            new attribute(strings[3205], new named_type(IFC4X3_TC1_IfcTessellatedFaceSet_type), false),
            new attribute(strings[3213], new named_type(IFC4X3_TC1_IfcTextureVertexList_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcIndexedTriangleTextureMap_type->set_attributes({
            new attribute(strings[3214], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_TC1_IfcPositiveInteger_type))), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcInterceptor_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcInterceptorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcInterceptorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcInterceptorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcIntersectionCurve_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcInventory_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcInventoryTypeEnum_type), true),
            new attribute(strings[3215], new named_type(IFC4X3_TC1_IfcActorSelect_type), true),
            new attribute(strings[3216], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPerson_type)), true),
            new attribute(strings[3217], new named_type(IFC4X3_TC1_IfcDate_type), true),
            new attribute(strings[2913], new named_type(IFC4X3_TC1_IfcCostValue_type), true),
            new attribute(strings[2912], new named_type(IFC4X3_TC1_IfcCostValue_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcIrregularTimeSeries_type->set_attributes({
            new attribute(strings[3218], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcIrregularTimeSeriesValue_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcIrregularTimeSeriesValue_type->set_attributes({
            new attribute(strings[3219], new named_type(IFC4X3_TC1_IfcDateTime_type), false),
            new attribute(strings[3220], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcValue_type)), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcJunctionBox_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcJunctionBoxTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcJunctionBoxType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcJunctionBoxTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcKerb_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcKerbTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcKerbType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcKerbTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLShapeProfileDef_type->set_attributes({
            new attribute(strings[2985], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2986], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3000], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3201], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3221], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3222], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLaborResource_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLaborResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLaborResourceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLaborResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLagTime_type->set_attributes({
            new attribute(strings[3223], new named_type(IFC4X3_TC1_IfcTimeOrRatioSelect_type), false),
            new attribute(strings[3224], new named_type(IFC4X3_TC1_IfcTaskDurationEnum_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcLamp_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLampTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLampType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLampTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLibraryInformation_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2888], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3225], new named_type(IFC4X3_TC1_IfcActorSelect_type), true),
            new attribute(strings[3226], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3099], new named_type(IFC4X3_TC1_IfcURIReference_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLibraryReference_type->set_attributes({
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3227], new named_type(IFC4X3_TC1_IfcLanguageId_type), true),
            new attribute(strings[3228], new named_type(IFC4X3_TC1_IfcLibraryInformation_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLightDistributionData_type->set_attributes({
            new attribute(strings[3229], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), false),
            new attribute(strings[3230], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type)), false),
            new attribute(strings[3231], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLuminousIntensityDistributionMeasure_type)), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcLightFixture_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLightFixtureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLightFixtureType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLightFixtureTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLightIntensityDistribution_type->set_attributes({
            new attribute(strings[3232], new named_type(IFC4X3_TC1_IfcLightDistributionCurveEnum_type), false),
            new attribute(strings[3233], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLightDistributionData_type)), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcLightSource_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3234], new named_type(IFC4X3_TC1_IfcColourRgb_type), false),
            new attribute(strings[3235], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3236], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcLightSourceAmbient_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcLightSourceDirectional_type->set_attributes({
            new attribute(strings[3162], new named_type(IFC4X3_TC1_IfcDirection_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcLightSourceGoniometric_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), false),
            new attribute(strings[3237], new named_type(IFC4X3_TC1_IfcColourRgb_type), true),
            new attribute(strings[3238], new named_type(IFC4X3_TC1_IfcThermodynamicTemperatureMeasure_type), false),
            new attribute(strings[3239], new named_type(IFC4X3_TC1_IfcLuminousFluxMeasure_type), false),
            new attribute(strings[3240], new named_type(IFC4X3_TC1_IfcLightEmissionSourceEnum_type), false),
            new attribute(strings[3241], new named_type(IFC4X3_TC1_IfcLightDistributionDataSourceSelect_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLightSourcePositional_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcCartesianPoint_type), false),
            new attribute(strings[3001], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3242], new named_type(IFC4X3_TC1_IfcReal_type), false),
            new attribute(strings[3243], new named_type(IFC4X3_TC1_IfcReal_type), false),
            new attribute(strings[3244], new named_type(IFC4X3_TC1_IfcReal_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLightSourceSpot_type->set_attributes({
            new attribute(strings[3162], new named_type(IFC4X3_TC1_IfcDirection_type), false),
            new attribute(strings[3245], new named_type(IFC4X3_TC1_IfcReal_type), true),
            new attribute(strings[3246], new named_type(IFC4X3_TC1_IfcPositivePlaneAngleMeasure_type), false),
            new attribute(strings[3247], new named_type(IFC4X3_TC1_IfcPositivePlaneAngleMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLine_type->set_attributes({
            new attribute(strings[3248], new named_type(IFC4X3_TC1_IfcCartesianPoint_type), false),
            new attribute(strings[3249], new named_type(IFC4X3_TC1_IfcVector_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcLinearElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLinearPlacement_type->set_attributes({
            new attribute(strings[3250], new named_type(IFC4X3_TC1_IfcAxis2PlacementLinear_type), false),
            new attribute(strings[3251], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcLinearPositioningElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLiquidTerminal_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLiquidTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLiquidTerminalType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLiquidTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcLocalPlacement_type->set_attributes({
            new attribute(strings[3250], new named_type(IFC4X3_TC1_IfcAxis2Placement_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcLoop_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcManifoldSolidBrep_type->set_attributes({
            new attribute(strings[3252], new named_type(IFC4X3_TC1_IfcClosedShell_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcMapConversion_type->set_attributes({
            new attribute(strings[3253], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3254], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3255], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3256], new named_type(IFC4X3_TC1_IfcReal_type), true),
            new attribute(strings[3257], new named_type(IFC4X3_TC1_IfcReal_type), true),
            new attribute(strings[2996], new named_type(IFC4X3_TC1_IfcReal_type), true),
            new attribute(strings[3258], new named_type(IFC4X3_TC1_IfcReal_type), true),
            new attribute(strings[3259], new named_type(IFC4X3_TC1_IfcReal_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMappedItem_type->set_attributes({
            new attribute(strings[3260], new named_type(IFC4X3_TC1_IfcRepresentationMap_type), false),
            new attribute(strings[3261], new named_type(IFC4X3_TC1_IfcCartesianTransformationOperator_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcMarineFacility_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMarineFacilityTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMarinePart_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMarinePartTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterial_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[2896], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcMaterialClassificationRelationship_type->set_attributes({
            new attribute(strings[3262], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcClassificationSelect_type)), false),
            new attribute(strings[3263], new named_type(IFC4X3_TC1_IfcMaterial_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcMaterialConstituent_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3264], new named_type(IFC4X3_TC1_IfcMaterial_type), false),
            new attribute(strings[3265], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2896], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialConstituentSet_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3266], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcMaterialConstituent_type)), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcMaterialDefinition_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcMaterialDefinitionRepresentation_type->set_attributes({
            new attribute(strings[3267], new named_type(IFC4X3_TC1_IfcMaterial_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialLayer_type->set_attributes({
            new attribute(strings[3264], new named_type(IFC4X3_TC1_IfcMaterial_type), true),
            new attribute(strings[3268], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[3269], new named_type(IFC4X3_TC1_IfcLogical_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[2896], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3270], new named_type(IFC4X3_TC1_IfcInteger_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialLayerSet_type->set_attributes({
            new attribute(strings[3271], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcMaterialLayer_type)), false),
            new attribute(strings[3272], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcMaterialLayerSetUsage_type->set_attributes({
            new attribute(strings[3273], new named_type(IFC4X3_TC1_IfcMaterialLayerSet_type), false),
            new attribute(strings[3274], new named_type(IFC4X3_TC1_IfcLayerSetDirectionEnum_type), false),
            new attribute(strings[3275], new named_type(IFC4X3_TC1_IfcDirectionSenseEnum_type), false),
            new attribute(strings[3276], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3277], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialLayerWithOffsets_type->set_attributes({
            new attribute(strings[3278], new named_type(IFC4X3_TC1_IfcLayerSetDirectionEnum_type), false),
            new attribute(strings[3279], new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X3_TC1_IfcLengthMeasure_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialList_type->set_attributes({
            new attribute(strings[3280], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcMaterial_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcMaterialProfile_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3264], new named_type(IFC4X3_TC1_IfcMaterial_type), true),
            new attribute(strings[3281], new named_type(IFC4X3_TC1_IfcProfileDef_type), false),
            new attribute(strings[3270], new named_type(IFC4X3_TC1_IfcInteger_type), true),
            new attribute(strings[2896], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialProfileSet_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3282], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcMaterialProfile_type)), false),
            new attribute(strings[3283], new named_type(IFC4X3_TC1_IfcCompositeProfileDef_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialProfileSetUsage_type->set_attributes({
            new attribute(strings[3284], new named_type(IFC4X3_TC1_IfcMaterialProfileSet_type), false),
            new attribute(strings[3285], new named_type(IFC4X3_TC1_IfcCardinalPointReference_type), true),
            new attribute(strings[3277], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcMaterialProfileSetUsageTapering_type->set_attributes({
            new attribute(strings[3286], new named_type(IFC4X3_TC1_IfcMaterialProfileSet_type), false),
            new attribute(strings[3287], new named_type(IFC4X3_TC1_IfcCardinalPointReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialProfileWithOffsets_type->set_attributes({
            new attribute(strings[3279], new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X3_TC1_IfcLengthMeasure_type)), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialProperties_type->set_attributes({
            new attribute(strings[3264], new named_type(IFC4X3_TC1_IfcMaterialDefinition_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialRelationship_type->set_attributes({
            new attribute(strings[3288], new named_type(IFC4X3_TC1_IfcMaterial_type), false),
            new attribute(strings[3289], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcMaterial_type)), false),
            new attribute(strings[3290], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcMaterialUsageDefinition_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcMeasureWithUnit_type->set_attributes({
            new attribute(strings[3291], new named_type(IFC4X3_TC1_IfcValue_type), false),
            new attribute(strings[3292], new named_type(IFC4X3_TC1_IfcUnit_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcMechanicalFastener_type->set_attributes({
            new attribute(strings[3293], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3294], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMechanicalFastenerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMechanicalFastenerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMechanicalFastenerTypeEnum_type), false),
            new attribute(strings[3293], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3294], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMedicalDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMedicalDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMedicalDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMedicalDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMember_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMemberTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMemberType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMemberTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMetric_type->set_attributes({
            new attribute(strings[3295], new named_type(IFC4X3_TC1_IfcBenchmarkEnum_type), false),
            new attribute(strings[3296], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3297], new named_type(IFC4X3_TC1_IfcMetricValueSelect_type), true),
            new attribute(strings[3298], new named_type(IFC4X3_TC1_IfcReference_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMirroredProfileDef_type->set_attributes({
    },{
            false, false, false, true, false
    });
    IFC4X3_TC1_IfcMobileTelecommunicationsAppliance_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMobileTelecommunicationsApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMobileTelecommunicationsApplianceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMobileTelecommunicationsApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMonetaryUnit_type->set_attributes({
            new attribute(strings[3299], new named_type(IFC4X3_TC1_IfcLabel_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcMooringDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMooringDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMooringDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMooringDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMotorConnection_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMotorConnectionTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcMotorConnectionType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcMotorConnectionTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcNamedUnit_type->set_attributes({
            new attribute(strings[3300], new named_type(IFC4X3_TC1_IfcDimensionalExponents_type), false),
            new attribute(strings[3082], new named_type(IFC4X3_TC1_IfcUnitEnum_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcNavigationElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcNavigationElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcNavigationElementType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcNavigationElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcObject_type->set_attributes({
            new attribute(strings[3044], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcObjectDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcObjectPlacement_type->set_attributes({
            new attribute(strings[3301], new named_type(IFC4X3_TC1_IfcObjectPlacement_type), true)
    },{
            false
    });
    IFC4X3_TC1_IfcObjective_type->set_attributes({
            new attribute(strings[3302], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcConstraint_type)), true),
            new attribute(strings[3303], new named_type(IFC4X3_TC1_IfcLogicalOperatorEnum_type), true),
            new attribute(strings[3304], new named_type(IFC4X3_TC1_IfcObjectiveEnum_type), false),
            new attribute(strings[3305], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcOccupant_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcOccupantTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcOffsetCurve_type->set_attributes({
            new attribute(strings[3306], new named_type(IFC4X3_TC1_IfcCurve_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcOffsetCurve2D_type->set_attributes({
            new attribute(strings[3307], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2938], new named_type(IFC4X3_TC1_IfcLogical_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcOffsetCurve3D_type->set_attributes({
            new attribute(strings[3307], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[2938], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[2933], new named_type(IFC4X3_TC1_IfcDirection_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcOffsetCurveByDistances_type->set_attributes({
            new attribute(strings[3279], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcPointByDistanceExpression_type)), false),
            new attribute(strings[3140], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcOpenCrossProfileDef_type->set_attributes({
            new attribute(strings[3308], new named_type(IFC4X3_TC1_IfcBoolean_type), false),
            new attribute(strings[3309], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type)), false),
            new attribute(strings[3310], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type)), false),
            new attribute(strings[3311], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true),
            new attribute(strings[3312], new named_type(IFC4X3_TC1_IfcCartesianPoint_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcOpenShell_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcOpeningElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcOpeningElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcOrganization_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3313], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcActorRole_type)), true),
            new attribute(strings[3314], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcAddress_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcOrganizationRelationship_type->set_attributes({
            new attribute(strings[3315], new named_type(IFC4X3_TC1_IfcOrganization_type), false),
            new attribute(strings[3316], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcOrganization_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcOrientedEdge_type->set_attributes({
            new attribute(strings[3317], new named_type(IFC4X3_TC1_IfcEdge_type), false),
            new attribute(strings[3162], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            true, true, false, false
    });
    IFC4X3_TC1_IfcOuterBoundaryCurve_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_TC1_IfcOutlet_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcOutletTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcOutletType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcOutletTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcOwnerHistory_type->set_attributes({
            new attribute(strings[3318], new named_type(IFC4X3_TC1_IfcPersonAndOrganization_type), false),
            new attribute(strings[3319], new named_type(IFC4X3_TC1_IfcApplication_type), false),
            new attribute(strings[3320], new named_type(IFC4X3_TC1_IfcStateEnum_type), true),
            new attribute(strings[3321], new named_type(IFC4X3_TC1_IfcChangeActionEnum_type), true),
            new attribute(strings[3322], new named_type(IFC4X3_TC1_IfcTimeStamp_type), true),
            new attribute(strings[3323], new named_type(IFC4X3_TC1_IfcPersonAndOrganization_type), true),
            new attribute(strings[3324], new named_type(IFC4X3_TC1_IfcApplication_type), true),
            new attribute(strings[3325], new named_type(IFC4X3_TC1_IfcTimeStamp_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcParameterizedProfileDef_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement2D_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcPath_type->set_attributes({
            new attribute(strings[3139], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcOrientedEdge_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcPavement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPavementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPavementType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPavementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPcurve_type->set_attributes({
            new attribute(strings[3066], new named_type(IFC4X3_TC1_IfcSurface_type), false),
            new attribute(strings[3326], new named_type(IFC4X3_TC1_IfcCurve_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcPerformanceHistory_type->set_attributes({
            new attribute(strings[3327], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPerformanceHistoryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPermeableCoveringProperties_type->set_attributes({
            new attribute(strings[3116], new named_type(IFC4X3_TC1_IfcPermeableCoveringOperationEnum_type), false),
            new attribute(strings[3134], new named_type(IFC4X3_TC1_IfcWindowPanelPositionEnum_type), false),
            new attribute(strings[3328], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3329], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3128], new named_type(IFC4X3_TC1_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPermit_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPermitTypeEnum_type), true),
            new attribute(strings[2856], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2857], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPerson_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3330], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3331], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3332], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true),
            new attribute(strings[3333], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true),
            new attribute(strings[3334], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true),
            new attribute(strings[3313], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcActorRole_type)), true),
            new attribute(strings[3314], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcAddress_type)), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPersonAndOrganization_type->set_attributes({
            new attribute(strings[3335], new named_type(IFC4X3_TC1_IfcPerson_type), false),
            new attribute(strings[3336], new named_type(IFC4X3_TC1_IfcOrganization_type), false),
            new attribute(strings[3313], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcActorRole_type)), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcPhysicalComplexQuantity_type->set_attributes({
            new attribute(strings[3337], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPhysicalQuantity_type)), false),
            new attribute(strings[3338], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[3339], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3041], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPhysicalQuantity_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcPhysicalSimpleQuantity_type->set_attributes({
            new attribute(strings[3084], new named_type(IFC4X3_TC1_IfcNamedUnit_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcPile_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPileTypeEnum_type), true),
            new attribute(strings[3340], new named_type(IFC4X3_TC1_IfcPileConstructionEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPileType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPileTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPipeFitting_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPipeFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPipeFittingType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPipeFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPipeSegment_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPipeSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPipeSegmentType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPipeSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPixelTexture_type->set_attributes({
            new attribute(strings[2986], new named_type(IFC4X3_TC1_IfcInteger_type), false),
            new attribute(strings[3341], new named_type(IFC4X3_TC1_IfcInteger_type), false),
            new attribute(strings[3342], new named_type(IFC4X3_TC1_IfcInteger_type), false),
            new attribute(strings[3343], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcBinary_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPlacement_type->set_attributes({
            new attribute(strings[3099], new named_type(IFC4X3_TC1_IfcPoint_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcPlanarBox_type->set_attributes({
            new attribute(strings[3069], new named_type(IFC4X3_TC1_IfcAxis2Placement_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcPlanarExtent_type->set_attributes({
            new attribute(strings[3344], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3345], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcPlane_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcPlate_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPlateTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPlateType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPlateTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPoint_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcPointByDistanceExpression_type->set_attributes({
            new attribute(strings[3346], new named_type(IFC4X3_TC1_IfcCurveMeasureSelect_type), false),
            new attribute(strings[3347], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3348], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3349], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3306], new named_type(IFC4X3_TC1_IfcCurve_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcPointOnCurve_type->set_attributes({
            new attribute(strings[3306], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3350], new named_type(IFC4X3_TC1_IfcParameterValue_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcPointOnSurface_type->set_attributes({
            new attribute(strings[3066], new named_type(IFC4X3_TC1_IfcSurface_type), false),
            new attribute(strings[3351], new named_type(IFC4X3_TC1_IfcParameterValue_type), false),
            new attribute(strings[3352], new named_type(IFC4X3_TC1_IfcParameterValue_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcPolyLoop_type->set_attributes({
            new attribute(strings[3353], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_TC1_IfcCartesianPoint_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcPolygonalBoundedHalfSpace_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), false),
            new attribute(strings[3354], new named_type(IFC4X3_TC1_IfcBoundedCurve_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPolygonalFaceSet_type->set_attributes({
            new attribute(strings[3355], new named_type(IFC4X3_TC1_IfcBoolean_type), true),
            new attribute(strings[3356], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcIndexedPolygonalFace_type)), false),
            new attribute(strings[3357], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcPositiveInteger_type)), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPolyline_type->set_attributes({
            new attribute(strings[3209], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcCartesianPoint_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcPolynomialCurve_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcPlacement_type), false),
            new attribute(strings[3358], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcReal_type)), true),
            new attribute(strings[3359], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcReal_type)), true),
            new attribute(strings[3360], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcReal_type)), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPort_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPositioningElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPostalAddress_type->set_attributes({
            new attribute(strings[3361], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3362], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true),
            new attribute(strings[3363], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3364], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3365], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3366], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3367], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPreDefinedColour_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcPreDefinedCurveFont_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcPreDefinedItem_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcPreDefinedProperties_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcPreDefinedPropertySet_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPreDefinedTextFont_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcPresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcPresentationLayerAssignment_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3368], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcLayeredItem_type)), false),
            new attribute(strings[2900], new named_type(IFC4X3_TC1_IfcIdentifier_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPresentationLayerWithStyle_type->set_attributes({
            new attribute(strings[3369], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[3370], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[3371], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[3372], new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X3_TC1_IfcPresentationStyle_type)), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPresentationStyle_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_TC1_IfcProcedure_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcProcedureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProcedureType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcProcedureTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProcess_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2857], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProduct_type->set_attributes({
            new attribute(strings[3373], new named_type(IFC4X3_TC1_IfcObjectPlacement_type), true),
            new attribute(strings[3374], new named_type(IFC4X3_TC1_IfcProductRepresentation_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProductDefinitionShape_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcProductRepresentation_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3375], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcRepresentation_type)), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcProfileDef_type->set_attributes({
            new attribute(strings[3376], new named_type(IFC4X3_TC1_IfcProfileTypeEnum_type), false),
            new attribute(strings[3377], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcProfileProperties_type->set_attributes({
            new attribute(strings[3378], new named_type(IFC4X3_TC1_IfcProfileDef_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcProject_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProjectLibrary_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProjectOrder_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcProjectOrderTypeEnum_type), true),
            new attribute(strings[2856], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2857], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProjectedCRS_type->set_attributes({
            new attribute(strings[3379], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3380], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3381], new named_type(IFC4X3_TC1_IfcNamedUnit_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProjectionElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcProjectionElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProperty_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcIdentifier_type), false),
            new attribute(strings[3005], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcPropertyAbstraction_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcPropertyBoundedValue_type->set_attributes({
            new attribute(strings[3382], new named_type(IFC4X3_TC1_IfcValue_type), true),
            new attribute(strings[3383], new named_type(IFC4X3_TC1_IfcValue_type), true),
            new attribute(strings[3084], new named_type(IFC4X3_TC1_IfcUnit_type), true),
            new attribute(strings[3384], new named_type(IFC4X3_TC1_IfcValue_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPropertyDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPropertyDependencyRelationship_type->set_attributes({
            new attribute(strings[3385], new named_type(IFC4X3_TC1_IfcProperty_type), false),
            new attribute(strings[3386], new named_type(IFC4X3_TC1_IfcProperty_type), false),
            new attribute(strings[3387], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcPropertyEnumeratedValue_type->set_attributes({
            new attribute(strings[3388], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcValue_type)), true),
            new attribute(strings[3389], new named_type(IFC4X3_TC1_IfcPropertyEnumeration_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPropertyEnumeration_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[3388], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcValue_type)), false),
            new attribute(strings[3084], new named_type(IFC4X3_TC1_IfcUnit_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcPropertyListValue_type->set_attributes({
            new attribute(strings[3220], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcValue_type)), true),
            new attribute(strings[3084], new named_type(IFC4X3_TC1_IfcUnit_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPropertyReferenceValue_type->set_attributes({
            new attribute(strings[3014], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3390], new named_type(IFC4X3_TC1_IfcObjectReferenceSelect_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPropertySet_type->set_attributes({
            new attribute(strings[3015], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcProperty_type)), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcPropertySetDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPropertySetTemplate_type->set_attributes({
            new attribute(strings[3016], new named_type(IFC4X3_TC1_IfcPropertySetTemplateTypeEnum_type), true),
            new attribute(strings[3391], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3017], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPropertyTemplate_type)), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPropertySingleValue_type->set_attributes({
            new attribute(strings[3392], new named_type(IFC4X3_TC1_IfcValue_type), true),
            new attribute(strings[3084], new named_type(IFC4X3_TC1_IfcUnit_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPropertyTableValue_type->set_attributes({
            new attribute(strings[3393], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcValue_type)), true),
            new attribute(strings[3394], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcValue_type)), true),
            new attribute(strings[3387], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3395], new named_type(IFC4X3_TC1_IfcUnit_type), true),
            new attribute(strings[3396], new named_type(IFC4X3_TC1_IfcUnit_type), true),
            new attribute(strings[3397], new named_type(IFC4X3_TC1_IfcCurveInterpolationEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPropertyTemplate_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcPropertyTemplateDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcProtectiveDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcProtectiveDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProtectiveDeviceTrippingUnit_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcProtectiveDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcProtectiveDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPump_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPumpTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcPumpType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcPumpTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcQuantityArea_type->set_attributes({
            new attribute(strings[3398], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), false),
            new attribute(strings[3399], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcQuantityCount_type->set_attributes({
            new attribute(strings[3400], new named_type(IFC4X3_TC1_IfcCountMeasure_type), false),
            new attribute(strings[3399], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcQuantityLength_type->set_attributes({
            new attribute(strings[3401], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3399], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcQuantityNumber_type->set_attributes({
            new attribute(strings[3402], new named_type(IFC4X3_TC1_IfcNumericMeasure_type), false),
            new attribute(strings[3399], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcQuantitySet_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcQuantityTime_type->set_attributes({
            new attribute(strings[3403], new named_type(IFC4X3_TC1_IfcTimeMeasure_type), false),
            new attribute(strings[3399], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcQuantityVolume_type->set_attributes({
            new attribute(strings[3404], new named_type(IFC4X3_TC1_IfcVolumeMeasure_type), false),
            new attribute(strings[3399], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcQuantityWeight_type->set_attributes({
            new attribute(strings[3405], new named_type(IFC4X3_TC1_IfcMassMeasure_type), false),
            new attribute(strings[3399], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcRail_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRailTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRailType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRailTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRailing_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRailingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRailingType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRailingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRailway_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRailwayTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRailwayPart_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRailwayPartTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRamp_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRampTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRampFlight_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRampFlightTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRampFlightType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRampFlightTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRampType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRampTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRationalBSplineCurveWithKnots_type->set_attributes({
            new attribute(strings[3406], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcReal_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRationalBSplineSurfaceWithKnots_type->set_attributes({
            new attribute(strings[3406], new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcReal_type))), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRectangleHollowProfileDef_type->set_attributes({
            new attribute(strings[2987], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3407], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3408], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRectangleProfileDef_type->set_attributes({
            new attribute(strings[2976], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2977], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcRectangularPyramid_type->set_attributes({
            new attribute(strings[2953], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2954], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3341], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcRectangularTrimmedSurface_type->set_attributes({
            new attribute(strings[3066], new named_type(IFC4X3_TC1_IfcSurface_type), false),
            new attribute(strings[3409], new named_type(IFC4X3_TC1_IfcParameterValue_type), false),
            new attribute(strings[3410], new named_type(IFC4X3_TC1_IfcParameterValue_type), false),
            new attribute(strings[3411], new named_type(IFC4X3_TC1_IfcParameterValue_type), false),
            new attribute(strings[3412], new named_type(IFC4X3_TC1_IfcParameterValue_type), false),
            new attribute(strings[3413], new named_type(IFC4X3_TC1_IfcBoolean_type), false),
            new attribute(strings[3414], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRecurrencePattern_type->set_attributes({
            new attribute(strings[3415], new named_type(IFC4X3_TC1_IfcRecurrenceTypeEnum_type), false),
            new attribute(strings[3416], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcDayInMonthNumber_type)), true),
            new attribute(strings[3417], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcDayInWeekNumber_type)), true),
            new attribute(strings[3418], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcMonthInYearNumber_type)), true),
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcInteger_type), true),
            new attribute(strings[3419], new named_type(IFC4X3_TC1_IfcInteger_type), true),
            new attribute(strings[3420], new named_type(IFC4X3_TC1_IfcInteger_type), true),
            new attribute(strings[3421], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcTimePeriod_type)), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReference_type->set_attributes({
            new attribute(strings[3422], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3423], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3424], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3425], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcInteger_type)), true),
            new attribute(strings[3426], new named_type(IFC4X3_TC1_IfcReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcReferent_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcReferentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRegularTimeSeries_type->set_attributes({
            new attribute(strings[3427], new named_type(IFC4X3_TC1_IfcTimeMeasure_type), false),
            new attribute(strings[3218], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcTimeSeriesValue_type)), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcedSoil_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcReinforcedSoilTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcementBarProperties_type->set_attributes({
            new attribute(strings[3428], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), false),
            new attribute(strings[3429], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[3430], new named_type(IFC4X3_TC1_IfcReinforcingBarSurfaceEnum_type), true),
            new attribute(strings[3431], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3432], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3433], new named_type(IFC4X3_TC1_IfcCountMeasure_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcementDefinitionProperties_type->set_attributes({
            new attribute(strings[3434], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3435], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcSectionReinforcementProperties_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcingBar_type->set_attributes({
            new attribute(strings[3293], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3436], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), true),
            new attribute(strings[3437], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcReinforcingBarTypeEnum_type), true),
            new attribute(strings[3430], new named_type(IFC4X3_TC1_IfcReinforcingBarSurfaceEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcingBarType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcReinforcingBarTypeEnum_type), false),
            new attribute(strings[3293], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3436], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), true),
            new attribute(strings[3437], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3430], new named_type(IFC4X3_TC1_IfcReinforcingBarSurfaceEnum_type), true),
            new attribute(strings[3438], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3439], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcBendingParameterSelect_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcingElement_type->set_attributes({
            new attribute(strings[3429], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcingMesh_type->set_attributes({
            new attribute(strings[3440], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3441], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3442], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3443], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3444], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), true),
            new attribute(strings[3445], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), true),
            new attribute(strings[3446], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3447], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcReinforcingMeshTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcReinforcingMeshType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcReinforcingMeshTypeEnum_type), false),
            new attribute(strings[3440], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3441], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3442], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3443], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3444], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), true),
            new attribute(strings[3445], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), true),
            new attribute(strings[3446], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3447], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3438], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3439], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcBendingParameterSelect_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAdheresToElement_type->set_attributes({
            new attribute(strings[3448], new named_type(IFC4X3_TC1_IfcElement_type), false),
            new attribute(strings[3449], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcSurfaceFeature_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAggregates_type->set_attributes({
            new attribute(strings[3450], new named_type(IFC4X3_TC1_IfcObjectDefinition_type), false),
            new attribute(strings[3451], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcObjectDefinition_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssigns_type->set_attributes({
            new attribute(strings[3451], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcObjectDefinition_type)), false),
            new attribute(strings[3452], new named_type(IFC4X3_TC1_IfcStrippedOptional_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssignsToActor_type->set_attributes({
            new attribute(strings[3453], new named_type(IFC4X3_TC1_IfcActor_type), false),
            new attribute(strings[3454], new named_type(IFC4X3_TC1_IfcActorRole_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssignsToControl_type->set_attributes({
            new attribute(strings[3455], new named_type(IFC4X3_TC1_IfcControl_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssignsToGroup_type->set_attributes({
            new attribute(strings[3456], new named_type(IFC4X3_TC1_IfcGroup_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssignsToGroupByFactor_type->set_attributes({
            new attribute(strings[3457], new named_type(IFC4X3_TC1_IfcRatioMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssignsToProcess_type->set_attributes({
            new attribute(strings[3458], new named_type(IFC4X3_TC1_IfcProcessSelect_type), false),
            new attribute(strings[3459], new named_type(IFC4X3_TC1_IfcMeasureWithUnit_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssignsToProduct_type->set_attributes({
            new attribute(strings[3460], new named_type(IFC4X3_TC1_IfcProductSelect_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssignsToResource_type->set_attributes({
            new attribute(strings[3461], new named_type(IFC4X3_TC1_IfcResourceSelect_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssociates_type->set_attributes({
            new attribute(strings[3451], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcDefinitionSelect_type)), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssociatesApproval_type->set_attributes({
            new attribute(strings[2906], new named_type(IFC4X3_TC1_IfcApproval_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssociatesClassification_type->set_attributes({
            new attribute(strings[3462], new named_type(IFC4X3_TC1_IfcClassificationSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssociatesConstraint_type->set_attributes({
            new attribute(strings[3463], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3464], new named_type(IFC4X3_TC1_IfcConstraint_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssociatesDocument_type->set_attributes({
            new attribute(strings[3110], new named_type(IFC4X3_TC1_IfcDocumentSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssociatesLibrary_type->set_attributes({
            new attribute(strings[3465], new named_type(IFC4X3_TC1_IfcLibrarySelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssociatesMaterial_type->set_attributes({
            new attribute(strings[3288], new named_type(IFC4X3_TC1_IfcMaterialSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelAssociatesProfileDef_type->set_attributes({
            new attribute(strings[3466], new named_type(IFC4X3_TC1_IfcProfileDef_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnects_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnectsElements_type->set_attributes({
            new attribute(strings[3467], new named_type(IFC4X3_TC1_IfcConnectionGeometry_type), true),
            new attribute(strings[3448], new named_type(IFC4X3_TC1_IfcElement_type), false),
            new attribute(strings[3468], new named_type(IFC4X3_TC1_IfcElement_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnectsPathElements_type->set_attributes({
            new attribute(strings[3469], new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X3_TC1_IfcInteger_type)), false),
            new attribute(strings[3470], new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X3_TC1_IfcInteger_type)), false),
            new attribute(strings[3471], new named_type(IFC4X3_TC1_IfcConnectionTypeEnum_type), false),
            new attribute(strings[3472], new named_type(IFC4X3_TC1_IfcConnectionTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnectsPortToElement_type->set_attributes({
            new attribute(strings[3473], new named_type(IFC4X3_TC1_IfcPort_type), false),
            new attribute(strings[3468], new named_type(IFC4X3_TC1_IfcDistributionElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnectsPorts_type->set_attributes({
            new attribute(strings[3473], new named_type(IFC4X3_TC1_IfcPort_type), false),
            new attribute(strings[3474], new named_type(IFC4X3_TC1_IfcPort_type), false),
            new attribute(strings[3475], new named_type(IFC4X3_TC1_IfcElement_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnectsStructuralActivity_type->set_attributes({
            new attribute(strings[3448], new named_type(IFC4X3_TC1_IfcStructuralActivityAssignmentSelect_type), false),
            new attribute(strings[3476], new named_type(IFC4X3_TC1_IfcStructuralActivity_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnectsStructuralMember_type->set_attributes({
            new attribute(strings[3477], new named_type(IFC4X3_TC1_IfcStructuralMember_type), false),
            new attribute(strings[3478], new named_type(IFC4X3_TC1_IfcStructuralConnection_type), false),
            new attribute(strings[3479], new named_type(IFC4X3_TC1_IfcBoundaryCondition_type), true),
            new attribute(strings[3480], new named_type(IFC4X3_TC1_IfcStructuralConnectionCondition_type), true),
            new attribute(strings[3481], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3482], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnectsWithEccentricity_type->set_attributes({
            new attribute(strings[3483], new named_type(IFC4X3_TC1_IfcConnectionGeometry_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelConnectsWithRealizingElements_type->set_attributes({
            new attribute(strings[3484], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcElement_type)), false),
            new attribute(strings[3485], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelContainedInSpatialStructure_type->set_attributes({
            new attribute(strings[3486], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcProduct_type)), false),
            new attribute(strings[3487], new named_type(IFC4X3_TC1_IfcSpatialElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelCoversBldgElements_type->set_attributes({
            new attribute(strings[3488], new named_type(IFC4X3_TC1_IfcElement_type), false),
            new attribute(strings[3489], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcCovering_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelCoversSpaces_type->set_attributes({
            new attribute(strings[3490], new named_type(IFC4X3_TC1_IfcSpace_type), false),
            new attribute(strings[3489], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcCovering_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelDeclares_type->set_attributes({
            new attribute(strings[3491], new named_type(IFC4X3_TC1_IfcContext_type), false),
            new attribute(strings[3492], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcDefinitionSelect_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelDecomposes_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcRelDefines_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcRelDefinesByObject_type->set_attributes({
            new attribute(strings[3451], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcObject_type)), false),
            new attribute(strings[3450], new named_type(IFC4X3_TC1_IfcObject_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelDefinesByProperties_type->set_attributes({
            new attribute(strings[3451], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcObjectDefinition_type)), false),
            new attribute(strings[3493], new named_type(IFC4X3_TC1_IfcPropertySetDefinitionSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelDefinesByTemplate_type->set_attributes({
            new attribute(strings[3494], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPropertySetDefinition_type)), false),
            new attribute(strings[3495], new named_type(IFC4X3_TC1_IfcPropertySetTemplate_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelDefinesByType_type->set_attributes({
            new attribute(strings[3451], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcObject_type)), false),
            new attribute(strings[3496], new named_type(IFC4X3_TC1_IfcTypeObject_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelFillsElement_type->set_attributes({
            new attribute(strings[3497], new named_type(IFC4X3_TC1_IfcOpeningElement_type), false),
            new attribute(strings[3498], new named_type(IFC4X3_TC1_IfcElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelFlowControlElements_type->set_attributes({
            new attribute(strings[3499], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcDistributionControlElement_type)), false),
            new attribute(strings[3500], new named_type(IFC4X3_TC1_IfcDistributionFlowElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelInterferesElements_type->set_attributes({
            new attribute(strings[3448], new named_type(IFC4X3_TC1_IfcInterferenceSelect_type), false),
            new attribute(strings[3468], new named_type(IFC4X3_TC1_IfcInterferenceSelect_type), false),
            new attribute(strings[3501], new named_type(IFC4X3_TC1_IfcConnectionGeometry_type), true),
            new attribute(strings[3502], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3503], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[3504], new named_type(IFC4X3_TC1_IfcSpatialZone_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelNests_type->set_attributes({
            new attribute(strings[3450], new named_type(IFC4X3_TC1_IfcObjectDefinition_type), false),
            new attribute(strings[3451], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcObjectDefinition_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelPositions_type->set_attributes({
            new attribute(strings[3505], new named_type(IFC4X3_TC1_IfcPositioningElement_type), false),
            new attribute(strings[3506], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcProduct_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelProjectsElement_type->set_attributes({
            new attribute(strings[3448], new named_type(IFC4X3_TC1_IfcElement_type), false),
            new attribute(strings[3507], new named_type(IFC4X3_TC1_IfcFeatureElementAddition_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type->set_attributes({
            new attribute(strings[3486], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcSpatialReferenceSelect_type)), false),
            new attribute(strings[3487], new named_type(IFC4X3_TC1_IfcSpatialElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelSequence_type->set_attributes({
            new attribute(strings[3458], new named_type(IFC4X3_TC1_IfcProcess_type), false),
            new attribute(strings[3508], new named_type(IFC4X3_TC1_IfcProcess_type), false),
            new attribute(strings[3509], new named_type(IFC4X3_TC1_IfcLagTime_type), true),
            new attribute(strings[3510], new named_type(IFC4X3_TC1_IfcSequenceEnum_type), true),
            new attribute(strings[3511], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelServicesBuildings_type->set_attributes({
            new attribute(strings[3512], new named_type(IFC4X3_TC1_IfcSystem_type), false),
            new attribute(strings[3513], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcSpatialElement_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelSpaceBoundary_type->set_attributes({
            new attribute(strings[3490], new named_type(IFC4X3_TC1_IfcSpaceBoundarySelect_type), false),
            new attribute(strings[3498], new named_type(IFC4X3_TC1_IfcElement_type), false),
            new attribute(strings[3467], new named_type(IFC4X3_TC1_IfcConnectionGeometry_type), true),
            new attribute(strings[3514], new named_type(IFC4X3_TC1_IfcPhysicalOrVirtualEnum_type), false),
            new attribute(strings[3515], new named_type(IFC4X3_TC1_IfcInternalOrExternalEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type->set_attributes({
            new attribute(strings[3516], new named_type(IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type->set_attributes({
            new attribute(strings[3517], new named_type(IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelVoidsElement_type->set_attributes({
            new attribute(strings[3488], new named_type(IFC4X3_TC1_IfcElement_type), false),
            new attribute(strings[3518], new named_type(IFC4X3_TC1_IfcFeatureElementSubtraction_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRelationship_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcReparametrisedCompositeCurveSegment_type->set_attributes({
            new attribute(strings[3519], new named_type(IFC4X3_TC1_IfcParameterValue_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcRepresentation_type->set_attributes({
            new attribute(strings[3520], new named_type(IFC4X3_TC1_IfcRepresentationContext_type), false),
            new attribute(strings[3521], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3522], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3523], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcRepresentationItem_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcRepresentationContext_type->set_attributes({
            new attribute(strings[3524], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3525], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcRepresentationMap_type->set_attributes({
            new attribute(strings[3526], new named_type(IFC4X3_TC1_IfcAxis2Placement_type), false),
            new attribute(strings[3527], new named_type(IFC4X3_TC1_IfcRepresentation_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcResource_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2857], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcResourceApprovalRelationship_type->set_attributes({
            new attribute(strings[3156], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcResourceObjectSelect_type)), false),
            new attribute(strings[2906], new named_type(IFC4X3_TC1_IfcApproval_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcResourceConstraintRelationship_type->set_attributes({
            new attribute(strings[3464], new named_type(IFC4X3_TC1_IfcConstraint_type), false),
            new attribute(strings[3156], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcResourceObjectSelect_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcResourceLevelRelationship_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcResourceTime_type->set_attributes({
            new attribute(strings[3528], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3529], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3530], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3531], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3532], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3533], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3534], new named_type(IFC4X3_TC1_IfcBoolean_type), true),
            new attribute(strings[3535], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3536], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3537], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3538], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3539], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3540], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3541], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3542], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRevolvedAreaSolid_type->set_attributes({
            new attribute(strings[2932], new named_type(IFC4X3_TC1_IfcAxis1Placement_type), false),
            new attribute(strings[3543], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcRevolvedAreaSolidTapered_type->set_attributes({
            new attribute(strings[3158], new named_type(IFC4X3_TC1_IfcProfileDef_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcRightCircularCone_type->set_attributes({
            new attribute(strings[3341], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3544], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcRightCircularCylinder_type->set_attributes({
            new attribute(strings[3341], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3001], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcRoad_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRoadTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRoadPart_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRoadPartTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRoof_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRoofTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRoofType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcRoofTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcRoot_type->set_attributes({
            new attribute(strings[3545], new named_type(IFC4X3_TC1_IfcGloballyUniqueId_type), false),
            new attribute(strings[3546], new named_type(IFC4X3_TC1_IfcOwnerHistory_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcRoundedRectangleProfileDef_type->set_attributes({
            new attribute(strings[3547], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSIUnit_type->set_attributes({
            new attribute(strings[3548], new named_type(IFC4X3_TC1_IfcSIPrefix_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcSIUnitName_type), false)
    },{
            true, false, false, false
    });
    IFC4X3_TC1_IfcSanitaryTerminal_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSanitaryTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSanitaryTerminalType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSanitaryTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSchedulingTime_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3549], new named_type(IFC4X3_TC1_IfcDataOriginEnum_type), true),
            new attribute(strings[3550], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSeamCurve_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSecondOrderPolynomialSpiral_type->set_attributes({
            new attribute(strings[3551], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3552], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3055], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcSectionProperties_type->set_attributes({
            new attribute(strings[3553], new named_type(IFC4X3_TC1_IfcSectionTypeEnum_type), false),
            new attribute(strings[3554], new named_type(IFC4X3_TC1_IfcProfileDef_type), false),
            new attribute(strings[3555], new named_type(IFC4X3_TC1_IfcProfileDef_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSectionReinforcementProperties_type->set_attributes({
            new attribute(strings[3556], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3557], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3558], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3559], new named_type(IFC4X3_TC1_IfcReinforcingBarRoleEnum_type), false),
            new attribute(strings[3560], new named_type(IFC4X3_TC1_IfcSectionProperties_type), false),
            new attribute(strings[3561], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcReinforcementBarProperties_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSectionedSolid_type->set_attributes({
            new attribute(strings[3094], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3562], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcProfileDef_type)), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcSectionedSolidHorizontal_type->set_attributes({
            new attribute(strings[3563], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcAxis2PlacementLinear_type)), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSectionedSpine_type->set_attributes({
            new attribute(strings[3564], new named_type(IFC4X3_TC1_IfcCompositeCurve_type), false),
            new attribute(strings[3562], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcProfileDef_type)), false),
            new attribute(strings[3563], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type)), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSectionedSurface_type->set_attributes({
            new attribute(strings[3094], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3563], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcAxis2PlacementLinear_type)), false),
            new attribute(strings[3562], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_TC1_IfcProfileDef_type)), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSegment_type->set_attributes({
            new attribute(strings[3565], new named_type(IFC4X3_TC1_IfcTransitionCode_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcSegmentedReferenceCurve_type->set_attributes({
            new attribute(strings[3189], new named_type(IFC4X3_TC1_IfcBoundedCurve_type), false),
            new attribute(strings[3190], new named_type(IFC4X3_TC1_IfcPlacement_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcSensor_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSensorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSensorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSensorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSeventhOrderPolynomialSpiral_type->set_attributes({
            new attribute(strings[3566], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3567], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3568], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3569], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3570], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3551], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3552], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3055], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcShadingDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcShadingDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcShadingDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcShadingDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcShapeAspect_type->set_attributes({
            new attribute(strings[3571], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcShapeModel_type)), false),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3572], new named_type(IFC4X3_TC1_IfcLogical_type), false),
            new attribute(strings[3573], new named_type(IFC4X3_TC1_IfcProductRepresentationSelect_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcShapeModel_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcShapeRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcShellBasedSurfaceModel_type->set_attributes({
            new attribute(strings[3574], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcShell_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcSign_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSignTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSignType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSignTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSignal_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSignalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSignalType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSignalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSimpleProperty_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_TC1_IfcSimplePropertyTemplate_type->set_attributes({
            new attribute(strings[3016], new named_type(IFC4X3_TC1_IfcSimplePropertyTemplateTypeEnum_type), true),
            new attribute(strings[3575], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3576], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3577], new named_type(IFC4X3_TC1_IfcPropertyEnumeration_type), true),
            new attribute(strings[3578], new named_type(IFC4X3_TC1_IfcUnit_type), true),
            new attribute(strings[3579], new named_type(IFC4X3_TC1_IfcUnit_type), true),
            new attribute(strings[3387], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3580], new named_type(IFC4X3_TC1_IfcStateEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSineSpiral_type->set_attributes({
            new attribute(strings[3581], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3552], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3055], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcSite_type->set_attributes({
            new attribute(strings[3582], new named_type(IFC4X3_TC1_IfcCompoundPlaneAngleMeasure_type), true),
            new attribute(strings[3583], new named_type(IFC4X3_TC1_IfcCompoundPlaneAngleMeasure_type), true),
            new attribute(strings[3584], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3585], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3586], new named_type(IFC4X3_TC1_IfcPostalAddress_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSlab_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSlabTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSlabType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSlabTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSlippageConnectionCondition_type->set_attributes({
            new attribute(strings[3587], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3588], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3589], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcSolarDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSolarDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSolarDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSolarDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSolidModel_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcSpace_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSpaceTypeEnum_type), true),
            new attribute(strings[3590], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpaceHeater_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSpaceHeaterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpaceHeaterType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSpaceHeaterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpaceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSpaceTypeEnum_type), false),
            new attribute(strings[2984], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpatialElement_type->set_attributes({
            new attribute(strings[2984], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpatialElementType_type->set_attributes({
            new attribute(strings[3144], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpatialStructureElement_type->set_attributes({
            new attribute(strings[3591], new named_type(IFC4X3_TC1_IfcElementCompositionEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpatialStructureElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpatialZone_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSpatialZoneTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSpatialZoneType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSpatialZoneTypeEnum_type), false),
            new attribute(strings[2984], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSphere_type->set_attributes({
            new attribute(strings[3001], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcSphericalSurface_type->set_attributes({
            new attribute(strings[3001], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcSpiral_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement_type), true)
    },{
            false
    });
    IFC4X3_TC1_IfcStackTerminal_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStackTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStackTerminalType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStackTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStair_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStairTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStairFlight_type->set_attributes({
            new attribute(strings[3592], new named_type(IFC4X3_TC1_IfcInteger_type), true),
            new attribute(strings[3593], new named_type(IFC4X3_TC1_IfcInteger_type), true),
            new attribute(strings[3594], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3595], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStairFlightTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStairFlightType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStairFlightTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStairType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStairTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralAction_type->set_attributes({
            new attribute(strings[3596], new named_type(IFC4X3_TC1_IfcBoolean_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralActivity_type->set_attributes({
            new attribute(strings[3597], new named_type(IFC4X3_TC1_IfcStructuralLoad_type), false),
            new attribute(strings[3598], new named_type(IFC4X3_TC1_IfcGlobalOrLocalEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralAnalysisModel_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcAnalysisModelTypeEnum_type), false),
            new attribute(strings[3599], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), true),
            new attribute(strings[3600], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcStructuralLoadGroup_type)), true),
            new attribute(strings[3601], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcStructuralResultGroup_type)), true),
            new attribute(strings[3602], new named_type(IFC4X3_TC1_IfcObjectPlacement_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralConnection_type->set_attributes({
            new attribute(strings[3479], new named_type(IFC4X3_TC1_IfcBoundaryCondition_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralConnectionCondition_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_TC1_IfcStructuralCurveAction_type->set_attributes({
            new attribute(strings[3603], new named_type(IFC4X3_TC1_IfcProjectedOrTrueLengthEnum_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStructuralCurveActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralCurveConnection_type->set_attributes({
            new attribute(strings[3604], new named_type(IFC4X3_TC1_IfcDirection_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralCurveMember_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStructuralCurveMemberTypeEnum_type), false),
            new attribute(strings[2932], new named_type(IFC4X3_TC1_IfcDirection_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralCurveMemberVarying_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralCurveReaction_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStructuralCurveActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralItem_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLinearAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoad_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_TC1_IfcStructuralLoadCase_type->set_attributes({
            new attribute(strings[3605], new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_TC1_IfcRatioMeasure_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadConfiguration_type->set_attributes({
            new attribute(strings[3218], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcStructuralLoadOrResult_type)), false),
            new attribute(strings[3606], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X3_TC1_IfcLengthMeasure_type))), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadGroup_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcLoadGroupTypeEnum_type), false),
            new attribute(strings[3607], new named_type(IFC4X3_TC1_IfcActionTypeEnum_type), false),
            new attribute(strings[3608], new named_type(IFC4X3_TC1_IfcActionSourceTypeEnum_type), false),
            new attribute(strings[3609], new named_type(IFC4X3_TC1_IfcRatioMeasure_type), true),
            new attribute(strings[2862], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadLinearForce_type->set_attributes({
            new attribute(strings[3610], new named_type(IFC4X3_TC1_IfcLinearForceMeasure_type), true),
            new attribute(strings[3611], new named_type(IFC4X3_TC1_IfcLinearForceMeasure_type), true),
            new attribute(strings[3612], new named_type(IFC4X3_TC1_IfcLinearForceMeasure_type), true),
            new attribute(strings[3613], new named_type(IFC4X3_TC1_IfcLinearMomentMeasure_type), true),
            new attribute(strings[3614], new named_type(IFC4X3_TC1_IfcLinearMomentMeasure_type), true),
            new attribute(strings[3615], new named_type(IFC4X3_TC1_IfcLinearMomentMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadOrResult_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcStructuralLoadPlanarForce_type->set_attributes({
            new attribute(strings[3616], new named_type(IFC4X3_TC1_IfcPlanarForceMeasure_type), true),
            new attribute(strings[3617], new named_type(IFC4X3_TC1_IfcPlanarForceMeasure_type), true),
            new attribute(strings[3618], new named_type(IFC4X3_TC1_IfcPlanarForceMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadSingleDisplacement_type->set_attributes({
            new attribute(strings[3619], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3620], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3621], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3622], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3623], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3624], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadSingleDisplacementDistortion_type->set_attributes({
            new attribute(strings[3625], new named_type(IFC4X3_TC1_IfcCurvatureMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadSingleForce_type->set_attributes({
            new attribute(strings[3626], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3627], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3628], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3629], new named_type(IFC4X3_TC1_IfcTorqueMeasure_type), true),
            new attribute(strings[3630], new named_type(IFC4X3_TC1_IfcTorqueMeasure_type), true),
            new attribute(strings[3631], new named_type(IFC4X3_TC1_IfcTorqueMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadSingleForceWarping_type->set_attributes({
            new attribute(strings[3632], new named_type(IFC4X3_TC1_IfcWarpingMomentMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralLoadStatic_type->set_attributes({
    },{
            false
    });
    IFC4X3_TC1_IfcStructuralLoadTemperature_type->set_attributes({
            new attribute(strings[3633], new named_type(IFC4X3_TC1_IfcThermodynamicTemperatureMeasure_type), true),
            new attribute(strings[3634], new named_type(IFC4X3_TC1_IfcThermodynamicTemperatureMeasure_type), true),
            new attribute(strings[3635], new named_type(IFC4X3_TC1_IfcThermodynamicTemperatureMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralMember_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralPlanarAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralPointAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralPointConnection_type->set_attributes({
            new attribute(strings[3482], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralPointReaction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralReaction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralResultGroup_type->set_attributes({
            new attribute(strings[3636], new named_type(IFC4X3_TC1_IfcAnalysisTheoryTypeEnum_type), false),
            new attribute(strings[3637], new named_type(IFC4X3_TC1_IfcStructuralLoadGroup_type), true),
            new attribute(strings[3638], new named_type(IFC4X3_TC1_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralSurfaceAction_type->set_attributes({
            new attribute(strings[3603], new named_type(IFC4X3_TC1_IfcProjectedOrTrueLengthEnum_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStructuralSurfaceActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralSurfaceConnection_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralSurfaceMember_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStructuralSurfaceMemberTypeEnum_type), false),
            new attribute(strings[3000], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralSurfaceMemberVarying_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStructuralSurfaceReaction_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcStructuralSurfaceActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcStyleModel_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcStyledItem_type->set_attributes({
            new attribute(strings[3639], new named_type(IFC4X3_TC1_IfcRepresentationItem_type), true),
            new attribute(strings[3640], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPresentationStyle_type)), false),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcStyledRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcSubContractResource_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSubContractResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSubContractResourceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSubContractResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSubedge_type->set_attributes({
            new attribute(strings[3641], new named_type(IFC4X3_TC1_IfcEdge_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSurface_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcSurfaceCurve_type->set_attributes({
            new attribute(strings[3642], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3643], new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X3_TC1_IfcPcurve_type)), false),
            new attribute(strings[3644], new named_type(IFC4X3_TC1_IfcPreferredSurfaceCurveRepresentation_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSurfaceCurveSweptAreaSolid_type->set_attributes({
            new attribute(strings[3645], new named_type(IFC4X3_TC1_IfcSurface_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSurfaceFeature_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSurfaceFeatureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSurfaceOfLinearExtrusion_type->set_attributes({
            new attribute(strings[3157], new named_type(IFC4X3_TC1_IfcDirection_type), false),
            new attribute(strings[2985], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcSurfaceOfRevolution_type->set_attributes({
            new attribute(strings[3646], new named_type(IFC4X3_TC1_IfcAxis1Placement_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSurfaceReinforcementArea_type->set_attributes({
            new attribute(strings[3647], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X3_TC1_IfcLengthMeasure_type)), true),
            new attribute(strings[3648], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X3_TC1_IfcLengthMeasure_type)), true),
            new attribute(strings[3649], new named_type(IFC4X3_TC1_IfcRatioMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcSurfaceStyle_type->set_attributes({
            new attribute(strings[3650], new named_type(IFC4X3_TC1_IfcSurfaceSide_type), false),
            new attribute(strings[3640], new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC4X3_TC1_IfcSurfaceStyleElementSelect_type)), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcSurfaceStyleLighting_type->set_attributes({
            new attribute(strings[3651], new named_type(IFC4X3_TC1_IfcColourRgb_type), false),
            new attribute(strings[3652], new named_type(IFC4X3_TC1_IfcColourRgb_type), false),
            new attribute(strings[3653], new named_type(IFC4X3_TC1_IfcColourRgb_type), false),
            new attribute(strings[3654], new named_type(IFC4X3_TC1_IfcColourRgb_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcSurfaceStyleRefraction_type->set_attributes({
            new attribute(strings[3655], new named_type(IFC4X3_TC1_IfcReal_type), true),
            new attribute(strings[3656], new named_type(IFC4X3_TC1_IfcReal_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcSurfaceStyleRendering_type->set_attributes({
            new attribute(strings[3657], new named_type(IFC4X3_TC1_IfcColourOrFactor_type), true),
            new attribute(strings[3653], new named_type(IFC4X3_TC1_IfcColourOrFactor_type), true),
            new attribute(strings[3651], new named_type(IFC4X3_TC1_IfcColourOrFactor_type), true),
            new attribute(strings[3658], new named_type(IFC4X3_TC1_IfcColourOrFactor_type), true),
            new attribute(strings[3659], new named_type(IFC4X3_TC1_IfcColourOrFactor_type), true),
            new attribute(strings[3660], new named_type(IFC4X3_TC1_IfcSpecularHighlightSelect_type), true),
            new attribute(strings[3661], new named_type(IFC4X3_TC1_IfcReflectanceMethodEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSurfaceStyleShading_type->set_attributes({
            new attribute(strings[3662], new named_type(IFC4X3_TC1_IfcColourRgb_type), false),
            new attribute(strings[3663], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcSurfaceStyleWithTextures_type->set_attributes({
            new attribute(strings[3664], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcSurfaceTexture_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcSurfaceTexture_type->set_attributes({
            new attribute(strings[3665], new named_type(IFC4X3_TC1_IfcBoolean_type), false),
            new attribute(strings[3666], new named_type(IFC4X3_TC1_IfcBoolean_type), false),
            new attribute(strings[3667], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3668], new named_type(IFC4X3_TC1_IfcCartesianTransformationOperator2D_type), true),
            new attribute(strings[3669], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcIdentifier_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcSweptAreaSolid_type->set_attributes({
            new attribute(strings[3670], new named_type(IFC4X3_TC1_IfcProfileDef_type), false),
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcSweptDiskSolid_type->set_attributes({
            new attribute(strings[3094], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3001], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3671], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3095], new named_type(IFC4X3_TC1_IfcParameterValue_type), true),
            new attribute(strings[3096], new named_type(IFC4X3_TC1_IfcParameterValue_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcSweptDiskSolidPolygonal_type->set_attributes({
            new attribute(strings[3201], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSweptSurface_type->set_attributes({
            new attribute(strings[3672], new named_type(IFC4X3_TC1_IfcProfileDef_type), false),
            new attribute(strings[3023], new named_type(IFC4X3_TC1_IfcAxis2Placement3D_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcSwitchingDevice_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSwitchingDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSwitchingDeviceType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSwitchingDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSystem_type->set_attributes({
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcSystemFurnitureElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSystemFurnitureElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcSystemFurnitureElementType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcSystemFurnitureElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTShapeProfileDef_type->set_attributes({
            new attribute(strings[2985], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3673], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2922], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3200], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3201], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3202], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3674], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3675], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3203], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTable_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3676], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcTableRow_type)), true),
            new attribute(strings[3677], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcTableColumn_type)), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcTableColumn_type->set_attributes({
            new attribute(strings[2900], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3084], new named_type(IFC4X3_TC1_IfcUnit_type), true),
            new attribute(strings[3298], new named_type(IFC4X3_TC1_IfcReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcTableRow_type->set_attributes({
            new attribute(strings[3678], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcValue_type)), true),
            new attribute(strings[3679], new named_type(IFC4X3_TC1_IfcBoolean_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcTank_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTankTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTankType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTankTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTask_type->set_attributes({
            new attribute(strings[2856], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3680], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3681], new named_type(IFC4X3_TC1_IfcBoolean_type), false),
            new attribute(strings[3270], new named_type(IFC4X3_TC1_IfcInteger_type), true),
            new attribute(strings[3682], new named_type(IFC4X3_TC1_IfcTaskTime_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTaskTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTaskTime_type->set_attributes({
            new attribute(strings[3224], new named_type(IFC4X3_TC1_IfcTaskDurationEnum_type), true),
            new attribute(strings[3683], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3530], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3531], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3684], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3685], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3686], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3687], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3688], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3689], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3690], new named_type(IFC4X3_TC1_IfcBoolean_type), true),
            new attribute(strings[3535], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3691], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3538], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3539], new named_type(IFC4X3_TC1_IfcDateTime_type), true),
            new attribute(strings[3692], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3542], new named_type(IFC4X3_TC1_IfcPositiveRatioMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTaskTimeRecurring_type->set_attributes({
            new attribute(strings[3693], new named_type(IFC4X3_TC1_IfcRecurrencePattern_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTaskType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTaskTypeEnum_type), false),
            new attribute(strings[3680], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTelecomAddress_type->set_attributes({
            new attribute(strings[3694], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true),
            new attribute(strings[3695], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true),
            new attribute(strings[3696], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3697], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcLabel_type)), true),
            new attribute(strings[3698], new named_type(IFC4X3_TC1_IfcURIReference_type), true),
            new attribute(strings[3699], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcURIReference_type)), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTendon_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTendonTypeEnum_type), true),
            new attribute(strings[3293], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3436], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), true),
            new attribute(strings[3700], new named_type(IFC4X3_TC1_IfcForceMeasure_type), true),
            new attribute(strings[3701], new named_type(IFC4X3_TC1_IfcPressureMeasure_type), true),
            new attribute(strings[3702], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3703], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3704], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTendonAnchor_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTendonAnchorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTendonAnchorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTendonAnchorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTendonConduit_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTendonConduitTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTendonConduitType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTendonConduitTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTendonType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTendonTypeEnum_type), false),
            new attribute(strings[3293], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3436], new named_type(IFC4X3_TC1_IfcAreaMeasure_type), true),
            new attribute(strings[3705], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTessellatedFaceSet_type->set_attributes({
            new attribute(strings[2990], new named_type(IFC4X3_TC1_IfcCartesianPointList3D_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcTessellatedItem_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcTextLiteral_type->set_attributes({
            new attribute(strings[3706], new named_type(IFC4X3_TC1_IfcPresentableText_type), false),
            new attribute(strings[3069], new named_type(IFC4X3_TC1_IfcAxis2Placement_type), false),
            new attribute(strings[3707], new named_type(IFC4X3_TC1_IfcTextPath_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcTextLiteralWithExtent_type->set_attributes({
            new attribute(strings[3708], new named_type(IFC4X3_TC1_IfcPlanarExtent_type), false),
            new attribute(strings[3709], new named_type(IFC4X3_TC1_IfcBoxAlignment_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcTextStyle_type->set_attributes({
            new attribute(strings[3710], new named_type(IFC4X3_TC1_IfcTextStyleForDefinedFont_type), true),
            new attribute(strings[3711], new named_type(IFC4X3_TC1_IfcTextStyleTextModel_type), true),
            new attribute(strings[3712], new named_type(IFC4X3_TC1_IfcTextFontSelect_type), false),
            new attribute(strings[3074], new named_type(IFC4X3_TC1_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcTextStyleFontModel_type->set_attributes({
            new attribute(strings[3713], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcTextFontName_type)), false),
            new attribute(strings[3714], new named_type(IFC4X3_TC1_IfcFontStyle_type), true),
            new attribute(strings[3715], new named_type(IFC4X3_TC1_IfcFontVariant_type), true),
            new attribute(strings[3716], new named_type(IFC4X3_TC1_IfcFontWeight_type), true),
            new attribute(strings[3717], new named_type(IFC4X3_TC1_IfcSizeSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTextStyleForDefinedFont_type->set_attributes({
            new attribute(strings[3718], new named_type(IFC4X3_TC1_IfcColour_type), false),
            new attribute(strings[3719], new named_type(IFC4X3_TC1_IfcColour_type), true)
    },{
            false, false
    });
    IFC4X3_TC1_IfcTextStyleTextModel_type->set_attributes({
            new attribute(strings[3720], new named_type(IFC4X3_TC1_IfcSizeSelect_type), true),
            new attribute(strings[3721], new named_type(IFC4X3_TC1_IfcTextAlignment_type), true),
            new attribute(strings[3722], new named_type(IFC4X3_TC1_IfcTextDecoration_type), true),
            new attribute(strings[3723], new named_type(IFC4X3_TC1_IfcSizeSelect_type), true),
            new attribute(strings[3724], new named_type(IFC4X3_TC1_IfcSizeSelect_type), true),
            new attribute(strings[3725], new named_type(IFC4X3_TC1_IfcTextTransformation_type), true),
            new attribute(strings[3726], new named_type(IFC4X3_TC1_IfcSizeSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTextureCoordinate_type->set_attributes({
            new attribute(strings[3727], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcSurfaceTexture_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcTextureCoordinateGenerator_type->set_attributes({
            new attribute(strings[3667], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[3669], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcReal_type)), true)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcTextureCoordinateIndices_type->set_attributes({
            new attribute(strings[3214], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_TC1_IfcPositiveInteger_type)), false),
            new attribute(strings[3728], new named_type(IFC4X3_TC1_IfcIndexedPolygonalFace_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcTextureCoordinateIndicesWithVoids_type->set_attributes({
            new attribute(strings[3729], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_TC1_IfcPositiveInteger_type))), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcTextureMap_type->set_attributes({
            new attribute(strings[3730], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_TC1_IfcTextureVertex_type)), false),
            new attribute(strings[3205], new named_type(IFC4X3_TC1_IfcFace_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcTextureVertex_type->set_attributes({
            new attribute(strings[2990], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_TC1_IfcParameterValue_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcTextureVertexList_type->set_attributes({
            new attribute(strings[3731], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_TC1_IfcParameterValue_type))), false)
    },{
            false
    });
    IFC4X3_TC1_IfcThirdOrderPolynomialSpiral_type->set_attributes({
            new attribute(strings[3570], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false),
            new attribute(strings[3551], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3552], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3055], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcTimePeriod_type->set_attributes({
            new attribute(strings[3732], new named_type(IFC4X3_TC1_IfcTime_type), false),
            new attribute(strings[3733], new named_type(IFC4X3_TC1_IfcTime_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcTimeSeries_type->set_attributes({
            new attribute(strings[2891], new named_type(IFC4X3_TC1_IfcLabel_type), false),
            new attribute(strings[2861], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3732], new named_type(IFC4X3_TC1_IfcDateTime_type), false),
            new attribute(strings[3733], new named_type(IFC4X3_TC1_IfcDateTime_type), false),
            new attribute(strings[3734], new named_type(IFC4X3_TC1_IfcTimeSeriesDataTypeEnum_type), false),
            new attribute(strings[3549], new named_type(IFC4X3_TC1_IfcDataOriginEnum_type), false),
            new attribute(strings[3550], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3084], new named_type(IFC4X3_TC1_IfcUnit_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTimeSeriesValue_type->set_attributes({
            new attribute(strings[3220], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcValue_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcTopologicalRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcTopologyRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_TC1_IfcToroidalSurface_type->set_attributes({
            new attribute(strings[3735], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3736], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_TC1_IfcTrackElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTrackElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTrackElementType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTrackElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTransformer_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTransformerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTransformerType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTransformerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTransportElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTransportElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTransportElementType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTransportElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTransportationDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTransportationDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTrapeziumProfileDef_type->set_attributes({
            new attribute(strings[3737], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3738], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2977], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3739], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTriangulatedFaceSet_type->set_attributes({
            new attribute(strings[3740], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_TC1_IfcParameterValue_type))), true),
            new attribute(strings[3355], new named_type(IFC4X3_TC1_IfcBoolean_type), true),
            new attribute(strings[3210], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_TC1_IfcPositiveInteger_type))), false),
            new attribute(strings[3357], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcPositiveInteger_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcTriangulatedIrregularNetwork_type->set_attributes({
            new attribute(strings[3741], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcInteger_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTrimmedCurve_type->set_attributes({
            new attribute(strings[3306], new named_type(IFC4X3_TC1_IfcCurve_type), false),
            new attribute(strings[3742], new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X3_TC1_IfcTrimmingSelect_type)), false),
            new attribute(strings[3743], new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X3_TC1_IfcTrimmingSelect_type)), false),
            new attribute(strings[3744], new named_type(IFC4X3_TC1_IfcBoolean_type), false),
            new attribute(strings[3644], new named_type(IFC4X3_TC1_IfcTrimmingPreference_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_TC1_IfcTubeBundle_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTubeBundleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTubeBundleType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcTubeBundleTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTypeObject_type->set_attributes({
            new attribute(strings[3745], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[3746], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPropertySetDefinition_type)), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTypeProcess_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2857], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3747], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTypeProduct_type->set_attributes({
            new attribute(strings[3748], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_TC1_IfcRepresentationMap_type)), true),
            new attribute(strings[3140], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcTypeResource_type->set_attributes({
            new attribute(strings[2911], new named_type(IFC4X3_TC1_IfcIdentifier_type), true),
            new attribute(strings[2857], new named_type(IFC4X3_TC1_IfcText_type), true),
            new attribute(strings[3749], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcUShapeProfileDef_type->set_attributes({
            new attribute(strings[2985], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3673], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2922], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3200], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3201], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3221], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3203], new named_type(IFC4X3_TC1_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcUnitAssignment_type->set_attributes({
            new attribute(strings[3750], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcUnit_type)), false)
    },{
            false
    });
    IFC4X3_TC1_IfcUnitaryControlElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcUnitaryControlElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcUnitaryControlElementType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcUnitaryControlElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcUnitaryEquipment_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcUnitaryEquipmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcUnitaryEquipmentType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcUnitaryEquipmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcValve_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcValveTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcValveType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcValveTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcVector_type->set_attributes({
            new attribute(strings[3162], new named_type(IFC4X3_TC1_IfcDirection_type), false),
            new attribute(strings[3751], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcVehicle_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcVehicleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcVehicleType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcVehicleTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcVertex_type->set_attributes({
    },{
            
    });
    IFC4X3_TC1_IfcVertexLoop_type->set_attributes({
            new attribute(strings[3752], new named_type(IFC4X3_TC1_IfcVertex_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcVertexPoint_type->set_attributes({
            new attribute(strings[3753], new named_type(IFC4X3_TC1_IfcPoint_type), false)
    },{
            false
    });
    IFC4X3_TC1_IfcVibrationDamper_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcVibrationDamperTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcVibrationDamperType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcVibrationDamperTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcVibrationIsolator_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcVibrationIsolatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcVibrationIsolatorType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcVibrationIsolatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcVirtualElement_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcVirtualElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcVirtualGridIntersection_type->set_attributes({
            new attribute(strings[3754], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_TC1_IfcGridAxis_type)), false),
            new attribute(strings[3755], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X3_TC1_IfcLengthMeasure_type)), false)
    },{
            false, false
    });
    IFC4X3_TC1_IfcVoidingFeature_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcVoidingFeatureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWall_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWallTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWallStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWallType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWallTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWasteTerminal_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWasteTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWasteTerminalType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWasteTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWindow_type->set_attributes({
            new attribute(strings[3114], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3115], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWindowTypeEnum_type), true),
            new attribute(strings[3756], new named_type(IFC4X3_TC1_IfcWindowTypePartitioningEnum_type), true),
            new attribute(strings[3757], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWindowLiningProperties_type->set_attributes({
            new attribute(strings[3118], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3119], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3122], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3758], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3759], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3760], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3761], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3762], new named_type(IFC4X3_TC1_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3128], new named_type(IFC4X3_TC1_IfcShapeAspect_type), true),
            new attribute(strings[3124], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3129], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true),
            new attribute(strings[3130], new named_type(IFC4X3_TC1_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWindowPanelProperties_type->set_attributes({
            new attribute(strings[3116], new named_type(IFC4X3_TC1_IfcWindowPanelOperationEnum_type), false),
            new attribute(strings[3134], new named_type(IFC4X3_TC1_IfcWindowPanelPositionEnum_type), false),
            new attribute(strings[3328], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3329], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3128], new named_type(IFC4X3_TC1_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWindowType_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWindowTypeEnum_type), false),
            new attribute(strings[3756], new named_type(IFC4X3_TC1_IfcWindowTypePartitioningEnum_type), false),
            new attribute(strings[3135], new named_type(IFC4X3_TC1_IfcBoolean_type), true),
            new attribute(strings[3757], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWorkCalendar_type->set_attributes({
            new attribute(strings[3763], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcWorkTime_type)), true),
            new attribute(strings[3764], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcWorkTime_type)), true),
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWorkCalendarTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWorkControl_type->set_attributes({
            new attribute(strings[3325], new named_type(IFC4X3_TC1_IfcDateTime_type), false),
            new attribute(strings[3765], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_TC1_IfcPerson_type)), true),
            new attribute(strings[2862], new named_type(IFC4X3_TC1_IfcLabel_type), true),
            new attribute(strings[3766], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3689], new named_type(IFC4X3_TC1_IfcDuration_type), true),
            new attribute(strings[3732], new named_type(IFC4X3_TC1_IfcDateTime_type), false),
            new attribute(strings[3767], new named_type(IFC4X3_TC1_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWorkPlan_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWorkPlanTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWorkSchedule_type->set_attributes({
            new attribute(strings[2855], new named_type(IFC4X3_TC1_IfcWorkScheduleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcWorkTime_type->set_attributes({
            new attribute(strings[3768], new named_type(IFC4X3_TC1_IfcRecurrencePattern_type), true),
            new attribute(strings[3769], new named_type(IFC4X3_TC1_IfcDate_type), true),
            new attribute(strings[3770], new named_type(IFC4X3_TC1_IfcDate_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcZShapeProfileDef_type->set_attributes({
            new attribute(strings[2985], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3673], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2922], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3200], new named_type(IFC4X3_TC1_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3201], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3221], new named_type(IFC4X3_TC1_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcZone_type->set_attributes({
            new attribute(strings[2984], new named_type(IFC4X3_TC1_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_TC1_IfcActor_type->set_inverse_attributes({
            new inverse_attribute(strings[3771], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToActor_type, IFC4X3_TC1_IfcRelAssignsToActor_type->attributes()[0])
    });
    IFC4X3_TC1_IfcActorRole_type->set_inverse_attributes({
            new inverse_attribute(strings[3772], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_TC1_IfcAddress_type->set_inverse_attributes({
            new inverse_attribute(strings[3773], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcPerson_type, IFC4X3_TC1_IfcPerson_type->attributes()[7]),
            new inverse_attribute(strings[3774], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcOrganization_type, IFC4X3_TC1_IfcOrganization_type->attributes()[4])
    });
    IFC4X3_TC1_IfcAnnotation_type->set_inverse_attributes({
            new inverse_attribute(strings[3775], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelContainedInSpatialStructure_type, IFC4X3_TC1_IfcRelContainedInSpatialStructure_type->attributes()[0])
    });
    IFC4X3_TC1_IfcAppliedValue_type->set_inverse_attributes({
            new inverse_attribute(strings[3772], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_TC1_IfcApproval_type->set_inverse_attributes({
            new inverse_attribute(strings[3776], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3777], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociatesApproval_type, IFC4X3_TC1_IfcRelAssociatesApproval_type->attributes()[0]),
            new inverse_attribute(strings[3778], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcResourceApprovalRelationship_type, IFC4X3_TC1_IfcResourceApprovalRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3779], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcApprovalRelationship_type, IFC4X3_TC1_IfcApprovalRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3780], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcApprovalRelationship_type, IFC4X3_TC1_IfcApprovalRelationship_type->attributes()[0])
    });
    IFC4X3_TC1_IfcClassification_type->set_inverse_attributes({
            new inverse_attribute(strings[3781], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociatesClassification_type, IFC4X3_TC1_IfcRelAssociatesClassification_type->attributes()[0]),
            new inverse_attribute(strings[3782], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcClassificationReference_type, IFC4X3_TC1_IfcClassificationReference_type->attributes()[0])
    });
    IFC4X3_TC1_IfcClassificationReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3783], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociatesClassification_type, IFC4X3_TC1_IfcRelAssociatesClassification_type->attributes()[0]),
            new inverse_attribute(strings[3782], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcClassificationReference_type, IFC4X3_TC1_IfcClassificationReference_type->attributes()[0])
    });
    IFC4X3_TC1_IfcConstraint_type->set_inverse_attributes({
            new inverse_attribute(strings[3776], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3784], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcResourceConstraintRelationship_type, IFC4X3_TC1_IfcResourceConstraintRelationship_type->attributes()[0])
    });
    IFC4X3_TC1_IfcContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3785], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelDefinesByProperties_type, IFC4X3_TC1_IfcRelDefinesByProperties_type->attributes()[0]),
            new inverse_attribute(strings[3786], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelDeclares_type, IFC4X3_TC1_IfcRelDeclares_type->attributes()[0])
    });
    IFC4X3_TC1_IfcContextDependentUnit_type->set_inverse_attributes({
            new inverse_attribute(strings[3772], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_TC1_IfcControl_type->set_inverse_attributes({
            new inverse_attribute(strings[3787], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToControl_type, IFC4X3_TC1_IfcRelAssignsToControl_type->attributes()[0])
    });
    IFC4X3_TC1_IfcConversionBasedUnit_type->set_inverse_attributes({
            new inverse_attribute(strings[3772], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_TC1_IfcCoordinateReferenceSystem_type->set_inverse_attributes({
            new inverse_attribute(strings[3788], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcCoordinateOperation_type, IFC4X3_TC1_IfcCoordinateOperation_type->attributes()[0])
    });
    IFC4X3_TC1_IfcCovering_type->set_inverse_attributes({
            new inverse_attribute(strings[3789], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelCoversSpaces_type, IFC4X3_TC1_IfcRelCoversSpaces_type->attributes()[1]),
            new inverse_attribute(strings[3790], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelCoversBldgElements_type, IFC4X3_TC1_IfcRelCoversBldgElements_type->attributes()[1])
    });
    IFC4X3_TC1_IfcDistributionControlElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3791], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelFlowControlElements_type, IFC4X3_TC1_IfcRelFlowControlElements_type->attributes()[0])
    });
    IFC4X3_TC1_IfcDistributionElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3792], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelConnectsPortToElement_type, IFC4X3_TC1_IfcRelConnectsPortToElement_type->attributes()[1])
    });
    IFC4X3_TC1_IfcDistributionFlowElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3793], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelFlowControlElements_type, IFC4X3_TC1_IfcRelFlowControlElements_type->attributes()[1])
    });
    IFC4X3_TC1_IfcDocumentInformation_type->set_inverse_attributes({
            new inverse_attribute(strings[3794], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociatesDocument_type, IFC4X3_TC1_IfcRelAssociatesDocument_type->attributes()[0]),
            new inverse_attribute(strings[3795], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcDocumentReference_type, IFC4X3_TC1_IfcDocumentReference_type->attributes()[1]),
            new inverse_attribute(strings[3796], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcDocumentInformationRelationship_type, IFC4X3_TC1_IfcDocumentInformationRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3797], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcDocumentInformationRelationship_type, IFC4X3_TC1_IfcDocumentInformationRelationship_type->attributes()[0])
    });
    IFC4X3_TC1_IfcDocumentReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3798], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociatesDocument_type, IFC4X3_TC1_IfcRelAssociatesDocument_type->attributes()[0])
    });
    IFC4X3_TC1_IfcElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3799], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelFillsElement_type, IFC4X3_TC1_IfcRelFillsElement_type->attributes()[1]),
            new inverse_attribute(strings[3800], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelConnectsElements_type, IFC4X3_TC1_IfcRelConnectsElements_type->attributes()[1]),
            new inverse_attribute(strings[3801], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelInterferesElements_type, IFC4X3_TC1_IfcRelInterferesElements_type->attributes()[1]),
            new inverse_attribute(strings[3802], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelInterferesElements_type, IFC4X3_TC1_IfcRelInterferesElements_type->attributes()[0]),
            new inverse_attribute(strings[3803], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelProjectsElement_type, IFC4X3_TC1_IfcRelProjectsElement_type->attributes()[0]),
            new inverse_attribute(strings[3804], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelVoidsElement_type, IFC4X3_TC1_IfcRelVoidsElement_type->attributes()[0]),
            new inverse_attribute(strings[3805], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelConnectsWithRealizingElements_type, IFC4X3_TC1_IfcRelConnectsWithRealizingElements_type->attributes()[0]),
            new inverse_attribute(strings[3806], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelSpaceBoundary_type, IFC4X3_TC1_IfcRelSpaceBoundary_type->attributes()[1]),
            new inverse_attribute(strings[3807], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelConnectsElements_type, IFC4X3_TC1_IfcRelConnectsElements_type->attributes()[2]),
            new inverse_attribute(strings[3775], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelContainedInSpatialStructure_type, IFC4X3_TC1_IfcRelContainedInSpatialStructure_type->attributes()[0]),
            new inverse_attribute(strings[3808], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelCoversBldgElements_type, IFC4X3_TC1_IfcRelCoversBldgElements_type->attributes()[0]),
            new inverse_attribute(strings[3809], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAdheresToElement_type, IFC4X3_TC1_IfcRelAdheresToElement_type->attributes()[0])
    });
    IFC4X3_TC1_IfcExternalReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3810], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[0])
    });
    IFC4X3_TC1_IfcExternalSpatialElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3811], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelSpaceBoundary_type, IFC4X3_TC1_IfcRelSpaceBoundary_type->attributes()[0])
    });
    IFC4X3_TC1_IfcFace_type->set_inverse_attributes({
            new inverse_attribute(strings[3812], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcTextureMap_type, IFC4X3_TC1_IfcTextureMap_type->attributes()[1])
    });
    IFC4X3_TC1_IfcFeatureElementAddition_type->set_inverse_attributes({
            new inverse_attribute(strings[3813], inverse_attribute::unspecified_type, -1, -1, IFC4X3_TC1_IfcRelProjectsElement_type, IFC4X3_TC1_IfcRelProjectsElement_type->attributes()[1])
    });
    IFC4X3_TC1_IfcFeatureElementSubtraction_type->set_inverse_attributes({
            new inverse_attribute(strings[3814], inverse_attribute::unspecified_type, -1, -1, IFC4X3_TC1_IfcRelVoidsElement_type, IFC4X3_TC1_IfcRelVoidsElement_type->attributes()[1])
    });
    IFC4X3_TC1_IfcGeometricRepresentationContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3815], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcGeometricRepresentationSubContext_type, IFC4X3_TC1_IfcGeometricRepresentationSubContext_type->attributes()[0]),
            new inverse_attribute(strings[3788], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcCoordinateOperation_type, IFC4X3_TC1_IfcCoordinateOperation_type->attributes()[0])
    });
    IFC4X3_TC1_IfcGridAxis_type->set_inverse_attributes({
            new inverse_attribute(strings[3816], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcGrid_type, IFC4X3_TC1_IfcGrid_type->attributes()[2]),
            new inverse_attribute(strings[3817], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcGrid_type, IFC4X3_TC1_IfcGrid_type->attributes()[1]),
            new inverse_attribute(strings[3818], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcGrid_type, IFC4X3_TC1_IfcGrid_type->attributes()[0]),
            new inverse_attribute(strings[3819], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcVirtualGridIntersection_type, IFC4X3_TC1_IfcVirtualGridIntersection_type->attributes()[0])
    });
    IFC4X3_TC1_IfcGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3820], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToGroup_type, IFC4X3_TC1_IfcRelAssignsToGroup_type->attributes()[0]),
            new inverse_attribute(strings[3821], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type, IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type->attributes()[0])
    });
    IFC4X3_TC1_IfcIndexedPolygonalFace_type->set_inverse_attributes({
            new inverse_attribute(strings[3822], inverse_attribute::set_type, 1, -1, IFC4X3_TC1_IfcPolygonalFaceSet_type, IFC4X3_TC1_IfcPolygonalFaceSet_type->attributes()[1]),
            new inverse_attribute(strings[3823], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcTextureCoordinateIndices_type, IFC4X3_TC1_IfcTextureCoordinateIndices_type->attributes()[1])
    });
    IFC4X3_TC1_IfcLibraryInformation_type->set_inverse_attributes({
            new inverse_attribute(strings[3824], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociatesLibrary_type, IFC4X3_TC1_IfcRelAssociatesLibrary_type->attributes()[0]),
            new inverse_attribute(strings[3825], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcLibraryReference_type, IFC4X3_TC1_IfcLibraryReference_type->attributes()[2])
    });
    IFC4X3_TC1_IfcLibraryReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3826], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociatesLibrary_type, IFC4X3_TC1_IfcRelAssociatesLibrary_type->attributes()[0])
    });
    IFC4X3_TC1_IfcMaterial_type->set_inverse_attributes({
            new inverse_attribute(strings[3827], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcMaterialDefinitionRepresentation_type, IFC4X3_TC1_IfcMaterialDefinitionRepresentation_type->attributes()[0]),
            new inverse_attribute(strings[3779], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcMaterialRelationship_type, IFC4X3_TC1_IfcMaterialRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3828], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcMaterialRelationship_type, IFC4X3_TC1_IfcMaterialRelationship_type->attributes()[0])
    });
    IFC4X3_TC1_IfcMaterialConstituent_type->set_inverse_attributes({
            new inverse_attribute(strings[3829], inverse_attribute::unspecified_type, -1, -1, IFC4X3_TC1_IfcMaterialConstituentSet_type, IFC4X3_TC1_IfcMaterialConstituentSet_type->attributes()[2])
    });
    IFC4X3_TC1_IfcMaterialDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3830], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociatesMaterial_type, IFC4X3_TC1_IfcRelAssociatesMaterial_type->attributes()[0]),
            new inverse_attribute(strings[3776], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3015], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcMaterialProperties_type, IFC4X3_TC1_IfcMaterialProperties_type->attributes()[0])
    });
    IFC4X3_TC1_IfcMaterialLayer_type->set_inverse_attributes({
            new inverse_attribute(strings[3831], inverse_attribute::unspecified_type, -1, -1, IFC4X3_TC1_IfcMaterialLayerSet_type, IFC4X3_TC1_IfcMaterialLayerSet_type->attributes()[0])
    });
    IFC4X3_TC1_IfcMaterialProfile_type->set_inverse_attributes({
            new inverse_attribute(strings[3832], inverse_attribute::unspecified_type, -1, -1, IFC4X3_TC1_IfcMaterialProfileSet_type, IFC4X3_TC1_IfcMaterialProfileSet_type->attributes()[2])
    });
    IFC4X3_TC1_IfcMaterialUsageDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3830], inverse_attribute::set_type, 1, -1, IFC4X3_TC1_IfcRelAssociatesMaterial_type, IFC4X3_TC1_IfcRelAssociatesMaterial_type->attributes()[0])
    });
    IFC4X3_TC1_IfcObject_type->set_inverse_attributes({
            new inverse_attribute(strings[3833], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelDefinesByObject_type, IFC4X3_TC1_IfcRelDefinesByObject_type->attributes()[0]),
            new inverse_attribute(strings[3786], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelDefinesByObject_type, IFC4X3_TC1_IfcRelDefinesByObject_type->attributes()[1]),
            new inverse_attribute(strings[3834], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelDefinesByType_type, IFC4X3_TC1_IfcRelDefinesByType_type->attributes()[0]),
            new inverse_attribute(strings[3785], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelDefinesByProperties_type, IFC4X3_TC1_IfcRelDefinesByProperties_type->attributes()[0])
    });
    IFC4X3_TC1_IfcObjectDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3835], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssigns_type, IFC4X3_TC1_IfcRelAssigns_type->attributes()[0]),
            new inverse_attribute(strings[3836], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelNests_type, IFC4X3_TC1_IfcRelNests_type->attributes()[1]),
            new inverse_attribute(strings[3837], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelNests_type, IFC4X3_TC1_IfcRelNests_type->attributes()[0]),
            new inverse_attribute(strings[3838], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelDeclares_type, IFC4X3_TC1_IfcRelDeclares_type->attributes()[1]),
            new inverse_attribute(strings[3839], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAggregates_type, IFC4X3_TC1_IfcRelAggregates_type->attributes()[0]),
            new inverse_attribute(strings[3840], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelAggregates_type, IFC4X3_TC1_IfcRelAggregates_type->attributes()[1]),
            new inverse_attribute(strings[3841], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociates_type, IFC4X3_TC1_IfcRelAssociates_type->attributes()[0])
    });
    IFC4X3_TC1_IfcObjectPlacement_type->set_inverse_attributes({
            new inverse_attribute(strings[3842], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcProduct_type, IFC4X3_TC1_IfcProduct_type->attributes()[0]),
            new inverse_attribute(strings[3843], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcObjectPlacement_type, IFC4X3_TC1_IfcObjectPlacement_type->attributes()[0])
    });
    IFC4X3_TC1_IfcOpeningElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3844], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelFillsElement_type, IFC4X3_TC1_IfcRelFillsElement_type->attributes()[0])
    });
    IFC4X3_TC1_IfcOrganization_type->set_inverse_attributes({
            new inverse_attribute(strings[3845], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcOrganizationRelationship_type, IFC4X3_TC1_IfcOrganizationRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3780], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcOrganizationRelationship_type, IFC4X3_TC1_IfcOrganizationRelationship_type->attributes()[0]),
            new inverse_attribute(strings[3846], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcPersonAndOrganization_type, IFC4X3_TC1_IfcPersonAndOrganization_type->attributes()[1])
    });
    IFC4X3_TC1_IfcPerson_type->set_inverse_attributes({
            new inverse_attribute(strings[3847], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcPersonAndOrganization_type, IFC4X3_TC1_IfcPersonAndOrganization_type->attributes()[0])
    });
    IFC4X3_TC1_IfcPhysicalQuantity_type->set_inverse_attributes({
            new inverse_attribute(strings[3776], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3848], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcPhysicalComplexQuantity_type, IFC4X3_TC1_IfcPhysicalComplexQuantity_type->attributes()[0])
    });
    IFC4X3_TC1_IfcPort_type->set_inverse_attributes({
            new inverse_attribute(strings[3849], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelConnectsPortToElement_type, IFC4X3_TC1_IfcRelConnectsPortToElement_type->attributes()[0]),
            new inverse_attribute(strings[3807], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelConnectsPorts_type, IFC4X3_TC1_IfcRelConnectsPorts_type->attributes()[1]),
            new inverse_attribute(strings[3800], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelConnectsPorts_type, IFC4X3_TC1_IfcRelConnectsPorts_type->attributes()[0])
    });
    IFC4X3_TC1_IfcPositioningElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3775], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelContainedInSpatialStructure_type, IFC4X3_TC1_IfcRelContainedInSpatialStructure_type->attributes()[0]),
            new inverse_attribute(strings[3850], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelPositions_type, IFC4X3_TC1_IfcRelPositions_type->attributes()[0])
    });
    IFC4X3_TC1_IfcProcess_type->set_inverse_attributes({
            new inverse_attribute(strings[3851], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelSequence_type, IFC4X3_TC1_IfcRelSequence_type->attributes()[0]),
            new inverse_attribute(strings[3852], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelSequence_type, IFC4X3_TC1_IfcRelSequence_type->attributes()[1]),
            new inverse_attribute(strings[3853], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToProcess_type, IFC4X3_TC1_IfcRelAssignsToProcess_type->attributes()[0])
    });
    IFC4X3_TC1_IfcProduct_type->set_inverse_attributes({
            new inverse_attribute(strings[3854], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToProduct_type, IFC4X3_TC1_IfcRelAssignsToProduct_type->attributes()[0]),
            new inverse_attribute(strings[3855], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelPositions_type, IFC4X3_TC1_IfcRelPositions_type->attributes()[1]),
            new inverse_attribute(strings[3821], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type, IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type->attributes()[0])
    });
    IFC4X3_TC1_IfcProductDefinitionShape_type->set_inverse_attributes({
            new inverse_attribute(strings[3856], inverse_attribute::set_type, 1, -1, IFC4X3_TC1_IfcProduct_type, IFC4X3_TC1_IfcProduct_type->attributes()[1]),
            new inverse_attribute(strings[3857], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcShapeAspect_type, IFC4X3_TC1_IfcShapeAspect_type->attributes()[4])
    });
    IFC4X3_TC1_IfcProfileDef_type->set_inverse_attributes({
            new inverse_attribute(strings[3772], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3015], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcProfileProperties_type, IFC4X3_TC1_IfcProfileProperties_type->attributes()[0])
    });
    IFC4X3_TC1_IfcProperty_type->set_inverse_attributes({
            new inverse_attribute(strings[3858], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcPropertySet_type, IFC4X3_TC1_IfcPropertySet_type->attributes()[0]),
            new inverse_attribute(strings[3859], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcPropertyDependencyRelationship_type, IFC4X3_TC1_IfcPropertyDependencyRelationship_type->attributes()[0]),
            new inverse_attribute(strings[3860], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcPropertyDependencyRelationship_type, IFC4X3_TC1_IfcPropertyDependencyRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3848], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcComplexProperty_type, IFC4X3_TC1_IfcComplexProperty_type->attributes()[1]),
            new inverse_attribute(strings[3861], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcResourceConstraintRelationship_type, IFC4X3_TC1_IfcResourceConstraintRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3862], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcResourceApprovalRelationship_type, IFC4X3_TC1_IfcResourceApprovalRelationship_type->attributes()[0])
    });
    IFC4X3_TC1_IfcPropertyAbstraction_type->set_inverse_attributes({
            new inverse_attribute(strings[3776], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_TC1_IfcPropertyDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3838], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelDeclares_type, IFC4X3_TC1_IfcRelDeclares_type->attributes()[1]),
            new inverse_attribute(strings[3841], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssociates_type, IFC4X3_TC1_IfcRelAssociates_type->attributes()[0])
    });
    IFC4X3_TC1_IfcPropertySetDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3863], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcTypeObject_type, IFC4X3_TC1_IfcTypeObject_type->attributes()[1]),
            new inverse_attribute(strings[3785], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelDefinesByTemplate_type, IFC4X3_TC1_IfcRelDefinesByTemplate_type->attributes()[0]),
            new inverse_attribute(strings[3864], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelDefinesByProperties_type, IFC4X3_TC1_IfcRelDefinesByProperties_type->attributes()[1])
    });
    IFC4X3_TC1_IfcPropertySetTemplate_type->set_inverse_attributes({
            new inverse_attribute(strings[3865], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelDefinesByTemplate_type, IFC4X3_TC1_IfcRelDefinesByTemplate_type->attributes()[1])
    });
    IFC4X3_TC1_IfcPropertyTemplate_type->set_inverse_attributes({
            new inverse_attribute(strings[3866], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcComplexPropertyTemplate_type, IFC4X3_TC1_IfcComplexPropertyTemplate_type->attributes()[2]),
            new inverse_attribute(strings[3867], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcPropertySetTemplate_type, IFC4X3_TC1_IfcPropertySetTemplate_type->attributes()[2])
    });
    IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type->set_inverse_attributes({
            new inverse_attribute(strings[2886], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type, IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type->attributes()[0])
    });
    IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type->set_inverse_attributes({
            new inverse_attribute(strings[3868], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type, IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type->attributes()[0])
    });
    IFC4X3_TC1_IfcRepresentation_type->set_inverse_attributes({
            new inverse_attribute(strings[3869], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRepresentationMap_type, IFC4X3_TC1_IfcRepresentationMap_type->attributes()[1]),
            new inverse_attribute(strings[3870], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcPresentationLayerAssignment_type, IFC4X3_TC1_IfcPresentationLayerAssignment_type->attributes()[2]),
            new inverse_attribute(strings[3871], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcProductRepresentation_type, IFC4X3_TC1_IfcProductRepresentation_type->attributes()[2])
    });
    IFC4X3_TC1_IfcRepresentationContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3872], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRepresentation_type, IFC4X3_TC1_IfcRepresentation_type->attributes()[0])
    });
    IFC4X3_TC1_IfcRepresentationItem_type->set_inverse_attributes({
            new inverse_attribute(strings[3873], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcPresentationLayerAssignment_type, IFC4X3_TC1_IfcPresentationLayerAssignment_type->attributes()[2]),
            new inverse_attribute(strings[3874], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcStyledItem_type, IFC4X3_TC1_IfcStyledItem_type->attributes()[0])
    });
    IFC4X3_TC1_IfcRepresentationMap_type->set_inverse_attributes({
            new inverse_attribute(strings[3857], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcShapeAspect_type, IFC4X3_TC1_IfcShapeAspect_type->attributes()[4]),
            new inverse_attribute(strings[3875], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcMappedItem_type, IFC4X3_TC1_IfcMappedItem_type->attributes()[0])
    });
    IFC4X3_TC1_IfcResource_type->set_inverse_attributes({
            new inverse_attribute(strings[3876], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToResource_type, IFC4X3_TC1_IfcRelAssignsToResource_type->attributes()[0])
    });
    IFC4X3_TC1_IfcSegment_type->set_inverse_attributes({
            new inverse_attribute(strings[3877], inverse_attribute::set_type, 1, -1, IFC4X3_TC1_IfcCompositeCurve_type, IFC4X3_TC1_IfcCompositeCurve_type->attributes()[0])
    });
    IFC4X3_TC1_IfcShapeAspect_type->set_inverse_attributes({
            new inverse_attribute(strings[3776], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_TC1_IfcShapeModel_type->set_inverse_attributes({
            new inverse_attribute(strings[3878], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcShapeAspect_type, IFC4X3_TC1_IfcShapeAspect_type->attributes()[0])
    });
    IFC4X3_TC1_IfcSpace_type->set_inverse_attributes({
            new inverse_attribute(strings[3808], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelCoversSpaces_type, IFC4X3_TC1_IfcRelCoversSpaces_type->attributes()[0]),
            new inverse_attribute(strings[3811], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelSpaceBoundary_type, IFC4X3_TC1_IfcRelSpaceBoundary_type->attributes()[0])
    });
    IFC4X3_TC1_IfcSpatialElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3879], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelContainedInSpatialStructure_type, IFC4X3_TC1_IfcRelContainedInSpatialStructure_type->attributes()[1]),
            new inverse_attribute(strings[3880], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelServicesBuildings_type, IFC4X3_TC1_IfcRelServicesBuildings_type->attributes()[1]),
            new inverse_attribute(strings[3881], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type, IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type->attributes()[1]),
            new inverse_attribute(strings[3801], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelInterferesElements_type, IFC4X3_TC1_IfcRelInterferesElements_type->attributes()[1]),
            new inverse_attribute(strings[3802], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelInterferesElements_type, IFC4X3_TC1_IfcRelInterferesElements_type->attributes()[0])
    });
    IFC4X3_TC1_IfcStructuralActivity_type->set_inverse_attributes({
            new inverse_attribute(strings[3882], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelConnectsStructuralActivity_type, IFC4X3_TC1_IfcRelConnectsStructuralActivity_type->attributes()[1])
    });
    IFC4X3_TC1_IfcStructuralConnection_type->set_inverse_attributes({
            new inverse_attribute(strings[3883], inverse_attribute::set_type, 1, -1, IFC4X3_TC1_IfcRelConnectsStructuralMember_type, IFC4X3_TC1_IfcRelConnectsStructuralMember_type->attributes()[1])
    });
    IFC4X3_TC1_IfcStructuralItem_type->set_inverse_attributes({
            new inverse_attribute(strings[3884], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelConnectsStructuralActivity_type, IFC4X3_TC1_IfcRelConnectsStructuralActivity_type->attributes()[0])
    });
    IFC4X3_TC1_IfcStructuralLoadGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3885], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcStructuralResultGroup_type, IFC4X3_TC1_IfcStructuralResultGroup_type->attributes()[1]),
            new inverse_attribute(strings[3886], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcStructuralAnalysisModel_type, IFC4X3_TC1_IfcStructuralAnalysisModel_type->attributes()[2])
    });
    IFC4X3_TC1_IfcStructuralMember_type->set_inverse_attributes({
            new inverse_attribute(strings[3887], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelConnectsStructuralMember_type, IFC4X3_TC1_IfcRelConnectsStructuralMember_type->attributes()[0])
    });
    IFC4X3_TC1_IfcStructuralResultGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3888], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcStructuralAnalysisModel_type, IFC4X3_TC1_IfcStructuralAnalysisModel_type->attributes()[3])
    });
    IFC4X3_TC1_IfcSurfaceFeature_type->set_inverse_attributes({
            new inverse_attribute(strings[3889], inverse_attribute::unspecified_type, -1, -1, IFC4X3_TC1_IfcRelAdheresToElement_type, IFC4X3_TC1_IfcRelAdheresToElement_type->attributes()[1])
    });
    IFC4X3_TC1_IfcSurfaceTexture_type->set_inverse_attributes({
            new inverse_attribute(strings[3890], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcTextureCoordinate_type, IFC4X3_TC1_IfcTextureCoordinate_type->attributes()[0]),
            new inverse_attribute(strings[3891], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcSurfaceStyleWithTextures_type, IFC4X3_TC1_IfcSurfaceStyleWithTextures_type->attributes()[0])
    });
    IFC4X3_TC1_IfcSystem_type->set_inverse_attributes({
            new inverse_attribute(strings[3892], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelServicesBuildings_type, IFC4X3_TC1_IfcRelServicesBuildings_type->attributes()[0]),
            new inverse_attribute(strings[3893], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type, IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type->attributes()[0])
    });
    IFC4X3_TC1_IfcTessellatedFaceSet_type->set_inverse_attributes({
            new inverse_attribute(strings[3894], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcIndexedColourMap_type, IFC4X3_TC1_IfcIndexedColourMap_type->attributes()[0]),
            new inverse_attribute(strings[3895], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcIndexedTextureMap_type, IFC4X3_TC1_IfcIndexedTextureMap_type->attributes()[0])
    });
    IFC4X3_TC1_IfcTextureCoordinateIndices_type->set_inverse_attributes({
            new inverse_attribute(strings[3896], inverse_attribute::unspecified_type, -1, -1, IFC4X3_TC1_IfcIndexedPolygonalTextureMap_type, IFC4X3_TC1_IfcIndexedPolygonalTextureMap_type->attributes()[0])
    });
    IFC4X3_TC1_IfcTimeSeries_type->set_inverse_attributes({
            new inverse_attribute(strings[3772], inverse_attribute::set_type, 1, -1, IFC4X3_TC1_IfcExternalReferenceRelationship_type, IFC4X3_TC1_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_TC1_IfcTypeObject_type->set_inverse_attributes({
            new inverse_attribute(strings[3897], inverse_attribute::set_type, 0, 1, IFC4X3_TC1_IfcRelDefinesByType_type, IFC4X3_TC1_IfcRelDefinesByType_type->attributes()[1])
    });
    IFC4X3_TC1_IfcTypeProcess_type->set_inverse_attributes({
            new inverse_attribute(strings[3853], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToProcess_type, IFC4X3_TC1_IfcRelAssignsToProcess_type->attributes()[0])
    });
    IFC4X3_TC1_IfcTypeProduct_type->set_inverse_attributes({
            new inverse_attribute(strings[3854], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToProduct_type, IFC4X3_TC1_IfcRelAssignsToProduct_type->attributes()[0])
    });
    IFC4X3_TC1_IfcTypeResource_type->set_inverse_attributes({
            new inverse_attribute(strings[3876], inverse_attribute::set_type, 0, -1, IFC4X3_TC1_IfcRelAssignsToResource_type, IFC4X3_TC1_IfcRelAssignsToResource_type->attributes()[0])
    });
    IFC4X3_TC1_IfcControl_type->set_subtypes({
        IFC4X3_TC1_IfcActionRequest_type,IFC4X3_TC1_IfcCostItem_type,IFC4X3_TC1_IfcCostSchedule_type,IFC4X3_TC1_IfcPerformanceHistory_type,IFC4X3_TC1_IfcPermit_type,IFC4X3_TC1_IfcProjectOrder_type,IFC4X3_TC1_IfcWorkCalendar_type,IFC4X3_TC1_IfcWorkControl_type
    });
    IFC4X3_TC1_IfcObject_type->set_subtypes({
        IFC4X3_TC1_IfcActor_type,IFC4X3_TC1_IfcControl_type,IFC4X3_TC1_IfcGroup_type,IFC4X3_TC1_IfcProcess_type,IFC4X3_TC1_IfcProduct_type,IFC4X3_TC1_IfcResource_type
    });
    IFC4X3_TC1_IfcDistributionControlElement_type->set_subtypes({
        IFC4X3_TC1_IfcActuator_type,IFC4X3_TC1_IfcAlarm_type,IFC4X3_TC1_IfcController_type,IFC4X3_TC1_IfcFlowInstrument_type,IFC4X3_TC1_IfcProtectiveDeviceTrippingUnit_type,IFC4X3_TC1_IfcSensor_type,IFC4X3_TC1_IfcUnitaryControlElement_type
    });
    IFC4X3_TC1_IfcDistributionControlElementType_type->set_subtypes({
        IFC4X3_TC1_IfcActuatorType_type,IFC4X3_TC1_IfcAlarmType_type,IFC4X3_TC1_IfcControllerType_type,IFC4X3_TC1_IfcFlowInstrumentType_type,IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitType_type,IFC4X3_TC1_IfcSensorType_type,IFC4X3_TC1_IfcUnitaryControlElementType_type
    });
    IFC4X3_TC1_IfcManifoldSolidBrep_type->set_subtypes({
        IFC4X3_TC1_IfcAdvancedBrep_type,IFC4X3_TC1_IfcFacetedBrep_type
    });
    IFC4X3_TC1_IfcAdvancedBrep_type->set_subtypes({
        IFC4X3_TC1_IfcAdvancedBrepWithVoids_type
    });
    IFC4X3_TC1_IfcFaceSurface_type->set_subtypes({
        IFC4X3_TC1_IfcAdvancedFace_type
    });
    IFC4X3_TC1_IfcFlowTerminal_type->set_subtypes({
        IFC4X3_TC1_IfcAirTerminal_type,IFC4X3_TC1_IfcAudioVisualAppliance_type,IFC4X3_TC1_IfcCommunicationsAppliance_type,IFC4X3_TC1_IfcElectricAppliance_type,IFC4X3_TC1_IfcFireSuppressionTerminal_type,IFC4X3_TC1_IfcLamp_type,IFC4X3_TC1_IfcLightFixture_type,IFC4X3_TC1_IfcLiquidTerminal_type,IFC4X3_TC1_IfcMedicalDevice_type,IFC4X3_TC1_IfcMobileTelecommunicationsAppliance_type,IFC4X3_TC1_IfcOutlet_type,IFC4X3_TC1_IfcSanitaryTerminal_type,IFC4X3_TC1_IfcSignal_type,IFC4X3_TC1_IfcSpaceHeater_type,IFC4X3_TC1_IfcStackTerminal_type,IFC4X3_TC1_IfcWasteTerminal_type
    });
    IFC4X3_TC1_IfcFlowController_type->set_subtypes({
        IFC4X3_TC1_IfcAirTerminalBox_type,IFC4X3_TC1_IfcDamper_type,IFC4X3_TC1_IfcDistributionBoard_type,IFC4X3_TC1_IfcElectricDistributionBoard_type,IFC4X3_TC1_IfcElectricTimeControl_type,IFC4X3_TC1_IfcFlowMeter_type,IFC4X3_TC1_IfcProtectiveDevice_type,IFC4X3_TC1_IfcSwitchingDevice_type,IFC4X3_TC1_IfcValve_type
    });
    IFC4X3_TC1_IfcFlowControllerType_type->set_subtypes({
        IFC4X3_TC1_IfcAirTerminalBoxType_type,IFC4X3_TC1_IfcDamperType_type,IFC4X3_TC1_IfcDistributionBoardType_type,IFC4X3_TC1_IfcElectricDistributionBoardType_type,IFC4X3_TC1_IfcElectricTimeControlType_type,IFC4X3_TC1_IfcFlowMeterType_type,IFC4X3_TC1_IfcProtectiveDeviceType_type,IFC4X3_TC1_IfcSwitchingDeviceType_type,IFC4X3_TC1_IfcValveType_type
    });
    IFC4X3_TC1_IfcFlowTerminalType_type->set_subtypes({
        IFC4X3_TC1_IfcAirTerminalType_type,IFC4X3_TC1_IfcAudioVisualApplianceType_type,IFC4X3_TC1_IfcCommunicationsApplianceType_type,IFC4X3_TC1_IfcElectricApplianceType_type,IFC4X3_TC1_IfcFireSuppressionTerminalType_type,IFC4X3_TC1_IfcLampType_type,IFC4X3_TC1_IfcLightFixtureType_type,IFC4X3_TC1_IfcLiquidTerminalType_type,IFC4X3_TC1_IfcMedicalDeviceType_type,IFC4X3_TC1_IfcMobileTelecommunicationsApplianceType_type,IFC4X3_TC1_IfcOutletType_type,IFC4X3_TC1_IfcSanitaryTerminalType_type,IFC4X3_TC1_IfcSignalType_type,IFC4X3_TC1_IfcSpaceHeaterType_type,IFC4X3_TC1_IfcStackTerminalType_type,IFC4X3_TC1_IfcWasteTerminalType_type
    });
    IFC4X3_TC1_IfcEnergyConversionDevice_type->set_subtypes({
        IFC4X3_TC1_IfcAirToAirHeatRecovery_type,IFC4X3_TC1_IfcBoiler_type,IFC4X3_TC1_IfcBurner_type,IFC4X3_TC1_IfcChiller_type,IFC4X3_TC1_IfcCoil_type,IFC4X3_TC1_IfcCondenser_type,IFC4X3_TC1_IfcCooledBeam_type,IFC4X3_TC1_IfcCoolingTower_type,IFC4X3_TC1_IfcElectricGenerator_type,IFC4X3_TC1_IfcElectricMotor_type,IFC4X3_TC1_IfcEngine_type,IFC4X3_TC1_IfcEvaporativeCooler_type,IFC4X3_TC1_IfcEvaporator_type,IFC4X3_TC1_IfcHeatExchanger_type,IFC4X3_TC1_IfcHumidifier_type,IFC4X3_TC1_IfcMotorConnection_type,IFC4X3_TC1_IfcSolarDevice_type,IFC4X3_TC1_IfcTransformer_type,IFC4X3_TC1_IfcTubeBundle_type,IFC4X3_TC1_IfcUnitaryEquipment_type
    });
    IFC4X3_TC1_IfcEnergyConversionDeviceType_type->set_subtypes({
        IFC4X3_TC1_IfcAirToAirHeatRecoveryType_type,IFC4X3_TC1_IfcBoilerType_type,IFC4X3_TC1_IfcBurnerType_type,IFC4X3_TC1_IfcChillerType_type,IFC4X3_TC1_IfcCoilType_type,IFC4X3_TC1_IfcCondenserType_type,IFC4X3_TC1_IfcCooledBeamType_type,IFC4X3_TC1_IfcCoolingTowerType_type,IFC4X3_TC1_IfcElectricGeneratorType_type,IFC4X3_TC1_IfcElectricMotorType_type,IFC4X3_TC1_IfcEngineType_type,IFC4X3_TC1_IfcEvaporativeCoolerType_type,IFC4X3_TC1_IfcEvaporatorType_type,IFC4X3_TC1_IfcHeatExchangerType_type,IFC4X3_TC1_IfcHumidifierType_type,IFC4X3_TC1_IfcMotorConnectionType_type,IFC4X3_TC1_IfcSolarDeviceType_type,IFC4X3_TC1_IfcTransformerType_type,IFC4X3_TC1_IfcTubeBundleType_type,IFC4X3_TC1_IfcUnitaryEquipmentType_type
    });
    IFC4X3_TC1_IfcLinearPositioningElement_type->set_subtypes({
        IFC4X3_TC1_IfcAlignment_type
    });
    IFC4X3_TC1_IfcLinearElement_type->set_subtypes({
        IFC4X3_TC1_IfcAlignmentCant_type,IFC4X3_TC1_IfcAlignmentHorizontal_type,IFC4X3_TC1_IfcAlignmentSegment_type,IFC4X3_TC1_IfcAlignmentVertical_type
    });
    IFC4X3_TC1_IfcAlignmentParameterSegment_type->set_subtypes({
        IFC4X3_TC1_IfcAlignmentCantSegment_type,IFC4X3_TC1_IfcAlignmentHorizontalSegment_type,IFC4X3_TC1_IfcAlignmentVerticalSegment_type
    });
    IFC4X3_TC1_IfcProduct_type->set_subtypes({
        IFC4X3_TC1_IfcAnnotation_type,IFC4X3_TC1_IfcElement_type,IFC4X3_TC1_IfcLinearElement_type,IFC4X3_TC1_IfcPort_type,IFC4X3_TC1_IfcPositioningElement_type,IFC4X3_TC1_IfcSpatialElement_type,IFC4X3_TC1_IfcStructuralActivity_type,IFC4X3_TC1_IfcStructuralItem_type
    });
    IFC4X3_TC1_IfcGeometricRepresentationItem_type->set_subtypes({
        IFC4X3_TC1_IfcAnnotationFillArea_type,IFC4X3_TC1_IfcBooleanResult_type,IFC4X3_TC1_IfcBoundingBox_type,IFC4X3_TC1_IfcCartesianPointList_type,IFC4X3_TC1_IfcCartesianTransformationOperator_type,IFC4X3_TC1_IfcCsgPrimitive3D_type,IFC4X3_TC1_IfcCurve_type,IFC4X3_TC1_IfcDirection_type,IFC4X3_TC1_IfcFaceBasedSurfaceModel_type,IFC4X3_TC1_IfcFillAreaStyleHatching_type,IFC4X3_TC1_IfcFillAreaStyleTiles_type,IFC4X3_TC1_IfcGeometricSet_type,IFC4X3_TC1_IfcHalfSpaceSolid_type,IFC4X3_TC1_IfcLightSource_type,IFC4X3_TC1_IfcPlacement_type,IFC4X3_TC1_IfcPlanarExtent_type,IFC4X3_TC1_IfcPoint_type,IFC4X3_TC1_IfcSectionedSpine_type,IFC4X3_TC1_IfcSegment_type,IFC4X3_TC1_IfcShellBasedSurfaceModel_type,IFC4X3_TC1_IfcSolidModel_type,IFC4X3_TC1_IfcSurface_type,IFC4X3_TC1_IfcTessellatedItem_type,IFC4X3_TC1_IfcTextLiteral_type,IFC4X3_TC1_IfcVector_type
    });
    IFC4X3_TC1_IfcResourceLevelRelationship_type->set_subtypes({
        IFC4X3_TC1_IfcApprovalRelationship_type,IFC4X3_TC1_IfcCurrencyRelationship_type,IFC4X3_TC1_IfcDocumentInformationRelationship_type,IFC4X3_TC1_IfcExternalReferenceRelationship_type,IFC4X3_TC1_IfcMaterialRelationship_type,IFC4X3_TC1_IfcOrganizationRelationship_type,IFC4X3_TC1_IfcPropertyDependencyRelationship_type,IFC4X3_TC1_IfcResourceApprovalRelationship_type,IFC4X3_TC1_IfcResourceConstraintRelationship_type
    });
    IFC4X3_TC1_IfcProfileDef_type->set_subtypes({
        IFC4X3_TC1_IfcArbitraryClosedProfileDef_type,IFC4X3_TC1_IfcArbitraryOpenProfileDef_type,IFC4X3_TC1_IfcCompositeProfileDef_type,IFC4X3_TC1_IfcDerivedProfileDef_type,IFC4X3_TC1_IfcOpenCrossProfileDef_type,IFC4X3_TC1_IfcParameterizedProfileDef_type
    });
    IFC4X3_TC1_IfcArbitraryClosedProfileDef_type->set_subtypes({
        IFC4X3_TC1_IfcArbitraryProfileDefWithVoids_type
    });
    IFC4X3_TC1_IfcGroup_type->set_subtypes({
        IFC4X3_TC1_IfcAsset_type,IFC4X3_TC1_IfcInventory_type,IFC4X3_TC1_IfcStructuralLoadGroup_type,IFC4X3_TC1_IfcStructuralResultGroup_type,IFC4X3_TC1_IfcSystem_type
    });
    IFC4X3_TC1_IfcParameterizedProfileDef_type->set_subtypes({
        IFC4X3_TC1_IfcAsymmetricIShapeProfileDef_type,IFC4X3_TC1_IfcCShapeProfileDef_type,IFC4X3_TC1_IfcCircleProfileDef_type,IFC4X3_TC1_IfcEllipseProfileDef_type,IFC4X3_TC1_IfcIShapeProfileDef_type,IFC4X3_TC1_IfcLShapeProfileDef_type,IFC4X3_TC1_IfcRectangleProfileDef_type,IFC4X3_TC1_IfcTShapeProfileDef_type,IFC4X3_TC1_IfcTrapeziumProfileDef_type,IFC4X3_TC1_IfcUShapeProfileDef_type,IFC4X3_TC1_IfcZShapeProfileDef_type
    });
    IFC4X3_TC1_IfcPlacement_type->set_subtypes({
        IFC4X3_TC1_IfcAxis1Placement_type,IFC4X3_TC1_IfcAxis2Placement2D_type,IFC4X3_TC1_IfcAxis2Placement3D_type,IFC4X3_TC1_IfcAxis2PlacementLinear_type
    });
    IFC4X3_TC1_IfcBoundedCurve_type->set_subtypes({
        IFC4X3_TC1_IfcBSplineCurve_type,IFC4X3_TC1_IfcCompositeCurve_type,IFC4X3_TC1_IfcIndexedPolyCurve_type,IFC4X3_TC1_IfcPolyline_type,IFC4X3_TC1_IfcTrimmedCurve_type
    });
    IFC4X3_TC1_IfcBSplineCurve_type->set_subtypes({
        IFC4X3_TC1_IfcBSplineCurveWithKnots_type
    });
    IFC4X3_TC1_IfcBoundedSurface_type->set_subtypes({
        IFC4X3_TC1_IfcBSplineSurface_type,IFC4X3_TC1_IfcCurveBoundedPlane_type,IFC4X3_TC1_IfcCurveBoundedSurface_type,IFC4X3_TC1_IfcRectangularTrimmedSurface_type
    });
    IFC4X3_TC1_IfcBSplineSurface_type->set_subtypes({
        IFC4X3_TC1_IfcBSplineSurfaceWithKnots_type
    });
    IFC4X3_TC1_IfcBuiltElement_type->set_subtypes({
        IFC4X3_TC1_IfcBeam_type,IFC4X3_TC1_IfcBearing_type,IFC4X3_TC1_IfcBuildingElementProxy_type,IFC4X3_TC1_IfcChimney_type,IFC4X3_TC1_IfcColumn_type,IFC4X3_TC1_IfcCourse_type,IFC4X3_TC1_IfcCovering_type,IFC4X3_TC1_IfcCurtainWall_type,IFC4X3_TC1_IfcDeepFoundation_type,IFC4X3_TC1_IfcDoor_type,IFC4X3_TC1_IfcEarthworksElement_type,IFC4X3_TC1_IfcFooting_type,IFC4X3_TC1_IfcKerb_type,IFC4X3_TC1_IfcMember_type,IFC4X3_TC1_IfcMooringDevice_type,IFC4X3_TC1_IfcNavigationElement_type,IFC4X3_TC1_IfcPavement_type,IFC4X3_TC1_IfcPlate_type,IFC4X3_TC1_IfcRail_type,IFC4X3_TC1_IfcRailing_type,IFC4X3_TC1_IfcRamp_type,IFC4X3_TC1_IfcRampFlight_type,IFC4X3_TC1_IfcRoof_type,IFC4X3_TC1_IfcShadingDevice_type,IFC4X3_TC1_IfcSlab_type,IFC4X3_TC1_IfcStair_type,IFC4X3_TC1_IfcStairFlight_type,IFC4X3_TC1_IfcTrackElement_type,IFC4X3_TC1_IfcWall_type,IFC4X3_TC1_IfcWindow_type
    });
    IFC4X3_TC1_IfcBuiltElementType_type->set_subtypes({
        IFC4X3_TC1_IfcBeamType_type,IFC4X3_TC1_IfcBearingType_type,IFC4X3_TC1_IfcBuildingElementProxyType_type,IFC4X3_TC1_IfcChimneyType_type,IFC4X3_TC1_IfcColumnType_type,IFC4X3_TC1_IfcCourseType_type,IFC4X3_TC1_IfcCoveringType_type,IFC4X3_TC1_IfcCurtainWallType_type,IFC4X3_TC1_IfcDeepFoundationType_type,IFC4X3_TC1_IfcDoorType_type,IFC4X3_TC1_IfcFootingType_type,IFC4X3_TC1_IfcKerbType_type,IFC4X3_TC1_IfcMemberType_type,IFC4X3_TC1_IfcMooringDeviceType_type,IFC4X3_TC1_IfcNavigationElementType_type,IFC4X3_TC1_IfcPavementType_type,IFC4X3_TC1_IfcPlateType_type,IFC4X3_TC1_IfcRailType_type,IFC4X3_TC1_IfcRailingType_type,IFC4X3_TC1_IfcRampFlightType_type,IFC4X3_TC1_IfcRampType_type,IFC4X3_TC1_IfcRoofType_type,IFC4X3_TC1_IfcShadingDeviceType_type,IFC4X3_TC1_IfcSlabType_type,IFC4X3_TC1_IfcStairFlightType_type,IFC4X3_TC1_IfcStairType_type,IFC4X3_TC1_IfcTrackElementType_type,IFC4X3_TC1_IfcWallType_type,IFC4X3_TC1_IfcWindowType_type
    });
    IFC4X3_TC1_IfcSurfaceTexture_type->set_subtypes({
        IFC4X3_TC1_IfcBlobTexture_type,IFC4X3_TC1_IfcImageTexture_type,IFC4X3_TC1_IfcPixelTexture_type
    });
    IFC4X3_TC1_IfcCsgPrimitive3D_type->set_subtypes({
        IFC4X3_TC1_IfcBlock_type,IFC4X3_TC1_IfcRectangularPyramid_type,IFC4X3_TC1_IfcRightCircularCone_type,IFC4X3_TC1_IfcRightCircularCylinder_type,IFC4X3_TC1_IfcSphere_type
    });
    IFC4X3_TC1_IfcBooleanResult_type->set_subtypes({
        IFC4X3_TC1_IfcBooleanClippingResult_type
    });
    IFC4X3_TC1_IfcGeotechnicalAssembly_type->set_subtypes({
        IFC4X3_TC1_IfcBorehole_type,IFC4X3_TC1_IfcGeomodel_type,IFC4X3_TC1_IfcGeoslice_type
    });
    IFC4X3_TC1_IfcCompositeCurveOnSurface_type->set_subtypes({
        IFC4X3_TC1_IfcBoundaryCurve_type
    });
    IFC4X3_TC1_IfcBoundaryCondition_type->set_subtypes({
        IFC4X3_TC1_IfcBoundaryEdgeCondition_type,IFC4X3_TC1_IfcBoundaryFaceCondition_type,IFC4X3_TC1_IfcBoundaryNodeCondition_type
    });
    IFC4X3_TC1_IfcBoundaryNodeCondition_type->set_subtypes({
        IFC4X3_TC1_IfcBoundaryNodeConditionWarping_type
    });
    IFC4X3_TC1_IfcCurve_type->set_subtypes({
        IFC4X3_TC1_IfcBoundedCurve_type,IFC4X3_TC1_IfcConic_type,IFC4X3_TC1_IfcLine_type,IFC4X3_TC1_IfcOffsetCurve_type,IFC4X3_TC1_IfcPcurve_type,IFC4X3_TC1_IfcPolynomialCurve_type,IFC4X3_TC1_IfcSpiral_type,IFC4X3_TC1_IfcSurfaceCurve_type
    });
    IFC4X3_TC1_IfcSurface_type->set_subtypes({
        IFC4X3_TC1_IfcBoundedSurface_type,IFC4X3_TC1_IfcElementarySurface_type,IFC4X3_TC1_IfcSectionedSurface_type,IFC4X3_TC1_IfcSweptSurface_type
    });
    IFC4X3_TC1_IfcHalfSpaceSolid_type->set_subtypes({
        IFC4X3_TC1_IfcBoxedHalfSpace_type,IFC4X3_TC1_IfcPolygonalBoundedHalfSpace_type
    });
    IFC4X3_TC1_IfcFacility_type->set_subtypes({
        IFC4X3_TC1_IfcBridge_type,IFC4X3_TC1_IfcBuilding_type,IFC4X3_TC1_IfcMarineFacility_type,IFC4X3_TC1_IfcRailway_type,IFC4X3_TC1_IfcRoad_type
    });
    IFC4X3_TC1_IfcFacilityPart_type->set_subtypes({
        IFC4X3_TC1_IfcBridgePart_type,IFC4X3_TC1_IfcFacilityPartCommon_type,IFC4X3_TC1_IfcMarinePart_type,IFC4X3_TC1_IfcRailwayPart_type,IFC4X3_TC1_IfcRoadPart_type
    });
    IFC4X3_TC1_IfcElementComponent_type->set_subtypes({
        IFC4X3_TC1_IfcBuildingElementPart_type,IFC4X3_TC1_IfcDiscreteAccessory_type,IFC4X3_TC1_IfcFastener_type,IFC4X3_TC1_IfcImpactProtectionDevice_type,IFC4X3_TC1_IfcMechanicalFastener_type,IFC4X3_TC1_IfcReinforcingElement_type,IFC4X3_TC1_IfcSign_type,IFC4X3_TC1_IfcVibrationDamper_type,IFC4X3_TC1_IfcVibrationIsolator_type
    });
    IFC4X3_TC1_IfcElementComponentType_type->set_subtypes({
        IFC4X3_TC1_IfcBuildingElementPartType_type,IFC4X3_TC1_IfcDiscreteAccessoryType_type,IFC4X3_TC1_IfcFastenerType_type,IFC4X3_TC1_IfcImpactProtectionDeviceType_type,IFC4X3_TC1_IfcMechanicalFastenerType_type,IFC4X3_TC1_IfcReinforcingElementType_type,IFC4X3_TC1_IfcSignType_type,IFC4X3_TC1_IfcVibrationDamperType_type,IFC4X3_TC1_IfcVibrationIsolatorType_type
    });
    IFC4X3_TC1_IfcSpatialStructureElement_type->set_subtypes({
        IFC4X3_TC1_IfcBuildingStorey_type,IFC4X3_TC1_IfcFacility_type,IFC4X3_TC1_IfcFacilityPart_type,IFC4X3_TC1_IfcSite_type,IFC4X3_TC1_IfcSpace_type
    });
    IFC4X3_TC1_IfcSystem_type->set_subtypes({
        IFC4X3_TC1_IfcBuildingSystem_type,IFC4X3_TC1_IfcBuiltSystem_type,IFC4X3_TC1_IfcDistributionSystem_type,IFC4X3_TC1_IfcStructuralAnalysisModel_type,IFC4X3_TC1_IfcZone_type
    });
    IFC4X3_TC1_IfcElement_type->set_subtypes({
        IFC4X3_TC1_IfcBuiltElement_type,IFC4X3_TC1_IfcCivilElement_type,IFC4X3_TC1_IfcDistributionElement_type,IFC4X3_TC1_IfcElementAssembly_type,IFC4X3_TC1_IfcElementComponent_type,IFC4X3_TC1_IfcFeatureElement_type,IFC4X3_TC1_IfcFurnishingElement_type,IFC4X3_TC1_IfcGeographicElement_type,IFC4X3_TC1_IfcGeotechnicalElement_type,IFC4X3_TC1_IfcTransportationDevice_type,IFC4X3_TC1_IfcVirtualElement_type
    });
    IFC4X3_TC1_IfcElementType_type->set_subtypes({
        IFC4X3_TC1_IfcBuiltElementType_type,IFC4X3_TC1_IfcCivilElementType_type,IFC4X3_TC1_IfcDistributionElementType_type,IFC4X3_TC1_IfcElementAssemblyType_type,IFC4X3_TC1_IfcElementComponentType_type,IFC4X3_TC1_IfcFurnishingElementType_type,IFC4X3_TC1_IfcGeographicElementType_type,IFC4X3_TC1_IfcTransportationDeviceType_type
    });
    IFC4X3_TC1_IfcFlowFitting_type->set_subtypes({
        IFC4X3_TC1_IfcCableCarrierFitting_type,IFC4X3_TC1_IfcCableFitting_type,IFC4X3_TC1_IfcDuctFitting_type,IFC4X3_TC1_IfcJunctionBox_type,IFC4X3_TC1_IfcPipeFitting_type
    });
    IFC4X3_TC1_IfcFlowFittingType_type->set_subtypes({
        IFC4X3_TC1_IfcCableCarrierFittingType_type,IFC4X3_TC1_IfcCableFittingType_type,IFC4X3_TC1_IfcDuctFittingType_type,IFC4X3_TC1_IfcJunctionBoxType_type,IFC4X3_TC1_IfcPipeFittingType_type
    });
    IFC4X3_TC1_IfcFlowSegment_type->set_subtypes({
        IFC4X3_TC1_IfcCableCarrierSegment_type,IFC4X3_TC1_IfcCableSegment_type,IFC4X3_TC1_IfcConveyorSegment_type,IFC4X3_TC1_IfcDuctSegment_type,IFC4X3_TC1_IfcPipeSegment_type
    });
    IFC4X3_TC1_IfcFlowSegmentType_type->set_subtypes({
        IFC4X3_TC1_IfcCableCarrierSegmentType_type,IFC4X3_TC1_IfcCableSegmentType_type,IFC4X3_TC1_IfcConveyorSegmentType_type,IFC4X3_TC1_IfcDuctSegmentType_type,IFC4X3_TC1_IfcPipeSegmentType_type
    });
    IFC4X3_TC1_IfcDeepFoundation_type->set_subtypes({
        IFC4X3_TC1_IfcCaissonFoundation_type,IFC4X3_TC1_IfcPile_type
    });
    IFC4X3_TC1_IfcDeepFoundationType_type->set_subtypes({
        IFC4X3_TC1_IfcCaissonFoundationType_type,IFC4X3_TC1_IfcPileType_type
    });
    IFC4X3_TC1_IfcPoint_type->set_subtypes({
        IFC4X3_TC1_IfcCartesianPoint_type,IFC4X3_TC1_IfcPointByDistanceExpression_type,IFC4X3_TC1_IfcPointOnCurve_type,IFC4X3_TC1_IfcPointOnSurface_type
    });
    IFC4X3_TC1_IfcCartesianPointList_type->set_subtypes({
        IFC4X3_TC1_IfcCartesianPointList2D_type,IFC4X3_TC1_IfcCartesianPointList3D_type
    });
    IFC4X3_TC1_IfcCartesianTransformationOperator_type->set_subtypes({
        IFC4X3_TC1_IfcCartesianTransformationOperator2D_type,IFC4X3_TC1_IfcCartesianTransformationOperator3D_type
    });
    IFC4X3_TC1_IfcCartesianTransformationOperator2D_type->set_subtypes({
        IFC4X3_TC1_IfcCartesianTransformationOperator2DnonUniform_type
    });
    IFC4X3_TC1_IfcCartesianTransformationOperator3D_type->set_subtypes({
        IFC4X3_TC1_IfcCartesianTransformationOperator3DnonUniform_type
    });
    IFC4X3_TC1_IfcArbitraryOpenProfileDef_type->set_subtypes({
        IFC4X3_TC1_IfcCenterLineProfileDef_type
    });
    IFC4X3_TC1_IfcConic_type->set_subtypes({
        IFC4X3_TC1_IfcCircle_type,IFC4X3_TC1_IfcEllipse_type
    });
    IFC4X3_TC1_IfcCircleProfileDef_type->set_subtypes({
        IFC4X3_TC1_IfcCircleHollowProfileDef_type
    });
    IFC4X3_TC1_IfcExternalInformation_type->set_subtypes({
        IFC4X3_TC1_IfcClassification_type,IFC4X3_TC1_IfcDocumentInformation_type,IFC4X3_TC1_IfcLibraryInformation_type
    });
    IFC4X3_TC1_IfcExternalReference_type->set_subtypes({
        IFC4X3_TC1_IfcClassificationReference_type,IFC4X3_TC1_IfcDocumentReference_type,IFC4X3_TC1_IfcExternallyDefinedHatchStyle_type,IFC4X3_TC1_IfcExternallyDefinedSurfaceStyle_type,IFC4X3_TC1_IfcExternallyDefinedTextFont_type,IFC4X3_TC1_IfcLibraryReference_type
    });
    IFC4X3_TC1_IfcConnectedFaceSet_type->set_subtypes({
        IFC4X3_TC1_IfcClosedShell_type,IFC4X3_TC1_IfcOpenShell_type
    });
    IFC4X3_TC1_IfcSpiral_type->set_subtypes({
        IFC4X3_TC1_IfcClothoid_type,IFC4X3_TC1_IfcCosineSpiral_type,IFC4X3_TC1_IfcSecondOrderPolynomialSpiral_type,IFC4X3_TC1_IfcSeventhOrderPolynomialSpiral_type,IFC4X3_TC1_IfcSineSpiral_type,IFC4X3_TC1_IfcThirdOrderPolynomialSpiral_type
    });
    IFC4X3_TC1_IfcColourSpecification_type->set_subtypes({
        IFC4X3_TC1_IfcColourRgb_type
    });
    IFC4X3_TC1_IfcPresentationItem_type->set_subtypes({
        IFC4X3_TC1_IfcColourRgbList_type,IFC4X3_TC1_IfcColourSpecification_type,IFC4X3_TC1_IfcCurveStyleFont_type,IFC4X3_TC1_IfcCurveStyleFontAndScaling_type,IFC4X3_TC1_IfcCurveStyleFontPattern_type,IFC4X3_TC1_IfcIndexedColourMap_type,IFC4X3_TC1_IfcPreDefinedItem_type,IFC4X3_TC1_IfcSurfaceStyleLighting_type,IFC4X3_TC1_IfcSurfaceStyleRefraction_type,IFC4X3_TC1_IfcSurfaceStyleShading_type,IFC4X3_TC1_IfcSurfaceStyleWithTextures_type,IFC4X3_TC1_IfcSurfaceTexture_type,IFC4X3_TC1_IfcTextStyleForDefinedFont_type,IFC4X3_TC1_IfcTextStyleTextModel_type,IFC4X3_TC1_IfcTextureCoordinate_type,IFC4X3_TC1_IfcTextureVertex_type,IFC4X3_TC1_IfcTextureVertexList_type
    });
    IFC4X3_TC1_IfcProperty_type->set_subtypes({
        IFC4X3_TC1_IfcComplexProperty_type,IFC4X3_TC1_IfcSimpleProperty_type
    });
    IFC4X3_TC1_IfcPropertyTemplate_type->set_subtypes({
        IFC4X3_TC1_IfcComplexPropertyTemplate_type,IFC4X3_TC1_IfcSimplePropertyTemplate_type
    });
    IFC4X3_TC1_IfcCompositeCurve_type->set_subtypes({
        IFC4X3_TC1_IfcCompositeCurveOnSurface_type,IFC4X3_TC1_IfcGradientCurve_type,IFC4X3_TC1_IfcSegmentedReferenceCurve_type
    });
    IFC4X3_TC1_IfcSegment_type->set_subtypes({
        IFC4X3_TC1_IfcCompositeCurveSegment_type,IFC4X3_TC1_IfcCurveSegment_type
    });
    IFC4X3_TC1_IfcFlowMovingDevice_type->set_subtypes({
        IFC4X3_TC1_IfcCompressor_type,IFC4X3_TC1_IfcFan_type,IFC4X3_TC1_IfcPump_type
    });
    IFC4X3_TC1_IfcFlowMovingDeviceType_type->set_subtypes({
        IFC4X3_TC1_IfcCompressorType_type,IFC4X3_TC1_IfcFanType_type,IFC4X3_TC1_IfcPumpType_type
    });
    IFC4X3_TC1_IfcTopologicalRepresentationItem_type->set_subtypes({
        IFC4X3_TC1_IfcConnectedFaceSet_type,IFC4X3_TC1_IfcEdge_type,IFC4X3_TC1_IfcFace_type,IFC4X3_TC1_IfcFaceBound_type,IFC4X3_TC1_IfcLoop_type,IFC4X3_TC1_IfcPath_type,IFC4X3_TC1_IfcVertex_type
    });
    IFC4X3_TC1_IfcConnectionGeometry_type->set_subtypes({
        IFC4X3_TC1_IfcConnectionCurveGeometry_type,IFC4X3_TC1_IfcConnectionPointGeometry_type,IFC4X3_TC1_IfcConnectionSurfaceGeometry_type,IFC4X3_TC1_IfcConnectionVolumeGeometry_type
    });
    IFC4X3_TC1_IfcConnectionPointGeometry_type->set_subtypes({
        IFC4X3_TC1_IfcConnectionPointEccentricity_type
    });
    IFC4X3_TC1_IfcConstructionResource_type->set_subtypes({
        IFC4X3_TC1_IfcConstructionEquipmentResource_type,IFC4X3_TC1_IfcConstructionMaterialResource_type,IFC4X3_TC1_IfcConstructionProductResource_type,IFC4X3_TC1_IfcCrewResource_type,IFC4X3_TC1_IfcLaborResource_type,IFC4X3_TC1_IfcSubContractResource_type
    });
    IFC4X3_TC1_IfcConstructionResourceType_type->set_subtypes({
        IFC4X3_TC1_IfcConstructionEquipmentResourceType_type,IFC4X3_TC1_IfcConstructionMaterialResourceType_type,IFC4X3_TC1_IfcConstructionProductResourceType_type,IFC4X3_TC1_IfcCrewResourceType_type,IFC4X3_TC1_IfcLaborResourceType_type,IFC4X3_TC1_IfcSubContractResourceType_type
    });
    IFC4X3_TC1_IfcResource_type->set_subtypes({
        IFC4X3_TC1_IfcConstructionResource_type
    });
    IFC4X3_TC1_IfcTypeResource_type->set_subtypes({
        IFC4X3_TC1_IfcConstructionResourceType_type
    });
    IFC4X3_TC1_IfcObjectDefinition_type->set_subtypes({
        IFC4X3_TC1_IfcContext_type,IFC4X3_TC1_IfcObject_type,IFC4X3_TC1_IfcTypeObject_type
    });
    IFC4X3_TC1_IfcNamedUnit_type->set_subtypes({
        IFC4X3_TC1_IfcContextDependentUnit_type,IFC4X3_TC1_IfcConversionBasedUnit_type,IFC4X3_TC1_IfcSIUnit_type
    });
    IFC4X3_TC1_IfcConversionBasedUnit_type->set_subtypes({
        IFC4X3_TC1_IfcConversionBasedUnitWithOffset_type
    });
    IFC4X3_TC1_IfcAppliedValue_type->set_subtypes({
        IFC4X3_TC1_IfcCostValue_type
    });
    IFC4X3_TC1_IfcSolidModel_type->set_subtypes({
        IFC4X3_TC1_IfcCsgSolid_type,IFC4X3_TC1_IfcManifoldSolidBrep_type,IFC4X3_TC1_IfcSectionedSolid_type,IFC4X3_TC1_IfcSweptAreaSolid_type,IFC4X3_TC1_IfcSweptDiskSolid_type
    });
    IFC4X3_TC1_IfcPresentationStyle_type->set_subtypes({
        IFC4X3_TC1_IfcCurveStyle_type,IFC4X3_TC1_IfcFillAreaStyle_type,IFC4X3_TC1_IfcSurfaceStyle_type,IFC4X3_TC1_IfcTextStyle_type
    });
    IFC4X3_TC1_IfcElementarySurface_type->set_subtypes({
        IFC4X3_TC1_IfcCylindricalSurface_type,IFC4X3_TC1_IfcPlane_type,IFC4X3_TC1_IfcSphericalSurface_type,IFC4X3_TC1_IfcToroidalSurface_type
    });
    IFC4X3_TC1_IfcSweptAreaSolid_type->set_subtypes({
        IFC4X3_TC1_IfcDirectrixCurveSweptAreaSolid_type,IFC4X3_TC1_IfcExtrudedAreaSolid_type,IFC4X3_TC1_IfcRevolvedAreaSolid_type
    });
    IFC4X3_TC1_IfcFixedReferenceSweptAreaSolid_type->set_subtypes({
        IFC4X3_TC1_IfcDirectrixDerivedReferenceSweptAreaSolid_type
    });
    IFC4X3_TC1_IfcDistributionFlowElement_type->set_subtypes({
        IFC4X3_TC1_IfcDistributionChamberElement_type,IFC4X3_TC1_IfcEnergyConversionDevice_type,IFC4X3_TC1_IfcFlowController_type,IFC4X3_TC1_IfcFlowFitting_type,IFC4X3_TC1_IfcFlowMovingDevice_type,IFC4X3_TC1_IfcFlowSegment_type,IFC4X3_TC1_IfcFlowStorageDevice_type,IFC4X3_TC1_IfcFlowTerminal_type,IFC4X3_TC1_IfcFlowTreatmentDevice_type
    });
    IFC4X3_TC1_IfcDistributionFlowElementType_type->set_subtypes({
        IFC4X3_TC1_IfcDistributionChamberElementType_type,IFC4X3_TC1_IfcEnergyConversionDeviceType_type,IFC4X3_TC1_IfcFlowControllerType_type,IFC4X3_TC1_IfcFlowFittingType_type,IFC4X3_TC1_IfcFlowMovingDeviceType_type,IFC4X3_TC1_IfcFlowSegmentType_type,IFC4X3_TC1_IfcFlowStorageDeviceType_type,IFC4X3_TC1_IfcFlowTerminalType_type,IFC4X3_TC1_IfcFlowTreatmentDeviceType_type
    });
    IFC4X3_TC1_IfcDistributionSystem_type->set_subtypes({
        IFC4X3_TC1_IfcDistributionCircuit_type
    });
    IFC4X3_TC1_IfcDistributionElement_type->set_subtypes({
        IFC4X3_TC1_IfcDistributionControlElement_type,IFC4X3_TC1_IfcDistributionFlowElement_type
    });
    IFC4X3_TC1_IfcDistributionElementType_type->set_subtypes({
        IFC4X3_TC1_IfcDistributionControlElementType_type,IFC4X3_TC1_IfcDistributionFlowElementType_type
    });
    IFC4X3_TC1_IfcPort_type->set_subtypes({
        IFC4X3_TC1_IfcDistributionPort_type
    });
    IFC4X3_TC1_IfcPreDefinedPropertySet_type->set_subtypes({
        IFC4X3_TC1_IfcDoorLiningProperties_type,IFC4X3_TC1_IfcDoorPanelProperties_type,IFC4X3_TC1_IfcPermeableCoveringProperties_type,IFC4X3_TC1_IfcReinforcementDefinitionProperties_type,IFC4X3_TC1_IfcWindowLiningProperties_type,IFC4X3_TC1_IfcWindowPanelProperties_type
    });
    IFC4X3_TC1_IfcPreDefinedColour_type->set_subtypes({
        IFC4X3_TC1_IfcDraughtingPreDefinedColour_type
    });
    IFC4X3_TC1_IfcPreDefinedCurveFont_type->set_subtypes({
        IFC4X3_TC1_IfcDraughtingPreDefinedCurveFont_type
    });
    IFC4X3_TC1_IfcFlowTreatmentDevice_type->set_subtypes({
        IFC4X3_TC1_IfcDuctSilencer_type,IFC4X3_TC1_IfcElectricFlowTreatmentDevice_type,IFC4X3_TC1_IfcFilter_type,IFC4X3_TC1_IfcInterceptor_type
    });
    IFC4X3_TC1_IfcFlowTreatmentDeviceType_type->set_subtypes({
        IFC4X3_TC1_IfcDuctSilencerType_type,IFC4X3_TC1_IfcElectricFlowTreatmentDeviceType_type,IFC4X3_TC1_IfcFilterType_type,IFC4X3_TC1_IfcInterceptorType_type
    });
    IFC4X3_TC1_IfcFeatureElementSubtraction_type->set_subtypes({
        IFC4X3_TC1_IfcEarthworksCut_type,IFC4X3_TC1_IfcOpeningElement_type,IFC4X3_TC1_IfcVoidingFeature_type
    });
    IFC4X3_TC1_IfcEarthworksElement_type->set_subtypes({
        IFC4X3_TC1_IfcEarthworksFill_type,IFC4X3_TC1_IfcReinforcedSoil_type
    });
    IFC4X3_TC1_IfcEdge_type->set_subtypes({
        IFC4X3_TC1_IfcEdgeCurve_type,IFC4X3_TC1_IfcOrientedEdge_type,IFC4X3_TC1_IfcSubedge_type
    });
    IFC4X3_TC1_IfcLoop_type->set_subtypes({
        IFC4X3_TC1_IfcEdgeLoop_type,IFC4X3_TC1_IfcPolyLoop_type,IFC4X3_TC1_IfcVertexLoop_type
    });
    IFC4X3_TC1_IfcFlowStorageDevice_type->set_subtypes({
        IFC4X3_TC1_IfcElectricFlowStorageDevice_type,IFC4X3_TC1_IfcTank_type
    });
    IFC4X3_TC1_IfcFlowStorageDeviceType_type->set_subtypes({
        IFC4X3_TC1_IfcElectricFlowStorageDeviceType_type,IFC4X3_TC1_IfcTankType_type
    });
    IFC4X3_TC1_IfcQuantitySet_type->set_subtypes({
        IFC4X3_TC1_IfcElementQuantity_type
    });
    IFC4X3_TC1_IfcTypeProduct_type->set_subtypes({
        IFC4X3_TC1_IfcElementType_type,IFC4X3_TC1_IfcSpatialElementType_type
    });
    IFC4X3_TC1_IfcProcess_type->set_subtypes({
        IFC4X3_TC1_IfcEvent_type,IFC4X3_TC1_IfcProcedure_type,IFC4X3_TC1_IfcTask_type
    });
    IFC4X3_TC1_IfcSchedulingTime_type->set_subtypes({
        IFC4X3_TC1_IfcEventTime_type,IFC4X3_TC1_IfcLagTime_type,IFC4X3_TC1_IfcResourceTime_type,IFC4X3_TC1_IfcTaskTime_type,IFC4X3_TC1_IfcWorkTime_type
    });
    IFC4X3_TC1_IfcTypeProcess_type->set_subtypes({
        IFC4X3_TC1_IfcEventType_type,IFC4X3_TC1_IfcProcedureType_type,IFC4X3_TC1_IfcTaskType_type
    });
    IFC4X3_TC1_IfcPropertyAbstraction_type->set_subtypes({
        IFC4X3_TC1_IfcExtendedProperties_type,IFC4X3_TC1_IfcPreDefinedProperties_type,IFC4X3_TC1_IfcProperty_type,IFC4X3_TC1_IfcPropertyEnumeration_type
    });
    IFC4X3_TC1_IfcExternalSpatialStructureElement_type->set_subtypes({
        IFC4X3_TC1_IfcExternalSpatialElement_type
    });
    IFC4X3_TC1_IfcSpatialElement_type->set_subtypes({
        IFC4X3_TC1_IfcExternalSpatialStructureElement_type,IFC4X3_TC1_IfcSpatialStructureElement_type,IFC4X3_TC1_IfcSpatialZone_type
    });
    IFC4X3_TC1_IfcExtrudedAreaSolid_type->set_subtypes({
        IFC4X3_TC1_IfcExtrudedAreaSolidTapered_type
    });
    IFC4X3_TC1_IfcFaceBound_type->set_subtypes({
        IFC4X3_TC1_IfcFaceOuterBound_type
    });
    IFC4X3_TC1_IfcFace_type->set_subtypes({
        IFC4X3_TC1_IfcFaceSurface_type
    });
    IFC4X3_TC1_IfcFacetedBrep_type->set_subtypes({
        IFC4X3_TC1_IfcFacetedBrepWithVoids_type
    });
    IFC4X3_TC1_IfcStructuralConnectionCondition_type->set_subtypes({
        IFC4X3_TC1_IfcFailureConnectionCondition_type,IFC4X3_TC1_IfcSlippageConnectionCondition_type
    });
    IFC4X3_TC1_IfcFeatureElement_type->set_subtypes({
        IFC4X3_TC1_IfcFeatureElementAddition_type,IFC4X3_TC1_IfcFeatureElementSubtraction_type,IFC4X3_TC1_IfcSurfaceFeature_type
    });
    IFC4X3_TC1_IfcDirectrixCurveSweptAreaSolid_type->set_subtypes({
        IFC4X3_TC1_IfcFixedReferenceSweptAreaSolid_type,IFC4X3_TC1_IfcSurfaceCurveSweptAreaSolid_type
    });
    IFC4X3_TC1_IfcFurnishingElement_type->set_subtypes({
        IFC4X3_TC1_IfcFurniture_type,IFC4X3_TC1_IfcSystemFurnitureElement_type
    });
    IFC4X3_TC1_IfcFurnishingElementType_type->set_subtypes({
        IFC4X3_TC1_IfcFurnitureType_type,IFC4X3_TC1_IfcSystemFurnitureElementType_type
    });
    IFC4X3_TC1_IfcGeometricSet_type->set_subtypes({
        IFC4X3_TC1_IfcGeometricCurveSet_type
    });
    IFC4X3_TC1_IfcRepresentationContext_type->set_subtypes({
        IFC4X3_TC1_IfcGeometricRepresentationContext_type
    });
    IFC4X3_TC1_IfcRepresentationItem_type->set_subtypes({
        IFC4X3_TC1_IfcGeometricRepresentationItem_type,IFC4X3_TC1_IfcMappedItem_type,IFC4X3_TC1_IfcStyledItem_type,IFC4X3_TC1_IfcTopologicalRepresentationItem_type
    });
    IFC4X3_TC1_IfcGeometricRepresentationContext_type->set_subtypes({
        IFC4X3_TC1_IfcGeometricRepresentationSubContext_type
    });
    IFC4X3_TC1_IfcGeotechnicalElement_type->set_subtypes({
        IFC4X3_TC1_IfcGeotechnicalAssembly_type,IFC4X3_TC1_IfcGeotechnicalStratum_type
    });
    IFC4X3_TC1_IfcPositioningElement_type->set_subtypes({
        IFC4X3_TC1_IfcGrid_type,IFC4X3_TC1_IfcLinearPositioningElement_type,IFC4X3_TC1_IfcReferent_type
    });
    IFC4X3_TC1_IfcObjectPlacement_type->set_subtypes({
        IFC4X3_TC1_IfcGridPlacement_type,IFC4X3_TC1_IfcLinearPlacement_type,IFC4X3_TC1_IfcLocalPlacement_type
    });
    IFC4X3_TC1_IfcTessellatedItem_type->set_subtypes({
        IFC4X3_TC1_IfcIndexedPolygonalFace_type,IFC4X3_TC1_IfcTessellatedFaceSet_type
    });
    IFC4X3_TC1_IfcIndexedPolygonalFace_type->set_subtypes({
        IFC4X3_TC1_IfcIndexedPolygonalFaceWithVoids_type
    });
    IFC4X3_TC1_IfcIndexedTextureMap_type->set_subtypes({
        IFC4X3_TC1_IfcIndexedPolygonalTextureMap_type,IFC4X3_TC1_IfcIndexedTriangleTextureMap_type
    });
    IFC4X3_TC1_IfcTextureCoordinate_type->set_subtypes({
        IFC4X3_TC1_IfcIndexedTextureMap_type,IFC4X3_TC1_IfcTextureCoordinateGenerator_type,IFC4X3_TC1_IfcTextureMap_type
    });
    IFC4X3_TC1_IfcSurfaceCurve_type->set_subtypes({
        IFC4X3_TC1_IfcIntersectionCurve_type,IFC4X3_TC1_IfcSeamCurve_type
    });
    IFC4X3_TC1_IfcTimeSeries_type->set_subtypes({
        IFC4X3_TC1_IfcIrregularTimeSeries_type,IFC4X3_TC1_IfcRegularTimeSeries_type
    });
    IFC4X3_TC1_IfcLightSource_type->set_subtypes({
        IFC4X3_TC1_IfcLightSourceAmbient_type,IFC4X3_TC1_IfcLightSourceDirectional_type,IFC4X3_TC1_IfcLightSourceGoniometric_type,IFC4X3_TC1_IfcLightSourcePositional_type
    });
    IFC4X3_TC1_IfcLightSourcePositional_type->set_subtypes({
        IFC4X3_TC1_IfcLightSourceSpot_type
    });
    IFC4X3_TC1_IfcCoordinateOperation_type->set_subtypes({
        IFC4X3_TC1_IfcMapConversion_type
    });
    IFC4X3_TC1_IfcMaterialDefinition_type->set_subtypes({
        IFC4X3_TC1_IfcMaterial_type,IFC4X3_TC1_IfcMaterialConstituent_type,IFC4X3_TC1_IfcMaterialConstituentSet_type,IFC4X3_TC1_IfcMaterialLayer_type,IFC4X3_TC1_IfcMaterialLayerSet_type,IFC4X3_TC1_IfcMaterialProfile_type,IFC4X3_TC1_IfcMaterialProfileSet_type
    });
    IFC4X3_TC1_IfcProductRepresentation_type->set_subtypes({
        IFC4X3_TC1_IfcMaterialDefinitionRepresentation_type,IFC4X3_TC1_IfcProductDefinitionShape_type
    });
    IFC4X3_TC1_IfcMaterialUsageDefinition_type->set_subtypes({
        IFC4X3_TC1_IfcMaterialLayerSetUsage_type,IFC4X3_TC1_IfcMaterialProfileSetUsage_type
    });
    IFC4X3_TC1_IfcMaterialLayer_type->set_subtypes({
        IFC4X3_TC1_IfcMaterialLayerWithOffsets_type
    });
    IFC4X3_TC1_IfcMaterialProfileSetUsage_type->set_subtypes({
        IFC4X3_TC1_IfcMaterialProfileSetUsageTapering_type
    });
    IFC4X3_TC1_IfcMaterialProfile_type->set_subtypes({
        IFC4X3_TC1_IfcMaterialProfileWithOffsets_type
    });
    IFC4X3_TC1_IfcExtendedProperties_type->set_subtypes({
        IFC4X3_TC1_IfcMaterialProperties_type,IFC4X3_TC1_IfcProfileProperties_type
    });
    IFC4X3_TC1_IfcConstraint_type->set_subtypes({
        IFC4X3_TC1_IfcMetric_type,IFC4X3_TC1_IfcObjective_type
    });
    IFC4X3_TC1_IfcDerivedProfileDef_type->set_subtypes({
        IFC4X3_TC1_IfcMirroredProfileDef_type
    });
    IFC4X3_TC1_IfcRoot_type->set_subtypes({
        IFC4X3_TC1_IfcObjectDefinition_type,IFC4X3_TC1_IfcPropertyDefinition_type,IFC4X3_TC1_IfcRelationship_type
    });
    IFC4X3_TC1_IfcActor_type->set_subtypes({
        IFC4X3_TC1_IfcOccupant_type
    });
    IFC4X3_TC1_IfcOffsetCurve_type->set_subtypes({
        IFC4X3_TC1_IfcOffsetCurve2D_type,IFC4X3_TC1_IfcOffsetCurve3D_type,IFC4X3_TC1_IfcOffsetCurveByDistances_type
    });
    IFC4X3_TC1_IfcBoundaryCurve_type->set_subtypes({
        IFC4X3_TC1_IfcOuterBoundaryCurve_type
    });
    IFC4X3_TC1_IfcPhysicalQuantity_type->set_subtypes({
        IFC4X3_TC1_IfcPhysicalComplexQuantity_type,IFC4X3_TC1_IfcPhysicalSimpleQuantity_type
    });
    IFC4X3_TC1_IfcPlanarExtent_type->set_subtypes({
        IFC4X3_TC1_IfcPlanarBox_type
    });
    IFC4X3_TC1_IfcTessellatedFaceSet_type->set_subtypes({
        IFC4X3_TC1_IfcPolygonalFaceSet_type,IFC4X3_TC1_IfcTriangulatedFaceSet_type
    });
    IFC4X3_TC1_IfcAddress_type->set_subtypes({
        IFC4X3_TC1_IfcPostalAddress_type,IFC4X3_TC1_IfcTelecomAddress_type
    });
    IFC4X3_TC1_IfcPreDefinedItem_type->set_subtypes({
        IFC4X3_TC1_IfcPreDefinedColour_type,IFC4X3_TC1_IfcPreDefinedCurveFont_type,IFC4X3_TC1_IfcPreDefinedTextFont_type
    });
    IFC4X3_TC1_IfcPropertySetDefinition_type->set_subtypes({
        IFC4X3_TC1_IfcPreDefinedPropertySet_type,IFC4X3_TC1_IfcPropertySet_type,IFC4X3_TC1_IfcQuantitySet_type
    });
    IFC4X3_TC1_IfcPresentationLayerAssignment_type->set_subtypes({
        IFC4X3_TC1_IfcPresentationLayerWithStyle_type
    });
    IFC4X3_TC1_IfcContext_type->set_subtypes({
        IFC4X3_TC1_IfcProject_type,IFC4X3_TC1_IfcProjectLibrary_type
    });
    IFC4X3_TC1_IfcCoordinateReferenceSystem_type->set_subtypes({
        IFC4X3_TC1_IfcProjectedCRS_type
    });
    IFC4X3_TC1_IfcFeatureElementAddition_type->set_subtypes({
        IFC4X3_TC1_IfcProjectionElement_type
    });
    IFC4X3_TC1_IfcSimpleProperty_type->set_subtypes({
        IFC4X3_TC1_IfcPropertyBoundedValue_type,IFC4X3_TC1_IfcPropertyEnumeratedValue_type,IFC4X3_TC1_IfcPropertyListValue_type,IFC4X3_TC1_IfcPropertyReferenceValue_type,IFC4X3_TC1_IfcPropertySingleValue_type,IFC4X3_TC1_IfcPropertyTableValue_type
    });
    IFC4X3_TC1_IfcPropertyDefinition_type->set_subtypes({
        IFC4X3_TC1_IfcPropertySetDefinition_type,IFC4X3_TC1_IfcPropertyTemplateDefinition_type
    });
    IFC4X3_TC1_IfcPropertyTemplateDefinition_type->set_subtypes({
        IFC4X3_TC1_IfcPropertySetTemplate_type,IFC4X3_TC1_IfcPropertyTemplate_type
    });
    IFC4X3_TC1_IfcPhysicalSimpleQuantity_type->set_subtypes({
        IFC4X3_TC1_IfcQuantityArea_type,IFC4X3_TC1_IfcQuantityCount_type,IFC4X3_TC1_IfcQuantityLength_type,IFC4X3_TC1_IfcQuantityNumber_type,IFC4X3_TC1_IfcQuantityTime_type,IFC4X3_TC1_IfcQuantityVolume_type,IFC4X3_TC1_IfcQuantityWeight_type
    });
    IFC4X3_TC1_IfcBSplineCurveWithKnots_type->set_subtypes({
        IFC4X3_TC1_IfcRationalBSplineCurveWithKnots_type
    });
    IFC4X3_TC1_IfcBSplineSurfaceWithKnots_type->set_subtypes({
        IFC4X3_TC1_IfcRationalBSplineSurfaceWithKnots_type
    });
    IFC4X3_TC1_IfcRectangleProfileDef_type->set_subtypes({
        IFC4X3_TC1_IfcRectangleHollowProfileDef_type,IFC4X3_TC1_IfcRoundedRectangleProfileDef_type
    });
    IFC4X3_TC1_IfcPreDefinedProperties_type->set_subtypes({
        IFC4X3_TC1_IfcReinforcementBarProperties_type,IFC4X3_TC1_IfcSectionProperties_type,IFC4X3_TC1_IfcSectionReinforcementProperties_type
    });
    IFC4X3_TC1_IfcReinforcingElement_type->set_subtypes({
        IFC4X3_TC1_IfcReinforcingBar_type,IFC4X3_TC1_IfcReinforcingMesh_type,IFC4X3_TC1_IfcTendon_type,IFC4X3_TC1_IfcTendonAnchor_type,IFC4X3_TC1_IfcTendonConduit_type
    });
    IFC4X3_TC1_IfcReinforcingElementType_type->set_subtypes({
        IFC4X3_TC1_IfcReinforcingBarType_type,IFC4X3_TC1_IfcReinforcingMeshType_type,IFC4X3_TC1_IfcTendonAnchorType_type,IFC4X3_TC1_IfcTendonConduitType_type,IFC4X3_TC1_IfcTendonType_type
    });
    IFC4X3_TC1_IfcRelDecomposes_type->set_subtypes({
        IFC4X3_TC1_IfcRelAdheresToElement_type,IFC4X3_TC1_IfcRelAggregates_type,IFC4X3_TC1_IfcRelNests_type,IFC4X3_TC1_IfcRelProjectsElement_type,IFC4X3_TC1_IfcRelVoidsElement_type
    });
    IFC4X3_TC1_IfcRelationship_type->set_subtypes({
        IFC4X3_TC1_IfcRelAssigns_type,IFC4X3_TC1_IfcRelAssociates_type,IFC4X3_TC1_IfcRelConnects_type,IFC4X3_TC1_IfcRelDeclares_type,IFC4X3_TC1_IfcRelDecomposes_type,IFC4X3_TC1_IfcRelDefines_type
    });
    IFC4X3_TC1_IfcRelAssigns_type->set_subtypes({
        IFC4X3_TC1_IfcRelAssignsToActor_type,IFC4X3_TC1_IfcRelAssignsToControl_type,IFC4X3_TC1_IfcRelAssignsToGroup_type,IFC4X3_TC1_IfcRelAssignsToProcess_type,IFC4X3_TC1_IfcRelAssignsToProduct_type,IFC4X3_TC1_IfcRelAssignsToResource_type
    });
    IFC4X3_TC1_IfcRelAssignsToGroup_type->set_subtypes({
        IFC4X3_TC1_IfcRelAssignsToGroupByFactor_type
    });
    IFC4X3_TC1_IfcRelAssociates_type->set_subtypes({
        IFC4X3_TC1_IfcRelAssociatesApproval_type,IFC4X3_TC1_IfcRelAssociatesClassification_type,IFC4X3_TC1_IfcRelAssociatesConstraint_type,IFC4X3_TC1_IfcRelAssociatesDocument_type,IFC4X3_TC1_IfcRelAssociatesLibrary_type,IFC4X3_TC1_IfcRelAssociatesMaterial_type,IFC4X3_TC1_IfcRelAssociatesProfileDef_type
    });
    IFC4X3_TC1_IfcRelConnects_type->set_subtypes({
        IFC4X3_TC1_IfcRelConnectsElements_type,IFC4X3_TC1_IfcRelConnectsPortToElement_type,IFC4X3_TC1_IfcRelConnectsPorts_type,IFC4X3_TC1_IfcRelConnectsStructuralActivity_type,IFC4X3_TC1_IfcRelConnectsStructuralMember_type,IFC4X3_TC1_IfcRelContainedInSpatialStructure_type,IFC4X3_TC1_IfcRelCoversBldgElements_type,IFC4X3_TC1_IfcRelCoversSpaces_type,IFC4X3_TC1_IfcRelFillsElement_type,IFC4X3_TC1_IfcRelFlowControlElements_type,IFC4X3_TC1_IfcRelInterferesElements_type,IFC4X3_TC1_IfcRelPositions_type,IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type,IFC4X3_TC1_IfcRelSequence_type,IFC4X3_TC1_IfcRelServicesBuildings_type,IFC4X3_TC1_IfcRelSpaceBoundary_type
    });
    IFC4X3_TC1_IfcRelConnectsElements_type->set_subtypes({
        IFC4X3_TC1_IfcRelConnectsPathElements_type,IFC4X3_TC1_IfcRelConnectsWithRealizingElements_type
    });
    IFC4X3_TC1_IfcRelConnectsStructuralMember_type->set_subtypes({
        IFC4X3_TC1_IfcRelConnectsWithEccentricity_type
    });
    IFC4X3_TC1_IfcRelDefines_type->set_subtypes({
        IFC4X3_TC1_IfcRelDefinesByObject_type,IFC4X3_TC1_IfcRelDefinesByProperties_type,IFC4X3_TC1_IfcRelDefinesByTemplate_type,IFC4X3_TC1_IfcRelDefinesByType_type
    });
    IFC4X3_TC1_IfcRelSpaceBoundary_type->set_subtypes({
        IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type
    });
    IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type->set_subtypes({
        IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type
    });
    IFC4X3_TC1_IfcCompositeCurveSegment_type->set_subtypes({
        IFC4X3_TC1_IfcReparametrisedCompositeCurveSegment_type
    });
    IFC4X3_TC1_IfcRevolvedAreaSolid_type->set_subtypes({
        IFC4X3_TC1_IfcRevolvedAreaSolidTapered_type
    });
    IFC4X3_TC1_IfcSectionedSolid_type->set_subtypes({
        IFC4X3_TC1_IfcSectionedSolidHorizontal_type
    });
    IFC4X3_TC1_IfcRepresentation_type->set_subtypes({
        IFC4X3_TC1_IfcShapeModel_type,IFC4X3_TC1_IfcStyleModel_type
    });
    IFC4X3_TC1_IfcShapeModel_type->set_subtypes({
        IFC4X3_TC1_IfcShapeRepresentation_type,IFC4X3_TC1_IfcTopologyRepresentation_type
    });
    IFC4X3_TC1_IfcSpatialStructureElementType_type->set_subtypes({
        IFC4X3_TC1_IfcSpaceType_type
    });
    IFC4X3_TC1_IfcSpatialElementType_type->set_subtypes({
        IFC4X3_TC1_IfcSpatialStructureElementType_type,IFC4X3_TC1_IfcSpatialZoneType_type
    });
    IFC4X3_TC1_IfcStructuralActivity_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralAction_type,IFC4X3_TC1_IfcStructuralReaction_type
    });
    IFC4X3_TC1_IfcStructuralItem_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralConnection_type,IFC4X3_TC1_IfcStructuralMember_type
    });
    IFC4X3_TC1_IfcStructuralAction_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralCurveAction_type,IFC4X3_TC1_IfcStructuralPointAction_type,IFC4X3_TC1_IfcStructuralSurfaceAction_type
    });
    IFC4X3_TC1_IfcStructuralConnection_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralCurveConnection_type,IFC4X3_TC1_IfcStructuralPointConnection_type,IFC4X3_TC1_IfcStructuralSurfaceConnection_type
    });
    IFC4X3_TC1_IfcStructuralMember_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralCurveMember_type,IFC4X3_TC1_IfcStructuralSurfaceMember_type
    });
    IFC4X3_TC1_IfcStructuralCurveMember_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralCurveMemberVarying_type
    });
    IFC4X3_TC1_IfcStructuralReaction_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralCurveReaction_type,IFC4X3_TC1_IfcStructuralPointReaction_type,IFC4X3_TC1_IfcStructuralSurfaceReaction_type
    });
    IFC4X3_TC1_IfcStructuralCurveAction_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralLinearAction_type
    });
    IFC4X3_TC1_IfcStructuralLoadGroup_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralLoadCase_type
    });
    IFC4X3_TC1_IfcStructuralLoad_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralLoadConfiguration_type,IFC4X3_TC1_IfcStructuralLoadOrResult_type
    });
    IFC4X3_TC1_IfcStructuralLoadStatic_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralLoadLinearForce_type,IFC4X3_TC1_IfcStructuralLoadPlanarForce_type,IFC4X3_TC1_IfcStructuralLoadSingleDisplacement_type,IFC4X3_TC1_IfcStructuralLoadSingleForce_type,IFC4X3_TC1_IfcStructuralLoadTemperature_type
    });
    IFC4X3_TC1_IfcStructuralLoadSingleDisplacement_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralLoadSingleDisplacementDistortion_type
    });
    IFC4X3_TC1_IfcStructuralLoadSingleForce_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralLoadSingleForceWarping_type
    });
    IFC4X3_TC1_IfcStructuralLoadOrResult_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralLoadStatic_type,IFC4X3_TC1_IfcSurfaceReinforcementArea_type
    });
    IFC4X3_TC1_IfcStructuralSurfaceAction_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralPlanarAction_type
    });
    IFC4X3_TC1_IfcStructuralSurfaceMember_type->set_subtypes({
        IFC4X3_TC1_IfcStructuralSurfaceMemberVarying_type
    });
    IFC4X3_TC1_IfcStyleModel_type->set_subtypes({
        IFC4X3_TC1_IfcStyledRepresentation_type
    });
    IFC4X3_TC1_IfcSweptSurface_type->set_subtypes({
        IFC4X3_TC1_IfcSurfaceOfLinearExtrusion_type,IFC4X3_TC1_IfcSurfaceOfRevolution_type
    });
    IFC4X3_TC1_IfcSurfaceStyleShading_type->set_subtypes({
        IFC4X3_TC1_IfcSurfaceStyleRendering_type
    });
    IFC4X3_TC1_IfcSweptDiskSolid_type->set_subtypes({
        IFC4X3_TC1_IfcSweptDiskSolidPolygonal_type
    });
    IFC4X3_TC1_IfcTaskTime_type->set_subtypes({
        IFC4X3_TC1_IfcTaskTimeRecurring_type
    });
    IFC4X3_TC1_IfcTextLiteral_type->set_subtypes({
        IFC4X3_TC1_IfcTextLiteralWithExtent_type
    });
    IFC4X3_TC1_IfcPreDefinedTextFont_type->set_subtypes({
        IFC4X3_TC1_IfcTextStyleFontModel_type
    });
    IFC4X3_TC1_IfcTextureCoordinateIndices_type->set_subtypes({
        IFC4X3_TC1_IfcTextureCoordinateIndicesWithVoids_type
    });
    IFC4X3_TC1_IfcTransportationDevice_type->set_subtypes({
        IFC4X3_TC1_IfcTransportElement_type,IFC4X3_TC1_IfcVehicle_type
    });
    IFC4X3_TC1_IfcTransportationDeviceType_type->set_subtypes({
        IFC4X3_TC1_IfcTransportElementType_type,IFC4X3_TC1_IfcVehicleType_type
    });
    IFC4X3_TC1_IfcTriangulatedFaceSet_type->set_subtypes({
        IFC4X3_TC1_IfcTriangulatedIrregularNetwork_type
    });
    IFC4X3_TC1_IfcTypeObject_type->set_subtypes({
        IFC4X3_TC1_IfcTypeProcess_type,IFC4X3_TC1_IfcTypeProduct_type,IFC4X3_TC1_IfcTypeResource_type
    });
    IFC4X3_TC1_IfcVertex_type->set_subtypes({
        IFC4X3_TC1_IfcVertexPoint_type
    });
    IFC4X3_TC1_IfcWall_type->set_subtypes({
        IFC4X3_TC1_IfcWallStandardCase_type
    });
    IFC4X3_TC1_IfcWorkControl_type->set_subtypes({
        IFC4X3_TC1_IfcWorkPlan_type,IFC4X3_TC1_IfcWorkSchedule_type
    });

    std::vector<const declaration*> declarations= {
    IFC4X3_TC1_IfcAbsorbedDoseMeasure_type,
    IFC4X3_TC1_IfcAccelerationMeasure_type,
    IFC4X3_TC1_IfcActionRequest_type,
    IFC4X3_TC1_IfcActionRequestTypeEnum_type,
    IFC4X3_TC1_IfcActionSourceTypeEnum_type,
    IFC4X3_TC1_IfcActionTypeEnum_type,
    IFC4X3_TC1_IfcActor_type,
    IFC4X3_TC1_IfcActorRole_type,
    IFC4X3_TC1_IfcActorSelect_type,
    IFC4X3_TC1_IfcActuator_type,
    IFC4X3_TC1_IfcActuatorType_type,
    IFC4X3_TC1_IfcActuatorTypeEnum_type,
    IFC4X3_TC1_IfcAddress_type,
    IFC4X3_TC1_IfcAddressTypeEnum_type,
    IFC4X3_TC1_IfcAdvancedBrep_type,
    IFC4X3_TC1_IfcAdvancedBrepWithVoids_type,
    IFC4X3_TC1_IfcAdvancedFace_type,
    IFC4X3_TC1_IfcAirTerminal_type,
    IFC4X3_TC1_IfcAirTerminalBox_type,
    IFC4X3_TC1_IfcAirTerminalBoxType_type,
    IFC4X3_TC1_IfcAirTerminalBoxTypeEnum_type,
    IFC4X3_TC1_IfcAirTerminalType_type,
    IFC4X3_TC1_IfcAirTerminalTypeEnum_type,
    IFC4X3_TC1_IfcAirToAirHeatRecovery_type,
    IFC4X3_TC1_IfcAirToAirHeatRecoveryType_type,
    IFC4X3_TC1_IfcAirToAirHeatRecoveryTypeEnum_type,
    IFC4X3_TC1_IfcAlarm_type,
    IFC4X3_TC1_IfcAlarmType_type,
    IFC4X3_TC1_IfcAlarmTypeEnum_type,
    IFC4X3_TC1_IfcAlignment_type,
    IFC4X3_TC1_IfcAlignmentCant_type,
    IFC4X3_TC1_IfcAlignmentCantSegment_type,
    IFC4X3_TC1_IfcAlignmentCantSegmentTypeEnum_type,
    IFC4X3_TC1_IfcAlignmentHorizontal_type,
    IFC4X3_TC1_IfcAlignmentHorizontalSegment_type,
    IFC4X3_TC1_IfcAlignmentHorizontalSegmentTypeEnum_type,
    IFC4X3_TC1_IfcAlignmentParameterSegment_type,
    IFC4X3_TC1_IfcAlignmentSegment_type,
    IFC4X3_TC1_IfcAlignmentTypeEnum_type,
    IFC4X3_TC1_IfcAlignmentVertical_type,
    IFC4X3_TC1_IfcAlignmentVerticalSegment_type,
    IFC4X3_TC1_IfcAlignmentVerticalSegmentTypeEnum_type,
    IFC4X3_TC1_IfcAmountOfSubstanceMeasure_type,
    IFC4X3_TC1_IfcAnalysisModelTypeEnum_type,
    IFC4X3_TC1_IfcAnalysisTheoryTypeEnum_type,
    IFC4X3_TC1_IfcAngularVelocityMeasure_type,
    IFC4X3_TC1_IfcAnnotation_type,
    IFC4X3_TC1_IfcAnnotationFillArea_type,
    IFC4X3_TC1_IfcAnnotationTypeEnum_type,
    IFC4X3_TC1_IfcApplication_type,
    IFC4X3_TC1_IfcAppliedValue_type,
    IFC4X3_TC1_IfcAppliedValueSelect_type,
    IFC4X3_TC1_IfcApproval_type,
    IFC4X3_TC1_IfcApprovalRelationship_type,
    IFC4X3_TC1_IfcArbitraryClosedProfileDef_type,
    IFC4X3_TC1_IfcArbitraryOpenProfileDef_type,
    IFC4X3_TC1_IfcArbitraryProfileDefWithVoids_type,
    IFC4X3_TC1_IfcArcIndex_type,
    IFC4X3_TC1_IfcAreaDensityMeasure_type,
    IFC4X3_TC1_IfcAreaMeasure_type,
    IFC4X3_TC1_IfcArithmeticOperatorEnum_type,
    IFC4X3_TC1_IfcAssemblyPlaceEnum_type,
    IFC4X3_TC1_IfcAsset_type,
    IFC4X3_TC1_IfcAsymmetricIShapeProfileDef_type,
    IFC4X3_TC1_IfcAudioVisualAppliance_type,
    IFC4X3_TC1_IfcAudioVisualApplianceType_type,
    IFC4X3_TC1_IfcAudioVisualApplianceTypeEnum_type,
    IFC4X3_TC1_IfcAxis1Placement_type,
    IFC4X3_TC1_IfcAxis2Placement_type,
    IFC4X3_TC1_IfcAxis2Placement2D_type,
    IFC4X3_TC1_IfcAxis2Placement3D_type,
    IFC4X3_TC1_IfcAxis2PlacementLinear_type,
    IFC4X3_TC1_IfcBeam_type,
    IFC4X3_TC1_IfcBeamType_type,
    IFC4X3_TC1_IfcBeamTypeEnum_type,
    IFC4X3_TC1_IfcBearing_type,
    IFC4X3_TC1_IfcBearingType_type,
    IFC4X3_TC1_IfcBearingTypeEnum_type,
    IFC4X3_TC1_IfcBenchmarkEnum_type,
    IFC4X3_TC1_IfcBendingParameterSelect_type,
    IFC4X3_TC1_IfcBinary_type,
    IFC4X3_TC1_IfcBlobTexture_type,
    IFC4X3_TC1_IfcBlock_type,
    IFC4X3_TC1_IfcBoiler_type,
    IFC4X3_TC1_IfcBoilerType_type,
    IFC4X3_TC1_IfcBoilerTypeEnum_type,
    IFC4X3_TC1_IfcBoolean_type,
    IFC4X3_TC1_IfcBooleanClippingResult_type,
    IFC4X3_TC1_IfcBooleanOperand_type,
    IFC4X3_TC1_IfcBooleanOperator_type,
    IFC4X3_TC1_IfcBooleanResult_type,
    IFC4X3_TC1_IfcBorehole_type,
    IFC4X3_TC1_IfcBoundaryCondition_type,
    IFC4X3_TC1_IfcBoundaryCurve_type,
    IFC4X3_TC1_IfcBoundaryEdgeCondition_type,
    IFC4X3_TC1_IfcBoundaryFaceCondition_type,
    IFC4X3_TC1_IfcBoundaryNodeCondition_type,
    IFC4X3_TC1_IfcBoundaryNodeConditionWarping_type,
    IFC4X3_TC1_IfcBoundedCurve_type,
    IFC4X3_TC1_IfcBoundedSurface_type,
    IFC4X3_TC1_IfcBoundingBox_type,
    IFC4X3_TC1_IfcBoxAlignment_type,
    IFC4X3_TC1_IfcBoxedHalfSpace_type,
    IFC4X3_TC1_IfcBridge_type,
    IFC4X3_TC1_IfcBridgePart_type,
    IFC4X3_TC1_IfcBridgePartTypeEnum_type,
    IFC4X3_TC1_IfcBridgeTypeEnum_type,
    IFC4X3_TC1_IfcBSplineCurve_type,
    IFC4X3_TC1_IfcBSplineCurveForm_type,
    IFC4X3_TC1_IfcBSplineCurveWithKnots_type,
    IFC4X3_TC1_IfcBSplineSurface_type,
    IFC4X3_TC1_IfcBSplineSurfaceForm_type,
    IFC4X3_TC1_IfcBSplineSurfaceWithKnots_type,
    IFC4X3_TC1_IfcBuilding_type,
    IFC4X3_TC1_IfcBuildingElementPart_type,
    IFC4X3_TC1_IfcBuildingElementPartType_type,
    IFC4X3_TC1_IfcBuildingElementPartTypeEnum_type,
    IFC4X3_TC1_IfcBuildingElementProxy_type,
    IFC4X3_TC1_IfcBuildingElementProxyType_type,
    IFC4X3_TC1_IfcBuildingElementProxyTypeEnum_type,
    IFC4X3_TC1_IfcBuildingStorey_type,
    IFC4X3_TC1_IfcBuildingSystem_type,
    IFC4X3_TC1_IfcBuildingSystemTypeEnum_type,
    IFC4X3_TC1_IfcBuiltElement_type,
    IFC4X3_TC1_IfcBuiltElementType_type,
    IFC4X3_TC1_IfcBuiltSystem_type,
    IFC4X3_TC1_IfcBuiltSystemTypeEnum_type,
    IFC4X3_TC1_IfcBurner_type,
    IFC4X3_TC1_IfcBurnerType_type,
    IFC4X3_TC1_IfcBurnerTypeEnum_type,
    IFC4X3_TC1_IfcCableCarrierFitting_type,
    IFC4X3_TC1_IfcCableCarrierFittingType_type,
    IFC4X3_TC1_IfcCableCarrierFittingTypeEnum_type,
    IFC4X3_TC1_IfcCableCarrierSegment_type,
    IFC4X3_TC1_IfcCableCarrierSegmentType_type,
    IFC4X3_TC1_IfcCableCarrierSegmentTypeEnum_type,
    IFC4X3_TC1_IfcCableFitting_type,
    IFC4X3_TC1_IfcCableFittingType_type,
    IFC4X3_TC1_IfcCableFittingTypeEnum_type,
    IFC4X3_TC1_IfcCableSegment_type,
    IFC4X3_TC1_IfcCableSegmentType_type,
    IFC4X3_TC1_IfcCableSegmentTypeEnum_type,
    IFC4X3_TC1_IfcCaissonFoundation_type,
    IFC4X3_TC1_IfcCaissonFoundationType_type,
    IFC4X3_TC1_IfcCaissonFoundationTypeEnum_type,
    IFC4X3_TC1_IfcCardinalPointReference_type,
    IFC4X3_TC1_IfcCartesianPoint_type,
    IFC4X3_TC1_IfcCartesianPointList_type,
    IFC4X3_TC1_IfcCartesianPointList2D_type,
    IFC4X3_TC1_IfcCartesianPointList3D_type,
    IFC4X3_TC1_IfcCartesianTransformationOperator_type,
    IFC4X3_TC1_IfcCartesianTransformationOperator2D_type,
    IFC4X3_TC1_IfcCartesianTransformationOperator2DnonUniform_type,
    IFC4X3_TC1_IfcCartesianTransformationOperator3D_type,
    IFC4X3_TC1_IfcCartesianTransformationOperator3DnonUniform_type,
    IFC4X3_TC1_IfcCenterLineProfileDef_type,
    IFC4X3_TC1_IfcChangeActionEnum_type,
    IFC4X3_TC1_IfcChiller_type,
    IFC4X3_TC1_IfcChillerType_type,
    IFC4X3_TC1_IfcChillerTypeEnum_type,
    IFC4X3_TC1_IfcChimney_type,
    IFC4X3_TC1_IfcChimneyType_type,
    IFC4X3_TC1_IfcChimneyTypeEnum_type,
    IFC4X3_TC1_IfcCircle_type,
    IFC4X3_TC1_IfcCircleHollowProfileDef_type,
    IFC4X3_TC1_IfcCircleProfileDef_type,
    IFC4X3_TC1_IfcCivilElement_type,
    IFC4X3_TC1_IfcCivilElementType_type,
    IFC4X3_TC1_IfcClassification_type,
    IFC4X3_TC1_IfcClassificationReference_type,
    IFC4X3_TC1_IfcClassificationReferenceSelect_type,
    IFC4X3_TC1_IfcClassificationSelect_type,
    IFC4X3_TC1_IfcClosedShell_type,
    IFC4X3_TC1_IfcClothoid_type,
    IFC4X3_TC1_IfcCoil_type,
    IFC4X3_TC1_IfcCoilType_type,
    IFC4X3_TC1_IfcCoilTypeEnum_type,
    IFC4X3_TC1_IfcColour_type,
    IFC4X3_TC1_IfcColourOrFactor_type,
    IFC4X3_TC1_IfcColourRgb_type,
    IFC4X3_TC1_IfcColourRgbList_type,
    IFC4X3_TC1_IfcColourSpecification_type,
    IFC4X3_TC1_IfcColumn_type,
    IFC4X3_TC1_IfcColumnType_type,
    IFC4X3_TC1_IfcColumnTypeEnum_type,
    IFC4X3_TC1_IfcCommunicationsAppliance_type,
    IFC4X3_TC1_IfcCommunicationsApplianceType_type,
    IFC4X3_TC1_IfcCommunicationsApplianceTypeEnum_type,
    IFC4X3_TC1_IfcComplexNumber_type,
    IFC4X3_TC1_IfcComplexProperty_type,
    IFC4X3_TC1_IfcComplexPropertyTemplate_type,
    IFC4X3_TC1_IfcComplexPropertyTemplateTypeEnum_type,
    IFC4X3_TC1_IfcCompositeCurve_type,
    IFC4X3_TC1_IfcCompositeCurveOnSurface_type,
    IFC4X3_TC1_IfcCompositeCurveSegment_type,
    IFC4X3_TC1_IfcCompositeProfileDef_type,
    IFC4X3_TC1_IfcCompoundPlaneAngleMeasure_type,
    IFC4X3_TC1_IfcCompressor_type,
    IFC4X3_TC1_IfcCompressorType_type,
    IFC4X3_TC1_IfcCompressorTypeEnum_type,
    IFC4X3_TC1_IfcCondenser_type,
    IFC4X3_TC1_IfcCondenserType_type,
    IFC4X3_TC1_IfcCondenserTypeEnum_type,
    IFC4X3_TC1_IfcConic_type,
    IFC4X3_TC1_IfcConnectedFaceSet_type,
    IFC4X3_TC1_IfcConnectionCurveGeometry_type,
    IFC4X3_TC1_IfcConnectionGeometry_type,
    IFC4X3_TC1_IfcConnectionPointEccentricity_type,
    IFC4X3_TC1_IfcConnectionPointGeometry_type,
    IFC4X3_TC1_IfcConnectionSurfaceGeometry_type,
    IFC4X3_TC1_IfcConnectionTypeEnum_type,
    IFC4X3_TC1_IfcConnectionVolumeGeometry_type,
    IFC4X3_TC1_IfcConstraint_type,
    IFC4X3_TC1_IfcConstraintEnum_type,
    IFC4X3_TC1_IfcConstructionEquipmentResource_type,
    IFC4X3_TC1_IfcConstructionEquipmentResourceType_type,
    IFC4X3_TC1_IfcConstructionEquipmentResourceTypeEnum_type,
    IFC4X3_TC1_IfcConstructionMaterialResource_type,
    IFC4X3_TC1_IfcConstructionMaterialResourceType_type,
    IFC4X3_TC1_IfcConstructionMaterialResourceTypeEnum_type,
    IFC4X3_TC1_IfcConstructionProductResource_type,
    IFC4X3_TC1_IfcConstructionProductResourceType_type,
    IFC4X3_TC1_IfcConstructionProductResourceTypeEnum_type,
    IFC4X3_TC1_IfcConstructionResource_type,
    IFC4X3_TC1_IfcConstructionResourceType_type,
    IFC4X3_TC1_IfcContext_type,
    IFC4X3_TC1_IfcContextDependentMeasure_type,
    IFC4X3_TC1_IfcContextDependentUnit_type,
    IFC4X3_TC1_IfcControl_type,
    IFC4X3_TC1_IfcController_type,
    IFC4X3_TC1_IfcControllerType_type,
    IFC4X3_TC1_IfcControllerTypeEnum_type,
    IFC4X3_TC1_IfcConversionBasedUnit_type,
    IFC4X3_TC1_IfcConversionBasedUnitWithOffset_type,
    IFC4X3_TC1_IfcConveyorSegment_type,
    IFC4X3_TC1_IfcConveyorSegmentType_type,
    IFC4X3_TC1_IfcConveyorSegmentTypeEnum_type,
    IFC4X3_TC1_IfcCooledBeam_type,
    IFC4X3_TC1_IfcCooledBeamType_type,
    IFC4X3_TC1_IfcCooledBeamTypeEnum_type,
    IFC4X3_TC1_IfcCoolingTower_type,
    IFC4X3_TC1_IfcCoolingTowerType_type,
    IFC4X3_TC1_IfcCoolingTowerTypeEnum_type,
    IFC4X3_TC1_IfcCoordinateOperation_type,
    IFC4X3_TC1_IfcCoordinateReferenceSystem_type,
    IFC4X3_TC1_IfcCoordinateReferenceSystemSelect_type,
    IFC4X3_TC1_IfcCosineSpiral_type,
    IFC4X3_TC1_IfcCostItem_type,
    IFC4X3_TC1_IfcCostItemTypeEnum_type,
    IFC4X3_TC1_IfcCostSchedule_type,
    IFC4X3_TC1_IfcCostScheduleTypeEnum_type,
    IFC4X3_TC1_IfcCostValue_type,
    IFC4X3_TC1_IfcCountMeasure_type,
    IFC4X3_TC1_IfcCourse_type,
    IFC4X3_TC1_IfcCourseType_type,
    IFC4X3_TC1_IfcCourseTypeEnum_type,
    IFC4X3_TC1_IfcCovering_type,
    IFC4X3_TC1_IfcCoveringType_type,
    IFC4X3_TC1_IfcCoveringTypeEnum_type,
    IFC4X3_TC1_IfcCrewResource_type,
    IFC4X3_TC1_IfcCrewResourceType_type,
    IFC4X3_TC1_IfcCrewResourceTypeEnum_type,
    IFC4X3_TC1_IfcCsgPrimitive3D_type,
    IFC4X3_TC1_IfcCsgSelect_type,
    IFC4X3_TC1_IfcCsgSolid_type,
    IFC4X3_TC1_IfcCShapeProfileDef_type,
    IFC4X3_TC1_IfcCurrencyRelationship_type,
    IFC4X3_TC1_IfcCurtainWall_type,
    IFC4X3_TC1_IfcCurtainWallType_type,
    IFC4X3_TC1_IfcCurtainWallTypeEnum_type,
    IFC4X3_TC1_IfcCurvatureMeasure_type,
    IFC4X3_TC1_IfcCurve_type,
    IFC4X3_TC1_IfcCurveBoundedPlane_type,
    IFC4X3_TC1_IfcCurveBoundedSurface_type,
    IFC4X3_TC1_IfcCurveFontOrScaledCurveFontSelect_type,
    IFC4X3_TC1_IfcCurveInterpolationEnum_type,
    IFC4X3_TC1_IfcCurveMeasureSelect_type,
    IFC4X3_TC1_IfcCurveOnSurface_type,
    IFC4X3_TC1_IfcCurveOrEdgeCurve_type,
    IFC4X3_TC1_IfcCurveSegment_type,
    IFC4X3_TC1_IfcCurveStyle_type,
    IFC4X3_TC1_IfcCurveStyleFont_type,
    IFC4X3_TC1_IfcCurveStyleFontAndScaling_type,
    IFC4X3_TC1_IfcCurveStyleFontPattern_type,
    IFC4X3_TC1_IfcCurveStyleFontSelect_type,
    IFC4X3_TC1_IfcCylindricalSurface_type,
    IFC4X3_TC1_IfcDamper_type,
    IFC4X3_TC1_IfcDamperType_type,
    IFC4X3_TC1_IfcDamperTypeEnum_type,
    IFC4X3_TC1_IfcDataOriginEnum_type,
    IFC4X3_TC1_IfcDate_type,
    IFC4X3_TC1_IfcDateTime_type,
    IFC4X3_TC1_IfcDayInMonthNumber_type,
    IFC4X3_TC1_IfcDayInWeekNumber_type,
    IFC4X3_TC1_IfcDeepFoundation_type,
    IFC4X3_TC1_IfcDeepFoundationType_type,
    IFC4X3_TC1_IfcDefinitionSelect_type,
    IFC4X3_TC1_IfcDerivedMeasureValue_type,
    IFC4X3_TC1_IfcDerivedProfileDef_type,
    IFC4X3_TC1_IfcDerivedUnit_type,
    IFC4X3_TC1_IfcDerivedUnitElement_type,
    IFC4X3_TC1_IfcDerivedUnitEnum_type,
    IFC4X3_TC1_IfcDescriptiveMeasure_type,
    IFC4X3_TC1_IfcDimensionalExponents_type,
    IFC4X3_TC1_IfcDimensionCount_type,
    IFC4X3_TC1_IfcDirection_type,
    IFC4X3_TC1_IfcDirectionSenseEnum_type,
    IFC4X3_TC1_IfcDirectrixCurveSweptAreaSolid_type,
    IFC4X3_TC1_IfcDirectrixDerivedReferenceSweptAreaSolid_type,
    IFC4X3_TC1_IfcDiscreteAccessory_type,
    IFC4X3_TC1_IfcDiscreteAccessoryType_type,
    IFC4X3_TC1_IfcDiscreteAccessoryTypeEnum_type,
    IFC4X3_TC1_IfcDistributionBoard_type,
    IFC4X3_TC1_IfcDistributionBoardType_type,
    IFC4X3_TC1_IfcDistributionBoardTypeEnum_type,
    IFC4X3_TC1_IfcDistributionChamberElement_type,
    IFC4X3_TC1_IfcDistributionChamberElementType_type,
    IFC4X3_TC1_IfcDistributionChamberElementTypeEnum_type,
    IFC4X3_TC1_IfcDistributionCircuit_type,
    IFC4X3_TC1_IfcDistributionControlElement_type,
    IFC4X3_TC1_IfcDistributionControlElementType_type,
    IFC4X3_TC1_IfcDistributionElement_type,
    IFC4X3_TC1_IfcDistributionElementType_type,
    IFC4X3_TC1_IfcDistributionFlowElement_type,
    IFC4X3_TC1_IfcDistributionFlowElementType_type,
    IFC4X3_TC1_IfcDistributionPort_type,
    IFC4X3_TC1_IfcDistributionPortTypeEnum_type,
    IFC4X3_TC1_IfcDistributionSystem_type,
    IFC4X3_TC1_IfcDistributionSystemEnum_type,
    IFC4X3_TC1_IfcDocumentConfidentialityEnum_type,
    IFC4X3_TC1_IfcDocumentInformation_type,
    IFC4X3_TC1_IfcDocumentInformationRelationship_type,
    IFC4X3_TC1_IfcDocumentReference_type,
    IFC4X3_TC1_IfcDocumentSelect_type,
    IFC4X3_TC1_IfcDocumentStatusEnum_type,
    IFC4X3_TC1_IfcDoor_type,
    IFC4X3_TC1_IfcDoorLiningProperties_type,
    IFC4X3_TC1_IfcDoorPanelOperationEnum_type,
    IFC4X3_TC1_IfcDoorPanelPositionEnum_type,
    IFC4X3_TC1_IfcDoorPanelProperties_type,
    IFC4X3_TC1_IfcDoorType_type,
    IFC4X3_TC1_IfcDoorTypeEnum_type,
    IFC4X3_TC1_IfcDoorTypeOperationEnum_type,
    IFC4X3_TC1_IfcDoseEquivalentMeasure_type,
    IFC4X3_TC1_IfcDraughtingPreDefinedColour_type,
    IFC4X3_TC1_IfcDraughtingPreDefinedCurveFont_type,
    IFC4X3_TC1_IfcDuctFitting_type,
    IFC4X3_TC1_IfcDuctFittingType_type,
    IFC4X3_TC1_IfcDuctFittingTypeEnum_type,
    IFC4X3_TC1_IfcDuctSegment_type,
    IFC4X3_TC1_IfcDuctSegmentType_type,
    IFC4X3_TC1_IfcDuctSegmentTypeEnum_type,
    IFC4X3_TC1_IfcDuctSilencer_type,
    IFC4X3_TC1_IfcDuctSilencerType_type,
    IFC4X3_TC1_IfcDuctSilencerTypeEnum_type,
    IFC4X3_TC1_IfcDuration_type,
    IFC4X3_TC1_IfcDynamicViscosityMeasure_type,
    IFC4X3_TC1_IfcEarthworksCut_type,
    IFC4X3_TC1_IfcEarthworksCutTypeEnum_type,
    IFC4X3_TC1_IfcEarthworksElement_type,
    IFC4X3_TC1_IfcEarthworksFill_type,
    IFC4X3_TC1_IfcEarthworksFillTypeEnum_type,
    IFC4X3_TC1_IfcEdge_type,
    IFC4X3_TC1_IfcEdgeCurve_type,
    IFC4X3_TC1_IfcEdgeLoop_type,
    IFC4X3_TC1_IfcElectricAppliance_type,
    IFC4X3_TC1_IfcElectricApplianceType_type,
    IFC4X3_TC1_IfcElectricApplianceTypeEnum_type,
    IFC4X3_TC1_IfcElectricCapacitanceMeasure_type,
    IFC4X3_TC1_IfcElectricChargeMeasure_type,
    IFC4X3_TC1_IfcElectricConductanceMeasure_type,
    IFC4X3_TC1_IfcElectricCurrentMeasure_type,
    IFC4X3_TC1_IfcElectricDistributionBoard_type,
    IFC4X3_TC1_IfcElectricDistributionBoardType_type,
    IFC4X3_TC1_IfcElectricDistributionBoardTypeEnum_type,
    IFC4X3_TC1_IfcElectricFlowStorageDevice_type,
    IFC4X3_TC1_IfcElectricFlowStorageDeviceType_type,
    IFC4X3_TC1_IfcElectricFlowStorageDeviceTypeEnum_type,
    IFC4X3_TC1_IfcElectricFlowTreatmentDevice_type,
    IFC4X3_TC1_IfcElectricFlowTreatmentDeviceType_type,
    IFC4X3_TC1_IfcElectricFlowTreatmentDeviceTypeEnum_type,
    IFC4X3_TC1_IfcElectricGenerator_type,
    IFC4X3_TC1_IfcElectricGeneratorType_type,
    IFC4X3_TC1_IfcElectricGeneratorTypeEnum_type,
    IFC4X3_TC1_IfcElectricMotor_type,
    IFC4X3_TC1_IfcElectricMotorType_type,
    IFC4X3_TC1_IfcElectricMotorTypeEnum_type,
    IFC4X3_TC1_IfcElectricResistanceMeasure_type,
    IFC4X3_TC1_IfcElectricTimeControl_type,
    IFC4X3_TC1_IfcElectricTimeControlType_type,
    IFC4X3_TC1_IfcElectricTimeControlTypeEnum_type,
    IFC4X3_TC1_IfcElectricVoltageMeasure_type,
    IFC4X3_TC1_IfcElement_type,
    IFC4X3_TC1_IfcElementarySurface_type,
    IFC4X3_TC1_IfcElementAssembly_type,
    IFC4X3_TC1_IfcElementAssemblyType_type,
    IFC4X3_TC1_IfcElementAssemblyTypeEnum_type,
    IFC4X3_TC1_IfcElementComponent_type,
    IFC4X3_TC1_IfcElementComponentType_type,
    IFC4X3_TC1_IfcElementCompositionEnum_type,
    IFC4X3_TC1_IfcElementQuantity_type,
    IFC4X3_TC1_IfcElementType_type,
    IFC4X3_TC1_IfcEllipse_type,
    IFC4X3_TC1_IfcEllipseProfileDef_type,
    IFC4X3_TC1_IfcEnergyConversionDevice_type,
    IFC4X3_TC1_IfcEnergyConversionDeviceType_type,
    IFC4X3_TC1_IfcEnergyMeasure_type,
    IFC4X3_TC1_IfcEngine_type,
    IFC4X3_TC1_IfcEngineType_type,
    IFC4X3_TC1_IfcEngineTypeEnum_type,
    IFC4X3_TC1_IfcEvaporativeCooler_type,
    IFC4X3_TC1_IfcEvaporativeCoolerType_type,
    IFC4X3_TC1_IfcEvaporativeCoolerTypeEnum_type,
    IFC4X3_TC1_IfcEvaporator_type,
    IFC4X3_TC1_IfcEvaporatorType_type,
    IFC4X3_TC1_IfcEvaporatorTypeEnum_type,
    IFC4X3_TC1_IfcEvent_type,
    IFC4X3_TC1_IfcEventTime_type,
    IFC4X3_TC1_IfcEventTriggerTypeEnum_type,
    IFC4X3_TC1_IfcEventType_type,
    IFC4X3_TC1_IfcEventTypeEnum_type,
    IFC4X3_TC1_IfcExtendedProperties_type,
    IFC4X3_TC1_IfcExternalInformation_type,
    IFC4X3_TC1_IfcExternallyDefinedHatchStyle_type,
    IFC4X3_TC1_IfcExternallyDefinedSurfaceStyle_type,
    IFC4X3_TC1_IfcExternallyDefinedTextFont_type,
    IFC4X3_TC1_IfcExternalReference_type,
    IFC4X3_TC1_IfcExternalReferenceRelationship_type,
    IFC4X3_TC1_IfcExternalSpatialElement_type,
    IFC4X3_TC1_IfcExternalSpatialElementTypeEnum_type,
    IFC4X3_TC1_IfcExternalSpatialStructureElement_type,
    IFC4X3_TC1_IfcExtrudedAreaSolid_type,
    IFC4X3_TC1_IfcExtrudedAreaSolidTapered_type,
    IFC4X3_TC1_IfcFace_type,
    IFC4X3_TC1_IfcFaceBasedSurfaceModel_type,
    IFC4X3_TC1_IfcFaceBound_type,
    IFC4X3_TC1_IfcFaceOuterBound_type,
    IFC4X3_TC1_IfcFaceSurface_type,
    IFC4X3_TC1_IfcFacetedBrep_type,
    IFC4X3_TC1_IfcFacetedBrepWithVoids_type,
    IFC4X3_TC1_IfcFacility_type,
    IFC4X3_TC1_IfcFacilityPart_type,
    IFC4X3_TC1_IfcFacilityPartCommon_type,
    IFC4X3_TC1_IfcFacilityPartCommonTypeEnum_type,
    IFC4X3_TC1_IfcFacilityUsageEnum_type,
    IFC4X3_TC1_IfcFailureConnectionCondition_type,
    IFC4X3_TC1_IfcFan_type,
    IFC4X3_TC1_IfcFanType_type,
    IFC4X3_TC1_IfcFanTypeEnum_type,
    IFC4X3_TC1_IfcFastener_type,
    IFC4X3_TC1_IfcFastenerType_type,
    IFC4X3_TC1_IfcFastenerTypeEnum_type,
    IFC4X3_TC1_IfcFeatureElement_type,
    IFC4X3_TC1_IfcFeatureElementAddition_type,
    IFC4X3_TC1_IfcFeatureElementSubtraction_type,
    IFC4X3_TC1_IfcFillAreaStyle_type,
    IFC4X3_TC1_IfcFillAreaStyleHatching_type,
    IFC4X3_TC1_IfcFillAreaStyleTiles_type,
    IFC4X3_TC1_IfcFillStyleSelect_type,
    IFC4X3_TC1_IfcFilter_type,
    IFC4X3_TC1_IfcFilterType_type,
    IFC4X3_TC1_IfcFilterTypeEnum_type,
    IFC4X3_TC1_IfcFireSuppressionTerminal_type,
    IFC4X3_TC1_IfcFireSuppressionTerminalType_type,
    IFC4X3_TC1_IfcFireSuppressionTerminalTypeEnum_type,
    IFC4X3_TC1_IfcFixedReferenceSweptAreaSolid_type,
    IFC4X3_TC1_IfcFlowController_type,
    IFC4X3_TC1_IfcFlowControllerType_type,
    IFC4X3_TC1_IfcFlowDirectionEnum_type,
    IFC4X3_TC1_IfcFlowFitting_type,
    IFC4X3_TC1_IfcFlowFittingType_type,
    IFC4X3_TC1_IfcFlowInstrument_type,
    IFC4X3_TC1_IfcFlowInstrumentType_type,
    IFC4X3_TC1_IfcFlowInstrumentTypeEnum_type,
    IFC4X3_TC1_IfcFlowMeter_type,
    IFC4X3_TC1_IfcFlowMeterType_type,
    IFC4X3_TC1_IfcFlowMeterTypeEnum_type,
    IFC4X3_TC1_IfcFlowMovingDevice_type,
    IFC4X3_TC1_IfcFlowMovingDeviceType_type,
    IFC4X3_TC1_IfcFlowSegment_type,
    IFC4X3_TC1_IfcFlowSegmentType_type,
    IFC4X3_TC1_IfcFlowStorageDevice_type,
    IFC4X3_TC1_IfcFlowStorageDeviceType_type,
    IFC4X3_TC1_IfcFlowTerminal_type,
    IFC4X3_TC1_IfcFlowTerminalType_type,
    IFC4X3_TC1_IfcFlowTreatmentDevice_type,
    IFC4X3_TC1_IfcFlowTreatmentDeviceType_type,
    IFC4X3_TC1_IfcFontStyle_type,
    IFC4X3_TC1_IfcFontVariant_type,
    IFC4X3_TC1_IfcFontWeight_type,
    IFC4X3_TC1_IfcFooting_type,
    IFC4X3_TC1_IfcFootingType_type,
    IFC4X3_TC1_IfcFootingTypeEnum_type,
    IFC4X3_TC1_IfcForceMeasure_type,
    IFC4X3_TC1_IfcFrequencyMeasure_type,
    IFC4X3_TC1_IfcFurnishingElement_type,
    IFC4X3_TC1_IfcFurnishingElementType_type,
    IFC4X3_TC1_IfcFurniture_type,
    IFC4X3_TC1_IfcFurnitureType_type,
    IFC4X3_TC1_IfcFurnitureTypeEnum_type,
    IFC4X3_TC1_IfcGeographicElement_type,
    IFC4X3_TC1_IfcGeographicElementType_type,
    IFC4X3_TC1_IfcGeographicElementTypeEnum_type,
    IFC4X3_TC1_IfcGeometricCurveSet_type,
    IFC4X3_TC1_IfcGeometricProjectionEnum_type,
    IFC4X3_TC1_IfcGeometricRepresentationContext_type,
    IFC4X3_TC1_IfcGeometricRepresentationItem_type,
    IFC4X3_TC1_IfcGeometricRepresentationSubContext_type,
    IFC4X3_TC1_IfcGeometricSet_type,
    IFC4X3_TC1_IfcGeometricSetSelect_type,
    IFC4X3_TC1_IfcGeomodel_type,
    IFC4X3_TC1_IfcGeoslice_type,
    IFC4X3_TC1_IfcGeotechnicalAssembly_type,
    IFC4X3_TC1_IfcGeotechnicalElement_type,
    IFC4X3_TC1_IfcGeotechnicalStratum_type,
    IFC4X3_TC1_IfcGeotechnicalStratumTypeEnum_type,
    IFC4X3_TC1_IfcGloballyUniqueId_type,
    IFC4X3_TC1_IfcGlobalOrLocalEnum_type,
    IFC4X3_TC1_IfcGradientCurve_type,
    IFC4X3_TC1_IfcGrid_type,
    IFC4X3_TC1_IfcGridAxis_type,
    IFC4X3_TC1_IfcGridPlacement_type,
    IFC4X3_TC1_IfcGridPlacementDirectionSelect_type,
    IFC4X3_TC1_IfcGridTypeEnum_type,
    IFC4X3_TC1_IfcGroup_type,
    IFC4X3_TC1_IfcHalfSpaceSolid_type,
    IFC4X3_TC1_IfcHatchLineDistanceSelect_type,
    IFC4X3_TC1_IfcHeatExchanger_type,
    IFC4X3_TC1_IfcHeatExchangerType_type,
    IFC4X3_TC1_IfcHeatExchangerTypeEnum_type,
    IFC4X3_TC1_IfcHeatFluxDensityMeasure_type,
    IFC4X3_TC1_IfcHeatingValueMeasure_type,
    IFC4X3_TC1_IfcHumidifier_type,
    IFC4X3_TC1_IfcHumidifierType_type,
    IFC4X3_TC1_IfcHumidifierTypeEnum_type,
    IFC4X3_TC1_IfcIdentifier_type,
    IFC4X3_TC1_IfcIlluminanceMeasure_type,
    IFC4X3_TC1_IfcImageTexture_type,
    IFC4X3_TC1_IfcImpactProtectionDevice_type,
    IFC4X3_TC1_IfcImpactProtectionDeviceType_type,
    IFC4X3_TC1_IfcImpactProtectionDeviceTypeEnum_type,
    IFC4X3_TC1_IfcIndexedColourMap_type,
    IFC4X3_TC1_IfcIndexedPolyCurve_type,
    IFC4X3_TC1_IfcIndexedPolygonalFace_type,
    IFC4X3_TC1_IfcIndexedPolygonalFaceWithVoids_type,
    IFC4X3_TC1_IfcIndexedPolygonalTextureMap_type,
    IFC4X3_TC1_IfcIndexedTextureMap_type,
    IFC4X3_TC1_IfcIndexedTriangleTextureMap_type,
    IFC4X3_TC1_IfcInductanceMeasure_type,
    IFC4X3_TC1_IfcInteger_type,
    IFC4X3_TC1_IfcIntegerCountRateMeasure_type,
    IFC4X3_TC1_IfcInterceptor_type,
    IFC4X3_TC1_IfcInterceptorType_type,
    IFC4X3_TC1_IfcInterceptorTypeEnum_type,
    IFC4X3_TC1_IfcInterferenceSelect_type,
    IFC4X3_TC1_IfcInternalOrExternalEnum_type,
    IFC4X3_TC1_IfcIntersectionCurve_type,
    IFC4X3_TC1_IfcInventory_type,
    IFC4X3_TC1_IfcInventoryTypeEnum_type,
    IFC4X3_TC1_IfcIonConcentrationMeasure_type,
    IFC4X3_TC1_IfcIrregularTimeSeries_type,
    IFC4X3_TC1_IfcIrregularTimeSeriesValue_type,
    IFC4X3_TC1_IfcIShapeProfileDef_type,
    IFC4X3_TC1_IfcIsothermalMoistureCapacityMeasure_type,
    IFC4X3_TC1_IfcJunctionBox_type,
    IFC4X3_TC1_IfcJunctionBoxType_type,
    IFC4X3_TC1_IfcJunctionBoxTypeEnum_type,
    IFC4X3_TC1_IfcKerb_type,
    IFC4X3_TC1_IfcKerbType_type,
    IFC4X3_TC1_IfcKerbTypeEnum_type,
    IFC4X3_TC1_IfcKinematicViscosityMeasure_type,
    IFC4X3_TC1_IfcKnotType_type,
    IFC4X3_TC1_IfcLabel_type,
    IFC4X3_TC1_IfcLaborResource_type,
    IFC4X3_TC1_IfcLaborResourceType_type,
    IFC4X3_TC1_IfcLaborResourceTypeEnum_type,
    IFC4X3_TC1_IfcLagTime_type,
    IFC4X3_TC1_IfcLamp_type,
    IFC4X3_TC1_IfcLampType_type,
    IFC4X3_TC1_IfcLampTypeEnum_type,
    IFC4X3_TC1_IfcLanguageId_type,
    IFC4X3_TC1_IfcLayeredItem_type,
    IFC4X3_TC1_IfcLayerSetDirectionEnum_type,
    IFC4X3_TC1_IfcLengthMeasure_type,
    IFC4X3_TC1_IfcLibraryInformation_type,
    IFC4X3_TC1_IfcLibraryReference_type,
    IFC4X3_TC1_IfcLibrarySelect_type,
    IFC4X3_TC1_IfcLightDistributionCurveEnum_type,
    IFC4X3_TC1_IfcLightDistributionData_type,
    IFC4X3_TC1_IfcLightDistributionDataSourceSelect_type,
    IFC4X3_TC1_IfcLightEmissionSourceEnum_type,
    IFC4X3_TC1_IfcLightFixture_type,
    IFC4X3_TC1_IfcLightFixtureType_type,
    IFC4X3_TC1_IfcLightFixtureTypeEnum_type,
    IFC4X3_TC1_IfcLightIntensityDistribution_type,
    IFC4X3_TC1_IfcLightSource_type,
    IFC4X3_TC1_IfcLightSourceAmbient_type,
    IFC4X3_TC1_IfcLightSourceDirectional_type,
    IFC4X3_TC1_IfcLightSourceGoniometric_type,
    IFC4X3_TC1_IfcLightSourcePositional_type,
    IFC4X3_TC1_IfcLightSourceSpot_type,
    IFC4X3_TC1_IfcLine_type,
    IFC4X3_TC1_IfcLinearElement_type,
    IFC4X3_TC1_IfcLinearForceMeasure_type,
    IFC4X3_TC1_IfcLinearMomentMeasure_type,
    IFC4X3_TC1_IfcLinearPlacement_type,
    IFC4X3_TC1_IfcLinearPositioningElement_type,
    IFC4X3_TC1_IfcLinearStiffnessMeasure_type,
    IFC4X3_TC1_IfcLinearVelocityMeasure_type,
    IFC4X3_TC1_IfcLineIndex_type,
    IFC4X3_TC1_IfcLiquidTerminal_type,
    IFC4X3_TC1_IfcLiquidTerminalType_type,
    IFC4X3_TC1_IfcLiquidTerminalTypeEnum_type,
    IFC4X3_TC1_IfcLoadGroupTypeEnum_type,
    IFC4X3_TC1_IfcLocalPlacement_type,
    IFC4X3_TC1_IfcLogical_type,
    IFC4X3_TC1_IfcLogicalOperatorEnum_type,
    IFC4X3_TC1_IfcLoop_type,
    IFC4X3_TC1_IfcLShapeProfileDef_type,
    IFC4X3_TC1_IfcLuminousFluxMeasure_type,
    IFC4X3_TC1_IfcLuminousIntensityDistributionMeasure_type,
    IFC4X3_TC1_IfcLuminousIntensityMeasure_type,
    IFC4X3_TC1_IfcMagneticFluxDensityMeasure_type,
    IFC4X3_TC1_IfcMagneticFluxMeasure_type,
    IFC4X3_TC1_IfcManifoldSolidBrep_type,
    IFC4X3_TC1_IfcMapConversion_type,
    IFC4X3_TC1_IfcMappedItem_type,
    IFC4X3_TC1_IfcMarineFacility_type,
    IFC4X3_TC1_IfcMarineFacilityTypeEnum_type,
    IFC4X3_TC1_IfcMarinePart_type,
    IFC4X3_TC1_IfcMarinePartTypeEnum_type,
    IFC4X3_TC1_IfcMassDensityMeasure_type,
    IFC4X3_TC1_IfcMassFlowRateMeasure_type,
    IFC4X3_TC1_IfcMassMeasure_type,
    IFC4X3_TC1_IfcMassPerLengthMeasure_type,
    IFC4X3_TC1_IfcMaterial_type,
    IFC4X3_TC1_IfcMaterialClassificationRelationship_type,
    IFC4X3_TC1_IfcMaterialConstituent_type,
    IFC4X3_TC1_IfcMaterialConstituentSet_type,
    IFC4X3_TC1_IfcMaterialDefinition_type,
    IFC4X3_TC1_IfcMaterialDefinitionRepresentation_type,
    IFC4X3_TC1_IfcMaterialLayer_type,
    IFC4X3_TC1_IfcMaterialLayerSet_type,
    IFC4X3_TC1_IfcMaterialLayerSetUsage_type,
    IFC4X3_TC1_IfcMaterialLayerWithOffsets_type,
    IFC4X3_TC1_IfcMaterialList_type,
    IFC4X3_TC1_IfcMaterialProfile_type,
    IFC4X3_TC1_IfcMaterialProfileSet_type,
    IFC4X3_TC1_IfcMaterialProfileSetUsage_type,
    IFC4X3_TC1_IfcMaterialProfileSetUsageTapering_type,
    IFC4X3_TC1_IfcMaterialProfileWithOffsets_type,
    IFC4X3_TC1_IfcMaterialProperties_type,
    IFC4X3_TC1_IfcMaterialRelationship_type,
    IFC4X3_TC1_IfcMaterialSelect_type,
    IFC4X3_TC1_IfcMaterialUsageDefinition_type,
    IFC4X3_TC1_IfcMeasureValue_type,
    IFC4X3_TC1_IfcMeasureWithUnit_type,
    IFC4X3_TC1_IfcMechanicalFastener_type,
    IFC4X3_TC1_IfcMechanicalFastenerType_type,
    IFC4X3_TC1_IfcMechanicalFastenerTypeEnum_type,
    IFC4X3_TC1_IfcMedicalDevice_type,
    IFC4X3_TC1_IfcMedicalDeviceType_type,
    IFC4X3_TC1_IfcMedicalDeviceTypeEnum_type,
    IFC4X3_TC1_IfcMember_type,
    IFC4X3_TC1_IfcMemberType_type,
    IFC4X3_TC1_IfcMemberTypeEnum_type,
    IFC4X3_TC1_IfcMetric_type,
    IFC4X3_TC1_IfcMetricValueSelect_type,
    IFC4X3_TC1_IfcMirroredProfileDef_type,
    IFC4X3_TC1_IfcMobileTelecommunicationsAppliance_type,
    IFC4X3_TC1_IfcMobileTelecommunicationsApplianceType_type,
    IFC4X3_TC1_IfcMobileTelecommunicationsApplianceTypeEnum_type,
    IFC4X3_TC1_IfcModulusOfElasticityMeasure_type,
    IFC4X3_TC1_IfcModulusOfLinearSubgradeReactionMeasure_type,
    IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionMeasure_type,
    IFC4X3_TC1_IfcModulusOfRotationalSubgradeReactionSelect_type,
    IFC4X3_TC1_IfcModulusOfSubgradeReactionMeasure_type,
    IFC4X3_TC1_IfcModulusOfSubgradeReactionSelect_type,
    IFC4X3_TC1_IfcModulusOfTranslationalSubgradeReactionSelect_type,
    IFC4X3_TC1_IfcMoistureDiffusivityMeasure_type,
    IFC4X3_TC1_IfcMolecularWeightMeasure_type,
    IFC4X3_TC1_IfcMomentOfInertiaMeasure_type,
    IFC4X3_TC1_IfcMonetaryMeasure_type,
    IFC4X3_TC1_IfcMonetaryUnit_type,
    IFC4X3_TC1_IfcMonthInYearNumber_type,
    IFC4X3_TC1_IfcMooringDevice_type,
    IFC4X3_TC1_IfcMooringDeviceType_type,
    IFC4X3_TC1_IfcMooringDeviceTypeEnum_type,
    IFC4X3_TC1_IfcMotorConnection_type,
    IFC4X3_TC1_IfcMotorConnectionType_type,
    IFC4X3_TC1_IfcMotorConnectionTypeEnum_type,
    IFC4X3_TC1_IfcNamedUnit_type,
    IFC4X3_TC1_IfcNavigationElement_type,
    IFC4X3_TC1_IfcNavigationElementType_type,
    IFC4X3_TC1_IfcNavigationElementTypeEnum_type,
    IFC4X3_TC1_IfcNonNegativeLengthMeasure_type,
    IFC4X3_TC1_IfcNormalisedRatioMeasure_type,
    IFC4X3_TC1_IfcNumericMeasure_type,
    IFC4X3_TC1_IfcObject_type,
    IFC4X3_TC1_IfcObjectDefinition_type,
    IFC4X3_TC1_IfcObjective_type,
    IFC4X3_TC1_IfcObjectiveEnum_type,
    IFC4X3_TC1_IfcObjectPlacement_type,
    IFC4X3_TC1_IfcObjectReferenceSelect_type,
    IFC4X3_TC1_IfcOccupant_type,
    IFC4X3_TC1_IfcOccupantTypeEnum_type,
    IFC4X3_TC1_IfcOffsetCurve_type,
    IFC4X3_TC1_IfcOffsetCurve2D_type,
    IFC4X3_TC1_IfcOffsetCurve3D_type,
    IFC4X3_TC1_IfcOffsetCurveByDistances_type,
    IFC4X3_TC1_IfcOpenCrossProfileDef_type,
    IFC4X3_TC1_IfcOpeningElement_type,
    IFC4X3_TC1_IfcOpeningElementTypeEnum_type,
    IFC4X3_TC1_IfcOpenShell_type,
    IFC4X3_TC1_IfcOrganization_type,
    IFC4X3_TC1_IfcOrganizationRelationship_type,
    IFC4X3_TC1_IfcOrientedEdge_type,
    IFC4X3_TC1_IfcOuterBoundaryCurve_type,
    IFC4X3_TC1_IfcOutlet_type,
    IFC4X3_TC1_IfcOutletType_type,
    IFC4X3_TC1_IfcOutletTypeEnum_type,
    IFC4X3_TC1_IfcOwnerHistory_type,
    IFC4X3_TC1_IfcParameterizedProfileDef_type,
    IFC4X3_TC1_IfcParameterValue_type,
    IFC4X3_TC1_IfcPath_type,
    IFC4X3_TC1_IfcPavement_type,
    IFC4X3_TC1_IfcPavementType_type,
    IFC4X3_TC1_IfcPavementTypeEnum_type,
    IFC4X3_TC1_IfcPcurve_type,
    IFC4X3_TC1_IfcPerformanceHistory_type,
    IFC4X3_TC1_IfcPerformanceHistoryTypeEnum_type,
    IFC4X3_TC1_IfcPermeableCoveringOperationEnum_type,
    IFC4X3_TC1_IfcPermeableCoveringProperties_type,
    IFC4X3_TC1_IfcPermit_type,
    IFC4X3_TC1_IfcPermitTypeEnum_type,
    IFC4X3_TC1_IfcPerson_type,
    IFC4X3_TC1_IfcPersonAndOrganization_type,
    IFC4X3_TC1_IfcPHMeasure_type,
    IFC4X3_TC1_IfcPhysicalComplexQuantity_type,
    IFC4X3_TC1_IfcPhysicalOrVirtualEnum_type,
    IFC4X3_TC1_IfcPhysicalQuantity_type,
    IFC4X3_TC1_IfcPhysicalSimpleQuantity_type,
    IFC4X3_TC1_IfcPile_type,
    IFC4X3_TC1_IfcPileConstructionEnum_type,
    IFC4X3_TC1_IfcPileType_type,
    IFC4X3_TC1_IfcPileTypeEnum_type,
    IFC4X3_TC1_IfcPipeFitting_type,
    IFC4X3_TC1_IfcPipeFittingType_type,
    IFC4X3_TC1_IfcPipeFittingTypeEnum_type,
    IFC4X3_TC1_IfcPipeSegment_type,
    IFC4X3_TC1_IfcPipeSegmentType_type,
    IFC4X3_TC1_IfcPipeSegmentTypeEnum_type,
    IFC4X3_TC1_IfcPixelTexture_type,
    IFC4X3_TC1_IfcPlacement_type,
    IFC4X3_TC1_IfcPlanarBox_type,
    IFC4X3_TC1_IfcPlanarExtent_type,
    IFC4X3_TC1_IfcPlanarForceMeasure_type,
    IFC4X3_TC1_IfcPlane_type,
    IFC4X3_TC1_IfcPlaneAngleMeasure_type,
    IFC4X3_TC1_IfcPlate_type,
    IFC4X3_TC1_IfcPlateType_type,
    IFC4X3_TC1_IfcPlateTypeEnum_type,
    IFC4X3_TC1_IfcPoint_type,
    IFC4X3_TC1_IfcPointByDistanceExpression_type,
    IFC4X3_TC1_IfcPointOnCurve_type,
    IFC4X3_TC1_IfcPointOnSurface_type,
    IFC4X3_TC1_IfcPointOrVertexPoint_type,
    IFC4X3_TC1_IfcPolygonalBoundedHalfSpace_type,
    IFC4X3_TC1_IfcPolygonalFaceSet_type,
    IFC4X3_TC1_IfcPolyline_type,
    IFC4X3_TC1_IfcPolyLoop_type,
    IFC4X3_TC1_IfcPolynomialCurve_type,
    IFC4X3_TC1_IfcPort_type,
    IFC4X3_TC1_IfcPositioningElement_type,
    IFC4X3_TC1_IfcPositiveInteger_type,
    IFC4X3_TC1_IfcPositiveLengthMeasure_type,
    IFC4X3_TC1_IfcPositivePlaneAngleMeasure_type,
    IFC4X3_TC1_IfcPositiveRatioMeasure_type,
    IFC4X3_TC1_IfcPostalAddress_type,
    IFC4X3_TC1_IfcPowerMeasure_type,
    IFC4X3_TC1_IfcPreDefinedColour_type,
    IFC4X3_TC1_IfcPreDefinedCurveFont_type,
    IFC4X3_TC1_IfcPreDefinedItem_type,
    IFC4X3_TC1_IfcPreDefinedProperties_type,
    IFC4X3_TC1_IfcPreDefinedPropertySet_type,
    IFC4X3_TC1_IfcPreDefinedTextFont_type,
    IFC4X3_TC1_IfcPreferredSurfaceCurveRepresentation_type,
    IFC4X3_TC1_IfcPresentableText_type,
    IFC4X3_TC1_IfcPresentationItem_type,
    IFC4X3_TC1_IfcPresentationLayerAssignment_type,
    IFC4X3_TC1_IfcPresentationLayerWithStyle_type,
    IFC4X3_TC1_IfcPresentationStyle_type,
    IFC4X3_TC1_IfcPressureMeasure_type,
    IFC4X3_TC1_IfcProcedure_type,
    IFC4X3_TC1_IfcProcedureType_type,
    IFC4X3_TC1_IfcProcedureTypeEnum_type,
    IFC4X3_TC1_IfcProcess_type,
    IFC4X3_TC1_IfcProcessSelect_type,
    IFC4X3_TC1_IfcProduct_type,
    IFC4X3_TC1_IfcProductDefinitionShape_type,
    IFC4X3_TC1_IfcProductRepresentation_type,
    IFC4X3_TC1_IfcProductRepresentationSelect_type,
    IFC4X3_TC1_IfcProductSelect_type,
    IFC4X3_TC1_IfcProfileDef_type,
    IFC4X3_TC1_IfcProfileProperties_type,
    IFC4X3_TC1_IfcProfileTypeEnum_type,
    IFC4X3_TC1_IfcProject_type,
    IFC4X3_TC1_IfcProjectedCRS_type,
    IFC4X3_TC1_IfcProjectedOrTrueLengthEnum_type,
    IFC4X3_TC1_IfcProjectionElement_type,
    IFC4X3_TC1_IfcProjectionElementTypeEnum_type,
    IFC4X3_TC1_IfcProjectLibrary_type,
    IFC4X3_TC1_IfcProjectOrder_type,
    IFC4X3_TC1_IfcProjectOrderTypeEnum_type,
    IFC4X3_TC1_IfcProperty_type,
    IFC4X3_TC1_IfcPropertyAbstraction_type,
    IFC4X3_TC1_IfcPropertyBoundedValue_type,
    IFC4X3_TC1_IfcPropertyDefinition_type,
    IFC4X3_TC1_IfcPropertyDependencyRelationship_type,
    IFC4X3_TC1_IfcPropertyEnumeratedValue_type,
    IFC4X3_TC1_IfcPropertyEnumeration_type,
    IFC4X3_TC1_IfcPropertyListValue_type,
    IFC4X3_TC1_IfcPropertyReferenceValue_type,
    IFC4X3_TC1_IfcPropertySet_type,
    IFC4X3_TC1_IfcPropertySetDefinition_type,
    IFC4X3_TC1_IfcPropertySetDefinitionSelect_type,
    IFC4X3_TC1_IfcPropertySetDefinitionSet_type,
    IFC4X3_TC1_IfcPropertySetTemplate_type,
    IFC4X3_TC1_IfcPropertySetTemplateTypeEnum_type,
    IFC4X3_TC1_IfcPropertySingleValue_type,
    IFC4X3_TC1_IfcPropertyTableValue_type,
    IFC4X3_TC1_IfcPropertyTemplate_type,
    IFC4X3_TC1_IfcPropertyTemplateDefinition_type,
    IFC4X3_TC1_IfcProtectiveDevice_type,
    IFC4X3_TC1_IfcProtectiveDeviceTrippingUnit_type,
    IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitType_type,
    IFC4X3_TC1_IfcProtectiveDeviceTrippingUnitTypeEnum_type,
    IFC4X3_TC1_IfcProtectiveDeviceType_type,
    IFC4X3_TC1_IfcProtectiveDeviceTypeEnum_type,
    IFC4X3_TC1_IfcPump_type,
    IFC4X3_TC1_IfcPumpType_type,
    IFC4X3_TC1_IfcPumpTypeEnum_type,
    IFC4X3_TC1_IfcQuantityArea_type,
    IFC4X3_TC1_IfcQuantityCount_type,
    IFC4X3_TC1_IfcQuantityLength_type,
    IFC4X3_TC1_IfcQuantityNumber_type,
    IFC4X3_TC1_IfcQuantitySet_type,
    IFC4X3_TC1_IfcQuantityTime_type,
    IFC4X3_TC1_IfcQuantityVolume_type,
    IFC4X3_TC1_IfcQuantityWeight_type,
    IFC4X3_TC1_IfcRadioActivityMeasure_type,
    IFC4X3_TC1_IfcRail_type,
    IFC4X3_TC1_IfcRailing_type,
    IFC4X3_TC1_IfcRailingType_type,
    IFC4X3_TC1_IfcRailingTypeEnum_type,
    IFC4X3_TC1_IfcRailType_type,
    IFC4X3_TC1_IfcRailTypeEnum_type,
    IFC4X3_TC1_IfcRailway_type,
    IFC4X3_TC1_IfcRailwayPart_type,
    IFC4X3_TC1_IfcRailwayPartTypeEnum_type,
    IFC4X3_TC1_IfcRailwayTypeEnum_type,
    IFC4X3_TC1_IfcRamp_type,
    IFC4X3_TC1_IfcRampFlight_type,
    IFC4X3_TC1_IfcRampFlightType_type,
    IFC4X3_TC1_IfcRampFlightTypeEnum_type,
    IFC4X3_TC1_IfcRampType_type,
    IFC4X3_TC1_IfcRampTypeEnum_type,
    IFC4X3_TC1_IfcRatioMeasure_type,
    IFC4X3_TC1_IfcRationalBSplineCurveWithKnots_type,
    IFC4X3_TC1_IfcRationalBSplineSurfaceWithKnots_type,
    IFC4X3_TC1_IfcReal_type,
    IFC4X3_TC1_IfcRectangleHollowProfileDef_type,
    IFC4X3_TC1_IfcRectangleProfileDef_type,
    IFC4X3_TC1_IfcRectangularPyramid_type,
    IFC4X3_TC1_IfcRectangularTrimmedSurface_type,
    IFC4X3_TC1_IfcRecurrencePattern_type,
    IFC4X3_TC1_IfcRecurrenceTypeEnum_type,
    IFC4X3_TC1_IfcReference_type,
    IFC4X3_TC1_IfcReferent_type,
    IFC4X3_TC1_IfcReferentTypeEnum_type,
    IFC4X3_TC1_IfcReflectanceMethodEnum_type,
    IFC4X3_TC1_IfcRegularTimeSeries_type,
    IFC4X3_TC1_IfcReinforcedSoil_type,
    IFC4X3_TC1_IfcReinforcedSoilTypeEnum_type,
    IFC4X3_TC1_IfcReinforcementBarProperties_type,
    IFC4X3_TC1_IfcReinforcementDefinitionProperties_type,
    IFC4X3_TC1_IfcReinforcingBar_type,
    IFC4X3_TC1_IfcReinforcingBarRoleEnum_type,
    IFC4X3_TC1_IfcReinforcingBarSurfaceEnum_type,
    IFC4X3_TC1_IfcReinforcingBarType_type,
    IFC4X3_TC1_IfcReinforcingBarTypeEnum_type,
    IFC4X3_TC1_IfcReinforcingElement_type,
    IFC4X3_TC1_IfcReinforcingElementType_type,
    IFC4X3_TC1_IfcReinforcingMesh_type,
    IFC4X3_TC1_IfcReinforcingMeshType_type,
    IFC4X3_TC1_IfcReinforcingMeshTypeEnum_type,
    IFC4X3_TC1_IfcRelAdheresToElement_type,
    IFC4X3_TC1_IfcRelAggregates_type,
    IFC4X3_TC1_IfcRelAssigns_type,
    IFC4X3_TC1_IfcRelAssignsToActor_type,
    IFC4X3_TC1_IfcRelAssignsToControl_type,
    IFC4X3_TC1_IfcRelAssignsToGroup_type,
    IFC4X3_TC1_IfcRelAssignsToGroupByFactor_type,
    IFC4X3_TC1_IfcRelAssignsToProcess_type,
    IFC4X3_TC1_IfcRelAssignsToProduct_type,
    IFC4X3_TC1_IfcRelAssignsToResource_type,
    IFC4X3_TC1_IfcRelAssociates_type,
    IFC4X3_TC1_IfcRelAssociatesApproval_type,
    IFC4X3_TC1_IfcRelAssociatesClassification_type,
    IFC4X3_TC1_IfcRelAssociatesConstraint_type,
    IFC4X3_TC1_IfcRelAssociatesDocument_type,
    IFC4X3_TC1_IfcRelAssociatesLibrary_type,
    IFC4X3_TC1_IfcRelAssociatesMaterial_type,
    IFC4X3_TC1_IfcRelAssociatesProfileDef_type,
    IFC4X3_TC1_IfcRelationship_type,
    IFC4X3_TC1_IfcRelConnects_type,
    IFC4X3_TC1_IfcRelConnectsElements_type,
    IFC4X3_TC1_IfcRelConnectsPathElements_type,
    IFC4X3_TC1_IfcRelConnectsPorts_type,
    IFC4X3_TC1_IfcRelConnectsPortToElement_type,
    IFC4X3_TC1_IfcRelConnectsStructuralActivity_type,
    IFC4X3_TC1_IfcRelConnectsStructuralMember_type,
    IFC4X3_TC1_IfcRelConnectsWithEccentricity_type,
    IFC4X3_TC1_IfcRelConnectsWithRealizingElements_type,
    IFC4X3_TC1_IfcRelContainedInSpatialStructure_type,
    IFC4X3_TC1_IfcRelCoversBldgElements_type,
    IFC4X3_TC1_IfcRelCoversSpaces_type,
    IFC4X3_TC1_IfcRelDeclares_type,
    IFC4X3_TC1_IfcRelDecomposes_type,
    IFC4X3_TC1_IfcRelDefines_type,
    IFC4X3_TC1_IfcRelDefinesByObject_type,
    IFC4X3_TC1_IfcRelDefinesByProperties_type,
    IFC4X3_TC1_IfcRelDefinesByTemplate_type,
    IFC4X3_TC1_IfcRelDefinesByType_type,
    IFC4X3_TC1_IfcRelFillsElement_type,
    IFC4X3_TC1_IfcRelFlowControlElements_type,
    IFC4X3_TC1_IfcRelInterferesElements_type,
    IFC4X3_TC1_IfcRelNests_type,
    IFC4X3_TC1_IfcRelPositions_type,
    IFC4X3_TC1_IfcRelProjectsElement_type,
    IFC4X3_TC1_IfcRelReferencedInSpatialStructure_type,
    IFC4X3_TC1_IfcRelSequence_type,
    IFC4X3_TC1_IfcRelServicesBuildings_type,
    IFC4X3_TC1_IfcRelSpaceBoundary_type,
    IFC4X3_TC1_IfcRelSpaceBoundary1stLevel_type,
    IFC4X3_TC1_IfcRelSpaceBoundary2ndLevel_type,
    IFC4X3_TC1_IfcRelVoidsElement_type,
    IFC4X3_TC1_IfcReparametrisedCompositeCurveSegment_type,
    IFC4X3_TC1_IfcRepresentation_type,
    IFC4X3_TC1_IfcRepresentationContext_type,
    IFC4X3_TC1_IfcRepresentationItem_type,
    IFC4X3_TC1_IfcRepresentationMap_type,
    IFC4X3_TC1_IfcResource_type,
    IFC4X3_TC1_IfcResourceApprovalRelationship_type,
    IFC4X3_TC1_IfcResourceConstraintRelationship_type,
    IFC4X3_TC1_IfcResourceLevelRelationship_type,
    IFC4X3_TC1_IfcResourceObjectSelect_type,
    IFC4X3_TC1_IfcResourceSelect_type,
    IFC4X3_TC1_IfcResourceTime_type,
    IFC4X3_TC1_IfcRevolvedAreaSolid_type,
    IFC4X3_TC1_IfcRevolvedAreaSolidTapered_type,
    IFC4X3_TC1_IfcRightCircularCone_type,
    IFC4X3_TC1_IfcRightCircularCylinder_type,
    IFC4X3_TC1_IfcRoad_type,
    IFC4X3_TC1_IfcRoadPart_type,
    IFC4X3_TC1_IfcRoadPartTypeEnum_type,
    IFC4X3_TC1_IfcRoadTypeEnum_type,
    IFC4X3_TC1_IfcRoleEnum_type,
    IFC4X3_TC1_IfcRoof_type,
    IFC4X3_TC1_IfcRoofType_type,
    IFC4X3_TC1_IfcRoofTypeEnum_type,
    IFC4X3_TC1_IfcRoot_type,
    IFC4X3_TC1_IfcRotationalFrequencyMeasure_type,
    IFC4X3_TC1_IfcRotationalMassMeasure_type,
    IFC4X3_TC1_IfcRotationalStiffnessMeasure_type,
    IFC4X3_TC1_IfcRotationalStiffnessSelect_type,
    IFC4X3_TC1_IfcRoundedRectangleProfileDef_type,
    IFC4X3_TC1_IfcSanitaryTerminal_type,
    IFC4X3_TC1_IfcSanitaryTerminalType_type,
    IFC4X3_TC1_IfcSanitaryTerminalTypeEnum_type,
    IFC4X3_TC1_IfcSchedulingTime_type,
    IFC4X3_TC1_IfcSeamCurve_type,
    IFC4X3_TC1_IfcSecondOrderPolynomialSpiral_type,
    IFC4X3_TC1_IfcSectionalAreaIntegralMeasure_type,
    IFC4X3_TC1_IfcSectionedSolid_type,
    IFC4X3_TC1_IfcSectionedSolidHorizontal_type,
    IFC4X3_TC1_IfcSectionedSpine_type,
    IFC4X3_TC1_IfcSectionedSurface_type,
    IFC4X3_TC1_IfcSectionModulusMeasure_type,
    IFC4X3_TC1_IfcSectionProperties_type,
    IFC4X3_TC1_IfcSectionReinforcementProperties_type,
    IFC4X3_TC1_IfcSectionTypeEnum_type,
    IFC4X3_TC1_IfcSegment_type,
    IFC4X3_TC1_IfcSegmentedReferenceCurve_type,
    IFC4X3_TC1_IfcSegmentIndexSelect_type,
    IFC4X3_TC1_IfcSensor_type,
    IFC4X3_TC1_IfcSensorType_type,
    IFC4X3_TC1_IfcSensorTypeEnum_type,
    IFC4X3_TC1_IfcSequenceEnum_type,
    IFC4X3_TC1_IfcSeventhOrderPolynomialSpiral_type,
    IFC4X3_TC1_IfcShadingDevice_type,
    IFC4X3_TC1_IfcShadingDeviceType_type,
    IFC4X3_TC1_IfcShadingDeviceTypeEnum_type,
    IFC4X3_TC1_IfcShapeAspect_type,
    IFC4X3_TC1_IfcShapeModel_type,
    IFC4X3_TC1_IfcShapeRepresentation_type,
    IFC4X3_TC1_IfcShearModulusMeasure_type,
    IFC4X3_TC1_IfcShell_type,
    IFC4X3_TC1_IfcShellBasedSurfaceModel_type,
    IFC4X3_TC1_IfcSign_type,
    IFC4X3_TC1_IfcSignal_type,
    IFC4X3_TC1_IfcSignalType_type,
    IFC4X3_TC1_IfcSignalTypeEnum_type,
    IFC4X3_TC1_IfcSignType_type,
    IFC4X3_TC1_IfcSignTypeEnum_type,
    IFC4X3_TC1_IfcSimpleProperty_type,
    IFC4X3_TC1_IfcSimplePropertyTemplate_type,
    IFC4X3_TC1_IfcSimplePropertyTemplateTypeEnum_type,
    IFC4X3_TC1_IfcSimpleValue_type,
    IFC4X3_TC1_IfcSineSpiral_type,
    IFC4X3_TC1_IfcSIPrefix_type,
    IFC4X3_TC1_IfcSite_type,
    IFC4X3_TC1_IfcSIUnit_type,
    IFC4X3_TC1_IfcSIUnitName_type,
    IFC4X3_TC1_IfcSizeSelect_type,
    IFC4X3_TC1_IfcSlab_type,
    IFC4X3_TC1_IfcSlabType_type,
    IFC4X3_TC1_IfcSlabTypeEnum_type,
    IFC4X3_TC1_IfcSlippageConnectionCondition_type,
    IFC4X3_TC1_IfcSolarDevice_type,
    IFC4X3_TC1_IfcSolarDeviceType_type,
    IFC4X3_TC1_IfcSolarDeviceTypeEnum_type,
    IFC4X3_TC1_IfcSolidAngleMeasure_type,
    IFC4X3_TC1_IfcSolidModel_type,
    IFC4X3_TC1_IfcSolidOrShell_type,
    IFC4X3_TC1_IfcSoundPowerLevelMeasure_type,
    IFC4X3_TC1_IfcSoundPowerMeasure_type,
    IFC4X3_TC1_IfcSoundPressureLevelMeasure_type,
    IFC4X3_TC1_IfcSoundPressureMeasure_type,
    IFC4X3_TC1_IfcSpace_type,
    IFC4X3_TC1_IfcSpaceBoundarySelect_type,
    IFC4X3_TC1_IfcSpaceHeater_type,
    IFC4X3_TC1_IfcSpaceHeaterType_type,
    IFC4X3_TC1_IfcSpaceHeaterTypeEnum_type,
    IFC4X3_TC1_IfcSpaceType_type,
    IFC4X3_TC1_IfcSpaceTypeEnum_type,
    IFC4X3_TC1_IfcSpatialElement_type,
    IFC4X3_TC1_IfcSpatialElementType_type,
    IFC4X3_TC1_IfcSpatialReferenceSelect_type,
    IFC4X3_TC1_IfcSpatialStructureElement_type,
    IFC4X3_TC1_IfcSpatialStructureElementType_type,
    IFC4X3_TC1_IfcSpatialZone_type,
    IFC4X3_TC1_IfcSpatialZoneType_type,
    IFC4X3_TC1_IfcSpatialZoneTypeEnum_type,
    IFC4X3_TC1_IfcSpecificHeatCapacityMeasure_type,
    IFC4X3_TC1_IfcSpecularExponent_type,
    IFC4X3_TC1_IfcSpecularHighlightSelect_type,
    IFC4X3_TC1_IfcSpecularRoughness_type,
    IFC4X3_TC1_IfcSphere_type,
    IFC4X3_TC1_IfcSphericalSurface_type,
    IFC4X3_TC1_IfcSpiral_type,
    IFC4X3_TC1_IfcStackTerminal_type,
    IFC4X3_TC1_IfcStackTerminalType_type,
    IFC4X3_TC1_IfcStackTerminalTypeEnum_type,
    IFC4X3_TC1_IfcStair_type,
    IFC4X3_TC1_IfcStairFlight_type,
    IFC4X3_TC1_IfcStairFlightType_type,
    IFC4X3_TC1_IfcStairFlightTypeEnum_type,
    IFC4X3_TC1_IfcStairType_type,
    IFC4X3_TC1_IfcStairTypeEnum_type,
    IFC4X3_TC1_IfcStateEnum_type,
    IFC4X3_TC1_IfcStrippedOptional_type,
    IFC4X3_TC1_IfcStructuralAction_type,
    IFC4X3_TC1_IfcStructuralActivity_type,
    IFC4X3_TC1_IfcStructuralActivityAssignmentSelect_type,
    IFC4X3_TC1_IfcStructuralAnalysisModel_type,
    IFC4X3_TC1_IfcStructuralConnection_type,
    IFC4X3_TC1_IfcStructuralConnectionCondition_type,
    IFC4X3_TC1_IfcStructuralCurveAction_type,
    IFC4X3_TC1_IfcStructuralCurveActivityTypeEnum_type,
    IFC4X3_TC1_IfcStructuralCurveConnection_type,
    IFC4X3_TC1_IfcStructuralCurveMember_type,
    IFC4X3_TC1_IfcStructuralCurveMemberTypeEnum_type,
    IFC4X3_TC1_IfcStructuralCurveMemberVarying_type,
    IFC4X3_TC1_IfcStructuralCurveReaction_type,
    IFC4X3_TC1_IfcStructuralItem_type,
    IFC4X3_TC1_IfcStructuralLinearAction_type,
    IFC4X3_TC1_IfcStructuralLoad_type,
    IFC4X3_TC1_IfcStructuralLoadCase_type,
    IFC4X3_TC1_IfcStructuralLoadConfiguration_type,
    IFC4X3_TC1_IfcStructuralLoadGroup_type,
    IFC4X3_TC1_IfcStructuralLoadLinearForce_type,
    IFC4X3_TC1_IfcStructuralLoadOrResult_type,
    IFC4X3_TC1_IfcStructuralLoadPlanarForce_type,
    IFC4X3_TC1_IfcStructuralLoadSingleDisplacement_type,
    IFC4X3_TC1_IfcStructuralLoadSingleDisplacementDistortion_type,
    IFC4X3_TC1_IfcStructuralLoadSingleForce_type,
    IFC4X3_TC1_IfcStructuralLoadSingleForceWarping_type,
    IFC4X3_TC1_IfcStructuralLoadStatic_type,
    IFC4X3_TC1_IfcStructuralLoadTemperature_type,
    IFC4X3_TC1_IfcStructuralMember_type,
    IFC4X3_TC1_IfcStructuralPlanarAction_type,
    IFC4X3_TC1_IfcStructuralPointAction_type,
    IFC4X3_TC1_IfcStructuralPointConnection_type,
    IFC4X3_TC1_IfcStructuralPointReaction_type,
    IFC4X3_TC1_IfcStructuralReaction_type,
    IFC4X3_TC1_IfcStructuralResultGroup_type,
    IFC4X3_TC1_IfcStructuralSurfaceAction_type,
    IFC4X3_TC1_IfcStructuralSurfaceActivityTypeEnum_type,
    IFC4X3_TC1_IfcStructuralSurfaceConnection_type,
    IFC4X3_TC1_IfcStructuralSurfaceMember_type,
    IFC4X3_TC1_IfcStructuralSurfaceMemberTypeEnum_type,
    IFC4X3_TC1_IfcStructuralSurfaceMemberVarying_type,
    IFC4X3_TC1_IfcStructuralSurfaceReaction_type,
    IFC4X3_TC1_IfcStyledItem_type,
    IFC4X3_TC1_IfcStyledRepresentation_type,
    IFC4X3_TC1_IfcStyleModel_type,
    IFC4X3_TC1_IfcSubContractResource_type,
    IFC4X3_TC1_IfcSubContractResourceType_type,
    IFC4X3_TC1_IfcSubContractResourceTypeEnum_type,
    IFC4X3_TC1_IfcSubedge_type,
    IFC4X3_TC1_IfcSurface_type,
    IFC4X3_TC1_IfcSurfaceCurve_type,
    IFC4X3_TC1_IfcSurfaceCurveSweptAreaSolid_type,
    IFC4X3_TC1_IfcSurfaceFeature_type,
    IFC4X3_TC1_IfcSurfaceFeatureTypeEnum_type,
    IFC4X3_TC1_IfcSurfaceOfLinearExtrusion_type,
    IFC4X3_TC1_IfcSurfaceOfRevolution_type,
    IFC4X3_TC1_IfcSurfaceOrFaceSurface_type,
    IFC4X3_TC1_IfcSurfaceReinforcementArea_type,
    IFC4X3_TC1_IfcSurfaceSide_type,
    IFC4X3_TC1_IfcSurfaceStyle_type,
    IFC4X3_TC1_IfcSurfaceStyleElementSelect_type,
    IFC4X3_TC1_IfcSurfaceStyleLighting_type,
    IFC4X3_TC1_IfcSurfaceStyleRefraction_type,
    IFC4X3_TC1_IfcSurfaceStyleRendering_type,
    IFC4X3_TC1_IfcSurfaceStyleShading_type,
    IFC4X3_TC1_IfcSurfaceStyleWithTextures_type,
    IFC4X3_TC1_IfcSurfaceTexture_type,
    IFC4X3_TC1_IfcSweptAreaSolid_type,
    IFC4X3_TC1_IfcSweptDiskSolid_type,
    IFC4X3_TC1_IfcSweptDiskSolidPolygonal_type,
    IFC4X3_TC1_IfcSweptSurface_type,
    IFC4X3_TC1_IfcSwitchingDevice_type,
    IFC4X3_TC1_IfcSwitchingDeviceType_type,
    IFC4X3_TC1_IfcSwitchingDeviceTypeEnum_type,
    IFC4X3_TC1_IfcSystem_type,
    IFC4X3_TC1_IfcSystemFurnitureElement_type,
    IFC4X3_TC1_IfcSystemFurnitureElementType_type,
    IFC4X3_TC1_IfcSystemFurnitureElementTypeEnum_type,
    IFC4X3_TC1_IfcTable_type,
    IFC4X3_TC1_IfcTableColumn_type,
    IFC4X3_TC1_IfcTableRow_type,
    IFC4X3_TC1_IfcTank_type,
    IFC4X3_TC1_IfcTankType_type,
    IFC4X3_TC1_IfcTankTypeEnum_type,
    IFC4X3_TC1_IfcTask_type,
    IFC4X3_TC1_IfcTaskDurationEnum_type,
    IFC4X3_TC1_IfcTaskTime_type,
    IFC4X3_TC1_IfcTaskTimeRecurring_type,
    IFC4X3_TC1_IfcTaskType_type,
    IFC4X3_TC1_IfcTaskTypeEnum_type,
    IFC4X3_TC1_IfcTelecomAddress_type,
    IFC4X3_TC1_IfcTemperatureGradientMeasure_type,
    IFC4X3_TC1_IfcTemperatureRateOfChangeMeasure_type,
    IFC4X3_TC1_IfcTendon_type,
    IFC4X3_TC1_IfcTendonAnchor_type,
    IFC4X3_TC1_IfcTendonAnchorType_type,
    IFC4X3_TC1_IfcTendonAnchorTypeEnum_type,
    IFC4X3_TC1_IfcTendonConduit_type,
    IFC4X3_TC1_IfcTendonConduitType_type,
    IFC4X3_TC1_IfcTendonConduitTypeEnum_type,
    IFC4X3_TC1_IfcTendonType_type,
    IFC4X3_TC1_IfcTendonTypeEnum_type,
    IFC4X3_TC1_IfcTessellatedFaceSet_type,
    IFC4X3_TC1_IfcTessellatedItem_type,
    IFC4X3_TC1_IfcText_type,
    IFC4X3_TC1_IfcTextAlignment_type,
    IFC4X3_TC1_IfcTextDecoration_type,
    IFC4X3_TC1_IfcTextFontName_type,
    IFC4X3_TC1_IfcTextFontSelect_type,
    IFC4X3_TC1_IfcTextLiteral_type,
    IFC4X3_TC1_IfcTextLiteralWithExtent_type,
    IFC4X3_TC1_IfcTextPath_type,
    IFC4X3_TC1_IfcTextStyle_type,
    IFC4X3_TC1_IfcTextStyleFontModel_type,
    IFC4X3_TC1_IfcTextStyleForDefinedFont_type,
    IFC4X3_TC1_IfcTextStyleTextModel_type,
    IFC4X3_TC1_IfcTextTransformation_type,
    IFC4X3_TC1_IfcTextureCoordinate_type,
    IFC4X3_TC1_IfcTextureCoordinateGenerator_type,
    IFC4X3_TC1_IfcTextureCoordinateIndices_type,
    IFC4X3_TC1_IfcTextureCoordinateIndicesWithVoids_type,
    IFC4X3_TC1_IfcTextureMap_type,
    IFC4X3_TC1_IfcTextureVertex_type,
    IFC4X3_TC1_IfcTextureVertexList_type,
    IFC4X3_TC1_IfcThermalAdmittanceMeasure_type,
    IFC4X3_TC1_IfcThermalConductivityMeasure_type,
    IFC4X3_TC1_IfcThermalExpansionCoefficientMeasure_type,
    IFC4X3_TC1_IfcThermalResistanceMeasure_type,
    IFC4X3_TC1_IfcThermalTransmittanceMeasure_type,
    IFC4X3_TC1_IfcThermodynamicTemperatureMeasure_type,
    IFC4X3_TC1_IfcThirdOrderPolynomialSpiral_type,
    IFC4X3_TC1_IfcTime_type,
    IFC4X3_TC1_IfcTimeMeasure_type,
    IFC4X3_TC1_IfcTimeOrRatioSelect_type,
    IFC4X3_TC1_IfcTimePeriod_type,
    IFC4X3_TC1_IfcTimeSeries_type,
    IFC4X3_TC1_IfcTimeSeriesDataTypeEnum_type,
    IFC4X3_TC1_IfcTimeSeriesValue_type,
    IFC4X3_TC1_IfcTimeStamp_type,
    IFC4X3_TC1_IfcTopologicalRepresentationItem_type,
    IFC4X3_TC1_IfcTopologyRepresentation_type,
    IFC4X3_TC1_IfcToroidalSurface_type,
    IFC4X3_TC1_IfcTorqueMeasure_type,
    IFC4X3_TC1_IfcTrackElement_type,
    IFC4X3_TC1_IfcTrackElementType_type,
    IFC4X3_TC1_IfcTrackElementTypeEnum_type,
    IFC4X3_TC1_IfcTransformer_type,
    IFC4X3_TC1_IfcTransformerType_type,
    IFC4X3_TC1_IfcTransformerTypeEnum_type,
    IFC4X3_TC1_IfcTransitionCode_type,
    IFC4X3_TC1_IfcTranslationalStiffnessSelect_type,
    IFC4X3_TC1_IfcTransportationDevice_type,
    IFC4X3_TC1_IfcTransportationDeviceType_type,
    IFC4X3_TC1_IfcTransportElement_type,
    IFC4X3_TC1_IfcTransportElementType_type,
    IFC4X3_TC1_IfcTransportElementTypeEnum_type,
    IFC4X3_TC1_IfcTrapeziumProfileDef_type,
    IFC4X3_TC1_IfcTriangulatedFaceSet_type,
    IFC4X3_TC1_IfcTriangulatedIrregularNetwork_type,
    IFC4X3_TC1_IfcTrimmedCurve_type,
    IFC4X3_TC1_IfcTrimmingPreference_type,
    IFC4X3_TC1_IfcTrimmingSelect_type,
    IFC4X3_TC1_IfcTShapeProfileDef_type,
    IFC4X3_TC1_IfcTubeBundle_type,
    IFC4X3_TC1_IfcTubeBundleType_type,
    IFC4X3_TC1_IfcTubeBundleTypeEnum_type,
    IFC4X3_TC1_IfcTypeObject_type,
    IFC4X3_TC1_IfcTypeProcess_type,
    IFC4X3_TC1_IfcTypeProduct_type,
    IFC4X3_TC1_IfcTypeResource_type,
    IFC4X3_TC1_IfcUnit_type,
    IFC4X3_TC1_IfcUnitaryControlElement_type,
    IFC4X3_TC1_IfcUnitaryControlElementType_type,
    IFC4X3_TC1_IfcUnitaryControlElementTypeEnum_type,
    IFC4X3_TC1_IfcUnitaryEquipment_type,
    IFC4X3_TC1_IfcUnitaryEquipmentType_type,
    IFC4X3_TC1_IfcUnitaryEquipmentTypeEnum_type,
    IFC4X3_TC1_IfcUnitAssignment_type,
    IFC4X3_TC1_IfcUnitEnum_type,
    IFC4X3_TC1_IfcURIReference_type,
    IFC4X3_TC1_IfcUShapeProfileDef_type,
    IFC4X3_TC1_IfcValue_type,
    IFC4X3_TC1_IfcValve_type,
    IFC4X3_TC1_IfcValveType_type,
    IFC4X3_TC1_IfcValveTypeEnum_type,
    IFC4X3_TC1_IfcVaporPermeabilityMeasure_type,
    IFC4X3_TC1_IfcVector_type,
    IFC4X3_TC1_IfcVectorOrDirection_type,
    IFC4X3_TC1_IfcVehicle_type,
    IFC4X3_TC1_IfcVehicleType_type,
    IFC4X3_TC1_IfcVehicleTypeEnum_type,
    IFC4X3_TC1_IfcVertex_type,
    IFC4X3_TC1_IfcVertexLoop_type,
    IFC4X3_TC1_IfcVertexPoint_type,
    IFC4X3_TC1_IfcVibrationDamper_type,
    IFC4X3_TC1_IfcVibrationDamperType_type,
    IFC4X3_TC1_IfcVibrationDamperTypeEnum_type,
    IFC4X3_TC1_IfcVibrationIsolator_type,
    IFC4X3_TC1_IfcVibrationIsolatorType_type,
    IFC4X3_TC1_IfcVibrationIsolatorTypeEnum_type,
    IFC4X3_TC1_IfcVirtualElement_type,
    IFC4X3_TC1_IfcVirtualElementTypeEnum_type,
    IFC4X3_TC1_IfcVirtualGridIntersection_type,
    IFC4X3_TC1_IfcVoidingFeature_type,
    IFC4X3_TC1_IfcVoidingFeatureTypeEnum_type,
    IFC4X3_TC1_IfcVolumeMeasure_type,
    IFC4X3_TC1_IfcVolumetricFlowRateMeasure_type,
    IFC4X3_TC1_IfcWall_type,
    IFC4X3_TC1_IfcWallStandardCase_type,
    IFC4X3_TC1_IfcWallType_type,
    IFC4X3_TC1_IfcWallTypeEnum_type,
    IFC4X3_TC1_IfcWarpingConstantMeasure_type,
    IFC4X3_TC1_IfcWarpingMomentMeasure_type,
    IFC4X3_TC1_IfcWarpingStiffnessSelect_type,
    IFC4X3_TC1_IfcWasteTerminal_type,
    IFC4X3_TC1_IfcWasteTerminalType_type,
    IFC4X3_TC1_IfcWasteTerminalTypeEnum_type,
    IFC4X3_TC1_IfcWindow_type,
    IFC4X3_TC1_IfcWindowLiningProperties_type,
    IFC4X3_TC1_IfcWindowPanelOperationEnum_type,
    IFC4X3_TC1_IfcWindowPanelPositionEnum_type,
    IFC4X3_TC1_IfcWindowPanelProperties_type,
    IFC4X3_TC1_IfcWindowType_type,
    IFC4X3_TC1_IfcWindowTypeEnum_type,
    IFC4X3_TC1_IfcWindowTypePartitioningEnum_type,
    IFC4X3_TC1_IfcWorkCalendar_type,
    IFC4X3_TC1_IfcWorkCalendarTypeEnum_type,
    IFC4X3_TC1_IfcWorkControl_type,
    IFC4X3_TC1_IfcWorkPlan_type,
    IFC4X3_TC1_IfcWorkPlanTypeEnum_type,
    IFC4X3_TC1_IfcWorkSchedule_type,
    IFC4X3_TC1_IfcWorkScheduleTypeEnum_type,
    IFC4X3_TC1_IfcWorkTime_type,
    IFC4X3_TC1_IfcZone_type,
    IFC4X3_TC1_IfcZShapeProfileDef_type
        };
    return new schema_definition(strings[3898], declarations, new IFC4X3_TC1_instance_factory());
}


#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC pop_options
#elif defined(_MSC_VER)
#pragma optimize("", on)
#endif
        
static std::unique_ptr<schema_definition> schema;

void Ifc4x3_tc1::clear_schema() {
    schema.reset();
}

const schema_definition& Ifc4x3_tc1::get_schema() {
    if (!schema) {
        schema.reset(IFC4X3_TC1_populate_schema());
    }
    return *schema;
}

