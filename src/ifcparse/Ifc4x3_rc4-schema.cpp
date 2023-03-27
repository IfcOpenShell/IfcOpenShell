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
 * This file has been generated from IFC4x3_RC2.exp. Do not make modifications  *
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/

#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/Ifc4x3_rc4.h"

using namespace IfcParse;

entity* IFC4X3_RC4_IfcActionRequest_type = 0;
entity* IFC4X3_RC4_IfcActor_type = 0;
entity* IFC4X3_RC4_IfcActorRole_type = 0;
entity* IFC4X3_RC4_IfcActuator_type = 0;
entity* IFC4X3_RC4_IfcActuatorType_type = 0;
entity* IFC4X3_RC4_IfcAddress_type = 0;
entity* IFC4X3_RC4_IfcAdvancedBrep_type = 0;
entity* IFC4X3_RC4_IfcAdvancedBrepWithVoids_type = 0;
entity* IFC4X3_RC4_IfcAdvancedFace_type = 0;
entity* IFC4X3_RC4_IfcAirTerminal_type = 0;
entity* IFC4X3_RC4_IfcAirTerminalBox_type = 0;
entity* IFC4X3_RC4_IfcAirTerminalBoxType_type = 0;
entity* IFC4X3_RC4_IfcAirTerminalType_type = 0;
entity* IFC4X3_RC4_IfcAirToAirHeatRecovery_type = 0;
entity* IFC4X3_RC4_IfcAirToAirHeatRecoveryType_type = 0;
entity* IFC4X3_RC4_IfcAlarm_type = 0;
entity* IFC4X3_RC4_IfcAlarmType_type = 0;
entity* IFC4X3_RC4_IfcAlignment_type = 0;
entity* IFC4X3_RC4_IfcAlignmentCant_type = 0;
entity* IFC4X3_RC4_IfcAlignmentCantSegment_type = 0;
entity* IFC4X3_RC4_IfcAlignmentHorizontal_type = 0;
entity* IFC4X3_RC4_IfcAlignmentHorizontalSegment_type = 0;
entity* IFC4X3_RC4_IfcAlignmentParameterSegment_type = 0;
entity* IFC4X3_RC4_IfcAlignmentSegment_type = 0;
entity* IFC4X3_RC4_IfcAlignmentVertical_type = 0;
entity* IFC4X3_RC4_IfcAlignmentVerticalSegment_type = 0;
entity* IFC4X3_RC4_IfcAnnotation_type = 0;
entity* IFC4X3_RC4_IfcAnnotationFillArea_type = 0;
entity* IFC4X3_RC4_IfcApplication_type = 0;
entity* IFC4X3_RC4_IfcAppliedValue_type = 0;
entity* IFC4X3_RC4_IfcApproval_type = 0;
entity* IFC4X3_RC4_IfcApprovalRelationship_type = 0;
entity* IFC4X3_RC4_IfcArbitraryClosedProfileDef_type = 0;
entity* IFC4X3_RC4_IfcArbitraryOpenProfileDef_type = 0;
entity* IFC4X3_RC4_IfcArbitraryProfileDefWithVoids_type = 0;
entity* IFC4X3_RC4_IfcAsset_type = 0;
entity* IFC4X3_RC4_IfcAsymmetricIShapeProfileDef_type = 0;
entity* IFC4X3_RC4_IfcAudioVisualAppliance_type = 0;
entity* IFC4X3_RC4_IfcAudioVisualApplianceType_type = 0;
entity* IFC4X3_RC4_IfcAxis1Placement_type = 0;
entity* IFC4X3_RC4_IfcAxis2Placement2D_type = 0;
entity* IFC4X3_RC4_IfcAxis2Placement3D_type = 0;
entity* IFC4X3_RC4_IfcAxis2PlacementLinear_type = 0;
entity* IFC4X3_RC4_IfcBSplineCurve_type = 0;
entity* IFC4X3_RC4_IfcBSplineCurveWithKnots_type = 0;
entity* IFC4X3_RC4_IfcBSplineSurface_type = 0;
entity* IFC4X3_RC4_IfcBSplineSurfaceWithKnots_type = 0;
entity* IFC4X3_RC4_IfcBeam_type = 0;
entity* IFC4X3_RC4_IfcBeamStandardCase_type = 0;
entity* IFC4X3_RC4_IfcBeamType_type = 0;
entity* IFC4X3_RC4_IfcBearing_type = 0;
entity* IFC4X3_RC4_IfcBearingType_type = 0;
entity* IFC4X3_RC4_IfcBlobTexture_type = 0;
entity* IFC4X3_RC4_IfcBlock_type = 0;
entity* IFC4X3_RC4_IfcBoiler_type = 0;
entity* IFC4X3_RC4_IfcBoilerType_type = 0;
entity* IFC4X3_RC4_IfcBooleanClippingResult_type = 0;
entity* IFC4X3_RC4_IfcBooleanResult_type = 0;
entity* IFC4X3_RC4_IfcBorehole_type = 0;
entity* IFC4X3_RC4_IfcBoundaryCondition_type = 0;
entity* IFC4X3_RC4_IfcBoundaryCurve_type = 0;
entity* IFC4X3_RC4_IfcBoundaryEdgeCondition_type = 0;
entity* IFC4X3_RC4_IfcBoundaryFaceCondition_type = 0;
entity* IFC4X3_RC4_IfcBoundaryNodeCondition_type = 0;
entity* IFC4X3_RC4_IfcBoundaryNodeConditionWarping_type = 0;
entity* IFC4X3_RC4_IfcBoundedCurve_type = 0;
entity* IFC4X3_RC4_IfcBoundedSurface_type = 0;
entity* IFC4X3_RC4_IfcBoundingBox_type = 0;
entity* IFC4X3_RC4_IfcBoxedHalfSpace_type = 0;
entity* IFC4X3_RC4_IfcBridge_type = 0;
entity* IFC4X3_RC4_IfcBuilding_type = 0;
entity* IFC4X3_RC4_IfcBuildingElementPart_type = 0;
entity* IFC4X3_RC4_IfcBuildingElementPartType_type = 0;
entity* IFC4X3_RC4_IfcBuildingElementProxy_type = 0;
entity* IFC4X3_RC4_IfcBuildingElementProxyType_type = 0;
entity* IFC4X3_RC4_IfcBuildingStorey_type = 0;
entity* IFC4X3_RC4_IfcBuildingSystem_type = 0;
entity* IFC4X3_RC4_IfcBuiltElement_type = 0;
entity* IFC4X3_RC4_IfcBuiltElementType_type = 0;
entity* IFC4X3_RC4_IfcBuiltSystem_type = 0;
entity* IFC4X3_RC4_IfcBurner_type = 0;
entity* IFC4X3_RC4_IfcBurnerType_type = 0;
entity* IFC4X3_RC4_IfcCShapeProfileDef_type = 0;
entity* IFC4X3_RC4_IfcCableCarrierFitting_type = 0;
entity* IFC4X3_RC4_IfcCableCarrierFittingType_type = 0;
entity* IFC4X3_RC4_IfcCableCarrierSegment_type = 0;
entity* IFC4X3_RC4_IfcCableCarrierSegmentType_type = 0;
entity* IFC4X3_RC4_IfcCableFitting_type = 0;
entity* IFC4X3_RC4_IfcCableFittingType_type = 0;
entity* IFC4X3_RC4_IfcCableSegment_type = 0;
entity* IFC4X3_RC4_IfcCableSegmentType_type = 0;
entity* IFC4X3_RC4_IfcCaissonFoundation_type = 0;
entity* IFC4X3_RC4_IfcCaissonFoundationType_type = 0;
entity* IFC4X3_RC4_IfcCartesianPoint_type = 0;
entity* IFC4X3_RC4_IfcCartesianPointList_type = 0;
entity* IFC4X3_RC4_IfcCartesianPointList2D_type = 0;
entity* IFC4X3_RC4_IfcCartesianPointList3D_type = 0;
entity* IFC4X3_RC4_IfcCartesianTransformationOperator_type = 0;
entity* IFC4X3_RC4_IfcCartesianTransformationOperator2D_type = 0;
entity* IFC4X3_RC4_IfcCartesianTransformationOperator2DnonUniform_type = 0;
entity* IFC4X3_RC4_IfcCartesianTransformationOperator3D_type = 0;
entity* IFC4X3_RC4_IfcCartesianTransformationOperator3DnonUniform_type = 0;
entity* IFC4X3_RC4_IfcCenterLineProfileDef_type = 0;
entity* IFC4X3_RC4_IfcChiller_type = 0;
entity* IFC4X3_RC4_IfcChillerType_type = 0;
entity* IFC4X3_RC4_IfcChimney_type = 0;
entity* IFC4X3_RC4_IfcChimneyType_type = 0;
entity* IFC4X3_RC4_IfcCircle_type = 0;
entity* IFC4X3_RC4_IfcCircleHollowProfileDef_type = 0;
entity* IFC4X3_RC4_IfcCircleProfileDef_type = 0;
entity* IFC4X3_RC4_IfcCivilElement_type = 0;
entity* IFC4X3_RC4_IfcCivilElementType_type = 0;
entity* IFC4X3_RC4_IfcClassification_type = 0;
entity* IFC4X3_RC4_IfcClassificationReference_type = 0;
entity* IFC4X3_RC4_IfcClosedShell_type = 0;
entity* IFC4X3_RC4_IfcClothoid_type = 0;
entity* IFC4X3_RC4_IfcCoil_type = 0;
entity* IFC4X3_RC4_IfcCoilType_type = 0;
entity* IFC4X3_RC4_IfcColourRgb_type = 0;
entity* IFC4X3_RC4_IfcColourRgbList_type = 0;
entity* IFC4X3_RC4_IfcColourSpecification_type = 0;
entity* IFC4X3_RC4_IfcColumn_type = 0;
entity* IFC4X3_RC4_IfcColumnStandardCase_type = 0;
entity* IFC4X3_RC4_IfcColumnType_type = 0;
entity* IFC4X3_RC4_IfcCommunicationsAppliance_type = 0;
entity* IFC4X3_RC4_IfcCommunicationsApplianceType_type = 0;
entity* IFC4X3_RC4_IfcComplexProperty_type = 0;
entity* IFC4X3_RC4_IfcComplexPropertyTemplate_type = 0;
entity* IFC4X3_RC4_IfcCompositeCurve_type = 0;
entity* IFC4X3_RC4_IfcCompositeCurveOnSurface_type = 0;
entity* IFC4X3_RC4_IfcCompositeCurveSegment_type = 0;
entity* IFC4X3_RC4_IfcCompositeProfileDef_type = 0;
entity* IFC4X3_RC4_IfcCompressor_type = 0;
entity* IFC4X3_RC4_IfcCompressorType_type = 0;
entity* IFC4X3_RC4_IfcCondenser_type = 0;
entity* IFC4X3_RC4_IfcCondenserType_type = 0;
entity* IFC4X3_RC4_IfcConic_type = 0;
entity* IFC4X3_RC4_IfcConnectedFaceSet_type = 0;
entity* IFC4X3_RC4_IfcConnectionCurveGeometry_type = 0;
entity* IFC4X3_RC4_IfcConnectionGeometry_type = 0;
entity* IFC4X3_RC4_IfcConnectionPointEccentricity_type = 0;
entity* IFC4X3_RC4_IfcConnectionPointGeometry_type = 0;
entity* IFC4X3_RC4_IfcConnectionSurfaceGeometry_type = 0;
entity* IFC4X3_RC4_IfcConnectionVolumeGeometry_type = 0;
entity* IFC4X3_RC4_IfcConstraint_type = 0;
entity* IFC4X3_RC4_IfcConstructionEquipmentResource_type = 0;
entity* IFC4X3_RC4_IfcConstructionEquipmentResourceType_type = 0;
entity* IFC4X3_RC4_IfcConstructionMaterialResource_type = 0;
entity* IFC4X3_RC4_IfcConstructionMaterialResourceType_type = 0;
entity* IFC4X3_RC4_IfcConstructionProductResource_type = 0;
entity* IFC4X3_RC4_IfcConstructionProductResourceType_type = 0;
entity* IFC4X3_RC4_IfcConstructionResource_type = 0;
entity* IFC4X3_RC4_IfcConstructionResourceType_type = 0;
entity* IFC4X3_RC4_IfcContext_type = 0;
entity* IFC4X3_RC4_IfcContextDependentUnit_type = 0;
entity* IFC4X3_RC4_IfcControl_type = 0;
entity* IFC4X3_RC4_IfcController_type = 0;
entity* IFC4X3_RC4_IfcControllerType_type = 0;
entity* IFC4X3_RC4_IfcConversionBasedUnit_type = 0;
entity* IFC4X3_RC4_IfcConversionBasedUnitWithOffset_type = 0;
entity* IFC4X3_RC4_IfcConveyorSegment_type = 0;
entity* IFC4X3_RC4_IfcConveyorSegmentType_type = 0;
entity* IFC4X3_RC4_IfcCooledBeam_type = 0;
entity* IFC4X3_RC4_IfcCooledBeamType_type = 0;
entity* IFC4X3_RC4_IfcCoolingTower_type = 0;
entity* IFC4X3_RC4_IfcCoolingTowerType_type = 0;
entity* IFC4X3_RC4_IfcCoordinateOperation_type = 0;
entity* IFC4X3_RC4_IfcCoordinateReferenceSystem_type = 0;
entity* IFC4X3_RC4_IfcCosine_type = 0;
entity* IFC4X3_RC4_IfcCostItem_type = 0;
entity* IFC4X3_RC4_IfcCostSchedule_type = 0;
entity* IFC4X3_RC4_IfcCostValue_type = 0;
entity* IFC4X3_RC4_IfcCourse_type = 0;
entity* IFC4X3_RC4_IfcCourseType_type = 0;
entity* IFC4X3_RC4_IfcCovering_type = 0;
entity* IFC4X3_RC4_IfcCoveringType_type = 0;
entity* IFC4X3_RC4_IfcCrewResource_type = 0;
entity* IFC4X3_RC4_IfcCrewResourceType_type = 0;
entity* IFC4X3_RC4_IfcCsgPrimitive3D_type = 0;
entity* IFC4X3_RC4_IfcCsgSolid_type = 0;
entity* IFC4X3_RC4_IfcCurrencyRelationship_type = 0;
entity* IFC4X3_RC4_IfcCurtainWall_type = 0;
entity* IFC4X3_RC4_IfcCurtainWallType_type = 0;
entity* IFC4X3_RC4_IfcCurve_type = 0;
entity* IFC4X3_RC4_IfcCurveBoundedPlane_type = 0;
entity* IFC4X3_RC4_IfcCurveBoundedSurface_type = 0;
entity* IFC4X3_RC4_IfcCurveSegment_type = 0;
entity* IFC4X3_RC4_IfcCurveStyle_type = 0;
entity* IFC4X3_RC4_IfcCurveStyleFont_type = 0;
entity* IFC4X3_RC4_IfcCurveStyleFontAndScaling_type = 0;
entity* IFC4X3_RC4_IfcCurveStyleFontPattern_type = 0;
entity* IFC4X3_RC4_IfcCylindricalSurface_type = 0;
entity* IFC4X3_RC4_IfcDamper_type = 0;
entity* IFC4X3_RC4_IfcDamperType_type = 0;
entity* IFC4X3_RC4_IfcDeepFoundation_type = 0;
entity* IFC4X3_RC4_IfcDeepFoundationType_type = 0;
entity* IFC4X3_RC4_IfcDerivedProfileDef_type = 0;
entity* IFC4X3_RC4_IfcDerivedUnit_type = 0;
entity* IFC4X3_RC4_IfcDerivedUnitElement_type = 0;
entity* IFC4X3_RC4_IfcDimensionalExponents_type = 0;
entity* IFC4X3_RC4_IfcDirection_type = 0;
entity* IFC4X3_RC4_IfcDirectrixCurveSweptAreaSolid_type = 0;
entity* IFC4X3_RC4_IfcDirectrixDerivedReferenceSweptAreaSolid_type = 0;
entity* IFC4X3_RC4_IfcDiscreteAccessory_type = 0;
entity* IFC4X3_RC4_IfcDiscreteAccessoryType_type = 0;
entity* IFC4X3_RC4_IfcDistributionBoard_type = 0;
entity* IFC4X3_RC4_IfcDistributionBoardType_type = 0;
entity* IFC4X3_RC4_IfcDistributionChamberElement_type = 0;
entity* IFC4X3_RC4_IfcDistributionChamberElementType_type = 0;
entity* IFC4X3_RC4_IfcDistributionCircuit_type = 0;
entity* IFC4X3_RC4_IfcDistributionControlElement_type = 0;
entity* IFC4X3_RC4_IfcDistributionControlElementType_type = 0;
entity* IFC4X3_RC4_IfcDistributionElement_type = 0;
entity* IFC4X3_RC4_IfcDistributionElementType_type = 0;
entity* IFC4X3_RC4_IfcDistributionFlowElement_type = 0;
entity* IFC4X3_RC4_IfcDistributionFlowElementType_type = 0;
entity* IFC4X3_RC4_IfcDistributionPort_type = 0;
entity* IFC4X3_RC4_IfcDistributionSystem_type = 0;
entity* IFC4X3_RC4_IfcDocumentInformation_type = 0;
entity* IFC4X3_RC4_IfcDocumentInformationRelationship_type = 0;
entity* IFC4X3_RC4_IfcDocumentReference_type = 0;
entity* IFC4X3_RC4_IfcDoor_type = 0;
entity* IFC4X3_RC4_IfcDoorLiningProperties_type = 0;
entity* IFC4X3_RC4_IfcDoorPanelProperties_type = 0;
entity* IFC4X3_RC4_IfcDoorStandardCase_type = 0;
entity* IFC4X3_RC4_IfcDoorStyle_type = 0;
entity* IFC4X3_RC4_IfcDoorType_type = 0;
entity* IFC4X3_RC4_IfcDraughtingPreDefinedColour_type = 0;
entity* IFC4X3_RC4_IfcDraughtingPreDefinedCurveFont_type = 0;
entity* IFC4X3_RC4_IfcDuctFitting_type = 0;
entity* IFC4X3_RC4_IfcDuctFittingType_type = 0;
entity* IFC4X3_RC4_IfcDuctSegment_type = 0;
entity* IFC4X3_RC4_IfcDuctSegmentType_type = 0;
entity* IFC4X3_RC4_IfcDuctSilencer_type = 0;
entity* IFC4X3_RC4_IfcDuctSilencerType_type = 0;
entity* IFC4X3_RC4_IfcEarthworksCut_type = 0;
entity* IFC4X3_RC4_IfcEarthworksElement_type = 0;
entity* IFC4X3_RC4_IfcEarthworksFill_type = 0;
entity* IFC4X3_RC4_IfcEdge_type = 0;
entity* IFC4X3_RC4_IfcEdgeCurve_type = 0;
entity* IFC4X3_RC4_IfcEdgeLoop_type = 0;
entity* IFC4X3_RC4_IfcElectricAppliance_type = 0;
entity* IFC4X3_RC4_IfcElectricApplianceType_type = 0;
entity* IFC4X3_RC4_IfcElectricDistributionBoard_type = 0;
entity* IFC4X3_RC4_IfcElectricDistributionBoardType_type = 0;
entity* IFC4X3_RC4_IfcElectricFlowStorageDevice_type = 0;
entity* IFC4X3_RC4_IfcElectricFlowStorageDeviceType_type = 0;
entity* IFC4X3_RC4_IfcElectricFlowTreatmentDevice_type = 0;
entity* IFC4X3_RC4_IfcElectricFlowTreatmentDeviceType_type = 0;
entity* IFC4X3_RC4_IfcElectricGenerator_type = 0;
entity* IFC4X3_RC4_IfcElectricGeneratorType_type = 0;
entity* IFC4X3_RC4_IfcElectricMotor_type = 0;
entity* IFC4X3_RC4_IfcElectricMotorType_type = 0;
entity* IFC4X3_RC4_IfcElectricTimeControl_type = 0;
entity* IFC4X3_RC4_IfcElectricTimeControlType_type = 0;
entity* IFC4X3_RC4_IfcElement_type = 0;
entity* IFC4X3_RC4_IfcElementAssembly_type = 0;
entity* IFC4X3_RC4_IfcElementAssemblyType_type = 0;
entity* IFC4X3_RC4_IfcElementComponent_type = 0;
entity* IFC4X3_RC4_IfcElementComponentType_type = 0;
entity* IFC4X3_RC4_IfcElementQuantity_type = 0;
entity* IFC4X3_RC4_IfcElementType_type = 0;
entity* IFC4X3_RC4_IfcElementarySurface_type = 0;
entity* IFC4X3_RC4_IfcEllipse_type = 0;
entity* IFC4X3_RC4_IfcEllipseProfileDef_type = 0;
entity* IFC4X3_RC4_IfcEnergyConversionDevice_type = 0;
entity* IFC4X3_RC4_IfcEnergyConversionDeviceType_type = 0;
entity* IFC4X3_RC4_IfcEngine_type = 0;
entity* IFC4X3_RC4_IfcEngineType_type = 0;
entity* IFC4X3_RC4_IfcEvaporativeCooler_type = 0;
entity* IFC4X3_RC4_IfcEvaporativeCoolerType_type = 0;
entity* IFC4X3_RC4_IfcEvaporator_type = 0;
entity* IFC4X3_RC4_IfcEvaporatorType_type = 0;
entity* IFC4X3_RC4_IfcEvent_type = 0;
entity* IFC4X3_RC4_IfcEventTime_type = 0;
entity* IFC4X3_RC4_IfcEventType_type = 0;
entity* IFC4X3_RC4_IfcExtendedProperties_type = 0;
entity* IFC4X3_RC4_IfcExternalInformation_type = 0;
entity* IFC4X3_RC4_IfcExternalReference_type = 0;
entity* IFC4X3_RC4_IfcExternalReferenceRelationship_type = 0;
entity* IFC4X3_RC4_IfcExternalSpatialElement_type = 0;
entity* IFC4X3_RC4_IfcExternalSpatialStructureElement_type = 0;
entity* IFC4X3_RC4_IfcExternallyDefinedHatchStyle_type = 0;
entity* IFC4X3_RC4_IfcExternallyDefinedSurfaceStyle_type = 0;
entity* IFC4X3_RC4_IfcExternallyDefinedTextFont_type = 0;
entity* IFC4X3_RC4_IfcExtrudedAreaSolid_type = 0;
entity* IFC4X3_RC4_IfcExtrudedAreaSolidTapered_type = 0;
entity* IFC4X3_RC4_IfcFace_type = 0;
entity* IFC4X3_RC4_IfcFaceBasedSurfaceModel_type = 0;
entity* IFC4X3_RC4_IfcFaceBound_type = 0;
entity* IFC4X3_RC4_IfcFaceOuterBound_type = 0;
entity* IFC4X3_RC4_IfcFaceSurface_type = 0;
entity* IFC4X3_RC4_IfcFacetedBrep_type = 0;
entity* IFC4X3_RC4_IfcFacetedBrepWithVoids_type = 0;
entity* IFC4X3_RC4_IfcFacility_type = 0;
entity* IFC4X3_RC4_IfcFacilityPart_type = 0;
entity* IFC4X3_RC4_IfcFailureConnectionCondition_type = 0;
entity* IFC4X3_RC4_IfcFan_type = 0;
entity* IFC4X3_RC4_IfcFanType_type = 0;
entity* IFC4X3_RC4_IfcFastener_type = 0;
entity* IFC4X3_RC4_IfcFastenerType_type = 0;
entity* IFC4X3_RC4_IfcFeatureElement_type = 0;
entity* IFC4X3_RC4_IfcFeatureElementAddition_type = 0;
entity* IFC4X3_RC4_IfcFeatureElementSubtraction_type = 0;
entity* IFC4X3_RC4_IfcFillAreaStyle_type = 0;
entity* IFC4X3_RC4_IfcFillAreaStyleHatching_type = 0;
entity* IFC4X3_RC4_IfcFillAreaStyleTiles_type = 0;
entity* IFC4X3_RC4_IfcFilter_type = 0;
entity* IFC4X3_RC4_IfcFilterType_type = 0;
entity* IFC4X3_RC4_IfcFireSuppressionTerminal_type = 0;
entity* IFC4X3_RC4_IfcFireSuppressionTerminalType_type = 0;
entity* IFC4X3_RC4_IfcFixedReferenceSweptAreaSolid_type = 0;
entity* IFC4X3_RC4_IfcFlowController_type = 0;
entity* IFC4X3_RC4_IfcFlowControllerType_type = 0;
entity* IFC4X3_RC4_IfcFlowFitting_type = 0;
entity* IFC4X3_RC4_IfcFlowFittingType_type = 0;
entity* IFC4X3_RC4_IfcFlowInstrument_type = 0;
entity* IFC4X3_RC4_IfcFlowInstrumentType_type = 0;
entity* IFC4X3_RC4_IfcFlowMeter_type = 0;
entity* IFC4X3_RC4_IfcFlowMeterType_type = 0;
entity* IFC4X3_RC4_IfcFlowMovingDevice_type = 0;
entity* IFC4X3_RC4_IfcFlowMovingDeviceType_type = 0;
entity* IFC4X3_RC4_IfcFlowSegment_type = 0;
entity* IFC4X3_RC4_IfcFlowSegmentType_type = 0;
entity* IFC4X3_RC4_IfcFlowStorageDevice_type = 0;
entity* IFC4X3_RC4_IfcFlowStorageDeviceType_type = 0;
entity* IFC4X3_RC4_IfcFlowTerminal_type = 0;
entity* IFC4X3_RC4_IfcFlowTerminalType_type = 0;
entity* IFC4X3_RC4_IfcFlowTreatmentDevice_type = 0;
entity* IFC4X3_RC4_IfcFlowTreatmentDeviceType_type = 0;
entity* IFC4X3_RC4_IfcFooting_type = 0;
entity* IFC4X3_RC4_IfcFootingType_type = 0;
entity* IFC4X3_RC4_IfcFurnishingElement_type = 0;
entity* IFC4X3_RC4_IfcFurnishingElementType_type = 0;
entity* IFC4X3_RC4_IfcFurniture_type = 0;
entity* IFC4X3_RC4_IfcFurnitureType_type = 0;
entity* IFC4X3_RC4_IfcGeographicElement_type = 0;
entity* IFC4X3_RC4_IfcGeographicElementType_type = 0;
entity* IFC4X3_RC4_IfcGeometricCurveSet_type = 0;
entity* IFC4X3_RC4_IfcGeometricRepresentationContext_type = 0;
entity* IFC4X3_RC4_IfcGeometricRepresentationItem_type = 0;
entity* IFC4X3_RC4_IfcGeometricRepresentationSubContext_type = 0;
entity* IFC4X3_RC4_IfcGeometricSet_type = 0;
entity* IFC4X3_RC4_IfcGeomodel_type = 0;
entity* IFC4X3_RC4_IfcGeoslice_type = 0;
entity* IFC4X3_RC4_IfcGeotechnicalAssembly_type = 0;
entity* IFC4X3_RC4_IfcGeotechnicalElement_type = 0;
entity* IFC4X3_RC4_IfcGeotechnicalStratum_type = 0;
entity* IFC4X3_RC4_IfcGradientCurve_type = 0;
entity* IFC4X3_RC4_IfcGrid_type = 0;
entity* IFC4X3_RC4_IfcGridAxis_type = 0;
entity* IFC4X3_RC4_IfcGridPlacement_type = 0;
entity* IFC4X3_RC4_IfcGroup_type = 0;
entity* IFC4X3_RC4_IfcHalfSpaceSolid_type = 0;
entity* IFC4X3_RC4_IfcHeatExchanger_type = 0;
entity* IFC4X3_RC4_IfcHeatExchangerType_type = 0;
entity* IFC4X3_RC4_IfcHumidifier_type = 0;
entity* IFC4X3_RC4_IfcHumidifierType_type = 0;
entity* IFC4X3_RC4_IfcIShapeProfileDef_type = 0;
entity* IFC4X3_RC4_IfcImageTexture_type = 0;
entity* IFC4X3_RC4_IfcImpactProtectionDevice_type = 0;
entity* IFC4X3_RC4_IfcImpactProtectionDeviceType_type = 0;
entity* IFC4X3_RC4_IfcIndexedColourMap_type = 0;
entity* IFC4X3_RC4_IfcIndexedPolyCurve_type = 0;
entity* IFC4X3_RC4_IfcIndexedPolygonalFace_type = 0;
entity* IFC4X3_RC4_IfcIndexedPolygonalFaceWithVoids_type = 0;
entity* IFC4X3_RC4_IfcIndexedTextureMap_type = 0;
entity* IFC4X3_RC4_IfcIndexedTriangleTextureMap_type = 0;
entity* IFC4X3_RC4_IfcInterceptor_type = 0;
entity* IFC4X3_RC4_IfcInterceptorType_type = 0;
entity* IFC4X3_RC4_IfcIntersectionCurve_type = 0;
entity* IFC4X3_RC4_IfcInventory_type = 0;
entity* IFC4X3_RC4_IfcIrregularTimeSeries_type = 0;
entity* IFC4X3_RC4_IfcIrregularTimeSeriesValue_type = 0;
entity* IFC4X3_RC4_IfcJunctionBox_type = 0;
entity* IFC4X3_RC4_IfcJunctionBoxType_type = 0;
entity* IFC4X3_RC4_IfcKerb_type = 0;
entity* IFC4X3_RC4_IfcKerbType_type = 0;
entity* IFC4X3_RC4_IfcLShapeProfileDef_type = 0;
entity* IFC4X3_RC4_IfcLaborResource_type = 0;
entity* IFC4X3_RC4_IfcLaborResourceType_type = 0;
entity* IFC4X3_RC4_IfcLagTime_type = 0;
entity* IFC4X3_RC4_IfcLamp_type = 0;
entity* IFC4X3_RC4_IfcLampType_type = 0;
entity* IFC4X3_RC4_IfcLibraryInformation_type = 0;
entity* IFC4X3_RC4_IfcLibraryReference_type = 0;
entity* IFC4X3_RC4_IfcLightDistributionData_type = 0;
entity* IFC4X3_RC4_IfcLightFixture_type = 0;
entity* IFC4X3_RC4_IfcLightFixtureType_type = 0;
entity* IFC4X3_RC4_IfcLightIntensityDistribution_type = 0;
entity* IFC4X3_RC4_IfcLightSource_type = 0;
entity* IFC4X3_RC4_IfcLightSourceAmbient_type = 0;
entity* IFC4X3_RC4_IfcLightSourceDirectional_type = 0;
entity* IFC4X3_RC4_IfcLightSourceGoniometric_type = 0;
entity* IFC4X3_RC4_IfcLightSourcePositional_type = 0;
entity* IFC4X3_RC4_IfcLightSourceSpot_type = 0;
entity* IFC4X3_RC4_IfcLine_type = 0;
entity* IFC4X3_RC4_IfcLinearElement_type = 0;
entity* IFC4X3_RC4_IfcLinearPlacement_type = 0;
entity* IFC4X3_RC4_IfcLinearPositioningElement_type = 0;
entity* IFC4X3_RC4_IfcLiquidTerminal_type = 0;
entity* IFC4X3_RC4_IfcLiquidTerminalType_type = 0;
entity* IFC4X3_RC4_IfcLocalPlacement_type = 0;
entity* IFC4X3_RC4_IfcLoop_type = 0;
entity* IFC4X3_RC4_IfcManifoldSolidBrep_type = 0;
entity* IFC4X3_RC4_IfcMapConversion_type = 0;
entity* IFC4X3_RC4_IfcMappedItem_type = 0;
entity* IFC4X3_RC4_IfcMarineFacility_type = 0;
entity* IFC4X3_RC4_IfcMaterial_type = 0;
entity* IFC4X3_RC4_IfcMaterialClassificationRelationship_type = 0;
entity* IFC4X3_RC4_IfcMaterialConstituent_type = 0;
entity* IFC4X3_RC4_IfcMaterialConstituentSet_type = 0;
entity* IFC4X3_RC4_IfcMaterialDefinition_type = 0;
entity* IFC4X3_RC4_IfcMaterialDefinitionRepresentation_type = 0;
entity* IFC4X3_RC4_IfcMaterialLayer_type = 0;
entity* IFC4X3_RC4_IfcMaterialLayerSet_type = 0;
entity* IFC4X3_RC4_IfcMaterialLayerSetUsage_type = 0;
entity* IFC4X3_RC4_IfcMaterialLayerWithOffsets_type = 0;
entity* IFC4X3_RC4_IfcMaterialList_type = 0;
entity* IFC4X3_RC4_IfcMaterialProfile_type = 0;
entity* IFC4X3_RC4_IfcMaterialProfileSet_type = 0;
entity* IFC4X3_RC4_IfcMaterialProfileSetUsage_type = 0;
entity* IFC4X3_RC4_IfcMaterialProfileSetUsageTapering_type = 0;
entity* IFC4X3_RC4_IfcMaterialProfileWithOffsets_type = 0;
entity* IFC4X3_RC4_IfcMaterialProperties_type = 0;
entity* IFC4X3_RC4_IfcMaterialRelationship_type = 0;
entity* IFC4X3_RC4_IfcMaterialUsageDefinition_type = 0;
entity* IFC4X3_RC4_IfcMeasureWithUnit_type = 0;
entity* IFC4X3_RC4_IfcMechanicalFastener_type = 0;
entity* IFC4X3_RC4_IfcMechanicalFastenerType_type = 0;
entity* IFC4X3_RC4_IfcMedicalDevice_type = 0;
entity* IFC4X3_RC4_IfcMedicalDeviceType_type = 0;
entity* IFC4X3_RC4_IfcMember_type = 0;
entity* IFC4X3_RC4_IfcMemberStandardCase_type = 0;
entity* IFC4X3_RC4_IfcMemberType_type = 0;
entity* IFC4X3_RC4_IfcMetric_type = 0;
entity* IFC4X3_RC4_IfcMirroredProfileDef_type = 0;
entity* IFC4X3_RC4_IfcMobileTelecommunicationsAppliance_type = 0;
entity* IFC4X3_RC4_IfcMobileTelecommunicationsApplianceType_type = 0;
entity* IFC4X3_RC4_IfcMonetaryUnit_type = 0;
entity* IFC4X3_RC4_IfcMooringDevice_type = 0;
entity* IFC4X3_RC4_IfcMooringDeviceType_type = 0;
entity* IFC4X3_RC4_IfcMotorConnection_type = 0;
entity* IFC4X3_RC4_IfcMotorConnectionType_type = 0;
entity* IFC4X3_RC4_IfcNamedUnit_type = 0;
entity* IFC4X3_RC4_IfcNavigationElement_type = 0;
entity* IFC4X3_RC4_IfcNavigationElementType_type = 0;
entity* IFC4X3_RC4_IfcObject_type = 0;
entity* IFC4X3_RC4_IfcObjectDefinition_type = 0;
entity* IFC4X3_RC4_IfcObjectPlacement_type = 0;
entity* IFC4X3_RC4_IfcObjective_type = 0;
entity* IFC4X3_RC4_IfcOccupant_type = 0;
entity* IFC4X3_RC4_IfcOffsetCurve_type = 0;
entity* IFC4X3_RC4_IfcOffsetCurve2D_type = 0;
entity* IFC4X3_RC4_IfcOffsetCurve3D_type = 0;
entity* IFC4X3_RC4_IfcOffsetCurveByDistances_type = 0;
entity* IFC4X3_RC4_IfcOpenCrossProfileDef_type = 0;
entity* IFC4X3_RC4_IfcOpenShell_type = 0;
entity* IFC4X3_RC4_IfcOpeningElement_type = 0;
entity* IFC4X3_RC4_IfcOpeningStandardCase_type = 0;
entity* IFC4X3_RC4_IfcOrganization_type = 0;
entity* IFC4X3_RC4_IfcOrganizationRelationship_type = 0;
entity* IFC4X3_RC4_IfcOrientedEdge_type = 0;
entity* IFC4X3_RC4_IfcOuterBoundaryCurve_type = 0;
entity* IFC4X3_RC4_IfcOutlet_type = 0;
entity* IFC4X3_RC4_IfcOutletType_type = 0;
entity* IFC4X3_RC4_IfcOwnerHistory_type = 0;
entity* IFC4X3_RC4_IfcParameterizedProfileDef_type = 0;
entity* IFC4X3_RC4_IfcPath_type = 0;
entity* IFC4X3_RC4_IfcPavement_type = 0;
entity* IFC4X3_RC4_IfcPavementType_type = 0;
entity* IFC4X3_RC4_IfcPcurve_type = 0;
entity* IFC4X3_RC4_IfcPerformanceHistory_type = 0;
entity* IFC4X3_RC4_IfcPermeableCoveringProperties_type = 0;
entity* IFC4X3_RC4_IfcPermit_type = 0;
entity* IFC4X3_RC4_IfcPerson_type = 0;
entity* IFC4X3_RC4_IfcPersonAndOrganization_type = 0;
entity* IFC4X3_RC4_IfcPhysicalComplexQuantity_type = 0;
entity* IFC4X3_RC4_IfcPhysicalQuantity_type = 0;
entity* IFC4X3_RC4_IfcPhysicalSimpleQuantity_type = 0;
entity* IFC4X3_RC4_IfcPile_type = 0;
entity* IFC4X3_RC4_IfcPileType_type = 0;
entity* IFC4X3_RC4_IfcPipeFitting_type = 0;
entity* IFC4X3_RC4_IfcPipeFittingType_type = 0;
entity* IFC4X3_RC4_IfcPipeSegment_type = 0;
entity* IFC4X3_RC4_IfcPipeSegmentType_type = 0;
entity* IFC4X3_RC4_IfcPixelTexture_type = 0;
entity* IFC4X3_RC4_IfcPlacement_type = 0;
entity* IFC4X3_RC4_IfcPlanarBox_type = 0;
entity* IFC4X3_RC4_IfcPlanarExtent_type = 0;
entity* IFC4X3_RC4_IfcPlane_type = 0;
entity* IFC4X3_RC4_IfcPlant_type = 0;
entity* IFC4X3_RC4_IfcPlate_type = 0;
entity* IFC4X3_RC4_IfcPlateStandardCase_type = 0;
entity* IFC4X3_RC4_IfcPlateType_type = 0;
entity* IFC4X3_RC4_IfcPoint_type = 0;
entity* IFC4X3_RC4_IfcPointByDistanceExpression_type = 0;
entity* IFC4X3_RC4_IfcPointOnCurve_type = 0;
entity* IFC4X3_RC4_IfcPointOnSurface_type = 0;
entity* IFC4X3_RC4_IfcPolyLoop_type = 0;
entity* IFC4X3_RC4_IfcPolygonalBoundedHalfSpace_type = 0;
entity* IFC4X3_RC4_IfcPolygonalFaceSet_type = 0;
entity* IFC4X3_RC4_IfcPolyline_type = 0;
entity* IFC4X3_RC4_IfcPolynomialCurve_type = 0;
entity* IFC4X3_RC4_IfcPort_type = 0;
entity* IFC4X3_RC4_IfcPositioningElement_type = 0;
entity* IFC4X3_RC4_IfcPostalAddress_type = 0;
entity* IFC4X3_RC4_IfcPreDefinedColour_type = 0;
entity* IFC4X3_RC4_IfcPreDefinedCurveFont_type = 0;
entity* IFC4X3_RC4_IfcPreDefinedItem_type = 0;
entity* IFC4X3_RC4_IfcPreDefinedProperties_type = 0;
entity* IFC4X3_RC4_IfcPreDefinedPropertySet_type = 0;
entity* IFC4X3_RC4_IfcPreDefinedTextFont_type = 0;
entity* IFC4X3_RC4_IfcPresentationItem_type = 0;
entity* IFC4X3_RC4_IfcPresentationLayerAssignment_type = 0;
entity* IFC4X3_RC4_IfcPresentationLayerWithStyle_type = 0;
entity* IFC4X3_RC4_IfcPresentationStyle_type = 0;
entity* IFC4X3_RC4_IfcProcedure_type = 0;
entity* IFC4X3_RC4_IfcProcedureType_type = 0;
entity* IFC4X3_RC4_IfcProcess_type = 0;
entity* IFC4X3_RC4_IfcProduct_type = 0;
entity* IFC4X3_RC4_IfcProductDefinitionShape_type = 0;
entity* IFC4X3_RC4_IfcProductRepresentation_type = 0;
entity* IFC4X3_RC4_IfcProfileDef_type = 0;
entity* IFC4X3_RC4_IfcProfileProperties_type = 0;
entity* IFC4X3_RC4_IfcProject_type = 0;
entity* IFC4X3_RC4_IfcProjectLibrary_type = 0;
entity* IFC4X3_RC4_IfcProjectOrder_type = 0;
entity* IFC4X3_RC4_IfcProjectedCRS_type = 0;
entity* IFC4X3_RC4_IfcProjectionElement_type = 0;
entity* IFC4X3_RC4_IfcProperty_type = 0;
entity* IFC4X3_RC4_IfcPropertyAbstraction_type = 0;
entity* IFC4X3_RC4_IfcPropertyBoundedValue_type = 0;
entity* IFC4X3_RC4_IfcPropertyDefinition_type = 0;
entity* IFC4X3_RC4_IfcPropertyDependencyRelationship_type = 0;
entity* IFC4X3_RC4_IfcPropertyEnumeratedValue_type = 0;
entity* IFC4X3_RC4_IfcPropertyEnumeration_type = 0;
entity* IFC4X3_RC4_IfcPropertyListValue_type = 0;
entity* IFC4X3_RC4_IfcPropertyReferenceValue_type = 0;
entity* IFC4X3_RC4_IfcPropertySet_type = 0;
entity* IFC4X3_RC4_IfcPropertySetDefinition_type = 0;
entity* IFC4X3_RC4_IfcPropertySetTemplate_type = 0;
entity* IFC4X3_RC4_IfcPropertySingleValue_type = 0;
entity* IFC4X3_RC4_IfcPropertyTableValue_type = 0;
entity* IFC4X3_RC4_IfcPropertyTemplate_type = 0;
entity* IFC4X3_RC4_IfcPropertyTemplateDefinition_type = 0;
entity* IFC4X3_RC4_IfcProtectiveDevice_type = 0;
entity* IFC4X3_RC4_IfcProtectiveDeviceTrippingUnit_type = 0;
entity* IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitType_type = 0;
entity* IFC4X3_RC4_IfcProtectiveDeviceType_type = 0;
entity* IFC4X3_RC4_IfcProxy_type = 0;
entity* IFC4X3_RC4_IfcPump_type = 0;
entity* IFC4X3_RC4_IfcPumpType_type = 0;
entity* IFC4X3_RC4_IfcQuantityArea_type = 0;
entity* IFC4X3_RC4_IfcQuantityCount_type = 0;
entity* IFC4X3_RC4_IfcQuantityLength_type = 0;
entity* IFC4X3_RC4_IfcQuantitySet_type = 0;
entity* IFC4X3_RC4_IfcQuantityTime_type = 0;
entity* IFC4X3_RC4_IfcQuantityVolume_type = 0;
entity* IFC4X3_RC4_IfcQuantityWeight_type = 0;
entity* IFC4X3_RC4_IfcRail_type = 0;
entity* IFC4X3_RC4_IfcRailType_type = 0;
entity* IFC4X3_RC4_IfcRailing_type = 0;
entity* IFC4X3_RC4_IfcRailingType_type = 0;
entity* IFC4X3_RC4_IfcRailway_type = 0;
entity* IFC4X3_RC4_IfcRamp_type = 0;
entity* IFC4X3_RC4_IfcRampFlight_type = 0;
entity* IFC4X3_RC4_IfcRampFlightType_type = 0;
entity* IFC4X3_RC4_IfcRampType_type = 0;
entity* IFC4X3_RC4_IfcRationalBSplineCurveWithKnots_type = 0;
entity* IFC4X3_RC4_IfcRationalBSplineSurfaceWithKnots_type = 0;
entity* IFC4X3_RC4_IfcRectangleHollowProfileDef_type = 0;
entity* IFC4X3_RC4_IfcRectangleProfileDef_type = 0;
entity* IFC4X3_RC4_IfcRectangularPyramid_type = 0;
entity* IFC4X3_RC4_IfcRectangularTrimmedSurface_type = 0;
entity* IFC4X3_RC4_IfcRecurrencePattern_type = 0;
entity* IFC4X3_RC4_IfcReference_type = 0;
entity* IFC4X3_RC4_IfcReferent_type = 0;
entity* IFC4X3_RC4_IfcRegularTimeSeries_type = 0;
entity* IFC4X3_RC4_IfcReinforcedSoil_type = 0;
entity* IFC4X3_RC4_IfcReinforcementBarProperties_type = 0;
entity* IFC4X3_RC4_IfcReinforcementDefinitionProperties_type = 0;
entity* IFC4X3_RC4_IfcReinforcingBar_type = 0;
entity* IFC4X3_RC4_IfcReinforcingBarType_type = 0;
entity* IFC4X3_RC4_IfcReinforcingElement_type = 0;
entity* IFC4X3_RC4_IfcReinforcingElementType_type = 0;
entity* IFC4X3_RC4_IfcReinforcingMesh_type = 0;
entity* IFC4X3_RC4_IfcReinforcingMeshType_type = 0;
entity* IFC4X3_RC4_IfcRelAdheresToElement_type = 0;
entity* IFC4X3_RC4_IfcRelAggregates_type = 0;
entity* IFC4X3_RC4_IfcRelAssigns_type = 0;
entity* IFC4X3_RC4_IfcRelAssignsToActor_type = 0;
entity* IFC4X3_RC4_IfcRelAssignsToControl_type = 0;
entity* IFC4X3_RC4_IfcRelAssignsToGroup_type = 0;
entity* IFC4X3_RC4_IfcRelAssignsToGroupByFactor_type = 0;
entity* IFC4X3_RC4_IfcRelAssignsToProcess_type = 0;
entity* IFC4X3_RC4_IfcRelAssignsToProduct_type = 0;
entity* IFC4X3_RC4_IfcRelAssignsToResource_type = 0;
entity* IFC4X3_RC4_IfcRelAssociates_type = 0;
entity* IFC4X3_RC4_IfcRelAssociatesApproval_type = 0;
entity* IFC4X3_RC4_IfcRelAssociatesClassification_type = 0;
entity* IFC4X3_RC4_IfcRelAssociatesConstraint_type = 0;
entity* IFC4X3_RC4_IfcRelAssociatesDocument_type = 0;
entity* IFC4X3_RC4_IfcRelAssociatesLibrary_type = 0;
entity* IFC4X3_RC4_IfcRelAssociatesMaterial_type = 0;
entity* IFC4X3_RC4_IfcRelAssociatesProfileDef_type = 0;
entity* IFC4X3_RC4_IfcRelConnects_type = 0;
entity* IFC4X3_RC4_IfcRelConnectsElements_type = 0;
entity* IFC4X3_RC4_IfcRelConnectsPathElements_type = 0;
entity* IFC4X3_RC4_IfcRelConnectsPortToElement_type = 0;
entity* IFC4X3_RC4_IfcRelConnectsPorts_type = 0;
entity* IFC4X3_RC4_IfcRelConnectsStructuralActivity_type = 0;
entity* IFC4X3_RC4_IfcRelConnectsStructuralMember_type = 0;
entity* IFC4X3_RC4_IfcRelConnectsWithEccentricity_type = 0;
entity* IFC4X3_RC4_IfcRelConnectsWithRealizingElements_type = 0;
entity* IFC4X3_RC4_IfcRelContainedInSpatialStructure_type = 0;
entity* IFC4X3_RC4_IfcRelCoversBldgElements_type = 0;
entity* IFC4X3_RC4_IfcRelCoversSpaces_type = 0;
entity* IFC4X3_RC4_IfcRelDeclares_type = 0;
entity* IFC4X3_RC4_IfcRelDecomposes_type = 0;
entity* IFC4X3_RC4_IfcRelDefines_type = 0;
entity* IFC4X3_RC4_IfcRelDefinesByObject_type = 0;
entity* IFC4X3_RC4_IfcRelDefinesByProperties_type = 0;
entity* IFC4X3_RC4_IfcRelDefinesByTemplate_type = 0;
entity* IFC4X3_RC4_IfcRelDefinesByType_type = 0;
entity* IFC4X3_RC4_IfcRelFillsElement_type = 0;
entity* IFC4X3_RC4_IfcRelFlowControlElements_type = 0;
entity* IFC4X3_RC4_IfcRelInterferesElements_type = 0;
entity* IFC4X3_RC4_IfcRelNests_type = 0;
entity* IFC4X3_RC4_IfcRelPositions_type = 0;
entity* IFC4X3_RC4_IfcRelProjectsElement_type = 0;
entity* IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type = 0;
entity* IFC4X3_RC4_IfcRelSequence_type = 0;
entity* IFC4X3_RC4_IfcRelServicesBuildings_type = 0;
entity* IFC4X3_RC4_IfcRelSpaceBoundary_type = 0;
entity* IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type = 0;
entity* IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type = 0;
entity* IFC4X3_RC4_IfcRelVoidsElement_type = 0;
entity* IFC4X3_RC4_IfcRelationship_type = 0;
entity* IFC4X3_RC4_IfcReparametrisedCompositeCurveSegment_type = 0;
entity* IFC4X3_RC4_IfcRepresentation_type = 0;
entity* IFC4X3_RC4_IfcRepresentationContext_type = 0;
entity* IFC4X3_RC4_IfcRepresentationItem_type = 0;
entity* IFC4X3_RC4_IfcRepresentationMap_type = 0;
entity* IFC4X3_RC4_IfcResource_type = 0;
entity* IFC4X3_RC4_IfcResourceApprovalRelationship_type = 0;
entity* IFC4X3_RC4_IfcResourceConstraintRelationship_type = 0;
entity* IFC4X3_RC4_IfcResourceLevelRelationship_type = 0;
entity* IFC4X3_RC4_IfcResourceTime_type = 0;
entity* IFC4X3_RC4_IfcRevolvedAreaSolid_type = 0;
entity* IFC4X3_RC4_IfcRevolvedAreaSolidTapered_type = 0;
entity* IFC4X3_RC4_IfcRightCircularCone_type = 0;
entity* IFC4X3_RC4_IfcRightCircularCylinder_type = 0;
entity* IFC4X3_RC4_IfcRoad_type = 0;
entity* IFC4X3_RC4_IfcRoof_type = 0;
entity* IFC4X3_RC4_IfcRoofType_type = 0;
entity* IFC4X3_RC4_IfcRoot_type = 0;
entity* IFC4X3_RC4_IfcRoundedRectangleProfileDef_type = 0;
entity* IFC4X3_RC4_IfcSIUnit_type = 0;
entity* IFC4X3_RC4_IfcSanitaryTerminal_type = 0;
entity* IFC4X3_RC4_IfcSanitaryTerminalType_type = 0;
entity* IFC4X3_RC4_IfcSchedulingTime_type = 0;
entity* IFC4X3_RC4_IfcSeamCurve_type = 0;
entity* IFC4X3_RC4_IfcSecondOrderPolynomialSpiral_type = 0;
entity* IFC4X3_RC4_IfcSectionProperties_type = 0;
entity* IFC4X3_RC4_IfcSectionReinforcementProperties_type = 0;
entity* IFC4X3_RC4_IfcSectionedSolid_type = 0;
entity* IFC4X3_RC4_IfcSectionedSolidHorizontal_type = 0;
entity* IFC4X3_RC4_IfcSectionedSpine_type = 0;
entity* IFC4X3_RC4_IfcSectionedSurface_type = 0;
entity* IFC4X3_RC4_IfcSegment_type = 0;
entity* IFC4X3_RC4_IfcSegmentedReferenceCurve_type = 0;
entity* IFC4X3_RC4_IfcSensor_type = 0;
entity* IFC4X3_RC4_IfcSensorType_type = 0;
entity* IFC4X3_RC4_IfcSeventhOrderPolynomialSpiral_type = 0;
entity* IFC4X3_RC4_IfcShadingDevice_type = 0;
entity* IFC4X3_RC4_IfcShadingDeviceType_type = 0;
entity* IFC4X3_RC4_IfcShapeAspect_type = 0;
entity* IFC4X3_RC4_IfcShapeModel_type = 0;
entity* IFC4X3_RC4_IfcShapeRepresentation_type = 0;
entity* IFC4X3_RC4_IfcShellBasedSurfaceModel_type = 0;
entity* IFC4X3_RC4_IfcSign_type = 0;
entity* IFC4X3_RC4_IfcSignType_type = 0;
entity* IFC4X3_RC4_IfcSignal_type = 0;
entity* IFC4X3_RC4_IfcSignalType_type = 0;
entity* IFC4X3_RC4_IfcSimpleProperty_type = 0;
entity* IFC4X3_RC4_IfcSimplePropertyTemplate_type = 0;
entity* IFC4X3_RC4_IfcSine_type = 0;
entity* IFC4X3_RC4_IfcSite_type = 0;
entity* IFC4X3_RC4_IfcSlab_type = 0;
entity* IFC4X3_RC4_IfcSlabElementedCase_type = 0;
entity* IFC4X3_RC4_IfcSlabStandardCase_type = 0;
entity* IFC4X3_RC4_IfcSlabType_type = 0;
entity* IFC4X3_RC4_IfcSlippageConnectionCondition_type = 0;
entity* IFC4X3_RC4_IfcSolarDevice_type = 0;
entity* IFC4X3_RC4_IfcSolarDeviceType_type = 0;
entity* IFC4X3_RC4_IfcSolidModel_type = 0;
entity* IFC4X3_RC4_IfcSolidStratum_type = 0;
entity* IFC4X3_RC4_IfcSpace_type = 0;
entity* IFC4X3_RC4_IfcSpaceHeater_type = 0;
entity* IFC4X3_RC4_IfcSpaceHeaterType_type = 0;
entity* IFC4X3_RC4_IfcSpaceType_type = 0;
entity* IFC4X3_RC4_IfcSpatialElement_type = 0;
entity* IFC4X3_RC4_IfcSpatialElementType_type = 0;
entity* IFC4X3_RC4_IfcSpatialStructureElement_type = 0;
entity* IFC4X3_RC4_IfcSpatialStructureElementType_type = 0;
entity* IFC4X3_RC4_IfcSpatialZone_type = 0;
entity* IFC4X3_RC4_IfcSpatialZoneType_type = 0;
entity* IFC4X3_RC4_IfcSphere_type = 0;
entity* IFC4X3_RC4_IfcSphericalSurface_type = 0;
entity* IFC4X3_RC4_IfcSpiral_type = 0;
entity* IFC4X3_RC4_IfcStackTerminal_type = 0;
entity* IFC4X3_RC4_IfcStackTerminalType_type = 0;
entity* IFC4X3_RC4_IfcStair_type = 0;
entity* IFC4X3_RC4_IfcStairFlight_type = 0;
entity* IFC4X3_RC4_IfcStairFlightType_type = 0;
entity* IFC4X3_RC4_IfcStairType_type = 0;
entity* IFC4X3_RC4_IfcStructuralAction_type = 0;
entity* IFC4X3_RC4_IfcStructuralActivity_type = 0;
entity* IFC4X3_RC4_IfcStructuralAnalysisModel_type = 0;
entity* IFC4X3_RC4_IfcStructuralConnection_type = 0;
entity* IFC4X3_RC4_IfcStructuralConnectionCondition_type = 0;
entity* IFC4X3_RC4_IfcStructuralCurveAction_type = 0;
entity* IFC4X3_RC4_IfcStructuralCurveConnection_type = 0;
entity* IFC4X3_RC4_IfcStructuralCurveMember_type = 0;
entity* IFC4X3_RC4_IfcStructuralCurveMemberVarying_type = 0;
entity* IFC4X3_RC4_IfcStructuralCurveReaction_type = 0;
entity* IFC4X3_RC4_IfcStructuralItem_type = 0;
entity* IFC4X3_RC4_IfcStructuralLinearAction_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoad_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadCase_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadConfiguration_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadGroup_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadLinearForce_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadOrResult_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadPlanarForce_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadSingleDisplacement_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadSingleDisplacementDistortion_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadSingleForce_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadSingleForceWarping_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadStatic_type = 0;
entity* IFC4X3_RC4_IfcStructuralLoadTemperature_type = 0;
entity* IFC4X3_RC4_IfcStructuralMember_type = 0;
entity* IFC4X3_RC4_IfcStructuralPlanarAction_type = 0;
entity* IFC4X3_RC4_IfcStructuralPointAction_type = 0;
entity* IFC4X3_RC4_IfcStructuralPointConnection_type = 0;
entity* IFC4X3_RC4_IfcStructuralPointReaction_type = 0;
entity* IFC4X3_RC4_IfcStructuralReaction_type = 0;
entity* IFC4X3_RC4_IfcStructuralResultGroup_type = 0;
entity* IFC4X3_RC4_IfcStructuralSurfaceAction_type = 0;
entity* IFC4X3_RC4_IfcStructuralSurfaceConnection_type = 0;
entity* IFC4X3_RC4_IfcStructuralSurfaceMember_type = 0;
entity* IFC4X3_RC4_IfcStructuralSurfaceMemberVarying_type = 0;
entity* IFC4X3_RC4_IfcStructuralSurfaceReaction_type = 0;
entity* IFC4X3_RC4_IfcStyleModel_type = 0;
entity* IFC4X3_RC4_IfcStyledItem_type = 0;
entity* IFC4X3_RC4_IfcStyledRepresentation_type = 0;
entity* IFC4X3_RC4_IfcSubContractResource_type = 0;
entity* IFC4X3_RC4_IfcSubContractResourceType_type = 0;
entity* IFC4X3_RC4_IfcSubedge_type = 0;
entity* IFC4X3_RC4_IfcSurface_type = 0;
entity* IFC4X3_RC4_IfcSurfaceCurve_type = 0;
entity* IFC4X3_RC4_IfcSurfaceCurveSweptAreaSolid_type = 0;
entity* IFC4X3_RC4_IfcSurfaceFeature_type = 0;
entity* IFC4X3_RC4_IfcSurfaceOfLinearExtrusion_type = 0;
entity* IFC4X3_RC4_IfcSurfaceOfRevolution_type = 0;
entity* IFC4X3_RC4_IfcSurfaceReinforcementArea_type = 0;
entity* IFC4X3_RC4_IfcSurfaceStyle_type = 0;
entity* IFC4X3_RC4_IfcSurfaceStyleLighting_type = 0;
entity* IFC4X3_RC4_IfcSurfaceStyleRefraction_type = 0;
entity* IFC4X3_RC4_IfcSurfaceStyleRendering_type = 0;
entity* IFC4X3_RC4_IfcSurfaceStyleShading_type = 0;
entity* IFC4X3_RC4_IfcSurfaceStyleWithTextures_type = 0;
entity* IFC4X3_RC4_IfcSurfaceTexture_type = 0;
entity* IFC4X3_RC4_IfcSweptAreaSolid_type = 0;
entity* IFC4X3_RC4_IfcSweptDiskSolid_type = 0;
entity* IFC4X3_RC4_IfcSweptDiskSolidPolygonal_type = 0;
entity* IFC4X3_RC4_IfcSweptSurface_type = 0;
entity* IFC4X3_RC4_IfcSwitchingDevice_type = 0;
entity* IFC4X3_RC4_IfcSwitchingDeviceType_type = 0;
entity* IFC4X3_RC4_IfcSystem_type = 0;
entity* IFC4X3_RC4_IfcSystemFurnitureElement_type = 0;
entity* IFC4X3_RC4_IfcSystemFurnitureElementType_type = 0;
entity* IFC4X3_RC4_IfcTShapeProfileDef_type = 0;
entity* IFC4X3_RC4_IfcTable_type = 0;
entity* IFC4X3_RC4_IfcTableColumn_type = 0;
entity* IFC4X3_RC4_IfcTableRow_type = 0;
entity* IFC4X3_RC4_IfcTank_type = 0;
entity* IFC4X3_RC4_IfcTankType_type = 0;
entity* IFC4X3_RC4_IfcTask_type = 0;
entity* IFC4X3_RC4_IfcTaskTime_type = 0;
entity* IFC4X3_RC4_IfcTaskTimeRecurring_type = 0;
entity* IFC4X3_RC4_IfcTaskType_type = 0;
entity* IFC4X3_RC4_IfcTelecomAddress_type = 0;
entity* IFC4X3_RC4_IfcTendon_type = 0;
entity* IFC4X3_RC4_IfcTendonAnchor_type = 0;
entity* IFC4X3_RC4_IfcTendonAnchorType_type = 0;
entity* IFC4X3_RC4_IfcTendonConduit_type = 0;
entity* IFC4X3_RC4_IfcTendonConduitType_type = 0;
entity* IFC4X3_RC4_IfcTendonType_type = 0;
entity* IFC4X3_RC4_IfcTessellatedFaceSet_type = 0;
entity* IFC4X3_RC4_IfcTessellatedItem_type = 0;
entity* IFC4X3_RC4_IfcTextLiteral_type = 0;
entity* IFC4X3_RC4_IfcTextLiteralWithExtent_type = 0;
entity* IFC4X3_RC4_IfcTextStyle_type = 0;
entity* IFC4X3_RC4_IfcTextStyleFontModel_type = 0;
entity* IFC4X3_RC4_IfcTextStyleForDefinedFont_type = 0;
entity* IFC4X3_RC4_IfcTextStyleTextModel_type = 0;
entity* IFC4X3_RC4_IfcTextureCoordinate_type = 0;
entity* IFC4X3_RC4_IfcTextureCoordinateGenerator_type = 0;
entity* IFC4X3_RC4_IfcTextureMap_type = 0;
entity* IFC4X3_RC4_IfcTextureVertex_type = 0;
entity* IFC4X3_RC4_IfcTextureVertexList_type = 0;
entity* IFC4X3_RC4_IfcThirdOrderPolynomialSpiral_type = 0;
entity* IFC4X3_RC4_IfcTimePeriod_type = 0;
entity* IFC4X3_RC4_IfcTimeSeries_type = 0;
entity* IFC4X3_RC4_IfcTimeSeriesValue_type = 0;
entity* IFC4X3_RC4_IfcTopologicalRepresentationItem_type = 0;
entity* IFC4X3_RC4_IfcTopologyRepresentation_type = 0;
entity* IFC4X3_RC4_IfcToroidalSurface_type = 0;
entity* IFC4X3_RC4_IfcTrackElement_type = 0;
entity* IFC4X3_RC4_IfcTrackElementType_type = 0;
entity* IFC4X3_RC4_IfcTransformer_type = 0;
entity* IFC4X3_RC4_IfcTransformerType_type = 0;
entity* IFC4X3_RC4_IfcTransportElement_type = 0;
entity* IFC4X3_RC4_IfcTransportElementType_type = 0;
entity* IFC4X3_RC4_IfcTrapeziumProfileDef_type = 0;
entity* IFC4X3_RC4_IfcTriangulatedFaceSet_type = 0;
entity* IFC4X3_RC4_IfcTriangulatedIrregularNetwork_type = 0;
entity* IFC4X3_RC4_IfcTrimmedCurve_type = 0;
entity* IFC4X3_RC4_IfcTubeBundle_type = 0;
entity* IFC4X3_RC4_IfcTubeBundleType_type = 0;
entity* IFC4X3_RC4_IfcTypeObject_type = 0;
entity* IFC4X3_RC4_IfcTypeProcess_type = 0;
entity* IFC4X3_RC4_IfcTypeProduct_type = 0;
entity* IFC4X3_RC4_IfcTypeResource_type = 0;
entity* IFC4X3_RC4_IfcUShapeProfileDef_type = 0;
entity* IFC4X3_RC4_IfcUnitAssignment_type = 0;
entity* IFC4X3_RC4_IfcUnitaryControlElement_type = 0;
entity* IFC4X3_RC4_IfcUnitaryControlElementType_type = 0;
entity* IFC4X3_RC4_IfcUnitaryEquipment_type = 0;
entity* IFC4X3_RC4_IfcUnitaryEquipmentType_type = 0;
entity* IFC4X3_RC4_IfcValve_type = 0;
entity* IFC4X3_RC4_IfcValveType_type = 0;
entity* IFC4X3_RC4_IfcVector_type = 0;
entity* IFC4X3_RC4_IfcVertex_type = 0;
entity* IFC4X3_RC4_IfcVertexLoop_type = 0;
entity* IFC4X3_RC4_IfcVertexPoint_type = 0;
entity* IFC4X3_RC4_IfcVibrationDamper_type = 0;
entity* IFC4X3_RC4_IfcVibrationDamperType_type = 0;
entity* IFC4X3_RC4_IfcVibrationIsolator_type = 0;
entity* IFC4X3_RC4_IfcVibrationIsolatorType_type = 0;
entity* IFC4X3_RC4_IfcVirtualElement_type = 0;
entity* IFC4X3_RC4_IfcVirtualGridIntersection_type = 0;
entity* IFC4X3_RC4_IfcVoidStratum_type = 0;
entity* IFC4X3_RC4_IfcVoidingFeature_type = 0;
entity* IFC4X3_RC4_IfcWall_type = 0;
entity* IFC4X3_RC4_IfcWallElementedCase_type = 0;
entity* IFC4X3_RC4_IfcWallStandardCase_type = 0;
entity* IFC4X3_RC4_IfcWallType_type = 0;
entity* IFC4X3_RC4_IfcWasteTerminal_type = 0;
entity* IFC4X3_RC4_IfcWasteTerminalType_type = 0;
entity* IFC4X3_RC4_IfcWaterStratum_type = 0;
entity* IFC4X3_RC4_IfcWindow_type = 0;
entity* IFC4X3_RC4_IfcWindowLiningProperties_type = 0;
entity* IFC4X3_RC4_IfcWindowPanelProperties_type = 0;
entity* IFC4X3_RC4_IfcWindowStandardCase_type = 0;
entity* IFC4X3_RC4_IfcWindowStyle_type = 0;
entity* IFC4X3_RC4_IfcWindowType_type = 0;
entity* IFC4X3_RC4_IfcWorkCalendar_type = 0;
entity* IFC4X3_RC4_IfcWorkControl_type = 0;
entity* IFC4X3_RC4_IfcWorkPlan_type = 0;
entity* IFC4X3_RC4_IfcWorkSchedule_type = 0;
entity* IFC4X3_RC4_IfcWorkTime_type = 0;
entity* IFC4X3_RC4_IfcZShapeProfileDef_type = 0;
entity* IFC4X3_RC4_IfcZone_type = 0;
type_declaration* IFC4X3_RC4_IfcAbsorbedDoseMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcAccelerationMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcAmountOfSubstanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcAngularVelocityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcArcIndex_type = 0;
type_declaration* IFC4X3_RC4_IfcAreaDensityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcAreaMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcBinary_type = 0;
type_declaration* IFC4X3_RC4_IfcBoolean_type = 0;
type_declaration* IFC4X3_RC4_IfcBoxAlignment_type = 0;
type_declaration* IFC4X3_RC4_IfcCardinalPointReference_type = 0;
type_declaration* IFC4X3_RC4_IfcComplexNumber_type = 0;
type_declaration* IFC4X3_RC4_IfcCompoundPlaneAngleMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcContextDependentMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcCountMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcCurvatureMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcDate_type = 0;
type_declaration* IFC4X3_RC4_IfcDateTime_type = 0;
type_declaration* IFC4X3_RC4_IfcDayInMonthNumber_type = 0;
type_declaration* IFC4X3_RC4_IfcDayInWeekNumber_type = 0;
type_declaration* IFC4X3_RC4_IfcDescriptiveMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcDimensionCount_type = 0;
type_declaration* IFC4X3_RC4_IfcDoseEquivalentMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcDuration_type = 0;
type_declaration* IFC4X3_RC4_IfcDynamicViscosityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcElectricCapacitanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcElectricChargeMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcElectricConductanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcElectricCurrentMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcElectricResistanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcElectricVoltageMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcEnergyMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcFontStyle_type = 0;
type_declaration* IFC4X3_RC4_IfcFontVariant_type = 0;
type_declaration* IFC4X3_RC4_IfcFontWeight_type = 0;
type_declaration* IFC4X3_RC4_IfcForceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcFrequencyMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcGloballyUniqueId_type = 0;
type_declaration* IFC4X3_RC4_IfcHeatFluxDensityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcHeatingValueMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcIdentifier_type = 0;
type_declaration* IFC4X3_RC4_IfcIlluminanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcInductanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcInteger_type = 0;
type_declaration* IFC4X3_RC4_IfcIntegerCountRateMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcIonConcentrationMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcIsothermalMoistureCapacityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcKinematicViscosityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcLabel_type = 0;
type_declaration* IFC4X3_RC4_IfcLanguageId_type = 0;
type_declaration* IFC4X3_RC4_IfcLengthMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcLineIndex_type = 0;
type_declaration* IFC4X3_RC4_IfcLinearForceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcLinearMomentMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcLinearStiffnessMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcLinearVelocityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcLogical_type = 0;
type_declaration* IFC4X3_RC4_IfcLuminousFluxMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcLuminousIntensityDistributionMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcLuminousIntensityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMagneticFluxDensityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMagneticFluxMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMassDensityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMassFlowRateMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMassMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMassPerLengthMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcModulusOfElasticityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcModulusOfLinearSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcModulusOfSubgradeReactionMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMoistureDiffusivityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMolecularWeightMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMomentOfInertiaMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMonetaryMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcMonthInYearNumber_type = 0;
type_declaration* IFC4X3_RC4_IfcNonNegativeLengthMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcNormalisedRatioMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcNumericMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcPHMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcParameterValue_type = 0;
type_declaration* IFC4X3_RC4_IfcPlanarForceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcPlaneAngleMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcPositiveInteger_type = 0;
type_declaration* IFC4X3_RC4_IfcPositiveLengthMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcPositivePlaneAngleMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcPositiveRatioMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcPowerMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcPresentableText_type = 0;
type_declaration* IFC4X3_RC4_IfcPressureMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcPropertySetDefinitionSet_type = 0;
type_declaration* IFC4X3_RC4_IfcRadioActivityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcRatioMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcReal_type = 0;
type_declaration* IFC4X3_RC4_IfcRotationalFrequencyMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcRotationalMassMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcRotationalStiffnessMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSectionModulusMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSectionalAreaIntegralMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcShearModulusMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSolidAngleMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSoundPowerLevelMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSoundPowerMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSoundPressureLevelMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSoundPressureMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSpecificHeatCapacityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcSpecularExponent_type = 0;
type_declaration* IFC4X3_RC4_IfcSpecularRoughness_type = 0;
type_declaration* IFC4X3_RC4_IfcTemperatureGradientMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcTemperatureRateOfChangeMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcText_type = 0;
type_declaration* IFC4X3_RC4_IfcTextAlignment_type = 0;
type_declaration* IFC4X3_RC4_IfcTextDecoration_type = 0;
type_declaration* IFC4X3_RC4_IfcTextFontName_type = 0;
type_declaration* IFC4X3_RC4_IfcTextTransformation_type = 0;
type_declaration* IFC4X3_RC4_IfcThermalAdmittanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcThermalConductivityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcThermalExpansionCoefficientMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcThermalResistanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcThermalTransmittanceMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcThermodynamicTemperatureMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcTime_type = 0;
type_declaration* IFC4X3_RC4_IfcTimeMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcTimeStamp_type = 0;
type_declaration* IFC4X3_RC4_IfcTorqueMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcURIReference_type = 0;
type_declaration* IFC4X3_RC4_IfcVaporPermeabilityMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcVolumeMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcVolumetricFlowRateMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcWarpingConstantMeasure_type = 0;
type_declaration* IFC4X3_RC4_IfcWarpingMomentMeasure_type = 0;
select_type* IFC4X3_RC4_IfcActorSelect_type = 0;
select_type* IFC4X3_RC4_IfcAppliedValueSelect_type = 0;
select_type* IFC4X3_RC4_IfcAxis2Placement_type = 0;
select_type* IFC4X3_RC4_IfcBendingParameterSelect_type = 0;
select_type* IFC4X3_RC4_IfcBooleanOperand_type = 0;
select_type* IFC4X3_RC4_IfcClassificationReferenceSelect_type = 0;
select_type* IFC4X3_RC4_IfcClassificationSelect_type = 0;
select_type* IFC4X3_RC4_IfcColour_type = 0;
select_type* IFC4X3_RC4_IfcColourOrFactor_type = 0;
select_type* IFC4X3_RC4_IfcCoordinateReferenceSystemSelect_type = 0;
select_type* IFC4X3_RC4_IfcCsgSelect_type = 0;
select_type* IFC4X3_RC4_IfcCurveFontOrScaledCurveFontSelect_type = 0;
select_type* IFC4X3_RC4_IfcCurveMeasureSelect_type = 0;
select_type* IFC4X3_RC4_IfcCurveOnSurface_type = 0;
select_type* IFC4X3_RC4_IfcCurveOrEdgeCurve_type = 0;
select_type* IFC4X3_RC4_IfcCurveStyleFontSelect_type = 0;
select_type* IFC4X3_RC4_IfcDefinitionSelect_type = 0;
select_type* IFC4X3_RC4_IfcDerivedMeasureValue_type = 0;
select_type* IFC4X3_RC4_IfcDocumentSelect_type = 0;
select_type* IFC4X3_RC4_IfcFacilityPartTypeSelect_type = 0;
select_type* IFC4X3_RC4_IfcFillStyleSelect_type = 0;
select_type* IFC4X3_RC4_IfcGeometricSetSelect_type = 0;
select_type* IFC4X3_RC4_IfcGridPlacementDirectionSelect_type = 0;
select_type* IFC4X3_RC4_IfcHatchLineDistanceSelect_type = 0;
select_type* IFC4X3_RC4_IfcImpactProtectionDeviceTypeSelect_type = 0;
select_type* IFC4X3_RC4_IfcInterferenceSelect_type = 0;
select_type* IFC4X3_RC4_IfcLayeredItem_type = 0;
select_type* IFC4X3_RC4_IfcLibrarySelect_type = 0;
select_type* IFC4X3_RC4_IfcLightDistributionDataSourceSelect_type = 0;
select_type* IFC4X3_RC4_IfcMaterialSelect_type = 0;
select_type* IFC4X3_RC4_IfcMeasureValue_type = 0;
select_type* IFC4X3_RC4_IfcMetricValueSelect_type = 0;
select_type* IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionSelect_type = 0;
select_type* IFC4X3_RC4_IfcModulusOfSubgradeReactionSelect_type = 0;
select_type* IFC4X3_RC4_IfcModulusOfTranslationalSubgradeReactionSelect_type = 0;
select_type* IFC4X3_RC4_IfcObjectReferenceSelect_type = 0;
select_type* IFC4X3_RC4_IfcPointOrVertexPoint_type = 0;
select_type* IFC4X3_RC4_IfcProcessSelect_type = 0;
select_type* IFC4X3_RC4_IfcProductRepresentationSelect_type = 0;
select_type* IFC4X3_RC4_IfcProductSelect_type = 0;
select_type* IFC4X3_RC4_IfcPropertySetDefinitionSelect_type = 0;
select_type* IFC4X3_RC4_IfcResourceObjectSelect_type = 0;
select_type* IFC4X3_RC4_IfcResourceSelect_type = 0;
select_type* IFC4X3_RC4_IfcRotationalStiffnessSelect_type = 0;
select_type* IFC4X3_RC4_IfcSegmentIndexSelect_type = 0;
select_type* IFC4X3_RC4_IfcShell_type = 0;
select_type* IFC4X3_RC4_IfcSimpleValue_type = 0;
select_type* IFC4X3_RC4_IfcSizeSelect_type = 0;
select_type* IFC4X3_RC4_IfcSolidOrShell_type = 0;
select_type* IFC4X3_RC4_IfcSpaceBoundarySelect_type = 0;
select_type* IFC4X3_RC4_IfcSpatialReferenceSelect_type = 0;
select_type* IFC4X3_RC4_IfcSpecularHighlightSelect_type = 0;
select_type* IFC4X3_RC4_IfcStructuralActivityAssignmentSelect_type = 0;
select_type* IFC4X3_RC4_IfcSurfaceOrFaceSurface_type = 0;
select_type* IFC4X3_RC4_IfcSurfaceStyleElementSelect_type = 0;
select_type* IFC4X3_RC4_IfcTextFontSelect_type = 0;
select_type* IFC4X3_RC4_IfcTimeOrRatioSelect_type = 0;
select_type* IFC4X3_RC4_IfcTranslationalStiffnessSelect_type = 0;
select_type* IFC4X3_RC4_IfcTransportElementTypeSelect_type = 0;
select_type* IFC4X3_RC4_IfcTrimmingSelect_type = 0;
select_type* IFC4X3_RC4_IfcUnit_type = 0;
select_type* IFC4X3_RC4_IfcValue_type = 0;
select_type* IFC4X3_RC4_IfcVectorOrDirection_type = 0;
select_type* IFC4X3_RC4_IfcWarpingStiffnessSelect_type = 0;
enumeration_type* IFC4X3_RC4_IfcActionRequestTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcActionSourceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcActionTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcActuatorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAddressTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAirTerminalBoxTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAirTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAirToAirHeatRecoveryTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAlarmTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAlignmentCantSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAlignmentHorizontalSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAlignmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAlignmentVerticalSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAnalysisModelTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAnalysisTheoryTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAnnotationTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcArithmeticOperatorEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAssemblyPlaceEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcAudioVisualApplianceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBSplineCurveForm_type = 0;
enumeration_type* IFC4X3_RC4_IfcBSplineSurfaceForm_type = 0;
enumeration_type* IFC4X3_RC4_IfcBeamTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBearingTypeDisplacementEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBearingTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBenchmarkEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBoilerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBooleanOperator_type = 0;
enumeration_type* IFC4X3_RC4_IfcBridgePartTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBridgeTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBuildingElementPartTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBuildingElementProxyTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBuildingSystemTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBuiltSystemTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcBurnerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCableCarrierFittingTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCableCarrierSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCableFittingTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCableSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCaissonFoundationTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcChangeActionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcChillerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcChimneyTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCoilTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcColumnTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCommunicationsApplianceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcComplexPropertyTemplateTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCompressorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCondenserTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcConnectionTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcConstraintEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcConstructionEquipmentResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcConstructionMaterialResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcConstructionProductResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcControllerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcConveyorSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCooledBeamTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCoolingTowerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCostItemTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCostScheduleTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCourseTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCoveringTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCrewResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCurtainWallTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcCurveInterpolationEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDamperTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDataOriginEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDerivedUnitEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDirectionSenseEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDiscreteAccessoryTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDistributionBoardTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDistributionChamberElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDistributionPortTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDistributionSystemEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDocumentConfidentialityEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDocumentStatusEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDoorPanelOperationEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDoorPanelPositionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDoorStyleConstructionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDoorStyleOperationEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDoorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDoorTypeOperationEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDuctFittingTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDuctSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcDuctSilencerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcEarthworksCutTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcEarthworksFillTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElectricApplianceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElectricDistributionBoardTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElectricFlowStorageDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElectricFlowTreatmentDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElectricGeneratorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElectricMotorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElectricTimeControlTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElementAssemblyTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcElementCompositionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcEngineTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcEvaporativeCoolerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcEvaporatorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcEventTriggerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcEventTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcExternalSpatialElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFacilityPartCommonTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFacilityUsageEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFanTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFastenerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFilterTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFireSuppressionTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFlowDirectionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFlowInstrumentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFlowMeterTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFootingTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcFurnitureTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcGeographicElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcGeometricProjectionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcGlobalOrLocalEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcGridTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcHeatExchangerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcHumidifierTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcImpactProtectionDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcInterceptorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcInternalOrExternalEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcInventoryTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcJunctionBoxTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcKnotType_type = 0;
enumeration_type* IFC4X3_RC4_IfcLaborResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcLampTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcLayerSetDirectionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcLightDistributionCurveEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcLightEmissionSourceEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcLightFixtureTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcLiquidTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcLoadGroupTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcLogicalOperatorEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcMarineFacilityTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcMarinePartTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcMechanicalFastenerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcMedicalDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcMemberTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcMobileTelecommunicationsApplianceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcMooringDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcMotorConnectionTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcNavigationElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcObjectTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcObjectiveEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcOccupantTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcOpeningElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcOutletTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPavementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPerformanceHistoryTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPermeableCoveringOperationEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPermitTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPhysicalOrVirtualEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPileConstructionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPileTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPipeFittingTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPipeSegmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPlateTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPreferredSurfaceCurveRepresentation_type = 0;
enumeration_type* IFC4X3_RC4_IfcProcedureTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcProfileTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcProjectOrderTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcProjectedOrTrueLengthEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcProjectionElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPropertySetTemplateTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcProtectiveDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcPumpTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRailTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRailingTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRailwayPartTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRailwayTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRampFlightTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRampTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRecurrenceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcReferentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcReflectanceMethodEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcReinforcedSoilTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcReinforcingBarRoleEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcReinforcingBarSurfaceEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcReinforcingBarTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcReinforcingMeshTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRoadPartTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRoadTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRoleEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcRoofTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSIPrefix_type = 0;
enumeration_type* IFC4X3_RC4_IfcSIUnitName_type = 0;
enumeration_type* IFC4X3_RC4_IfcSanitaryTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSectionTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSensorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSequenceEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcShadingDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSignTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSignalTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSimplePropertyTemplateTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSlabTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSolarDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSpaceHeaterTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSpaceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSpatialZoneTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcStackTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcStairFlightTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcStairTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcStateEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcStructuralCurveActivityTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcStructuralCurveMemberTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcStructuralSurfaceActivityTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcStructuralSurfaceMemberTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSubContractResourceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSurfaceFeatureTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSurfaceSide_type = 0;
enumeration_type* IFC4X3_RC4_IfcSwitchingDeviceTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcSystemFurnitureElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTankTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTaskDurationEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTaskTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTendonAnchorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTendonConduitTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTendonTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTextPath_type = 0;
enumeration_type* IFC4X3_RC4_IfcTimeSeriesDataTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTrackElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTransformerTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTransitionCode_type = 0;
enumeration_type* IFC4X3_RC4_IfcTransportElementFixedTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTransportElementNonFixedTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcTrimmingPreference_type = 0;
enumeration_type* IFC4X3_RC4_IfcTubeBundleTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcUnitEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcUnitaryControlElementTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcUnitaryEquipmentTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcValveTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcVibrationDamperTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcVibrationIsolatorTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcVoidingFeatureTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWallTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWasteTerminalTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWindowPanelOperationEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWindowPanelPositionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWindowStyleConstructionEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWindowStyleOperationEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWindowTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWindowTypePartitioningEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWorkCalendarTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWorkPlanTypeEnum_type = 0;
enumeration_type* IFC4X3_RC4_IfcWorkScheduleTypeEnum_type = 0;

class IFC4X3_RC4_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        switch(data->type()->index_in_schema()) {
            case 0: return new ::Ifc4x3_rc4::IfcAbsorbedDoseMeasure(data);
            case 1: return new ::Ifc4x3_rc4::IfcAccelerationMeasure(data);
            case 2: return new ::Ifc4x3_rc4::IfcActionRequest(data);
            case 3: return new ::Ifc4x3_rc4::IfcActionRequestTypeEnum(data);
            case 4: return new ::Ifc4x3_rc4::IfcActionSourceTypeEnum(data);
            case 5: return new ::Ifc4x3_rc4::IfcActionTypeEnum(data);
            case 6: return new ::Ifc4x3_rc4::IfcActor(data);
            case 7: return new ::Ifc4x3_rc4::IfcActorRole(data);
            case 9: return new ::Ifc4x3_rc4::IfcActuator(data);
            case 10: return new ::Ifc4x3_rc4::IfcActuatorType(data);
            case 11: return new ::Ifc4x3_rc4::IfcActuatorTypeEnum(data);
            case 12: return new ::Ifc4x3_rc4::IfcAddress(data);
            case 13: return new ::Ifc4x3_rc4::IfcAddressTypeEnum(data);
            case 14: return new ::Ifc4x3_rc4::IfcAdvancedBrep(data);
            case 15: return new ::Ifc4x3_rc4::IfcAdvancedBrepWithVoids(data);
            case 16: return new ::Ifc4x3_rc4::IfcAdvancedFace(data);
            case 17: return new ::Ifc4x3_rc4::IfcAirTerminal(data);
            case 18: return new ::Ifc4x3_rc4::IfcAirTerminalBox(data);
            case 19: return new ::Ifc4x3_rc4::IfcAirTerminalBoxType(data);
            case 20: return new ::Ifc4x3_rc4::IfcAirTerminalBoxTypeEnum(data);
            case 21: return new ::Ifc4x3_rc4::IfcAirTerminalType(data);
            case 22: return new ::Ifc4x3_rc4::IfcAirTerminalTypeEnum(data);
            case 23: return new ::Ifc4x3_rc4::IfcAirToAirHeatRecovery(data);
            case 24: return new ::Ifc4x3_rc4::IfcAirToAirHeatRecoveryType(data);
            case 25: return new ::Ifc4x3_rc4::IfcAirToAirHeatRecoveryTypeEnum(data);
            case 26: return new ::Ifc4x3_rc4::IfcAlarm(data);
            case 27: return new ::Ifc4x3_rc4::IfcAlarmType(data);
            case 28: return new ::Ifc4x3_rc4::IfcAlarmTypeEnum(data);
            case 29: return new ::Ifc4x3_rc4::IfcAlignment(data);
            case 30: return new ::Ifc4x3_rc4::IfcAlignmentCant(data);
            case 31: return new ::Ifc4x3_rc4::IfcAlignmentCantSegment(data);
            case 32: return new ::Ifc4x3_rc4::IfcAlignmentCantSegmentTypeEnum(data);
            case 33: return new ::Ifc4x3_rc4::IfcAlignmentHorizontal(data);
            case 34: return new ::Ifc4x3_rc4::IfcAlignmentHorizontalSegment(data);
            case 35: return new ::Ifc4x3_rc4::IfcAlignmentHorizontalSegmentTypeEnum(data);
            case 36: return new ::Ifc4x3_rc4::IfcAlignmentParameterSegment(data);
            case 37: return new ::Ifc4x3_rc4::IfcAlignmentSegment(data);
            case 38: return new ::Ifc4x3_rc4::IfcAlignmentTypeEnum(data);
            case 39: return new ::Ifc4x3_rc4::IfcAlignmentVertical(data);
            case 40: return new ::Ifc4x3_rc4::IfcAlignmentVerticalSegment(data);
            case 41: return new ::Ifc4x3_rc4::IfcAlignmentVerticalSegmentTypeEnum(data);
            case 42: return new ::Ifc4x3_rc4::IfcAmountOfSubstanceMeasure(data);
            case 43: return new ::Ifc4x3_rc4::IfcAnalysisModelTypeEnum(data);
            case 44: return new ::Ifc4x3_rc4::IfcAnalysisTheoryTypeEnum(data);
            case 45: return new ::Ifc4x3_rc4::IfcAngularVelocityMeasure(data);
            case 46: return new ::Ifc4x3_rc4::IfcAnnotation(data);
            case 47: return new ::Ifc4x3_rc4::IfcAnnotationFillArea(data);
            case 48: return new ::Ifc4x3_rc4::IfcAnnotationTypeEnum(data);
            case 49: return new ::Ifc4x3_rc4::IfcApplication(data);
            case 50: return new ::Ifc4x3_rc4::IfcAppliedValue(data);
            case 52: return new ::Ifc4x3_rc4::IfcApproval(data);
            case 53: return new ::Ifc4x3_rc4::IfcApprovalRelationship(data);
            case 54: return new ::Ifc4x3_rc4::IfcArbitraryClosedProfileDef(data);
            case 55: return new ::Ifc4x3_rc4::IfcArbitraryOpenProfileDef(data);
            case 56: return new ::Ifc4x3_rc4::IfcArbitraryProfileDefWithVoids(data);
            case 57: return new ::Ifc4x3_rc4::IfcArcIndex(data);
            case 58: return new ::Ifc4x3_rc4::IfcAreaDensityMeasure(data);
            case 59: return new ::Ifc4x3_rc4::IfcAreaMeasure(data);
            case 60: return new ::Ifc4x3_rc4::IfcArithmeticOperatorEnum(data);
            case 61: return new ::Ifc4x3_rc4::IfcAssemblyPlaceEnum(data);
            case 62: return new ::Ifc4x3_rc4::IfcAsset(data);
            case 63: return new ::Ifc4x3_rc4::IfcAsymmetricIShapeProfileDef(data);
            case 64: return new ::Ifc4x3_rc4::IfcAudioVisualAppliance(data);
            case 65: return new ::Ifc4x3_rc4::IfcAudioVisualApplianceType(data);
            case 66: return new ::Ifc4x3_rc4::IfcAudioVisualApplianceTypeEnum(data);
            case 67: return new ::Ifc4x3_rc4::IfcAxis1Placement(data);
            case 69: return new ::Ifc4x3_rc4::IfcAxis2Placement2D(data);
            case 70: return new ::Ifc4x3_rc4::IfcAxis2Placement3D(data);
            case 71: return new ::Ifc4x3_rc4::IfcAxis2PlacementLinear(data);
            case 72: return new ::Ifc4x3_rc4::IfcBeam(data);
            case 73: return new ::Ifc4x3_rc4::IfcBeamStandardCase(data);
            case 74: return new ::Ifc4x3_rc4::IfcBeamType(data);
            case 75: return new ::Ifc4x3_rc4::IfcBeamTypeEnum(data);
            case 76: return new ::Ifc4x3_rc4::IfcBearing(data);
            case 77: return new ::Ifc4x3_rc4::IfcBearingType(data);
            case 78: return new ::Ifc4x3_rc4::IfcBearingTypeDisplacementEnum(data);
            case 79: return new ::Ifc4x3_rc4::IfcBearingTypeEnum(data);
            case 80: return new ::Ifc4x3_rc4::IfcBenchmarkEnum(data);
            case 82: return new ::Ifc4x3_rc4::IfcBinary(data);
            case 83: return new ::Ifc4x3_rc4::IfcBlobTexture(data);
            case 84: return new ::Ifc4x3_rc4::IfcBlock(data);
            case 85: return new ::Ifc4x3_rc4::IfcBoiler(data);
            case 86: return new ::Ifc4x3_rc4::IfcBoilerType(data);
            case 87: return new ::Ifc4x3_rc4::IfcBoilerTypeEnum(data);
            case 88: return new ::Ifc4x3_rc4::IfcBoolean(data);
            case 89: return new ::Ifc4x3_rc4::IfcBooleanClippingResult(data);
            case 91: return new ::Ifc4x3_rc4::IfcBooleanOperator(data);
            case 92: return new ::Ifc4x3_rc4::IfcBooleanResult(data);
            case 93: return new ::Ifc4x3_rc4::IfcBorehole(data);
            case 94: return new ::Ifc4x3_rc4::IfcBoundaryCondition(data);
            case 95: return new ::Ifc4x3_rc4::IfcBoundaryCurve(data);
            case 96: return new ::Ifc4x3_rc4::IfcBoundaryEdgeCondition(data);
            case 97: return new ::Ifc4x3_rc4::IfcBoundaryFaceCondition(data);
            case 98: return new ::Ifc4x3_rc4::IfcBoundaryNodeCondition(data);
            case 99: return new ::Ifc4x3_rc4::IfcBoundaryNodeConditionWarping(data);
            case 100: return new ::Ifc4x3_rc4::IfcBoundedCurve(data);
            case 101: return new ::Ifc4x3_rc4::IfcBoundedSurface(data);
            case 102: return new ::Ifc4x3_rc4::IfcBoundingBox(data);
            case 103: return new ::Ifc4x3_rc4::IfcBoxAlignment(data);
            case 104: return new ::Ifc4x3_rc4::IfcBoxedHalfSpace(data);
            case 105: return new ::Ifc4x3_rc4::IfcBridge(data);
            case 106: return new ::Ifc4x3_rc4::IfcBridgePartTypeEnum(data);
            case 107: return new ::Ifc4x3_rc4::IfcBridgeTypeEnum(data);
            case 108: return new ::Ifc4x3_rc4::IfcBSplineCurve(data);
            case 109: return new ::Ifc4x3_rc4::IfcBSplineCurveForm(data);
            case 110: return new ::Ifc4x3_rc4::IfcBSplineCurveWithKnots(data);
            case 111: return new ::Ifc4x3_rc4::IfcBSplineSurface(data);
            case 112: return new ::Ifc4x3_rc4::IfcBSplineSurfaceForm(data);
            case 113: return new ::Ifc4x3_rc4::IfcBSplineSurfaceWithKnots(data);
            case 114: return new ::Ifc4x3_rc4::IfcBuilding(data);
            case 115: return new ::Ifc4x3_rc4::IfcBuildingElementPart(data);
            case 116: return new ::Ifc4x3_rc4::IfcBuildingElementPartType(data);
            case 117: return new ::Ifc4x3_rc4::IfcBuildingElementPartTypeEnum(data);
            case 118: return new ::Ifc4x3_rc4::IfcBuildingElementProxy(data);
            case 119: return new ::Ifc4x3_rc4::IfcBuildingElementProxyType(data);
            case 120: return new ::Ifc4x3_rc4::IfcBuildingElementProxyTypeEnum(data);
            case 121: return new ::Ifc4x3_rc4::IfcBuildingStorey(data);
            case 122: return new ::Ifc4x3_rc4::IfcBuildingSystem(data);
            case 123: return new ::Ifc4x3_rc4::IfcBuildingSystemTypeEnum(data);
            case 124: return new ::Ifc4x3_rc4::IfcBuiltElement(data);
            case 125: return new ::Ifc4x3_rc4::IfcBuiltElementType(data);
            case 126: return new ::Ifc4x3_rc4::IfcBuiltSystem(data);
            case 127: return new ::Ifc4x3_rc4::IfcBuiltSystemTypeEnum(data);
            case 128: return new ::Ifc4x3_rc4::IfcBurner(data);
            case 129: return new ::Ifc4x3_rc4::IfcBurnerType(data);
            case 130: return new ::Ifc4x3_rc4::IfcBurnerTypeEnum(data);
            case 131: return new ::Ifc4x3_rc4::IfcCableCarrierFitting(data);
            case 132: return new ::Ifc4x3_rc4::IfcCableCarrierFittingType(data);
            case 133: return new ::Ifc4x3_rc4::IfcCableCarrierFittingTypeEnum(data);
            case 134: return new ::Ifc4x3_rc4::IfcCableCarrierSegment(data);
            case 135: return new ::Ifc4x3_rc4::IfcCableCarrierSegmentType(data);
            case 136: return new ::Ifc4x3_rc4::IfcCableCarrierSegmentTypeEnum(data);
            case 137: return new ::Ifc4x3_rc4::IfcCableFitting(data);
            case 138: return new ::Ifc4x3_rc4::IfcCableFittingType(data);
            case 139: return new ::Ifc4x3_rc4::IfcCableFittingTypeEnum(data);
            case 140: return new ::Ifc4x3_rc4::IfcCableSegment(data);
            case 141: return new ::Ifc4x3_rc4::IfcCableSegmentType(data);
            case 142: return new ::Ifc4x3_rc4::IfcCableSegmentTypeEnum(data);
            case 143: return new ::Ifc4x3_rc4::IfcCaissonFoundation(data);
            case 144: return new ::Ifc4x3_rc4::IfcCaissonFoundationType(data);
            case 145: return new ::Ifc4x3_rc4::IfcCaissonFoundationTypeEnum(data);
            case 146: return new ::Ifc4x3_rc4::IfcCardinalPointReference(data);
            case 147: return new ::Ifc4x3_rc4::IfcCartesianPoint(data);
            case 148: return new ::Ifc4x3_rc4::IfcCartesianPointList(data);
            case 149: return new ::Ifc4x3_rc4::IfcCartesianPointList2D(data);
            case 150: return new ::Ifc4x3_rc4::IfcCartesianPointList3D(data);
            case 151: return new ::Ifc4x3_rc4::IfcCartesianTransformationOperator(data);
            case 152: return new ::Ifc4x3_rc4::IfcCartesianTransformationOperator2D(data);
            case 153: return new ::Ifc4x3_rc4::IfcCartesianTransformationOperator2DnonUniform(data);
            case 154: return new ::Ifc4x3_rc4::IfcCartesianTransformationOperator3D(data);
            case 155: return new ::Ifc4x3_rc4::IfcCartesianTransformationOperator3DnonUniform(data);
            case 156: return new ::Ifc4x3_rc4::IfcCenterLineProfileDef(data);
            case 157: return new ::Ifc4x3_rc4::IfcChangeActionEnum(data);
            case 158: return new ::Ifc4x3_rc4::IfcChiller(data);
            case 159: return new ::Ifc4x3_rc4::IfcChillerType(data);
            case 160: return new ::Ifc4x3_rc4::IfcChillerTypeEnum(data);
            case 161: return new ::Ifc4x3_rc4::IfcChimney(data);
            case 162: return new ::Ifc4x3_rc4::IfcChimneyType(data);
            case 163: return new ::Ifc4x3_rc4::IfcChimneyTypeEnum(data);
            case 164: return new ::Ifc4x3_rc4::IfcCircle(data);
            case 165: return new ::Ifc4x3_rc4::IfcCircleHollowProfileDef(data);
            case 166: return new ::Ifc4x3_rc4::IfcCircleProfileDef(data);
            case 167: return new ::Ifc4x3_rc4::IfcCivilElement(data);
            case 168: return new ::Ifc4x3_rc4::IfcCivilElementType(data);
            case 169: return new ::Ifc4x3_rc4::IfcClassification(data);
            case 170: return new ::Ifc4x3_rc4::IfcClassificationReference(data);
            case 173: return new ::Ifc4x3_rc4::IfcClosedShell(data);
            case 174: return new ::Ifc4x3_rc4::IfcClothoid(data);
            case 175: return new ::Ifc4x3_rc4::IfcCoil(data);
            case 176: return new ::Ifc4x3_rc4::IfcCoilType(data);
            case 177: return new ::Ifc4x3_rc4::IfcCoilTypeEnum(data);
            case 180: return new ::Ifc4x3_rc4::IfcColourRgb(data);
            case 181: return new ::Ifc4x3_rc4::IfcColourRgbList(data);
            case 182: return new ::Ifc4x3_rc4::IfcColourSpecification(data);
            case 183: return new ::Ifc4x3_rc4::IfcColumn(data);
            case 184: return new ::Ifc4x3_rc4::IfcColumnStandardCase(data);
            case 185: return new ::Ifc4x3_rc4::IfcColumnType(data);
            case 186: return new ::Ifc4x3_rc4::IfcColumnTypeEnum(data);
            case 187: return new ::Ifc4x3_rc4::IfcCommunicationsAppliance(data);
            case 188: return new ::Ifc4x3_rc4::IfcCommunicationsApplianceType(data);
            case 189: return new ::Ifc4x3_rc4::IfcCommunicationsApplianceTypeEnum(data);
            case 190: return new ::Ifc4x3_rc4::IfcComplexNumber(data);
            case 191: return new ::Ifc4x3_rc4::IfcComplexProperty(data);
            case 192: return new ::Ifc4x3_rc4::IfcComplexPropertyTemplate(data);
            case 193: return new ::Ifc4x3_rc4::IfcComplexPropertyTemplateTypeEnum(data);
            case 194: return new ::Ifc4x3_rc4::IfcCompositeCurve(data);
            case 195: return new ::Ifc4x3_rc4::IfcCompositeCurveOnSurface(data);
            case 196: return new ::Ifc4x3_rc4::IfcCompositeCurveSegment(data);
            case 197: return new ::Ifc4x3_rc4::IfcCompositeProfileDef(data);
            case 198: return new ::Ifc4x3_rc4::IfcCompoundPlaneAngleMeasure(data);
            case 199: return new ::Ifc4x3_rc4::IfcCompressor(data);
            case 200: return new ::Ifc4x3_rc4::IfcCompressorType(data);
            case 201: return new ::Ifc4x3_rc4::IfcCompressorTypeEnum(data);
            case 202: return new ::Ifc4x3_rc4::IfcCondenser(data);
            case 203: return new ::Ifc4x3_rc4::IfcCondenserType(data);
            case 204: return new ::Ifc4x3_rc4::IfcCondenserTypeEnum(data);
            case 205: return new ::Ifc4x3_rc4::IfcConic(data);
            case 206: return new ::Ifc4x3_rc4::IfcConnectedFaceSet(data);
            case 207: return new ::Ifc4x3_rc4::IfcConnectionCurveGeometry(data);
            case 208: return new ::Ifc4x3_rc4::IfcConnectionGeometry(data);
            case 209: return new ::Ifc4x3_rc4::IfcConnectionPointEccentricity(data);
            case 210: return new ::Ifc4x3_rc4::IfcConnectionPointGeometry(data);
            case 211: return new ::Ifc4x3_rc4::IfcConnectionSurfaceGeometry(data);
            case 212: return new ::Ifc4x3_rc4::IfcConnectionTypeEnum(data);
            case 213: return new ::Ifc4x3_rc4::IfcConnectionVolumeGeometry(data);
            case 214: return new ::Ifc4x3_rc4::IfcConstraint(data);
            case 215: return new ::Ifc4x3_rc4::IfcConstraintEnum(data);
            case 216: return new ::Ifc4x3_rc4::IfcConstructionEquipmentResource(data);
            case 217: return new ::Ifc4x3_rc4::IfcConstructionEquipmentResourceType(data);
            case 218: return new ::Ifc4x3_rc4::IfcConstructionEquipmentResourceTypeEnum(data);
            case 219: return new ::Ifc4x3_rc4::IfcConstructionMaterialResource(data);
            case 220: return new ::Ifc4x3_rc4::IfcConstructionMaterialResourceType(data);
            case 221: return new ::Ifc4x3_rc4::IfcConstructionMaterialResourceTypeEnum(data);
            case 222: return new ::Ifc4x3_rc4::IfcConstructionProductResource(data);
            case 223: return new ::Ifc4x3_rc4::IfcConstructionProductResourceType(data);
            case 224: return new ::Ifc4x3_rc4::IfcConstructionProductResourceTypeEnum(data);
            case 225: return new ::Ifc4x3_rc4::IfcConstructionResource(data);
            case 226: return new ::Ifc4x3_rc4::IfcConstructionResourceType(data);
            case 227: return new ::Ifc4x3_rc4::IfcContext(data);
            case 228: return new ::Ifc4x3_rc4::IfcContextDependentMeasure(data);
            case 229: return new ::Ifc4x3_rc4::IfcContextDependentUnit(data);
            case 230: return new ::Ifc4x3_rc4::IfcControl(data);
            case 231: return new ::Ifc4x3_rc4::IfcController(data);
            case 232: return new ::Ifc4x3_rc4::IfcControllerType(data);
            case 233: return new ::Ifc4x3_rc4::IfcControllerTypeEnum(data);
            case 234: return new ::Ifc4x3_rc4::IfcConversionBasedUnit(data);
            case 235: return new ::Ifc4x3_rc4::IfcConversionBasedUnitWithOffset(data);
            case 236: return new ::Ifc4x3_rc4::IfcConveyorSegment(data);
            case 237: return new ::Ifc4x3_rc4::IfcConveyorSegmentType(data);
            case 238: return new ::Ifc4x3_rc4::IfcConveyorSegmentTypeEnum(data);
            case 239: return new ::Ifc4x3_rc4::IfcCooledBeam(data);
            case 240: return new ::Ifc4x3_rc4::IfcCooledBeamType(data);
            case 241: return new ::Ifc4x3_rc4::IfcCooledBeamTypeEnum(data);
            case 242: return new ::Ifc4x3_rc4::IfcCoolingTower(data);
            case 243: return new ::Ifc4x3_rc4::IfcCoolingTowerType(data);
            case 244: return new ::Ifc4x3_rc4::IfcCoolingTowerTypeEnum(data);
            case 245: return new ::Ifc4x3_rc4::IfcCoordinateOperation(data);
            case 246: return new ::Ifc4x3_rc4::IfcCoordinateReferenceSystem(data);
            case 248: return new ::Ifc4x3_rc4::IfcCosine(data);
            case 249: return new ::Ifc4x3_rc4::IfcCostItem(data);
            case 250: return new ::Ifc4x3_rc4::IfcCostItemTypeEnum(data);
            case 251: return new ::Ifc4x3_rc4::IfcCostSchedule(data);
            case 252: return new ::Ifc4x3_rc4::IfcCostScheduleTypeEnum(data);
            case 253: return new ::Ifc4x3_rc4::IfcCostValue(data);
            case 254: return new ::Ifc4x3_rc4::IfcCountMeasure(data);
            case 255: return new ::Ifc4x3_rc4::IfcCourse(data);
            case 256: return new ::Ifc4x3_rc4::IfcCourseType(data);
            case 257: return new ::Ifc4x3_rc4::IfcCourseTypeEnum(data);
            case 258: return new ::Ifc4x3_rc4::IfcCovering(data);
            case 259: return new ::Ifc4x3_rc4::IfcCoveringType(data);
            case 260: return new ::Ifc4x3_rc4::IfcCoveringTypeEnum(data);
            case 261: return new ::Ifc4x3_rc4::IfcCrewResource(data);
            case 262: return new ::Ifc4x3_rc4::IfcCrewResourceType(data);
            case 263: return new ::Ifc4x3_rc4::IfcCrewResourceTypeEnum(data);
            case 264: return new ::Ifc4x3_rc4::IfcCsgPrimitive3D(data);
            case 266: return new ::Ifc4x3_rc4::IfcCsgSolid(data);
            case 267: return new ::Ifc4x3_rc4::IfcCShapeProfileDef(data);
            case 268: return new ::Ifc4x3_rc4::IfcCurrencyRelationship(data);
            case 269: return new ::Ifc4x3_rc4::IfcCurtainWall(data);
            case 270: return new ::Ifc4x3_rc4::IfcCurtainWallType(data);
            case 271: return new ::Ifc4x3_rc4::IfcCurtainWallTypeEnum(data);
            case 272: return new ::Ifc4x3_rc4::IfcCurvatureMeasure(data);
            case 273: return new ::Ifc4x3_rc4::IfcCurve(data);
            case 274: return new ::Ifc4x3_rc4::IfcCurveBoundedPlane(data);
            case 275: return new ::Ifc4x3_rc4::IfcCurveBoundedSurface(data);
            case 277: return new ::Ifc4x3_rc4::IfcCurveInterpolationEnum(data);
            case 281: return new ::Ifc4x3_rc4::IfcCurveSegment(data);
            case 282: return new ::Ifc4x3_rc4::IfcCurveStyle(data);
            case 283: return new ::Ifc4x3_rc4::IfcCurveStyleFont(data);
            case 284: return new ::Ifc4x3_rc4::IfcCurveStyleFontAndScaling(data);
            case 285: return new ::Ifc4x3_rc4::IfcCurveStyleFontPattern(data);
            case 287: return new ::Ifc4x3_rc4::IfcCylindricalSurface(data);
            case 288: return new ::Ifc4x3_rc4::IfcDamper(data);
            case 289: return new ::Ifc4x3_rc4::IfcDamperType(data);
            case 290: return new ::Ifc4x3_rc4::IfcDamperTypeEnum(data);
            case 291: return new ::Ifc4x3_rc4::IfcDataOriginEnum(data);
            case 292: return new ::Ifc4x3_rc4::IfcDate(data);
            case 293: return new ::Ifc4x3_rc4::IfcDateTime(data);
            case 294: return new ::Ifc4x3_rc4::IfcDayInMonthNumber(data);
            case 295: return new ::Ifc4x3_rc4::IfcDayInWeekNumber(data);
            case 296: return new ::Ifc4x3_rc4::IfcDeepFoundation(data);
            case 297: return new ::Ifc4x3_rc4::IfcDeepFoundationType(data);
            case 300: return new ::Ifc4x3_rc4::IfcDerivedProfileDef(data);
            case 301: return new ::Ifc4x3_rc4::IfcDerivedUnit(data);
            case 302: return new ::Ifc4x3_rc4::IfcDerivedUnitElement(data);
            case 303: return new ::Ifc4x3_rc4::IfcDerivedUnitEnum(data);
            case 304: return new ::Ifc4x3_rc4::IfcDescriptiveMeasure(data);
            case 305: return new ::Ifc4x3_rc4::IfcDimensionalExponents(data);
            case 306: return new ::Ifc4x3_rc4::IfcDimensionCount(data);
            case 307: return new ::Ifc4x3_rc4::IfcDirection(data);
            case 308: return new ::Ifc4x3_rc4::IfcDirectionSenseEnum(data);
            case 309: return new ::Ifc4x3_rc4::IfcDirectrixCurveSweptAreaSolid(data);
            case 310: return new ::Ifc4x3_rc4::IfcDirectrixDerivedReferenceSweptAreaSolid(data);
            case 311: return new ::Ifc4x3_rc4::IfcDiscreteAccessory(data);
            case 312: return new ::Ifc4x3_rc4::IfcDiscreteAccessoryType(data);
            case 313: return new ::Ifc4x3_rc4::IfcDiscreteAccessoryTypeEnum(data);
            case 314: return new ::Ifc4x3_rc4::IfcDistributionBoard(data);
            case 315: return new ::Ifc4x3_rc4::IfcDistributionBoardType(data);
            case 316: return new ::Ifc4x3_rc4::IfcDistributionBoardTypeEnum(data);
            case 317: return new ::Ifc4x3_rc4::IfcDistributionChamberElement(data);
            case 318: return new ::Ifc4x3_rc4::IfcDistributionChamberElementType(data);
            case 319: return new ::Ifc4x3_rc4::IfcDistributionChamberElementTypeEnum(data);
            case 320: return new ::Ifc4x3_rc4::IfcDistributionCircuit(data);
            case 321: return new ::Ifc4x3_rc4::IfcDistributionControlElement(data);
            case 322: return new ::Ifc4x3_rc4::IfcDistributionControlElementType(data);
            case 323: return new ::Ifc4x3_rc4::IfcDistributionElement(data);
            case 324: return new ::Ifc4x3_rc4::IfcDistributionElementType(data);
            case 325: return new ::Ifc4x3_rc4::IfcDistributionFlowElement(data);
            case 326: return new ::Ifc4x3_rc4::IfcDistributionFlowElementType(data);
            case 327: return new ::Ifc4x3_rc4::IfcDistributionPort(data);
            case 328: return new ::Ifc4x3_rc4::IfcDistributionPortTypeEnum(data);
            case 329: return new ::Ifc4x3_rc4::IfcDistributionSystem(data);
            case 330: return new ::Ifc4x3_rc4::IfcDistributionSystemEnum(data);
            case 331: return new ::Ifc4x3_rc4::IfcDocumentConfidentialityEnum(data);
            case 332: return new ::Ifc4x3_rc4::IfcDocumentInformation(data);
            case 333: return new ::Ifc4x3_rc4::IfcDocumentInformationRelationship(data);
            case 334: return new ::Ifc4x3_rc4::IfcDocumentReference(data);
            case 336: return new ::Ifc4x3_rc4::IfcDocumentStatusEnum(data);
            case 337: return new ::Ifc4x3_rc4::IfcDoor(data);
            case 338: return new ::Ifc4x3_rc4::IfcDoorLiningProperties(data);
            case 339: return new ::Ifc4x3_rc4::IfcDoorPanelOperationEnum(data);
            case 340: return new ::Ifc4x3_rc4::IfcDoorPanelPositionEnum(data);
            case 341: return new ::Ifc4x3_rc4::IfcDoorPanelProperties(data);
            case 342: return new ::Ifc4x3_rc4::IfcDoorStandardCase(data);
            case 343: return new ::Ifc4x3_rc4::IfcDoorStyle(data);
            case 344: return new ::Ifc4x3_rc4::IfcDoorStyleConstructionEnum(data);
            case 345: return new ::Ifc4x3_rc4::IfcDoorStyleOperationEnum(data);
            case 346: return new ::Ifc4x3_rc4::IfcDoorType(data);
            case 347: return new ::Ifc4x3_rc4::IfcDoorTypeEnum(data);
            case 348: return new ::Ifc4x3_rc4::IfcDoorTypeOperationEnum(data);
            case 349: return new ::Ifc4x3_rc4::IfcDoseEquivalentMeasure(data);
            case 350: return new ::Ifc4x3_rc4::IfcDraughtingPreDefinedColour(data);
            case 351: return new ::Ifc4x3_rc4::IfcDraughtingPreDefinedCurveFont(data);
            case 352: return new ::Ifc4x3_rc4::IfcDuctFitting(data);
            case 353: return new ::Ifc4x3_rc4::IfcDuctFittingType(data);
            case 354: return new ::Ifc4x3_rc4::IfcDuctFittingTypeEnum(data);
            case 355: return new ::Ifc4x3_rc4::IfcDuctSegment(data);
            case 356: return new ::Ifc4x3_rc4::IfcDuctSegmentType(data);
            case 357: return new ::Ifc4x3_rc4::IfcDuctSegmentTypeEnum(data);
            case 358: return new ::Ifc4x3_rc4::IfcDuctSilencer(data);
            case 359: return new ::Ifc4x3_rc4::IfcDuctSilencerType(data);
            case 360: return new ::Ifc4x3_rc4::IfcDuctSilencerTypeEnum(data);
            case 361: return new ::Ifc4x3_rc4::IfcDuration(data);
            case 362: return new ::Ifc4x3_rc4::IfcDynamicViscosityMeasure(data);
            case 363: return new ::Ifc4x3_rc4::IfcEarthworksCut(data);
            case 364: return new ::Ifc4x3_rc4::IfcEarthworksCutTypeEnum(data);
            case 365: return new ::Ifc4x3_rc4::IfcEarthworksElement(data);
            case 366: return new ::Ifc4x3_rc4::IfcEarthworksFill(data);
            case 367: return new ::Ifc4x3_rc4::IfcEarthworksFillTypeEnum(data);
            case 368: return new ::Ifc4x3_rc4::IfcEdge(data);
            case 369: return new ::Ifc4x3_rc4::IfcEdgeCurve(data);
            case 370: return new ::Ifc4x3_rc4::IfcEdgeLoop(data);
            case 371: return new ::Ifc4x3_rc4::IfcElectricAppliance(data);
            case 372: return new ::Ifc4x3_rc4::IfcElectricApplianceType(data);
            case 373: return new ::Ifc4x3_rc4::IfcElectricApplianceTypeEnum(data);
            case 374: return new ::Ifc4x3_rc4::IfcElectricCapacitanceMeasure(data);
            case 375: return new ::Ifc4x3_rc4::IfcElectricChargeMeasure(data);
            case 376: return new ::Ifc4x3_rc4::IfcElectricConductanceMeasure(data);
            case 377: return new ::Ifc4x3_rc4::IfcElectricCurrentMeasure(data);
            case 378: return new ::Ifc4x3_rc4::IfcElectricDistributionBoard(data);
            case 379: return new ::Ifc4x3_rc4::IfcElectricDistributionBoardType(data);
            case 380: return new ::Ifc4x3_rc4::IfcElectricDistributionBoardTypeEnum(data);
            case 381: return new ::Ifc4x3_rc4::IfcElectricFlowStorageDevice(data);
            case 382: return new ::Ifc4x3_rc4::IfcElectricFlowStorageDeviceType(data);
            case 383: return new ::Ifc4x3_rc4::IfcElectricFlowStorageDeviceTypeEnum(data);
            case 384: return new ::Ifc4x3_rc4::IfcElectricFlowTreatmentDevice(data);
            case 385: return new ::Ifc4x3_rc4::IfcElectricFlowTreatmentDeviceType(data);
            case 386: return new ::Ifc4x3_rc4::IfcElectricFlowTreatmentDeviceTypeEnum(data);
            case 387: return new ::Ifc4x3_rc4::IfcElectricGenerator(data);
            case 388: return new ::Ifc4x3_rc4::IfcElectricGeneratorType(data);
            case 389: return new ::Ifc4x3_rc4::IfcElectricGeneratorTypeEnum(data);
            case 390: return new ::Ifc4x3_rc4::IfcElectricMotor(data);
            case 391: return new ::Ifc4x3_rc4::IfcElectricMotorType(data);
            case 392: return new ::Ifc4x3_rc4::IfcElectricMotorTypeEnum(data);
            case 393: return new ::Ifc4x3_rc4::IfcElectricResistanceMeasure(data);
            case 394: return new ::Ifc4x3_rc4::IfcElectricTimeControl(data);
            case 395: return new ::Ifc4x3_rc4::IfcElectricTimeControlType(data);
            case 396: return new ::Ifc4x3_rc4::IfcElectricTimeControlTypeEnum(data);
            case 397: return new ::Ifc4x3_rc4::IfcElectricVoltageMeasure(data);
            case 398: return new ::Ifc4x3_rc4::IfcElement(data);
            case 399: return new ::Ifc4x3_rc4::IfcElementarySurface(data);
            case 400: return new ::Ifc4x3_rc4::IfcElementAssembly(data);
            case 401: return new ::Ifc4x3_rc4::IfcElementAssemblyType(data);
            case 402: return new ::Ifc4x3_rc4::IfcElementAssemblyTypeEnum(data);
            case 403: return new ::Ifc4x3_rc4::IfcElementComponent(data);
            case 404: return new ::Ifc4x3_rc4::IfcElementComponentType(data);
            case 405: return new ::Ifc4x3_rc4::IfcElementCompositionEnum(data);
            case 406: return new ::Ifc4x3_rc4::IfcElementQuantity(data);
            case 407: return new ::Ifc4x3_rc4::IfcElementType(data);
            case 408: return new ::Ifc4x3_rc4::IfcEllipse(data);
            case 409: return new ::Ifc4x3_rc4::IfcEllipseProfileDef(data);
            case 410: return new ::Ifc4x3_rc4::IfcEnergyConversionDevice(data);
            case 411: return new ::Ifc4x3_rc4::IfcEnergyConversionDeviceType(data);
            case 412: return new ::Ifc4x3_rc4::IfcEnergyMeasure(data);
            case 413: return new ::Ifc4x3_rc4::IfcEngine(data);
            case 414: return new ::Ifc4x3_rc4::IfcEngineType(data);
            case 415: return new ::Ifc4x3_rc4::IfcEngineTypeEnum(data);
            case 416: return new ::Ifc4x3_rc4::IfcEvaporativeCooler(data);
            case 417: return new ::Ifc4x3_rc4::IfcEvaporativeCoolerType(data);
            case 418: return new ::Ifc4x3_rc4::IfcEvaporativeCoolerTypeEnum(data);
            case 419: return new ::Ifc4x3_rc4::IfcEvaporator(data);
            case 420: return new ::Ifc4x3_rc4::IfcEvaporatorType(data);
            case 421: return new ::Ifc4x3_rc4::IfcEvaporatorTypeEnum(data);
            case 422: return new ::Ifc4x3_rc4::IfcEvent(data);
            case 423: return new ::Ifc4x3_rc4::IfcEventTime(data);
            case 424: return new ::Ifc4x3_rc4::IfcEventTriggerTypeEnum(data);
            case 425: return new ::Ifc4x3_rc4::IfcEventType(data);
            case 426: return new ::Ifc4x3_rc4::IfcEventTypeEnum(data);
            case 427: return new ::Ifc4x3_rc4::IfcExtendedProperties(data);
            case 428: return new ::Ifc4x3_rc4::IfcExternalInformation(data);
            case 429: return new ::Ifc4x3_rc4::IfcExternallyDefinedHatchStyle(data);
            case 430: return new ::Ifc4x3_rc4::IfcExternallyDefinedSurfaceStyle(data);
            case 431: return new ::Ifc4x3_rc4::IfcExternallyDefinedTextFont(data);
            case 432: return new ::Ifc4x3_rc4::IfcExternalReference(data);
            case 433: return new ::Ifc4x3_rc4::IfcExternalReferenceRelationship(data);
            case 434: return new ::Ifc4x3_rc4::IfcExternalSpatialElement(data);
            case 435: return new ::Ifc4x3_rc4::IfcExternalSpatialElementTypeEnum(data);
            case 436: return new ::Ifc4x3_rc4::IfcExternalSpatialStructureElement(data);
            case 437: return new ::Ifc4x3_rc4::IfcExtrudedAreaSolid(data);
            case 438: return new ::Ifc4x3_rc4::IfcExtrudedAreaSolidTapered(data);
            case 439: return new ::Ifc4x3_rc4::IfcFace(data);
            case 440: return new ::Ifc4x3_rc4::IfcFaceBasedSurfaceModel(data);
            case 441: return new ::Ifc4x3_rc4::IfcFaceBound(data);
            case 442: return new ::Ifc4x3_rc4::IfcFaceOuterBound(data);
            case 443: return new ::Ifc4x3_rc4::IfcFaceSurface(data);
            case 444: return new ::Ifc4x3_rc4::IfcFacetedBrep(data);
            case 445: return new ::Ifc4x3_rc4::IfcFacetedBrepWithVoids(data);
            case 446: return new ::Ifc4x3_rc4::IfcFacility(data);
            case 447: return new ::Ifc4x3_rc4::IfcFacilityPart(data);
            case 448: return new ::Ifc4x3_rc4::IfcFacilityPartCommonTypeEnum(data);
            case 450: return new ::Ifc4x3_rc4::IfcFacilityUsageEnum(data);
            case 451: return new ::Ifc4x3_rc4::IfcFailureConnectionCondition(data);
            case 452: return new ::Ifc4x3_rc4::IfcFan(data);
            case 453: return new ::Ifc4x3_rc4::IfcFanType(data);
            case 454: return new ::Ifc4x3_rc4::IfcFanTypeEnum(data);
            case 455: return new ::Ifc4x3_rc4::IfcFastener(data);
            case 456: return new ::Ifc4x3_rc4::IfcFastenerType(data);
            case 457: return new ::Ifc4x3_rc4::IfcFastenerTypeEnum(data);
            case 458: return new ::Ifc4x3_rc4::IfcFeatureElement(data);
            case 459: return new ::Ifc4x3_rc4::IfcFeatureElementAddition(data);
            case 460: return new ::Ifc4x3_rc4::IfcFeatureElementSubtraction(data);
            case 461: return new ::Ifc4x3_rc4::IfcFillAreaStyle(data);
            case 462: return new ::Ifc4x3_rc4::IfcFillAreaStyleHatching(data);
            case 463: return new ::Ifc4x3_rc4::IfcFillAreaStyleTiles(data);
            case 465: return new ::Ifc4x3_rc4::IfcFilter(data);
            case 466: return new ::Ifc4x3_rc4::IfcFilterType(data);
            case 467: return new ::Ifc4x3_rc4::IfcFilterTypeEnum(data);
            case 468: return new ::Ifc4x3_rc4::IfcFireSuppressionTerminal(data);
            case 469: return new ::Ifc4x3_rc4::IfcFireSuppressionTerminalType(data);
            case 470: return new ::Ifc4x3_rc4::IfcFireSuppressionTerminalTypeEnum(data);
            case 471: return new ::Ifc4x3_rc4::IfcFixedReferenceSweptAreaSolid(data);
            case 472: return new ::Ifc4x3_rc4::IfcFlowController(data);
            case 473: return new ::Ifc4x3_rc4::IfcFlowControllerType(data);
            case 474: return new ::Ifc4x3_rc4::IfcFlowDirectionEnum(data);
            case 475: return new ::Ifc4x3_rc4::IfcFlowFitting(data);
            case 476: return new ::Ifc4x3_rc4::IfcFlowFittingType(data);
            case 477: return new ::Ifc4x3_rc4::IfcFlowInstrument(data);
            case 478: return new ::Ifc4x3_rc4::IfcFlowInstrumentType(data);
            case 479: return new ::Ifc4x3_rc4::IfcFlowInstrumentTypeEnum(data);
            case 480: return new ::Ifc4x3_rc4::IfcFlowMeter(data);
            case 481: return new ::Ifc4x3_rc4::IfcFlowMeterType(data);
            case 482: return new ::Ifc4x3_rc4::IfcFlowMeterTypeEnum(data);
            case 483: return new ::Ifc4x3_rc4::IfcFlowMovingDevice(data);
            case 484: return new ::Ifc4x3_rc4::IfcFlowMovingDeviceType(data);
            case 485: return new ::Ifc4x3_rc4::IfcFlowSegment(data);
            case 486: return new ::Ifc4x3_rc4::IfcFlowSegmentType(data);
            case 487: return new ::Ifc4x3_rc4::IfcFlowStorageDevice(data);
            case 488: return new ::Ifc4x3_rc4::IfcFlowStorageDeviceType(data);
            case 489: return new ::Ifc4x3_rc4::IfcFlowTerminal(data);
            case 490: return new ::Ifc4x3_rc4::IfcFlowTerminalType(data);
            case 491: return new ::Ifc4x3_rc4::IfcFlowTreatmentDevice(data);
            case 492: return new ::Ifc4x3_rc4::IfcFlowTreatmentDeviceType(data);
            case 493: return new ::Ifc4x3_rc4::IfcFontStyle(data);
            case 494: return new ::Ifc4x3_rc4::IfcFontVariant(data);
            case 495: return new ::Ifc4x3_rc4::IfcFontWeight(data);
            case 496: return new ::Ifc4x3_rc4::IfcFooting(data);
            case 497: return new ::Ifc4x3_rc4::IfcFootingType(data);
            case 498: return new ::Ifc4x3_rc4::IfcFootingTypeEnum(data);
            case 499: return new ::Ifc4x3_rc4::IfcForceMeasure(data);
            case 500: return new ::Ifc4x3_rc4::IfcFrequencyMeasure(data);
            case 501: return new ::Ifc4x3_rc4::IfcFurnishingElement(data);
            case 502: return new ::Ifc4x3_rc4::IfcFurnishingElementType(data);
            case 503: return new ::Ifc4x3_rc4::IfcFurniture(data);
            case 504: return new ::Ifc4x3_rc4::IfcFurnitureType(data);
            case 505: return new ::Ifc4x3_rc4::IfcFurnitureTypeEnum(data);
            case 506: return new ::Ifc4x3_rc4::IfcGeographicElement(data);
            case 507: return new ::Ifc4x3_rc4::IfcGeographicElementType(data);
            case 508: return new ::Ifc4x3_rc4::IfcGeographicElementTypeEnum(data);
            case 509: return new ::Ifc4x3_rc4::IfcGeometricCurveSet(data);
            case 510: return new ::Ifc4x3_rc4::IfcGeometricProjectionEnum(data);
            case 511: return new ::Ifc4x3_rc4::IfcGeometricRepresentationContext(data);
            case 512: return new ::Ifc4x3_rc4::IfcGeometricRepresentationItem(data);
            case 513: return new ::Ifc4x3_rc4::IfcGeometricRepresentationSubContext(data);
            case 514: return new ::Ifc4x3_rc4::IfcGeometricSet(data);
            case 516: return new ::Ifc4x3_rc4::IfcGeomodel(data);
            case 517: return new ::Ifc4x3_rc4::IfcGeoslice(data);
            case 518: return new ::Ifc4x3_rc4::IfcGeotechnicalAssembly(data);
            case 519: return new ::Ifc4x3_rc4::IfcGeotechnicalElement(data);
            case 520: return new ::Ifc4x3_rc4::IfcGeotechnicalStratum(data);
            case 521: return new ::Ifc4x3_rc4::IfcGloballyUniqueId(data);
            case 522: return new ::Ifc4x3_rc4::IfcGlobalOrLocalEnum(data);
            case 523: return new ::Ifc4x3_rc4::IfcGradientCurve(data);
            case 524: return new ::Ifc4x3_rc4::IfcGrid(data);
            case 525: return new ::Ifc4x3_rc4::IfcGridAxis(data);
            case 526: return new ::Ifc4x3_rc4::IfcGridPlacement(data);
            case 528: return new ::Ifc4x3_rc4::IfcGridTypeEnum(data);
            case 529: return new ::Ifc4x3_rc4::IfcGroup(data);
            case 530: return new ::Ifc4x3_rc4::IfcHalfSpaceSolid(data);
            case 532: return new ::Ifc4x3_rc4::IfcHeatExchanger(data);
            case 533: return new ::Ifc4x3_rc4::IfcHeatExchangerType(data);
            case 534: return new ::Ifc4x3_rc4::IfcHeatExchangerTypeEnum(data);
            case 535: return new ::Ifc4x3_rc4::IfcHeatFluxDensityMeasure(data);
            case 536: return new ::Ifc4x3_rc4::IfcHeatingValueMeasure(data);
            case 537: return new ::Ifc4x3_rc4::IfcHumidifier(data);
            case 538: return new ::Ifc4x3_rc4::IfcHumidifierType(data);
            case 539: return new ::Ifc4x3_rc4::IfcHumidifierTypeEnum(data);
            case 540: return new ::Ifc4x3_rc4::IfcIdentifier(data);
            case 541: return new ::Ifc4x3_rc4::IfcIlluminanceMeasure(data);
            case 542: return new ::Ifc4x3_rc4::IfcImageTexture(data);
            case 543: return new ::Ifc4x3_rc4::IfcImpactProtectionDevice(data);
            case 544: return new ::Ifc4x3_rc4::IfcImpactProtectionDeviceType(data);
            case 545: return new ::Ifc4x3_rc4::IfcImpactProtectionDeviceTypeEnum(data);
            case 547: return new ::Ifc4x3_rc4::IfcIndexedColourMap(data);
            case 548: return new ::Ifc4x3_rc4::IfcIndexedPolyCurve(data);
            case 549: return new ::Ifc4x3_rc4::IfcIndexedPolygonalFace(data);
            case 550: return new ::Ifc4x3_rc4::IfcIndexedPolygonalFaceWithVoids(data);
            case 551: return new ::Ifc4x3_rc4::IfcIndexedTextureMap(data);
            case 552: return new ::Ifc4x3_rc4::IfcIndexedTriangleTextureMap(data);
            case 553: return new ::Ifc4x3_rc4::IfcInductanceMeasure(data);
            case 554: return new ::Ifc4x3_rc4::IfcInteger(data);
            case 555: return new ::Ifc4x3_rc4::IfcIntegerCountRateMeasure(data);
            case 556: return new ::Ifc4x3_rc4::IfcInterceptor(data);
            case 557: return new ::Ifc4x3_rc4::IfcInterceptorType(data);
            case 558: return new ::Ifc4x3_rc4::IfcInterceptorTypeEnum(data);
            case 560: return new ::Ifc4x3_rc4::IfcInternalOrExternalEnum(data);
            case 561: return new ::Ifc4x3_rc4::IfcIntersectionCurve(data);
            case 562: return new ::Ifc4x3_rc4::IfcInventory(data);
            case 563: return new ::Ifc4x3_rc4::IfcInventoryTypeEnum(data);
            case 564: return new ::Ifc4x3_rc4::IfcIonConcentrationMeasure(data);
            case 565: return new ::Ifc4x3_rc4::IfcIrregularTimeSeries(data);
            case 566: return new ::Ifc4x3_rc4::IfcIrregularTimeSeriesValue(data);
            case 567: return new ::Ifc4x3_rc4::IfcIShapeProfileDef(data);
            case 568: return new ::Ifc4x3_rc4::IfcIsothermalMoistureCapacityMeasure(data);
            case 569: return new ::Ifc4x3_rc4::IfcJunctionBox(data);
            case 570: return new ::Ifc4x3_rc4::IfcJunctionBoxType(data);
            case 571: return new ::Ifc4x3_rc4::IfcJunctionBoxTypeEnum(data);
            case 572: return new ::Ifc4x3_rc4::IfcKerb(data);
            case 573: return new ::Ifc4x3_rc4::IfcKerbType(data);
            case 574: return new ::Ifc4x3_rc4::IfcKinematicViscosityMeasure(data);
            case 575: return new ::Ifc4x3_rc4::IfcKnotType(data);
            case 576: return new ::Ifc4x3_rc4::IfcLabel(data);
            case 577: return new ::Ifc4x3_rc4::IfcLaborResource(data);
            case 578: return new ::Ifc4x3_rc4::IfcLaborResourceType(data);
            case 579: return new ::Ifc4x3_rc4::IfcLaborResourceTypeEnum(data);
            case 580: return new ::Ifc4x3_rc4::IfcLagTime(data);
            case 581: return new ::Ifc4x3_rc4::IfcLamp(data);
            case 582: return new ::Ifc4x3_rc4::IfcLampType(data);
            case 583: return new ::Ifc4x3_rc4::IfcLampTypeEnum(data);
            case 584: return new ::Ifc4x3_rc4::IfcLanguageId(data);
            case 586: return new ::Ifc4x3_rc4::IfcLayerSetDirectionEnum(data);
            case 587: return new ::Ifc4x3_rc4::IfcLengthMeasure(data);
            case 588: return new ::Ifc4x3_rc4::IfcLibraryInformation(data);
            case 589: return new ::Ifc4x3_rc4::IfcLibraryReference(data);
            case 591: return new ::Ifc4x3_rc4::IfcLightDistributionCurveEnum(data);
            case 592: return new ::Ifc4x3_rc4::IfcLightDistributionData(data);
            case 594: return new ::Ifc4x3_rc4::IfcLightEmissionSourceEnum(data);
            case 595: return new ::Ifc4x3_rc4::IfcLightFixture(data);
            case 596: return new ::Ifc4x3_rc4::IfcLightFixtureType(data);
            case 597: return new ::Ifc4x3_rc4::IfcLightFixtureTypeEnum(data);
            case 598: return new ::Ifc4x3_rc4::IfcLightIntensityDistribution(data);
            case 599: return new ::Ifc4x3_rc4::IfcLightSource(data);
            case 600: return new ::Ifc4x3_rc4::IfcLightSourceAmbient(data);
            case 601: return new ::Ifc4x3_rc4::IfcLightSourceDirectional(data);
            case 602: return new ::Ifc4x3_rc4::IfcLightSourceGoniometric(data);
            case 603: return new ::Ifc4x3_rc4::IfcLightSourcePositional(data);
            case 604: return new ::Ifc4x3_rc4::IfcLightSourceSpot(data);
            case 605: return new ::Ifc4x3_rc4::IfcLine(data);
            case 606: return new ::Ifc4x3_rc4::IfcLinearElement(data);
            case 607: return new ::Ifc4x3_rc4::IfcLinearForceMeasure(data);
            case 608: return new ::Ifc4x3_rc4::IfcLinearMomentMeasure(data);
            case 609: return new ::Ifc4x3_rc4::IfcLinearPlacement(data);
            case 610: return new ::Ifc4x3_rc4::IfcLinearPositioningElement(data);
            case 611: return new ::Ifc4x3_rc4::IfcLinearStiffnessMeasure(data);
            case 612: return new ::Ifc4x3_rc4::IfcLinearVelocityMeasure(data);
            case 613: return new ::Ifc4x3_rc4::IfcLineIndex(data);
            case 614: return new ::Ifc4x3_rc4::IfcLiquidTerminal(data);
            case 615: return new ::Ifc4x3_rc4::IfcLiquidTerminalType(data);
            case 616: return new ::Ifc4x3_rc4::IfcLiquidTerminalTypeEnum(data);
            case 617: return new ::Ifc4x3_rc4::IfcLoadGroupTypeEnum(data);
            case 618: return new ::Ifc4x3_rc4::IfcLocalPlacement(data);
            case 619: return new ::Ifc4x3_rc4::IfcLogical(data);
            case 620: return new ::Ifc4x3_rc4::IfcLogicalOperatorEnum(data);
            case 621: return new ::Ifc4x3_rc4::IfcLoop(data);
            case 622: return new ::Ifc4x3_rc4::IfcLShapeProfileDef(data);
            case 623: return new ::Ifc4x3_rc4::IfcLuminousFluxMeasure(data);
            case 624: return new ::Ifc4x3_rc4::IfcLuminousIntensityDistributionMeasure(data);
            case 625: return new ::Ifc4x3_rc4::IfcLuminousIntensityMeasure(data);
            case 626: return new ::Ifc4x3_rc4::IfcMagneticFluxDensityMeasure(data);
            case 627: return new ::Ifc4x3_rc4::IfcMagneticFluxMeasure(data);
            case 628: return new ::Ifc4x3_rc4::IfcManifoldSolidBrep(data);
            case 629: return new ::Ifc4x3_rc4::IfcMapConversion(data);
            case 630: return new ::Ifc4x3_rc4::IfcMappedItem(data);
            case 631: return new ::Ifc4x3_rc4::IfcMarineFacility(data);
            case 632: return new ::Ifc4x3_rc4::IfcMarineFacilityTypeEnum(data);
            case 633: return new ::Ifc4x3_rc4::IfcMarinePartTypeEnum(data);
            case 634: return new ::Ifc4x3_rc4::IfcMassDensityMeasure(data);
            case 635: return new ::Ifc4x3_rc4::IfcMassFlowRateMeasure(data);
            case 636: return new ::Ifc4x3_rc4::IfcMassMeasure(data);
            case 637: return new ::Ifc4x3_rc4::IfcMassPerLengthMeasure(data);
            case 638: return new ::Ifc4x3_rc4::IfcMaterial(data);
            case 639: return new ::Ifc4x3_rc4::IfcMaterialClassificationRelationship(data);
            case 640: return new ::Ifc4x3_rc4::IfcMaterialConstituent(data);
            case 641: return new ::Ifc4x3_rc4::IfcMaterialConstituentSet(data);
            case 642: return new ::Ifc4x3_rc4::IfcMaterialDefinition(data);
            case 643: return new ::Ifc4x3_rc4::IfcMaterialDefinitionRepresentation(data);
            case 644: return new ::Ifc4x3_rc4::IfcMaterialLayer(data);
            case 645: return new ::Ifc4x3_rc4::IfcMaterialLayerSet(data);
            case 646: return new ::Ifc4x3_rc4::IfcMaterialLayerSetUsage(data);
            case 647: return new ::Ifc4x3_rc4::IfcMaterialLayerWithOffsets(data);
            case 648: return new ::Ifc4x3_rc4::IfcMaterialList(data);
            case 649: return new ::Ifc4x3_rc4::IfcMaterialProfile(data);
            case 650: return new ::Ifc4x3_rc4::IfcMaterialProfileSet(data);
            case 651: return new ::Ifc4x3_rc4::IfcMaterialProfileSetUsage(data);
            case 652: return new ::Ifc4x3_rc4::IfcMaterialProfileSetUsageTapering(data);
            case 653: return new ::Ifc4x3_rc4::IfcMaterialProfileWithOffsets(data);
            case 654: return new ::Ifc4x3_rc4::IfcMaterialProperties(data);
            case 655: return new ::Ifc4x3_rc4::IfcMaterialRelationship(data);
            case 657: return new ::Ifc4x3_rc4::IfcMaterialUsageDefinition(data);
            case 659: return new ::Ifc4x3_rc4::IfcMeasureWithUnit(data);
            case 660: return new ::Ifc4x3_rc4::IfcMechanicalFastener(data);
            case 661: return new ::Ifc4x3_rc4::IfcMechanicalFastenerType(data);
            case 662: return new ::Ifc4x3_rc4::IfcMechanicalFastenerTypeEnum(data);
            case 663: return new ::Ifc4x3_rc4::IfcMedicalDevice(data);
            case 664: return new ::Ifc4x3_rc4::IfcMedicalDeviceType(data);
            case 665: return new ::Ifc4x3_rc4::IfcMedicalDeviceTypeEnum(data);
            case 666: return new ::Ifc4x3_rc4::IfcMember(data);
            case 667: return new ::Ifc4x3_rc4::IfcMemberStandardCase(data);
            case 668: return new ::Ifc4x3_rc4::IfcMemberType(data);
            case 669: return new ::Ifc4x3_rc4::IfcMemberTypeEnum(data);
            case 670: return new ::Ifc4x3_rc4::IfcMetric(data);
            case 672: return new ::Ifc4x3_rc4::IfcMirroredProfileDef(data);
            case 673: return new ::Ifc4x3_rc4::IfcMobileTelecommunicationsAppliance(data);
            case 674: return new ::Ifc4x3_rc4::IfcMobileTelecommunicationsApplianceType(data);
            case 675: return new ::Ifc4x3_rc4::IfcMobileTelecommunicationsApplianceTypeEnum(data);
            case 676: return new ::Ifc4x3_rc4::IfcModulusOfElasticityMeasure(data);
            case 677: return new ::Ifc4x3_rc4::IfcModulusOfLinearSubgradeReactionMeasure(data);
            case 678: return new ::Ifc4x3_rc4::IfcModulusOfRotationalSubgradeReactionMeasure(data);
            case 680: return new ::Ifc4x3_rc4::IfcModulusOfSubgradeReactionMeasure(data);
            case 683: return new ::Ifc4x3_rc4::IfcMoistureDiffusivityMeasure(data);
            case 684: return new ::Ifc4x3_rc4::IfcMolecularWeightMeasure(data);
            case 685: return new ::Ifc4x3_rc4::IfcMomentOfInertiaMeasure(data);
            case 686: return new ::Ifc4x3_rc4::IfcMonetaryMeasure(data);
            case 687: return new ::Ifc4x3_rc4::IfcMonetaryUnit(data);
            case 688: return new ::Ifc4x3_rc4::IfcMonthInYearNumber(data);
            case 689: return new ::Ifc4x3_rc4::IfcMooringDevice(data);
            case 690: return new ::Ifc4x3_rc4::IfcMooringDeviceType(data);
            case 691: return new ::Ifc4x3_rc4::IfcMooringDeviceTypeEnum(data);
            case 692: return new ::Ifc4x3_rc4::IfcMotorConnection(data);
            case 693: return new ::Ifc4x3_rc4::IfcMotorConnectionType(data);
            case 694: return new ::Ifc4x3_rc4::IfcMotorConnectionTypeEnum(data);
            case 695: return new ::Ifc4x3_rc4::IfcNamedUnit(data);
            case 696: return new ::Ifc4x3_rc4::IfcNavigationElement(data);
            case 697: return new ::Ifc4x3_rc4::IfcNavigationElementType(data);
            case 698: return new ::Ifc4x3_rc4::IfcNavigationElementTypeEnum(data);
            case 699: return new ::Ifc4x3_rc4::IfcNonNegativeLengthMeasure(data);
            case 700: return new ::Ifc4x3_rc4::IfcNormalisedRatioMeasure(data);
            case 701: return new ::Ifc4x3_rc4::IfcNumericMeasure(data);
            case 702: return new ::Ifc4x3_rc4::IfcObject(data);
            case 703: return new ::Ifc4x3_rc4::IfcObjectDefinition(data);
            case 704: return new ::Ifc4x3_rc4::IfcObjective(data);
            case 705: return new ::Ifc4x3_rc4::IfcObjectiveEnum(data);
            case 706: return new ::Ifc4x3_rc4::IfcObjectPlacement(data);
            case 708: return new ::Ifc4x3_rc4::IfcObjectTypeEnum(data);
            case 709: return new ::Ifc4x3_rc4::IfcOccupant(data);
            case 710: return new ::Ifc4x3_rc4::IfcOccupantTypeEnum(data);
            case 711: return new ::Ifc4x3_rc4::IfcOffsetCurve(data);
            case 712: return new ::Ifc4x3_rc4::IfcOffsetCurve2D(data);
            case 713: return new ::Ifc4x3_rc4::IfcOffsetCurve3D(data);
            case 714: return new ::Ifc4x3_rc4::IfcOffsetCurveByDistances(data);
            case 715: return new ::Ifc4x3_rc4::IfcOpenCrossProfileDef(data);
            case 716: return new ::Ifc4x3_rc4::IfcOpeningElement(data);
            case 717: return new ::Ifc4x3_rc4::IfcOpeningElementTypeEnum(data);
            case 718: return new ::Ifc4x3_rc4::IfcOpeningStandardCase(data);
            case 719: return new ::Ifc4x3_rc4::IfcOpenShell(data);
            case 720: return new ::Ifc4x3_rc4::IfcOrganization(data);
            case 721: return new ::Ifc4x3_rc4::IfcOrganizationRelationship(data);
            case 722: return new ::Ifc4x3_rc4::IfcOrientedEdge(data);
            case 723: return new ::Ifc4x3_rc4::IfcOuterBoundaryCurve(data);
            case 724: return new ::Ifc4x3_rc4::IfcOutlet(data);
            case 725: return new ::Ifc4x3_rc4::IfcOutletType(data);
            case 726: return new ::Ifc4x3_rc4::IfcOutletTypeEnum(data);
            case 727: return new ::Ifc4x3_rc4::IfcOwnerHistory(data);
            case 728: return new ::Ifc4x3_rc4::IfcParameterizedProfileDef(data);
            case 729: return new ::Ifc4x3_rc4::IfcParameterValue(data);
            case 730: return new ::Ifc4x3_rc4::IfcPath(data);
            case 731: return new ::Ifc4x3_rc4::IfcPavement(data);
            case 732: return new ::Ifc4x3_rc4::IfcPavementType(data);
            case 733: return new ::Ifc4x3_rc4::IfcPavementTypeEnum(data);
            case 734: return new ::Ifc4x3_rc4::IfcPcurve(data);
            case 735: return new ::Ifc4x3_rc4::IfcPerformanceHistory(data);
            case 736: return new ::Ifc4x3_rc4::IfcPerformanceHistoryTypeEnum(data);
            case 737: return new ::Ifc4x3_rc4::IfcPermeableCoveringOperationEnum(data);
            case 738: return new ::Ifc4x3_rc4::IfcPermeableCoveringProperties(data);
            case 739: return new ::Ifc4x3_rc4::IfcPermit(data);
            case 740: return new ::Ifc4x3_rc4::IfcPermitTypeEnum(data);
            case 741: return new ::Ifc4x3_rc4::IfcPerson(data);
            case 742: return new ::Ifc4x3_rc4::IfcPersonAndOrganization(data);
            case 743: return new ::Ifc4x3_rc4::IfcPHMeasure(data);
            case 744: return new ::Ifc4x3_rc4::IfcPhysicalComplexQuantity(data);
            case 745: return new ::Ifc4x3_rc4::IfcPhysicalOrVirtualEnum(data);
            case 746: return new ::Ifc4x3_rc4::IfcPhysicalQuantity(data);
            case 747: return new ::Ifc4x3_rc4::IfcPhysicalSimpleQuantity(data);
            case 748: return new ::Ifc4x3_rc4::IfcPile(data);
            case 749: return new ::Ifc4x3_rc4::IfcPileConstructionEnum(data);
            case 750: return new ::Ifc4x3_rc4::IfcPileType(data);
            case 751: return new ::Ifc4x3_rc4::IfcPileTypeEnum(data);
            case 752: return new ::Ifc4x3_rc4::IfcPipeFitting(data);
            case 753: return new ::Ifc4x3_rc4::IfcPipeFittingType(data);
            case 754: return new ::Ifc4x3_rc4::IfcPipeFittingTypeEnum(data);
            case 755: return new ::Ifc4x3_rc4::IfcPipeSegment(data);
            case 756: return new ::Ifc4x3_rc4::IfcPipeSegmentType(data);
            case 757: return new ::Ifc4x3_rc4::IfcPipeSegmentTypeEnum(data);
            case 758: return new ::Ifc4x3_rc4::IfcPixelTexture(data);
            case 759: return new ::Ifc4x3_rc4::IfcPlacement(data);
            case 760: return new ::Ifc4x3_rc4::IfcPlanarBox(data);
            case 761: return new ::Ifc4x3_rc4::IfcPlanarExtent(data);
            case 762: return new ::Ifc4x3_rc4::IfcPlanarForceMeasure(data);
            case 763: return new ::Ifc4x3_rc4::IfcPlane(data);
            case 764: return new ::Ifc4x3_rc4::IfcPlaneAngleMeasure(data);
            case 765: return new ::Ifc4x3_rc4::IfcPlant(data);
            case 766: return new ::Ifc4x3_rc4::IfcPlate(data);
            case 767: return new ::Ifc4x3_rc4::IfcPlateStandardCase(data);
            case 768: return new ::Ifc4x3_rc4::IfcPlateType(data);
            case 769: return new ::Ifc4x3_rc4::IfcPlateTypeEnum(data);
            case 770: return new ::Ifc4x3_rc4::IfcPoint(data);
            case 771: return new ::Ifc4x3_rc4::IfcPointByDistanceExpression(data);
            case 772: return new ::Ifc4x3_rc4::IfcPointOnCurve(data);
            case 773: return new ::Ifc4x3_rc4::IfcPointOnSurface(data);
            case 775: return new ::Ifc4x3_rc4::IfcPolygonalBoundedHalfSpace(data);
            case 776: return new ::Ifc4x3_rc4::IfcPolygonalFaceSet(data);
            case 777: return new ::Ifc4x3_rc4::IfcPolyline(data);
            case 778: return new ::Ifc4x3_rc4::IfcPolyLoop(data);
            case 779: return new ::Ifc4x3_rc4::IfcPolynomialCurve(data);
            case 780: return new ::Ifc4x3_rc4::IfcPort(data);
            case 781: return new ::Ifc4x3_rc4::IfcPositioningElement(data);
            case 782: return new ::Ifc4x3_rc4::IfcPositiveInteger(data);
            case 783: return new ::Ifc4x3_rc4::IfcPositiveLengthMeasure(data);
            case 784: return new ::Ifc4x3_rc4::IfcPositivePlaneAngleMeasure(data);
            case 785: return new ::Ifc4x3_rc4::IfcPositiveRatioMeasure(data);
            case 786: return new ::Ifc4x3_rc4::IfcPostalAddress(data);
            case 787: return new ::Ifc4x3_rc4::IfcPowerMeasure(data);
            case 788: return new ::Ifc4x3_rc4::IfcPreDefinedColour(data);
            case 789: return new ::Ifc4x3_rc4::IfcPreDefinedCurveFont(data);
            case 790: return new ::Ifc4x3_rc4::IfcPreDefinedItem(data);
            case 791: return new ::Ifc4x3_rc4::IfcPreDefinedProperties(data);
            case 792: return new ::Ifc4x3_rc4::IfcPreDefinedPropertySet(data);
            case 793: return new ::Ifc4x3_rc4::IfcPreDefinedTextFont(data);
            case 794: return new ::Ifc4x3_rc4::IfcPreferredSurfaceCurveRepresentation(data);
            case 795: return new ::Ifc4x3_rc4::IfcPresentableText(data);
            case 796: return new ::Ifc4x3_rc4::IfcPresentationItem(data);
            case 797: return new ::Ifc4x3_rc4::IfcPresentationLayerAssignment(data);
            case 798: return new ::Ifc4x3_rc4::IfcPresentationLayerWithStyle(data);
            case 799: return new ::Ifc4x3_rc4::IfcPresentationStyle(data);
            case 800: return new ::Ifc4x3_rc4::IfcPressureMeasure(data);
            case 801: return new ::Ifc4x3_rc4::IfcProcedure(data);
            case 802: return new ::Ifc4x3_rc4::IfcProcedureType(data);
            case 803: return new ::Ifc4x3_rc4::IfcProcedureTypeEnum(data);
            case 804: return new ::Ifc4x3_rc4::IfcProcess(data);
            case 806: return new ::Ifc4x3_rc4::IfcProduct(data);
            case 807: return new ::Ifc4x3_rc4::IfcProductDefinitionShape(data);
            case 808: return new ::Ifc4x3_rc4::IfcProductRepresentation(data);
            case 811: return new ::Ifc4x3_rc4::IfcProfileDef(data);
            case 812: return new ::Ifc4x3_rc4::IfcProfileProperties(data);
            case 813: return new ::Ifc4x3_rc4::IfcProfileTypeEnum(data);
            case 814: return new ::Ifc4x3_rc4::IfcProject(data);
            case 815: return new ::Ifc4x3_rc4::IfcProjectedCRS(data);
            case 816: return new ::Ifc4x3_rc4::IfcProjectedOrTrueLengthEnum(data);
            case 817: return new ::Ifc4x3_rc4::IfcProjectionElement(data);
            case 818: return new ::Ifc4x3_rc4::IfcProjectionElementTypeEnum(data);
            case 819: return new ::Ifc4x3_rc4::IfcProjectLibrary(data);
            case 820: return new ::Ifc4x3_rc4::IfcProjectOrder(data);
            case 821: return new ::Ifc4x3_rc4::IfcProjectOrderTypeEnum(data);
            case 822: return new ::Ifc4x3_rc4::IfcProperty(data);
            case 823: return new ::Ifc4x3_rc4::IfcPropertyAbstraction(data);
            case 824: return new ::Ifc4x3_rc4::IfcPropertyBoundedValue(data);
            case 825: return new ::Ifc4x3_rc4::IfcPropertyDefinition(data);
            case 826: return new ::Ifc4x3_rc4::IfcPropertyDependencyRelationship(data);
            case 827: return new ::Ifc4x3_rc4::IfcPropertyEnumeratedValue(data);
            case 828: return new ::Ifc4x3_rc4::IfcPropertyEnumeration(data);
            case 829: return new ::Ifc4x3_rc4::IfcPropertyListValue(data);
            case 830: return new ::Ifc4x3_rc4::IfcPropertyReferenceValue(data);
            case 831: return new ::Ifc4x3_rc4::IfcPropertySet(data);
            case 832: return new ::Ifc4x3_rc4::IfcPropertySetDefinition(data);
            case 834: return new ::Ifc4x3_rc4::IfcPropertySetDefinitionSet(data);
            case 835: return new ::Ifc4x3_rc4::IfcPropertySetTemplate(data);
            case 836: return new ::Ifc4x3_rc4::IfcPropertySetTemplateTypeEnum(data);
            case 837: return new ::Ifc4x3_rc4::IfcPropertySingleValue(data);
            case 838: return new ::Ifc4x3_rc4::IfcPropertyTableValue(data);
            case 839: return new ::Ifc4x3_rc4::IfcPropertyTemplate(data);
            case 840: return new ::Ifc4x3_rc4::IfcPropertyTemplateDefinition(data);
            case 841: return new ::Ifc4x3_rc4::IfcProtectiveDevice(data);
            case 842: return new ::Ifc4x3_rc4::IfcProtectiveDeviceTrippingUnit(data);
            case 843: return new ::Ifc4x3_rc4::IfcProtectiveDeviceTrippingUnitType(data);
            case 844: return new ::Ifc4x3_rc4::IfcProtectiveDeviceTrippingUnitTypeEnum(data);
            case 845: return new ::Ifc4x3_rc4::IfcProtectiveDeviceType(data);
            case 846: return new ::Ifc4x3_rc4::IfcProtectiveDeviceTypeEnum(data);
            case 847: return new ::Ifc4x3_rc4::IfcProxy(data);
            case 848: return new ::Ifc4x3_rc4::IfcPump(data);
            case 849: return new ::Ifc4x3_rc4::IfcPumpType(data);
            case 850: return new ::Ifc4x3_rc4::IfcPumpTypeEnum(data);
            case 851: return new ::Ifc4x3_rc4::IfcQuantityArea(data);
            case 852: return new ::Ifc4x3_rc4::IfcQuantityCount(data);
            case 853: return new ::Ifc4x3_rc4::IfcQuantityLength(data);
            case 854: return new ::Ifc4x3_rc4::IfcQuantitySet(data);
            case 855: return new ::Ifc4x3_rc4::IfcQuantityTime(data);
            case 856: return new ::Ifc4x3_rc4::IfcQuantityVolume(data);
            case 857: return new ::Ifc4x3_rc4::IfcQuantityWeight(data);
            case 858: return new ::Ifc4x3_rc4::IfcRadioActivityMeasure(data);
            case 859: return new ::Ifc4x3_rc4::IfcRail(data);
            case 860: return new ::Ifc4x3_rc4::IfcRailing(data);
            case 861: return new ::Ifc4x3_rc4::IfcRailingType(data);
            case 862: return new ::Ifc4x3_rc4::IfcRailingTypeEnum(data);
            case 863: return new ::Ifc4x3_rc4::IfcRailType(data);
            case 864: return new ::Ifc4x3_rc4::IfcRailTypeEnum(data);
            case 865: return new ::Ifc4x3_rc4::IfcRailway(data);
            case 866: return new ::Ifc4x3_rc4::IfcRailwayPartTypeEnum(data);
            case 867: return new ::Ifc4x3_rc4::IfcRailwayTypeEnum(data);
            case 868: return new ::Ifc4x3_rc4::IfcRamp(data);
            case 869: return new ::Ifc4x3_rc4::IfcRampFlight(data);
            case 870: return new ::Ifc4x3_rc4::IfcRampFlightType(data);
            case 871: return new ::Ifc4x3_rc4::IfcRampFlightTypeEnum(data);
            case 872: return new ::Ifc4x3_rc4::IfcRampType(data);
            case 873: return new ::Ifc4x3_rc4::IfcRampTypeEnum(data);
            case 874: return new ::Ifc4x3_rc4::IfcRatioMeasure(data);
            case 875: return new ::Ifc4x3_rc4::IfcRationalBSplineCurveWithKnots(data);
            case 876: return new ::Ifc4x3_rc4::IfcRationalBSplineSurfaceWithKnots(data);
            case 877: return new ::Ifc4x3_rc4::IfcReal(data);
            case 878: return new ::Ifc4x3_rc4::IfcRectangleHollowProfileDef(data);
            case 879: return new ::Ifc4x3_rc4::IfcRectangleProfileDef(data);
            case 880: return new ::Ifc4x3_rc4::IfcRectangularPyramid(data);
            case 881: return new ::Ifc4x3_rc4::IfcRectangularTrimmedSurface(data);
            case 882: return new ::Ifc4x3_rc4::IfcRecurrencePattern(data);
            case 883: return new ::Ifc4x3_rc4::IfcRecurrenceTypeEnum(data);
            case 884: return new ::Ifc4x3_rc4::IfcReference(data);
            case 885: return new ::Ifc4x3_rc4::IfcReferent(data);
            case 886: return new ::Ifc4x3_rc4::IfcReferentTypeEnum(data);
            case 887: return new ::Ifc4x3_rc4::IfcReflectanceMethodEnum(data);
            case 888: return new ::Ifc4x3_rc4::IfcRegularTimeSeries(data);
            case 889: return new ::Ifc4x3_rc4::IfcReinforcedSoil(data);
            case 890: return new ::Ifc4x3_rc4::IfcReinforcedSoilTypeEnum(data);
            case 891: return new ::Ifc4x3_rc4::IfcReinforcementBarProperties(data);
            case 892: return new ::Ifc4x3_rc4::IfcReinforcementDefinitionProperties(data);
            case 893: return new ::Ifc4x3_rc4::IfcReinforcingBar(data);
            case 894: return new ::Ifc4x3_rc4::IfcReinforcingBarRoleEnum(data);
            case 895: return new ::Ifc4x3_rc4::IfcReinforcingBarSurfaceEnum(data);
            case 896: return new ::Ifc4x3_rc4::IfcReinforcingBarType(data);
            case 897: return new ::Ifc4x3_rc4::IfcReinforcingBarTypeEnum(data);
            case 898: return new ::Ifc4x3_rc4::IfcReinforcingElement(data);
            case 899: return new ::Ifc4x3_rc4::IfcReinforcingElementType(data);
            case 900: return new ::Ifc4x3_rc4::IfcReinforcingMesh(data);
            case 901: return new ::Ifc4x3_rc4::IfcReinforcingMeshType(data);
            case 902: return new ::Ifc4x3_rc4::IfcReinforcingMeshTypeEnum(data);
            case 903: return new ::Ifc4x3_rc4::IfcRelAdheresToElement(data);
            case 904: return new ::Ifc4x3_rc4::IfcRelAggregates(data);
            case 905: return new ::Ifc4x3_rc4::IfcRelAssigns(data);
            case 906: return new ::Ifc4x3_rc4::IfcRelAssignsToActor(data);
            case 907: return new ::Ifc4x3_rc4::IfcRelAssignsToControl(data);
            case 908: return new ::Ifc4x3_rc4::IfcRelAssignsToGroup(data);
            case 909: return new ::Ifc4x3_rc4::IfcRelAssignsToGroupByFactor(data);
            case 910: return new ::Ifc4x3_rc4::IfcRelAssignsToProcess(data);
            case 911: return new ::Ifc4x3_rc4::IfcRelAssignsToProduct(data);
            case 912: return new ::Ifc4x3_rc4::IfcRelAssignsToResource(data);
            case 913: return new ::Ifc4x3_rc4::IfcRelAssociates(data);
            case 914: return new ::Ifc4x3_rc4::IfcRelAssociatesApproval(data);
            case 915: return new ::Ifc4x3_rc4::IfcRelAssociatesClassification(data);
            case 916: return new ::Ifc4x3_rc4::IfcRelAssociatesConstraint(data);
            case 917: return new ::Ifc4x3_rc4::IfcRelAssociatesDocument(data);
            case 918: return new ::Ifc4x3_rc4::IfcRelAssociatesLibrary(data);
            case 919: return new ::Ifc4x3_rc4::IfcRelAssociatesMaterial(data);
            case 920: return new ::Ifc4x3_rc4::IfcRelAssociatesProfileDef(data);
            case 921: return new ::Ifc4x3_rc4::IfcRelationship(data);
            case 922: return new ::Ifc4x3_rc4::IfcRelConnects(data);
            case 923: return new ::Ifc4x3_rc4::IfcRelConnectsElements(data);
            case 924: return new ::Ifc4x3_rc4::IfcRelConnectsPathElements(data);
            case 925: return new ::Ifc4x3_rc4::IfcRelConnectsPorts(data);
            case 926: return new ::Ifc4x3_rc4::IfcRelConnectsPortToElement(data);
            case 927: return new ::Ifc4x3_rc4::IfcRelConnectsStructuralActivity(data);
            case 928: return new ::Ifc4x3_rc4::IfcRelConnectsStructuralMember(data);
            case 929: return new ::Ifc4x3_rc4::IfcRelConnectsWithEccentricity(data);
            case 930: return new ::Ifc4x3_rc4::IfcRelConnectsWithRealizingElements(data);
            case 931: return new ::Ifc4x3_rc4::IfcRelContainedInSpatialStructure(data);
            case 932: return new ::Ifc4x3_rc4::IfcRelCoversBldgElements(data);
            case 933: return new ::Ifc4x3_rc4::IfcRelCoversSpaces(data);
            case 934: return new ::Ifc4x3_rc4::IfcRelDeclares(data);
            case 935: return new ::Ifc4x3_rc4::IfcRelDecomposes(data);
            case 936: return new ::Ifc4x3_rc4::IfcRelDefines(data);
            case 937: return new ::Ifc4x3_rc4::IfcRelDefinesByObject(data);
            case 938: return new ::Ifc4x3_rc4::IfcRelDefinesByProperties(data);
            case 939: return new ::Ifc4x3_rc4::IfcRelDefinesByTemplate(data);
            case 940: return new ::Ifc4x3_rc4::IfcRelDefinesByType(data);
            case 941: return new ::Ifc4x3_rc4::IfcRelFillsElement(data);
            case 942: return new ::Ifc4x3_rc4::IfcRelFlowControlElements(data);
            case 943: return new ::Ifc4x3_rc4::IfcRelInterferesElements(data);
            case 944: return new ::Ifc4x3_rc4::IfcRelNests(data);
            case 945: return new ::Ifc4x3_rc4::IfcRelPositions(data);
            case 946: return new ::Ifc4x3_rc4::IfcRelProjectsElement(data);
            case 947: return new ::Ifc4x3_rc4::IfcRelReferencedInSpatialStructure(data);
            case 948: return new ::Ifc4x3_rc4::IfcRelSequence(data);
            case 949: return new ::Ifc4x3_rc4::IfcRelServicesBuildings(data);
            case 950: return new ::Ifc4x3_rc4::IfcRelSpaceBoundary(data);
            case 951: return new ::Ifc4x3_rc4::IfcRelSpaceBoundary1stLevel(data);
            case 952: return new ::Ifc4x3_rc4::IfcRelSpaceBoundary2ndLevel(data);
            case 953: return new ::Ifc4x3_rc4::IfcRelVoidsElement(data);
            case 954: return new ::Ifc4x3_rc4::IfcReparametrisedCompositeCurveSegment(data);
            case 955: return new ::Ifc4x3_rc4::IfcRepresentation(data);
            case 956: return new ::Ifc4x3_rc4::IfcRepresentationContext(data);
            case 957: return new ::Ifc4x3_rc4::IfcRepresentationItem(data);
            case 958: return new ::Ifc4x3_rc4::IfcRepresentationMap(data);
            case 959: return new ::Ifc4x3_rc4::IfcResource(data);
            case 960: return new ::Ifc4x3_rc4::IfcResourceApprovalRelationship(data);
            case 961: return new ::Ifc4x3_rc4::IfcResourceConstraintRelationship(data);
            case 962: return new ::Ifc4x3_rc4::IfcResourceLevelRelationship(data);
            case 965: return new ::Ifc4x3_rc4::IfcResourceTime(data);
            case 966: return new ::Ifc4x3_rc4::IfcRevolvedAreaSolid(data);
            case 967: return new ::Ifc4x3_rc4::IfcRevolvedAreaSolidTapered(data);
            case 968: return new ::Ifc4x3_rc4::IfcRightCircularCone(data);
            case 969: return new ::Ifc4x3_rc4::IfcRightCircularCylinder(data);
            case 970: return new ::Ifc4x3_rc4::IfcRoad(data);
            case 971: return new ::Ifc4x3_rc4::IfcRoadPartTypeEnum(data);
            case 972: return new ::Ifc4x3_rc4::IfcRoadTypeEnum(data);
            case 973: return new ::Ifc4x3_rc4::IfcRoleEnum(data);
            case 974: return new ::Ifc4x3_rc4::IfcRoof(data);
            case 975: return new ::Ifc4x3_rc4::IfcRoofType(data);
            case 976: return new ::Ifc4x3_rc4::IfcRoofTypeEnum(data);
            case 977: return new ::Ifc4x3_rc4::IfcRoot(data);
            case 978: return new ::Ifc4x3_rc4::IfcRotationalFrequencyMeasure(data);
            case 979: return new ::Ifc4x3_rc4::IfcRotationalMassMeasure(data);
            case 980: return new ::Ifc4x3_rc4::IfcRotationalStiffnessMeasure(data);
            case 982: return new ::Ifc4x3_rc4::IfcRoundedRectangleProfileDef(data);
            case 983: return new ::Ifc4x3_rc4::IfcSanitaryTerminal(data);
            case 984: return new ::Ifc4x3_rc4::IfcSanitaryTerminalType(data);
            case 985: return new ::Ifc4x3_rc4::IfcSanitaryTerminalTypeEnum(data);
            case 986: return new ::Ifc4x3_rc4::IfcSchedulingTime(data);
            case 987: return new ::Ifc4x3_rc4::IfcSeamCurve(data);
            case 988: return new ::Ifc4x3_rc4::IfcSecondOrderPolynomialSpiral(data);
            case 989: return new ::Ifc4x3_rc4::IfcSectionalAreaIntegralMeasure(data);
            case 990: return new ::Ifc4x3_rc4::IfcSectionedSolid(data);
            case 991: return new ::Ifc4x3_rc4::IfcSectionedSolidHorizontal(data);
            case 992: return new ::Ifc4x3_rc4::IfcSectionedSpine(data);
            case 993: return new ::Ifc4x3_rc4::IfcSectionedSurface(data);
            case 994: return new ::Ifc4x3_rc4::IfcSectionModulusMeasure(data);
            case 995: return new ::Ifc4x3_rc4::IfcSectionProperties(data);
            case 996: return new ::Ifc4x3_rc4::IfcSectionReinforcementProperties(data);
            case 997: return new ::Ifc4x3_rc4::IfcSectionTypeEnum(data);
            case 998: return new ::Ifc4x3_rc4::IfcSegment(data);
            case 999: return new ::Ifc4x3_rc4::IfcSegmentedReferenceCurve(data);
            case 1001: return new ::Ifc4x3_rc4::IfcSensor(data);
            case 1002: return new ::Ifc4x3_rc4::IfcSensorType(data);
            case 1003: return new ::Ifc4x3_rc4::IfcSensorTypeEnum(data);
            case 1004: return new ::Ifc4x3_rc4::IfcSequenceEnum(data);
            case 1005: return new ::Ifc4x3_rc4::IfcSeventhOrderPolynomialSpiral(data);
            case 1006: return new ::Ifc4x3_rc4::IfcShadingDevice(data);
            case 1007: return new ::Ifc4x3_rc4::IfcShadingDeviceType(data);
            case 1008: return new ::Ifc4x3_rc4::IfcShadingDeviceTypeEnum(data);
            case 1009: return new ::Ifc4x3_rc4::IfcShapeAspect(data);
            case 1010: return new ::Ifc4x3_rc4::IfcShapeModel(data);
            case 1011: return new ::Ifc4x3_rc4::IfcShapeRepresentation(data);
            case 1012: return new ::Ifc4x3_rc4::IfcShearModulusMeasure(data);
            case 1014: return new ::Ifc4x3_rc4::IfcShellBasedSurfaceModel(data);
            case 1015: return new ::Ifc4x3_rc4::IfcSign(data);
            case 1016: return new ::Ifc4x3_rc4::IfcSignal(data);
            case 1017: return new ::Ifc4x3_rc4::IfcSignalType(data);
            case 1018: return new ::Ifc4x3_rc4::IfcSignalTypeEnum(data);
            case 1019: return new ::Ifc4x3_rc4::IfcSignType(data);
            case 1020: return new ::Ifc4x3_rc4::IfcSignTypeEnum(data);
            case 1021: return new ::Ifc4x3_rc4::IfcSimpleProperty(data);
            case 1022: return new ::Ifc4x3_rc4::IfcSimplePropertyTemplate(data);
            case 1023: return new ::Ifc4x3_rc4::IfcSimplePropertyTemplateTypeEnum(data);
            case 1025: return new ::Ifc4x3_rc4::IfcSine(data);
            case 1026: return new ::Ifc4x3_rc4::IfcSIPrefix(data);
            case 1027: return new ::Ifc4x3_rc4::IfcSite(data);
            case 1028: return new ::Ifc4x3_rc4::IfcSIUnit(data);
            case 1029: return new ::Ifc4x3_rc4::IfcSIUnitName(data);
            case 1031: return new ::Ifc4x3_rc4::IfcSlab(data);
            case 1032: return new ::Ifc4x3_rc4::IfcSlabElementedCase(data);
            case 1033: return new ::Ifc4x3_rc4::IfcSlabStandardCase(data);
            case 1034: return new ::Ifc4x3_rc4::IfcSlabType(data);
            case 1035: return new ::Ifc4x3_rc4::IfcSlabTypeEnum(data);
            case 1036: return new ::Ifc4x3_rc4::IfcSlippageConnectionCondition(data);
            case 1037: return new ::Ifc4x3_rc4::IfcSolarDevice(data);
            case 1038: return new ::Ifc4x3_rc4::IfcSolarDeviceType(data);
            case 1039: return new ::Ifc4x3_rc4::IfcSolarDeviceTypeEnum(data);
            case 1040: return new ::Ifc4x3_rc4::IfcSolidAngleMeasure(data);
            case 1041: return new ::Ifc4x3_rc4::IfcSolidModel(data);
            case 1043: return new ::Ifc4x3_rc4::IfcSolidStratum(data);
            case 1044: return new ::Ifc4x3_rc4::IfcSoundPowerLevelMeasure(data);
            case 1045: return new ::Ifc4x3_rc4::IfcSoundPowerMeasure(data);
            case 1046: return new ::Ifc4x3_rc4::IfcSoundPressureLevelMeasure(data);
            case 1047: return new ::Ifc4x3_rc4::IfcSoundPressureMeasure(data);
            case 1048: return new ::Ifc4x3_rc4::IfcSpace(data);
            case 1050: return new ::Ifc4x3_rc4::IfcSpaceHeater(data);
            case 1051: return new ::Ifc4x3_rc4::IfcSpaceHeaterType(data);
            case 1052: return new ::Ifc4x3_rc4::IfcSpaceHeaterTypeEnum(data);
            case 1053: return new ::Ifc4x3_rc4::IfcSpaceType(data);
            case 1054: return new ::Ifc4x3_rc4::IfcSpaceTypeEnum(data);
            case 1055: return new ::Ifc4x3_rc4::IfcSpatialElement(data);
            case 1056: return new ::Ifc4x3_rc4::IfcSpatialElementType(data);
            case 1058: return new ::Ifc4x3_rc4::IfcSpatialStructureElement(data);
            case 1059: return new ::Ifc4x3_rc4::IfcSpatialStructureElementType(data);
            case 1060: return new ::Ifc4x3_rc4::IfcSpatialZone(data);
            case 1061: return new ::Ifc4x3_rc4::IfcSpatialZoneType(data);
            case 1062: return new ::Ifc4x3_rc4::IfcSpatialZoneTypeEnum(data);
            case 1063: return new ::Ifc4x3_rc4::IfcSpecificHeatCapacityMeasure(data);
            case 1064: return new ::Ifc4x3_rc4::IfcSpecularExponent(data);
            case 1066: return new ::Ifc4x3_rc4::IfcSpecularRoughness(data);
            case 1067: return new ::Ifc4x3_rc4::IfcSphere(data);
            case 1068: return new ::Ifc4x3_rc4::IfcSphericalSurface(data);
            case 1069: return new ::Ifc4x3_rc4::IfcSpiral(data);
            case 1070: return new ::Ifc4x3_rc4::IfcStackTerminal(data);
            case 1071: return new ::Ifc4x3_rc4::IfcStackTerminalType(data);
            case 1072: return new ::Ifc4x3_rc4::IfcStackTerminalTypeEnum(data);
            case 1073: return new ::Ifc4x3_rc4::IfcStair(data);
            case 1074: return new ::Ifc4x3_rc4::IfcStairFlight(data);
            case 1075: return new ::Ifc4x3_rc4::IfcStairFlightType(data);
            case 1076: return new ::Ifc4x3_rc4::IfcStairFlightTypeEnum(data);
            case 1077: return new ::Ifc4x3_rc4::IfcStairType(data);
            case 1078: return new ::Ifc4x3_rc4::IfcStairTypeEnum(data);
            case 1079: return new ::Ifc4x3_rc4::IfcStateEnum(data);
            case 1080: return new ::Ifc4x3_rc4::IfcStructuralAction(data);
            case 1081: return new ::Ifc4x3_rc4::IfcStructuralActivity(data);
            case 1083: return new ::Ifc4x3_rc4::IfcStructuralAnalysisModel(data);
            case 1084: return new ::Ifc4x3_rc4::IfcStructuralConnection(data);
            case 1085: return new ::Ifc4x3_rc4::IfcStructuralConnectionCondition(data);
            case 1086: return new ::Ifc4x3_rc4::IfcStructuralCurveAction(data);
            case 1087: return new ::Ifc4x3_rc4::IfcStructuralCurveActivityTypeEnum(data);
            case 1088: return new ::Ifc4x3_rc4::IfcStructuralCurveConnection(data);
            case 1089: return new ::Ifc4x3_rc4::IfcStructuralCurveMember(data);
            case 1090: return new ::Ifc4x3_rc4::IfcStructuralCurveMemberTypeEnum(data);
            case 1091: return new ::Ifc4x3_rc4::IfcStructuralCurveMemberVarying(data);
            case 1092: return new ::Ifc4x3_rc4::IfcStructuralCurveReaction(data);
            case 1093: return new ::Ifc4x3_rc4::IfcStructuralItem(data);
            case 1094: return new ::Ifc4x3_rc4::IfcStructuralLinearAction(data);
            case 1095: return new ::Ifc4x3_rc4::IfcStructuralLoad(data);
            case 1096: return new ::Ifc4x3_rc4::IfcStructuralLoadCase(data);
            case 1097: return new ::Ifc4x3_rc4::IfcStructuralLoadConfiguration(data);
            case 1098: return new ::Ifc4x3_rc4::IfcStructuralLoadGroup(data);
            case 1099: return new ::Ifc4x3_rc4::IfcStructuralLoadLinearForce(data);
            case 1100: return new ::Ifc4x3_rc4::IfcStructuralLoadOrResult(data);
            case 1101: return new ::Ifc4x3_rc4::IfcStructuralLoadPlanarForce(data);
            case 1102: return new ::Ifc4x3_rc4::IfcStructuralLoadSingleDisplacement(data);
            case 1103: return new ::Ifc4x3_rc4::IfcStructuralLoadSingleDisplacementDistortion(data);
            case 1104: return new ::Ifc4x3_rc4::IfcStructuralLoadSingleForce(data);
            case 1105: return new ::Ifc4x3_rc4::IfcStructuralLoadSingleForceWarping(data);
            case 1106: return new ::Ifc4x3_rc4::IfcStructuralLoadStatic(data);
            case 1107: return new ::Ifc4x3_rc4::IfcStructuralLoadTemperature(data);
            case 1108: return new ::Ifc4x3_rc4::IfcStructuralMember(data);
            case 1109: return new ::Ifc4x3_rc4::IfcStructuralPlanarAction(data);
            case 1110: return new ::Ifc4x3_rc4::IfcStructuralPointAction(data);
            case 1111: return new ::Ifc4x3_rc4::IfcStructuralPointConnection(data);
            case 1112: return new ::Ifc4x3_rc4::IfcStructuralPointReaction(data);
            case 1113: return new ::Ifc4x3_rc4::IfcStructuralReaction(data);
            case 1114: return new ::Ifc4x3_rc4::IfcStructuralResultGroup(data);
            case 1115: return new ::Ifc4x3_rc4::IfcStructuralSurfaceAction(data);
            case 1116: return new ::Ifc4x3_rc4::IfcStructuralSurfaceActivityTypeEnum(data);
            case 1117: return new ::Ifc4x3_rc4::IfcStructuralSurfaceConnection(data);
            case 1118: return new ::Ifc4x3_rc4::IfcStructuralSurfaceMember(data);
            case 1119: return new ::Ifc4x3_rc4::IfcStructuralSurfaceMemberTypeEnum(data);
            case 1120: return new ::Ifc4x3_rc4::IfcStructuralSurfaceMemberVarying(data);
            case 1121: return new ::Ifc4x3_rc4::IfcStructuralSurfaceReaction(data);
            case 1122: return new ::Ifc4x3_rc4::IfcStyledItem(data);
            case 1123: return new ::Ifc4x3_rc4::IfcStyledRepresentation(data);
            case 1124: return new ::Ifc4x3_rc4::IfcStyleModel(data);
            case 1125: return new ::Ifc4x3_rc4::IfcSubContractResource(data);
            case 1126: return new ::Ifc4x3_rc4::IfcSubContractResourceType(data);
            case 1127: return new ::Ifc4x3_rc4::IfcSubContractResourceTypeEnum(data);
            case 1128: return new ::Ifc4x3_rc4::IfcSubedge(data);
            case 1129: return new ::Ifc4x3_rc4::IfcSurface(data);
            case 1130: return new ::Ifc4x3_rc4::IfcSurfaceCurve(data);
            case 1131: return new ::Ifc4x3_rc4::IfcSurfaceCurveSweptAreaSolid(data);
            case 1132: return new ::Ifc4x3_rc4::IfcSurfaceFeature(data);
            case 1133: return new ::Ifc4x3_rc4::IfcSurfaceFeatureTypeEnum(data);
            case 1134: return new ::Ifc4x3_rc4::IfcSurfaceOfLinearExtrusion(data);
            case 1135: return new ::Ifc4x3_rc4::IfcSurfaceOfRevolution(data);
            case 1137: return new ::Ifc4x3_rc4::IfcSurfaceReinforcementArea(data);
            case 1138: return new ::Ifc4x3_rc4::IfcSurfaceSide(data);
            case 1139: return new ::Ifc4x3_rc4::IfcSurfaceStyle(data);
            case 1141: return new ::Ifc4x3_rc4::IfcSurfaceStyleLighting(data);
            case 1142: return new ::Ifc4x3_rc4::IfcSurfaceStyleRefraction(data);
            case 1143: return new ::Ifc4x3_rc4::IfcSurfaceStyleRendering(data);
            case 1144: return new ::Ifc4x3_rc4::IfcSurfaceStyleShading(data);
            case 1145: return new ::Ifc4x3_rc4::IfcSurfaceStyleWithTextures(data);
            case 1146: return new ::Ifc4x3_rc4::IfcSurfaceTexture(data);
            case 1147: return new ::Ifc4x3_rc4::IfcSweptAreaSolid(data);
            case 1148: return new ::Ifc4x3_rc4::IfcSweptDiskSolid(data);
            case 1149: return new ::Ifc4x3_rc4::IfcSweptDiskSolidPolygonal(data);
            case 1150: return new ::Ifc4x3_rc4::IfcSweptSurface(data);
            case 1151: return new ::Ifc4x3_rc4::IfcSwitchingDevice(data);
            case 1152: return new ::Ifc4x3_rc4::IfcSwitchingDeviceType(data);
            case 1153: return new ::Ifc4x3_rc4::IfcSwitchingDeviceTypeEnum(data);
            case 1154: return new ::Ifc4x3_rc4::IfcSystem(data);
            case 1155: return new ::Ifc4x3_rc4::IfcSystemFurnitureElement(data);
            case 1156: return new ::Ifc4x3_rc4::IfcSystemFurnitureElementType(data);
            case 1157: return new ::Ifc4x3_rc4::IfcSystemFurnitureElementTypeEnum(data);
            case 1158: return new ::Ifc4x3_rc4::IfcTable(data);
            case 1159: return new ::Ifc4x3_rc4::IfcTableColumn(data);
            case 1160: return new ::Ifc4x3_rc4::IfcTableRow(data);
            case 1161: return new ::Ifc4x3_rc4::IfcTank(data);
            case 1162: return new ::Ifc4x3_rc4::IfcTankType(data);
            case 1163: return new ::Ifc4x3_rc4::IfcTankTypeEnum(data);
            case 1164: return new ::Ifc4x3_rc4::IfcTask(data);
            case 1165: return new ::Ifc4x3_rc4::IfcTaskDurationEnum(data);
            case 1166: return new ::Ifc4x3_rc4::IfcTaskTime(data);
            case 1167: return new ::Ifc4x3_rc4::IfcTaskTimeRecurring(data);
            case 1168: return new ::Ifc4x3_rc4::IfcTaskType(data);
            case 1169: return new ::Ifc4x3_rc4::IfcTaskTypeEnum(data);
            case 1170: return new ::Ifc4x3_rc4::IfcTelecomAddress(data);
            case 1171: return new ::Ifc4x3_rc4::IfcTemperatureGradientMeasure(data);
            case 1172: return new ::Ifc4x3_rc4::IfcTemperatureRateOfChangeMeasure(data);
            case 1173: return new ::Ifc4x3_rc4::IfcTendon(data);
            case 1174: return new ::Ifc4x3_rc4::IfcTendonAnchor(data);
            case 1175: return new ::Ifc4x3_rc4::IfcTendonAnchorType(data);
            case 1176: return new ::Ifc4x3_rc4::IfcTendonAnchorTypeEnum(data);
            case 1177: return new ::Ifc4x3_rc4::IfcTendonConduit(data);
            case 1178: return new ::Ifc4x3_rc4::IfcTendonConduitType(data);
            case 1179: return new ::Ifc4x3_rc4::IfcTendonConduitTypeEnum(data);
            case 1180: return new ::Ifc4x3_rc4::IfcTendonType(data);
            case 1181: return new ::Ifc4x3_rc4::IfcTendonTypeEnum(data);
            case 1182: return new ::Ifc4x3_rc4::IfcTessellatedFaceSet(data);
            case 1183: return new ::Ifc4x3_rc4::IfcTessellatedItem(data);
            case 1184: return new ::Ifc4x3_rc4::IfcText(data);
            case 1185: return new ::Ifc4x3_rc4::IfcTextAlignment(data);
            case 1186: return new ::Ifc4x3_rc4::IfcTextDecoration(data);
            case 1187: return new ::Ifc4x3_rc4::IfcTextFontName(data);
            case 1189: return new ::Ifc4x3_rc4::IfcTextLiteral(data);
            case 1190: return new ::Ifc4x3_rc4::IfcTextLiteralWithExtent(data);
            case 1191: return new ::Ifc4x3_rc4::IfcTextPath(data);
            case 1192: return new ::Ifc4x3_rc4::IfcTextStyle(data);
            case 1193: return new ::Ifc4x3_rc4::IfcTextStyleFontModel(data);
            case 1194: return new ::Ifc4x3_rc4::IfcTextStyleForDefinedFont(data);
            case 1195: return new ::Ifc4x3_rc4::IfcTextStyleTextModel(data);
            case 1196: return new ::Ifc4x3_rc4::IfcTextTransformation(data);
            case 1197: return new ::Ifc4x3_rc4::IfcTextureCoordinate(data);
            case 1198: return new ::Ifc4x3_rc4::IfcTextureCoordinateGenerator(data);
            case 1199: return new ::Ifc4x3_rc4::IfcTextureMap(data);
            case 1200: return new ::Ifc4x3_rc4::IfcTextureVertex(data);
            case 1201: return new ::Ifc4x3_rc4::IfcTextureVertexList(data);
            case 1202: return new ::Ifc4x3_rc4::IfcThermalAdmittanceMeasure(data);
            case 1203: return new ::Ifc4x3_rc4::IfcThermalConductivityMeasure(data);
            case 1204: return new ::Ifc4x3_rc4::IfcThermalExpansionCoefficientMeasure(data);
            case 1205: return new ::Ifc4x3_rc4::IfcThermalResistanceMeasure(data);
            case 1206: return new ::Ifc4x3_rc4::IfcThermalTransmittanceMeasure(data);
            case 1207: return new ::Ifc4x3_rc4::IfcThermodynamicTemperatureMeasure(data);
            case 1208: return new ::Ifc4x3_rc4::IfcThirdOrderPolynomialSpiral(data);
            case 1209: return new ::Ifc4x3_rc4::IfcTime(data);
            case 1210: return new ::Ifc4x3_rc4::IfcTimeMeasure(data);
            case 1212: return new ::Ifc4x3_rc4::IfcTimePeriod(data);
            case 1213: return new ::Ifc4x3_rc4::IfcTimeSeries(data);
            case 1214: return new ::Ifc4x3_rc4::IfcTimeSeriesDataTypeEnum(data);
            case 1215: return new ::Ifc4x3_rc4::IfcTimeSeriesValue(data);
            case 1216: return new ::Ifc4x3_rc4::IfcTimeStamp(data);
            case 1217: return new ::Ifc4x3_rc4::IfcTopologicalRepresentationItem(data);
            case 1218: return new ::Ifc4x3_rc4::IfcTopologyRepresentation(data);
            case 1219: return new ::Ifc4x3_rc4::IfcToroidalSurface(data);
            case 1220: return new ::Ifc4x3_rc4::IfcTorqueMeasure(data);
            case 1221: return new ::Ifc4x3_rc4::IfcTrackElement(data);
            case 1222: return new ::Ifc4x3_rc4::IfcTrackElementType(data);
            case 1223: return new ::Ifc4x3_rc4::IfcTrackElementTypeEnum(data);
            case 1224: return new ::Ifc4x3_rc4::IfcTransformer(data);
            case 1225: return new ::Ifc4x3_rc4::IfcTransformerType(data);
            case 1226: return new ::Ifc4x3_rc4::IfcTransformerTypeEnum(data);
            case 1227: return new ::Ifc4x3_rc4::IfcTransitionCode(data);
            case 1229: return new ::Ifc4x3_rc4::IfcTransportElement(data);
            case 1230: return new ::Ifc4x3_rc4::IfcTransportElementFixedTypeEnum(data);
            case 1231: return new ::Ifc4x3_rc4::IfcTransportElementNonFixedTypeEnum(data);
            case 1232: return new ::Ifc4x3_rc4::IfcTransportElementType(data);
            case 1234: return new ::Ifc4x3_rc4::IfcTrapeziumProfileDef(data);
            case 1235: return new ::Ifc4x3_rc4::IfcTriangulatedFaceSet(data);
            case 1236: return new ::Ifc4x3_rc4::IfcTriangulatedIrregularNetwork(data);
            case 1237: return new ::Ifc4x3_rc4::IfcTrimmedCurve(data);
            case 1238: return new ::Ifc4x3_rc4::IfcTrimmingPreference(data);
            case 1240: return new ::Ifc4x3_rc4::IfcTShapeProfileDef(data);
            case 1241: return new ::Ifc4x3_rc4::IfcTubeBundle(data);
            case 1242: return new ::Ifc4x3_rc4::IfcTubeBundleType(data);
            case 1243: return new ::Ifc4x3_rc4::IfcTubeBundleTypeEnum(data);
            case 1244: return new ::Ifc4x3_rc4::IfcTypeObject(data);
            case 1245: return new ::Ifc4x3_rc4::IfcTypeProcess(data);
            case 1246: return new ::Ifc4x3_rc4::IfcTypeProduct(data);
            case 1247: return new ::Ifc4x3_rc4::IfcTypeResource(data);
            case 1249: return new ::Ifc4x3_rc4::IfcUnitaryControlElement(data);
            case 1250: return new ::Ifc4x3_rc4::IfcUnitaryControlElementType(data);
            case 1251: return new ::Ifc4x3_rc4::IfcUnitaryControlElementTypeEnum(data);
            case 1252: return new ::Ifc4x3_rc4::IfcUnitaryEquipment(data);
            case 1253: return new ::Ifc4x3_rc4::IfcUnitaryEquipmentType(data);
            case 1254: return new ::Ifc4x3_rc4::IfcUnitaryEquipmentTypeEnum(data);
            case 1255: return new ::Ifc4x3_rc4::IfcUnitAssignment(data);
            case 1256: return new ::Ifc4x3_rc4::IfcUnitEnum(data);
            case 1257: return new ::Ifc4x3_rc4::IfcURIReference(data);
            case 1258: return new ::Ifc4x3_rc4::IfcUShapeProfileDef(data);
            case 1260: return new ::Ifc4x3_rc4::IfcValve(data);
            case 1261: return new ::Ifc4x3_rc4::IfcValveType(data);
            case 1262: return new ::Ifc4x3_rc4::IfcValveTypeEnum(data);
            case 1263: return new ::Ifc4x3_rc4::IfcVaporPermeabilityMeasure(data);
            case 1264: return new ::Ifc4x3_rc4::IfcVector(data);
            case 1266: return new ::Ifc4x3_rc4::IfcVertex(data);
            case 1267: return new ::Ifc4x3_rc4::IfcVertexLoop(data);
            case 1268: return new ::Ifc4x3_rc4::IfcVertexPoint(data);
            case 1269: return new ::Ifc4x3_rc4::IfcVibrationDamper(data);
            case 1270: return new ::Ifc4x3_rc4::IfcVibrationDamperType(data);
            case 1271: return new ::Ifc4x3_rc4::IfcVibrationDamperTypeEnum(data);
            case 1272: return new ::Ifc4x3_rc4::IfcVibrationIsolator(data);
            case 1273: return new ::Ifc4x3_rc4::IfcVibrationIsolatorType(data);
            case 1274: return new ::Ifc4x3_rc4::IfcVibrationIsolatorTypeEnum(data);
            case 1275: return new ::Ifc4x3_rc4::IfcVirtualElement(data);
            case 1276: return new ::Ifc4x3_rc4::IfcVirtualGridIntersection(data);
            case 1277: return new ::Ifc4x3_rc4::IfcVoidingFeature(data);
            case 1278: return new ::Ifc4x3_rc4::IfcVoidingFeatureTypeEnum(data);
            case 1279: return new ::Ifc4x3_rc4::IfcVoidStratum(data);
            case 1280: return new ::Ifc4x3_rc4::IfcVolumeMeasure(data);
            case 1281: return new ::Ifc4x3_rc4::IfcVolumetricFlowRateMeasure(data);
            case 1282: return new ::Ifc4x3_rc4::IfcWall(data);
            case 1283: return new ::Ifc4x3_rc4::IfcWallElementedCase(data);
            case 1284: return new ::Ifc4x3_rc4::IfcWallStandardCase(data);
            case 1285: return new ::Ifc4x3_rc4::IfcWallType(data);
            case 1286: return new ::Ifc4x3_rc4::IfcWallTypeEnum(data);
            case 1287: return new ::Ifc4x3_rc4::IfcWarpingConstantMeasure(data);
            case 1288: return new ::Ifc4x3_rc4::IfcWarpingMomentMeasure(data);
            case 1290: return new ::Ifc4x3_rc4::IfcWasteTerminal(data);
            case 1291: return new ::Ifc4x3_rc4::IfcWasteTerminalType(data);
            case 1292: return new ::Ifc4x3_rc4::IfcWasteTerminalTypeEnum(data);
            case 1293: return new ::Ifc4x3_rc4::IfcWaterStratum(data);
            case 1294: return new ::Ifc4x3_rc4::IfcWindow(data);
            case 1295: return new ::Ifc4x3_rc4::IfcWindowLiningProperties(data);
            case 1296: return new ::Ifc4x3_rc4::IfcWindowPanelOperationEnum(data);
            case 1297: return new ::Ifc4x3_rc4::IfcWindowPanelPositionEnum(data);
            case 1298: return new ::Ifc4x3_rc4::IfcWindowPanelProperties(data);
            case 1299: return new ::Ifc4x3_rc4::IfcWindowStandardCase(data);
            case 1300: return new ::Ifc4x3_rc4::IfcWindowStyle(data);
            case 1301: return new ::Ifc4x3_rc4::IfcWindowStyleConstructionEnum(data);
            case 1302: return new ::Ifc4x3_rc4::IfcWindowStyleOperationEnum(data);
            case 1303: return new ::Ifc4x3_rc4::IfcWindowType(data);
            case 1304: return new ::Ifc4x3_rc4::IfcWindowTypeEnum(data);
            case 1305: return new ::Ifc4x3_rc4::IfcWindowTypePartitioningEnum(data);
            case 1306: return new ::Ifc4x3_rc4::IfcWorkCalendar(data);
            case 1307: return new ::Ifc4x3_rc4::IfcWorkCalendarTypeEnum(data);
            case 1308: return new ::Ifc4x3_rc4::IfcWorkControl(data);
            case 1309: return new ::Ifc4x3_rc4::IfcWorkPlan(data);
            case 1310: return new ::Ifc4x3_rc4::IfcWorkPlanTypeEnum(data);
            case 1311: return new ::Ifc4x3_rc4::IfcWorkSchedule(data);
            case 1312: return new ::Ifc4x3_rc4::IfcWorkScheduleTypeEnum(data);
            case 1313: return new ::Ifc4x3_rc4::IfcWorkTime(data);
            case 1314: return new ::Ifc4x3_rc4::IfcZone(data);
            case 1315: return new ::Ifc4x3_rc4::IfcZShapeProfileDef(data);
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
"RAILWAYCROCODILE"s,
"RAILWAYDETONATOR"s,
"IfcAlignmentCantSegmentTypeEnum"s,
"BLOSSCURVE"s,
"CONSTANTCANT"s,
"COSINECURVE"s,
"HELMERTCURVE"s,
"LINEARTRANSITION"s,
"SINECURVE"s,
"VIENNESEBEND"s,
"IfcAlignmentHorizontalSegmentTypeEnum"s,
"LINE"s,
"CIRCULARARC"s,
"CLOTHOID"s,
"CUBIC"s,
"IfcAlignmentTypeEnum"s,
"IfcAlignmentVerticalSegmentTypeEnum"s,
"CONSTANTGRADIENT"s,
"PARABOLICARC"s,
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
"IfcAnnotationTypeEnum"s,
"ASSUMEDPOINT"s,
"ASBUILTAREA"s,
"ASBUILTLINE"s,
"NON_PHYSICAL_SIGNAL"s,
"ASSUMEDLINE"s,
"WIDTHEVENT"s,
"ASSUMEDAREA"s,
"SUPERELEVATIONEVENT"s,
"ASBUILTPOINT"s,
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
"COMMUNICATIONTERMINAL"s,
"RECORDINGEQUIPMENT"s,
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
"GIRDER_SEGMENT"s,
"DIAPHRAGM"s,
"PIERCAP"s,
"HATSTONE"s,
"CORNICE"s,
"EDGEBEAM"s,
"IfcBearingTypeDisplacementEnum"s,
"FIXED_MOVEMENT"s,
"GUIDED_LONGITUDINAL"s,
"GUIDED_TRANSVERSAL"s,
"FREE_MOVEMENT"s,
"IfcBearingTypeEnum"s,
"CYLINDRICAL"s,
"SPHERICAL"s,
"ELASTOMERIC"s,
"POT"s,
"GUIDE"s,
"ROCKER"s,
"ROLLER"s,
"DISK"s,
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
"INSULATION"s,
"PRECASTPANEL"s,
"APRON"s,
"ARMOURUNIT"s,
"SAFETYCAGE"s,
"IfcBuildingElementProxyTypeEnum"s,
"COMPLEX"s,
"ELEMENT"s,
"PARTIAL"s,
"PROVISIONFORVOID"s,
"PROVISIONFORSPACE"s,
"IfcBuildingSystemTypeEnum"s,
"FENESTRATION"s,
"LOADBEARING"s,
"OUTERSHELL"s,
"SHADING"s,
"REINFORCING"s,
"PRESTRESSING"s,
"EROSIONPREVENTION"s,
"IfcBuiltSystemTypeEnum"s,
"MOORING"s,
"TRACKCIRCUIT"s,
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
"CABLEBRACKET"s,
"CATENARYWIRE"s,
"DROPPER"s,
"IfcCableFittingTypeEnum"s,
"CONNECTOR"s,
"ENTRY"s,
"EXIT"s,
"JUNCTION"s,
"TRANSITION"s,
"FANOUT"s,
"IfcCableSegmentTypeEnum"s,
"BUSBARSEGMENT"s,
"CABLESEGMENT"s,
"CONDUCTORSEGMENT"s,
"CORESEGMENT"s,
"CONTACTWIRESEGMENT"s,
"FIBERSEGMENT"s,
"FIBERTUBE"s,
"OPTICALCABLESEGMENT"s,
"STITCHWIRE"s,
"WIREPAIRSEGMENT"s,
"IfcCaissonFoundationTypeEnum"s,
"WELL"s,
"CAISSON"s,
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
"PIERSTEM"s,
"PIERSTEM_SEGMENT"s,
"STANDCOLUMN"s,
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
"AUTOMATON"s,
"INTELLIGENTPERIPHERAL"s,
"IPNETWORKEQUIPMENT"s,
"OPTICALNETWORKUNIT"s,
"TELECOMMAND"s,
"TELEPHONYEXCHANGE"s,
"TRANSITIONCOMPONENT"s,
"TRANSPONDER"s,
"TRANSPORTEQUIPMENT"s,
"OPTICALLINETERMINAL"s,
"LINESIDEELECTRONICUNIT"s,
"RADIOBLOCKCENTER"s,
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
"IfcConveyorSegmentTypeEnum"s,
"CHUTECONVEYOR"s,
"BELTCONVEYOR"s,
"SCREWCONVEYOR"s,
"BUCKETCONVEYOR"s,
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
"IfcCourseTypeEnum"s,
"ARMOUR"s,
"FILTER"s,
"BALLASTBED"s,
"CORE"s,
"PAVEMENT"s,
"PROTECTION"s,
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
"COPING"s,
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
"EXPANSION_JOINT_DEVICE"s,
"CABLEARRANGER"s,
"INSULATOR"s,
"LOCK"s,
"TENSIONINGEQUIPMENT"s,
"RAILPAD"s,
"SLIDINGCHAIR"s,
"RAIL_LUBRICATION"s,
"PANEL_STRENGTHENING"s,
"RAILBRACE"s,
"ELASTIC_CUSHION"s,
"SOUNDABSORPTION"s,
"POINTMACHINEMOUNTINGDEVICE"s,
"POINT_MACHINE_LOCKING_DEVICE"s,
"RAIL_MECHANICAL_EQUIPMENT"s,
"BIRDPROTECTION"s,
"IfcDistributionBoardTypeEnum"s,
"SWITCHBOARD"s,
"CONSUMERUNIT"s,
"MOTORCONTROLCENTRE"s,
"DISTRIBUTIONFRAME"s,
"DISTRIBUTIONBOARD"s,
"DISPATCHINGBOARD"s,
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
"CATENARY_SYSTEM"s,
"OVERHEAD_CONTACTLINE_SYSTEM"s,
"RETURN_CIRCUIT"s,
"FIXEDTRANSMISSIONNETWORK"s,
"OPERATIONALTELEPHONYSYSTEM"s,
"MOBILENETWORK"s,
"MONITORINGSYSTEM"s,
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
"BOOM_BARRIER"s,
"TURNSTILE"s,
"IfcDoorTypeOperationEnum"s,
"DOUBLE_PANEL_SINGLE_SWING"s,
"DOUBLE_PANEL_SINGLE_SWING_OPPOSITE_LEFT"s,
"DOUBLE_PANEL_SINGLE_SWING_OPPOSITE_RIGHT"s,
"DOUBLE_PANEL_DOUBLE_SWING"s,
"DOUBLE_PANEL_SLIDING"s,
"DOUBLE_PANEL_FOLDING"s,
"REVOLVING_HORIZONTAL"s,
"SWING_FIXED_LEFT"s,
"SWING_FIXED_RIGHT"s,
"DOUBLE_PANEL_LIFTING_VERTICAL"s,
"LIFTING_HORIZONTAL"s,
"LIFTING_VERTICAL_LEFT"s,
"LIFTING_VERTICAL_RIGHT"s,
"REVOLVING_VERTICAL"s,
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
"IfcEarthworksCutTypeEnum"s,
"DREDGING"s,
"EXCAVATION"s,
"OVEREXCAVATION"s,
"TOPSOILREMOVAL"s,
"STEPEXCAVATION"s,
"PAVEMENTMILLING"s,
"CUT"s,
"BASE_EXCAVATION"s,
"IfcEarthworksFillTypeEnum"s,
"BACKFILL"s,
"COUNTERWEIGHT"s,
"SUBGRADE"s,
"EMBANKMENT"s,
"TRANSITIONSECTION"s,
"SUBGRADEBED"s,
"SLOPEFILL"s,
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
"IfcElectricFlowStorageDeviceTypeEnum"s,
"BATTERY"s,
"CAPACITORBANK"s,
"HARMONICFILTER"s,
"INDUCTORBANK"s,
"UPS"s,
"CAPACITOR"s,
"COMPENSATOR"s,
"INDUCTOR"s,
"RECHARGER"s,
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
"TIMECLOCK"s,
"TIMEDELAY"s,
"RELAY"s,
"IfcElectricVoltageMeasure"s,
"IfcElementAssemblyTypeEnum"s,
"ACCESSORY_ASSEMBLY"s,
"ARCH"s,
"BEAM_GRID"s,
"BRACED_FRAME"s,
"REINFORCEMENT_UNIT"s,
"RIGID_FRAME"s,
"SLAB_FIELD"s,
"CROSS_BRACING"s,
"MAST"s,
"SIGNALASSEMBLY"s,
"GRID"s,
"SHELTER"s,
"SUPPORTINGASSEMBLY"s,
"SUSPENSIONASSEMBLY"s,
"TRACTION_SWITCHING_ASSEMBLY"s,
"TRACKPANEL"s,
"TURNOUTPANEL"s,
"DILATATIONPANEL"s,
"RAIL_MECHANICAL_EQUIPMENT_ASSEMBLY"s,
"ENTRANCEWORKS"s,
"SUMPBUSTER"s,
"TRAFFIC_CALMING_DEVICE"s,
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
"IfcFacilityPartCommonTypeEnum"s,
"SEGMENT"s,
"ABOVEGROUND"s,
"LEVELCROSSING"s,
"BELOWGROUND"s,
"TERMINAL"s,
"IfcFacilityUsageEnum"s,
"LATERAL"s,
"REGION"s,
"VERTICAL"s,
"LONGITUDINAL"s,
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
"FIREMONITOR"s,
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
"COMBINED"s,
"VOLTMETER"s,
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
"TECHNICALCABINET"s,
"IfcGeographicElementTypeEnum"s,
"TERRAIN"s,
"SOIL_BORING_POINT"s,
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
"TURNOUTHEATING"s,
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
"IfcImpactProtectionDeviceTypeEnum"s,
"CRASHCUSHION"s,
"DAMPINGSYSTEM"s,
"FENDER"s,
"BUMPER"s,
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
"IfcLiquidTerminalTypeEnum"s,
"LOADINGARM"s,
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
"IfcMarineFacilityTypeEnum"s,
"CANAL"s,
"WATERWAYSHIPLIFT"s,
"REVETMENT"s,
"LAUNCHRECOVERY"s,
"MARINEDEFENCE"s,
"HYDROLIFT"s,
"SHIPYARD"s,
"SHIPLIFT"s,
"PORT"s,
"QUAY"s,
"FLOATINGDOCK"s,
"NAVIGATIONALCHANNEL"s,
"BREAKWATER"s,
"DRYDOCK"s,
"JETTY"s,
"SHIPLOCK"s,
"BARRIERBEACH"s,
"SLIPWAY"s,
"WATERWAY"s,
"IfcMarinePartTypeEnum"s,
"CREST"s,
"MANUFACTURING"s,
"LOWWATERLINE"s,
"WATERFIELD"s,
"CILL_LEVEL"s,
"BERTHINGSTRUCTURE"s,
"COPELEVEL"s,
"CHAMBER"s,
"STORAGEAREA"s,
"APPROACHCHANNEL"s,
"VEHICLESERVICING"s,
"SHIPTRANSFER"s,
"GATEHEAD"s,
"GUDINGSTRUCTURE"s,
"BELOWWATERLINE"s,
"WEATHERSIDE"s,
"LANDFIELD"s,
"LEEWARDSIDE"s,
"ABOVEWATERLINE"s,
"ANCHORAGE"s,
"NAVIGATIONALAREA"s,
"HIGHWATERLINE"s,
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
"COUPLER"s,
"RAILJOINT"s,
"RAILFASTENING"s,
"CHAIN"s,
"ROPE"s,
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
"STIFFENING_RIB"s,
"ARCH_SEGMENT"s,
"SUSPENSION_CABLE"s,
"SUSPENDER"s,
"STAY_CABLE"s,
"STRUCTURALCABLE"s,
"TIEBAR"s,
"IfcMobileTelecommunicationsApplianceTypeEnum"s,
"E_UTRAN_NODE_B"s,
"REMOTERADIOUNIT"s,
"ACCESSPOINT"s,
"BASETRANSCEIVERSTATION"s,
"REMOTEUNIT"s,
"BASEBANDUNIT"s,
"MASTERUNIT"s,
"GATEWAY_GPRS_SUPPORT_NODE"s,
"SUBSCRIBERSERVER"s,
"MOBILESWITCHINGCENTER"s,
"MSCSERVER"s,
"PACKETCONTROLUNIT"s,
"SERVICE_GPRS_SUPPORT_NODE"s,
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
"LINETENSIONER"s,
"MAGNETICDEVICE"s,
"MOORINGHOOKS"s,
"VACUUMDEVICE"s,
"BOLLARD"s,
"IfcMotorConnectionTypeEnum"s,
"BELTDRIVE"s,
"COUPLING"s,
"DIRECTDRIVE"s,
"IfcNavigationElementTypeEnum"s,
"BEACON"s,
"BUOY"s,
"IfcNonNegativeLengthMeasure"s,
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
"DRIVEN"s,
"JETGROUTING"s,
"COHESION"s,
"FRICTION"s,
"SUPPORT"s,
"IfcPipeFittingTypeEnum"s,
"IfcPipeSegmentTypeEnum"s,
"GUTTER"s,
"SPOOL"s,
"IfcPlanarForceMeasure"s,
"IfcPlaneAngleMeasure"s,
"IfcPlateTypeEnum"s,
"CURTAIN_PANEL"s,
"SHEET"s,
"FLANGE_PLATE"s,
"WEB_PLATE"s,
"STIFFENER_PLATE"s,
"GUSSET_PLATE"s,
"COVER_PLATE"s,
"SPLICE_PLATE"s,
"BASE_PLATE"s,
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
"BLISTER"s,
"DEVIATOR"s,
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
"ANTI_ARCING_DEVICE"s,
"SPARKGAP"s,
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
"RACKRAIL"s,
"BLADE"s,
"GUARDRAIL"s,
"STOCKRAIL"s,
"CHECKRAIL"s,
"RAIL"s,
"IfcRailingTypeEnum"s,
"HANDRAIL"s,
"BALUSTRADE"s,
"FENCE"s,
"IfcRailwayPartTypeEnum"s,
"TRACKSTRUCTURE"s,
"TRACKSTRUCTUREPART"s,
"LINESIDESTRUCTUREPART"s,
"DILATATIONSUPERSTRUCTURE"s,
"PLAINTRACKSUPESTRUCTURE"s,
"LINESIDESTRUCTURE"s,
"TURNOUTSUPERSTRUCTURE"s,
"IfcRailwayTypeEnum"s,
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
"REFERENCEMARKER"s,
"LANDMARK"s,
"BOUNDARY"s,
"POSITION"s,
"IfcReflectanceMethodEnum"s,
"BLINN"s,
"FLAT"s,
"GLASS"s,
"MATT"s,
"MIRROR"s,
"PHONG"s,
"STRAUSS"s,
"IfcReinforcedSoilTypeEnum"s,
"SURCHARGEPRELOADED"s,
"VERTICALLYDRAINED"s,
"DYNAMICALLYCOMPACTED"s,
"REPLACED"s,
"ROLLERCOMPACTED"s,
"GROUTED"s,
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
"SPACEBAR"s,
"IfcReinforcingMeshTypeEnum"s,
"IfcRoadPartTypeEnum"s,
"ROADSIDEPART"s,
"BUS_STOP"s,
"HARDSHOULDER"s,
"PASSINGBAY"s,
"ROADWAYPLATEAU"s,
"ROADSIDE"s,
"REFUGEISLAND"s,
"TOLLPLAZA"s,
"CENTRALRESERVE"s,
"SIDEWALK"s,
"PARKINGBAY"s,
"RAILWAYCROSSING"s,
"PEDESTRIAN_CROSSING"s,
"SOFTSHOULDER"s,
"BICYCLECROSSING"s,
"CENTRALISLAND"s,
"SHOULDER"s,
"TRAFFICLANE"s,
"ROADSEGMENT"s,
"ROUNDABOUT"s,
"LAYBY"s,
"CARRIAGEWAY"s,
"TRAFFICISLAND"s,
"IfcRoadTypeEnum"s,
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
"EARTHQUAKESENSOR"s,
"FOREIGNOBJECTDETECTIONSENSOR"s,
"OBSTACLESENSOR"s,
"RAINSENSOR"s,
"SNOWDEPTHSENSOR"s,
"TRAINSENSOR"s,
"TURNOUTCLOSURESENSOR"s,
"WHEELSENSOR"s,
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
"IfcSignTypeEnum"s,
"MARKER"s,
"PICTORAL"s,
"IfcSignalTypeEnum"s,
"VISUAL"s,
"AUDIO"s,
"MIXED"s,
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
"APPROACH_SLAB"s,
"WEARING"s,
"TRACKSLAB"s,
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
"BERTH"s,
"IfcSpatialZoneTypeEnum"s,
"CONSTRUCTION"s,
"FIRESAFETY"s,
"OCCUPANCY"s,
"RESERVATION"s,
"INTERFERENCE"s,
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
"LADDER"s,
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
"DEFECT"s,
"HATCHMARKING"s,
"LINEMARKING"s,
"PAVEMENTSURFACEMARKING"s,
"SYMBOLMARKING"s,
"NONSKIDSURFACING"s,
"RUMBLESTRIP"s,
"TRANSVERSERUMBLESTRIP"s,
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
"START_AND_STOP_EQUIPMENT"s,
"IfcSystemFurnitureElementTypeEnum"s,
"PANEL"s,
"WORKSURFACE"s,
"SUBRACK"s,
"IfcTankTypeEnum"s,
"BASIN"s,
"BREAKPRESSURE"s,
"EXPANSION"s,
"FEEDANDEXPANSION"s,
"PRESSUREVESSEL"s,
"STORAGE"s,
"VESSEL"s,
"OILRETENTIONTRAY"s,
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
"FIXED_END"s,
"TENSIONING_END"s,
"IfcTendonConduitTypeEnum"s,
"GROUTING_DUCT"s,
"TRUMPET"s,
"DIABOLO"s,
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
"IfcTrackElementTypeEnum"s,
"TRACKENDOFALIGNMENT"s,
"BLOCKINGDEVICE"s,
"VEHICLESTOP"s,
"SLEEPER"s,
"HALF_SET_OF_BLADES"s,
"SPEEDREGULATOR"s,
"DERAILER"s,
"FROG"s,
"IfcTransformerTypeEnum"s,
"FREQUENCY"s,
"INVERTER"s,
"RECTIFIER"s,
"VOLTAGE"s,
"CHOPPER"s,
"IfcTransitionCode"s,
"DISCONTINUOUS"s,
"CONTSAMEGRADIENT"s,
"CONTSAMEGRADIENTSAMECURVATURE"s,
"IfcTranslationalStiffnessSelect"s,
"IfcTransportElementFixedTypeEnum"s,
"ELEVATOR"s,
"ESCALATOR"s,
"MOVINGWALKWAY"s,
"CRANEWAY"s,
"LIFTINGGEAR"s,
"HAULINGGEAR"s,
"IfcTransportElementNonFixedTypeEnum"s,
"VEHICLE"s,
"VEHICLETRACKED"s,
"ROLLINGSTOCK"s,
"VEHICLEWHEELED"s,
"VEHICLEAIR"s,
"CARGO"s,
"VEHICLEMARINE"s,
"IfcTransportElementTypeSelect"s,
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
"BASESTATIONCONTROLLER"s,
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
"IfcVibrationDamperTypeEnum"s,
"BENDING_YIELD"s,
"SHEAR_YIELD"s,
"AXIAL_YIELD"s,
"VISCOUS"s,
"RUBBER"s,
"IfcVibrationIsolatorTypeEnum"s,
"COMPRESSION"s,
"SPRING"s,
"BASE"s,
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
"RETAININGWALL"s,
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
"IfcCurveMeasureSelect"s,
"IfcDerivedMeasureValue"s,
"IfcFacilityPartTypeSelect"s,
"IfcImpactProtectionDeviceTypeSelect"s,
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
"IfcCosine"s,
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
"IfcOpeningStandardCase"s,
"IfcOutletType"s,
"IfcPavementType"s,
"IfcPerformanceHistory"s,
"IfcPermeableCoveringProperties"s,
"IfcPermit"s,
"IfcPileType"s,
"IfcPipeFittingType"s,
"IfcPipeSegmentType"s,
"IfcPlant"s,
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
"IfcSine"s,
"IfcSite"s,
"IfcSlabType"s,
"IfcSolarDeviceType"s,
"IfcSolidStratum"s,
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
"IfcTransportElement"s,
"IfcTrimmedCurve"s,
"IfcTubeBundleType"s,
"IfcUnitaryEquipmentType"s,
"IfcValveType"s,
"IfcVibrationDamper"s,
"IfcVibrationDamperType"s,
"IfcVibrationIsolator"s,
"IfcVibrationIsolatorType"s,
"IfcVirtualElement"s,
"IfcVoidStratum"s,
"IfcVoidingFeature"s,
"IfcWallType"s,
"IfcWasteTerminalType"s,
"IfcWaterStratum"s,
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
"IfcColumnStandardCase"s,
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
"IfcDoorStandardCase"s,
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
"IfcMemberStandardCase"s,
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
"IfcPlateStandardCase"s,
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
"IfcTrackElement"s,
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
"Location"s,
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
"TexCoords"s,
"TexCoordIndex"s,
"Jurisdiction"s,
"ResponsiblePersons"s,
"LastUpdateDate"s,
"Values"s,
"TimeStamp"s,
"ListValues"s,
"Mountable"s,
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
"InterferenceSpace"s,
"InterferenceType"s,
"ImpliedOrder"s,
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
"FixedAxisVertical"s,
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
"ReferencedInStructures"s,
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
"Types"s,
"IFC4X3_RC4"s};

#if defined(__clang__)
__attribute__((optnone))
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC4X3_RC4_populate_schema() {
    IFC4X3_RC4_IfcAbsorbedDoseMeasure_type = new type_declaration(strings[0], 0, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcAccelerationMeasure_type = new type_declaration(strings[1], 1, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcActionRequestTypeEnum_type = new enumeration_type(strings[2], 3, {
        strings[3],
        strings[4],
        strings[5],
        strings[6],
        strings[7],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcActionSourceTypeEnum_type = new enumeration_type(strings[10], 4, {
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
    IFC4X3_RC4_IfcActionTypeEnum_type = new enumeration_type(strings[36], 5, {
        strings[37],
        strings[38],
        strings[39],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcActuatorTypeEnum_type = new enumeration_type(strings[40], 11, {
        strings[41],
        strings[42],
        strings[43],
        strings[44],
        strings[45],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcAddressTypeEnum_type = new enumeration_type(strings[46], 13, {
        strings[47],
        strings[48],
        strings[49],
        strings[50],
        strings[8]
    });
    IFC4X3_RC4_IfcAirTerminalBoxTypeEnum_type = new enumeration_type(strings[51], 20, {
        strings[52],
        strings[53],
        strings[54],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcAirTerminalTypeEnum_type = new enumeration_type(strings[55], 22, {
        strings[56],
        strings[57],
        strings[58],
        strings[59],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type(strings[60], 25, {
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
    IFC4X3_RC4_IfcAlarmTypeEnum_type = new enumeration_type(strings[70], 28, {
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
    IFC4X3_RC4_IfcAlignmentCantSegmentTypeEnum_type = new enumeration_type(strings[79], 32, {
        strings[80],
        strings[81],
        strings[82],
        strings[83],
        strings[84],
        strings[85],
        strings[86]
    });
    IFC4X3_RC4_IfcAlignmentHorizontalSegmentTypeEnum_type = new enumeration_type(strings[87], 35, {
        strings[88],
        strings[89],
        strings[90],
        strings[91],
        strings[83],
        strings[80],
        strings[82],
        strings[85],
        strings[86]
    });
    IFC4X3_RC4_IfcAlignmentTypeEnum_type = new enumeration_type(strings[92], 38, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcAlignmentVerticalSegmentTypeEnum_type = new enumeration_type(strings[93], 41, {
        strings[94],
        strings[89],
        strings[95],
        strings[90]
    });
    IFC4X3_RC4_IfcAmountOfSubstanceMeasure_type = new type_declaration(strings[96], 42, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcAnalysisModelTypeEnum_type = new enumeration_type(strings[97], 43, {
        strings[98],
        strings[99],
        strings[100],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcAnalysisTheoryTypeEnum_type = new enumeration_type(strings[101], 44, {
        strings[102],
        strings[103],
        strings[104],
        strings[105],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcAngularVelocityMeasure_type = new type_declaration(strings[106], 45, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcAnnotationTypeEnum_type = new enumeration_type(strings[107], 48, {
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
    IFC4X3_RC4_IfcAreaDensityMeasure_type = new type_declaration(strings[117], 58, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcAreaMeasure_type = new type_declaration(strings[118], 59, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcArithmeticOperatorEnum_type = new enumeration_type(strings[119], 60, {
        strings[120],
        strings[121],
        strings[122],
        strings[123]
    });
    IFC4X3_RC4_IfcAssemblyPlaceEnum_type = new enumeration_type(strings[124], 61, {
        strings[48],
        strings[125],
        strings[9]
    });
    IFC4X3_RC4_IfcAudioVisualApplianceTypeEnum_type = new enumeration_type(strings[126], 66, {
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
    IFC4X3_RC4_IfcBSplineCurveForm_type = new enumeration_type(strings[140], 109, {
        strings[141],
        strings[142],
        strings[143],
        strings[144],
        strings[145],
        strings[146]
    });
    IFC4X3_RC4_IfcBSplineSurfaceForm_type = new enumeration_type(strings[147], 112, {
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
    IFC4X3_RC4_IfcBeamTypeEnum_type = new enumeration_type(strings[158], 75, {
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
    IFC4X3_RC4_IfcBearingTypeDisplacementEnum_type = new enumeration_type(strings[171], 78, {
        strings[172],
        strings[173],
        strings[174],
        strings[175],
        strings[9]
    });
    IFC4X3_RC4_IfcBearingTypeEnum_type = new enumeration_type(strings[176], 79, {
        strings[177],
        strings[178],
        strings[179],
        strings[180],
        strings[181],
        strings[182],
        strings[183],
        strings[184],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcBenchmarkEnum_type = new enumeration_type(strings[185], 80, {
        strings[186],
        strings[187],
        strings[188],
        strings[189],
        strings[190],
        strings[191],
        strings[192],
        strings[193],
        strings[194],
        strings[195]
    });
    IFC4X3_RC4_IfcBinary_type = new type_declaration(strings[196], 82, new simple_type(simple_type::binary_type));
    IFC4X3_RC4_IfcBoilerTypeEnum_type = new enumeration_type(strings[197], 87, {
        strings[198],
        strings[199],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcBoolean_type = new type_declaration(strings[200], 88, new simple_type(simple_type::boolean_type));
    IFC4X3_RC4_IfcBooleanOperator_type = new enumeration_type(strings[201], 91, {
        strings[202],
        strings[203],
        strings[204]
    });
    IFC4X3_RC4_IfcBridgePartTypeEnum_type = new enumeration_type(strings[205], 106, {
        strings[206],
        strings[207],
        strings[208],
        strings[209],
        strings[210],
        strings[211],
        strings[212],
        strings[213],
        strings[214],
        strings[215],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcBridgeTypeEnum_type = new enumeration_type(strings[216], 107, {
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
    IFC4X3_RC4_IfcBuildingElementPartTypeEnum_type = new enumeration_type(strings[225], 117, {
        strings[226],
        strings[227],
        strings[228],
        strings[229],
        strings[230],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcBuildingElementProxyTypeEnum_type = new enumeration_type(strings[231], 120, {
        strings[232],
        strings[233],
        strings[234],
        strings[235],
        strings[236],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcBuildingSystemTypeEnum_type = new enumeration_type(strings[237], 123, {
        strings[238],
        strings[209],
        strings[239],
        strings[240],
        strings[241],
        strings[23],
        strings[242],
        strings[243],
        strings[244],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcBuiltSystemTypeEnum_type = new enumeration_type(strings[245], 127, {
        strings[242],
        strings[246],
        strings[240],
        strings[247],
        strings[244],
        strings[209],
        strings[239],
        strings[241],
        strings[238],
        strings[23],
        strings[243],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcBurnerTypeEnum_type = new enumeration_type(strings[248], 130, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCableCarrierFittingTypeEnum_type = new enumeration_type(strings[249], 133, {
        strings[250],
        strings[251],
        strings[252],
        strings[253],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCableCarrierSegmentTypeEnum_type = new enumeration_type(strings[254], 136, {
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
    IFC4X3_RC4_IfcCableFittingTypeEnum_type = new enumeration_type(strings[262], 139, {
        strings[263],
        strings[264],
        strings[265],
        strings[266],
        strings[267],
        strings[268],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCableSegmentTypeEnum_type = new enumeration_type(strings[269], 142, {
        strings[270],
        strings[271],
        strings[272],
        strings[273],
        strings[274],
        strings[275],
        strings[276],
        strings[277],
        strings[278],
        strings[279],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCaissonFoundationTypeEnum_type = new enumeration_type(strings[280], 145, {
        strings[281],
        strings[282],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCardinalPointReference_type = new type_declaration(strings[283], 146, new simple_type(simple_type::integer_type));
    IFC4X3_RC4_IfcChangeActionEnum_type = new enumeration_type(strings[284], 157, {
        strings[285],
        strings[286],
        strings[287],
        strings[288],
        strings[9]
    });
    IFC4X3_RC4_IfcChillerTypeEnum_type = new enumeration_type(strings[289], 160, {
        strings[290],
        strings[291],
        strings[292],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcChimneyTypeEnum_type = new enumeration_type(strings[293], 163, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCoilTypeEnum_type = new enumeration_type(strings[294], 177, {
        strings[295],
        strings[296],
        strings[297],
        strings[298],
        strings[299],
        strings[300],
        strings[301],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcColumnTypeEnum_type = new enumeration_type(strings[302], 186, {
        strings[303],
        strings[304],
        strings[305],
        strings[306],
        strings[307],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCommunicationsApplianceTypeEnum_type = new enumeration_type(strings[308], 189, {
        strings[309],
        strings[310],
        strings[4],
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
        strings[329],
        strings[330],
        strings[331],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcComplexNumber_type = new type_declaration(strings[332], 190, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IFC4X3_RC4_IfcComplexPropertyTemplateTypeEnum_type = new enumeration_type(strings[333], 193, {
        strings[334],
        strings[335]
    });
    IFC4X3_RC4_IfcCompoundPlaneAngleMeasure_type = new type_declaration(strings[336], 198, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
    IFC4X3_RC4_IfcCompressorTypeEnum_type = new enumeration_type(strings[337], 201, {
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
        strings[350],
        strings[351],
        strings[352],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCondenserTypeEnum_type = new enumeration_type(strings[353], 204, {
        strings[290],
        strings[354],
        strings[291],
        strings[355],
        strings[356],
        strings[357],
        strings[358],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcConnectionTypeEnum_type = new enumeration_type(strings[359], 212, {
        strings[360],
        strings[361],
        strings[362],
        strings[9]
    });
    IFC4X3_RC4_IfcConstraintEnum_type = new enumeration_type(strings[363], 215, {
        strings[364],
        strings[365],
        strings[366],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcConstructionEquipmentResourceTypeEnum_type = new enumeration_type(strings[367], 218, {
        strings[368],
        strings[369],
        strings[370],
        strings[371],
        strings[372],
        strings[373],
        strings[374],
        strings[375],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcConstructionMaterialResourceTypeEnum_type = new enumeration_type(strings[376], 221, {
        strings[377],
        strings[378],
        strings[379],
        strings[380],
        strings[381],
        strings[382],
        strings[383],
        strings[384],
        strings[385],
        strings[9],
        strings[8]
    });
    IFC4X3_RC4_IfcConstructionProductResourceTypeEnum_type = new enumeration_type(strings[386], 224, {
        strings[387],
        strings[388],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcContextDependentMeasure_type = new type_declaration(strings[389], 228, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcControllerTypeEnum_type = new enumeration_type(strings[390], 233, {
        strings[391],
        strings[392],
        strings[393],
        strings[394],
        strings[395],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcConveyorSegmentTypeEnum_type = new enumeration_type(strings[396], 238, {
        strings[397],
        strings[398],
        strings[399],
        strings[400],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCooledBeamTypeEnum_type = new enumeration_type(strings[401], 241, {
        strings[402],
        strings[403],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCoolingTowerTypeEnum_type = new enumeration_type(strings[404], 244, {
        strings[405],
        strings[406],
        strings[407],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCostItemTypeEnum_type = new enumeration_type(strings[408], 250, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCostScheduleTypeEnum_type = new enumeration_type(strings[409], 252, {
        strings[410],
        strings[411],
        strings[412],
        strings[413],
        strings[414],
        strings[415],
        strings[416],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCountMeasure_type = new type_declaration(strings[417], 254, new simple_type(simple_type::number_type));
    IFC4X3_RC4_IfcCourseTypeEnum_type = new enumeration_type(strings[418], 257, {
        strings[419],
        strings[420],
        strings[421],
        strings[422],
        strings[423],
        strings[424],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCoveringTypeEnum_type = new enumeration_type(strings[425], 260, {
        strings[426],
        strings[427],
        strings[428],
        strings[429],
        strings[430],
        strings[431],
        strings[226],
        strings[432],
        strings[433],
        strings[434],
        strings[435],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCrewResourceTypeEnum_type = new enumeration_type(strings[436], 263, {
        strings[47],
        strings[48],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCurtainWallTypeEnum_type = new enumeration_type(strings[437], 271, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcCurvatureMeasure_type = new type_declaration(strings[438], 272, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcCurveInterpolationEnum_type = new enumeration_type(strings[439], 277, {
        strings[440],
        strings[441],
        strings[442],
        strings[9]
    });
    IFC4X3_RC4_IfcDamperTypeEnum_type = new enumeration_type(strings[443], 290, {
        strings[444],
        strings[445],
        strings[446],
        strings[447],
        strings[448],
        strings[449],
        strings[450],
        strings[451],
        strings[452],
        strings[453],
        strings[454],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDataOriginEnum_type = new enumeration_type(strings[455], 291, {
        strings[456],
        strings[457],
        strings[458],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDate_type = new type_declaration(strings[459], 292, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcDateTime_type = new type_declaration(strings[460], 293, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcDayInMonthNumber_type = new type_declaration(strings[461], 294, new simple_type(simple_type::integer_type));
    IFC4X3_RC4_IfcDayInWeekNumber_type = new type_declaration(strings[462], 295, new simple_type(simple_type::integer_type));
    IFC4X3_RC4_IfcDerivedUnitEnum_type = new enumeration_type(strings[463], 303, {
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
        strings[514],
        strings[515],
        strings[8]
    });
    IFC4X3_RC4_IfcDescriptiveMeasure_type = new type_declaration(strings[516], 304, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcDimensionCount_type = new type_declaration(strings[517], 306, new simple_type(simple_type::integer_type));
    IFC4X3_RC4_IfcDirectionSenseEnum_type = new enumeration_type(strings[518], 308, {
        strings[519],
        strings[520]
    });
    IFC4X3_RC4_IfcDiscreteAccessoryTypeEnum_type = new enumeration_type(strings[521], 313, {
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
    IFC4X3_RC4_IfcDistributionBoardTypeEnum_type = new enumeration_type(strings[541], 316, {
        strings[542],
        strings[543],
        strings[544],
        strings[545],
        strings[546],
        strings[547],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDistributionChamberElementTypeEnum_type = new enumeration_type(strings[548], 319, {
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
    IFC4X3_RC4_IfcDistributionPortTypeEnum_type = new enumeration_type(strings[557], 328, {
        strings[558],
        strings[559],
        strings[560],
        strings[561],
        strings[562],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDistributionSystemEnum_type = new enumeration_type(strings[563], 330, {
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
        strings[380],
        strings[583],
        strings[584],
        strings[371],
        strings[372],
        strings[585],
        strings[586],
        strings[587],
        strings[588],
        strings[589],
        strings[590],
        strings[591],
        strings[592],
        strings[593],
        strings[594],
        strings[595],
        strings[136],
        strings[596],
        strings[597],
        strings[598],
        strings[599],
        strings[600],
        strings[601],
        strings[602],
        strings[603],
        strings[604],
        strings[605],
        strings[606],
        strings[607],
        strings[608],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDocumentConfidentialityEnum_type = new enumeration_type(strings[609], 331, {
        strings[610],
        strings[611],
        strings[612],
        strings[613],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDocumentStatusEnum_type = new enumeration_type(strings[614], 336, {
        strings[615],
        strings[616],
        strings[617],
        strings[618],
        strings[9]
    });
    IFC4X3_RC4_IfcDoorPanelOperationEnum_type = new enumeration_type(strings[619], 339, {
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
    IFC4X3_RC4_IfcDoorPanelPositionEnum_type = new enumeration_type(strings[627], 340, {
        strings[628],
        strings[629],
        strings[630],
        strings[9]
    });
    IFC4X3_RC4_IfcDoorStyleConstructionEnum_type = new enumeration_type(strings[631], 344, {
        strings[632],
        strings[633],
        strings[634],
        strings[385],
        strings[635],
        strings[636],
        strings[384],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDoorStyleOperationEnum_type = new enumeration_type(strings[637], 345, {
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
        strings[624],
        strings[625],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDoorTypeEnum_type = new enumeration_type(strings[652], 347, {
        strings[653],
        strings[654],
        strings[655],
        strings[656],
        strings[657],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDoorTypeOperationEnum_type = new enumeration_type(strings[658], 348, {
        strings[638],
        strings[639],
        strings[659],
        strings[660],
        strings[661],
        strings[643],
        strings[644],
        strings[662],
        strings[646],
        strings[647],
        strings[663],
        strings[649],
        strings[650],
        strings[664],
        strings[665],
        strings[625],
        strings[666],
        strings[667],
        strings[668],
        strings[669],
        strings[670],
        strings[671],
        strings[672],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDoseEquivalentMeasure_type = new type_declaration(strings[673], 349, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcDuctFittingTypeEnum_type = new enumeration_type(strings[674], 354, {
        strings[250],
        strings[263],
        strings[264],
        strings[265],
        strings[266],
        strings[675],
        strings[267],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDuctSegmentTypeEnum_type = new enumeration_type(strings[676], 357, {
        strings[677],
        strings[678],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDuctSilencerTypeEnum_type = new enumeration_type(strings[679], 360, {
        strings[680],
        strings[681],
        strings[682],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcDuration_type = new type_declaration(strings[683], 361, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcDynamicViscosityMeasure_type = new type_declaration(strings[684], 362, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcEarthworksCutTypeEnum_type = new enumeration_type(strings[685], 364, {
        strings[555],
        strings[686],
        strings[687],
        strings[688],
        strings[689],
        strings[690],
        strings[691],
        strings[692],
        strings[693],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcEarthworksFillTypeEnum_type = new enumeration_type(strings[694], 367, {
        strings[695],
        strings[696],
        strings[697],
        strings[698],
        strings[699],
        strings[700],
        strings[701],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElectricApplianceTypeEnum_type = new enumeration_type(strings[702], 373, {
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
        strings[714],
        strings[715],
        strings[716],
        strings[717],
        strings[718],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElectricCapacitanceMeasure_type = new type_declaration(strings[719], 374, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcElectricChargeMeasure_type = new type_declaration(strings[720], 375, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcElectricConductanceMeasure_type = new type_declaration(strings[721], 376, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcElectricCurrentMeasure_type = new type_declaration(strings[722], 377, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcElectricDistributionBoardTypeEnum_type = new enumeration_type(strings[723], 380, {
        strings[543],
        strings[546],
        strings[544],
        strings[542],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type(strings[724], 383, {
        strings[725],
        strings[726],
        strings[727],
        strings[728],
        strings[729],
        strings[730],
        strings[731],
        strings[732],
        strings[733],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElectricFlowTreatmentDeviceTypeEnum_type = new enumeration_type(strings[734], 386, {
        strings[735],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElectricGeneratorTypeEnum_type = new enumeration_type(strings[736], 389, {
        strings[737],
        strings[738],
        strings[739],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElectricMotorTypeEnum_type = new enumeration_type(strings[740], 392, {
        strings[741],
        strings[742],
        strings[743],
        strings[744],
        strings[745],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElectricResistanceMeasure_type = new type_declaration(strings[746], 393, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcElectricTimeControlTypeEnum_type = new enumeration_type(strings[747], 396, {
        strings[748],
        strings[749],
        strings[750],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElectricVoltageMeasure_type = new type_declaration(strings[751], 397, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcElementAssemblyTypeEnum_type = new enumeration_type(strings[752], 402, {
        strings[753],
        strings[754],
        strings[755],
        strings[756],
        strings[222],
        strings[757],
        strings[758],
        strings[759],
        strings[224],
        strings[206],
        strings[210],
        strings[212],
        strings[760],
        strings[207],
        strings[761],
        strings[762],
        strings[763],
        strings[764],
        strings[765],
        strings[766],
        strings[767],
        strings[768],
        strings[769],
        strings[770],
        strings[771],
        strings[772],
        strings[773],
        strings[774],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcElementCompositionEnum_type = new enumeration_type(strings[775], 405, {
        strings[232],
        strings[233],
        strings[234]
    });
    IFC4X3_RC4_IfcEnergyMeasure_type = new type_declaration(strings[776], 412, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcEngineTypeEnum_type = new enumeration_type(strings[777], 415, {
        strings[778],
        strings[779],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcEvaporativeCoolerTypeEnum_type = new enumeration_type(strings[780], 418, {
        strings[781],
        strings[782],
        strings[783],
        strings[784],
        strings[785],
        strings[786],
        strings[787],
        strings[788],
        strings[789],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcEvaporatorTypeEnum_type = new enumeration_type(strings[790], 421, {
        strings[791],
        strings[792],
        strings[793],
        strings[794],
        strings[795],
        strings[796],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcEventTriggerTypeEnum_type = new enumeration_type(strings[797], 424, {
        strings[798],
        strings[799],
        strings[800],
        strings[801],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcEventTypeEnum_type = new enumeration_type(strings[802], 426, {
        strings[803],
        strings[804],
        strings[805],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcExternalSpatialElementTypeEnum_type = new enumeration_type(strings[806], 435, {
        strings[807],
        strings[808],
        strings[809],
        strings[810],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFacilityPartCommonTypeEnum_type = new enumeration_type(strings[811], 448, {
        strings[812],
        strings[813],
        strings[266],
        strings[814],
        strings[815],
        strings[213],
        strings[816],
        strings[214],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFacilityUsageEnum_type = new enumeration_type(strings[817], 450, {
        strings[818],
        strings[819],
        strings[820],
        strings[821],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFanTypeEnum_type = new enumeration_type(strings[822], 454, {
        strings[823],
        strings[824],
        strings[825],
        strings[826],
        strings[827],
        strings[828],
        strings[829],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFastenerTypeEnum_type = new enumeration_type(strings[830], 457, {
        strings[831],
        strings[832],
        strings[833],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFilterTypeEnum_type = new enumeration_type(strings[834], 467, {
        strings[835],
        strings[836],
        strings[837],
        strings[838],
        strings[839],
        strings[840],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type(strings[841], 470, {
        strings[842],
        strings[843],
        strings[844],
        strings[845],
        strings[846],
        strings[847],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFlowDirectionEnum_type = new enumeration_type(strings[848], 474, {
        strings[849],
        strings[850],
        strings[851],
        strings[9]
    });
    IFC4X3_RC4_IfcFlowInstrumentTypeEnum_type = new enumeration_type(strings[852], 479, {
        strings[853],
        strings[854],
        strings[855],
        strings[856],
        strings[857],
        strings[858],
        strings[859],
        strings[860],
        strings[861],
        strings[862],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFlowMeterTypeEnum_type = new enumeration_type(strings[863], 482, {
        strings[864],
        strings[865],
        strings[866],
        strings[867],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcFontStyle_type = new type_declaration(strings[868], 493, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcFontVariant_type = new type_declaration(strings[869], 494, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcFontWeight_type = new type_declaration(strings[870], 495, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcFootingTypeEnum_type = new enumeration_type(strings[871], 498, {
        strings[872],
        strings[873],
        strings[874],
        strings[875],
        strings[876],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcForceMeasure_type = new type_declaration(strings[877], 499, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcFrequencyMeasure_type = new type_declaration(strings[878], 500, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcFurnitureTypeEnum_type = new enumeration_type(strings[879], 505, {
        strings[880],
        strings[881],
        strings[882],
        strings[883],
        strings[884],
        strings[885],
        strings[886],
        strings[887],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcGeographicElementTypeEnum_type = new enumeration_type(strings[888], 508, {
        strings[889],
        strings[890],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcGeometricProjectionEnum_type = new enumeration_type(strings[891], 510, {
        strings[892],
        strings[893],
        strings[894],
        strings[895],
        strings[896],
        strings[897],
        strings[898],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcGlobalOrLocalEnum_type = new enumeration_type(strings[899], 522, {
        strings[900],
        strings[901]
    });
    IFC4X3_RC4_IfcGloballyUniqueId_type = new type_declaration(strings[902], 521, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcGridTypeEnum_type = new enumeration_type(strings[903], 528, {
        strings[681],
        strings[904],
        strings[905],
        strings[906],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcHeatExchangerTypeEnum_type = new enumeration_type(strings[907], 534, {
        strings[908],
        strings[909],
        strings[910],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcHeatFluxDensityMeasure_type = new type_declaration(strings[911], 535, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcHeatingValueMeasure_type = new type_declaration(strings[912], 536, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcHumidifierTypeEnum_type = new enumeration_type(strings[913], 539, {
        strings[914],
        strings[915],
        strings[916],
        strings[917],
        strings[918],
        strings[919],
        strings[920],
        strings[921],
        strings[922],
        strings[923],
        strings[924],
        strings[925],
        strings[926],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcIdentifier_type = new type_declaration(strings[927], 540, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcIlluminanceMeasure_type = new type_declaration(strings[928], 541, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcImpactProtectionDeviceTypeEnum_type = new enumeration_type(strings[929], 545, {
        strings[930],
        strings[931],
        strings[932],
        strings[933],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcInductanceMeasure_type = new type_declaration(strings[934], 553, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcInteger_type = new type_declaration(strings[935], 554, new simple_type(simple_type::integer_type));
    IFC4X3_RC4_IfcIntegerCountRateMeasure_type = new type_declaration(strings[936], 555, new simple_type(simple_type::integer_type));
    IFC4X3_RC4_IfcInterceptorTypeEnum_type = new enumeration_type(strings[937], 558, {
        strings[938],
        strings[939],
        strings[587],
        strings[940],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcInternalOrExternalEnum_type = new enumeration_type(strings[941], 560, {
        strings[942],
        strings[807],
        strings[808],
        strings[809],
        strings[810],
        strings[9]
    });
    IFC4X3_RC4_IfcInventoryTypeEnum_type = new enumeration_type(strings[943], 563, {
        strings[944],
        strings[945],
        strings[946],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcIonConcentrationMeasure_type = new type_declaration(strings[947], 564, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcIsothermalMoistureCapacityMeasure_type = new type_declaration(strings[948], 568, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcJunctionBoxTypeEnum_type = new enumeration_type(strings[949], 571, {
        strings[573],
        strings[950],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcKinematicViscosityMeasure_type = new type_declaration(strings[951], 574, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcKnotType_type = new enumeration_type(strings[952], 575, {
        strings[953],
        strings[954],
        strings[955],
        strings[146]
    });
    IFC4X3_RC4_IfcLabel_type = new type_declaration(strings[956], 576, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcLaborResourceTypeEnum_type = new enumeration_type(strings[957], 579, {
        strings[958],
        strings[959],
        strings[960],
        strings[378],
        strings[379],
        strings[961],
        strings[962],
        strings[427],
        strings[963],
        strings[964],
        strings[965],
        strings[382],
        strings[966],
        strings[373],
        strings[967],
        strings[429],
        strings[968],
        strings[969],
        strings[970],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcLampTypeEnum_type = new enumeration_type(strings[971], 583, {
        strings[972],
        strings[973],
        strings[974],
        strings[975],
        strings[976],
        strings[977],
        strings[978],
        strings[979],
        strings[980],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcLanguageId_type = new type_declaration(strings[981], 584, new named_type(IFC4X3_RC4_IfcIdentifier_type));
    IFC4X3_RC4_IfcLayerSetDirectionEnum_type = new enumeration_type(strings[982], 586, {
        strings[983],
        strings[984],
        strings[985]
    });
    IFC4X3_RC4_IfcLengthMeasure_type = new type_declaration(strings[986], 587, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcLightDistributionCurveEnum_type = new enumeration_type(strings[987], 591, {
        strings[988],
        strings[989],
        strings[990],
        strings[9]
    });
    IFC4X3_RC4_IfcLightEmissionSourceEnum_type = new enumeration_type(strings[991], 594, {
        strings[972],
        strings[973],
        strings[975],
        strings[976],
        strings[992],
        strings[993],
        strings[994],
        strings[995],
        strings[978],
        strings[980],
        strings[9]
    });
    IFC4X3_RC4_IfcLightFixtureTypeEnum_type = new enumeration_type(strings[996], 597, {
        strings[997],
        strings[998],
        strings[999],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcLinearForceMeasure_type = new type_declaration(strings[1000], 607, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcLinearMomentMeasure_type = new type_declaration(strings[1001], 608, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcLinearStiffnessMeasure_type = new type_declaration(strings[1002], 611, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcLinearVelocityMeasure_type = new type_declaration(strings[1003], 612, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcLiquidTerminalTypeEnum_type = new enumeration_type(strings[1004], 616, {
        strings[1005],
        strings[844],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcLoadGroupTypeEnum_type = new enumeration_type(strings[1006], 617, {
        strings[1007],
        strings[1008],
        strings[1009],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcLogical_type = new type_declaration(strings[1010], 619, new simple_type(simple_type::logical_type));
    IFC4X3_RC4_IfcLogicalOperatorEnum_type = new enumeration_type(strings[1011], 620, {
        strings[1012],
        strings[1013],
        strings[1014],
        strings[1015],
        strings[1016]
    });
    IFC4X3_RC4_IfcLuminousFluxMeasure_type = new type_declaration(strings[1017], 623, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcLuminousIntensityDistributionMeasure_type = new type_declaration(strings[1018], 624, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcLuminousIntensityMeasure_type = new type_declaration(strings[1019], 625, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMagneticFluxDensityMeasure_type = new type_declaration(strings[1020], 626, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMagneticFluxMeasure_type = new type_declaration(strings[1021], 627, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMarineFacilityTypeEnum_type = new enumeration_type(strings[1022], 632, {
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
        strings[1033],
        strings[1034],
        strings[1035],
        strings[1036],
        strings[1037],
        strings[1038],
        strings[1039],
        strings[1040],
        strings[1041],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcMarinePartTypeEnum_type = new enumeration_type(strings[1042], 633, {
        strings[1043],
        strings[1044],
        strings[1045],
        strings[422],
        strings[1046],
        strings[1047],
        strings[1048],
        strings[1049],
        strings[1050],
        strings[1051],
        strings[1052],
        strings[1053],
        strings[1054],
        strings[1055],
        strings[1056],
        strings[1057],
        strings[1058],
        strings[1059],
        strings[424],
        strings[1060],
        strings[1061],
        strings[1062],
        strings[1063],
        strings[1064],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcMassDensityMeasure_type = new type_declaration(strings[1065], 634, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMassFlowRateMeasure_type = new type_declaration(strings[1066], 635, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMassMeasure_type = new type_declaration(strings[1067], 636, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMassPerLengthMeasure_type = new type_declaration(strings[1068], 637, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMechanicalFastenerTypeEnum_type = new enumeration_type(strings[1069], 662, {
        strings[1070],
        strings[1071],
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
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcMedicalDeviceTypeEnum_type = new enumeration_type(strings[1085], 665, {
        strings[1086],
        strings[1087],
        strings[1088],
        strings[1089],
        strings[1090],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcMemberTypeEnum_type = new enumeration_type(strings[1091], 669, {
        strings[1092],
        strings[1093],
        strings[1094],
        strings[1095],
        strings[1096],
        strings[908],
        strings[6],
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
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcMobileTelecommunicationsApplianceTypeEnum_type = new enumeration_type(strings[1109], 675, {
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
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcModulusOfElasticityMeasure_type = new type_declaration(strings[1123], 676, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration(strings[1124], 677, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration(strings[1125], 678, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionSelect_type = new select_type(strings[1126], 679, {
        IFC4X3_RC4_IfcBoolean_type,
        IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionMeasure_type
    });
    IFC4X3_RC4_IfcModulusOfSubgradeReactionMeasure_type = new type_declaration(strings[1127], 680, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcModulusOfSubgradeReactionSelect_type = new select_type(strings[1128], 681, {
        IFC4X3_RC4_IfcBoolean_type,
        IFC4X3_RC4_IfcModulusOfSubgradeReactionMeasure_type
    });
    IFC4X3_RC4_IfcModulusOfTranslationalSubgradeReactionSelect_type = new select_type(strings[1129], 682, {
        IFC4X3_RC4_IfcBoolean_type,
        IFC4X3_RC4_IfcModulusOfLinearSubgradeReactionMeasure_type
    });
    IFC4X3_RC4_IfcMoistureDiffusivityMeasure_type = new type_declaration(strings[1130], 683, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMolecularWeightMeasure_type = new type_declaration(strings[1131], 684, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMomentOfInertiaMeasure_type = new type_declaration(strings[1132], 685, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMonetaryMeasure_type = new type_declaration(strings[1133], 686, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcMonthInYearNumber_type = new type_declaration(strings[1134], 688, new simple_type(simple_type::integer_type));
    IFC4X3_RC4_IfcMooringDeviceTypeEnum_type = new enumeration_type(strings[1135], 691, {
        strings[1136],
        strings[1137],
        strings[1138],
        strings[1139],
        strings[1140],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcMotorConnectionTypeEnum_type = new enumeration_type(strings[1141], 694, {
        strings[1142],
        strings[1143],
        strings[1144],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcNavigationElementTypeEnum_type = new enumeration_type(strings[1145], 698, {
        strings[1146],
        strings[1147],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcNonNegativeLengthMeasure_type = new type_declaration(strings[1148], 699, new named_type(IFC4X3_RC4_IfcLengthMeasure_type));
    IFC4X3_RC4_IfcNumericMeasure_type = new type_declaration(strings[1149], 701, new simple_type(simple_type::number_type));
    IFC4X3_RC4_IfcObjectTypeEnum_type = new enumeration_type(strings[1150], 708, {
        strings[1151],
        strings[1152],
        strings[571],
        strings[1153],
        strings[1154],
        strings[1155],
        strings[1156],
        strings[9]
    });
    IFC4X3_RC4_IfcObjectiveEnum_type = new enumeration_type(strings[1157], 705, {
        strings[1158],
        strings[1159],
        strings[1160],
        strings[807],
        strings[1161],
        strings[1162],
        strings[1163],
        strings[1164],
        strings[1165],
        strings[1166],
        strings[1167],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcOccupantTypeEnum_type = new enumeration_type(strings[1168], 710, {
        strings[1169],
        strings[1170],
        strings[1171],
        strings[1172],
        strings[1173],
        strings[1174],
        strings[1175],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcOpeningElementTypeEnum_type = new enumeration_type(strings[1176], 717, {
        strings[1177],
        strings[1178],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcOutletTypeEnum_type = new enumeration_type(strings[1179], 726, {
        strings[1180],
        strings[1181],
        strings[1182],
        strings[1183],
        strings[1184],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPHMeasure_type = new type_declaration(strings[1185], 743, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcParameterValue_type = new type_declaration(strings[1186], 729, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcPavementTypeEnum_type = new enumeration_type(strings[1187], 733, {
        strings[1188],
        strings[1189],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPerformanceHistoryTypeEnum_type = new enumeration_type(strings[1190], 736, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPermeableCoveringOperationEnum_type = new enumeration_type(strings[1191], 737, {
        strings[1192],
        strings[1193],
        strings[1194],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPermitTypeEnum_type = new enumeration_type(strings[1195], 740, {
        strings[1196],
        strings[1197],
        strings[1198],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPhysicalOrVirtualEnum_type = new enumeration_type(strings[1199], 745, {
        strings[1200],
        strings[1201],
        strings[9]
    });
    IFC4X3_RC4_IfcPileConstructionEnum_type = new enumeration_type(strings[1202], 749, {
        strings[1203],
        strings[1204],
        strings[1205],
        strings[1206],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPileTypeEnum_type = new enumeration_type(strings[1207], 751, {
        strings[1208],
        strings[1209],
        strings[1210],
        strings[1211],
        strings[1212],
        strings[1213],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPipeFittingTypeEnum_type = new enumeration_type(strings[1214], 754, {
        strings[250],
        strings[263],
        strings[264],
        strings[265],
        strings[266],
        strings[675],
        strings[267],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPipeSegmentTypeEnum_type = new enumeration_type(strings[1215], 757, {
        strings[220],
        strings[678],
        strings[677],
        strings[1216],
        strings[1217],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPlanarForceMeasure_type = new type_declaration(strings[1218], 762, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcPlaneAngleMeasure_type = new type_declaration(strings[1219], 764, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcPlateTypeEnum_type = new enumeration_type(strings[1220], 769, {
        strings[1221],
        strings[1222],
        strings[1223],
        strings[1224],
        strings[1225],
        strings[1226],
        strings[1227],
        strings[1228],
        strings[1229],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPositiveInteger_type = new type_declaration(strings[1230], 782, new named_type(IFC4X3_RC4_IfcInteger_type));
    IFC4X3_RC4_IfcPositiveLengthMeasure_type = new type_declaration(strings[1231], 783, new named_type(IFC4X3_RC4_IfcLengthMeasure_type));
    IFC4X3_RC4_IfcPositivePlaneAngleMeasure_type = new type_declaration(strings[1232], 784, new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type));
    IFC4X3_RC4_IfcPowerMeasure_type = new type_declaration(strings[1233], 787, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcPreferredSurfaceCurveRepresentation_type = new enumeration_type(strings[1234], 794, {
        strings[1235],
        strings[1236],
        strings[1237]
    });
    IFC4X3_RC4_IfcPresentableText_type = new type_declaration(strings[1238], 795, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcPressureMeasure_type = new type_declaration(strings[1239], 800, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcProcedureTypeEnum_type = new enumeration_type(strings[1240], 803, {
        strings[1241],
        strings[1242],
        strings[1243],
        strings[1244],
        strings[1245],
        strings[1246],
        strings[1247],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcProfileTypeEnum_type = new enumeration_type(strings[1248], 813, {
        strings[1249],
        strings[1250]
    });
    IFC4X3_RC4_IfcProjectOrderTypeEnum_type = new enumeration_type(strings[1251], 821, {
        strings[1252],
        strings[1253],
        strings[1254],
        strings[1255],
        strings[1256],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcProjectedOrTrueLengthEnum_type = new enumeration_type(strings[1257], 816, {
        strings[1258],
        strings[1259]
    });
    IFC4X3_RC4_IfcProjectionElementTypeEnum_type = new enumeration_type(strings[1260], 818, {
        strings[1261],
        strings[1262],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPropertySetTemplateTypeEnum_type = new enumeration_type(strings[1263], 836, {
        strings[1264],
        strings[1265],
        strings[1266],
        strings[1267],
        strings[1268],
        strings[1269],
        strings[1270],
        strings[9]
    });
    IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type = new enumeration_type(strings[1271], 844, {
        strings[1272],
        strings[1273],
        strings[1274],
        strings[1275],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcProtectiveDeviceTypeEnum_type = new enumeration_type(strings[1276], 846, {
        strings[1277],
        strings[1278],
        strings[1279],
        strings[1280],
        strings[1281],
        strings[1282],
        strings[1283],
        strings[1284],
        strings[1285],
        strings[1286],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcPumpTypeEnum_type = new enumeration_type(strings[1287], 850, {
        strings[1288],
        strings[1289],
        strings[1290],
        strings[1291],
        strings[1292],
        strings[1293],
        strings[1294],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRadioActivityMeasure_type = new type_declaration(strings[1295], 858, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcRailTypeEnum_type = new enumeration_type(strings[1296], 864, {
        strings[1297],
        strings[1298],
        strings[1299],
        strings[1300],
        strings[1301],
        strings[1302],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRailingTypeEnum_type = new enumeration_type(strings[1303], 862, {
        strings[1304],
        strings[1299],
        strings[1305],
        strings[1306],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRailwayPartTypeEnum_type = new enumeration_type(strings[1307], 866, {
        strings[1308],
        strings[1309],
        strings[1310],
        strings[1311],
        strings[1312],
        strings[1313],
        strings[214],
        strings[1314],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRailwayTypeEnum_type = new enumeration_type(strings[1315], 867, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRampFlightTypeEnum_type = new enumeration_type(strings[1316], 871, {
        strings[1317],
        strings[1318],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRampTypeEnum_type = new enumeration_type(strings[1319], 873, {
        strings[1320],
        strings[1321],
        strings[1322],
        strings[1323],
        strings[1324],
        strings[1325],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRatioMeasure_type = new type_declaration(strings[1326], 874, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcReal_type = new type_declaration(strings[1327], 877, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcRecurrenceTypeEnum_type = new enumeration_type(strings[1328], 883, {
        strings[1329],
        strings[1330],
        strings[1331],
        strings[1332],
        strings[1333],
        strings[1334],
        strings[1335],
        strings[1336]
    });
    IFC4X3_RC4_IfcReferentTypeEnum_type = new enumeration_type(strings[1337], 886, {
        strings[1338],
        strings[1339],
        strings[1340],
        strings[1341],
        strings[1342],
        strings[1343],
        strings[203],
        strings[1344],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcReflectanceMethodEnum_type = new enumeration_type(strings[1345], 887, {
        strings[1346],
        strings[1347],
        strings[1348],
        strings[1349],
        strings[383],
        strings[1350],
        strings[1351],
        strings[384],
        strings[1352],
        strings[9]
    });
    IFC4X3_RC4_IfcReinforcedSoilTypeEnum_type = new enumeration_type(strings[1353], 890, {
        strings[1354],
        strings[1355],
        strings[1356],
        strings[1357],
        strings[1358],
        strings[1359],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcReinforcingBarRoleEnum_type = new enumeration_type(strings[1360], 894, {
        strings[1361],
        strings[1362],
        strings[1363],
        strings[1101],
        strings[1364],
        strings[1365],
        strings[1366],
        strings[1367],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcReinforcingBarSurfaceEnum_type = new enumeration_type(strings[1368], 895, {
        strings[1369],
        strings[1370]
    });
    IFC4X3_RC4_IfcReinforcingBarTypeEnum_type = new enumeration_type(strings[1371], 897, {
        strings[1367],
        strings[1365],
        strings[1363],
        strings[1361],
        strings[1364],
        strings[1366],
        strings[1362],
        strings[1101],
        strings[1372],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcReinforcingMeshTypeEnum_type = new enumeration_type(strings[1373], 902, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRoadPartTypeEnum_type = new enumeration_type(strings[1374], 971, {
        strings[1375],
        strings[1376],
        strings[1377],
        strings[203],
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
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRoadTypeEnum_type = new enumeration_type(strings[1398], 972, {
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcRoleEnum_type = new enumeration_type(strings[1399], 973, {
        strings[1400],
        strings[1401],
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
        strings[1174],
        strings[1417],
        strings[1418],
        strings[1419],
        strings[1420],
        strings[8]
    });
    IFC4X3_RC4_IfcRoofTypeEnum_type = new enumeration_type(strings[1421], 976, {
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
    IFC4X3_RC4_IfcRotationalFrequencyMeasure_type = new type_declaration(strings[1435], 978, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcRotationalMassMeasure_type = new type_declaration(strings[1436], 979, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcRotationalStiffnessMeasure_type = new type_declaration(strings[1437], 980, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcRotationalStiffnessSelect_type = new select_type(strings[1438], 981, {
        IFC4X3_RC4_IfcBoolean_type,
        IFC4X3_RC4_IfcRotationalStiffnessMeasure_type
    });
    IFC4X3_RC4_IfcSIPrefix_type = new enumeration_type(strings[1439], 1026, {
        strings[1440],
        strings[1441],
        strings[1442],
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
        strings[1455]
    });
    IFC4X3_RC4_IfcSIUnitName_type = new enumeration_type(strings[1456], 1029, {
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
        strings[1472],
        strings[1473],
        strings[1474],
        strings[1475],
        strings[1476],
        strings[1477],
        strings[1478],
        strings[1479],
        strings[1480],
        strings[1481],
        strings[1482],
        strings[1483],
        strings[1484],
        strings[1485],
        strings[1486]
    });
    IFC4X3_RC4_IfcSanitaryTerminalTypeEnum_type = new enumeration_type(strings[1487], 985, {
        strings[1488],
        strings[1489],
        strings[1490],
        strings[1491],
        strings[850],
        strings[1492],
        strings[1493],
        strings[1494],
        strings[1495],
        strings[1496],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSectionModulusMeasure_type = new type_declaration(strings[1497], 994, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSectionTypeEnum_type = new enumeration_type(strings[1498], 997, {
        strings[1499],
        strings[1500]
    });
    IFC4X3_RC4_IfcSectionalAreaIntegralMeasure_type = new type_declaration(strings[1501], 989, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSensorTypeEnum_type = new enumeration_type(strings[1502], 1003, {
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
        strings[1521],
        strings[1522],
        strings[1523],
        strings[1524],
        strings[1525],
        strings[1526],
        strings[1527],
        strings[1528],
        strings[1529],
        strings[1530],
        strings[1531],
        strings[1532],
        strings[1533],
        strings[1534],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSequenceEnum_type = new enumeration_type(strings[1535], 1004, {
        strings[1536],
        strings[1537],
        strings[1538],
        strings[1539],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcShadingDeviceTypeEnum_type = new enumeration_type(strings[1540], 1008, {
        strings[1541],
        strings[1542],
        strings[1543],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcShearModulusMeasure_type = new type_declaration(strings[1544], 1012, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSignTypeEnum_type = new enumeration_type(strings[1545], 1020, {
        strings[1546],
        strings[1547],
        strings[1350],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSignalTypeEnum_type = new enumeration_type(strings[1548], 1018, {
        strings[1549],
        strings[1550],
        strings[1551],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSimplePropertyTemplateTypeEnum_type = new enumeration_type(strings[1552], 1023, {
        strings[1553],
        strings[1554],
        strings[1555],
        strings[1556],
        strings[1557],
        strings[1558],
        strings[1559],
        strings[1560],
        strings[1561],
        strings[1562],
        strings[1563],
        strings[1564]
    });
    IFC4X3_RC4_IfcSlabTypeEnum_type = new enumeration_type(strings[1565], 1035, {
        strings[1566],
        strings[1567],
        strings[1568],
        strings[1569],
        strings[1570],
        strings[373],
        strings[1571],
        strings[1384],
        strings[1572],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSolarDeviceTypeEnum_type = new enumeration_type(strings[1573], 1039, {
        strings[1574],
        strings[1575],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSolidAngleMeasure_type = new type_declaration(strings[1576], 1040, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSoundPowerLevelMeasure_type = new type_declaration(strings[1577], 1044, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSoundPowerMeasure_type = new type_declaration(strings[1578], 1045, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSoundPressureLevelMeasure_type = new type_declaration(strings[1579], 1046, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSoundPressureMeasure_type = new type_declaration(strings[1580], 1047, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSpaceHeaterTypeEnum_type = new enumeration_type(strings[1581], 1052, {
        strings[1582],
        strings[1583],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSpaceTypeEnum_type = new enumeration_type(strings[1584], 1054, {
        strings[1585],
        strings[1586],
        strings[1587],
        strings[942],
        strings[807],
        strings[1588],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSpatialZoneTypeEnum_type = new enumeration_type(strings[1589], 1062, {
        strings[1590],
        strings[1591],
        strings[372],
        strings[1592],
        strings[592],
        strings[1275],
        strings[23],
        strings[599],
        strings[1593],
        strings[1594],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSpecificHeatCapacityMeasure_type = new type_declaration(strings[1595], 1063, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSpecularExponent_type = new type_declaration(strings[1596], 1064, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcSpecularRoughness_type = new type_declaration(strings[1597], 1066, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcStackTerminalTypeEnum_type = new enumeration_type(strings[1598], 1072, {
        strings[1599],
        strings[1600],
        strings[1601],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcStairFlightTypeEnum_type = new enumeration_type(strings[1602], 1076, {
        strings[1317],
        strings[1603],
        strings[1318],
        strings[1604],
        strings[1434],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcStairTypeEnum_type = new enumeration_type(strings[1605], 1078, {
        strings[1606],
        strings[1607],
        strings[1608],
        strings[1609],
        strings[1610],
        strings[1611],
        strings[1612],
        strings[1613],
        strings[1614],
        strings[1615],
        strings[1616],
        strings[1617],
        strings[1618],
        strings[1619],
        strings[1620],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcStateEnum_type = new enumeration_type(strings[1621], 1079, {
        strings[1622],
        strings[1623],
        strings[1624],
        strings[1625],
        strings[1626]
    });
    IFC4X3_RC4_IfcStructuralCurveActivityTypeEnum_type = new enumeration_type(strings[1627], 1087, {
        strings[1628],
        strings[440],
        strings[1629],
        strings[1630],
        strings[1631],
        strings[1632],
        strings[1633],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcStructuralCurveMemberTypeEnum_type = new enumeration_type(strings[1634], 1090, {
        strings[1635],
        strings[1636],
        strings[558],
        strings[1637],
        strings[1638],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcStructuralSurfaceActivityTypeEnum_type = new enumeration_type(strings[1639], 1116, {
        strings[1628],
        strings[1640],
        strings[1633],
        strings[1641],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcStructuralSurfaceMemberTypeEnum_type = new enumeration_type(strings[1642], 1119, {
        strings[1643],
        strings[1644],
        strings[1645],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSubContractResourceTypeEnum_type = new enumeration_type(strings[1646], 1127, {
        strings[1647],
        strings[1198],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSurfaceFeatureTypeEnum_type = new enumeration_type(strings[1648], 1133, {
        strings[1649],
        strings[1650],
        strings[1651],
        strings[1652],
        strings[1653],
        strings[1654],
        strings[1655],
        strings[1656],
        strings[1657],
        strings[1658],
        strings[1659],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSurfaceSide_type = new enumeration_type(strings[1660], 1138, {
        strings[519],
        strings[520],
        strings[1661]
    });
    IFC4X3_RC4_IfcSwitchingDeviceTypeEnum_type = new enumeration_type(strings[1662], 1153, {
        strings[1663],
        strings[1664],
        strings[1665],
        strings[1666],
        strings[1667],
        strings[1668],
        strings[1669],
        strings[1670],
        strings[1671],
        strings[750],
        strings[1672],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcSystemFurnitureElementTypeEnum_type = new enumeration_type(strings[1673], 1157, {
        strings[1674],
        strings[1675],
        strings[1676],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTankTypeEnum_type = new enumeration_type(strings[1677], 1163, {
        strings[1678],
        strings[1679],
        strings[1680],
        strings[1681],
        strings[1682],
        strings[1683],
        strings[1684],
        strings[1685],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTaskDurationEnum_type = new enumeration_type(strings[1686], 1165, {
        strings[1687],
        strings[1688],
        strings[9]
    });
    IFC4X3_RC4_IfcTaskTypeEnum_type = new enumeration_type(strings[1689], 1169, {
        strings[1690],
        strings[1590],
        strings[1691],
        strings[1692],
        strings[574],
        strings[1693],
        strings[1694],
        strings[1695],
        strings[1696],
        strings[1697],
        strings[1698],
        strings[1699],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTemperatureGradientMeasure_type = new type_declaration(strings[1700], 1171, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcTemperatureRateOfChangeMeasure_type = new type_declaration(strings[1701], 1172, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcTendonAnchorTypeEnum_type = new enumeration_type(strings[1702], 1176, {
        strings[1080],
        strings[1703],
        strings[1704],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTendonConduitTypeEnum_type = new enumeration_type(strings[1705], 1179, {
        strings[560],
        strings[1080],
        strings[1706],
        strings[1707],
        strings[1708],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTendonTypeEnum_type = new enumeration_type(strings[1709], 1181, {
        strings[1710],
        strings[1711],
        strings[1712],
        strings[1713],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcText_type = new type_declaration(strings[1714], 1184, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcTextAlignment_type = new type_declaration(strings[1715], 1185, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcTextDecoration_type = new type_declaration(strings[1716], 1186, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcTextFontName_type = new type_declaration(strings[1717], 1187, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcTextPath_type = new enumeration_type(strings[1718], 1191, {
        strings[628],
        strings[630],
        strings[1719],
        strings[1720]
    });
    IFC4X3_RC4_IfcTextTransformation_type = new type_declaration(strings[1721], 1196, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcThermalAdmittanceMeasure_type = new type_declaration(strings[1722], 1202, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcThermalConductivityMeasure_type = new type_declaration(strings[1723], 1203, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcThermalExpansionCoefficientMeasure_type = new type_declaration(strings[1724], 1204, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcThermalResistanceMeasure_type = new type_declaration(strings[1725], 1205, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcThermalTransmittanceMeasure_type = new type_declaration(strings[1726], 1206, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcThermodynamicTemperatureMeasure_type = new type_declaration(strings[1727], 1207, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcTime_type = new type_declaration(strings[1728], 1209, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcTimeMeasure_type = new type_declaration(strings[1729], 1210, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcTimeOrRatioSelect_type = new select_type(strings[1730], 1211, {
        IFC4X3_RC4_IfcDuration_type,
        IFC4X3_RC4_IfcRatioMeasure_type
    });
    IFC4X3_RC4_IfcTimeSeriesDataTypeEnum_type = new enumeration_type(strings[1731], 1214, {
        strings[1732],
        strings[1633],
        strings[1733],
        strings[1734],
        strings[1735],
        strings[1736],
        strings[9]
    });
    IFC4X3_RC4_IfcTimeStamp_type = new type_declaration(strings[1737], 1216, new simple_type(simple_type::integer_type));
    IFC4X3_RC4_IfcTorqueMeasure_type = new type_declaration(strings[1738], 1220, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcTrackElementTypeEnum_type = new enumeration_type(strings[1739], 1223, {
        strings[1740],
        strings[1741],
        strings[1742],
        strings[1743],
        strings[1744],
        strings[1745],
        strings[1746],
        strings[1747],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTransformerTypeEnum_type = new enumeration_type(strings[1748], 1226, {
        strings[32],
        strings[1749],
        strings[1750],
        strings[1751],
        strings[1752],
        strings[1753],
        strings[861],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTransitionCode_type = new enumeration_type(strings[1754], 1227, {
        strings[1755],
        strings[1732],
        strings[1756],
        strings[1757]
    });
    IFC4X3_RC4_IfcTranslationalStiffnessSelect_type = new select_type(strings[1758], 1228, {
        IFC4X3_RC4_IfcBoolean_type,
        IFC4X3_RC4_IfcLinearStiffnessMeasure_type
    });
    IFC4X3_RC4_IfcTransportElementFixedTypeEnum_type = new enumeration_type(strings[1759], 1230, {
        strings[1760],
        strings[1761],
        strings[1762],
        strings[1763],
        strings[1764],
        strings[1765],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTransportElementNonFixedTypeEnum_type = new enumeration_type(strings[1766], 1231, {
        strings[1767],
        strings[1768],
        strings[1769],
        strings[1770],
        strings[1771],
        strings[1772],
        strings[1773],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcTransportElementTypeSelect_type = new select_type(strings[1774], 1233, {
        IFC4X3_RC4_IfcTransportElementFixedTypeEnum_type,
        IFC4X3_RC4_IfcTransportElementNonFixedTypeEnum_type
    });
    IFC4X3_RC4_IfcTrimmingPreference_type = new enumeration_type(strings[1775], 1238, {
        strings[1776],
        strings[1164],
        strings[146]
    });
    IFC4X3_RC4_IfcTubeBundleTypeEnum_type = new enumeration_type(strings[1777], 1243, {
        strings[1778],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcURIReference_type = new type_declaration(strings[1779], 1257, new simple_type(simple_type::string_type));
    IFC4X3_RC4_IfcUnitEnum_type = new enumeration_type(strings[1780], 1256, {
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
        strings[1795],
        strings[1796],
        strings[1797],
        strings[1798],
        strings[1799],
        strings[1800],
        strings[1801],
        strings[1802],
        strings[1803],
        strings[1804],
        strings[1805],
        strings[1806],
        strings[1807],
        strings[1808],
        strings[1809],
        strings[8]
    });
    IFC4X3_RC4_IfcUnitaryControlElementTypeEnum_type = new enumeration_type(strings[1810], 1251, {
        strings[1811],
        strings[1812],
        strings[1813],
        strings[1814],
        strings[1815],
        strings[1816],
        strings[1817],
        strings[1818],
        strings[861],
        strings[1819],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcUnitaryEquipmentTypeEnum_type = new enumeration_type(strings[1820], 1254, {
        strings[1821],
        strings[1822],
        strings[1823],
        strings[1824],
        strings[1825],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcValveTypeEnum_type = new enumeration_type(strings[1826], 1262, {
        strings[1827],
        strings[1828],
        strings[1829],
        strings[1830],
        strings[1831],
        strings[1832],
        strings[1833],
        strings[1834],
        strings[1835],
        strings[1836],
        strings[1837],
        strings[1838],
        strings[1839],
        strings[1840],
        strings[1841],
        strings[1842],
        strings[1843],
        strings[1844],
        strings[1845],
        strings[1846],
        strings[1847],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcVaporPermeabilityMeasure_type = new type_declaration(strings[1848], 1263, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcVibrationDamperTypeEnum_type = new enumeration_type(strings[1849], 1271, {
        strings[1850],
        strings[1851],
        strings[1852],
        strings[1212],
        strings[1853],
        strings[1854],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcVibrationIsolatorTypeEnum_type = new enumeration_type(strings[1855], 1274, {
        strings[1856],
        strings[1857],
        strings[1858],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcVoidingFeatureTypeEnum_type = new enumeration_type(strings[1859], 1278, {
        strings[1860],
        strings[1861],
        strings[1862],
        strings[1863],
        strings[1864],
        strings[1365],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcVolumeMeasure_type = new type_declaration(strings[1865], 1280, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcVolumetricFlowRateMeasure_type = new type_declaration(strings[1866], 1281, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcWallTypeEnum_type = new enumeration_type(strings[1867], 1286, {
        strings[1868],
        strings[1869],
        strings[1870],
        strings[1871],
        strings[1362],
        strings[1872],
        strings[1873],
        strings[1629],
        strings[1874],
        strings[1875],
        strings[1876],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcWarpingConstantMeasure_type = new type_declaration(strings[1877], 1287, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcWarpingMomentMeasure_type = new type_declaration(strings[1878], 1288, new simple_type(simple_type::real_type));
    IFC4X3_RC4_IfcWarpingStiffnessSelect_type = new select_type(strings[1879], 1289, {
        IFC4X3_RC4_IfcBoolean_type,
        IFC4X3_RC4_IfcWarpingMomentMeasure_type
    });
    IFC4X3_RC4_IfcWasteTerminalTypeEnum_type = new enumeration_type(strings[1880], 1292, {
        strings[1881],
        strings[1882],
        strings[1883],
        strings[1884],
        strings[1885],
        strings[1886],
        strings[1887],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcWindowPanelOperationEnum_type = new enumeration_type(strings[1888], 1296, {
        strings[1889],
        strings[1890],
        strings[1891],
        strings[1892],
        strings[1893],
        strings[1894],
        strings[1895],
        strings[1896],
        strings[1897],
        strings[1898],
        strings[1899],
        strings[1900],
        strings[1901],
        strings[9]
    });
    IFC4X3_RC4_IfcWindowPanelPositionEnum_type = new enumeration_type(strings[1902], 1297, {
        strings[628],
        strings[629],
        strings[630],
        strings[1903],
        strings[1904],
        strings[9]
    });
    IFC4X3_RC4_IfcWindowStyleConstructionEnum_type = new enumeration_type(strings[1905], 1301, {
        strings[632],
        strings[633],
        strings[634],
        strings[385],
        strings[635],
        strings[384],
        strings[1906],
        strings[9]
    });
    IFC4X3_RC4_IfcWindowStyleOperationEnum_type = new enumeration_type(strings[1907], 1302, {
        strings[1908],
        strings[1909],
        strings[1910],
        strings[1911],
        strings[1912],
        strings[1913],
        strings[1914],
        strings[1915],
        strings[1916],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcWindowTypeEnum_type = new enumeration_type(strings[1917], 1304, {
        strings[1918],
        strings[1919],
        strings[1920],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcWindowTypePartitioningEnum_type = new enumeration_type(strings[1921], 1305, {
        strings[1908],
        strings[1909],
        strings[1910],
        strings[1911],
        strings[1912],
        strings[1913],
        strings[1914],
        strings[1915],
        strings[1916],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcWorkCalendarTypeEnum_type = new enumeration_type(strings[1922], 1307, {
        strings[1923],
        strings[1924],
        strings[1925],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcWorkPlanTypeEnum_type = new enumeration_type(strings[1926], 1310, {
        strings[1927],
        strings[1928],
        strings[1929],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcWorkScheduleTypeEnum_type = new enumeration_type(strings[1930], 1312, {
        strings[1927],
        strings[1928],
        strings[1929],
        strings[8],
        strings[9]
    });
    IFC4X3_RC4_IfcActorRole_type = new entity(strings[1931], false, 7, 0);
    IFC4X3_RC4_IfcAddress_type = new entity(strings[1932], true, 12, 0);
    IFC4X3_RC4_IfcAlignmentParameterSegment_type = new entity(strings[1933], true, 36, 0);
    IFC4X3_RC4_IfcAlignmentVerticalSegment_type = new entity(strings[1934], false, 40, IFC4X3_RC4_IfcAlignmentParameterSegment_type);
    IFC4X3_RC4_IfcApplication_type = new entity(strings[1935], false, 49, 0);
    IFC4X3_RC4_IfcAppliedValue_type = new entity(strings[1936], false, 50, 0);
    IFC4X3_RC4_IfcApproval_type = new entity(strings[1937], false, 52, 0);
    IFC4X3_RC4_IfcBoundaryCondition_type = new entity(strings[1938], true, 94, 0);
    IFC4X3_RC4_IfcBoundaryEdgeCondition_type = new entity(strings[1939], false, 96, IFC4X3_RC4_IfcBoundaryCondition_type);
    IFC4X3_RC4_IfcBoundaryFaceCondition_type = new entity(strings[1940], false, 97, IFC4X3_RC4_IfcBoundaryCondition_type);
    IFC4X3_RC4_IfcBoundaryNodeCondition_type = new entity(strings[1941], false, 98, IFC4X3_RC4_IfcBoundaryCondition_type);
    IFC4X3_RC4_IfcBoundaryNodeConditionWarping_type = new entity(strings[1942], false, 99, IFC4X3_RC4_IfcBoundaryNodeCondition_type);
    IFC4X3_RC4_IfcConnectionGeometry_type = new entity(strings[1943], true, 208, 0);
    IFC4X3_RC4_IfcConnectionPointGeometry_type = new entity(strings[1944], false, 210, IFC4X3_RC4_IfcConnectionGeometry_type);
    IFC4X3_RC4_IfcConnectionSurfaceGeometry_type = new entity(strings[1945], false, 211, IFC4X3_RC4_IfcConnectionGeometry_type);
    IFC4X3_RC4_IfcConnectionVolumeGeometry_type = new entity(strings[1946], false, 213, IFC4X3_RC4_IfcConnectionGeometry_type);
    IFC4X3_RC4_IfcConstraint_type = new entity(strings[1947], true, 214, 0);
    IFC4X3_RC4_IfcCoordinateOperation_type = new entity(strings[1948], true, 245, 0);
    IFC4X3_RC4_IfcCoordinateReferenceSystem_type = new entity(strings[1949], true, 246, 0);
    IFC4X3_RC4_IfcCostValue_type = new entity(strings[1950], false, 253, IFC4X3_RC4_IfcAppliedValue_type);
    IFC4X3_RC4_IfcDerivedUnit_type = new entity(strings[1951], false, 301, 0);
    IFC4X3_RC4_IfcDerivedUnitElement_type = new entity(strings[1952], false, 302, 0);
    IFC4X3_RC4_IfcDimensionalExponents_type = new entity(strings[1953], false, 305, 0);
    IFC4X3_RC4_IfcExternalInformation_type = new entity(strings[1954], true, 428, 0);
    IFC4X3_RC4_IfcExternalReference_type = new entity(strings[1955], true, 432, 0);
    IFC4X3_RC4_IfcExternallyDefinedHatchStyle_type = new entity(strings[1956], false, 429, IFC4X3_RC4_IfcExternalReference_type);
    IFC4X3_RC4_IfcExternallyDefinedSurfaceStyle_type = new entity(strings[1957], false, 430, IFC4X3_RC4_IfcExternalReference_type);
    IFC4X3_RC4_IfcExternallyDefinedTextFont_type = new entity(strings[1958], false, 431, IFC4X3_RC4_IfcExternalReference_type);
    IFC4X3_RC4_IfcGridAxis_type = new entity(strings[1959], false, 525, 0);
    IFC4X3_RC4_IfcIrregularTimeSeriesValue_type = new entity(strings[1960], false, 566, 0);
    IFC4X3_RC4_IfcLibraryInformation_type = new entity(strings[1961], false, 588, IFC4X3_RC4_IfcExternalInformation_type);
    IFC4X3_RC4_IfcLibraryReference_type = new entity(strings[1962], false, 589, IFC4X3_RC4_IfcExternalReference_type);
    IFC4X3_RC4_IfcLightDistributionData_type = new entity(strings[1963], false, 592, 0);
    IFC4X3_RC4_IfcLightIntensityDistribution_type = new entity(strings[1964], false, 598, 0);
    IFC4X3_RC4_IfcMapConversion_type = new entity(strings[1965], false, 629, IFC4X3_RC4_IfcCoordinateOperation_type);
    IFC4X3_RC4_IfcMaterialClassificationRelationship_type = new entity(strings[1966], false, 639, 0);
    IFC4X3_RC4_IfcMaterialDefinition_type = new entity(strings[1967], true, 642, 0);
    IFC4X3_RC4_IfcMaterialLayer_type = new entity(strings[1968], false, 644, IFC4X3_RC4_IfcMaterialDefinition_type);
    IFC4X3_RC4_IfcMaterialLayerSet_type = new entity(strings[1969], false, 645, IFC4X3_RC4_IfcMaterialDefinition_type);
    IFC4X3_RC4_IfcMaterialLayerWithOffsets_type = new entity(strings[1970], false, 647, IFC4X3_RC4_IfcMaterialLayer_type);
    IFC4X3_RC4_IfcMaterialList_type = new entity(strings[1971], false, 648, 0);
    IFC4X3_RC4_IfcMaterialProfile_type = new entity(strings[1972], false, 649, IFC4X3_RC4_IfcMaterialDefinition_type);
    IFC4X3_RC4_IfcMaterialProfileSet_type = new entity(strings[1973], false, 650, IFC4X3_RC4_IfcMaterialDefinition_type);
    IFC4X3_RC4_IfcMaterialProfileWithOffsets_type = new entity(strings[1974], false, 653, IFC4X3_RC4_IfcMaterialProfile_type);
    IFC4X3_RC4_IfcMaterialUsageDefinition_type = new entity(strings[1975], true, 657, 0);
    IFC4X3_RC4_IfcMeasureWithUnit_type = new entity(strings[1976], false, 659, 0);
    IFC4X3_RC4_IfcMetric_type = new entity(strings[1977], false, 670, IFC4X3_RC4_IfcConstraint_type);
    IFC4X3_RC4_IfcMonetaryUnit_type = new entity(strings[1978], false, 687, 0);
    IFC4X3_RC4_IfcNamedUnit_type = new entity(strings[1979], true, 695, 0);
    IFC4X3_RC4_IfcObjectPlacement_type = new entity(strings[1980], true, 706, 0);
    IFC4X3_RC4_IfcObjective_type = new entity(strings[1981], false, 704, IFC4X3_RC4_IfcConstraint_type);
    IFC4X3_RC4_IfcOrganization_type = new entity(strings[1982], false, 720, 0);
    IFC4X3_RC4_IfcOwnerHistory_type = new entity(strings[1983], false, 727, 0);
    IFC4X3_RC4_IfcPerson_type = new entity(strings[1984], false, 741, 0);
    IFC4X3_RC4_IfcPersonAndOrganization_type = new entity(strings[1985], false, 742, 0);
    IFC4X3_RC4_IfcPhysicalQuantity_type = new entity(strings[1986], true, 746, 0);
    IFC4X3_RC4_IfcPhysicalSimpleQuantity_type = new entity(strings[1987], true, 747, IFC4X3_RC4_IfcPhysicalQuantity_type);
    IFC4X3_RC4_IfcPostalAddress_type = new entity(strings[1988], false, 786, IFC4X3_RC4_IfcAddress_type);
    IFC4X3_RC4_IfcPresentationItem_type = new entity(strings[1989], true, 796, 0);
    IFC4X3_RC4_IfcPresentationLayerAssignment_type = new entity(strings[1990], false, 797, 0);
    IFC4X3_RC4_IfcPresentationLayerWithStyle_type = new entity(strings[1991], false, 798, IFC4X3_RC4_IfcPresentationLayerAssignment_type);
    IFC4X3_RC4_IfcPresentationStyle_type = new entity(strings[1992], true, 799, 0);
    IFC4X3_RC4_IfcProductRepresentation_type = new entity(strings[1993], true, 808, 0);
    IFC4X3_RC4_IfcProfileDef_type = new entity(strings[1994], false, 811, 0);
    IFC4X3_RC4_IfcProjectedCRS_type = new entity(strings[1995], false, 815, IFC4X3_RC4_IfcCoordinateReferenceSystem_type);
    IFC4X3_RC4_IfcPropertyAbstraction_type = new entity(strings[1996], true, 823, 0);
    IFC4X3_RC4_IfcPropertyEnumeration_type = new entity(strings[1997], false, 828, IFC4X3_RC4_IfcPropertyAbstraction_type);
    IFC4X3_RC4_IfcQuantityArea_type = new entity(strings[1998], false, 851, IFC4X3_RC4_IfcPhysicalSimpleQuantity_type);
    IFC4X3_RC4_IfcQuantityCount_type = new entity(strings[1999], false, 852, IFC4X3_RC4_IfcPhysicalSimpleQuantity_type);
    IFC4X3_RC4_IfcQuantityLength_type = new entity(strings[2000], false, 853, IFC4X3_RC4_IfcPhysicalSimpleQuantity_type);
    IFC4X3_RC4_IfcQuantityTime_type = new entity(strings[2001], false, 855, IFC4X3_RC4_IfcPhysicalSimpleQuantity_type);
    IFC4X3_RC4_IfcQuantityVolume_type = new entity(strings[2002], false, 856, IFC4X3_RC4_IfcPhysicalSimpleQuantity_type);
    IFC4X3_RC4_IfcQuantityWeight_type = new entity(strings[2003], false, 857, IFC4X3_RC4_IfcPhysicalSimpleQuantity_type);
    IFC4X3_RC4_IfcRecurrencePattern_type = new entity(strings[2004], false, 882, 0);
    IFC4X3_RC4_IfcReference_type = new entity(strings[2005], false, 884, 0);
    IFC4X3_RC4_IfcRepresentation_type = new entity(strings[2006], true, 955, 0);
    IFC4X3_RC4_IfcRepresentationContext_type = new entity(strings[2007], true, 956, 0);
    IFC4X3_RC4_IfcRepresentationItem_type = new entity(strings[2008], true, 957, 0);
    IFC4X3_RC4_IfcRepresentationMap_type = new entity(strings[2009], false, 958, 0);
    IFC4X3_RC4_IfcResourceLevelRelationship_type = new entity(strings[2010], true, 962, 0);
    IFC4X3_RC4_IfcRoot_type = new entity(strings[2011], true, 977, 0);
    IFC4X3_RC4_IfcSIUnit_type = new entity(strings[2012], false, 1028, IFC4X3_RC4_IfcNamedUnit_type);
    IFC4X3_RC4_IfcSchedulingTime_type = new entity(strings[2013], true, 986, 0);
    IFC4X3_RC4_IfcShapeAspect_type = new entity(strings[2014], false, 1009, 0);
    IFC4X3_RC4_IfcShapeModel_type = new entity(strings[2015], true, 1010, IFC4X3_RC4_IfcRepresentation_type);
    IFC4X3_RC4_IfcShapeRepresentation_type = new entity(strings[2016], false, 1011, IFC4X3_RC4_IfcShapeModel_type);
    IFC4X3_RC4_IfcStructuralConnectionCondition_type = new entity(strings[2017], true, 1085, 0);
    IFC4X3_RC4_IfcStructuralLoad_type = new entity(strings[2018], true, 1095, 0);
    IFC4X3_RC4_IfcStructuralLoadConfiguration_type = new entity(strings[2019], false, 1097, IFC4X3_RC4_IfcStructuralLoad_type);
    IFC4X3_RC4_IfcStructuralLoadOrResult_type = new entity(strings[2020], true, 1100, IFC4X3_RC4_IfcStructuralLoad_type);
    IFC4X3_RC4_IfcStructuralLoadStatic_type = new entity(strings[2021], true, 1106, IFC4X3_RC4_IfcStructuralLoadOrResult_type);
    IFC4X3_RC4_IfcStructuralLoadTemperature_type = new entity(strings[2022], false, 1107, IFC4X3_RC4_IfcStructuralLoadStatic_type);
    IFC4X3_RC4_IfcStyleModel_type = new entity(strings[2023], true, 1124, IFC4X3_RC4_IfcRepresentation_type);
    IFC4X3_RC4_IfcStyledItem_type = new entity(strings[2024], false, 1122, IFC4X3_RC4_IfcRepresentationItem_type);
    IFC4X3_RC4_IfcStyledRepresentation_type = new entity(strings[2025], false, 1123, IFC4X3_RC4_IfcStyleModel_type);
    IFC4X3_RC4_IfcSurfaceReinforcementArea_type = new entity(strings[2026], false, 1137, IFC4X3_RC4_IfcStructuralLoadOrResult_type);
    IFC4X3_RC4_IfcSurfaceStyle_type = new entity(strings[2027], false, 1139, IFC4X3_RC4_IfcPresentationStyle_type);
    IFC4X3_RC4_IfcSurfaceStyleLighting_type = new entity(strings[2028], false, 1141, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcSurfaceStyleRefraction_type = new entity(strings[2029], false, 1142, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcSurfaceStyleShading_type = new entity(strings[2030], false, 1144, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcSurfaceStyleWithTextures_type = new entity(strings[2031], false, 1145, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcSurfaceTexture_type = new entity(strings[2032], true, 1146, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcTable_type = new entity(strings[2033], false, 1158, 0);
    IFC4X3_RC4_IfcTableColumn_type = new entity(strings[2034], false, 1159, 0);
    IFC4X3_RC4_IfcTableRow_type = new entity(strings[2035], false, 1160, 0);
    IFC4X3_RC4_IfcTaskTime_type = new entity(strings[2036], false, 1166, IFC4X3_RC4_IfcSchedulingTime_type);
    IFC4X3_RC4_IfcTaskTimeRecurring_type = new entity(strings[2037], false, 1167, IFC4X3_RC4_IfcTaskTime_type);
    IFC4X3_RC4_IfcTelecomAddress_type = new entity(strings[2038], false, 1170, IFC4X3_RC4_IfcAddress_type);
    IFC4X3_RC4_IfcTextStyle_type = new entity(strings[2039], false, 1192, IFC4X3_RC4_IfcPresentationStyle_type);
    IFC4X3_RC4_IfcTextStyleForDefinedFont_type = new entity(strings[2040], false, 1194, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcTextStyleTextModel_type = new entity(strings[2041], false, 1195, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcTextureCoordinate_type = new entity(strings[2042], true, 1197, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcTextureCoordinateGenerator_type = new entity(strings[2043], false, 1198, IFC4X3_RC4_IfcTextureCoordinate_type);
    IFC4X3_RC4_IfcTextureMap_type = new entity(strings[2044], false, 1199, IFC4X3_RC4_IfcTextureCoordinate_type);
    IFC4X3_RC4_IfcTextureVertex_type = new entity(strings[2045], false, 1200, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcTextureVertexList_type = new entity(strings[2046], false, 1201, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcTimePeriod_type = new entity(strings[2047], false, 1212, 0);
    IFC4X3_RC4_IfcTimeSeries_type = new entity(strings[2048], true, 1213, 0);
    IFC4X3_RC4_IfcTimeSeriesValue_type = new entity(strings[2049], false, 1215, 0);
    IFC4X3_RC4_IfcTopologicalRepresentationItem_type = new entity(strings[2050], true, 1217, IFC4X3_RC4_IfcRepresentationItem_type);
    IFC4X3_RC4_IfcTopologyRepresentation_type = new entity(strings[2051], false, 1218, IFC4X3_RC4_IfcShapeModel_type);
    IFC4X3_RC4_IfcUnitAssignment_type = new entity(strings[2052], false, 1255, 0);
    IFC4X3_RC4_IfcVertex_type = new entity(strings[2053], false, 1266, IFC4X3_RC4_IfcTopologicalRepresentationItem_type);
    IFC4X3_RC4_IfcVertexPoint_type = new entity(strings[2054], false, 1268, IFC4X3_RC4_IfcVertex_type);
    IFC4X3_RC4_IfcVirtualGridIntersection_type = new entity(strings[2055], false, 1276, 0);
    IFC4X3_RC4_IfcWorkTime_type = new entity(strings[2056], false, 1313, IFC4X3_RC4_IfcSchedulingTime_type);
    IFC4X3_RC4_IfcActorSelect_type = new select_type(strings[2057], 8, {
        IFC4X3_RC4_IfcOrganization_type,
        IFC4X3_RC4_IfcPerson_type,
        IFC4X3_RC4_IfcPersonAndOrganization_type
    });
    IFC4X3_RC4_IfcArcIndex_type = new type_declaration(strings[2058], 57, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_RC4_IfcPositiveInteger_type)));
    IFC4X3_RC4_IfcBendingParameterSelect_type = new select_type(strings[2059], 81, {
        IFC4X3_RC4_IfcLengthMeasure_type,
        IFC4X3_RC4_IfcPlaneAngleMeasure_type
    });
    IFC4X3_RC4_IfcBoxAlignment_type = new type_declaration(strings[2060], 103, new named_type(IFC4X3_RC4_IfcLabel_type));
    IFC4X3_RC4_IfcCurveMeasureSelect_type = new select_type(strings[2061], 278, {
        IFC4X3_RC4_IfcNonNegativeLengthMeasure_type,
        IFC4X3_RC4_IfcParameterValue_type
    });
    IFC4X3_RC4_IfcDerivedMeasureValue_type = new select_type(strings[2062], 299, {
        IFC4X3_RC4_IfcAbsorbedDoseMeasure_type,
        IFC4X3_RC4_IfcAccelerationMeasure_type,
        IFC4X3_RC4_IfcAngularVelocityMeasure_type,
        IFC4X3_RC4_IfcAreaDensityMeasure_type,
        IFC4X3_RC4_IfcCompoundPlaneAngleMeasure_type,
        IFC4X3_RC4_IfcCurvatureMeasure_type,
        IFC4X3_RC4_IfcDoseEquivalentMeasure_type,
        IFC4X3_RC4_IfcDynamicViscosityMeasure_type,
        IFC4X3_RC4_IfcElectricCapacitanceMeasure_type,
        IFC4X3_RC4_IfcElectricChargeMeasure_type,
        IFC4X3_RC4_IfcElectricConductanceMeasure_type,
        IFC4X3_RC4_IfcElectricResistanceMeasure_type,
        IFC4X3_RC4_IfcElectricVoltageMeasure_type,
        IFC4X3_RC4_IfcEnergyMeasure_type,
        IFC4X3_RC4_IfcForceMeasure_type,
        IFC4X3_RC4_IfcFrequencyMeasure_type,
        IFC4X3_RC4_IfcHeatFluxDensityMeasure_type,
        IFC4X3_RC4_IfcHeatingValueMeasure_type,
        IFC4X3_RC4_IfcIlluminanceMeasure_type,
        IFC4X3_RC4_IfcInductanceMeasure_type,
        IFC4X3_RC4_IfcIntegerCountRateMeasure_type,
        IFC4X3_RC4_IfcIonConcentrationMeasure_type,
        IFC4X3_RC4_IfcIsothermalMoistureCapacityMeasure_type,
        IFC4X3_RC4_IfcKinematicViscosityMeasure_type,
        IFC4X3_RC4_IfcLinearForceMeasure_type,
        IFC4X3_RC4_IfcLinearMomentMeasure_type,
        IFC4X3_RC4_IfcLinearStiffnessMeasure_type,
        IFC4X3_RC4_IfcLinearVelocityMeasure_type,
        IFC4X3_RC4_IfcLuminousFluxMeasure_type,
        IFC4X3_RC4_IfcLuminousIntensityDistributionMeasure_type,
        IFC4X3_RC4_IfcMagneticFluxDensityMeasure_type,
        IFC4X3_RC4_IfcMagneticFluxMeasure_type,
        IFC4X3_RC4_IfcMassDensityMeasure_type,
        IFC4X3_RC4_IfcMassFlowRateMeasure_type,
        IFC4X3_RC4_IfcMassPerLengthMeasure_type,
        IFC4X3_RC4_IfcModulusOfElasticityMeasure_type,
        IFC4X3_RC4_IfcModulusOfLinearSubgradeReactionMeasure_type,
        IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionMeasure_type,
        IFC4X3_RC4_IfcModulusOfSubgradeReactionMeasure_type,
        IFC4X3_RC4_IfcMoistureDiffusivityMeasure_type,
        IFC4X3_RC4_IfcMolecularWeightMeasure_type,
        IFC4X3_RC4_IfcMomentOfInertiaMeasure_type,
        IFC4X3_RC4_IfcMonetaryMeasure_type,
        IFC4X3_RC4_IfcPHMeasure_type,
        IFC4X3_RC4_IfcPlanarForceMeasure_type,
        IFC4X3_RC4_IfcPowerMeasure_type,
        IFC4X3_RC4_IfcPressureMeasure_type,
        IFC4X3_RC4_IfcRadioActivityMeasure_type,
        IFC4X3_RC4_IfcRotationalFrequencyMeasure_type,
        IFC4X3_RC4_IfcRotationalMassMeasure_type,
        IFC4X3_RC4_IfcRotationalStiffnessMeasure_type,
        IFC4X3_RC4_IfcSectionModulusMeasure_type,
        IFC4X3_RC4_IfcSectionalAreaIntegralMeasure_type,
        IFC4X3_RC4_IfcShearModulusMeasure_type,
        IFC4X3_RC4_IfcSoundPowerLevelMeasure_type,
        IFC4X3_RC4_IfcSoundPowerMeasure_type,
        IFC4X3_RC4_IfcSoundPressureLevelMeasure_type,
        IFC4X3_RC4_IfcSoundPressureMeasure_type,
        IFC4X3_RC4_IfcSpecificHeatCapacityMeasure_type,
        IFC4X3_RC4_IfcTemperatureGradientMeasure_type,
        IFC4X3_RC4_IfcTemperatureRateOfChangeMeasure_type,
        IFC4X3_RC4_IfcThermalAdmittanceMeasure_type,
        IFC4X3_RC4_IfcThermalConductivityMeasure_type,
        IFC4X3_RC4_IfcThermalExpansionCoefficientMeasure_type,
        IFC4X3_RC4_IfcThermalResistanceMeasure_type,
        IFC4X3_RC4_IfcThermalTransmittanceMeasure_type,
        IFC4X3_RC4_IfcTorqueMeasure_type,
        IFC4X3_RC4_IfcVaporPermeabilityMeasure_type,
        IFC4X3_RC4_IfcVolumetricFlowRateMeasure_type,
        IFC4X3_RC4_IfcWarpingConstantMeasure_type,
        IFC4X3_RC4_IfcWarpingMomentMeasure_type
    });
    IFC4X3_RC4_IfcFacilityPartTypeSelect_type = new select_type(strings[2063], 449, {
        IFC4X3_RC4_IfcBridgePartTypeEnum_type,
        IFC4X3_RC4_IfcFacilityPartCommonTypeEnum_type,
        IFC4X3_RC4_IfcMarinePartTypeEnum_type,
        IFC4X3_RC4_IfcRailwayPartTypeEnum_type,
        IFC4X3_RC4_IfcRoadPartTypeEnum_type
    });
    IFC4X3_RC4_IfcImpactProtectionDeviceTypeSelect_type = new select_type(strings[2064], 546, {
        IFC4X3_RC4_IfcImpactProtectionDeviceTypeEnum_type,
        IFC4X3_RC4_IfcVibrationDamperTypeEnum_type,
        IFC4X3_RC4_IfcVibrationIsolatorTypeEnum_type
    });
    IFC4X3_RC4_IfcLayeredItem_type = new select_type(strings[2065], 585, {
        IFC4X3_RC4_IfcRepresentation_type,
        IFC4X3_RC4_IfcRepresentationItem_type
    });
    IFC4X3_RC4_IfcLibrarySelect_type = new select_type(strings[2066], 590, {
        IFC4X3_RC4_IfcLibraryInformation_type,
        IFC4X3_RC4_IfcLibraryReference_type
    });
    IFC4X3_RC4_IfcLightDistributionDataSourceSelect_type = new select_type(strings[2067], 593, {
        IFC4X3_RC4_IfcExternalReference_type,
        IFC4X3_RC4_IfcLightIntensityDistribution_type
    });
    IFC4X3_RC4_IfcLineIndex_type = new type_declaration(strings[2068], 613, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcPositiveInteger_type)));
    IFC4X3_RC4_IfcMaterialSelect_type = new select_type(strings[2069], 656, {
        IFC4X3_RC4_IfcMaterialDefinition_type,
        IFC4X3_RC4_IfcMaterialList_type,
        IFC4X3_RC4_IfcMaterialUsageDefinition_type
    });
    IFC4X3_RC4_IfcNormalisedRatioMeasure_type = new type_declaration(strings[2070], 700, new named_type(IFC4X3_RC4_IfcRatioMeasure_type));
    IFC4X3_RC4_IfcObjectReferenceSelect_type = new select_type(strings[2071], 707, {
        IFC4X3_RC4_IfcAddress_type,
        IFC4X3_RC4_IfcAppliedValue_type,
        IFC4X3_RC4_IfcExternalReference_type,
        IFC4X3_RC4_IfcMaterialDefinition_type,
        IFC4X3_RC4_IfcOrganization_type,
        IFC4X3_RC4_IfcPerson_type,
        IFC4X3_RC4_IfcPersonAndOrganization_type,
        IFC4X3_RC4_IfcTable_type,
        IFC4X3_RC4_IfcTimeSeries_type
    });
    IFC4X3_RC4_IfcPositiveRatioMeasure_type = new type_declaration(strings[2072], 785, new named_type(IFC4X3_RC4_IfcRatioMeasure_type));
    IFC4X3_RC4_IfcSegmentIndexSelect_type = new select_type(strings[2073], 1000, {
        IFC4X3_RC4_IfcArcIndex_type,
        IFC4X3_RC4_IfcLineIndex_type
    });
    IFC4X3_RC4_IfcSimpleValue_type = new select_type(strings[2074], 1024, {
        IFC4X3_RC4_IfcBinary_type,
        IFC4X3_RC4_IfcBoolean_type,
        IFC4X3_RC4_IfcDate_type,
        IFC4X3_RC4_IfcDateTime_type,
        IFC4X3_RC4_IfcDuration_type,
        IFC4X3_RC4_IfcIdentifier_type,
        IFC4X3_RC4_IfcInteger_type,
        IFC4X3_RC4_IfcLabel_type,
        IFC4X3_RC4_IfcLogical_type,
        IFC4X3_RC4_IfcPositiveInteger_type,
        IFC4X3_RC4_IfcReal_type,
        IFC4X3_RC4_IfcText_type,
        IFC4X3_RC4_IfcTime_type,
        IFC4X3_RC4_IfcTimeStamp_type
    });
    IFC4X3_RC4_IfcSizeSelect_type = new select_type(strings[2075], 1030, {
        IFC4X3_RC4_IfcDescriptiveMeasure_type,
        IFC4X3_RC4_IfcLengthMeasure_type,
        IFC4X3_RC4_IfcNormalisedRatioMeasure_type,
        IFC4X3_RC4_IfcPositiveLengthMeasure_type,
        IFC4X3_RC4_IfcPositiveRatioMeasure_type,
        IFC4X3_RC4_IfcRatioMeasure_type
    });
    IFC4X3_RC4_IfcSpecularHighlightSelect_type = new select_type(strings[2076], 1065, {
        IFC4X3_RC4_IfcSpecularExponent_type,
        IFC4X3_RC4_IfcSpecularRoughness_type
    });
    IFC4X3_RC4_IfcSurfaceStyleElementSelect_type = new select_type(strings[2077], 1140, {
        IFC4X3_RC4_IfcExternallyDefinedSurfaceStyle_type,
        IFC4X3_RC4_IfcSurfaceStyleLighting_type,
        IFC4X3_RC4_IfcSurfaceStyleRefraction_type,
        IFC4X3_RC4_IfcSurfaceStyleShading_type,
        IFC4X3_RC4_IfcSurfaceStyleWithTextures_type
    });
    IFC4X3_RC4_IfcUnit_type = new select_type(strings[2078], 1248, {
        IFC4X3_RC4_IfcDerivedUnit_type,
        IFC4X3_RC4_IfcMonetaryUnit_type,
        IFC4X3_RC4_IfcNamedUnit_type
    });
    IFC4X3_RC4_IfcAlignmentCantSegment_type = new entity(strings[2079], false, 31, IFC4X3_RC4_IfcAlignmentParameterSegment_type);
    IFC4X3_RC4_IfcAlignmentHorizontalSegment_type = new entity(strings[2080], false, 34, IFC4X3_RC4_IfcAlignmentParameterSegment_type);
    IFC4X3_RC4_IfcApprovalRelationship_type = new entity(strings[2081], false, 53, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcArbitraryClosedProfileDef_type = new entity(strings[2082], false, 54, IFC4X3_RC4_IfcProfileDef_type);
    IFC4X3_RC4_IfcArbitraryOpenProfileDef_type = new entity(strings[2083], false, 55, IFC4X3_RC4_IfcProfileDef_type);
    IFC4X3_RC4_IfcArbitraryProfileDefWithVoids_type = new entity(strings[2084], false, 56, IFC4X3_RC4_IfcArbitraryClosedProfileDef_type);
    IFC4X3_RC4_IfcBlobTexture_type = new entity(strings[2085], false, 83, IFC4X3_RC4_IfcSurfaceTexture_type);
    IFC4X3_RC4_IfcCenterLineProfileDef_type = new entity(strings[2086], false, 156, IFC4X3_RC4_IfcArbitraryOpenProfileDef_type);
    IFC4X3_RC4_IfcClassification_type = new entity(strings[2087], false, 169, IFC4X3_RC4_IfcExternalInformation_type);
    IFC4X3_RC4_IfcClassificationReference_type = new entity(strings[2088], false, 170, IFC4X3_RC4_IfcExternalReference_type);
    IFC4X3_RC4_IfcColourRgbList_type = new entity(strings[2089], false, 181, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcColourSpecification_type = new entity(strings[2090], true, 182, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcCompositeProfileDef_type = new entity(strings[2091], false, 197, IFC4X3_RC4_IfcProfileDef_type);
    IFC4X3_RC4_IfcConnectedFaceSet_type = new entity(strings[2092], false, 206, IFC4X3_RC4_IfcTopologicalRepresentationItem_type);
    IFC4X3_RC4_IfcConnectionCurveGeometry_type = new entity(strings[2093], false, 207, IFC4X3_RC4_IfcConnectionGeometry_type);
    IFC4X3_RC4_IfcConnectionPointEccentricity_type = new entity(strings[2094], false, 209, IFC4X3_RC4_IfcConnectionPointGeometry_type);
    IFC4X3_RC4_IfcContextDependentUnit_type = new entity(strings[2095], false, 229, IFC4X3_RC4_IfcNamedUnit_type);
    IFC4X3_RC4_IfcConversionBasedUnit_type = new entity(strings[2096], false, 234, IFC4X3_RC4_IfcNamedUnit_type);
    IFC4X3_RC4_IfcConversionBasedUnitWithOffset_type = new entity(strings[2097], false, 235, IFC4X3_RC4_IfcConversionBasedUnit_type);
    IFC4X3_RC4_IfcCurrencyRelationship_type = new entity(strings[2098], false, 268, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcCurveStyle_type = new entity(strings[2099], false, 282, IFC4X3_RC4_IfcPresentationStyle_type);
    IFC4X3_RC4_IfcCurveStyleFont_type = new entity(strings[2100], false, 283, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcCurveStyleFontAndScaling_type = new entity(strings[2101], false, 284, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcCurveStyleFontPattern_type = new entity(strings[2102], false, 285, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcDerivedProfileDef_type = new entity(strings[2103], false, 300, IFC4X3_RC4_IfcProfileDef_type);
    IFC4X3_RC4_IfcDocumentInformation_type = new entity(strings[2104], false, 332, IFC4X3_RC4_IfcExternalInformation_type);
    IFC4X3_RC4_IfcDocumentInformationRelationship_type = new entity(strings[2105], false, 333, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcDocumentReference_type = new entity(strings[2106], false, 334, IFC4X3_RC4_IfcExternalReference_type);
    IFC4X3_RC4_IfcEdge_type = new entity(strings[2107], false, 368, IFC4X3_RC4_IfcTopologicalRepresentationItem_type);
    IFC4X3_RC4_IfcEdgeCurve_type = new entity(strings[2108], false, 369, IFC4X3_RC4_IfcEdge_type);
    IFC4X3_RC4_IfcEventTime_type = new entity(strings[2109], false, 423, IFC4X3_RC4_IfcSchedulingTime_type);
    IFC4X3_RC4_IfcExtendedProperties_type = new entity(strings[2110], true, 427, IFC4X3_RC4_IfcPropertyAbstraction_type);
    IFC4X3_RC4_IfcExternalReferenceRelationship_type = new entity(strings[2111], false, 433, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcFace_type = new entity(strings[2112], false, 439, IFC4X3_RC4_IfcTopologicalRepresentationItem_type);
    IFC4X3_RC4_IfcFaceBound_type = new entity(strings[2113], false, 441, IFC4X3_RC4_IfcTopologicalRepresentationItem_type);
    IFC4X3_RC4_IfcFaceOuterBound_type = new entity(strings[2114], false, 442, IFC4X3_RC4_IfcFaceBound_type);
    IFC4X3_RC4_IfcFaceSurface_type = new entity(strings[2115], false, 443, IFC4X3_RC4_IfcFace_type);
    IFC4X3_RC4_IfcFailureConnectionCondition_type = new entity(strings[2116], false, 451, IFC4X3_RC4_IfcStructuralConnectionCondition_type);
    IFC4X3_RC4_IfcFillAreaStyle_type = new entity(strings[2117], false, 461, IFC4X3_RC4_IfcPresentationStyle_type);
    IFC4X3_RC4_IfcGeometricRepresentationContext_type = new entity(strings[2118], false, 511, IFC4X3_RC4_IfcRepresentationContext_type);
    IFC4X3_RC4_IfcGeometricRepresentationItem_type = new entity(strings[2119], true, 512, IFC4X3_RC4_IfcRepresentationItem_type);
    IFC4X3_RC4_IfcGeometricRepresentationSubContext_type = new entity(strings[2120], false, 513, IFC4X3_RC4_IfcGeometricRepresentationContext_type);
    IFC4X3_RC4_IfcGeometricSet_type = new entity(strings[2121], false, 514, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcGridPlacement_type = new entity(strings[2122], false, 526, IFC4X3_RC4_IfcObjectPlacement_type);
    IFC4X3_RC4_IfcHalfSpaceSolid_type = new entity(strings[2123], false, 530, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcImageTexture_type = new entity(strings[2124], false, 542, IFC4X3_RC4_IfcSurfaceTexture_type);
    IFC4X3_RC4_IfcIndexedColourMap_type = new entity(strings[2125], false, 547, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcIndexedTextureMap_type = new entity(strings[2126], true, 551, IFC4X3_RC4_IfcTextureCoordinate_type);
    IFC4X3_RC4_IfcIndexedTriangleTextureMap_type = new entity(strings[2127], false, 552, IFC4X3_RC4_IfcIndexedTextureMap_type);
    IFC4X3_RC4_IfcIrregularTimeSeries_type = new entity(strings[2128], false, 565, IFC4X3_RC4_IfcTimeSeries_type);
    IFC4X3_RC4_IfcLagTime_type = new entity(strings[2129], false, 580, IFC4X3_RC4_IfcSchedulingTime_type);
    IFC4X3_RC4_IfcLightSource_type = new entity(strings[2130], true, 599, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcLightSourceAmbient_type = new entity(strings[2131], false, 600, IFC4X3_RC4_IfcLightSource_type);
    IFC4X3_RC4_IfcLightSourceDirectional_type = new entity(strings[2132], false, 601, IFC4X3_RC4_IfcLightSource_type);
    IFC4X3_RC4_IfcLightSourceGoniometric_type = new entity(strings[2133], false, 602, IFC4X3_RC4_IfcLightSource_type);
    IFC4X3_RC4_IfcLightSourcePositional_type = new entity(strings[2134], false, 603, IFC4X3_RC4_IfcLightSource_type);
    IFC4X3_RC4_IfcLightSourceSpot_type = new entity(strings[2135], false, 604, IFC4X3_RC4_IfcLightSourcePositional_type);
    IFC4X3_RC4_IfcLinearPlacement_type = new entity(strings[2136], false, 609, IFC4X3_RC4_IfcObjectPlacement_type);
    IFC4X3_RC4_IfcLocalPlacement_type = new entity(strings[2137], false, 618, IFC4X3_RC4_IfcObjectPlacement_type);
    IFC4X3_RC4_IfcLoop_type = new entity(strings[2138], false, 621, IFC4X3_RC4_IfcTopologicalRepresentationItem_type);
    IFC4X3_RC4_IfcMappedItem_type = new entity(strings[2139], false, 630, IFC4X3_RC4_IfcRepresentationItem_type);
    IFC4X3_RC4_IfcMaterial_type = new entity(strings[2140], false, 638, IFC4X3_RC4_IfcMaterialDefinition_type);
    IFC4X3_RC4_IfcMaterialConstituent_type = new entity(strings[2141], false, 640, IFC4X3_RC4_IfcMaterialDefinition_type);
    IFC4X3_RC4_IfcMaterialConstituentSet_type = new entity(strings[2142], false, 641, IFC4X3_RC4_IfcMaterialDefinition_type);
    IFC4X3_RC4_IfcMaterialDefinitionRepresentation_type = new entity(strings[2143], false, 643, IFC4X3_RC4_IfcProductRepresentation_type);
    IFC4X3_RC4_IfcMaterialLayerSetUsage_type = new entity(strings[2144], false, 646, IFC4X3_RC4_IfcMaterialUsageDefinition_type);
    IFC4X3_RC4_IfcMaterialProfileSetUsage_type = new entity(strings[2145], false, 651, IFC4X3_RC4_IfcMaterialUsageDefinition_type);
    IFC4X3_RC4_IfcMaterialProfileSetUsageTapering_type = new entity(strings[2146], false, 652, IFC4X3_RC4_IfcMaterialProfileSetUsage_type);
    IFC4X3_RC4_IfcMaterialProperties_type = new entity(strings[2147], false, 654, IFC4X3_RC4_IfcExtendedProperties_type);
    IFC4X3_RC4_IfcMaterialRelationship_type = new entity(strings[2148], false, 655, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcMirroredProfileDef_type = new entity(strings[2149], false, 672, IFC4X3_RC4_IfcDerivedProfileDef_type);
    IFC4X3_RC4_IfcObjectDefinition_type = new entity(strings[2150], true, 703, IFC4X3_RC4_IfcRoot_type);
    IFC4X3_RC4_IfcOpenCrossProfileDef_type = new entity(strings[2151], false, 715, IFC4X3_RC4_IfcProfileDef_type);
    IFC4X3_RC4_IfcOpenShell_type = new entity(strings[2152], false, 719, IFC4X3_RC4_IfcConnectedFaceSet_type);
    IFC4X3_RC4_IfcOrganizationRelationship_type = new entity(strings[2153], false, 721, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcOrientedEdge_type = new entity(strings[2154], false, 722, IFC4X3_RC4_IfcEdge_type);
    IFC4X3_RC4_IfcParameterizedProfileDef_type = new entity(strings[2155], true, 728, IFC4X3_RC4_IfcProfileDef_type);
    IFC4X3_RC4_IfcPath_type = new entity(strings[2156], false, 730, IFC4X3_RC4_IfcTopologicalRepresentationItem_type);
    IFC4X3_RC4_IfcPhysicalComplexQuantity_type = new entity(strings[2157], false, 744, IFC4X3_RC4_IfcPhysicalQuantity_type);
    IFC4X3_RC4_IfcPixelTexture_type = new entity(strings[2158], false, 758, IFC4X3_RC4_IfcSurfaceTexture_type);
    IFC4X3_RC4_IfcPlacement_type = new entity(strings[2159], true, 759, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcPlanarExtent_type = new entity(strings[2160], false, 761, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcPoint_type = new entity(strings[2161], true, 770, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcPointByDistanceExpression_type = new entity(strings[2162], false, 771, IFC4X3_RC4_IfcPoint_type);
    IFC4X3_RC4_IfcPointOnCurve_type = new entity(strings[2163], false, 772, IFC4X3_RC4_IfcPoint_type);
    IFC4X3_RC4_IfcPointOnSurface_type = new entity(strings[2164], false, 773, IFC4X3_RC4_IfcPoint_type);
    IFC4X3_RC4_IfcPolyLoop_type = new entity(strings[2165], false, 778, IFC4X3_RC4_IfcLoop_type);
    IFC4X3_RC4_IfcPolygonalBoundedHalfSpace_type = new entity(strings[2166], false, 775, IFC4X3_RC4_IfcHalfSpaceSolid_type);
    IFC4X3_RC4_IfcPreDefinedItem_type = new entity(strings[2167], true, 790, IFC4X3_RC4_IfcPresentationItem_type);
    IFC4X3_RC4_IfcPreDefinedProperties_type = new entity(strings[2168], true, 791, IFC4X3_RC4_IfcPropertyAbstraction_type);
    IFC4X3_RC4_IfcPreDefinedTextFont_type = new entity(strings[2169], true, 793, IFC4X3_RC4_IfcPreDefinedItem_type);
    IFC4X3_RC4_IfcProductDefinitionShape_type = new entity(strings[2170], false, 807, IFC4X3_RC4_IfcProductRepresentation_type);
    IFC4X3_RC4_IfcProfileProperties_type = new entity(strings[2171], false, 812, IFC4X3_RC4_IfcExtendedProperties_type);
    IFC4X3_RC4_IfcProperty_type = new entity(strings[2172], true, 822, IFC4X3_RC4_IfcPropertyAbstraction_type);
    IFC4X3_RC4_IfcPropertyDefinition_type = new entity(strings[2173], true, 825, IFC4X3_RC4_IfcRoot_type);
    IFC4X3_RC4_IfcPropertyDependencyRelationship_type = new entity(strings[2174], false, 826, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcPropertySetDefinition_type = new entity(strings[2175], true, 832, IFC4X3_RC4_IfcPropertyDefinition_type);
    IFC4X3_RC4_IfcPropertyTemplateDefinition_type = new entity(strings[2176], true, 840, IFC4X3_RC4_IfcPropertyDefinition_type);
    IFC4X3_RC4_IfcQuantitySet_type = new entity(strings[2177], true, 854, IFC4X3_RC4_IfcPropertySetDefinition_type);
    IFC4X3_RC4_IfcRectangleProfileDef_type = new entity(strings[2178], false, 879, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcRegularTimeSeries_type = new entity(strings[2179], false, 888, IFC4X3_RC4_IfcTimeSeries_type);
    IFC4X3_RC4_IfcReinforcementBarProperties_type = new entity(strings[2180], false, 891, IFC4X3_RC4_IfcPreDefinedProperties_type);
    IFC4X3_RC4_IfcRelationship_type = new entity(strings[2181], true, 921, IFC4X3_RC4_IfcRoot_type);
    IFC4X3_RC4_IfcResourceApprovalRelationship_type = new entity(strings[2182], false, 960, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcResourceConstraintRelationship_type = new entity(strings[2183], false, 961, IFC4X3_RC4_IfcResourceLevelRelationship_type);
    IFC4X3_RC4_IfcResourceTime_type = new entity(strings[2184], false, 965, IFC4X3_RC4_IfcSchedulingTime_type);
    IFC4X3_RC4_IfcRoundedRectangleProfileDef_type = new entity(strings[2185], false, 982, IFC4X3_RC4_IfcRectangleProfileDef_type);
    IFC4X3_RC4_IfcSectionProperties_type = new entity(strings[2186], false, 995, IFC4X3_RC4_IfcPreDefinedProperties_type);
    IFC4X3_RC4_IfcSectionReinforcementProperties_type = new entity(strings[2187], false, 996, IFC4X3_RC4_IfcPreDefinedProperties_type);
    IFC4X3_RC4_IfcSectionedSpine_type = new entity(strings[2188], false, 992, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcSegment_type = new entity(strings[2189], true, 998, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcShellBasedSurfaceModel_type = new entity(strings[2190], false, 1014, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcSimpleProperty_type = new entity(strings[2191], true, 1021, IFC4X3_RC4_IfcProperty_type);
    IFC4X3_RC4_IfcSlippageConnectionCondition_type = new entity(strings[2192], false, 1036, IFC4X3_RC4_IfcStructuralConnectionCondition_type);
    IFC4X3_RC4_IfcSolidModel_type = new entity(strings[2193], true, 1041, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcStructuralLoadLinearForce_type = new entity(strings[2194], false, 1099, IFC4X3_RC4_IfcStructuralLoadStatic_type);
    IFC4X3_RC4_IfcStructuralLoadPlanarForce_type = new entity(strings[2195], false, 1101, IFC4X3_RC4_IfcStructuralLoadStatic_type);
    IFC4X3_RC4_IfcStructuralLoadSingleDisplacement_type = new entity(strings[2196], false, 1102, IFC4X3_RC4_IfcStructuralLoadStatic_type);
    IFC4X3_RC4_IfcStructuralLoadSingleDisplacementDistortion_type = new entity(strings[2197], false, 1103, IFC4X3_RC4_IfcStructuralLoadSingleDisplacement_type);
    IFC4X3_RC4_IfcStructuralLoadSingleForce_type = new entity(strings[2198], false, 1104, IFC4X3_RC4_IfcStructuralLoadStatic_type);
    IFC4X3_RC4_IfcStructuralLoadSingleForceWarping_type = new entity(strings[2199], false, 1105, IFC4X3_RC4_IfcStructuralLoadSingleForce_type);
    IFC4X3_RC4_IfcSubedge_type = new entity(strings[2200], false, 1128, IFC4X3_RC4_IfcEdge_type);
    IFC4X3_RC4_IfcSurface_type = new entity(strings[2201], true, 1129, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcSurfaceStyleRendering_type = new entity(strings[2202], false, 1143, IFC4X3_RC4_IfcSurfaceStyleShading_type);
    IFC4X3_RC4_IfcSweptAreaSolid_type = new entity(strings[2203], true, 1147, IFC4X3_RC4_IfcSolidModel_type);
    IFC4X3_RC4_IfcSweptDiskSolid_type = new entity(strings[2204], false, 1148, IFC4X3_RC4_IfcSolidModel_type);
    IFC4X3_RC4_IfcSweptDiskSolidPolygonal_type = new entity(strings[2205], false, 1149, IFC4X3_RC4_IfcSweptDiskSolid_type);
    IFC4X3_RC4_IfcSweptSurface_type = new entity(strings[2206], true, 1150, IFC4X3_RC4_IfcSurface_type);
    IFC4X3_RC4_IfcTShapeProfileDef_type = new entity(strings[2207], false, 1240, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcTessellatedItem_type = new entity(strings[2208], true, 1183, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcTextLiteral_type = new entity(strings[2209], false, 1189, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcTextLiteralWithExtent_type = new entity(strings[2210], false, 1190, IFC4X3_RC4_IfcTextLiteral_type);
    IFC4X3_RC4_IfcTextStyleFontModel_type = new entity(strings[2211], false, 1193, IFC4X3_RC4_IfcPreDefinedTextFont_type);
    IFC4X3_RC4_IfcTrapeziumProfileDef_type = new entity(strings[2212], false, 1234, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcTypeObject_type = new entity(strings[2213], false, 1244, IFC4X3_RC4_IfcObjectDefinition_type);
    IFC4X3_RC4_IfcTypeProcess_type = new entity(strings[2214], true, 1245, IFC4X3_RC4_IfcTypeObject_type);
    IFC4X3_RC4_IfcTypeProduct_type = new entity(strings[2215], false, 1246, IFC4X3_RC4_IfcTypeObject_type);
    IFC4X3_RC4_IfcTypeResource_type = new entity(strings[2216], true, 1247, IFC4X3_RC4_IfcTypeObject_type);
    IFC4X3_RC4_IfcUShapeProfileDef_type = new entity(strings[2217], false, 1258, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcVector_type = new entity(strings[2218], false, 1264, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcVertexLoop_type = new entity(strings[2219], false, 1267, IFC4X3_RC4_IfcLoop_type);
    IFC4X3_RC4_IfcWindowStyle_type = new entity(strings[2220], false, 1300, IFC4X3_RC4_IfcTypeProduct_type);
    IFC4X3_RC4_IfcZShapeProfileDef_type = new entity(strings[2221], false, 1315, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcClassificationReferenceSelect_type = new select_type(strings[2222], 171, {
        IFC4X3_RC4_IfcClassification_type,
        IFC4X3_RC4_IfcClassificationReference_type
    });
    IFC4X3_RC4_IfcClassificationSelect_type = new select_type(strings[2223], 172, {
        IFC4X3_RC4_IfcClassification_type,
        IFC4X3_RC4_IfcClassificationReference_type
    });
    IFC4X3_RC4_IfcCoordinateReferenceSystemSelect_type = new select_type(strings[2224], 247, {
        IFC4X3_RC4_IfcCoordinateReferenceSystem_type,
        IFC4X3_RC4_IfcGeometricRepresentationContext_type
    });
    IFC4X3_RC4_IfcDefinitionSelect_type = new select_type(strings[2225], 298, {
        IFC4X3_RC4_IfcObjectDefinition_type,
        IFC4X3_RC4_IfcPropertyDefinition_type
    });
    IFC4X3_RC4_IfcDocumentSelect_type = new select_type(strings[2226], 335, {
        IFC4X3_RC4_IfcDocumentInformation_type,
        IFC4X3_RC4_IfcDocumentReference_type
    });
    IFC4X3_RC4_IfcHatchLineDistanceSelect_type = new select_type(strings[2227], 531, {
        IFC4X3_RC4_IfcPositiveLengthMeasure_type,
        IFC4X3_RC4_IfcVector_type
    });
    IFC4X3_RC4_IfcMeasureValue_type = new select_type(strings[2228], 658, {
        IFC4X3_RC4_IfcAmountOfSubstanceMeasure_type,
        IFC4X3_RC4_IfcAreaMeasure_type,
        IFC4X3_RC4_IfcComplexNumber_type,
        IFC4X3_RC4_IfcContextDependentMeasure_type,
        IFC4X3_RC4_IfcCountMeasure_type,
        IFC4X3_RC4_IfcDescriptiveMeasure_type,
        IFC4X3_RC4_IfcElectricCurrentMeasure_type,
        IFC4X3_RC4_IfcLengthMeasure_type,
        IFC4X3_RC4_IfcLuminousIntensityMeasure_type,
        IFC4X3_RC4_IfcMassMeasure_type,
        IFC4X3_RC4_IfcNonNegativeLengthMeasure_type,
        IFC4X3_RC4_IfcNormalisedRatioMeasure_type,
        IFC4X3_RC4_IfcNumericMeasure_type,
        IFC4X3_RC4_IfcParameterValue_type,
        IFC4X3_RC4_IfcPlaneAngleMeasure_type,
        IFC4X3_RC4_IfcPositiveLengthMeasure_type,
        IFC4X3_RC4_IfcPositivePlaneAngleMeasure_type,
        IFC4X3_RC4_IfcPositiveRatioMeasure_type,
        IFC4X3_RC4_IfcRatioMeasure_type,
        IFC4X3_RC4_IfcSolidAngleMeasure_type,
        IFC4X3_RC4_IfcThermodynamicTemperatureMeasure_type,
        IFC4X3_RC4_IfcTimeMeasure_type,
        IFC4X3_RC4_IfcVolumeMeasure_type
    });
    IFC4X3_RC4_IfcPointOrVertexPoint_type = new select_type(strings[2229], 774, {
        IFC4X3_RC4_IfcPoint_type,
        IFC4X3_RC4_IfcVertexPoint_type
    });
    IFC4X3_RC4_IfcProductRepresentationSelect_type = new select_type(strings[2230], 809, {
        IFC4X3_RC4_IfcProductDefinitionShape_type,
        IFC4X3_RC4_IfcRepresentationMap_type
    });
    IFC4X3_RC4_IfcPropertySetDefinitionSet_type = new type_declaration(strings[2231], 834, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPropertySetDefinition_type)));
    IFC4X3_RC4_IfcResourceObjectSelect_type = new select_type(strings[2232], 963, {
        IFC4X3_RC4_IfcActorRole_type,
        IFC4X3_RC4_IfcAppliedValue_type,
        IFC4X3_RC4_IfcApproval_type,
        IFC4X3_RC4_IfcConstraint_type,
        IFC4X3_RC4_IfcContextDependentUnit_type,
        IFC4X3_RC4_IfcConversionBasedUnit_type,
        IFC4X3_RC4_IfcExternalInformation_type,
        IFC4X3_RC4_IfcExternalReference_type,
        IFC4X3_RC4_IfcMaterialDefinition_type,
        IFC4X3_RC4_IfcOrganization_type,
        IFC4X3_RC4_IfcPerson_type,
        IFC4X3_RC4_IfcPersonAndOrganization_type,
        IFC4X3_RC4_IfcPhysicalQuantity_type,
        IFC4X3_RC4_IfcProfileDef_type,
        IFC4X3_RC4_IfcPropertyAbstraction_type,
        IFC4X3_RC4_IfcShapeAspect_type,
        IFC4X3_RC4_IfcTimeSeries_type
    });
    IFC4X3_RC4_IfcTextFontSelect_type = new select_type(strings[2233], 1188, {
        IFC4X3_RC4_IfcExternallyDefinedTextFont_type,
        IFC4X3_RC4_IfcPreDefinedTextFont_type
    });
    IFC4X3_RC4_IfcValue_type = new select_type(strings[2234], 1259, {
        IFC4X3_RC4_IfcDerivedMeasureValue_type,
        IFC4X3_RC4_IfcMeasureValue_type,
        IFC4X3_RC4_IfcSimpleValue_type
    });
    IFC4X3_RC4_IfcAdvancedFace_type = new entity(strings[2235], false, 16, IFC4X3_RC4_IfcFaceSurface_type);
    IFC4X3_RC4_IfcAnnotationFillArea_type = new entity(strings[2236], false, 47, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcAsymmetricIShapeProfileDef_type = new entity(strings[2237], false, 63, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcAxis1Placement_type = new entity(strings[2238], false, 67, IFC4X3_RC4_IfcPlacement_type);
    IFC4X3_RC4_IfcAxis2Placement2D_type = new entity(strings[2239], false, 69, IFC4X3_RC4_IfcPlacement_type);
    IFC4X3_RC4_IfcAxis2Placement3D_type = new entity(strings[2240], false, 70, IFC4X3_RC4_IfcPlacement_type);
    IFC4X3_RC4_IfcAxis2PlacementLinear_type = new entity(strings[2241], false, 71, IFC4X3_RC4_IfcPlacement_type);
    IFC4X3_RC4_IfcBooleanResult_type = new entity(strings[2242], false, 92, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcBoundedSurface_type = new entity(strings[2243], true, 101, IFC4X3_RC4_IfcSurface_type);
    IFC4X3_RC4_IfcBoundingBox_type = new entity(strings[2244], false, 102, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcBoxedHalfSpace_type = new entity(strings[2245], false, 104, IFC4X3_RC4_IfcHalfSpaceSolid_type);
    IFC4X3_RC4_IfcCShapeProfileDef_type = new entity(strings[2246], false, 267, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcCartesianPoint_type = new entity(strings[2247], false, 147, IFC4X3_RC4_IfcPoint_type);
    IFC4X3_RC4_IfcCartesianPointList_type = new entity(strings[2248], true, 148, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcCartesianPointList2D_type = new entity(strings[2249], false, 149, IFC4X3_RC4_IfcCartesianPointList_type);
    IFC4X3_RC4_IfcCartesianPointList3D_type = new entity(strings[2250], false, 150, IFC4X3_RC4_IfcCartesianPointList_type);
    IFC4X3_RC4_IfcCartesianTransformationOperator_type = new entity(strings[2251], true, 151, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcCartesianTransformationOperator2D_type = new entity(strings[2252], false, 152, IFC4X3_RC4_IfcCartesianTransformationOperator_type);
    IFC4X3_RC4_IfcCartesianTransformationOperator2DnonUniform_type = new entity(strings[2253], false, 153, IFC4X3_RC4_IfcCartesianTransformationOperator2D_type);
    IFC4X3_RC4_IfcCartesianTransformationOperator3D_type = new entity(strings[2254], false, 154, IFC4X3_RC4_IfcCartesianTransformationOperator_type);
    IFC4X3_RC4_IfcCartesianTransformationOperator3DnonUniform_type = new entity(strings[2255], false, 155, IFC4X3_RC4_IfcCartesianTransformationOperator3D_type);
    IFC4X3_RC4_IfcCircleProfileDef_type = new entity(strings[2256], false, 166, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcClosedShell_type = new entity(strings[2257], false, 173, IFC4X3_RC4_IfcConnectedFaceSet_type);
    IFC4X3_RC4_IfcColourRgb_type = new entity(strings[2258], false, 180, IFC4X3_RC4_IfcColourSpecification_type);
    IFC4X3_RC4_IfcComplexProperty_type = new entity(strings[2259], false, 191, IFC4X3_RC4_IfcProperty_type);
    IFC4X3_RC4_IfcCompositeCurveSegment_type = new entity(strings[2260], false, 196, IFC4X3_RC4_IfcSegment_type);
    IFC4X3_RC4_IfcConstructionResourceType_type = new entity(strings[2261], true, 226, IFC4X3_RC4_IfcTypeResource_type);
    IFC4X3_RC4_IfcContext_type = new entity(strings[2262], true, 227, IFC4X3_RC4_IfcObjectDefinition_type);
    IFC4X3_RC4_IfcCrewResourceType_type = new entity(strings[2263], false, 262, IFC4X3_RC4_IfcConstructionResourceType_type);
    IFC4X3_RC4_IfcCsgPrimitive3D_type = new entity(strings[2264], true, 264, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcCsgSolid_type = new entity(strings[2265], false, 266, IFC4X3_RC4_IfcSolidModel_type);
    IFC4X3_RC4_IfcCurve_type = new entity(strings[2266], true, 273, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcCurveBoundedPlane_type = new entity(strings[2267], false, 274, IFC4X3_RC4_IfcBoundedSurface_type);
    IFC4X3_RC4_IfcCurveBoundedSurface_type = new entity(strings[2268], false, 275, IFC4X3_RC4_IfcBoundedSurface_type);
    IFC4X3_RC4_IfcCurveSegment_type = new entity(strings[2269], false, 281, IFC4X3_RC4_IfcSegment_type);
    IFC4X3_RC4_IfcDirection_type = new entity(strings[2270], false, 307, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcDirectrixCurveSweptAreaSolid_type = new entity(strings[2271], true, 309, IFC4X3_RC4_IfcSweptAreaSolid_type);
    IFC4X3_RC4_IfcDoorStyle_type = new entity(strings[2272], false, 343, IFC4X3_RC4_IfcTypeProduct_type);
    IFC4X3_RC4_IfcEdgeLoop_type = new entity(strings[2273], false, 370, IFC4X3_RC4_IfcLoop_type);
    IFC4X3_RC4_IfcElementQuantity_type = new entity(strings[2274], false, 406, IFC4X3_RC4_IfcQuantitySet_type);
    IFC4X3_RC4_IfcElementType_type = new entity(strings[2275], true, 407, IFC4X3_RC4_IfcTypeProduct_type);
    IFC4X3_RC4_IfcElementarySurface_type = new entity(strings[2276], true, 399, IFC4X3_RC4_IfcSurface_type);
    IFC4X3_RC4_IfcEllipseProfileDef_type = new entity(strings[2277], false, 409, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcEventType_type = new entity(strings[2278], false, 425, IFC4X3_RC4_IfcTypeProcess_type);
    IFC4X3_RC4_IfcExtrudedAreaSolid_type = new entity(strings[2279], false, 437, IFC4X3_RC4_IfcSweptAreaSolid_type);
    IFC4X3_RC4_IfcExtrudedAreaSolidTapered_type = new entity(strings[2280], false, 438, IFC4X3_RC4_IfcExtrudedAreaSolid_type);
    IFC4X3_RC4_IfcFaceBasedSurfaceModel_type = new entity(strings[2281], false, 440, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcFillAreaStyleHatching_type = new entity(strings[2282], false, 462, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcFillAreaStyleTiles_type = new entity(strings[2283], false, 463, IFC4X3_RC4_IfcGeometricRepresentationItem_type);
    IFC4X3_RC4_IfcFixedReferenceSweptAreaSolid_type = new entity(strings[2284], false, 471, IFC4X3_RC4_IfcDirectrixCurveSweptAreaSolid_type);
    IFC4X3_RC4_IfcFurnishingElementType_type = new entity(strings[2285], false, 502, IFC4X3_RC4_IfcElementType_type);
    IFC4X3_RC4_IfcFurnitureType_type = new entity(strings[2286], false, 504, IFC4X3_RC4_IfcFurnishingElementType_type);
    IFC4X3_RC4_IfcGeographicElementType_type = new entity(strings[2287], false, 507, IFC4X3_RC4_IfcElementType_type);
    IFC4X3_RC4_IfcGeometricCurveSet_type = new entity(strings[2288], false, 509, IFC4X3_RC4_IfcGeometricSet_type);
    IFC4X3_RC4_IfcIShapeProfileDef_type = new entity(strings[2289], false, 567, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcIndexedPolygonalFace_type = new entity(strings[2290], false, 549, IFC4X3_RC4_IfcTessellatedItem_type);
    IFC4X3_RC4_IfcIndexedPolygonalFaceWithVoids_type = new entity(strings[2291], false, 550, IFC4X3_RC4_IfcIndexedPolygonalFace_type);
    IFC4X3_RC4_IfcLShapeProfileDef_type = new entity(strings[2292], false, 622, IFC4X3_RC4_IfcParameterizedProfileDef_type);
    IFC4X3_RC4_IfcLaborResourceType_type = new entity(strings[2293], false, 578, IFC4X3_RC4_IfcConstructionResourceType_type);
    IFC4X3_RC4_IfcLine_type = new entity(strings[2294], false, 605, IFC4X3_RC4_IfcCurve_type);
    IFC4X3_RC4_IfcManifoldSolidBrep_type = new entity(strings[2295], true, 628, IFC4X3_RC4_IfcSolidModel_type);
    IFC4X3_RC4_IfcObject_type = new entity(strings[2296], true, 702, IFC4X3_RC4_IfcObjectDefinition_type);
    IFC4X3_RC4_IfcOffsetCurve_type = new entity(strings[2297], true, 711, IFC4X3_RC4_IfcCurve_type);
    IFC4X3_RC4_IfcOffsetCurve2D_type = new entity(strings[2298], false, 712, IFC4X3_RC4_IfcOffsetCurve_type);
    IFC4X3_RC4_IfcOffsetCurve3D_type = new entity(strings[2299], false, 713, IFC4X3_RC4_IfcOffsetCurve_type);
    IFC4X3_RC4_IfcOffsetCurveByDistances_type = new entity(strings[2300], false, 714, IFC4X3_RC4_IfcOffsetCurve_type);
    IFC4X3_RC4_IfcPcurve_type = new entity(strings[2301], false, 734, IFC4X3_RC4_IfcCurve_type);
    IFC4X3_RC4_IfcPlanarBox_type = new entity(strings[2302], false, 760, IFC4X3_RC4_IfcPlanarExtent_type);
    IFC4X3_RC4_IfcPlane_type = new entity(strings[2303], false, 763, IFC4X3_RC4_IfcElementarySurface_type);
    IFC4X3_RC4_IfcPolynomialCurve_type = new entity(strings[2304], false, 779, IFC4X3_RC4_IfcCurve_type);
    IFC4X3_RC4_IfcPreDefinedColour_type = new entity(strings[2305], true, 788, IFC4X3_RC4_IfcPreDefinedItem_type);
    IFC4X3_RC4_IfcPreDefinedCurveFont_type = new entity(strings[2306], true, 789, IFC4X3_RC4_IfcPreDefinedItem_type);
    IFC4X3_RC4_IfcPreDefinedPropertySet_type = new entity(strings[2307], true, 792, IFC4X3_RC4_IfcPropertySetDefinition_type);
    IFC4X3_RC4_IfcProcedureType_type = new entity(strings[2308], false, 802, IFC4X3_RC4_IfcTypeProcess_type);
    IFC4X3_RC4_IfcProcess_type = new entity(strings[2309], true, 804, IFC4X3_RC4_IfcObject_type);
    IFC4X3_RC4_IfcProduct_type = new entity(strings[2310], true, 806, IFC4X3_RC4_IfcObject_type);
    IFC4X3_RC4_IfcProject_type = new entity(strings[2311], false, 814, IFC4X3_RC4_IfcContext_type);
    IFC4X3_RC4_IfcProjectLibrary_type = new entity(strings[2312], false, 819, IFC4X3_RC4_IfcContext_type);
    IFC4X3_RC4_IfcPropertyBoundedValue_type = new entity(strings[2313], false, 824, IFC4X3_RC4_IfcSimpleProperty_type);
    IFC4X3_RC4_IfcPropertyEnumeratedValue_type = new entity(strings[2314], false, 827, IFC4X3_RC4_IfcSimpleProperty_type);
    IFC4X3_RC4_IfcPropertyListValue_type = new entity(strings[2315], false, 829, IFC4X3_RC4_IfcSimpleProperty_type);
    IFC4X3_RC4_IfcPropertyReferenceValue_type = new entity(strings[2316], false, 830, IFC4X3_RC4_IfcSimpleProperty_type);
    IFC4X3_RC4_IfcPropertySet_type = new entity(strings[2317], false, 831, IFC4X3_RC4_IfcPropertySetDefinition_type);
    IFC4X3_RC4_IfcPropertySetTemplate_type = new entity(strings[2318], false, 835, IFC4X3_RC4_IfcPropertyTemplateDefinition_type);
    IFC4X3_RC4_IfcPropertySingleValue_type = new entity(strings[2319], false, 837, IFC4X3_RC4_IfcSimpleProperty_type);
    IFC4X3_RC4_IfcPropertyTableValue_type = new entity(strings[2320], false, 838, IFC4X3_RC4_IfcSimpleProperty_type);
    IFC4X3_RC4_IfcPropertyTemplate_type = new entity(strings[2321], true, 839, IFC4X3_RC4_IfcPropertyTemplateDefinition_type);
    IFC4X3_RC4_IfcProxy_type = new entity(strings[2322], false, 847, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcRectangleHollowProfileDef_type = new entity(strings[2323], false, 878, IFC4X3_RC4_IfcRectangleProfileDef_type);
    IFC4X3_RC4_IfcRectangularPyramid_type = new entity(strings[2324], false, 880, IFC4X3_RC4_IfcCsgPrimitive3D_type);
    IFC4X3_RC4_IfcRectangularTrimmedSurface_type = new entity(strings[2325], false, 881, IFC4X3_RC4_IfcBoundedSurface_type);
    IFC4X3_RC4_IfcReinforcementDefinitionProperties_type = new entity(strings[2326], false, 892, IFC4X3_RC4_IfcPreDefinedPropertySet_type);
    IFC4X3_RC4_IfcRelAssigns_type = new entity(strings[2327], true, 905, IFC4X3_RC4_IfcRelationship_type);
    IFC4X3_RC4_IfcRelAssignsToActor_type = new entity(strings[2328], false, 906, IFC4X3_RC4_IfcRelAssigns_type);
    IFC4X3_RC4_IfcRelAssignsToControl_type = new entity(strings[2329], false, 907, IFC4X3_RC4_IfcRelAssigns_type);
    IFC4X3_RC4_IfcRelAssignsToGroup_type = new entity(strings[2330], false, 908, IFC4X3_RC4_IfcRelAssigns_type);
    IFC4X3_RC4_IfcRelAssignsToGroupByFactor_type = new entity(strings[2331], false, 909, IFC4X3_RC4_IfcRelAssignsToGroup_type);
    IFC4X3_RC4_IfcRelAssignsToProcess_type = new entity(strings[2332], false, 910, IFC4X3_RC4_IfcRelAssigns_type);
    IFC4X3_RC4_IfcRelAssignsToProduct_type = new entity(strings[2333], false, 911, IFC4X3_RC4_IfcRelAssigns_type);
    IFC4X3_RC4_IfcRelAssignsToResource_type = new entity(strings[2334], false, 912, IFC4X3_RC4_IfcRelAssigns_type);
    IFC4X3_RC4_IfcRelAssociates_type = new entity(strings[2335], true, 913, IFC4X3_RC4_IfcRelationship_type);
    IFC4X3_RC4_IfcRelAssociatesApproval_type = new entity(strings[2336], false, 914, IFC4X3_RC4_IfcRelAssociates_type);
    IFC4X3_RC4_IfcRelAssociatesClassification_type = new entity(strings[2337], false, 915, IFC4X3_RC4_IfcRelAssociates_type);
    IFC4X3_RC4_IfcRelAssociatesConstraint_type = new entity(strings[2338], false, 916, IFC4X3_RC4_IfcRelAssociates_type);
    IFC4X3_RC4_IfcRelAssociatesDocument_type = new entity(strings[2339], false, 917, IFC4X3_RC4_IfcRelAssociates_type);
    IFC4X3_RC4_IfcRelAssociatesLibrary_type = new entity(strings[2340], false, 918, IFC4X3_RC4_IfcRelAssociates_type);
    IFC4X3_RC4_IfcRelAssociatesMaterial_type = new entity(strings[2341], false, 919, IFC4X3_RC4_IfcRelAssociates_type);
    IFC4X3_RC4_IfcRelAssociatesProfileDef_type = new entity(strings[2342], false, 920, IFC4X3_RC4_IfcRelAssociates_type);
    IFC4X3_RC4_IfcRelConnects_type = new entity(strings[2343], true, 922, IFC4X3_RC4_IfcRelationship_type);
    IFC4X3_RC4_IfcRelConnectsElements_type = new entity(strings[2344], false, 923, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelConnectsPathElements_type = new entity(strings[2345], false, 924, IFC4X3_RC4_IfcRelConnectsElements_type);
    IFC4X3_RC4_IfcRelConnectsPortToElement_type = new entity(strings[2346], false, 926, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelConnectsPorts_type = new entity(strings[2347], false, 925, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelConnectsStructuralActivity_type = new entity(strings[2348], false, 927, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelConnectsStructuralMember_type = new entity(strings[2349], false, 928, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelConnectsWithEccentricity_type = new entity(strings[2350], false, 929, IFC4X3_RC4_IfcRelConnectsStructuralMember_type);
    IFC4X3_RC4_IfcRelConnectsWithRealizingElements_type = new entity(strings[2351], false, 930, IFC4X3_RC4_IfcRelConnectsElements_type);
    IFC4X3_RC4_IfcRelContainedInSpatialStructure_type = new entity(strings[2352], false, 931, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelCoversBldgElements_type = new entity(strings[2353], false, 932, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelCoversSpaces_type = new entity(strings[2354], false, 933, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelDeclares_type = new entity(strings[2355], false, 934, IFC4X3_RC4_IfcRelationship_type);
    IFC4X3_RC4_IfcRelDecomposes_type = new entity(strings[2356], true, 935, IFC4X3_RC4_IfcRelationship_type);
    IFC4X3_RC4_IfcRelDefines_type = new entity(strings[2357], true, 936, IFC4X3_RC4_IfcRelationship_type);
    IFC4X3_RC4_IfcRelDefinesByObject_type = new entity(strings[2358], false, 937, IFC4X3_RC4_IfcRelDefines_type);
    IFC4X3_RC4_IfcRelDefinesByProperties_type = new entity(strings[2359], false, 938, IFC4X3_RC4_IfcRelDefines_type);
    IFC4X3_RC4_IfcRelDefinesByTemplate_type = new entity(strings[2360], false, 939, IFC4X3_RC4_IfcRelDefines_type);
    IFC4X3_RC4_IfcRelDefinesByType_type = new entity(strings[2361], false, 940, IFC4X3_RC4_IfcRelDefines_type);
    IFC4X3_RC4_IfcRelFillsElement_type = new entity(strings[2362], false, 941, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelFlowControlElements_type = new entity(strings[2363], false, 942, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelInterferesElements_type = new entity(strings[2364], false, 943, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelNests_type = new entity(strings[2365], false, 944, IFC4X3_RC4_IfcRelDecomposes_type);
    IFC4X3_RC4_IfcRelPositions_type = new entity(strings[2366], false, 945, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelProjectsElement_type = new entity(strings[2367], false, 946, IFC4X3_RC4_IfcRelDecomposes_type);
    IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type = new entity(strings[2368], false, 947, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelSequence_type = new entity(strings[2369], false, 948, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelServicesBuildings_type = new entity(strings[2370], false, 949, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelSpaceBoundary_type = new entity(strings[2371], false, 950, IFC4X3_RC4_IfcRelConnects_type);
    IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type = new entity(strings[2372], false, 951, IFC4X3_RC4_IfcRelSpaceBoundary_type);
    IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type = new entity(strings[2373], false, 952, IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type);
    IFC4X3_RC4_IfcRelVoidsElement_type = new entity(strings[2374], false, 953, IFC4X3_RC4_IfcRelDecomposes_type);
    IFC4X3_RC4_IfcReparametrisedCompositeCurveSegment_type = new entity(strings[2375], false, 954, IFC4X3_RC4_IfcCompositeCurveSegment_type);
    IFC4X3_RC4_IfcResource_type = new entity(strings[2376], true, 959, IFC4X3_RC4_IfcObject_type);
    IFC4X3_RC4_IfcRevolvedAreaSolid_type = new entity(strings[2377], false, 966, IFC4X3_RC4_IfcSweptAreaSolid_type);
    IFC4X3_RC4_IfcRevolvedAreaSolidTapered_type = new entity(strings[2378], false, 967, IFC4X3_RC4_IfcRevolvedAreaSolid_type);
    IFC4X3_RC4_IfcRightCircularCone_type = new entity(strings[2379], false, 968, IFC4X3_RC4_IfcCsgPrimitive3D_type);
    IFC4X3_RC4_IfcRightCircularCylinder_type = new entity(strings[2380], false, 969, IFC4X3_RC4_IfcCsgPrimitive3D_type);
    IFC4X3_RC4_IfcSectionedSolid_type = new entity(strings[2381], true, 990, IFC4X3_RC4_IfcSolidModel_type);
    IFC4X3_RC4_IfcSectionedSolidHorizontal_type = new entity(strings[2382], false, 991, IFC4X3_RC4_IfcSectionedSolid_type);
    IFC4X3_RC4_IfcSectionedSurface_type = new entity(strings[2383], false, 993, IFC4X3_RC4_IfcSurface_type);
    IFC4X3_RC4_IfcSimplePropertyTemplate_type = new entity(strings[2384], false, 1022, IFC4X3_RC4_IfcPropertyTemplate_type);
    IFC4X3_RC4_IfcSpatialElement_type = new entity(strings[2385], true, 1055, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcSpatialElementType_type = new entity(strings[2386], true, 1056, IFC4X3_RC4_IfcTypeProduct_type);
    IFC4X3_RC4_IfcSpatialStructureElement_type = new entity(strings[2387], true, 1058, IFC4X3_RC4_IfcSpatialElement_type);
    IFC4X3_RC4_IfcSpatialStructureElementType_type = new entity(strings[2388], true, 1059, IFC4X3_RC4_IfcSpatialElementType_type);
    IFC4X3_RC4_IfcSpatialZone_type = new entity(strings[2389], false, 1060, IFC4X3_RC4_IfcSpatialElement_type);
    IFC4X3_RC4_IfcSpatialZoneType_type = new entity(strings[2390], false, 1061, IFC4X3_RC4_IfcSpatialElementType_type);
    IFC4X3_RC4_IfcSphere_type = new entity(strings[2391], false, 1067, IFC4X3_RC4_IfcCsgPrimitive3D_type);
    IFC4X3_RC4_IfcSphericalSurface_type = new entity(strings[2392], false, 1068, IFC4X3_RC4_IfcElementarySurface_type);
    IFC4X3_RC4_IfcSpiral_type = new entity(strings[2393], true, 1069, IFC4X3_RC4_IfcCurve_type);
    IFC4X3_RC4_IfcStructuralActivity_type = new entity(strings[2394], true, 1081, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcStructuralItem_type = new entity(strings[2395], true, 1093, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcStructuralMember_type = new entity(strings[2396], true, 1108, IFC4X3_RC4_IfcStructuralItem_type);
    IFC4X3_RC4_IfcStructuralReaction_type = new entity(strings[2397], true, 1113, IFC4X3_RC4_IfcStructuralActivity_type);
    IFC4X3_RC4_IfcStructuralSurfaceMember_type = new entity(strings[2398], false, 1118, IFC4X3_RC4_IfcStructuralMember_type);
    IFC4X3_RC4_IfcStructuralSurfaceMemberVarying_type = new entity(strings[2399], false, 1120, IFC4X3_RC4_IfcStructuralSurfaceMember_type);
    IFC4X3_RC4_IfcStructuralSurfaceReaction_type = new entity(strings[2400], false, 1121, IFC4X3_RC4_IfcStructuralReaction_type);
    IFC4X3_RC4_IfcSubContractResourceType_type = new entity(strings[2401], false, 1126, IFC4X3_RC4_IfcConstructionResourceType_type);
    IFC4X3_RC4_IfcSurfaceCurve_type = new entity(strings[2402], false, 1130, IFC4X3_RC4_IfcCurve_type);
    IFC4X3_RC4_IfcSurfaceCurveSweptAreaSolid_type = new entity(strings[2403], false, 1131, IFC4X3_RC4_IfcDirectrixCurveSweptAreaSolid_type);
    IFC4X3_RC4_IfcSurfaceOfLinearExtrusion_type = new entity(strings[2404], false, 1134, IFC4X3_RC4_IfcSweptSurface_type);
    IFC4X3_RC4_IfcSurfaceOfRevolution_type = new entity(strings[2405], false, 1135, IFC4X3_RC4_IfcSweptSurface_type);
    IFC4X3_RC4_IfcSystemFurnitureElementType_type = new entity(strings[2406], false, 1156, IFC4X3_RC4_IfcFurnishingElementType_type);
    IFC4X3_RC4_IfcTask_type = new entity(strings[2407], false, 1164, IFC4X3_RC4_IfcProcess_type);
    IFC4X3_RC4_IfcTaskType_type = new entity(strings[2408], false, 1168, IFC4X3_RC4_IfcTypeProcess_type);
    IFC4X3_RC4_IfcTessellatedFaceSet_type = new entity(strings[2409], true, 1182, IFC4X3_RC4_IfcTessellatedItem_type);
    IFC4X3_RC4_IfcThirdOrderPolynomialSpiral_type = new entity(strings[2410], false, 1208, IFC4X3_RC4_IfcSpiral_type);
    IFC4X3_RC4_IfcToroidalSurface_type = new entity(strings[2411], false, 1219, IFC4X3_RC4_IfcElementarySurface_type);
    IFC4X3_RC4_IfcTransportElementType_type = new entity(strings[2412], false, 1232, IFC4X3_RC4_IfcElementType_type);
    IFC4X3_RC4_IfcTriangulatedFaceSet_type = new entity(strings[2413], false, 1235, IFC4X3_RC4_IfcTessellatedFaceSet_type);
    IFC4X3_RC4_IfcTriangulatedIrregularNetwork_type = new entity(strings[2414], false, 1236, IFC4X3_RC4_IfcTriangulatedFaceSet_type);
    IFC4X3_RC4_IfcWindowLiningProperties_type = new entity(strings[2415], false, 1295, IFC4X3_RC4_IfcPreDefinedPropertySet_type);
    IFC4X3_RC4_IfcWindowPanelProperties_type = new entity(strings[2416], false, 1298, IFC4X3_RC4_IfcPreDefinedPropertySet_type);
    IFC4X3_RC4_IfcAppliedValueSelect_type = new select_type(strings[2417], 51, {
        IFC4X3_RC4_IfcMeasureWithUnit_type,
        IFC4X3_RC4_IfcReference_type,
        IFC4X3_RC4_IfcValue_type
    });
    IFC4X3_RC4_IfcAxis2Placement_type = new select_type(strings[2418], 68, {
        IFC4X3_RC4_IfcAxis2Placement2D_type,
        IFC4X3_RC4_IfcAxis2Placement3D_type
    });
    IFC4X3_RC4_IfcBooleanOperand_type = new select_type(strings[2419], 90, {
        IFC4X3_RC4_IfcBooleanResult_type,
        IFC4X3_RC4_IfcCsgPrimitive3D_type,
        IFC4X3_RC4_IfcHalfSpaceSolid_type,
        IFC4X3_RC4_IfcSolidModel_type,
        IFC4X3_RC4_IfcTessellatedFaceSet_type
    });
    IFC4X3_RC4_IfcColour_type = new select_type(strings[2420], 178, {
        IFC4X3_RC4_IfcColourSpecification_type,
        IFC4X3_RC4_IfcPreDefinedColour_type
    });
    IFC4X3_RC4_IfcColourOrFactor_type = new select_type(strings[2421], 179, {
        IFC4X3_RC4_IfcColourRgb_type,
        IFC4X3_RC4_IfcNormalisedRatioMeasure_type
    });
    IFC4X3_RC4_IfcCsgSelect_type = new select_type(strings[2422], 265, {
        IFC4X3_RC4_IfcBooleanResult_type,
        IFC4X3_RC4_IfcCsgPrimitive3D_type
    });
    IFC4X3_RC4_IfcCurveStyleFontSelect_type = new select_type(strings[2423], 286, {
        IFC4X3_RC4_IfcCurveStyleFont_type,
        IFC4X3_RC4_IfcPreDefinedCurveFont_type
    });
    IFC4X3_RC4_IfcFillStyleSelect_type = new select_type(strings[2424], 464, {
        IFC4X3_RC4_IfcColour_type,
        IFC4X3_RC4_IfcExternallyDefinedHatchStyle_type,
        IFC4X3_RC4_IfcFillAreaStyleHatching_type,
        IFC4X3_RC4_IfcFillAreaStyleTiles_type
    });
    IFC4X3_RC4_IfcGeometricSetSelect_type = new select_type(strings[2425], 515, {
        IFC4X3_RC4_IfcCurve_type,
        IFC4X3_RC4_IfcPoint_type,
        IFC4X3_RC4_IfcSurface_type
    });
    IFC4X3_RC4_IfcGridPlacementDirectionSelect_type = new select_type(strings[2426], 527, {
        IFC4X3_RC4_IfcDirection_type,
        IFC4X3_RC4_IfcVirtualGridIntersection_type
    });
    IFC4X3_RC4_IfcMetricValueSelect_type = new select_type(strings[2427], 671, {
        IFC4X3_RC4_IfcAppliedValue_type,
        IFC4X3_RC4_IfcMeasureWithUnit_type,
        IFC4X3_RC4_IfcReference_type,
        IFC4X3_RC4_IfcTable_type,
        IFC4X3_RC4_IfcTimeSeries_type,
        IFC4X3_RC4_IfcValue_type
    });
    IFC4X3_RC4_IfcProcessSelect_type = new select_type(strings[2428], 805, {
        IFC4X3_RC4_IfcProcess_type,
        IFC4X3_RC4_IfcTypeProcess_type
    });
    IFC4X3_RC4_IfcProductSelect_type = new select_type(strings[2429], 810, {
        IFC4X3_RC4_IfcProduct_type,
        IFC4X3_RC4_IfcTypeProduct_type
    });
    IFC4X3_RC4_IfcPropertySetDefinitionSelect_type = new select_type(strings[2430], 833, {
        IFC4X3_RC4_IfcPropertySetDefinition_type,
        IFC4X3_RC4_IfcPropertySetDefinitionSet_type
    });
    IFC4X3_RC4_IfcResourceSelect_type = new select_type(strings[2431], 964, {
        IFC4X3_RC4_IfcResource_type,
        IFC4X3_RC4_IfcTypeResource_type
    });
    IFC4X3_RC4_IfcShell_type = new select_type(strings[2432], 1013, {
        IFC4X3_RC4_IfcClosedShell_type,
        IFC4X3_RC4_IfcOpenShell_type
    });
    IFC4X3_RC4_IfcSolidOrShell_type = new select_type(strings[2433], 1042, {
        IFC4X3_RC4_IfcClosedShell_type,
        IFC4X3_RC4_IfcSolidModel_type
    });
    IFC4X3_RC4_IfcSurfaceOrFaceSurface_type = new select_type(strings[2434], 1136, {
        IFC4X3_RC4_IfcFaceBasedSurfaceModel_type,
        IFC4X3_RC4_IfcFaceSurface_type,
        IFC4X3_RC4_IfcSurface_type
    });
    IFC4X3_RC4_IfcTrimmingSelect_type = new select_type(strings[2435], 1239, {
        IFC4X3_RC4_IfcCartesianPoint_type,
        IFC4X3_RC4_IfcParameterValue_type
    });
    IFC4X3_RC4_IfcVectorOrDirection_type = new select_type(strings[2436], 1265, {
        IFC4X3_RC4_IfcDirection_type,
        IFC4X3_RC4_IfcVector_type
    });
    IFC4X3_RC4_IfcActor_type = new entity(strings[2437], false, 6, IFC4X3_RC4_IfcObject_type);
    IFC4X3_RC4_IfcAdvancedBrep_type = new entity(strings[2438], false, 14, IFC4X3_RC4_IfcManifoldSolidBrep_type);
    IFC4X3_RC4_IfcAdvancedBrepWithVoids_type = new entity(strings[2439], false, 15, IFC4X3_RC4_IfcAdvancedBrep_type);
    IFC4X3_RC4_IfcAnnotation_type = new entity(strings[2440], false, 46, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcBSplineSurface_type = new entity(strings[2441], true, 111, IFC4X3_RC4_IfcBoundedSurface_type);
    IFC4X3_RC4_IfcBSplineSurfaceWithKnots_type = new entity(strings[2442], false, 113, IFC4X3_RC4_IfcBSplineSurface_type);
    IFC4X3_RC4_IfcBlock_type = new entity(strings[2443], false, 84, IFC4X3_RC4_IfcCsgPrimitive3D_type);
    IFC4X3_RC4_IfcBooleanClippingResult_type = new entity(strings[2444], false, 89, IFC4X3_RC4_IfcBooleanResult_type);
    IFC4X3_RC4_IfcBoundedCurve_type = new entity(strings[2445], true, 100, IFC4X3_RC4_IfcCurve_type);
    IFC4X3_RC4_IfcBuildingStorey_type = new entity(strings[2446], false, 121, IFC4X3_RC4_IfcSpatialStructureElement_type);
    IFC4X3_RC4_IfcBuiltElementType_type = new entity(strings[2447], false, 125, IFC4X3_RC4_IfcElementType_type);
    IFC4X3_RC4_IfcChimneyType_type = new entity(strings[2448], false, 162, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcCircleHollowProfileDef_type = new entity(strings[2449], false, 165, IFC4X3_RC4_IfcCircleProfileDef_type);
    IFC4X3_RC4_IfcCivilElementType_type = new entity(strings[2450], false, 168, IFC4X3_RC4_IfcElementType_type);
    IFC4X3_RC4_IfcClothoid_type = new entity(strings[2451], false, 174, IFC4X3_RC4_IfcSpiral_type);
    IFC4X3_RC4_IfcColumnType_type = new entity(strings[2452], false, 185, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcComplexPropertyTemplate_type = new entity(strings[2453], false, 192, IFC4X3_RC4_IfcPropertyTemplate_type);
    IFC4X3_RC4_IfcCompositeCurve_type = new entity(strings[2454], false, 194, IFC4X3_RC4_IfcBoundedCurve_type);
    IFC4X3_RC4_IfcCompositeCurveOnSurface_type = new entity(strings[2455], false, 195, IFC4X3_RC4_IfcCompositeCurve_type);
    IFC4X3_RC4_IfcConic_type = new entity(strings[2456], true, 205, IFC4X3_RC4_IfcCurve_type);
    IFC4X3_RC4_IfcConstructionEquipmentResourceType_type = new entity(strings[2457], false, 217, IFC4X3_RC4_IfcConstructionResourceType_type);
    IFC4X3_RC4_IfcConstructionMaterialResourceType_type = new entity(strings[2458], false, 220, IFC4X3_RC4_IfcConstructionResourceType_type);
    IFC4X3_RC4_IfcConstructionProductResourceType_type = new entity(strings[2459], false, 223, IFC4X3_RC4_IfcConstructionResourceType_type);
    IFC4X3_RC4_IfcConstructionResource_type = new entity(strings[2460], true, 225, IFC4X3_RC4_IfcResource_type);
    IFC4X3_RC4_IfcControl_type = new entity(strings[2461], true, 230, IFC4X3_RC4_IfcObject_type);
    IFC4X3_RC4_IfcCosine_type = new entity(strings[2462], false, 248, IFC4X3_RC4_IfcSpiral_type);
    IFC4X3_RC4_IfcCostItem_type = new entity(strings[2463], false, 249, IFC4X3_RC4_IfcControl_type);
    IFC4X3_RC4_IfcCostSchedule_type = new entity(strings[2464], false, 251, IFC4X3_RC4_IfcControl_type);
    IFC4X3_RC4_IfcCourseType_type = new entity(strings[2465], false, 256, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcCoveringType_type = new entity(strings[2466], false, 259, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcCrewResource_type = new entity(strings[2467], false, 261, IFC4X3_RC4_IfcConstructionResource_type);
    IFC4X3_RC4_IfcCurtainWallType_type = new entity(strings[2468], false, 270, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcCylindricalSurface_type = new entity(strings[2469], false, 287, IFC4X3_RC4_IfcElementarySurface_type);
    IFC4X3_RC4_IfcDeepFoundationType_type = new entity(strings[2470], false, 297, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcDirectrixDerivedReferenceSweptAreaSolid_type = new entity(strings[2471], false, 310, IFC4X3_RC4_IfcFixedReferenceSweptAreaSolid_type);
    IFC4X3_RC4_IfcDistributionElementType_type = new entity(strings[2472], false, 324, IFC4X3_RC4_IfcElementType_type);
    IFC4X3_RC4_IfcDistributionFlowElementType_type = new entity(strings[2473], true, 326, IFC4X3_RC4_IfcDistributionElementType_type);
    IFC4X3_RC4_IfcDoorLiningProperties_type = new entity(strings[2474], false, 338, IFC4X3_RC4_IfcPreDefinedPropertySet_type);
    IFC4X3_RC4_IfcDoorPanelProperties_type = new entity(strings[2475], false, 341, IFC4X3_RC4_IfcPreDefinedPropertySet_type);
    IFC4X3_RC4_IfcDoorType_type = new entity(strings[2476], false, 346, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcDraughtingPreDefinedColour_type = new entity(strings[2477], false, 350, IFC4X3_RC4_IfcPreDefinedColour_type);
    IFC4X3_RC4_IfcDraughtingPreDefinedCurveFont_type = new entity(strings[2478], false, 351, IFC4X3_RC4_IfcPreDefinedCurveFont_type);
    IFC4X3_RC4_IfcElement_type = new entity(strings[2479], true, 398, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcElementAssembly_type = new entity(strings[2480], false, 400, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcElementAssemblyType_type = new entity(strings[2481], false, 401, IFC4X3_RC4_IfcElementType_type);
    IFC4X3_RC4_IfcElementComponent_type = new entity(strings[2482], true, 403, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcElementComponentType_type = new entity(strings[2483], true, 404, IFC4X3_RC4_IfcElementType_type);
    IFC4X3_RC4_IfcEllipse_type = new entity(strings[2484], false, 408, IFC4X3_RC4_IfcConic_type);
    IFC4X3_RC4_IfcEnergyConversionDeviceType_type = new entity(strings[2485], true, 411, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcEngineType_type = new entity(strings[2486], false, 414, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcEvaporativeCoolerType_type = new entity(strings[2487], false, 417, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcEvaporatorType_type = new entity(strings[2488], false, 420, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcEvent_type = new entity(strings[2489], false, 422, IFC4X3_RC4_IfcProcess_type);
    IFC4X3_RC4_IfcExternalSpatialStructureElement_type = new entity(strings[2490], true, 436, IFC4X3_RC4_IfcSpatialElement_type);
    IFC4X3_RC4_IfcFacetedBrep_type = new entity(strings[2491], false, 444, IFC4X3_RC4_IfcManifoldSolidBrep_type);
    IFC4X3_RC4_IfcFacetedBrepWithVoids_type = new entity(strings[2492], false, 445, IFC4X3_RC4_IfcFacetedBrep_type);
    IFC4X3_RC4_IfcFacility_type = new entity(strings[2493], false, 446, IFC4X3_RC4_IfcSpatialStructureElement_type);
    IFC4X3_RC4_IfcFacilityPart_type = new entity(strings[2494], false, 447, IFC4X3_RC4_IfcSpatialStructureElement_type);
    IFC4X3_RC4_IfcFastener_type = new entity(strings[2495], false, 455, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcFastenerType_type = new entity(strings[2496], false, 456, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcFeatureElement_type = new entity(strings[2497], true, 458, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcFeatureElementAddition_type = new entity(strings[2498], true, 459, IFC4X3_RC4_IfcFeatureElement_type);
    IFC4X3_RC4_IfcFeatureElementSubtraction_type = new entity(strings[2499], true, 460, IFC4X3_RC4_IfcFeatureElement_type);
    IFC4X3_RC4_IfcFlowControllerType_type = new entity(strings[2500], true, 473, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcFlowFittingType_type = new entity(strings[2501], true, 476, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcFlowMeterType_type = new entity(strings[2502], false, 481, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcFlowMovingDeviceType_type = new entity(strings[2503], true, 484, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcFlowSegmentType_type = new entity(strings[2504], true, 486, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcFlowStorageDeviceType_type = new entity(strings[2505], true, 488, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcFlowTerminalType_type = new entity(strings[2506], true, 490, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcFlowTreatmentDeviceType_type = new entity(strings[2507], true, 492, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcFootingType_type = new entity(strings[2508], false, 497, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcFurnishingElement_type = new entity(strings[2509], false, 501, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcFurniture_type = new entity(strings[2510], false, 503, IFC4X3_RC4_IfcFurnishingElement_type);
    IFC4X3_RC4_IfcGeographicElement_type = new entity(strings[2511], false, 506, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcGeotechnicalElement_type = new entity(strings[2512], true, 519, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcGeotechnicalStratum_type = new entity(strings[2513], true, 520, IFC4X3_RC4_IfcGeotechnicalElement_type);
    IFC4X3_RC4_IfcGradientCurve_type = new entity(strings[2514], false, 523, IFC4X3_RC4_IfcCompositeCurve_type);
    IFC4X3_RC4_IfcGroup_type = new entity(strings[2515], false, 529, IFC4X3_RC4_IfcObject_type);
    IFC4X3_RC4_IfcHeatExchangerType_type = new entity(strings[2516], false, 533, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcHumidifierType_type = new entity(strings[2517], false, 538, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcImpactProtectionDevice_type = new entity(strings[2518], false, 543, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcImpactProtectionDeviceType_type = new entity(strings[2519], false, 544, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcIndexedPolyCurve_type = new entity(strings[2520], false, 548, IFC4X3_RC4_IfcBoundedCurve_type);
    IFC4X3_RC4_IfcInterceptorType_type = new entity(strings[2521], false, 557, IFC4X3_RC4_IfcFlowTreatmentDeviceType_type);
    IFC4X3_RC4_IfcIntersectionCurve_type = new entity(strings[2522], false, 561, IFC4X3_RC4_IfcSurfaceCurve_type);
    IFC4X3_RC4_IfcInventory_type = new entity(strings[2523], false, 562, IFC4X3_RC4_IfcGroup_type);
    IFC4X3_RC4_IfcJunctionBoxType_type = new entity(strings[2524], false, 570, IFC4X3_RC4_IfcFlowFittingType_type);
    IFC4X3_RC4_IfcKerbType_type = new entity(strings[2525], false, 573, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcLaborResource_type = new entity(strings[2526], false, 577, IFC4X3_RC4_IfcConstructionResource_type);
    IFC4X3_RC4_IfcLampType_type = new entity(strings[2527], false, 582, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcLightFixtureType_type = new entity(strings[2528], false, 596, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcLinearElement_type = new entity(strings[2529], false, 606, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcLiquidTerminalType_type = new entity(strings[2530], false, 615, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcMarineFacility_type = new entity(strings[2531], false, 631, IFC4X3_RC4_IfcFacility_type);
    IFC4X3_RC4_IfcMechanicalFastener_type = new entity(strings[2532], false, 660, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcMechanicalFastenerType_type = new entity(strings[2533], false, 661, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcMedicalDeviceType_type = new entity(strings[2534], false, 664, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcMemberType_type = new entity(strings[2535], false, 668, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcMobileTelecommunicationsApplianceType_type = new entity(strings[2536], false, 674, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcMooringDeviceType_type = new entity(strings[2537], false, 690, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcMotorConnectionType_type = new entity(strings[2538], false, 693, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcNavigationElementType_type = new entity(strings[2539], false, 697, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcOccupant_type = new entity(strings[2540], false, 709, IFC4X3_RC4_IfcActor_type);
    IFC4X3_RC4_IfcOpeningElement_type = new entity(strings[2541], false, 716, IFC4X3_RC4_IfcFeatureElementSubtraction_type);
    IFC4X3_RC4_IfcOpeningStandardCase_type = new entity(strings[2542], false, 718, IFC4X3_RC4_IfcOpeningElement_type);
    IFC4X3_RC4_IfcOutletType_type = new entity(strings[2543], false, 725, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcPavementType_type = new entity(strings[2544], false, 732, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcPerformanceHistory_type = new entity(strings[2545], false, 735, IFC4X3_RC4_IfcControl_type);
    IFC4X3_RC4_IfcPermeableCoveringProperties_type = new entity(strings[2546], false, 738, IFC4X3_RC4_IfcPreDefinedPropertySet_type);
    IFC4X3_RC4_IfcPermit_type = new entity(strings[2547], false, 739, IFC4X3_RC4_IfcControl_type);
    IFC4X3_RC4_IfcPileType_type = new entity(strings[2548], false, 750, IFC4X3_RC4_IfcDeepFoundationType_type);
    IFC4X3_RC4_IfcPipeFittingType_type = new entity(strings[2549], false, 753, IFC4X3_RC4_IfcFlowFittingType_type);
    IFC4X3_RC4_IfcPipeSegmentType_type = new entity(strings[2550], false, 756, IFC4X3_RC4_IfcFlowSegmentType_type);
    IFC4X3_RC4_IfcPlant_type = new entity(strings[2551], false, 765, IFC4X3_RC4_IfcGeographicElement_type);
    IFC4X3_RC4_IfcPlateType_type = new entity(strings[2552], false, 768, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcPolygonalFaceSet_type = new entity(strings[2553], false, 776, IFC4X3_RC4_IfcTessellatedFaceSet_type);
    IFC4X3_RC4_IfcPolyline_type = new entity(strings[2554], false, 777, IFC4X3_RC4_IfcBoundedCurve_type);
    IFC4X3_RC4_IfcPort_type = new entity(strings[2555], true, 780, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcPositioningElement_type = new entity(strings[2556], true, 781, IFC4X3_RC4_IfcProduct_type);
    IFC4X3_RC4_IfcProcedure_type = new entity(strings[2557], false, 801, IFC4X3_RC4_IfcProcess_type);
    IFC4X3_RC4_IfcProjectOrder_type = new entity(strings[2558], false, 820, IFC4X3_RC4_IfcControl_type);
    IFC4X3_RC4_IfcProjectionElement_type = new entity(strings[2559], false, 817, IFC4X3_RC4_IfcFeatureElementAddition_type);
    IFC4X3_RC4_IfcProtectiveDeviceType_type = new entity(strings[2560], false, 845, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcPumpType_type = new entity(strings[2561], false, 849, IFC4X3_RC4_IfcFlowMovingDeviceType_type);
    IFC4X3_RC4_IfcRailType_type = new entity(strings[2562], false, 863, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcRailingType_type = new entity(strings[2563], false, 861, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcRailway_type = new entity(strings[2564], false, 865, IFC4X3_RC4_IfcFacility_type);
    IFC4X3_RC4_IfcRampFlightType_type = new entity(strings[2565], false, 870, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcRampType_type = new entity(strings[2566], false, 872, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcRationalBSplineSurfaceWithKnots_type = new entity(strings[2567], false, 876, IFC4X3_RC4_IfcBSplineSurfaceWithKnots_type);
    IFC4X3_RC4_IfcReferent_type = new entity(strings[2568], false, 885, IFC4X3_RC4_IfcPositioningElement_type);
    IFC4X3_RC4_IfcReinforcingElement_type = new entity(strings[2569], true, 898, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcReinforcingElementType_type = new entity(strings[2570], true, 899, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcReinforcingMesh_type = new entity(strings[2571], false, 900, IFC4X3_RC4_IfcReinforcingElement_type);
    IFC4X3_RC4_IfcReinforcingMeshType_type = new entity(strings[2572], false, 901, IFC4X3_RC4_IfcReinforcingElementType_type);
    IFC4X3_RC4_IfcRelAdheresToElement_type = new entity(strings[2573], false, 903, IFC4X3_RC4_IfcRelDecomposes_type);
    IFC4X3_RC4_IfcRelAggregates_type = new entity(strings[2574], false, 904, IFC4X3_RC4_IfcRelDecomposes_type);
    IFC4X3_RC4_IfcRoad_type = new entity(strings[2575], false, 970, IFC4X3_RC4_IfcFacility_type);
    IFC4X3_RC4_IfcRoofType_type = new entity(strings[2576], false, 975, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcSanitaryTerminalType_type = new entity(strings[2577], false, 984, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcSeamCurve_type = new entity(strings[2578], false, 987, IFC4X3_RC4_IfcSurfaceCurve_type);
    IFC4X3_RC4_IfcSecondOrderPolynomialSpiral_type = new entity(strings[2579], false, 988, IFC4X3_RC4_IfcSpiral_type);
    IFC4X3_RC4_IfcSegmentedReferenceCurve_type = new entity(strings[2580], false, 999, IFC4X3_RC4_IfcCompositeCurve_type);
    IFC4X3_RC4_IfcSeventhOrderPolynomialSpiral_type = new entity(strings[2581], false, 1005, IFC4X3_RC4_IfcSpiral_type);
    IFC4X3_RC4_IfcShadingDeviceType_type = new entity(strings[2582], false, 1007, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcSign_type = new entity(strings[2583], false, 1015, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcSignType_type = new entity(strings[2584], false, 1019, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcSignalType_type = new entity(strings[2585], false, 1017, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcSine_type = new entity(strings[2586], false, 1025, IFC4X3_RC4_IfcSpiral_type);
    IFC4X3_RC4_IfcSite_type = new entity(strings[2587], false, 1027, IFC4X3_RC4_IfcSpatialStructureElement_type);
    IFC4X3_RC4_IfcSlabType_type = new entity(strings[2588], false, 1034, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcSolarDeviceType_type = new entity(strings[2589], false, 1038, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcSolidStratum_type = new entity(strings[2590], false, 1043, IFC4X3_RC4_IfcGeotechnicalStratum_type);
    IFC4X3_RC4_IfcSpace_type = new entity(strings[2591], false, 1048, IFC4X3_RC4_IfcSpatialStructureElement_type);
    IFC4X3_RC4_IfcSpaceHeaterType_type = new entity(strings[2592], false, 1051, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcSpaceType_type = new entity(strings[2593], false, 1053, IFC4X3_RC4_IfcSpatialStructureElementType_type);
    IFC4X3_RC4_IfcStackTerminalType_type = new entity(strings[2594], false, 1071, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcStairFlightType_type = new entity(strings[2595], false, 1075, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcStairType_type = new entity(strings[2596], false, 1077, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcStructuralAction_type = new entity(strings[2597], true, 1080, IFC4X3_RC4_IfcStructuralActivity_type);
    IFC4X3_RC4_IfcStructuralConnection_type = new entity(strings[2598], true, 1084, IFC4X3_RC4_IfcStructuralItem_type);
    IFC4X3_RC4_IfcStructuralCurveAction_type = new entity(strings[2599], false, 1086, IFC4X3_RC4_IfcStructuralAction_type);
    IFC4X3_RC4_IfcStructuralCurveConnection_type = new entity(strings[2600], false, 1088, IFC4X3_RC4_IfcStructuralConnection_type);
    IFC4X3_RC4_IfcStructuralCurveMember_type = new entity(strings[2601], false, 1089, IFC4X3_RC4_IfcStructuralMember_type);
    IFC4X3_RC4_IfcStructuralCurveMemberVarying_type = new entity(strings[2602], false, 1091, IFC4X3_RC4_IfcStructuralCurveMember_type);
    IFC4X3_RC4_IfcStructuralCurveReaction_type = new entity(strings[2603], false, 1092, IFC4X3_RC4_IfcStructuralReaction_type);
    IFC4X3_RC4_IfcStructuralLinearAction_type = new entity(strings[2604], false, 1094, IFC4X3_RC4_IfcStructuralCurveAction_type);
    IFC4X3_RC4_IfcStructuralLoadGroup_type = new entity(strings[2605], false, 1098, IFC4X3_RC4_IfcGroup_type);
    IFC4X3_RC4_IfcStructuralPointAction_type = new entity(strings[2606], false, 1110, IFC4X3_RC4_IfcStructuralAction_type);
    IFC4X3_RC4_IfcStructuralPointConnection_type = new entity(strings[2607], false, 1111, IFC4X3_RC4_IfcStructuralConnection_type);
    IFC4X3_RC4_IfcStructuralPointReaction_type = new entity(strings[2608], false, 1112, IFC4X3_RC4_IfcStructuralReaction_type);
    IFC4X3_RC4_IfcStructuralResultGroup_type = new entity(strings[2609], false, 1114, IFC4X3_RC4_IfcGroup_type);
    IFC4X3_RC4_IfcStructuralSurfaceAction_type = new entity(strings[2610], false, 1115, IFC4X3_RC4_IfcStructuralAction_type);
    IFC4X3_RC4_IfcStructuralSurfaceConnection_type = new entity(strings[2611], false, 1117, IFC4X3_RC4_IfcStructuralConnection_type);
    IFC4X3_RC4_IfcSubContractResource_type = new entity(strings[2612], false, 1125, IFC4X3_RC4_IfcConstructionResource_type);
    IFC4X3_RC4_IfcSurfaceFeature_type = new entity(strings[2613], false, 1132, IFC4X3_RC4_IfcFeatureElement_type);
    IFC4X3_RC4_IfcSwitchingDeviceType_type = new entity(strings[2614], false, 1152, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcSystem_type = new entity(strings[2615], false, 1154, IFC4X3_RC4_IfcGroup_type);
    IFC4X3_RC4_IfcSystemFurnitureElement_type = new entity(strings[2616], false, 1155, IFC4X3_RC4_IfcFurnishingElement_type);
    IFC4X3_RC4_IfcTankType_type = new entity(strings[2617], false, 1162, IFC4X3_RC4_IfcFlowStorageDeviceType_type);
    IFC4X3_RC4_IfcTendon_type = new entity(strings[2618], false, 1173, IFC4X3_RC4_IfcReinforcingElement_type);
    IFC4X3_RC4_IfcTendonAnchor_type = new entity(strings[2619], false, 1174, IFC4X3_RC4_IfcReinforcingElement_type);
    IFC4X3_RC4_IfcTendonAnchorType_type = new entity(strings[2620], false, 1175, IFC4X3_RC4_IfcReinforcingElementType_type);
    IFC4X3_RC4_IfcTendonConduit_type = new entity(strings[2621], false, 1177, IFC4X3_RC4_IfcReinforcingElement_type);
    IFC4X3_RC4_IfcTendonConduitType_type = new entity(strings[2622], false, 1178, IFC4X3_RC4_IfcReinforcingElementType_type);
    IFC4X3_RC4_IfcTendonType_type = new entity(strings[2623], false, 1180, IFC4X3_RC4_IfcReinforcingElementType_type);
    IFC4X3_RC4_IfcTrackElementType_type = new entity(strings[2624], false, 1222, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcTransformerType_type = new entity(strings[2625], false, 1225, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcTransportElement_type = new entity(strings[2626], false, 1229, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcTrimmedCurve_type = new entity(strings[2627], false, 1237, IFC4X3_RC4_IfcBoundedCurve_type);
    IFC4X3_RC4_IfcTubeBundleType_type = new entity(strings[2628], false, 1242, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcUnitaryEquipmentType_type = new entity(strings[2629], false, 1253, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcValveType_type = new entity(strings[2630], false, 1261, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcVibrationDamper_type = new entity(strings[2631], false, 1269, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcVibrationDamperType_type = new entity(strings[2632], false, 1270, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcVibrationIsolator_type = new entity(strings[2633], false, 1272, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcVibrationIsolatorType_type = new entity(strings[2634], false, 1273, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcVirtualElement_type = new entity(strings[2635], false, 1275, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcVoidStratum_type = new entity(strings[2636], false, 1279, IFC4X3_RC4_IfcGeotechnicalStratum_type);
    IFC4X3_RC4_IfcVoidingFeature_type = new entity(strings[2637], false, 1277, IFC4X3_RC4_IfcFeatureElementSubtraction_type);
    IFC4X3_RC4_IfcWallType_type = new entity(strings[2638], false, 1285, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcWasteTerminalType_type = new entity(strings[2639], false, 1291, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcWaterStratum_type = new entity(strings[2640], false, 1293, IFC4X3_RC4_IfcGeotechnicalStratum_type);
    IFC4X3_RC4_IfcWindowType_type = new entity(strings[2641], false, 1303, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcWorkCalendar_type = new entity(strings[2642], false, 1306, IFC4X3_RC4_IfcControl_type);
    IFC4X3_RC4_IfcWorkControl_type = new entity(strings[2643], true, 1308, IFC4X3_RC4_IfcControl_type);
    IFC4X3_RC4_IfcWorkPlan_type = new entity(strings[2644], false, 1309, IFC4X3_RC4_IfcWorkControl_type);
    IFC4X3_RC4_IfcWorkSchedule_type = new entity(strings[2645], false, 1311, IFC4X3_RC4_IfcWorkControl_type);
    IFC4X3_RC4_IfcZone_type = new entity(strings[2646], false, 1314, IFC4X3_RC4_IfcSystem_type);
    IFC4X3_RC4_IfcCurveFontOrScaledCurveFontSelect_type = new select_type(strings[2647], 276, {
        IFC4X3_RC4_IfcCurveStyleFontAndScaling_type,
        IFC4X3_RC4_IfcCurveStyleFontSelect_type
    });
    IFC4X3_RC4_IfcCurveOnSurface_type = new select_type(strings[2648], 279, {
        IFC4X3_RC4_IfcCompositeCurveOnSurface_type,
        IFC4X3_RC4_IfcPcurve_type,
        IFC4X3_RC4_IfcSurfaceCurve_type
    });
    IFC4X3_RC4_IfcCurveOrEdgeCurve_type = new select_type(strings[2649], 280, {
        IFC4X3_RC4_IfcBoundedCurve_type,
        IFC4X3_RC4_IfcEdgeCurve_type
    });
    IFC4X3_RC4_IfcInterferenceSelect_type = new select_type(strings[2650], 559, {
        IFC4X3_RC4_IfcElement_type,
        IFC4X3_RC4_IfcSpatialElement_type
    });
    IFC4X3_RC4_IfcSpatialReferenceSelect_type = new select_type(strings[2651], 1057, {
        IFC4X3_RC4_IfcGroup_type,
        IFC4X3_RC4_IfcProduct_type
    });
    IFC4X3_RC4_IfcStructuralActivityAssignmentSelect_type = new select_type(strings[2652], 1082, {
        IFC4X3_RC4_IfcElement_type,
        IFC4X3_RC4_IfcStructuralItem_type
    });
    IFC4X3_RC4_IfcActionRequest_type = new entity(strings[2653], false, 2, IFC4X3_RC4_IfcControl_type);
    IFC4X3_RC4_IfcAirTerminalBoxType_type = new entity(strings[2654], false, 19, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcAirTerminalType_type = new entity(strings[2655], false, 21, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcAirToAirHeatRecoveryType_type = new entity(strings[2656], false, 24, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcAlignmentCant_type = new entity(strings[2657], false, 30, IFC4X3_RC4_IfcLinearElement_type);
    IFC4X3_RC4_IfcAlignmentHorizontal_type = new entity(strings[2658], false, 33, IFC4X3_RC4_IfcLinearElement_type);
    IFC4X3_RC4_IfcAlignmentSegment_type = new entity(strings[2659], false, 37, IFC4X3_RC4_IfcLinearElement_type);
    IFC4X3_RC4_IfcAlignmentVertical_type = new entity(strings[2660], false, 39, IFC4X3_RC4_IfcLinearElement_type);
    IFC4X3_RC4_IfcAsset_type = new entity(strings[2661], false, 62, IFC4X3_RC4_IfcGroup_type);
    IFC4X3_RC4_IfcAudioVisualApplianceType_type = new entity(strings[2662], false, 65, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcBSplineCurve_type = new entity(strings[2663], true, 108, IFC4X3_RC4_IfcBoundedCurve_type);
    IFC4X3_RC4_IfcBSplineCurveWithKnots_type = new entity(strings[2664], false, 110, IFC4X3_RC4_IfcBSplineCurve_type);
    IFC4X3_RC4_IfcBeamType_type = new entity(strings[2665], false, 74, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcBearingType_type = new entity(strings[2666], false, 77, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcBoilerType_type = new entity(strings[2667], false, 86, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcBoundaryCurve_type = new entity(strings[2668], false, 95, IFC4X3_RC4_IfcCompositeCurveOnSurface_type);
    IFC4X3_RC4_IfcBridge_type = new entity(strings[2669], false, 105, IFC4X3_RC4_IfcFacility_type);
    IFC4X3_RC4_IfcBuilding_type = new entity(strings[2670], false, 114, IFC4X3_RC4_IfcFacility_type);
    IFC4X3_RC4_IfcBuildingElementPart_type = new entity(strings[2671], false, 115, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcBuildingElementPartType_type = new entity(strings[2672], false, 116, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcBuildingElementProxyType_type = new entity(strings[2673], false, 119, IFC4X3_RC4_IfcBuiltElementType_type);
    IFC4X3_RC4_IfcBuildingSystem_type = new entity(strings[2674], false, 122, IFC4X3_RC4_IfcSystem_type);
    IFC4X3_RC4_IfcBuiltElement_type = new entity(strings[2675], false, 124, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcBuiltSystem_type = new entity(strings[2676], false, 126, IFC4X3_RC4_IfcSystem_type);
    IFC4X3_RC4_IfcBurnerType_type = new entity(strings[2677], false, 129, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcCableCarrierFittingType_type = new entity(strings[2678], false, 132, IFC4X3_RC4_IfcFlowFittingType_type);
    IFC4X3_RC4_IfcCableCarrierSegmentType_type = new entity(strings[2679], false, 135, IFC4X3_RC4_IfcFlowSegmentType_type);
    IFC4X3_RC4_IfcCableFittingType_type = new entity(strings[2680], false, 138, IFC4X3_RC4_IfcFlowFittingType_type);
    IFC4X3_RC4_IfcCableSegmentType_type = new entity(strings[2681], false, 141, IFC4X3_RC4_IfcFlowSegmentType_type);
    IFC4X3_RC4_IfcCaissonFoundationType_type = new entity(strings[2682], false, 144, IFC4X3_RC4_IfcDeepFoundationType_type);
    IFC4X3_RC4_IfcChillerType_type = new entity(strings[2683], false, 159, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcChimney_type = new entity(strings[2684], false, 161, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcCircle_type = new entity(strings[2685], false, 164, IFC4X3_RC4_IfcConic_type);
    IFC4X3_RC4_IfcCivilElement_type = new entity(strings[2686], false, 167, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcCoilType_type = new entity(strings[2687], false, 176, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcColumn_type = new entity(strings[2688], false, 183, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcColumnStandardCase_type = new entity(strings[2689], false, 184, IFC4X3_RC4_IfcColumn_type);
    IFC4X3_RC4_IfcCommunicationsApplianceType_type = new entity(strings[2690], false, 188, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcCompressorType_type = new entity(strings[2691], false, 200, IFC4X3_RC4_IfcFlowMovingDeviceType_type);
    IFC4X3_RC4_IfcCondenserType_type = new entity(strings[2692], false, 203, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcConstructionEquipmentResource_type = new entity(strings[2693], false, 216, IFC4X3_RC4_IfcConstructionResource_type);
    IFC4X3_RC4_IfcConstructionMaterialResource_type = new entity(strings[2694], false, 219, IFC4X3_RC4_IfcConstructionResource_type);
    IFC4X3_RC4_IfcConstructionProductResource_type = new entity(strings[2695], false, 222, IFC4X3_RC4_IfcConstructionResource_type);
    IFC4X3_RC4_IfcConveyorSegmentType_type = new entity(strings[2696], false, 237, IFC4X3_RC4_IfcFlowSegmentType_type);
    IFC4X3_RC4_IfcCooledBeamType_type = new entity(strings[2697], false, 240, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcCoolingTowerType_type = new entity(strings[2698], false, 243, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcCourse_type = new entity(strings[2699], false, 255, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcCovering_type = new entity(strings[2700], false, 258, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcCurtainWall_type = new entity(strings[2701], false, 269, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcDamperType_type = new entity(strings[2702], false, 289, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcDeepFoundation_type = new entity(strings[2703], false, 296, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcDiscreteAccessory_type = new entity(strings[2704], false, 311, IFC4X3_RC4_IfcElementComponent_type);
    IFC4X3_RC4_IfcDiscreteAccessoryType_type = new entity(strings[2705], false, 312, IFC4X3_RC4_IfcElementComponentType_type);
    IFC4X3_RC4_IfcDistributionBoardType_type = new entity(strings[2706], false, 315, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcDistributionChamberElementType_type = new entity(strings[2707], false, 318, IFC4X3_RC4_IfcDistributionFlowElementType_type);
    IFC4X3_RC4_IfcDistributionControlElementType_type = new entity(strings[2708], true, 322, IFC4X3_RC4_IfcDistributionElementType_type);
    IFC4X3_RC4_IfcDistributionElement_type = new entity(strings[2709], false, 323, IFC4X3_RC4_IfcElement_type);
    IFC4X3_RC4_IfcDistributionFlowElement_type = new entity(strings[2710], false, 325, IFC4X3_RC4_IfcDistributionElement_type);
    IFC4X3_RC4_IfcDistributionPort_type = new entity(strings[2711], false, 327, IFC4X3_RC4_IfcPort_type);
    IFC4X3_RC4_IfcDistributionSystem_type = new entity(strings[2712], false, 329, IFC4X3_RC4_IfcSystem_type);
    IFC4X3_RC4_IfcDoor_type = new entity(strings[2713], false, 337, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcDoorStandardCase_type = new entity(strings[2714], false, 342, IFC4X3_RC4_IfcDoor_type);
    IFC4X3_RC4_IfcDuctFittingType_type = new entity(strings[2715], false, 353, IFC4X3_RC4_IfcFlowFittingType_type);
    IFC4X3_RC4_IfcDuctSegmentType_type = new entity(strings[2716], false, 356, IFC4X3_RC4_IfcFlowSegmentType_type);
    IFC4X3_RC4_IfcDuctSilencerType_type = new entity(strings[2717], false, 359, IFC4X3_RC4_IfcFlowTreatmentDeviceType_type);
    IFC4X3_RC4_IfcEarthworksCut_type = new entity(strings[2718], false, 363, IFC4X3_RC4_IfcFeatureElementSubtraction_type);
    IFC4X3_RC4_IfcEarthworksElement_type = new entity(strings[2719], false, 365, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcEarthworksFill_type = new entity(strings[2720], false, 366, IFC4X3_RC4_IfcEarthworksElement_type);
    IFC4X3_RC4_IfcElectricApplianceType_type = new entity(strings[2721], false, 372, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcElectricDistributionBoardType_type = new entity(strings[2722], false, 379, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcElectricFlowStorageDeviceType_type = new entity(strings[2723], false, 382, IFC4X3_RC4_IfcFlowStorageDeviceType_type);
    IFC4X3_RC4_IfcElectricFlowTreatmentDeviceType_type = new entity(strings[2724], false, 385, IFC4X3_RC4_IfcFlowTreatmentDeviceType_type);
    IFC4X3_RC4_IfcElectricGeneratorType_type = new entity(strings[2725], false, 388, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcElectricMotorType_type = new entity(strings[2726], false, 391, IFC4X3_RC4_IfcEnergyConversionDeviceType_type);
    IFC4X3_RC4_IfcElectricTimeControlType_type = new entity(strings[2727], false, 395, IFC4X3_RC4_IfcFlowControllerType_type);
    IFC4X3_RC4_IfcEnergyConversionDevice_type = new entity(strings[2728], false, 410, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcEngine_type = new entity(strings[2729], false, 413, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcEvaporativeCooler_type = new entity(strings[2730], false, 416, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcEvaporator_type = new entity(strings[2731], false, 419, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcExternalSpatialElement_type = new entity(strings[2732], false, 434, IFC4X3_RC4_IfcExternalSpatialStructureElement_type);
    IFC4X3_RC4_IfcFanType_type = new entity(strings[2733], false, 453, IFC4X3_RC4_IfcFlowMovingDeviceType_type);
    IFC4X3_RC4_IfcFilterType_type = new entity(strings[2734], false, 466, IFC4X3_RC4_IfcFlowTreatmentDeviceType_type);
    IFC4X3_RC4_IfcFireSuppressionTerminalType_type = new entity(strings[2735], false, 469, IFC4X3_RC4_IfcFlowTerminalType_type);
    IFC4X3_RC4_IfcFlowController_type = new entity(strings[2736], false, 472, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcFlowFitting_type = new entity(strings[2737], false, 475, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcFlowInstrumentType_type = new entity(strings[2738], false, 478, IFC4X3_RC4_IfcDistributionControlElementType_type);
    IFC4X3_RC4_IfcFlowMeter_type = new entity(strings[2739], false, 480, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcFlowMovingDevice_type = new entity(strings[2740], false, 483, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcFlowSegment_type = new entity(strings[2741], false, 485, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcFlowStorageDevice_type = new entity(strings[2742], false, 487, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcFlowTerminal_type = new entity(strings[2743], false, 489, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcFlowTreatmentDevice_type = new entity(strings[2744], false, 491, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcFooting_type = new entity(strings[2745], false, 496, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcGeotechnicalAssembly_type = new entity(strings[2746], true, 518, IFC4X3_RC4_IfcGeotechnicalElement_type);
    IFC4X3_RC4_IfcGrid_type = new entity(strings[2747], false, 524, IFC4X3_RC4_IfcPositioningElement_type);
    IFC4X3_RC4_IfcHeatExchanger_type = new entity(strings[2748], false, 532, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcHumidifier_type = new entity(strings[2749], false, 537, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcInterceptor_type = new entity(strings[2750], false, 556, IFC4X3_RC4_IfcFlowTreatmentDevice_type);
    IFC4X3_RC4_IfcJunctionBox_type = new entity(strings[2751], false, 569, IFC4X3_RC4_IfcFlowFitting_type);
    IFC4X3_RC4_IfcKerb_type = new entity(strings[2752], false, 572, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcLamp_type = new entity(strings[2753], false, 581, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcLightFixture_type = new entity(strings[2754], false, 595, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcLinearPositioningElement_type = new entity(strings[2755], false, 610, IFC4X3_RC4_IfcPositioningElement_type);
    IFC4X3_RC4_IfcLiquidTerminal_type = new entity(strings[2756], false, 614, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcMedicalDevice_type = new entity(strings[2757], false, 663, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcMember_type = new entity(strings[2758], false, 666, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcMemberStandardCase_type = new entity(strings[2759], false, 667, IFC4X3_RC4_IfcMember_type);
    IFC4X3_RC4_IfcMobileTelecommunicationsAppliance_type = new entity(strings[2760], false, 673, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcMooringDevice_type = new entity(strings[2761], false, 689, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcMotorConnection_type = new entity(strings[2762], false, 692, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcNavigationElement_type = new entity(strings[2763], false, 696, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcOuterBoundaryCurve_type = new entity(strings[2764], false, 723, IFC4X3_RC4_IfcBoundaryCurve_type);
    IFC4X3_RC4_IfcOutlet_type = new entity(strings[2765], false, 724, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcPavement_type = new entity(strings[2766], false, 731, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcPile_type = new entity(strings[2767], false, 748, IFC4X3_RC4_IfcDeepFoundation_type);
    IFC4X3_RC4_IfcPipeFitting_type = new entity(strings[2768], false, 752, IFC4X3_RC4_IfcFlowFitting_type);
    IFC4X3_RC4_IfcPipeSegment_type = new entity(strings[2769], false, 755, IFC4X3_RC4_IfcFlowSegment_type);
    IFC4X3_RC4_IfcPlate_type = new entity(strings[2770], false, 766, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcPlateStandardCase_type = new entity(strings[2771], false, 767, IFC4X3_RC4_IfcPlate_type);
    IFC4X3_RC4_IfcProtectiveDevice_type = new entity(strings[2772], false, 841, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitType_type = new entity(strings[2773], false, 843, IFC4X3_RC4_IfcDistributionControlElementType_type);
    IFC4X3_RC4_IfcPump_type = new entity(strings[2774], false, 848, IFC4X3_RC4_IfcFlowMovingDevice_type);
    IFC4X3_RC4_IfcRail_type = new entity(strings[2775], false, 859, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcRailing_type = new entity(strings[2776], false, 860, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcRamp_type = new entity(strings[2777], false, 868, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcRampFlight_type = new entity(strings[2778], false, 869, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcRationalBSplineCurveWithKnots_type = new entity(strings[2779], false, 875, IFC4X3_RC4_IfcBSplineCurveWithKnots_type);
    IFC4X3_RC4_IfcReinforcedSoil_type = new entity(strings[2780], false, 889, IFC4X3_RC4_IfcEarthworksElement_type);
    IFC4X3_RC4_IfcReinforcingBar_type = new entity(strings[2781], false, 893, IFC4X3_RC4_IfcReinforcingElement_type);
    IFC4X3_RC4_IfcReinforcingBarType_type = new entity(strings[2782], false, 896, IFC4X3_RC4_IfcReinforcingElementType_type);
    IFC4X3_RC4_IfcRoof_type = new entity(strings[2783], false, 974, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcSanitaryTerminal_type = new entity(strings[2784], false, 983, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcSensorType_type = new entity(strings[2785], false, 1002, IFC4X3_RC4_IfcDistributionControlElementType_type);
    IFC4X3_RC4_IfcShadingDevice_type = new entity(strings[2786], false, 1006, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcSignal_type = new entity(strings[2787], false, 1016, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcSlab_type = new entity(strings[2788], false, 1031, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcSlabElementedCase_type = new entity(strings[2789], false, 1032, IFC4X3_RC4_IfcSlab_type);
    IFC4X3_RC4_IfcSlabStandardCase_type = new entity(strings[2790], false, 1033, IFC4X3_RC4_IfcSlab_type);
    IFC4X3_RC4_IfcSolarDevice_type = new entity(strings[2791], false, 1037, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcSpaceHeater_type = new entity(strings[2792], false, 1050, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcStackTerminal_type = new entity(strings[2793], false, 1070, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcStair_type = new entity(strings[2794], false, 1073, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcStairFlight_type = new entity(strings[2795], false, 1074, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcStructuralAnalysisModel_type = new entity(strings[2796], false, 1083, IFC4X3_RC4_IfcSystem_type);
    IFC4X3_RC4_IfcStructuralLoadCase_type = new entity(strings[2797], false, 1096, IFC4X3_RC4_IfcStructuralLoadGroup_type);
    IFC4X3_RC4_IfcStructuralPlanarAction_type = new entity(strings[2798], false, 1109, IFC4X3_RC4_IfcStructuralSurfaceAction_type);
    IFC4X3_RC4_IfcSwitchingDevice_type = new entity(strings[2799], false, 1151, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcTank_type = new entity(strings[2800], false, 1161, IFC4X3_RC4_IfcFlowStorageDevice_type);
    IFC4X3_RC4_IfcTrackElement_type = new entity(strings[2801], false, 1221, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcTransformer_type = new entity(strings[2802], false, 1224, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcTubeBundle_type = new entity(strings[2803], false, 1241, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcUnitaryControlElementType_type = new entity(strings[2804], false, 1250, IFC4X3_RC4_IfcDistributionControlElementType_type);
    IFC4X3_RC4_IfcUnitaryEquipment_type = new entity(strings[2805], false, 1252, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcValve_type = new entity(strings[2806], false, 1260, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcWall_type = new entity(strings[2807], false, 1282, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcWallElementedCase_type = new entity(strings[2808], false, 1283, IFC4X3_RC4_IfcWall_type);
    IFC4X3_RC4_IfcWallStandardCase_type = new entity(strings[2809], false, 1284, IFC4X3_RC4_IfcWall_type);
    IFC4X3_RC4_IfcWasteTerminal_type = new entity(strings[2810], false, 1290, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcWindow_type = new entity(strings[2811], false, 1294, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcWindowStandardCase_type = new entity(strings[2812], false, 1299, IFC4X3_RC4_IfcWindow_type);
    IFC4X3_RC4_IfcSpaceBoundarySelect_type = new select_type(strings[2813], 1049, {
        IFC4X3_RC4_IfcExternalSpatialElement_type,
        IFC4X3_RC4_IfcSpace_type
    });
    IFC4X3_RC4_IfcActuatorType_type = new entity(strings[2814], false, 10, IFC4X3_RC4_IfcDistributionControlElementType_type);
    IFC4X3_RC4_IfcAirTerminal_type = new entity(strings[2815], false, 17, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcAirTerminalBox_type = new entity(strings[2816], false, 18, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcAirToAirHeatRecovery_type = new entity(strings[2817], false, 23, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcAlarmType_type = new entity(strings[2818], false, 27, IFC4X3_RC4_IfcDistributionControlElementType_type);
    IFC4X3_RC4_IfcAlignment_type = new entity(strings[2819], false, 29, IFC4X3_RC4_IfcLinearPositioningElement_type);
    IFC4X3_RC4_IfcAudioVisualAppliance_type = new entity(strings[2820], false, 64, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcBeam_type = new entity(strings[2821], false, 72, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcBeamStandardCase_type = new entity(strings[2822], false, 73, IFC4X3_RC4_IfcBeam_type);
    IFC4X3_RC4_IfcBearing_type = new entity(strings[2823], false, 76, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcBoiler_type = new entity(strings[2824], false, 85, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcBorehole_type = new entity(strings[2825], false, 93, IFC4X3_RC4_IfcGeotechnicalAssembly_type);
    IFC4X3_RC4_IfcBuildingElementProxy_type = new entity(strings[2826], false, 118, IFC4X3_RC4_IfcBuiltElement_type);
    IFC4X3_RC4_IfcBurner_type = new entity(strings[2827], false, 128, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcCableCarrierFitting_type = new entity(strings[2828], false, 131, IFC4X3_RC4_IfcFlowFitting_type);
    IFC4X3_RC4_IfcCableCarrierSegment_type = new entity(strings[2829], false, 134, IFC4X3_RC4_IfcFlowSegment_type);
    IFC4X3_RC4_IfcCableFitting_type = new entity(strings[2830], false, 137, IFC4X3_RC4_IfcFlowFitting_type);
    IFC4X3_RC4_IfcCableSegment_type = new entity(strings[2831], false, 140, IFC4X3_RC4_IfcFlowSegment_type);
    IFC4X3_RC4_IfcCaissonFoundation_type = new entity(strings[2832], false, 143, IFC4X3_RC4_IfcDeepFoundation_type);
    IFC4X3_RC4_IfcChiller_type = new entity(strings[2833], false, 158, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcCoil_type = new entity(strings[2834], false, 175, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcCommunicationsAppliance_type = new entity(strings[2835], false, 187, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcCompressor_type = new entity(strings[2836], false, 199, IFC4X3_RC4_IfcFlowMovingDevice_type);
    IFC4X3_RC4_IfcCondenser_type = new entity(strings[2837], false, 202, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcControllerType_type = new entity(strings[2838], false, 232, IFC4X3_RC4_IfcDistributionControlElementType_type);
    IFC4X3_RC4_IfcConveyorSegment_type = new entity(strings[2839], false, 236, IFC4X3_RC4_IfcFlowSegment_type);
    IFC4X3_RC4_IfcCooledBeam_type = new entity(strings[2840], false, 239, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcCoolingTower_type = new entity(strings[2841], false, 242, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcDamper_type = new entity(strings[2842], false, 288, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcDistributionBoard_type = new entity(strings[2843], false, 314, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcDistributionChamberElement_type = new entity(strings[2844], false, 317, IFC4X3_RC4_IfcDistributionFlowElement_type);
    IFC4X3_RC4_IfcDistributionCircuit_type = new entity(strings[2845], false, 320, IFC4X3_RC4_IfcDistributionSystem_type);
    IFC4X3_RC4_IfcDistributionControlElement_type = new entity(strings[2846], false, 321, IFC4X3_RC4_IfcDistributionElement_type);
    IFC4X3_RC4_IfcDuctFitting_type = new entity(strings[2847], false, 352, IFC4X3_RC4_IfcFlowFitting_type);
    IFC4X3_RC4_IfcDuctSegment_type = new entity(strings[2848], false, 355, IFC4X3_RC4_IfcFlowSegment_type);
    IFC4X3_RC4_IfcDuctSilencer_type = new entity(strings[2849], false, 358, IFC4X3_RC4_IfcFlowTreatmentDevice_type);
    IFC4X3_RC4_IfcElectricAppliance_type = new entity(strings[2850], false, 371, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcElectricDistributionBoard_type = new entity(strings[2851], false, 378, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcElectricFlowStorageDevice_type = new entity(strings[2852], false, 381, IFC4X3_RC4_IfcFlowStorageDevice_type);
    IFC4X3_RC4_IfcElectricFlowTreatmentDevice_type = new entity(strings[2853], false, 384, IFC4X3_RC4_IfcFlowTreatmentDevice_type);
    IFC4X3_RC4_IfcElectricGenerator_type = new entity(strings[2854], false, 387, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcElectricMotor_type = new entity(strings[2855], false, 390, IFC4X3_RC4_IfcEnergyConversionDevice_type);
    IFC4X3_RC4_IfcElectricTimeControl_type = new entity(strings[2856], false, 394, IFC4X3_RC4_IfcFlowController_type);
    IFC4X3_RC4_IfcFan_type = new entity(strings[2857], false, 452, IFC4X3_RC4_IfcFlowMovingDevice_type);
    IFC4X3_RC4_IfcFilter_type = new entity(strings[2858], false, 465, IFC4X3_RC4_IfcFlowTreatmentDevice_type);
    IFC4X3_RC4_IfcFireSuppressionTerminal_type = new entity(strings[2859], false, 468, IFC4X3_RC4_IfcFlowTerminal_type);
    IFC4X3_RC4_IfcFlowInstrument_type = new entity(strings[2860], false, 477, IFC4X3_RC4_IfcDistributionControlElement_type);
    IFC4X3_RC4_IfcGeomodel_type = new entity(strings[2861], false, 516, IFC4X3_RC4_IfcGeotechnicalAssembly_type);
    IFC4X3_RC4_IfcGeoslice_type = new entity(strings[2862], false, 517, IFC4X3_RC4_IfcGeotechnicalAssembly_type);
    IFC4X3_RC4_IfcProtectiveDeviceTrippingUnit_type = new entity(strings[2863], false, 842, IFC4X3_RC4_IfcDistributionControlElement_type);
    IFC4X3_RC4_IfcSensor_type = new entity(strings[2864], false, 1001, IFC4X3_RC4_IfcDistributionControlElement_type);
    IFC4X3_RC4_IfcUnitaryControlElement_type = new entity(strings[2865], false, 1249, IFC4X3_RC4_IfcDistributionControlElement_type);
    IFC4X3_RC4_IfcActuator_type = new entity(strings[2866], false, 9, IFC4X3_RC4_IfcDistributionControlElement_type);
    IFC4X3_RC4_IfcAlarm_type = new entity(strings[2867], false, 26, IFC4X3_RC4_IfcDistributionControlElement_type);
    IFC4X3_RC4_IfcController_type = new entity(strings[2868], false, 231, IFC4X3_RC4_IfcDistributionControlElement_type);
    IFC4X3_RC4_IfcActionRequest_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcActionRequestTypeEnum_type), true),
            new attribute(strings[2870], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2871], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcActor_type->set_attributes({
            new attribute(strings[2872], new named_type(IFC4X3_RC4_IfcActorSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcActorRole_type->set_attributes({
            new attribute(strings[2873], new named_type(IFC4X3_RC4_IfcRoleEnum_type), false),
            new attribute(strings[2874], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcActuator_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcActuatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcActuatorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcActuatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAddress_type->set_attributes({
            new attribute(strings[2876], new named_type(IFC4X3_RC4_IfcAddressTypeEnum_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[2877], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcAdvancedBrep_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcAdvancedBrepWithVoids_type->set_attributes({
            new attribute(strings[2878], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcClosedShell_type)), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcAdvancedFace_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcAirTerminal_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAirTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAirTerminalBox_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAirTerminalBoxTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAirTerminalBoxType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAirTerminalBoxTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAirTerminalType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAirTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAirToAirHeatRecovery_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAirToAirHeatRecoveryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAirToAirHeatRecoveryType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAirToAirHeatRecoveryTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlarm_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAlarmTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlarmType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAlarmTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlignment_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAlignmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlignmentCant_type->set_attributes({
            new attribute(strings[2879], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlignmentCantSegment_type->set_attributes({
            new attribute(strings[2880], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2881], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[2882], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2883], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[2884], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2885], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAlignmentCantSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlignmentHorizontal_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlignmentHorizontalSegment_type->set_attributes({
            new attribute(strings[2886], new named_type(IFC4X3_RC4_IfcCartesianPoint_type), false),
            new attribute(strings[2887], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), false),
            new attribute(strings[2888], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2889], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2890], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[2891], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAlignmentHorizontalSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlignmentParameterSegment_type->set_attributes({
            new attribute(strings[2892], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2893], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcAlignmentSegment_type->set_attributes({
            new attribute(strings[2894], new named_type(IFC4X3_RC4_IfcAlignmentParameterSegment_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlignmentVertical_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAlignmentVerticalSegment_type->set_attributes({
            new attribute(strings[2880], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2881], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[2895], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2896], new named_type(IFC4X3_RC4_IfcRatioMeasure_type), false),
            new attribute(strings[2897], new named_type(IFC4X3_RC4_IfcRatioMeasure_type), false),
            new attribute(strings[2898], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAlignmentVerticalSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAnnotation_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAnnotationTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAnnotationFillArea_type->set_attributes({
            new attribute(strings[2899], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[2900], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcCurve_type)), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcApplication_type->set_attributes({
            new attribute(strings[2901], new named_type(IFC4X3_RC4_IfcOrganization_type), false),
            new attribute(strings[2902], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2903], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2904], new named_type(IFC4X3_RC4_IfcIdentifier_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcAppliedValue_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[2906], new named_type(IFC4X3_RC4_IfcAppliedValueSelect_type), true),
            new attribute(strings[2907], new named_type(IFC4X3_RC4_IfcMeasureWithUnit_type), true),
            new attribute(strings[2908], new named_type(IFC4X3_RC4_IfcDate_type), true),
            new attribute(strings[2909], new named_type(IFC4X3_RC4_IfcDate_type), true),
            new attribute(strings[2910], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2911], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2912], new named_type(IFC4X3_RC4_IfcArithmeticOperatorEnum_type), true),
            new attribute(strings[2913], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcAppliedValue_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcApproval_type->set_attributes({
            new attribute(strings[2914], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[2915], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[2870], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2916], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2917], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[2918], new named_type(IFC4X3_RC4_IfcActorSelect_type), true),
            new attribute(strings[2919], new named_type(IFC4X3_RC4_IfcActorSelect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcApprovalRelationship_type->set_attributes({
            new attribute(strings[2920], new named_type(IFC4X3_RC4_IfcApproval_type), false),
            new attribute(strings[2921], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcApproval_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcArbitraryClosedProfileDef_type->set_attributes({
            new attribute(strings[2922], new named_type(IFC4X3_RC4_IfcCurve_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcArbitraryOpenProfileDef_type->set_attributes({
            new attribute(strings[2923], new named_type(IFC4X3_RC4_IfcBoundedCurve_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcArbitraryProfileDefWithVoids_type->set_attributes({
            new attribute(strings[2924], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcCurve_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcAsset_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2926], new named_type(IFC4X3_RC4_IfcCostValue_type), true),
            new attribute(strings[2927], new named_type(IFC4X3_RC4_IfcCostValue_type), true),
            new attribute(strings[2928], new named_type(IFC4X3_RC4_IfcCostValue_type), true),
            new attribute(strings[2929], new named_type(IFC4X3_RC4_IfcActorSelect_type), true),
            new attribute(strings[2930], new named_type(IFC4X3_RC4_IfcActorSelect_type), true),
            new attribute(strings[2931], new named_type(IFC4X3_RC4_IfcPerson_type), true),
            new attribute(strings[2932], new named_type(IFC4X3_RC4_IfcDate_type), true),
            new attribute(strings[2933], new named_type(IFC4X3_RC4_IfcCostValue_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAsymmetricIShapeProfileDef_type->set_attributes({
            new attribute(strings[2934], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2935], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2936], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2937], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2938], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2939], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2940], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2941], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2942], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2943], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[2944], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[2945], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAudioVisualAppliance_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAudioVisualApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAudioVisualApplianceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAudioVisualApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcAxis1Placement_type->set_attributes({
            new attribute(strings[2946], new named_type(IFC4X3_RC4_IfcDirection_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcAxis2Placement2D_type->set_attributes({
            new attribute(strings[2947], new named_type(IFC4X3_RC4_IfcDirection_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcAxis2Placement3D_type->set_attributes({
            new attribute(strings[2946], new named_type(IFC4X3_RC4_IfcDirection_type), true),
            new attribute(strings[2947], new named_type(IFC4X3_RC4_IfcDirection_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcAxis2PlacementLinear_type->set_attributes({
            new attribute(strings[2946], new named_type(IFC4X3_RC4_IfcDirection_type), true),
            new attribute(strings[2947], new named_type(IFC4X3_RC4_IfcDirection_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcBSplineCurve_type->set_attributes({
            new attribute(strings[2948], new named_type(IFC4X3_RC4_IfcInteger_type), false),
            new attribute(strings[2949], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcCartesianPoint_type)), false),
            new attribute(strings[2950], new named_type(IFC4X3_RC4_IfcBSplineCurveForm_type), false),
            new attribute(strings[2951], new named_type(IFC4X3_RC4_IfcLogical_type), false),
            new attribute(strings[2952], new named_type(IFC4X3_RC4_IfcLogical_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcBSplineCurveWithKnots_type->set_attributes({
            new attribute(strings[2953], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcInteger_type)), false),
            new attribute(strings[2954], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcParameterValue_type)), false),
            new attribute(strings[2955], new named_type(IFC4X3_RC4_IfcKnotType_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBSplineSurface_type->set_attributes({
            new attribute(strings[2956], new named_type(IFC4X3_RC4_IfcInteger_type), false),
            new attribute(strings[2957], new named_type(IFC4X3_RC4_IfcInteger_type), false),
            new attribute(strings[2949], new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcCartesianPoint_type))), false),
            new attribute(strings[2958], new named_type(IFC4X3_RC4_IfcBSplineSurfaceForm_type), false),
            new attribute(strings[2959], new named_type(IFC4X3_RC4_IfcLogical_type), false),
            new attribute(strings[2960], new named_type(IFC4X3_RC4_IfcLogical_type), false),
            new attribute(strings[2952], new named_type(IFC4X3_RC4_IfcLogical_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBSplineSurfaceWithKnots_type->set_attributes({
            new attribute(strings[2961], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcInteger_type)), false),
            new attribute(strings[2962], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcInteger_type)), false),
            new attribute(strings[2963], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcParameterValue_type)), false),
            new attribute(strings[2964], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcParameterValue_type)), false),
            new attribute(strings[2955], new named_type(IFC4X3_RC4_IfcKnotType_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBeam_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBeamTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBeamStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBeamType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBeamTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBearing_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBearingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBearingType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBearingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBlobTexture_type->set_attributes({
            new attribute(strings[2965], new named_type(IFC4X3_RC4_IfcIdentifier_type), false),
            new attribute(strings[2966], new named_type(IFC4X3_RC4_IfcBinary_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBlock_type->set_attributes({
            new attribute(strings[2967], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2968], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2969], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcBoiler_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBoilerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBoilerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBoilerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBooleanClippingResult_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcBooleanResult_type->set_attributes({
            new attribute(strings[2970], new named_type(IFC4X3_RC4_IfcBooleanOperator_type), false),
            new attribute(strings[2971], new named_type(IFC4X3_RC4_IfcBooleanOperand_type), false),
            new attribute(strings[2972], new named_type(IFC4X3_RC4_IfcBooleanOperand_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcBorehole_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBoundaryCondition_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_RC4_IfcBoundaryCurve_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_RC4_IfcBoundaryEdgeCondition_type->set_attributes({
            new attribute(strings[2973], new named_type(IFC4X3_RC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2974], new named_type(IFC4X3_RC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2975], new named_type(IFC4X3_RC4_IfcModulusOfTranslationalSubgradeReactionSelect_type), true),
            new attribute(strings[2976], new named_type(IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true),
            new attribute(strings[2977], new named_type(IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true),
            new attribute(strings[2978], new named_type(IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBoundaryFaceCondition_type->set_attributes({
            new attribute(strings[2979], new named_type(IFC4X3_RC4_IfcModulusOfSubgradeReactionSelect_type), true),
            new attribute(strings[2980], new named_type(IFC4X3_RC4_IfcModulusOfSubgradeReactionSelect_type), true),
            new attribute(strings[2981], new named_type(IFC4X3_RC4_IfcModulusOfSubgradeReactionSelect_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcBoundaryNodeCondition_type->set_attributes({
            new attribute(strings[2982], new named_type(IFC4X3_RC4_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2983], new named_type(IFC4X3_RC4_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2984], new named_type(IFC4X3_RC4_IfcTranslationalStiffnessSelect_type), true),
            new attribute(strings[2985], new named_type(IFC4X3_RC4_IfcRotationalStiffnessSelect_type), true),
            new attribute(strings[2986], new named_type(IFC4X3_RC4_IfcRotationalStiffnessSelect_type), true),
            new attribute(strings[2987], new named_type(IFC4X3_RC4_IfcRotationalStiffnessSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBoundaryNodeConditionWarping_type->set_attributes({
            new attribute(strings[2988], new named_type(IFC4X3_RC4_IfcWarpingStiffnessSelect_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBoundedCurve_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcBoundedSurface_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcBoundingBox_type->set_attributes({
            new attribute(strings[2989], new named_type(IFC4X3_RC4_IfcCartesianPoint_type), false),
            new attribute(strings[2990], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2991], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2992], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcBoxedHalfSpace_type->set_attributes({
            new attribute(strings[2993], new named_type(IFC4X3_RC4_IfcBoundingBox_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcBridge_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBridgeTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuilding_type->set_attributes({
            new attribute(strings[2994], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[2995], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[2996], new named_type(IFC4X3_RC4_IfcPostalAddress_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuildingElementPart_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBuildingElementPartTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuildingElementPartType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBuildingElementPartTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuildingElementProxy_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBuildingElementProxyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuildingElementProxyType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBuildingElementProxyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuildingStorey_type->set_attributes({
            new attribute(strings[2997], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuildingSystem_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBuildingSystemTypeEnum_type), true),
            new attribute(strings[2998], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuiltElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuiltElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBuiltSystem_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBuiltSystemTypeEnum_type), true),
            new attribute(strings[2998], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBurner_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBurnerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcBurnerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcBurnerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCShapeProfileDef_type->set_attributes({
            new attribute(strings[2999], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3000], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3001], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3002], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3003], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCableCarrierFitting_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCableCarrierFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCableCarrierFittingType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCableCarrierFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCableCarrierSegment_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCableCarrierSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCableCarrierSegmentType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCableCarrierSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCableFitting_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCableFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCableFittingType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCableFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCableSegment_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCableSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCableSegmentType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCableSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCaissonFoundation_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCaissonFoundationTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCaissonFoundationType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCaissonFoundationTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCartesianPoint_type->set_attributes({
            new attribute(strings[3004], new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC4X3_RC4_IfcLengthMeasure_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcCartesianPointList_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcCartesianPointList2D_type->set_attributes({
            new attribute(strings[3005], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_RC4_IfcLengthMeasure_type))), false),
            new attribute(strings[3006], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcCartesianPointList3D_type->set_attributes({
            new attribute(strings[3005], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_RC4_IfcLengthMeasure_type))), false),
            new attribute(strings[3006], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcCartesianTransformationOperator_type->set_attributes({
            new attribute(strings[3007], new named_type(IFC4X3_RC4_IfcDirection_type), true),
            new attribute(strings[3008], new named_type(IFC4X3_RC4_IfcDirection_type), true),
            new attribute(strings[3009], new named_type(IFC4X3_RC4_IfcCartesianPoint_type), false),
            new attribute(strings[3010], new named_type(IFC4X3_RC4_IfcReal_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcCartesianTransformationOperator2D_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcCartesianTransformationOperator2DnonUniform_type->set_attributes({
            new attribute(strings[3011], new named_type(IFC4X3_RC4_IfcReal_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcCartesianTransformationOperator3D_type->set_attributes({
            new attribute(strings[3012], new named_type(IFC4X3_RC4_IfcDirection_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcCartesianTransformationOperator3DnonUniform_type->set_attributes({
            new attribute(strings[3011], new named_type(IFC4X3_RC4_IfcReal_type), true),
            new attribute(strings[3013], new named_type(IFC4X3_RC4_IfcReal_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCenterLineProfileDef_type->set_attributes({
            new attribute(strings[3014], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcChiller_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcChillerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcChillerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcChillerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcChimney_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcChimneyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcChimneyType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcChimneyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCircle_type->set_attributes({
            new attribute(strings[3015], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcCircleHollowProfileDef_type->set_attributes({
            new attribute(strings[3001], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcCircleProfileDef_type->set_attributes({
            new attribute(strings[3015], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcCivilElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCivilElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcClassification_type->set_attributes({
            new attribute(strings[3016], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3017], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3018], new named_type(IFC4X3_RC4_IfcDate_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3019], new named_type(IFC4X3_RC4_IfcURIReference_type), true),
            new attribute(strings[3020], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcIdentifier_type)), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcClassificationReference_type->set_attributes({
            new attribute(strings[3021], new named_type(IFC4X3_RC4_IfcClassificationReferenceSelect_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3022], new named_type(IFC4X3_RC4_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcClosedShell_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcClothoid_type->set_attributes({
            new attribute(strings[3023], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcCoil_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCoilTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCoilType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCoilTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcColourRgb_type->set_attributes({
            new attribute(strings[3024], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), false),
            new attribute(strings[3025], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), false),
            new attribute(strings[3026], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcColourRgbList_type->set_attributes({
            new attribute(strings[3027], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type))), false)
    },{
            false
    });
    IFC4X3_RC4_IfcColourSpecification_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_RC4_IfcColumn_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcColumnTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcColumnStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcColumnType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcColumnTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCommunicationsAppliance_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCommunicationsApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCommunicationsApplianceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCommunicationsApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcComplexProperty_type->set_attributes({
            new attribute(strings[3028], new named_type(IFC4X3_RC4_IfcIdentifier_type), false),
            new attribute(strings[3029], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcProperty_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcComplexPropertyTemplate_type->set_attributes({
            new attribute(strings[3028], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3030], new named_type(IFC4X3_RC4_IfcComplexPropertyTemplateTypeEnum_type), true),
            new attribute(strings[3031], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPropertyTemplate_type)), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCompositeCurve_type->set_attributes({
            new attribute(strings[3032], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcSegment_type)), false),
            new attribute(strings[2952], new named_type(IFC4X3_RC4_IfcLogical_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcCompositeCurveOnSurface_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_RC4_IfcCompositeCurveSegment_type->set_attributes({
            new attribute(strings[3033], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3034], new named_type(IFC4X3_RC4_IfcCurve_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcCompositeProfileDef_type->set_attributes({
            new attribute(strings[3035], new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC4X3_RC4_IfcProfileDef_type)), false),
            new attribute(strings[3036], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcCompressor_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCompressorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCompressorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCompressorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCondenser_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCondenserTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCondenserType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCondenserTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConic_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcConnectedFaceSet_type->set_attributes({
            new attribute(strings[3038], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcFace_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcConnectionCurveGeometry_type->set_attributes({
            new attribute(strings[3039], new named_type(IFC4X3_RC4_IfcCurveOrEdgeCurve_type), false),
            new attribute(strings[3040], new named_type(IFC4X3_RC4_IfcCurveOrEdgeCurve_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcConnectionGeometry_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcConnectionPointEccentricity_type->set_attributes({
            new attribute(strings[3041], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3042], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3043], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcConnectionPointGeometry_type->set_attributes({
            new attribute(strings[3044], new named_type(IFC4X3_RC4_IfcPointOrVertexPoint_type), false),
            new attribute(strings[3045], new named_type(IFC4X3_RC4_IfcPointOrVertexPoint_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcConnectionSurfaceGeometry_type->set_attributes({
            new attribute(strings[3046], new named_type(IFC4X3_RC4_IfcSurfaceOrFaceSurface_type), false),
            new attribute(strings[3047], new named_type(IFC4X3_RC4_IfcSurfaceOrFaceSurface_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcConnectionVolumeGeometry_type->set_attributes({
            new attribute(strings[3048], new named_type(IFC4X3_RC4_IfcSolidOrShell_type), false),
            new attribute(strings[3049], new named_type(IFC4X3_RC4_IfcSolidOrShell_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcConstraint_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3050], new named_type(IFC4X3_RC4_IfcConstraintEnum_type), false),
            new attribute(strings[3051], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3052], new named_type(IFC4X3_RC4_IfcActorSelect_type), true),
            new attribute(strings[3053], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3054], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConstructionEquipmentResource_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcConstructionEquipmentResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConstructionEquipmentResourceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcConstructionEquipmentResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConstructionMaterialResource_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcConstructionMaterialResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConstructionMaterialResourceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcConstructionMaterialResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConstructionProductResource_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcConstructionProductResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConstructionProductResourceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcConstructionProductResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConstructionResource_type->set_attributes({
            new attribute(strings[3055], new named_type(IFC4X3_RC4_IfcResourceTime_type), true),
            new attribute(strings[3056], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcAppliedValue_type)), true),
            new attribute(strings[3057], new named_type(IFC4X3_RC4_IfcPhysicalQuantity_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConstructionResourceType_type->set_attributes({
            new attribute(strings[3056], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcAppliedValue_type)), true),
            new attribute(strings[3057], new named_type(IFC4X3_RC4_IfcPhysicalQuantity_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcContext_type->set_attributes({
            new attribute(strings[3058], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2998], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3059], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3060], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcRepresentationContext_type)), true),
            new attribute(strings[3061], new named_type(IFC4X3_RC4_IfcUnitAssignment_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcContextDependentUnit_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcControl_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcController_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcControllerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcControllerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcControllerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConversionBasedUnit_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[3062], new named_type(IFC4X3_RC4_IfcMeasureWithUnit_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcConversionBasedUnitWithOffset_type->set_attributes({
            new attribute(strings[3063], new named_type(IFC4X3_RC4_IfcReal_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcConveyorSegment_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcConveyorSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcConveyorSegmentType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcConveyorSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCooledBeam_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCooledBeamTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCooledBeamType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCooledBeamTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCoolingTower_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCoolingTowerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCoolingTowerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCoolingTowerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCoordinateOperation_type->set_attributes({
            new attribute(strings[3064], new named_type(IFC4X3_RC4_IfcCoordinateReferenceSystemSelect_type), false),
            new attribute(strings[3065], new named_type(IFC4X3_RC4_IfcCoordinateReferenceSystem_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcCoordinateReferenceSystem_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3066], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3067], new named_type(IFC4X3_RC4_IfcIdentifier_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcCosine_type->set_attributes({
            new attribute(strings[3068], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3069], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcCostItem_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCostItemTypeEnum_type), true),
            new attribute(strings[3070], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcCostValue_type)), true),
            new attribute(strings[3071], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcPhysicalQuantity_type)), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCostSchedule_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCostScheduleTypeEnum_type), true),
            new attribute(strings[2870], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3072], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3073], new named_type(IFC4X3_RC4_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCostValue_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCourse_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCourseTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCourseType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCourseTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCovering_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCoveringTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCoveringType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCoveringTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCrewResource_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCrewResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCrewResourceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCrewResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCsgPrimitive3D_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcCsgSolid_type->set_attributes({
            new attribute(strings[3074], new named_type(IFC4X3_RC4_IfcCsgSelect_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcCurrencyRelationship_type->set_attributes({
            new attribute(strings[3075], new named_type(IFC4X3_RC4_IfcMonetaryUnit_type), false),
            new attribute(strings[3076], new named_type(IFC4X3_RC4_IfcMonetaryUnit_type), false),
            new attribute(strings[3077], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), false),
            new attribute(strings[3078], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3079], new named_type(IFC4X3_RC4_IfcLibraryInformation_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCurtainWall_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCurtainWallTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCurtainWallType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcCurtainWallTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcCurve_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcCurveBoundedPlane_type->set_attributes({
            new attribute(strings[3080], new named_type(IFC4X3_RC4_IfcPlane_type), false),
            new attribute(strings[2899], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[2900], new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X3_RC4_IfcCurve_type)), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcCurveBoundedSurface_type->set_attributes({
            new attribute(strings[3080], new named_type(IFC4X3_RC4_IfcSurface_type), false),
            new attribute(strings[3081], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcBoundaryCurve_type)), false),
            new attribute(strings[3082], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcCurveSegment_type->set_attributes({
            new attribute(strings[3083], new named_type(IFC4X3_RC4_IfcPlacement_type), false),
            new attribute(strings[3084], new named_type(IFC4X3_RC4_IfcCurveMeasureSelect_type), false),
            new attribute(strings[2890], new named_type(IFC4X3_RC4_IfcCurveMeasureSelect_type), false),
            new attribute(strings[3034], new named_type(IFC4X3_RC4_IfcCurve_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcCurveStyle_type->set_attributes({
            new attribute(strings[3085], new named_type(IFC4X3_RC4_IfcCurveFontOrScaledCurveFontSelect_type), true),
            new attribute(strings[3086], new named_type(IFC4X3_RC4_IfcSizeSelect_type), true),
            new attribute(strings[3087], new named_type(IFC4X3_RC4_IfcColour_type), true),
            new attribute(strings[3088], new named_type(IFC4X3_RC4_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcCurveStyleFont_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3089], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcCurveStyleFontPattern_type)), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcCurveStyleFontAndScaling_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3085], new named_type(IFC4X3_RC4_IfcCurveStyleFontSelect_type), false),
            new attribute(strings[3090], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcCurveStyleFontPattern_type->set_attributes({
            new attribute(strings[3091], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3092], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcCylindricalSurface_type->set_attributes({
            new attribute(strings[3015], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcDamper_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDamperTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDamperType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDamperTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDeepFoundation_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDeepFoundationType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDerivedProfileDef_type->set_attributes({
            new attribute(strings[3093], new named_type(IFC4X3_RC4_IfcProfileDef_type), false),
            new attribute(strings[2970], new named_type(IFC4X3_RC4_IfcCartesianTransformationOperator2D_type), false),
            new attribute(strings[3036], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcDerivedUnit_type->set_attributes({
            new attribute(strings[3094], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcDerivedUnitElement_type)), false),
            new attribute(strings[3095], new named_type(IFC4X3_RC4_IfcDerivedUnitEnum_type), false),
            new attribute(strings[3096], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcDerivedUnitElement_type->set_attributes({
            new attribute(strings[3097], new named_type(IFC4X3_RC4_IfcNamedUnit_type), false),
            new attribute(strings[3098], new simple_type(simple_type::integer_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcDimensionalExponents_type->set_attributes({
            new attribute(strings[3099], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3100], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3101], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3102], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3103], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3104], new simple_type(simple_type::integer_type), false),
            new attribute(strings[3105], new simple_type(simple_type::integer_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDirection_type->set_attributes({
            new attribute(strings[3106], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X3_RC4_IfcReal_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcDirectrixCurveSweptAreaSolid_type->set_attributes({
            new attribute(strings[3107], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3108], new named_type(IFC4X3_RC4_IfcCurveMeasureSelect_type), true),
            new attribute(strings[3109], new named_type(IFC4X3_RC4_IfcCurveMeasureSelect_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcDirectrixDerivedReferenceSweptAreaSolid_type->set_attributes({
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDiscreteAccessory_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDiscreteAccessoryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDiscreteAccessoryType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDiscreteAccessoryTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionBoard_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDistributionBoardTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionBoardType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDistributionBoardTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionChamberElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDistributionChamberElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionChamberElementType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDistributionChamberElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionCircuit_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionControlElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionControlElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionFlowElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionFlowElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionPort_type->set_attributes({
            new attribute(strings[3110], new named_type(IFC4X3_RC4_IfcFlowDirectionEnum_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDistributionPortTypeEnum_type), true),
            new attribute(strings[3111], new named_type(IFC4X3_RC4_IfcDistributionSystemEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDistributionSystem_type->set_attributes({
            new attribute(strings[2998], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDistributionSystemEnum_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDocumentInformation_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), false),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3019], new named_type(IFC4X3_RC4_IfcURIReference_type), true),
            new attribute(strings[2876], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3112], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3113], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3114], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3115], new named_type(IFC4X3_RC4_IfcActorSelect_type), true),
            new attribute(strings[3116], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcActorSelect_type)), true),
            new attribute(strings[3053], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3117], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3118], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3119], new named_type(IFC4X3_RC4_IfcDate_type), true),
            new attribute(strings[3120], new named_type(IFC4X3_RC4_IfcDate_type), true),
            new attribute(strings[3121], new named_type(IFC4X3_RC4_IfcDocumentConfidentialityEnum_type), true),
            new attribute(strings[2870], new named_type(IFC4X3_RC4_IfcDocumentStatusEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDocumentInformationRelationship_type->set_attributes({
            new attribute(strings[3122], new named_type(IFC4X3_RC4_IfcDocumentInformation_type), false),
            new attribute(strings[3123], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcDocumentInformation_type)), false),
            new attribute(strings[3124], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcDocumentReference_type->set_attributes({
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3125], new named_type(IFC4X3_RC4_IfcDocumentInformation_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcDoor_type->set_attributes({
            new attribute(strings[3126], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3127], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDoorTypeEnum_type), true),
            new attribute(strings[3128], new named_type(IFC4X3_RC4_IfcDoorTypeOperationEnum_type), true),
            new attribute(strings[3129], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDoorLiningProperties_type->set_attributes({
            new attribute(strings[3130], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3131], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3132], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3133], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3134], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3135], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3136], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3137], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3138], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3139], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3140], new named_type(IFC4X3_RC4_IfcShapeAspect_type), true),
            new attribute(strings[3141], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3142], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDoorPanelProperties_type->set_attributes({
            new attribute(strings[3143], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3144], new named_type(IFC4X3_RC4_IfcDoorPanelOperationEnum_type), false),
            new attribute(strings[3145], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3146], new named_type(IFC4X3_RC4_IfcDoorPanelPositionEnum_type), false),
            new attribute(strings[3140], new named_type(IFC4X3_RC4_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDoorStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDoorStyle_type->set_attributes({
            new attribute(strings[3128], new named_type(IFC4X3_RC4_IfcDoorStyleOperationEnum_type), false),
            new attribute(strings[3147], new named_type(IFC4X3_RC4_IfcDoorStyleConstructionEnum_type), false),
            new attribute(strings[3148], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3149], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDoorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDoorTypeEnum_type), false),
            new attribute(strings[3128], new named_type(IFC4X3_RC4_IfcDoorTypeOperationEnum_type), false),
            new attribute(strings[3148], new named_type(IFC4X3_RC4_IfcBoolean_type), true),
            new attribute(strings[3129], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDraughtingPreDefinedColour_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcDraughtingPreDefinedCurveFont_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcDuctFitting_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDuctFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDuctFittingType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDuctFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDuctSegment_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDuctSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDuctSegmentType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDuctSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDuctSilencer_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDuctSilencerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcDuctSilencerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcDuctSilencerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEarthworksCut_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEarthworksCutTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEarthworksElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEarthworksFill_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEarthworksFillTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEdge_type->set_attributes({
            new attribute(strings[3150], new named_type(IFC4X3_RC4_IfcVertex_type), false),
            new attribute(strings[3151], new named_type(IFC4X3_RC4_IfcVertex_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcEdgeCurve_type->set_attributes({
            new attribute(strings[3152], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3033], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcEdgeLoop_type->set_attributes({
            new attribute(strings[3153], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcOrientedEdge_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcElectricAppliance_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricApplianceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricDistributionBoard_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricDistributionBoardTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricDistributionBoardType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricDistributionBoardTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricFlowStorageDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricFlowStorageDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricFlowStorageDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricFlowStorageDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricFlowTreatmentDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricFlowTreatmentDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricFlowTreatmentDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricFlowTreatmentDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricGenerator_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricGeneratorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricGeneratorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricGeneratorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricMotor_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricMotorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricMotorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricMotorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricTimeControl_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricTimeControlTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElectricTimeControlType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElectricTimeControlTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElement_type->set_attributes({
            new attribute(strings[3154], new named_type(IFC4X3_RC4_IfcIdentifier_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElementAssembly_type->set_attributes({
            new attribute(strings[3155], new named_type(IFC4X3_RC4_IfcAssemblyPlaceEnum_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElementAssemblyTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElementAssemblyType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcElementAssemblyTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElementComponent_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElementComponentType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElementQuantity_type->set_attributes({
            new attribute(strings[3156], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3157], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPhysicalQuantity_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElementType_type->set_attributes({
            new attribute(strings[3158], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcElementarySurface_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcEllipse_type->set_attributes({
            new attribute(strings[3159], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3160], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcEllipseProfileDef_type->set_attributes({
            new attribute(strings[3159], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3160], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcEnergyConversionDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEnergyConversionDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEngine_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEngineTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEngineType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEngineTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEvaporativeCooler_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEvaporativeCoolerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEvaporativeCoolerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEvaporativeCoolerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEvaporator_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEvaporatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEvaporatorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEvaporatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEvent_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEventTypeEnum_type), true),
            new attribute(strings[3161], new named_type(IFC4X3_RC4_IfcEventTriggerTypeEnum_type), true),
            new attribute(strings[3162], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3163], new named_type(IFC4X3_RC4_IfcEventTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEventTime_type->set_attributes({
            new attribute(strings[3164], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3165], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3166], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3167], new named_type(IFC4X3_RC4_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcEventType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcEventTypeEnum_type), false),
            new attribute(strings[3161], new named_type(IFC4X3_RC4_IfcEventTriggerTypeEnum_type), false),
            new attribute(strings[3162], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcExtendedProperties_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3168], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcProperty_type)), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcExternalInformation_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcExternalReference_type->set_attributes({
            new attribute(strings[3019], new named_type(IFC4X3_RC4_IfcURIReference_type), true),
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcExternalReferenceRelationship_type->set_attributes({
            new attribute(strings[3169], new named_type(IFC4X3_RC4_IfcExternalReference_type), false),
            new attribute(strings[3170], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcResourceObjectSelect_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcExternalSpatialElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcExternalSpatialElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcExternalSpatialStructureElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcExternallyDefinedHatchStyle_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcExternallyDefinedSurfaceStyle_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcExternallyDefinedTextFont_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcExtrudedAreaSolid_type->set_attributes({
            new attribute(strings[3171], new named_type(IFC4X3_RC4_IfcDirection_type), false),
            new attribute(strings[2999], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcExtrudedAreaSolidTapered_type->set_attributes({
            new attribute(strings[3172], new named_type(IFC4X3_RC4_IfcProfileDef_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcFace_type->set_attributes({
            new attribute(strings[3173], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcFaceBound_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcFaceBasedSurfaceModel_type->set_attributes({
            new attribute(strings[3174], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcConnectedFaceSet_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcFaceBound_type->set_attributes({
            new attribute(strings[3175], new named_type(IFC4X3_RC4_IfcLoop_type), false),
            new attribute(strings[3176], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcFaceOuterBound_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_RC4_IfcFaceSurface_type->set_attributes({
            new attribute(strings[3177], new named_type(IFC4X3_RC4_IfcSurface_type), false),
            new attribute(strings[3033], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcFacetedBrep_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcFacetedBrepWithVoids_type->set_attributes({
            new attribute(strings[2878], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcClosedShell_type)), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcFacility_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFacilityPart_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFacilityPartTypeSelect_type), false),
            new attribute(strings[3178], new named_type(IFC4X3_RC4_IfcFacilityUsageEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFailureConnectionCondition_type->set_attributes({
            new attribute(strings[3179], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3180], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3181], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3182], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3183], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3184], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFan_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFanTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFanType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFanTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFastener_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFastenerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFastenerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFastenerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFeatureElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFeatureElementAddition_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFeatureElementSubtraction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFillAreaStyle_type->set_attributes({
            new attribute(strings[3185], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcFillStyleSelect_type)), false),
            new attribute(strings[3088], new named_type(IFC4X3_RC4_IfcBoolean_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcFillAreaStyleHatching_type->set_attributes({
            new attribute(strings[3186], new named_type(IFC4X3_RC4_IfcCurveStyle_type), false),
            new attribute(strings[3187], new named_type(IFC4X3_RC4_IfcHatchLineDistanceSelect_type), false),
            new attribute(strings[3188], new named_type(IFC4X3_RC4_IfcCartesianPoint_type), true),
            new attribute(strings[3189], new named_type(IFC4X3_RC4_IfcCartesianPoint_type), true),
            new attribute(strings[3190], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcFillAreaStyleTiles_type->set_attributes({
            new attribute(strings[3191], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_RC4_IfcVector_type)), false),
            new attribute(strings[3192], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcStyledItem_type)), false),
            new attribute(strings[3193], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcFilter_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFilterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFilterType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFilterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFireSuppressionTerminal_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFireSuppressionTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFireSuppressionTerminalType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFireSuppressionTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFixedReferenceSweptAreaSolid_type->set_attributes({
            new attribute(strings[3194], new named_type(IFC4X3_RC4_IfcDirection_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowController_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowControllerType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowFitting_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowFittingType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowInstrument_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFlowInstrumentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowInstrumentType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFlowInstrumentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowMeter_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFlowMeterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowMeterType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFlowMeterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowMovingDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowMovingDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowSegment_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowSegmentType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowStorageDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowStorageDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowTerminal_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowTerminalType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowTreatmentDevice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFlowTreatmentDeviceType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFooting_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFootingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFootingType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFootingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFurnishingElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFurnishingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFurniture_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFurnitureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcFurnitureType_type->set_attributes({
            new attribute(strings[3155], new named_type(IFC4X3_RC4_IfcAssemblyPlaceEnum_type), false),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcFurnitureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGeographicElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcGeographicElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGeographicElementType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcGeographicElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGeometricCurveSet_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcGeometricRepresentationContext_type->set_attributes({
            new attribute(strings[3195], new named_type(IFC4X3_RC4_IfcDimensionCount_type), false),
            new attribute(strings[3196], new named_type(IFC4X3_RC4_IfcReal_type), true),
            new attribute(strings[3197], new named_type(IFC4X3_RC4_IfcAxis2Placement_type), false),
            new attribute(strings[3198], new named_type(IFC4X3_RC4_IfcDirection_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGeometricRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcGeometricRepresentationSubContext_type->set_attributes({
            new attribute(strings[3199], new named_type(IFC4X3_RC4_IfcGeometricRepresentationContext_type), false),
            new attribute(strings[3200], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3201], new named_type(IFC4X3_RC4_IfcGeometricProjectionEnum_type), false),
            new attribute(strings[3202], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, true, true, true, true, false, false, false, false
    });
    IFC4X3_RC4_IfcGeometricSet_type->set_attributes({
            new attribute(strings[3094], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcGeometricSetSelect_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcGeomodel_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGeoslice_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGeotechnicalAssembly_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGeotechnicalElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGeotechnicalStratum_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGradientCurve_type->set_attributes({
            new attribute(strings[3203], new named_type(IFC4X3_RC4_IfcBoundedCurve_type), false),
            new attribute(strings[3204], new named_type(IFC4X3_RC4_IfcPlacement_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcGrid_type->set_attributes({
            new attribute(strings[3205], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcGridAxis_type)), false),
            new attribute(strings[3206], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcGridAxis_type)), false),
            new attribute(strings[3207], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcGridAxis_type)), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcGridTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcGridAxis_type->set_attributes({
            new attribute(strings[3208], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3209], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3033], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcGridPlacement_type->set_attributes({
            new attribute(strings[3210], new named_type(IFC4X3_RC4_IfcVirtualGridIntersection_type), false),
            new attribute(strings[3211], new named_type(IFC4X3_RC4_IfcGridPlacementDirectionSelect_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcGroup_type->set_attributes({
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcHalfSpaceSolid_type->set_attributes({
            new attribute(strings[3212], new named_type(IFC4X3_RC4_IfcSurface_type), false),
            new attribute(strings[3213], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcHeatExchanger_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcHeatExchangerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcHeatExchangerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcHeatExchangerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcHumidifier_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcHumidifierTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcHumidifierType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcHumidifierTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcIShapeProfileDef_type->set_attributes({
            new attribute(strings[3127], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2935], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2936], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3214], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3215], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3216], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3217], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcImageTexture_type->set_attributes({
            new attribute(strings[3218], new named_type(IFC4X3_RC4_IfcURIReference_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcImpactProtectionDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcImpactProtectionDeviceTypeSelect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcImpactProtectionDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcImpactProtectionDeviceTypeSelect_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcIndexedColourMap_type->set_attributes({
            new attribute(strings[3219], new named_type(IFC4X3_RC4_IfcTessellatedFaceSet_type), false),
            new attribute(strings[3220], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3221], new named_type(IFC4X3_RC4_IfcColourRgbList_type), false),
            new attribute(strings[3222], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcPositiveInteger_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcIndexedPolyCurve_type->set_attributes({
            new attribute(strings[3223], new named_type(IFC4X3_RC4_IfcCartesianPointList_type), false),
            new attribute(strings[3032], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcSegmentIndexSelect_type)), true),
            new attribute(strings[2952], new named_type(IFC4X3_RC4_IfcBoolean_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcIndexedPolygonalFace_type->set_attributes({
            new attribute(strings[3224], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_RC4_IfcPositiveInteger_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcIndexedPolygonalFaceWithVoids_type->set_attributes({
            new attribute(strings[3225], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_RC4_IfcPositiveInteger_type))), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcIndexedTextureMap_type->set_attributes({
            new attribute(strings[3219], new named_type(IFC4X3_RC4_IfcTessellatedFaceSet_type), false),
            new attribute(strings[3226], new named_type(IFC4X3_RC4_IfcTextureVertexList_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcIndexedTriangleTextureMap_type->set_attributes({
            new attribute(strings[3227], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_RC4_IfcPositiveInteger_type))), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcInterceptor_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcInterceptorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcInterceptorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcInterceptorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcIntersectionCurve_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcInventory_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcInventoryTypeEnum_type), true),
            new attribute(strings[3228], new named_type(IFC4X3_RC4_IfcActorSelect_type), true),
            new attribute(strings[3229], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPerson_type)), true),
            new attribute(strings[3230], new named_type(IFC4X3_RC4_IfcDate_type), true),
            new attribute(strings[2927], new named_type(IFC4X3_RC4_IfcCostValue_type), true),
            new attribute(strings[2926], new named_type(IFC4X3_RC4_IfcCostValue_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcIrregularTimeSeries_type->set_attributes({
            new attribute(strings[3231], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcIrregularTimeSeriesValue_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcIrregularTimeSeriesValue_type->set_attributes({
            new attribute(strings[3232], new named_type(IFC4X3_RC4_IfcDateTime_type), false),
            new attribute(strings[3233], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcValue_type)), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcJunctionBox_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcJunctionBoxTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcJunctionBoxType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcJunctionBoxTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcKerb_type->set_attributes({
            new attribute(strings[3234], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcKerbType_type->set_attributes({
            new attribute(strings[3234], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLShapeProfileDef_type->set_attributes({
            new attribute(strings[2999], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3000], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3014], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3215], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3235], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3236], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLaborResource_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLaborResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLaborResourceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLaborResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLagTime_type->set_attributes({
            new attribute(strings[3237], new named_type(IFC4X3_RC4_IfcTimeOrRatioSelect_type), false),
            new attribute(strings[3238], new named_type(IFC4X3_RC4_IfcTaskDurationEnum_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcLamp_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLampTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLampType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLampTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLibraryInformation_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2902], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3239], new named_type(IFC4X3_RC4_IfcActorSelect_type), true),
            new attribute(strings[3240], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3019], new named_type(IFC4X3_RC4_IfcURIReference_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLibraryReference_type->set_attributes({
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3241], new named_type(IFC4X3_RC4_IfcLanguageId_type), true),
            new attribute(strings[3242], new named_type(IFC4X3_RC4_IfcLibraryInformation_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLightDistributionData_type->set_attributes({
            new attribute(strings[3243], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), false),
            new attribute(strings[3244], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type)), false),
            new attribute(strings[3245], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLuminousIntensityDistributionMeasure_type)), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcLightFixture_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLightFixtureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLightFixtureType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLightFixtureTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLightIntensityDistribution_type->set_attributes({
            new attribute(strings[3246], new named_type(IFC4X3_RC4_IfcLightDistributionCurveEnum_type), false),
            new attribute(strings[3247], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLightDistributionData_type)), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcLightSource_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3248], new named_type(IFC4X3_RC4_IfcColourRgb_type), false),
            new attribute(strings[3249], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3250], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcLightSourceAmbient_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcLightSourceDirectional_type->set_attributes({
            new attribute(strings[3176], new named_type(IFC4X3_RC4_IfcDirection_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcLightSourceGoniometric_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), false),
            new attribute(strings[3251], new named_type(IFC4X3_RC4_IfcColourRgb_type), true),
            new attribute(strings[3252], new named_type(IFC4X3_RC4_IfcThermodynamicTemperatureMeasure_type), false),
            new attribute(strings[3253], new named_type(IFC4X3_RC4_IfcLuminousFluxMeasure_type), false),
            new attribute(strings[3254], new named_type(IFC4X3_RC4_IfcLightEmissionSourceEnum_type), false),
            new attribute(strings[3255], new named_type(IFC4X3_RC4_IfcLightDistributionDataSourceSelect_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLightSourcePositional_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcCartesianPoint_type), false),
            new attribute(strings[3015], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3256], new named_type(IFC4X3_RC4_IfcReal_type), false),
            new attribute(strings[3257], new named_type(IFC4X3_RC4_IfcReal_type), false),
            new attribute(strings[3258], new named_type(IFC4X3_RC4_IfcReal_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLightSourceSpot_type->set_attributes({
            new attribute(strings[3176], new named_type(IFC4X3_RC4_IfcDirection_type), false),
            new attribute(strings[3259], new named_type(IFC4X3_RC4_IfcReal_type), true),
            new attribute(strings[3260], new named_type(IFC4X3_RC4_IfcPositivePlaneAngleMeasure_type), false),
            new attribute(strings[3261], new named_type(IFC4X3_RC4_IfcPositivePlaneAngleMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLine_type->set_attributes({
            new attribute(strings[3262], new named_type(IFC4X3_RC4_IfcCartesianPoint_type), false),
            new attribute(strings[3263], new named_type(IFC4X3_RC4_IfcVector_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcLinearElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLinearPlacement_type->set_attributes({
            new attribute(strings[3264], new named_type(IFC4X3_RC4_IfcAxis2PlacementLinear_type), false),
            new attribute(strings[3265], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcLinearPositioningElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLiquidTerminal_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLiquidTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLiquidTerminalType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLiquidTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcLocalPlacement_type->set_attributes({
            new attribute(strings[3264], new named_type(IFC4X3_RC4_IfcAxis2Placement_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcLoop_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcManifoldSolidBrep_type->set_attributes({
            new attribute(strings[3266], new named_type(IFC4X3_RC4_IfcClosedShell_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcMapConversion_type->set_attributes({
            new attribute(strings[3267], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3268], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3269], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3270], new named_type(IFC4X3_RC4_IfcReal_type), true),
            new attribute(strings[3271], new named_type(IFC4X3_RC4_IfcReal_type), true),
            new attribute(strings[3010], new named_type(IFC4X3_RC4_IfcReal_type), true),
            new attribute(strings[3272], new named_type(IFC4X3_RC4_IfcReal_type), true),
            new attribute(strings[3273], new named_type(IFC4X3_RC4_IfcReal_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMappedItem_type->set_attributes({
            new attribute(strings[3274], new named_type(IFC4X3_RC4_IfcRepresentationMap_type), false),
            new attribute(strings[3275], new named_type(IFC4X3_RC4_IfcCartesianTransformationOperator_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcMarineFacility_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMarineFacilityTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterial_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[2910], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcMaterialClassificationRelationship_type->set_attributes({
            new attribute(strings[3276], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcClassificationSelect_type)), false),
            new attribute(strings[3277], new named_type(IFC4X3_RC4_IfcMaterial_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcMaterialConstituent_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3278], new named_type(IFC4X3_RC4_IfcMaterial_type), false),
            new attribute(strings[3279], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[2910], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialConstituentSet_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3280], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcMaterialConstituent_type)), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcMaterialDefinition_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcMaterialDefinitionRepresentation_type->set_attributes({
            new attribute(strings[3281], new named_type(IFC4X3_RC4_IfcMaterial_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialLayer_type->set_attributes({
            new attribute(strings[3278], new named_type(IFC4X3_RC4_IfcMaterial_type), true),
            new attribute(strings[3282], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), false),
            new attribute(strings[3283], new named_type(IFC4X3_RC4_IfcLogical_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[2910], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3284], new named_type(IFC4X3_RC4_IfcInteger_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialLayerSet_type->set_attributes({
            new attribute(strings[3285], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcMaterialLayer_type)), false),
            new attribute(strings[3286], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcMaterialLayerSetUsage_type->set_attributes({
            new attribute(strings[3287], new named_type(IFC4X3_RC4_IfcMaterialLayerSet_type), false),
            new attribute(strings[3288], new named_type(IFC4X3_RC4_IfcLayerSetDirectionEnum_type), false),
            new attribute(strings[3289], new named_type(IFC4X3_RC4_IfcDirectionSenseEnum_type), false),
            new attribute(strings[3290], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3291], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialLayerWithOffsets_type->set_attributes({
            new attribute(strings[3292], new named_type(IFC4X3_RC4_IfcLayerSetDirectionEnum_type), false),
            new attribute(strings[3293], new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X3_RC4_IfcLengthMeasure_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialList_type->set_attributes({
            new attribute(strings[3294], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcMaterial_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcMaterialProfile_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3278], new named_type(IFC4X3_RC4_IfcMaterial_type), true),
            new attribute(strings[3295], new named_type(IFC4X3_RC4_IfcProfileDef_type), false),
            new attribute(strings[3284], new named_type(IFC4X3_RC4_IfcInteger_type), true),
            new attribute(strings[2910], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialProfileSet_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3296], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcMaterialProfile_type)), false),
            new attribute(strings[3297], new named_type(IFC4X3_RC4_IfcCompositeProfileDef_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialProfileSetUsage_type->set_attributes({
            new attribute(strings[3298], new named_type(IFC4X3_RC4_IfcMaterialProfileSet_type), false),
            new attribute(strings[3299], new named_type(IFC4X3_RC4_IfcCardinalPointReference_type), true),
            new attribute(strings[3291], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcMaterialProfileSetUsageTapering_type->set_attributes({
            new attribute(strings[3300], new named_type(IFC4X3_RC4_IfcMaterialProfileSet_type), false),
            new attribute(strings[3301], new named_type(IFC4X3_RC4_IfcCardinalPointReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialProfileWithOffsets_type->set_attributes({
            new attribute(strings[3293], new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X3_RC4_IfcLengthMeasure_type)), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialProperties_type->set_attributes({
            new attribute(strings[3278], new named_type(IFC4X3_RC4_IfcMaterialDefinition_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialRelationship_type->set_attributes({
            new attribute(strings[3302], new named_type(IFC4X3_RC4_IfcMaterial_type), false),
            new attribute(strings[3303], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcMaterial_type)), false),
            new attribute(strings[3304], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcMaterialUsageDefinition_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcMeasureWithUnit_type->set_attributes({
            new attribute(strings[3305], new named_type(IFC4X3_RC4_IfcValue_type), false),
            new attribute(strings[3306], new named_type(IFC4X3_RC4_IfcUnit_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcMechanicalFastener_type->set_attributes({
            new attribute(strings[3307], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3308], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMechanicalFastenerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMechanicalFastenerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMechanicalFastenerTypeEnum_type), false),
            new attribute(strings[3307], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3308], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMedicalDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMedicalDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMedicalDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMedicalDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMember_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMemberTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMemberStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMemberType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMemberTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMetric_type->set_attributes({
            new attribute(strings[3309], new named_type(IFC4X3_RC4_IfcBenchmarkEnum_type), false),
            new attribute(strings[3310], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3311], new named_type(IFC4X3_RC4_IfcMetricValueSelect_type), true),
            new attribute(strings[3312], new named_type(IFC4X3_RC4_IfcReference_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMirroredProfileDef_type->set_attributes({
    },{
            false, false, false, true, false
    });
    IFC4X3_RC4_IfcMobileTelecommunicationsAppliance_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMobileTelecommunicationsApplianceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMobileTelecommunicationsApplianceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMobileTelecommunicationsApplianceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMonetaryUnit_type->set_attributes({
            new attribute(strings[3313], new named_type(IFC4X3_RC4_IfcLabel_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcMooringDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMooringDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMooringDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMooringDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMotorConnection_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMotorConnectionTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcMotorConnectionType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcMotorConnectionTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcNamedUnit_type->set_attributes({
            new attribute(strings[3314], new named_type(IFC4X3_RC4_IfcDimensionalExponents_type), false),
            new attribute(strings[3095], new named_type(IFC4X3_RC4_IfcUnitEnum_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcNavigationElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcNavigationElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcNavigationElementType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcNavigationElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcObject_type->set_attributes({
            new attribute(strings[3058], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcObjectDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcObjectPlacement_type->set_attributes({
            new attribute(strings[3315], new named_type(IFC4X3_RC4_IfcObjectPlacement_type), true)
    },{
            false
    });
    IFC4X3_RC4_IfcObjective_type->set_attributes({
            new attribute(strings[3316], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcConstraint_type)), true),
            new attribute(strings[3317], new named_type(IFC4X3_RC4_IfcLogicalOperatorEnum_type), true),
            new attribute(strings[3318], new named_type(IFC4X3_RC4_IfcObjectiveEnum_type), false),
            new attribute(strings[3319], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcOccupant_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcOccupantTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcOffsetCurve_type->set_attributes({
            new attribute(strings[3320], new named_type(IFC4X3_RC4_IfcCurve_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcOffsetCurve2D_type->set_attributes({
            new attribute(strings[3321], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2952], new named_type(IFC4X3_RC4_IfcLogical_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcOffsetCurve3D_type->set_attributes({
            new attribute(strings[3321], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[2952], new named_type(IFC4X3_RC4_IfcLogical_type), false),
            new attribute(strings[2947], new named_type(IFC4X3_RC4_IfcDirection_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcOffsetCurveByDistances_type->set_attributes({
            new attribute(strings[3293], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcPointByDistanceExpression_type)), false),
            new attribute(strings[3154], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcOpenCrossProfileDef_type->set_attributes({
            new attribute(strings[3322], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3323], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type)), false),
            new attribute(strings[3324], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type)), false),
            new attribute(strings[3325], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcOpenShell_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcOpeningElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcOpeningElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcOpeningStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcOrganization_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3326], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcActorRole_type)), true),
            new attribute(strings[3327], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcAddress_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcOrganizationRelationship_type->set_attributes({
            new attribute(strings[3328], new named_type(IFC4X3_RC4_IfcOrganization_type), false),
            new attribute(strings[3329], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcOrganization_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcOrientedEdge_type->set_attributes({
            new attribute(strings[3330], new named_type(IFC4X3_RC4_IfcEdge_type), false),
            new attribute(strings[3176], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            true, true, false, false
    });
    IFC4X3_RC4_IfcOuterBoundaryCurve_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_RC4_IfcOutlet_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcOutletTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcOutletType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcOutletTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcOwnerHistory_type->set_attributes({
            new attribute(strings[3331], new named_type(IFC4X3_RC4_IfcPersonAndOrganization_type), false),
            new attribute(strings[3332], new named_type(IFC4X3_RC4_IfcApplication_type), false),
            new attribute(strings[3333], new named_type(IFC4X3_RC4_IfcStateEnum_type), true),
            new attribute(strings[3334], new named_type(IFC4X3_RC4_IfcChangeActionEnum_type), true),
            new attribute(strings[3335], new named_type(IFC4X3_RC4_IfcTimeStamp_type), true),
            new attribute(strings[3336], new named_type(IFC4X3_RC4_IfcPersonAndOrganization_type), true),
            new attribute(strings[3337], new named_type(IFC4X3_RC4_IfcApplication_type), true),
            new attribute(strings[3338], new named_type(IFC4X3_RC4_IfcTimeStamp_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcParameterizedProfileDef_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement2D_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcPath_type->set_attributes({
            new attribute(strings[3153], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcOrientedEdge_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcPavement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPavementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPavementType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPavementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPcurve_type->set_attributes({
            new attribute(strings[3080], new named_type(IFC4X3_RC4_IfcSurface_type), false),
            new attribute(strings[3339], new named_type(IFC4X3_RC4_IfcCurve_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcPerformanceHistory_type->set_attributes({
            new attribute(strings[3340], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPerformanceHistoryTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPermeableCoveringProperties_type->set_attributes({
            new attribute(strings[3128], new named_type(IFC4X3_RC4_IfcPermeableCoveringOperationEnum_type), false),
            new attribute(strings[3146], new named_type(IFC4X3_RC4_IfcWindowPanelPositionEnum_type), false),
            new attribute(strings[3341], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3342], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3140], new named_type(IFC4X3_RC4_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPermit_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPermitTypeEnum_type), true),
            new attribute(strings[2870], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2871], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPerson_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3343], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3344], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3345], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true),
            new attribute(strings[3346], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true),
            new attribute(strings[3347], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true),
            new attribute(strings[3326], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcActorRole_type)), true),
            new attribute(strings[3327], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcAddress_type)), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPersonAndOrganization_type->set_attributes({
            new attribute(strings[3348], new named_type(IFC4X3_RC4_IfcPerson_type), false),
            new attribute(strings[3349], new named_type(IFC4X3_RC4_IfcOrganization_type), false),
            new attribute(strings[3326], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcActorRole_type)), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcPhysicalComplexQuantity_type->set_attributes({
            new attribute(strings[3350], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPhysicalQuantity_type)), false),
            new attribute(strings[3351], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[3352], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3055], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPhysicalQuantity_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcPhysicalSimpleQuantity_type->set_attributes({
            new attribute(strings[3097], new named_type(IFC4X3_RC4_IfcNamedUnit_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcPile_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPileTypeEnum_type), true),
            new attribute(strings[3147], new named_type(IFC4X3_RC4_IfcPileConstructionEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPileType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPileTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPipeFitting_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPipeFittingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPipeFittingType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPipeFittingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPipeSegment_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPipeSegmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPipeSegmentType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPipeSegmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPixelTexture_type->set_attributes({
            new attribute(strings[3000], new named_type(IFC4X3_RC4_IfcInteger_type), false),
            new attribute(strings[3353], new named_type(IFC4X3_RC4_IfcInteger_type), false),
            new attribute(strings[3354], new named_type(IFC4X3_RC4_IfcInteger_type), false),
            new attribute(strings[3355], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcBinary_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPlacement_type->set_attributes({
            new attribute(strings[3019], new named_type(IFC4X3_RC4_IfcPoint_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcPlanarBox_type->set_attributes({
            new attribute(strings[3083], new named_type(IFC4X3_RC4_IfcAxis2Placement_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcPlanarExtent_type->set_attributes({
            new attribute(strings[3356], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3357], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcPlane_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcPlant_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPlate_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPlateTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPlateStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPlateType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPlateTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPoint_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcPointByDistanceExpression_type->set_attributes({
            new attribute(strings[3358], new named_type(IFC4X3_RC4_IfcCurveMeasureSelect_type), false),
            new attribute(strings[3359], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3360], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3361], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3320], new named_type(IFC4X3_RC4_IfcCurve_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcPointOnCurve_type->set_attributes({
            new attribute(strings[3320], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3362], new named_type(IFC4X3_RC4_IfcParameterValue_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcPointOnSurface_type->set_attributes({
            new attribute(strings[3080], new named_type(IFC4X3_RC4_IfcSurface_type), false),
            new attribute(strings[3363], new named_type(IFC4X3_RC4_IfcParameterValue_type), false),
            new attribute(strings[3364], new named_type(IFC4X3_RC4_IfcParameterValue_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcPolyLoop_type->set_attributes({
            new attribute(strings[3365], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_RC4_IfcCartesianPoint_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcPolygonalBoundedHalfSpace_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), false),
            new attribute(strings[3366], new named_type(IFC4X3_RC4_IfcBoundedCurve_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPolygonalFaceSet_type->set_attributes({
            new attribute(strings[3367], new named_type(IFC4X3_RC4_IfcBoolean_type), true),
            new attribute(strings[3368], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcIndexedPolygonalFace_type)), false),
            new attribute(strings[3369], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcPositiveInteger_type)), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPolyline_type->set_attributes({
            new attribute(strings[3223], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcCartesianPoint_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcPolynomialCurve_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcPlacement_type), false),
            new attribute(strings[3370], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcReal_type)), true),
            new attribute(strings[3371], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcReal_type)), true),
            new attribute(strings[3372], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcReal_type)), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPort_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPositioningElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPostalAddress_type->set_attributes({
            new attribute(strings[3373], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3374], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true),
            new attribute(strings[3375], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3376], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3377], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3378], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3379], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPreDefinedColour_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcPreDefinedCurveFont_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcPreDefinedItem_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcPreDefinedProperties_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcPreDefinedPropertySet_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPreDefinedTextFont_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcPresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcPresentationLayerAssignment_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3380], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcLayeredItem_type)), false),
            new attribute(strings[2914], new named_type(IFC4X3_RC4_IfcIdentifier_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPresentationLayerWithStyle_type->set_attributes({
            new attribute(strings[3381], new named_type(IFC4X3_RC4_IfcLogical_type), false),
            new attribute(strings[3382], new named_type(IFC4X3_RC4_IfcLogical_type), false),
            new attribute(strings[3383], new named_type(IFC4X3_RC4_IfcLogical_type), false),
            new attribute(strings[3384], new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X3_RC4_IfcPresentationStyle_type)), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPresentationStyle_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_RC4_IfcProcedure_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcProcedureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProcedureType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcProcedureTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProcess_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2871], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProduct_type->set_attributes({
            new attribute(strings[3385], new named_type(IFC4X3_RC4_IfcObjectPlacement_type), true),
            new attribute(strings[3386], new named_type(IFC4X3_RC4_IfcProductRepresentation_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProductDefinitionShape_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcProductRepresentation_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3387], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcRepresentation_type)), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcProfileDef_type->set_attributes({
            new attribute(strings[3388], new named_type(IFC4X3_RC4_IfcProfileTypeEnum_type), false),
            new attribute(strings[3389], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcProfileProperties_type->set_attributes({
            new attribute(strings[3390], new named_type(IFC4X3_RC4_IfcProfileDef_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcProject_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProjectLibrary_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProjectOrder_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcProjectOrderTypeEnum_type), true),
            new attribute(strings[2870], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2871], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProjectedCRS_type->set_attributes({
            new attribute(strings[3391], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3392], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3393], new named_type(IFC4X3_RC4_IfcNamedUnit_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProjectionElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcProjectionElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProperty_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcIdentifier_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcPropertyAbstraction_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcPropertyBoundedValue_type->set_attributes({
            new attribute(strings[3394], new named_type(IFC4X3_RC4_IfcValue_type), true),
            new attribute(strings[3395], new named_type(IFC4X3_RC4_IfcValue_type), true),
            new attribute(strings[3097], new named_type(IFC4X3_RC4_IfcUnit_type), true),
            new attribute(strings[3396], new named_type(IFC4X3_RC4_IfcValue_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPropertyDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPropertyDependencyRelationship_type->set_attributes({
            new attribute(strings[3397], new named_type(IFC4X3_RC4_IfcProperty_type), false),
            new attribute(strings[3398], new named_type(IFC4X3_RC4_IfcProperty_type), false),
            new attribute(strings[3304], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcPropertyEnumeratedValue_type->set_attributes({
            new attribute(strings[3399], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcValue_type)), true),
            new attribute(strings[3400], new named_type(IFC4X3_RC4_IfcPropertyEnumeration_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPropertyEnumeration_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[3399], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcValue_type)), false),
            new attribute(strings[3097], new named_type(IFC4X3_RC4_IfcUnit_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcPropertyListValue_type->set_attributes({
            new attribute(strings[3233], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcValue_type)), true),
            new attribute(strings[3097], new named_type(IFC4X3_RC4_IfcUnit_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPropertyReferenceValue_type->set_attributes({
            new attribute(strings[3028], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3401], new named_type(IFC4X3_RC4_IfcObjectReferenceSelect_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPropertySet_type->set_attributes({
            new attribute(strings[3029], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcProperty_type)), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcPropertySetDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPropertySetTemplate_type->set_attributes({
            new attribute(strings[3030], new named_type(IFC4X3_RC4_IfcPropertySetTemplateTypeEnum_type), true),
            new attribute(strings[3402], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3031], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPropertyTemplate_type)), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPropertySingleValue_type->set_attributes({
            new attribute(strings[3403], new named_type(IFC4X3_RC4_IfcValue_type), true),
            new attribute(strings[3097], new named_type(IFC4X3_RC4_IfcUnit_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPropertyTableValue_type->set_attributes({
            new attribute(strings[3404], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcValue_type)), true),
            new attribute(strings[3405], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcValue_type)), true),
            new attribute(strings[3304], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3406], new named_type(IFC4X3_RC4_IfcUnit_type), true),
            new attribute(strings[3407], new named_type(IFC4X3_RC4_IfcUnit_type), true),
            new attribute(strings[3408], new named_type(IFC4X3_RC4_IfcCurveInterpolationEnum_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPropertyTemplate_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcPropertyTemplateDefinition_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcProtectiveDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcProtectiveDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProtectiveDeviceTrippingUnit_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProtectiveDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcProtectiveDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcProxy_type->set_attributes({
            new attribute(strings[3409], new named_type(IFC4X3_RC4_IfcObjectTypeEnum_type), false),
            new attribute(strings[3154], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPump_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPumpTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcPumpType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcPumpTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcQuantityArea_type->set_attributes({
            new attribute(strings[3410], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), false),
            new attribute(strings[3411], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcQuantityCount_type->set_attributes({
            new attribute(strings[3412], new named_type(IFC4X3_RC4_IfcCountMeasure_type), false),
            new attribute(strings[3411], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcQuantityLength_type->set_attributes({
            new attribute(strings[3413], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3411], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcQuantitySet_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcQuantityTime_type->set_attributes({
            new attribute(strings[3414], new named_type(IFC4X3_RC4_IfcTimeMeasure_type), false),
            new attribute(strings[3411], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcQuantityVolume_type->set_attributes({
            new attribute(strings[3415], new named_type(IFC4X3_RC4_IfcVolumeMeasure_type), false),
            new attribute(strings[3411], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcQuantityWeight_type->set_attributes({
            new attribute(strings[3416], new named_type(IFC4X3_RC4_IfcMassMeasure_type), false),
            new attribute(strings[3411], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcRail_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRailTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRailType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRailTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRailing_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRailingTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRailingType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRailingTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRailway_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRailwayTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRamp_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRampTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRampFlight_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRampFlightTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRampFlightType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRampFlightTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRampType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRampTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRationalBSplineCurveWithKnots_type->set_attributes({
            new attribute(strings[3417], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcReal_type)), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRationalBSplineSurfaceWithKnots_type->set_attributes({
            new attribute(strings[3417], new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcReal_type))), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRectangleHollowProfileDef_type->set_attributes({
            new attribute(strings[3001], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3418], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3419], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRectangleProfileDef_type->set_attributes({
            new attribute(strings[2990], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2991], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcRectangularPyramid_type->set_attributes({
            new attribute(strings[2967], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2968], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3353], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcRectangularTrimmedSurface_type->set_attributes({
            new attribute(strings[3080], new named_type(IFC4X3_RC4_IfcSurface_type), false),
            new attribute(strings[3420], new named_type(IFC4X3_RC4_IfcParameterValue_type), false),
            new attribute(strings[3421], new named_type(IFC4X3_RC4_IfcParameterValue_type), false),
            new attribute(strings[3422], new named_type(IFC4X3_RC4_IfcParameterValue_type), false),
            new attribute(strings[3423], new named_type(IFC4X3_RC4_IfcParameterValue_type), false),
            new attribute(strings[3424], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3425], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRecurrencePattern_type->set_attributes({
            new attribute(strings[3426], new named_type(IFC4X3_RC4_IfcRecurrenceTypeEnum_type), false),
            new attribute(strings[3427], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcDayInMonthNumber_type)), true),
            new attribute(strings[3428], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcDayInWeekNumber_type)), true),
            new attribute(strings[3429], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcMonthInYearNumber_type)), true),
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcInteger_type), true),
            new attribute(strings[3430], new named_type(IFC4X3_RC4_IfcInteger_type), true),
            new attribute(strings[3431], new named_type(IFC4X3_RC4_IfcInteger_type), true),
            new attribute(strings[3432], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcTimePeriod_type)), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReference_type->set_attributes({
            new attribute(strings[3433], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3434], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3435], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3436], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcInteger_type)), true),
            new attribute(strings[3437], new named_type(IFC4X3_RC4_IfcReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcReferent_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcReferentTypeEnum_type), true),
            new attribute(strings[3438], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRegularTimeSeries_type->set_attributes({
            new attribute(strings[3439], new named_type(IFC4X3_RC4_IfcTimeMeasure_type), false),
            new attribute(strings[3231], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcTimeSeriesValue_type)), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcedSoil_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcReinforcedSoilTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcementBarProperties_type->set_attributes({
            new attribute(strings[3440], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), false),
            new attribute(strings[3441], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[3442], new named_type(IFC4X3_RC4_IfcReinforcingBarSurfaceEnum_type), true),
            new attribute(strings[3443], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3444], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3445], new named_type(IFC4X3_RC4_IfcCountMeasure_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcementDefinitionProperties_type->set_attributes({
            new attribute(strings[3446], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3447], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcSectionReinforcementProperties_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcingBar_type->set_attributes({
            new attribute(strings[3307], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3448], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), true),
            new attribute(strings[3449], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcReinforcingBarTypeEnum_type), true),
            new attribute(strings[3442], new named_type(IFC4X3_RC4_IfcReinforcingBarSurfaceEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcingBarType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcReinforcingBarTypeEnum_type), false),
            new attribute(strings[3307], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3448], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), true),
            new attribute(strings[3449], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3442], new named_type(IFC4X3_RC4_IfcReinforcingBarSurfaceEnum_type), true),
            new attribute(strings[3450], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3451], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcBendingParameterSelect_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcingElement_type->set_attributes({
            new attribute(strings[3441], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcingElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcingMesh_type->set_attributes({
            new attribute(strings[3452], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3453], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3454], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3455], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3456], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), true),
            new attribute(strings[3457], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), true),
            new attribute(strings[3458], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3459], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcReinforcingMeshTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcReinforcingMeshType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcReinforcingMeshTypeEnum_type), false),
            new attribute(strings[3452], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3453], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3454], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3455], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3456], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), true),
            new attribute(strings[3457], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), true),
            new attribute(strings[3458], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3459], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3450], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3451], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcBendingParameterSelect_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAdheresToElement_type->set_attributes({
            new attribute(strings[3460], new named_type(IFC4X3_RC4_IfcElement_type), false),
            new attribute(strings[3461], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcSurfaceFeature_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAggregates_type->set_attributes({
            new attribute(strings[3462], new named_type(IFC4X3_RC4_IfcObjectDefinition_type), false),
            new attribute(strings[3463], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcObjectDefinition_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssigns_type->set_attributes({
            new attribute(strings[3463], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcObjectDefinition_type)), false),
            new attribute(strings[3464], new named_type(IFC4X3_RC4_IfcObjectTypeEnum_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssignsToActor_type->set_attributes({
            new attribute(strings[3465], new named_type(IFC4X3_RC4_IfcActor_type), false),
            new attribute(strings[3466], new named_type(IFC4X3_RC4_IfcActorRole_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssignsToControl_type->set_attributes({
            new attribute(strings[3467], new named_type(IFC4X3_RC4_IfcControl_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssignsToGroup_type->set_attributes({
            new attribute(strings[3468], new named_type(IFC4X3_RC4_IfcGroup_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssignsToGroupByFactor_type->set_attributes({
            new attribute(strings[3469], new named_type(IFC4X3_RC4_IfcRatioMeasure_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssignsToProcess_type->set_attributes({
            new attribute(strings[3470], new named_type(IFC4X3_RC4_IfcProcessSelect_type), false),
            new attribute(strings[3471], new named_type(IFC4X3_RC4_IfcMeasureWithUnit_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssignsToProduct_type->set_attributes({
            new attribute(strings[3472], new named_type(IFC4X3_RC4_IfcProductSelect_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssignsToResource_type->set_attributes({
            new attribute(strings[3473], new named_type(IFC4X3_RC4_IfcResourceSelect_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssociates_type->set_attributes({
            new attribute(strings[3463], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcDefinitionSelect_type)), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssociatesApproval_type->set_attributes({
            new attribute(strings[2920], new named_type(IFC4X3_RC4_IfcApproval_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssociatesClassification_type->set_attributes({
            new attribute(strings[3474], new named_type(IFC4X3_RC4_IfcClassificationSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssociatesConstraint_type->set_attributes({
            new attribute(strings[3475], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3476], new named_type(IFC4X3_RC4_IfcConstraint_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssociatesDocument_type->set_attributes({
            new attribute(strings[3122], new named_type(IFC4X3_RC4_IfcDocumentSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssociatesLibrary_type->set_attributes({
            new attribute(strings[3477], new named_type(IFC4X3_RC4_IfcLibrarySelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssociatesMaterial_type->set_attributes({
            new attribute(strings[3302], new named_type(IFC4X3_RC4_IfcMaterialSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelAssociatesProfileDef_type->set_attributes({
            new attribute(strings[3478], new named_type(IFC4X3_RC4_IfcProfileDef_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnects_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnectsElements_type->set_attributes({
            new attribute(strings[3479], new named_type(IFC4X3_RC4_IfcConnectionGeometry_type), true),
            new attribute(strings[3460], new named_type(IFC4X3_RC4_IfcElement_type), false),
            new attribute(strings[3480], new named_type(IFC4X3_RC4_IfcElement_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnectsPathElements_type->set_attributes({
            new attribute(strings[3481], new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X3_RC4_IfcInteger_type)), false),
            new attribute(strings[3482], new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X3_RC4_IfcInteger_type)), false),
            new attribute(strings[3483], new named_type(IFC4X3_RC4_IfcConnectionTypeEnum_type), false),
            new attribute(strings[3484], new named_type(IFC4X3_RC4_IfcConnectionTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnectsPortToElement_type->set_attributes({
            new attribute(strings[3485], new named_type(IFC4X3_RC4_IfcPort_type), false),
            new attribute(strings[3480], new named_type(IFC4X3_RC4_IfcDistributionElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnectsPorts_type->set_attributes({
            new attribute(strings[3485], new named_type(IFC4X3_RC4_IfcPort_type), false),
            new attribute(strings[3486], new named_type(IFC4X3_RC4_IfcPort_type), false),
            new attribute(strings[3487], new named_type(IFC4X3_RC4_IfcElement_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnectsStructuralActivity_type->set_attributes({
            new attribute(strings[3460], new named_type(IFC4X3_RC4_IfcStructuralActivityAssignmentSelect_type), false),
            new attribute(strings[3488], new named_type(IFC4X3_RC4_IfcStructuralActivity_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnectsStructuralMember_type->set_attributes({
            new attribute(strings[3489], new named_type(IFC4X3_RC4_IfcStructuralMember_type), false),
            new attribute(strings[3490], new named_type(IFC4X3_RC4_IfcStructuralConnection_type), false),
            new attribute(strings[3491], new named_type(IFC4X3_RC4_IfcBoundaryCondition_type), true),
            new attribute(strings[3492], new named_type(IFC4X3_RC4_IfcStructuralConnectionCondition_type), true),
            new attribute(strings[3493], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3494], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnectsWithEccentricity_type->set_attributes({
            new attribute(strings[3495], new named_type(IFC4X3_RC4_IfcConnectionGeometry_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelConnectsWithRealizingElements_type->set_attributes({
            new attribute(strings[3496], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcElement_type)), false),
            new attribute(strings[3497], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelContainedInSpatialStructure_type->set_attributes({
            new attribute(strings[3498], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcProduct_type)), false),
            new attribute(strings[3499], new named_type(IFC4X3_RC4_IfcSpatialElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelCoversBldgElements_type->set_attributes({
            new attribute(strings[3500], new named_type(IFC4X3_RC4_IfcElement_type), false),
            new attribute(strings[3501], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcCovering_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelCoversSpaces_type->set_attributes({
            new attribute(strings[3502], new named_type(IFC4X3_RC4_IfcSpace_type), false),
            new attribute(strings[3501], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcCovering_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelDeclares_type->set_attributes({
            new attribute(strings[3503], new named_type(IFC4X3_RC4_IfcContext_type), false),
            new attribute(strings[3504], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcDefinitionSelect_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelDecomposes_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcRelDefines_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcRelDefinesByObject_type->set_attributes({
            new attribute(strings[3463], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcObject_type)), false),
            new attribute(strings[3462], new named_type(IFC4X3_RC4_IfcObject_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelDefinesByProperties_type->set_attributes({
            new attribute(strings[3463], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcObjectDefinition_type)), false),
            new attribute(strings[3505], new named_type(IFC4X3_RC4_IfcPropertySetDefinitionSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelDefinesByTemplate_type->set_attributes({
            new attribute(strings[3506], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPropertySetDefinition_type)), false),
            new attribute(strings[3507], new named_type(IFC4X3_RC4_IfcPropertySetTemplate_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelDefinesByType_type->set_attributes({
            new attribute(strings[3463], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcObject_type)), false),
            new attribute(strings[3508], new named_type(IFC4X3_RC4_IfcTypeObject_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelFillsElement_type->set_attributes({
            new attribute(strings[3509], new named_type(IFC4X3_RC4_IfcOpeningElement_type), false),
            new attribute(strings[3510], new named_type(IFC4X3_RC4_IfcElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelFlowControlElements_type->set_attributes({
            new attribute(strings[3511], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcDistributionControlElement_type)), false),
            new attribute(strings[3512], new named_type(IFC4X3_RC4_IfcDistributionFlowElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelInterferesElements_type->set_attributes({
            new attribute(strings[3460], new named_type(IFC4X3_RC4_IfcInterferenceSelect_type), false),
            new attribute(strings[3480], new named_type(IFC4X3_RC4_IfcInterferenceSelect_type), false),
            new attribute(strings[3513], new named_type(IFC4X3_RC4_IfcConnectionGeometry_type), true),
            new attribute(strings[3514], new named_type(IFC4X3_RC4_IfcSpatialZone_type), true),
            new attribute(strings[3515], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3516], new named_type(IFC4X3_RC4_IfcLogical_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelNests_type->set_attributes({
            new attribute(strings[3462], new named_type(IFC4X3_RC4_IfcObjectDefinition_type), false),
            new attribute(strings[3463], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcObjectDefinition_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelPositions_type->set_attributes({
            new attribute(strings[3517], new named_type(IFC4X3_RC4_IfcPositioningElement_type), false),
            new attribute(strings[3518], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcProduct_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelProjectsElement_type->set_attributes({
            new attribute(strings[3460], new named_type(IFC4X3_RC4_IfcElement_type), false),
            new attribute(strings[3519], new named_type(IFC4X3_RC4_IfcFeatureElementAddition_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type->set_attributes({
            new attribute(strings[3498], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcSpatialReferenceSelect_type)), false),
            new attribute(strings[3499], new named_type(IFC4X3_RC4_IfcSpatialElement_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelSequence_type->set_attributes({
            new attribute(strings[3470], new named_type(IFC4X3_RC4_IfcProcess_type), false),
            new attribute(strings[3520], new named_type(IFC4X3_RC4_IfcProcess_type), false),
            new attribute(strings[3521], new named_type(IFC4X3_RC4_IfcLagTime_type), true),
            new attribute(strings[3522], new named_type(IFC4X3_RC4_IfcSequenceEnum_type), true),
            new attribute(strings[3523], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelServicesBuildings_type->set_attributes({
            new attribute(strings[3524], new named_type(IFC4X3_RC4_IfcSystem_type), false),
            new attribute(strings[3525], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcSpatialElement_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelSpaceBoundary_type->set_attributes({
            new attribute(strings[3502], new named_type(IFC4X3_RC4_IfcSpaceBoundarySelect_type), false),
            new attribute(strings[3510], new named_type(IFC4X3_RC4_IfcElement_type), false),
            new attribute(strings[3479], new named_type(IFC4X3_RC4_IfcConnectionGeometry_type), true),
            new attribute(strings[3526], new named_type(IFC4X3_RC4_IfcPhysicalOrVirtualEnum_type), false),
            new attribute(strings[3527], new named_type(IFC4X3_RC4_IfcInternalOrExternalEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type->set_attributes({
            new attribute(strings[3528], new named_type(IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type->set_attributes({
            new attribute(strings[3529], new named_type(IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelVoidsElement_type->set_attributes({
            new attribute(strings[3500], new named_type(IFC4X3_RC4_IfcElement_type), false),
            new attribute(strings[3530], new named_type(IFC4X3_RC4_IfcFeatureElementSubtraction_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRelationship_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcReparametrisedCompositeCurveSegment_type->set_attributes({
            new attribute(strings[3531], new named_type(IFC4X3_RC4_IfcParameterValue_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcRepresentation_type->set_attributes({
            new attribute(strings[3532], new named_type(IFC4X3_RC4_IfcRepresentationContext_type), false),
            new attribute(strings[3533], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3534], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3535], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcRepresentationItem_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcRepresentationContext_type->set_attributes({
            new attribute(strings[3536], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3537], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcRepresentationMap_type->set_attributes({
            new attribute(strings[3538], new named_type(IFC4X3_RC4_IfcAxis2Placement_type), false),
            new attribute(strings[3539], new named_type(IFC4X3_RC4_IfcRepresentation_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcResource_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2871], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcResourceApprovalRelationship_type->set_attributes({
            new attribute(strings[3170], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcResourceObjectSelect_type)), false),
            new attribute(strings[2920], new named_type(IFC4X3_RC4_IfcApproval_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcResourceConstraintRelationship_type->set_attributes({
            new attribute(strings[3476], new named_type(IFC4X3_RC4_IfcConstraint_type), false),
            new attribute(strings[3170], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcResourceObjectSelect_type)), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcResourceLevelRelationship_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcResourceTime_type->set_attributes({
            new attribute(strings[3540], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3541], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3542], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3543], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3544], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3545], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3546], new named_type(IFC4X3_RC4_IfcBoolean_type), true),
            new attribute(strings[3547], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3548], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3549], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3550], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3551], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3552], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3553], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), true),
            new attribute(strings[3554], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRevolvedAreaSolid_type->set_attributes({
            new attribute(strings[2946], new named_type(IFC4X3_RC4_IfcAxis1Placement_type), false),
            new attribute(strings[3555], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcRevolvedAreaSolidTapered_type->set_attributes({
            new attribute(strings[3172], new named_type(IFC4X3_RC4_IfcProfileDef_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcRightCircularCone_type->set_attributes({
            new attribute(strings[3353], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3556], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcRightCircularCylinder_type->set_attributes({
            new attribute(strings[3353], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3015], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcRoad_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRoadTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRoof_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRoofTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRoofType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcRoofTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcRoot_type->set_attributes({
            new attribute(strings[3557], new named_type(IFC4X3_RC4_IfcGloballyUniqueId_type), false),
            new attribute(strings[3558], new named_type(IFC4X3_RC4_IfcOwnerHistory_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcRoundedRectangleProfileDef_type->set_attributes({
            new attribute(strings[3559], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSIUnit_type->set_attributes({
            new attribute(strings[3560], new named_type(IFC4X3_RC4_IfcSIPrefix_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcSIUnitName_type), false)
    },{
            true, false, false, false
    });
    IFC4X3_RC4_IfcSanitaryTerminal_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSanitaryTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSanitaryTerminalType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSanitaryTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSchedulingTime_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3561], new named_type(IFC4X3_RC4_IfcDataOriginEnum_type), true),
            new attribute(strings[3562], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcSeamCurve_type->set_attributes({
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcSecondOrderPolynomialSpiral_type->set_attributes({
            new attribute(strings[3563], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3564], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3069], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSectionProperties_type->set_attributes({
            new attribute(strings[3565], new named_type(IFC4X3_RC4_IfcSectionTypeEnum_type), false),
            new attribute(strings[3566], new named_type(IFC4X3_RC4_IfcProfileDef_type), false),
            new attribute(strings[3567], new named_type(IFC4X3_RC4_IfcProfileDef_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcSectionReinforcementProperties_type->set_attributes({
            new attribute(strings[3568], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3569], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3570], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3571], new named_type(IFC4X3_RC4_IfcReinforcingBarRoleEnum_type), false),
            new attribute(strings[3572], new named_type(IFC4X3_RC4_IfcSectionProperties_type), false),
            new attribute(strings[3573], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcReinforcementBarProperties_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSectionedSolid_type->set_attributes({
            new attribute(strings[3107], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3574], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcProfileDef_type)), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcSectionedSolidHorizontal_type->set_attributes({
            new attribute(strings[3575], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcAxis2PlacementLinear_type)), false),
            new attribute(strings[3576], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSectionedSpine_type->set_attributes({
            new attribute(strings[3577], new named_type(IFC4X3_RC4_IfcCompositeCurve_type), false),
            new attribute(strings[3574], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcProfileDef_type)), false),
            new attribute(strings[3575], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type)), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcSectionedSurface_type->set_attributes({
            new attribute(strings[3107], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3575], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcPointByDistanceExpression_type)), false),
            new attribute(strings[3574], new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X3_RC4_IfcProfileDef_type)), false),
            new attribute(strings[3576], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSegment_type->set_attributes({
            new attribute(strings[3578], new named_type(IFC4X3_RC4_IfcTransitionCode_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcSegmentedReferenceCurve_type->set_attributes({
            new attribute(strings[3203], new named_type(IFC4X3_RC4_IfcBoundedCurve_type), false),
            new attribute(strings[3204], new named_type(IFC4X3_RC4_IfcPlacement_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSensor_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSensorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSensorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSensorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSeventhOrderPolynomialSpiral_type->set_attributes({
            new attribute(strings[3579], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3580], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3581], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3582], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3583], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3563], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3564], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3069], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcShadingDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcShadingDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcShadingDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcShadingDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcShapeAspect_type->set_attributes({
            new attribute(strings[3584], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcShapeModel_type)), false),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3585], new named_type(IFC4X3_RC4_IfcLogical_type), false),
            new attribute(strings[3586], new named_type(IFC4X3_RC4_IfcProductRepresentationSelect_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcShapeModel_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcShapeRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcShellBasedSurfaceModel_type->set_attributes({
            new attribute(strings[3587], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcShell_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcSign_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSignTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSignType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSignTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSignal_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSignalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSignalType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSignalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSimpleProperty_type->set_attributes({
    },{
            false, false
    });
    IFC4X3_RC4_IfcSimplePropertyTemplate_type->set_attributes({
            new attribute(strings[3030], new named_type(IFC4X3_RC4_IfcSimplePropertyTemplateTypeEnum_type), true),
            new attribute(strings[3588], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3589], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3590], new named_type(IFC4X3_RC4_IfcPropertyEnumeration_type), true),
            new attribute(strings[3591], new named_type(IFC4X3_RC4_IfcUnit_type), true),
            new attribute(strings[3592], new named_type(IFC4X3_RC4_IfcUnit_type), true),
            new attribute(strings[3304], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3593], new named_type(IFC4X3_RC4_IfcStateEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSine_type->set_attributes({
            new attribute(strings[3594], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3564], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3069], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSite_type->set_attributes({
            new attribute(strings[3595], new named_type(IFC4X3_RC4_IfcCompoundPlaneAngleMeasure_type), true),
            new attribute(strings[3596], new named_type(IFC4X3_RC4_IfcCompoundPlaneAngleMeasure_type), true),
            new attribute(strings[3597], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3598], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3599], new named_type(IFC4X3_RC4_IfcPostalAddress_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSlab_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSlabTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSlabElementedCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSlabStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSlabType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSlabTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSlippageConnectionCondition_type->set_attributes({
            new attribute(strings[3600], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3601], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3602], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSolarDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSolarDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSolarDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSolarDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSolidModel_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcSolidStratum_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpace_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSpaceTypeEnum_type), true),
            new attribute(strings[3603], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpaceHeater_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSpaceHeaterTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpaceHeaterType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSpaceHeaterTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpaceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSpaceTypeEnum_type), false),
            new attribute(strings[2998], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpatialElement_type->set_attributes({
            new attribute(strings[2998], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpatialElementType_type->set_attributes({
            new attribute(strings[3158], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpatialStructureElement_type->set_attributes({
            new attribute(strings[3604], new named_type(IFC4X3_RC4_IfcElementCompositionEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpatialStructureElementType_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpatialZone_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSpatialZoneTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSpatialZoneType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSpatialZoneTypeEnum_type), false),
            new attribute(strings[2998], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSphere_type->set_attributes({
            new attribute(strings[3015], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcSphericalSurface_type->set_attributes({
            new attribute(strings[3015], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcSpiral_type->set_attributes({
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement_type), true)
    },{
            false
    });
    IFC4X3_RC4_IfcStackTerminal_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStackTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStackTerminalType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStackTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStair_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStairTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStairFlight_type->set_attributes({
            new attribute(strings[3605], new named_type(IFC4X3_RC4_IfcInteger_type), true),
            new attribute(strings[3606], new named_type(IFC4X3_RC4_IfcInteger_type), true),
            new attribute(strings[3607], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3608], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStairFlightTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStairFlightType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStairFlightTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStairType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStairTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralAction_type->set_attributes({
            new attribute(strings[3609], new named_type(IFC4X3_RC4_IfcBoolean_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralActivity_type->set_attributes({
            new attribute(strings[3610], new named_type(IFC4X3_RC4_IfcStructuralLoad_type), false),
            new attribute(strings[3611], new named_type(IFC4X3_RC4_IfcGlobalOrLocalEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralAnalysisModel_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcAnalysisModelTypeEnum_type), false),
            new attribute(strings[3612], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), true),
            new attribute(strings[3613], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcStructuralLoadGroup_type)), true),
            new attribute(strings[3614], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcStructuralResultGroup_type)), true),
            new attribute(strings[3615], new named_type(IFC4X3_RC4_IfcObjectPlacement_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralConnection_type->set_attributes({
            new attribute(strings[3491], new named_type(IFC4X3_RC4_IfcBoundaryCondition_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralConnectionCondition_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_RC4_IfcStructuralCurveAction_type->set_attributes({
            new attribute(strings[3616], new named_type(IFC4X3_RC4_IfcProjectedOrTrueLengthEnum_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStructuralCurveActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralCurveConnection_type->set_attributes({
            new attribute(strings[2946], new named_type(IFC4X3_RC4_IfcDirection_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralCurveMember_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStructuralCurveMemberTypeEnum_type), false),
            new attribute(strings[2946], new named_type(IFC4X3_RC4_IfcDirection_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralCurveMemberVarying_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralCurveReaction_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStructuralCurveActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralItem_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLinearAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoad_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false
    });
    IFC4X3_RC4_IfcStructuralLoadCase_type->set_attributes({
            new attribute(strings[3617], new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_RC4_IfcRatioMeasure_type)), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadConfiguration_type->set_attributes({
            new attribute(strings[3231], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcStructuralLoadOrResult_type)), false),
            new attribute(strings[3618], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X3_RC4_IfcLengthMeasure_type))), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadGroup_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcLoadGroupTypeEnum_type), false),
            new attribute(strings[3619], new named_type(IFC4X3_RC4_IfcActionTypeEnum_type), false),
            new attribute(strings[3620], new named_type(IFC4X3_RC4_IfcActionSourceTypeEnum_type), false),
            new attribute(strings[3621], new named_type(IFC4X3_RC4_IfcRatioMeasure_type), true),
            new attribute(strings[2876], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadLinearForce_type->set_attributes({
            new attribute(strings[3622], new named_type(IFC4X3_RC4_IfcLinearForceMeasure_type), true),
            new attribute(strings[3623], new named_type(IFC4X3_RC4_IfcLinearForceMeasure_type), true),
            new attribute(strings[3624], new named_type(IFC4X3_RC4_IfcLinearForceMeasure_type), true),
            new attribute(strings[3625], new named_type(IFC4X3_RC4_IfcLinearMomentMeasure_type), true),
            new attribute(strings[3626], new named_type(IFC4X3_RC4_IfcLinearMomentMeasure_type), true),
            new attribute(strings[3627], new named_type(IFC4X3_RC4_IfcLinearMomentMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadOrResult_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcStructuralLoadPlanarForce_type->set_attributes({
            new attribute(strings[3628], new named_type(IFC4X3_RC4_IfcPlanarForceMeasure_type), true),
            new attribute(strings[3629], new named_type(IFC4X3_RC4_IfcPlanarForceMeasure_type), true),
            new attribute(strings[3630], new named_type(IFC4X3_RC4_IfcPlanarForceMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadSingleDisplacement_type->set_attributes({
            new attribute(strings[3631], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3632], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3633], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3634], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3635], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3636], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadSingleDisplacementDistortion_type->set_attributes({
            new attribute(strings[3637], new named_type(IFC4X3_RC4_IfcCurvatureMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadSingleForce_type->set_attributes({
            new attribute(strings[3638], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3639], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3640], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3641], new named_type(IFC4X3_RC4_IfcTorqueMeasure_type), true),
            new attribute(strings[3642], new named_type(IFC4X3_RC4_IfcTorqueMeasure_type), true),
            new attribute(strings[3643], new named_type(IFC4X3_RC4_IfcTorqueMeasure_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadSingleForceWarping_type->set_attributes({
            new attribute(strings[3644], new named_type(IFC4X3_RC4_IfcWarpingMomentMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralLoadStatic_type->set_attributes({
    },{
            false
    });
    IFC4X3_RC4_IfcStructuralLoadTemperature_type->set_attributes({
            new attribute(strings[3645], new named_type(IFC4X3_RC4_IfcThermodynamicTemperatureMeasure_type), true),
            new attribute(strings[3646], new named_type(IFC4X3_RC4_IfcThermodynamicTemperatureMeasure_type), true),
            new attribute(strings[3647], new named_type(IFC4X3_RC4_IfcThermodynamicTemperatureMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralMember_type->set_attributes({
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralPlanarAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralPointAction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralPointConnection_type->set_attributes({
            new attribute(strings[3494], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralPointReaction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralReaction_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralResultGroup_type->set_attributes({
            new attribute(strings[3648], new named_type(IFC4X3_RC4_IfcAnalysisTheoryTypeEnum_type), false),
            new attribute(strings[3649], new named_type(IFC4X3_RC4_IfcStructuralLoadGroup_type), true),
            new attribute(strings[3650], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralSurfaceAction_type->set_attributes({
            new attribute(strings[3616], new named_type(IFC4X3_RC4_IfcProjectedOrTrueLengthEnum_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStructuralSurfaceActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralSurfaceConnection_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralSurfaceMember_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStructuralSurfaceMemberTypeEnum_type), false),
            new attribute(strings[3014], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralSurfaceMemberVarying_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStructuralSurfaceReaction_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcStructuralSurfaceActivityTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcStyleModel_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcStyledItem_type->set_attributes({
            new attribute(strings[3651], new named_type(IFC4X3_RC4_IfcRepresentationItem_type), true),
            new attribute(strings[3652], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPresentationStyle_type)), false),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcStyledRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSubContractResource_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSubContractResourceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSubContractResourceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSubContractResourceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSubedge_type->set_attributes({
            new attribute(strings[3653], new named_type(IFC4X3_RC4_IfcEdge_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcSurface_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcSurfaceCurve_type->set_attributes({
            new attribute(strings[3654], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3655], new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X3_RC4_IfcPcurve_type)), false),
            new attribute(strings[3656], new named_type(IFC4X3_RC4_IfcPreferredSurfaceCurveRepresentation_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcSurfaceCurveSweptAreaSolid_type->set_attributes({
            new attribute(strings[3657], new named_type(IFC4X3_RC4_IfcSurface_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSurfaceFeature_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSurfaceFeatureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSurfaceOfLinearExtrusion_type->set_attributes({
            new attribute(strings[3171], new named_type(IFC4X3_RC4_IfcDirection_type), false),
            new attribute(strings[2999], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSurfaceOfRevolution_type->set_attributes({
            new attribute(strings[3658], new named_type(IFC4X3_RC4_IfcAxis1Placement_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcSurfaceReinforcementArea_type->set_attributes({
            new attribute(strings[3659], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X3_RC4_IfcLengthMeasure_type)), true),
            new attribute(strings[3660], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X3_RC4_IfcLengthMeasure_type)), true),
            new attribute(strings[3661], new named_type(IFC4X3_RC4_IfcRatioMeasure_type), true)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSurfaceStyle_type->set_attributes({
            new attribute(strings[3662], new named_type(IFC4X3_RC4_IfcSurfaceSide_type), false),
            new attribute(strings[3652], new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC4X3_RC4_IfcSurfaceStyleElementSelect_type)), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcSurfaceStyleLighting_type->set_attributes({
            new attribute(strings[3663], new named_type(IFC4X3_RC4_IfcColourRgb_type), false),
            new attribute(strings[3664], new named_type(IFC4X3_RC4_IfcColourRgb_type), false),
            new attribute(strings[3665], new named_type(IFC4X3_RC4_IfcColourRgb_type), false),
            new attribute(strings[3666], new named_type(IFC4X3_RC4_IfcColourRgb_type), false)
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcSurfaceStyleRefraction_type->set_attributes({
            new attribute(strings[3667], new named_type(IFC4X3_RC4_IfcReal_type), true),
            new attribute(strings[3668], new named_type(IFC4X3_RC4_IfcReal_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcSurfaceStyleRendering_type->set_attributes({
            new attribute(strings[3669], new named_type(IFC4X3_RC4_IfcColourOrFactor_type), true),
            new attribute(strings[3665], new named_type(IFC4X3_RC4_IfcColourOrFactor_type), true),
            new attribute(strings[3663], new named_type(IFC4X3_RC4_IfcColourOrFactor_type), true),
            new attribute(strings[3670], new named_type(IFC4X3_RC4_IfcColourOrFactor_type), true),
            new attribute(strings[3671], new named_type(IFC4X3_RC4_IfcColourOrFactor_type), true),
            new attribute(strings[3672], new named_type(IFC4X3_RC4_IfcSpecularHighlightSelect_type), true),
            new attribute(strings[3673], new named_type(IFC4X3_RC4_IfcReflectanceMethodEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSurfaceStyleShading_type->set_attributes({
            new attribute(strings[3674], new named_type(IFC4X3_RC4_IfcColourRgb_type), false),
            new attribute(strings[3675], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcSurfaceStyleWithTextures_type->set_attributes({
            new attribute(strings[3676], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcSurfaceTexture_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcSurfaceTexture_type->set_attributes({
            new attribute(strings[3677], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3678], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3679], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3680], new named_type(IFC4X3_RC4_IfcCartesianTransformationOperator2D_type), true),
            new attribute(strings[3681], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcIdentifier_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcSweptAreaSolid_type->set_attributes({
            new attribute(strings[3682], new named_type(IFC4X3_RC4_IfcProfileDef_type), false),
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcSweptDiskSolid_type->set_attributes({
            new attribute(strings[3107], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3015], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3683], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3108], new named_type(IFC4X3_RC4_IfcParameterValue_type), true),
            new attribute(strings[3109], new named_type(IFC4X3_RC4_IfcParameterValue_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcSweptDiskSolidPolygonal_type->set_attributes({
            new attribute(strings[3215], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSweptSurface_type->set_attributes({
            new attribute(strings[3684], new named_type(IFC4X3_RC4_IfcProfileDef_type), false),
            new attribute(strings[3037], new named_type(IFC4X3_RC4_IfcAxis2Placement3D_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcSwitchingDevice_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSwitchingDeviceTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSwitchingDeviceType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSwitchingDeviceTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSystem_type->set_attributes({
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcSystemFurnitureElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSystemFurnitureElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcSystemFurnitureElementType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcSystemFurnitureElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTShapeProfileDef_type->set_attributes({
            new attribute(strings[2999], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3685], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2936], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3214], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3215], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3216], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3686], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3687], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true),
            new attribute(strings[3217], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTable_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3688], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcTableRow_type)), true),
            new attribute(strings[3689], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcTableColumn_type)), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcTableColumn_type->set_attributes({
            new attribute(strings[2914], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3097], new named_type(IFC4X3_RC4_IfcUnit_type), true),
            new attribute(strings[3312], new named_type(IFC4X3_RC4_IfcReference_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcTableRow_type->set_attributes({
            new attribute(strings[3690], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcValue_type)), true),
            new attribute(strings[3691], new named_type(IFC4X3_RC4_IfcBoolean_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcTank_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTankTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTankType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTankTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTask_type->set_attributes({
            new attribute(strings[2870], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3692], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3693], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3284], new named_type(IFC4X3_RC4_IfcInteger_type), true),
            new attribute(strings[3694], new named_type(IFC4X3_RC4_IfcTaskTime_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTaskTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTaskTime_type->set_attributes({
            new attribute(strings[3238], new named_type(IFC4X3_RC4_IfcTaskDurationEnum_type), true),
            new attribute(strings[3695], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3542], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3543], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3696], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3697], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3698], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3699], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3700], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3701], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3702], new named_type(IFC4X3_RC4_IfcBoolean_type), true),
            new attribute(strings[3547], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3703], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3550], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3551], new named_type(IFC4X3_RC4_IfcDateTime_type), true),
            new attribute(strings[3704], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3554], new named_type(IFC4X3_RC4_IfcPositiveRatioMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTaskTimeRecurring_type->set_attributes({
            new attribute(strings[3705], new named_type(IFC4X3_RC4_IfcRecurrencePattern_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTaskType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTaskTypeEnum_type), false),
            new attribute(strings[3692], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTelecomAddress_type->set_attributes({
            new attribute(strings[3706], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true),
            new attribute(strings[3707], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true),
            new attribute(strings[3708], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3709], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcLabel_type)), true),
            new attribute(strings[3710], new named_type(IFC4X3_RC4_IfcURIReference_type), true),
            new attribute(strings[3711], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcURIReference_type)), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTendon_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTendonTypeEnum_type), true),
            new attribute(strings[3307], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3448], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), true),
            new attribute(strings[3712], new named_type(IFC4X3_RC4_IfcForceMeasure_type), true),
            new attribute(strings[3713], new named_type(IFC4X3_RC4_IfcPressureMeasure_type), true),
            new attribute(strings[3714], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3715], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3716], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTendonAnchor_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTendonAnchorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTendonAnchorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTendonAnchorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTendonConduit_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTendonConduitTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTendonConduitType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTendonConduitTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTendonType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTendonTypeEnum_type), false),
            new attribute(strings[3307], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3448], new named_type(IFC4X3_RC4_IfcAreaMeasure_type), true),
            new attribute(strings[3717], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTessellatedFaceSet_type->set_attributes({
            new attribute(strings[3004], new named_type(IFC4X3_RC4_IfcCartesianPointList3D_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcTessellatedItem_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcTextLiteral_type->set_attributes({
            new attribute(strings[3718], new named_type(IFC4X3_RC4_IfcPresentableText_type), false),
            new attribute(strings[3083], new named_type(IFC4X3_RC4_IfcAxis2Placement_type), false),
            new attribute(strings[3719], new named_type(IFC4X3_RC4_IfcTextPath_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcTextLiteralWithExtent_type->set_attributes({
            new attribute(strings[3720], new named_type(IFC4X3_RC4_IfcPlanarExtent_type), false),
            new attribute(strings[3721], new named_type(IFC4X3_RC4_IfcBoxAlignment_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcTextStyle_type->set_attributes({
            new attribute(strings[3722], new named_type(IFC4X3_RC4_IfcTextStyleForDefinedFont_type), true),
            new attribute(strings[3723], new named_type(IFC4X3_RC4_IfcTextStyleTextModel_type), true),
            new attribute(strings[3724], new named_type(IFC4X3_RC4_IfcTextFontSelect_type), false),
            new attribute(strings[3088], new named_type(IFC4X3_RC4_IfcBoolean_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcTextStyleFontModel_type->set_attributes({
            new attribute(strings[3725], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcTextFontName_type)), false),
            new attribute(strings[3726], new named_type(IFC4X3_RC4_IfcFontStyle_type), true),
            new attribute(strings[3727], new named_type(IFC4X3_RC4_IfcFontVariant_type), true),
            new attribute(strings[3728], new named_type(IFC4X3_RC4_IfcFontWeight_type), true),
            new attribute(strings[3729], new named_type(IFC4X3_RC4_IfcSizeSelect_type), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTextStyleForDefinedFont_type->set_attributes({
            new attribute(strings[3730], new named_type(IFC4X3_RC4_IfcColour_type), false),
            new attribute(strings[3731], new named_type(IFC4X3_RC4_IfcColour_type), true)
    },{
            false, false
    });
    IFC4X3_RC4_IfcTextStyleTextModel_type->set_attributes({
            new attribute(strings[3732], new named_type(IFC4X3_RC4_IfcSizeSelect_type), true),
            new attribute(strings[3733], new named_type(IFC4X3_RC4_IfcTextAlignment_type), true),
            new attribute(strings[3734], new named_type(IFC4X3_RC4_IfcTextDecoration_type), true),
            new attribute(strings[3735], new named_type(IFC4X3_RC4_IfcSizeSelect_type), true),
            new attribute(strings[3736], new named_type(IFC4X3_RC4_IfcSizeSelect_type), true),
            new attribute(strings[3737], new named_type(IFC4X3_RC4_IfcTextTransformation_type), true),
            new attribute(strings[3738], new named_type(IFC4X3_RC4_IfcSizeSelect_type), true)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTextureCoordinate_type->set_attributes({
            new attribute(strings[3739], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcSurfaceTexture_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcTextureCoordinateGenerator_type->set_attributes({
            new attribute(strings[3679], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[3681], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcReal_type)), true)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcTextureMap_type->set_attributes({
            new attribute(strings[3740], new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X3_RC4_IfcTextureVertex_type)), false),
            new attribute(strings[3219], new named_type(IFC4X3_RC4_IfcFace_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcTextureVertex_type->set_attributes({
            new attribute(strings[3004], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_RC4_IfcParameterValue_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcTextureVertexList_type->set_attributes({
            new attribute(strings[3741], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_RC4_IfcParameterValue_type))), false)
    },{
            false
    });
    IFC4X3_RC4_IfcThirdOrderPolynomialSpiral_type->set_attributes({
            new attribute(strings[3583], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false),
            new attribute(strings[3563], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3564], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3069], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcTimePeriod_type->set_attributes({
            new attribute(strings[3742], new named_type(IFC4X3_RC4_IfcTime_type), false),
            new attribute(strings[3743], new named_type(IFC4X3_RC4_IfcTime_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcTimeSeries_type->set_attributes({
            new attribute(strings[2905], new named_type(IFC4X3_RC4_IfcLabel_type), false),
            new attribute(strings[2875], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3742], new named_type(IFC4X3_RC4_IfcDateTime_type), false),
            new attribute(strings[3743], new named_type(IFC4X3_RC4_IfcDateTime_type), false),
            new attribute(strings[3744], new named_type(IFC4X3_RC4_IfcTimeSeriesDataTypeEnum_type), false),
            new attribute(strings[3561], new named_type(IFC4X3_RC4_IfcDataOriginEnum_type), false),
            new attribute(strings[3562], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3097], new named_type(IFC4X3_RC4_IfcUnit_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTimeSeriesValue_type->set_attributes({
            new attribute(strings[3233], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcValue_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcTopologicalRepresentationItem_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcTopologyRepresentation_type->set_attributes({
    },{
            false, false, false, false
    });
    IFC4X3_RC4_IfcToroidalSurface_type->set_attributes({
            new attribute(strings[3745], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3746], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false)
    },{
            false, false, false
    });
    IFC4X3_RC4_IfcTrackElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTrackElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTrackElementType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTrackElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTransformer_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTransformerTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTransformerType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTransformerTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTransportElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTransportElementTypeSelect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTransportElementType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTransportElementTypeSelect_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTrapeziumProfileDef_type->set_attributes({
            new attribute(strings[3747], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3748], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2991], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3749], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false)
    },{
            false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTriangulatedFaceSet_type->set_attributes({
            new attribute(strings[3750], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_RC4_IfcParameterValue_type))), true),
            new attribute(strings[3367], new named_type(IFC4X3_RC4_IfcBoolean_type), true),
            new attribute(strings[3224], new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X3_RC4_IfcPositiveInteger_type))), false),
            new attribute(strings[3369], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcPositiveInteger_type)), true)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcTriangulatedIrregularNetwork_type->set_attributes({
            new attribute(strings[3751], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcInteger_type)), false)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTrimmedCurve_type->set_attributes({
            new attribute(strings[3320], new named_type(IFC4X3_RC4_IfcCurve_type), false),
            new attribute(strings[3752], new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X3_RC4_IfcTrimmingSelect_type)), false),
            new attribute(strings[3753], new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X3_RC4_IfcTrimmingSelect_type)), false),
            new attribute(strings[3754], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3656], new named_type(IFC4X3_RC4_IfcTrimmingPreference_type), false)
    },{
            false, false, false, false, false
    });
    IFC4X3_RC4_IfcTubeBundle_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTubeBundleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTubeBundleType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcTubeBundleTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTypeObject_type->set_attributes({
            new attribute(strings[3755], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[3756], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPropertySetDefinition_type)), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTypeProcess_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2871], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3757], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTypeProduct_type->set_attributes({
            new attribute(strings[3758], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X3_RC4_IfcRepresentationMap_type)), true),
            new attribute(strings[3154], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcTypeResource_type->set_attributes({
            new attribute(strings[2925], new named_type(IFC4X3_RC4_IfcIdentifier_type), true),
            new attribute(strings[2871], new named_type(IFC4X3_RC4_IfcText_type), true),
            new attribute(strings[3759], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcUShapeProfileDef_type->set_attributes({
            new attribute(strings[2999], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3685], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2936], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3214], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3215], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3235], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3217], new named_type(IFC4X3_RC4_IfcPlaneAngleMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcUnitAssignment_type->set_attributes({
            new attribute(strings[3760], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcUnit_type)), false)
    },{
            false
    });
    IFC4X3_RC4_IfcUnitaryControlElement_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcUnitaryControlElementTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcUnitaryControlElementType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcUnitaryControlElementTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcUnitaryEquipment_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcUnitaryEquipmentTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcUnitaryEquipmentType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcUnitaryEquipmentTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcValve_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcValveTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcValveType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcValveTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcVector_type->set_attributes({
            new attribute(strings[3176], new named_type(IFC4X3_RC4_IfcDirection_type), false),
            new attribute(strings[3761], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcVertex_type->set_attributes({
    },{
            
    });
    IFC4X3_RC4_IfcVertexLoop_type->set_attributes({
            new attribute(strings[3762], new named_type(IFC4X3_RC4_IfcVertex_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcVertexPoint_type->set_attributes({
            new attribute(strings[3763], new named_type(IFC4X3_RC4_IfcPoint_type), false)
    },{
            false
    });
    IFC4X3_RC4_IfcVibrationDamper_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcVibrationDamperTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcVibrationDamperType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcVibrationDamperTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcVibrationIsolator_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcVibrationIsolatorTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcVibrationIsolatorType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcVibrationIsolatorTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcVirtualElement_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcVirtualGridIntersection_type->set_attributes({
            new attribute(strings[3764], new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X3_RC4_IfcGridAxis_type)), false),
            new attribute(strings[3765], new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X3_RC4_IfcLengthMeasure_type)), false)
    },{
            false, false
    });
    IFC4X3_RC4_IfcVoidStratum_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcVoidingFeature_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcVoidingFeatureTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWall_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWallTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWallElementedCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWallStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWallType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWallTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWasteTerminal_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWasteTerminalTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWasteTerminalType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWasteTerminalTypeEnum_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWaterStratum_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWindow_type->set_attributes({
            new attribute(strings[3126], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3127], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWindowTypeEnum_type), true),
            new attribute(strings[3766], new named_type(IFC4X3_RC4_IfcWindowTypePartitioningEnum_type), true),
            new attribute(strings[3767], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWindowLiningProperties_type->set_attributes({
            new attribute(strings[3130], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3131], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3134], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3768], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3769], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3770], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3771], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3772], new named_type(IFC4X3_RC4_IfcNormalisedRatioMeasure_type), true),
            new attribute(strings[3140], new named_type(IFC4X3_RC4_IfcShapeAspect_type), true),
            new attribute(strings[3136], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3141], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true),
            new attribute(strings[3142], new named_type(IFC4X3_RC4_IfcLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWindowPanelProperties_type->set_attributes({
            new attribute(strings[3128], new named_type(IFC4X3_RC4_IfcWindowPanelOperationEnum_type), false),
            new attribute(strings[3146], new named_type(IFC4X3_RC4_IfcWindowPanelPositionEnum_type), false),
            new attribute(strings[3341], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3342], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), true),
            new attribute(strings[3140], new named_type(IFC4X3_RC4_IfcShapeAspect_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWindowStandardCase_type->set_attributes({
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWindowStyle_type->set_attributes({
            new attribute(strings[3147], new named_type(IFC4X3_RC4_IfcWindowStyleConstructionEnum_type), false),
            new attribute(strings[3128], new named_type(IFC4X3_RC4_IfcWindowStyleOperationEnum_type), false),
            new attribute(strings[3148], new named_type(IFC4X3_RC4_IfcBoolean_type), false),
            new attribute(strings[3149], new named_type(IFC4X3_RC4_IfcBoolean_type), false)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWindowType_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWindowTypeEnum_type), false),
            new attribute(strings[3766], new named_type(IFC4X3_RC4_IfcWindowTypePartitioningEnum_type), false),
            new attribute(strings[3148], new named_type(IFC4X3_RC4_IfcBoolean_type), true),
            new attribute(strings[3767], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWorkCalendar_type->set_attributes({
            new attribute(strings[3773], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcWorkTime_type)), true),
            new attribute(strings[3774], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcWorkTime_type)), true),
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWorkCalendarTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWorkControl_type->set_attributes({
            new attribute(strings[3338], new named_type(IFC4X3_RC4_IfcDateTime_type), false),
            new attribute(strings[3775], new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X3_RC4_IfcPerson_type)), true),
            new attribute(strings[2876], new named_type(IFC4X3_RC4_IfcLabel_type), true),
            new attribute(strings[3776], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3701], new named_type(IFC4X3_RC4_IfcDuration_type), true),
            new attribute(strings[3742], new named_type(IFC4X3_RC4_IfcDateTime_type), false),
            new attribute(strings[3777], new named_type(IFC4X3_RC4_IfcDateTime_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWorkPlan_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWorkPlanTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWorkSchedule_type->set_attributes({
            new attribute(strings[2869], new named_type(IFC4X3_RC4_IfcWorkScheduleTypeEnum_type), true)
    },{
            false, false, false, false, false, false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcWorkTime_type->set_attributes({
            new attribute(strings[3778], new named_type(IFC4X3_RC4_IfcRecurrencePattern_type), true),
            new attribute(strings[3779], new named_type(IFC4X3_RC4_IfcDate_type), true),
            new attribute(strings[3780], new named_type(IFC4X3_RC4_IfcDate_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcZShapeProfileDef_type->set_attributes({
            new attribute(strings[2999], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3685], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[2936], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3214], new named_type(IFC4X3_RC4_IfcPositiveLengthMeasure_type), false),
            new attribute(strings[3215], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true),
            new attribute(strings[3235], new named_type(IFC4X3_RC4_IfcNonNegativeLengthMeasure_type), true)
    },{
            false, false, false, false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcZone_type->set_attributes({
            new attribute(strings[2998], new named_type(IFC4X3_RC4_IfcLabel_type), true)
    },{
            false, false, false, false, false, false
    });
    IFC4X3_RC4_IfcActor_type->set_inverse_attributes({
            new inverse_attribute(strings[3781], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToActor_type, IFC4X3_RC4_IfcRelAssignsToActor_type->attributes()[0])
    });
    IFC4X3_RC4_IfcActorRole_type->set_inverse_attributes({
            new inverse_attribute(strings[3782], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_RC4_IfcAddress_type->set_inverse_attributes({
            new inverse_attribute(strings[3783], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcPerson_type, IFC4X3_RC4_IfcPerson_type->attributes()[7]),
            new inverse_attribute(strings[3784], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcOrganization_type, IFC4X3_RC4_IfcOrganization_type->attributes()[4])
    });
    IFC4X3_RC4_IfcAnnotation_type->set_inverse_attributes({
            new inverse_attribute(strings[3785], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelContainedInSpatialStructure_type, IFC4X3_RC4_IfcRelContainedInSpatialStructure_type->attributes()[0])
    });
    IFC4X3_RC4_IfcAppliedValue_type->set_inverse_attributes({
            new inverse_attribute(strings[3782], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_RC4_IfcApproval_type->set_inverse_attributes({
            new inverse_attribute(strings[3786], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3787], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociatesApproval_type, IFC4X3_RC4_IfcRelAssociatesApproval_type->attributes()[0]),
            new inverse_attribute(strings[3788], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcResourceApprovalRelationship_type, IFC4X3_RC4_IfcResourceApprovalRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3789], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcApprovalRelationship_type, IFC4X3_RC4_IfcApprovalRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3790], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcApprovalRelationship_type, IFC4X3_RC4_IfcApprovalRelationship_type->attributes()[0])
    });
    IFC4X3_RC4_IfcClassification_type->set_inverse_attributes({
            new inverse_attribute(strings[3791], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociatesClassification_type, IFC4X3_RC4_IfcRelAssociatesClassification_type->attributes()[0]),
            new inverse_attribute(strings[3792], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcClassificationReference_type, IFC4X3_RC4_IfcClassificationReference_type->attributes()[0])
    });
    IFC4X3_RC4_IfcClassificationReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3793], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociatesClassification_type, IFC4X3_RC4_IfcRelAssociatesClassification_type->attributes()[0]),
            new inverse_attribute(strings[3792], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcClassificationReference_type, IFC4X3_RC4_IfcClassificationReference_type->attributes()[0])
    });
    IFC4X3_RC4_IfcConstraint_type->set_inverse_attributes({
            new inverse_attribute(strings[3786], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3794], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcResourceConstraintRelationship_type, IFC4X3_RC4_IfcResourceConstraintRelationship_type->attributes()[0])
    });
    IFC4X3_RC4_IfcContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3795], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelDefinesByProperties_type, IFC4X3_RC4_IfcRelDefinesByProperties_type->attributes()[0]),
            new inverse_attribute(strings[3796], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelDeclares_type, IFC4X3_RC4_IfcRelDeclares_type->attributes()[0])
    });
    IFC4X3_RC4_IfcContextDependentUnit_type->set_inverse_attributes({
            new inverse_attribute(strings[3782], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_RC4_IfcControl_type->set_inverse_attributes({
            new inverse_attribute(strings[3797], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToControl_type, IFC4X3_RC4_IfcRelAssignsToControl_type->attributes()[0])
    });
    IFC4X3_RC4_IfcConversionBasedUnit_type->set_inverse_attributes({
            new inverse_attribute(strings[3782], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_RC4_IfcCoordinateReferenceSystem_type->set_inverse_attributes({
            new inverse_attribute(strings[3798], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcCoordinateOperation_type, IFC4X3_RC4_IfcCoordinateOperation_type->attributes()[0])
    });
    IFC4X3_RC4_IfcCovering_type->set_inverse_attributes({
            new inverse_attribute(strings[3799], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelCoversSpaces_type, IFC4X3_RC4_IfcRelCoversSpaces_type->attributes()[1]),
            new inverse_attribute(strings[3800], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelCoversBldgElements_type, IFC4X3_RC4_IfcRelCoversBldgElements_type->attributes()[1])
    });
    IFC4X3_RC4_IfcDistributionControlElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3801], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelFlowControlElements_type, IFC4X3_RC4_IfcRelFlowControlElements_type->attributes()[0])
    });
    IFC4X3_RC4_IfcDistributionElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3802], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelConnectsPortToElement_type, IFC4X3_RC4_IfcRelConnectsPortToElement_type->attributes()[1])
    });
    IFC4X3_RC4_IfcDistributionFlowElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3803], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelFlowControlElements_type, IFC4X3_RC4_IfcRelFlowControlElements_type->attributes()[1])
    });
    IFC4X3_RC4_IfcDocumentInformation_type->set_inverse_attributes({
            new inverse_attribute(strings[3804], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociatesDocument_type, IFC4X3_RC4_IfcRelAssociatesDocument_type->attributes()[0]),
            new inverse_attribute(strings[3805], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcDocumentReference_type, IFC4X3_RC4_IfcDocumentReference_type->attributes()[1]),
            new inverse_attribute(strings[3806], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcDocumentInformationRelationship_type, IFC4X3_RC4_IfcDocumentInformationRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3807], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcDocumentInformationRelationship_type, IFC4X3_RC4_IfcDocumentInformationRelationship_type->attributes()[0])
    });
    IFC4X3_RC4_IfcDocumentReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3808], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociatesDocument_type, IFC4X3_RC4_IfcRelAssociatesDocument_type->attributes()[0])
    });
    IFC4X3_RC4_IfcElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3809], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelFillsElement_type, IFC4X3_RC4_IfcRelFillsElement_type->attributes()[1]),
            new inverse_attribute(strings[3810], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelConnectsElements_type, IFC4X3_RC4_IfcRelConnectsElements_type->attributes()[1]),
            new inverse_attribute(strings[3811], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelInterferesElements_type, IFC4X3_RC4_IfcRelInterferesElements_type->attributes()[1]),
            new inverse_attribute(strings[3812], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelInterferesElements_type, IFC4X3_RC4_IfcRelInterferesElements_type->attributes()[0]),
            new inverse_attribute(strings[3813], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelProjectsElement_type, IFC4X3_RC4_IfcRelProjectsElement_type->attributes()[0]),
            new inverse_attribute(strings[3814], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelVoidsElement_type, IFC4X3_RC4_IfcRelVoidsElement_type->attributes()[0]),
            new inverse_attribute(strings[3815], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelConnectsWithRealizingElements_type, IFC4X3_RC4_IfcRelConnectsWithRealizingElements_type->attributes()[0]),
            new inverse_attribute(strings[3816], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelSpaceBoundary_type, IFC4X3_RC4_IfcRelSpaceBoundary_type->attributes()[1]),
            new inverse_attribute(strings[3817], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelConnectsElements_type, IFC4X3_RC4_IfcRelConnectsElements_type->attributes()[2]),
            new inverse_attribute(strings[3785], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelContainedInSpatialStructure_type, IFC4X3_RC4_IfcRelContainedInSpatialStructure_type->attributes()[0]),
            new inverse_attribute(strings[3818], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelCoversBldgElements_type, IFC4X3_RC4_IfcRelCoversBldgElements_type->attributes()[0]),
            new inverse_attribute(strings[3819], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAdheresToElement_type, IFC4X3_RC4_IfcRelAdheresToElement_type->attributes()[0])
    });
    IFC4X3_RC4_IfcExternalReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3820], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[0])
    });
    IFC4X3_RC4_IfcExternalSpatialElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3821], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelSpaceBoundary_type, IFC4X3_RC4_IfcRelSpaceBoundary_type->attributes()[0])
    });
    IFC4X3_RC4_IfcFace_type->set_inverse_attributes({
            new inverse_attribute(strings[3822], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcTextureMap_type, IFC4X3_RC4_IfcTextureMap_type->attributes()[1])
    });
    IFC4X3_RC4_IfcFeatureElementAddition_type->set_inverse_attributes({
            new inverse_attribute(strings[3823], inverse_attribute::unspecified_type, -1, -1, IFC4X3_RC4_IfcRelProjectsElement_type, IFC4X3_RC4_IfcRelProjectsElement_type->attributes()[1])
    });
    IFC4X3_RC4_IfcFeatureElementSubtraction_type->set_inverse_attributes({
            new inverse_attribute(strings[3824], inverse_attribute::unspecified_type, -1, -1, IFC4X3_RC4_IfcRelVoidsElement_type, IFC4X3_RC4_IfcRelVoidsElement_type->attributes()[1])
    });
    IFC4X3_RC4_IfcGeometricRepresentationContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3825], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcGeometricRepresentationSubContext_type, IFC4X3_RC4_IfcGeometricRepresentationSubContext_type->attributes()[0]),
            new inverse_attribute(strings[3798], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcCoordinateOperation_type, IFC4X3_RC4_IfcCoordinateOperation_type->attributes()[0])
    });
    IFC4X3_RC4_IfcGridAxis_type->set_inverse_attributes({
            new inverse_attribute(strings[3826], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcGrid_type, IFC4X3_RC4_IfcGrid_type->attributes()[2]),
            new inverse_attribute(strings[3827], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcGrid_type, IFC4X3_RC4_IfcGrid_type->attributes()[1]),
            new inverse_attribute(strings[3828], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcGrid_type, IFC4X3_RC4_IfcGrid_type->attributes()[0]),
            new inverse_attribute(strings[3829], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcVirtualGridIntersection_type, IFC4X3_RC4_IfcVirtualGridIntersection_type->attributes()[0])
    });
    IFC4X3_RC4_IfcGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3830], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToGroup_type, IFC4X3_RC4_IfcRelAssignsToGroup_type->attributes()[0])
    });
    IFC4X3_RC4_IfcIndexedPolygonalFace_type->set_inverse_attributes({
            new inverse_attribute(strings[3831], inverse_attribute::set_type, 1, -1, IFC4X3_RC4_IfcPolygonalFaceSet_type, IFC4X3_RC4_IfcPolygonalFaceSet_type->attributes()[1])
    });
    IFC4X3_RC4_IfcLibraryInformation_type->set_inverse_attributes({
            new inverse_attribute(strings[3832], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociatesLibrary_type, IFC4X3_RC4_IfcRelAssociatesLibrary_type->attributes()[0]),
            new inverse_attribute(strings[3833], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcLibraryReference_type, IFC4X3_RC4_IfcLibraryReference_type->attributes()[2])
    });
    IFC4X3_RC4_IfcLibraryReference_type->set_inverse_attributes({
            new inverse_attribute(strings[3834], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociatesLibrary_type, IFC4X3_RC4_IfcRelAssociatesLibrary_type->attributes()[0])
    });
    IFC4X3_RC4_IfcMaterial_type->set_inverse_attributes({
            new inverse_attribute(strings[3835], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcMaterialDefinitionRepresentation_type, IFC4X3_RC4_IfcMaterialDefinitionRepresentation_type->attributes()[0]),
            new inverse_attribute(strings[3789], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcMaterialRelationship_type, IFC4X3_RC4_IfcMaterialRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3836], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcMaterialRelationship_type, IFC4X3_RC4_IfcMaterialRelationship_type->attributes()[0])
    });
    IFC4X3_RC4_IfcMaterialConstituent_type->set_inverse_attributes({
            new inverse_attribute(strings[3837], inverse_attribute::unspecified_type, -1, -1, IFC4X3_RC4_IfcMaterialConstituentSet_type, IFC4X3_RC4_IfcMaterialConstituentSet_type->attributes()[2])
    });
    IFC4X3_RC4_IfcMaterialDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3838], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociatesMaterial_type, IFC4X3_RC4_IfcRelAssociatesMaterial_type->attributes()[0]),
            new inverse_attribute(strings[3786], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3029], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcMaterialProperties_type, IFC4X3_RC4_IfcMaterialProperties_type->attributes()[0])
    });
    IFC4X3_RC4_IfcMaterialLayer_type->set_inverse_attributes({
            new inverse_attribute(strings[3839], inverse_attribute::unspecified_type, -1, -1, IFC4X3_RC4_IfcMaterialLayerSet_type, IFC4X3_RC4_IfcMaterialLayerSet_type->attributes()[0])
    });
    IFC4X3_RC4_IfcMaterialProfile_type->set_inverse_attributes({
            new inverse_attribute(strings[3840], inverse_attribute::unspecified_type, -1, -1, IFC4X3_RC4_IfcMaterialProfileSet_type, IFC4X3_RC4_IfcMaterialProfileSet_type->attributes()[2])
    });
    IFC4X3_RC4_IfcMaterialUsageDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3838], inverse_attribute::set_type, 1, -1, IFC4X3_RC4_IfcRelAssociatesMaterial_type, IFC4X3_RC4_IfcRelAssociatesMaterial_type->attributes()[0])
    });
    IFC4X3_RC4_IfcObject_type->set_inverse_attributes({
            new inverse_attribute(strings[3841], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelDefinesByObject_type, IFC4X3_RC4_IfcRelDefinesByObject_type->attributes()[0]),
            new inverse_attribute(strings[3796], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelDefinesByObject_type, IFC4X3_RC4_IfcRelDefinesByObject_type->attributes()[1]),
            new inverse_attribute(strings[3842], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelDefinesByType_type, IFC4X3_RC4_IfcRelDefinesByType_type->attributes()[0]),
            new inverse_attribute(strings[3795], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelDefinesByProperties_type, IFC4X3_RC4_IfcRelDefinesByProperties_type->attributes()[0])
    });
    IFC4X3_RC4_IfcObjectDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3843], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssigns_type, IFC4X3_RC4_IfcRelAssigns_type->attributes()[0]),
            new inverse_attribute(strings[3844], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelNests_type, IFC4X3_RC4_IfcRelNests_type->attributes()[1]),
            new inverse_attribute(strings[3845], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelNests_type, IFC4X3_RC4_IfcRelNests_type->attributes()[0]),
            new inverse_attribute(strings[3846], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelDeclares_type, IFC4X3_RC4_IfcRelDeclares_type->attributes()[1]),
            new inverse_attribute(strings[3847], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAggregates_type, IFC4X3_RC4_IfcRelAggregates_type->attributes()[0]),
            new inverse_attribute(strings[3848], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelAggregates_type, IFC4X3_RC4_IfcRelAggregates_type->attributes()[1]),
            new inverse_attribute(strings[3849], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociates_type, IFC4X3_RC4_IfcRelAssociates_type->attributes()[0])
    });
    IFC4X3_RC4_IfcObjectPlacement_type->set_inverse_attributes({
            new inverse_attribute(strings[3850], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcProduct_type, IFC4X3_RC4_IfcProduct_type->attributes()[0])
    });
    IFC4X3_RC4_IfcOpeningElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3851], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelFillsElement_type, IFC4X3_RC4_IfcRelFillsElement_type->attributes()[0])
    });
    IFC4X3_RC4_IfcOrganization_type->set_inverse_attributes({
            new inverse_attribute(strings[3852], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcOrganizationRelationship_type, IFC4X3_RC4_IfcOrganizationRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3790], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcOrganizationRelationship_type, IFC4X3_RC4_IfcOrganizationRelationship_type->attributes()[0]),
            new inverse_attribute(strings[3853], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcPersonAndOrganization_type, IFC4X3_RC4_IfcPersonAndOrganization_type->attributes()[1])
    });
    IFC4X3_RC4_IfcPerson_type->set_inverse_attributes({
            new inverse_attribute(strings[3854], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcPersonAndOrganization_type, IFC4X3_RC4_IfcPersonAndOrganization_type->attributes()[0])
    });
    IFC4X3_RC4_IfcPhysicalQuantity_type->set_inverse_attributes({
            new inverse_attribute(strings[3786], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3855], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcPhysicalComplexQuantity_type, IFC4X3_RC4_IfcPhysicalComplexQuantity_type->attributes()[0])
    });
    IFC4X3_RC4_IfcPort_type->set_inverse_attributes({
            new inverse_attribute(strings[3856], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelConnectsPortToElement_type, IFC4X3_RC4_IfcRelConnectsPortToElement_type->attributes()[0]),
            new inverse_attribute(strings[3817], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelConnectsPorts_type, IFC4X3_RC4_IfcRelConnectsPorts_type->attributes()[1]),
            new inverse_attribute(strings[3810], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelConnectsPorts_type, IFC4X3_RC4_IfcRelConnectsPorts_type->attributes()[0])
    });
    IFC4X3_RC4_IfcPositioningElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3785], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelContainedInSpatialStructure_type, IFC4X3_RC4_IfcRelContainedInSpatialStructure_type->attributes()[0]),
            new inverse_attribute(strings[3857], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelPositions_type, IFC4X3_RC4_IfcRelPositions_type->attributes()[0])
    });
    IFC4X3_RC4_IfcProcess_type->set_inverse_attributes({
            new inverse_attribute(strings[3858], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelSequence_type, IFC4X3_RC4_IfcRelSequence_type->attributes()[0]),
            new inverse_attribute(strings[3859], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelSequence_type, IFC4X3_RC4_IfcRelSequence_type->attributes()[1]),
            new inverse_attribute(strings[3860], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToProcess_type, IFC4X3_RC4_IfcRelAssignsToProcess_type->attributes()[0])
    });
    IFC4X3_RC4_IfcProduct_type->set_inverse_attributes({
            new inverse_attribute(strings[3861], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToProduct_type, IFC4X3_RC4_IfcRelAssignsToProduct_type->attributes()[0]),
            new inverse_attribute(strings[3862], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelPositions_type, IFC4X3_RC4_IfcRelPositions_type->attributes()[1]),
            new inverse_attribute(strings[3863], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type, IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type->attributes()[0])
    });
    IFC4X3_RC4_IfcProductDefinitionShape_type->set_inverse_attributes({
            new inverse_attribute(strings[3864], inverse_attribute::set_type, 1, -1, IFC4X3_RC4_IfcProduct_type, IFC4X3_RC4_IfcProduct_type->attributes()[1]),
            new inverse_attribute(strings[3865], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcShapeAspect_type, IFC4X3_RC4_IfcShapeAspect_type->attributes()[4])
    });
    IFC4X3_RC4_IfcProfileDef_type->set_inverse_attributes({
            new inverse_attribute(strings[3782], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3029], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcProfileProperties_type, IFC4X3_RC4_IfcProfileProperties_type->attributes()[0])
    });
    IFC4X3_RC4_IfcProperty_type->set_inverse_attributes({
            new inverse_attribute(strings[3866], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcPropertySet_type, IFC4X3_RC4_IfcPropertySet_type->attributes()[0]),
            new inverse_attribute(strings[3867], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcPropertyDependencyRelationship_type, IFC4X3_RC4_IfcPropertyDependencyRelationship_type->attributes()[0]),
            new inverse_attribute(strings[3868], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcPropertyDependencyRelationship_type, IFC4X3_RC4_IfcPropertyDependencyRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3855], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcComplexProperty_type, IFC4X3_RC4_IfcComplexProperty_type->attributes()[1]),
            new inverse_attribute(strings[3869], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcResourceConstraintRelationship_type, IFC4X3_RC4_IfcResourceConstraintRelationship_type->attributes()[1]),
            new inverse_attribute(strings[3870], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcResourceApprovalRelationship_type, IFC4X3_RC4_IfcResourceApprovalRelationship_type->attributes()[0])
    });
    IFC4X3_RC4_IfcPropertyAbstraction_type->set_inverse_attributes({
            new inverse_attribute(strings[3786], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_RC4_IfcPropertyDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3846], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelDeclares_type, IFC4X3_RC4_IfcRelDeclares_type->attributes()[1]),
            new inverse_attribute(strings[3849], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssociates_type, IFC4X3_RC4_IfcRelAssociates_type->attributes()[0])
    });
    IFC4X3_RC4_IfcPropertySetDefinition_type->set_inverse_attributes({
            new inverse_attribute(strings[3871], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcTypeObject_type, IFC4X3_RC4_IfcTypeObject_type->attributes()[1]),
            new inverse_attribute(strings[3795], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelDefinesByTemplate_type, IFC4X3_RC4_IfcRelDefinesByTemplate_type->attributes()[0]),
            new inverse_attribute(strings[3872], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelDefinesByProperties_type, IFC4X3_RC4_IfcRelDefinesByProperties_type->attributes()[1])
    });
    IFC4X3_RC4_IfcPropertySetTemplate_type->set_inverse_attributes({
            new inverse_attribute(strings[3873], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelDefinesByTemplate_type, IFC4X3_RC4_IfcRelDefinesByTemplate_type->attributes()[1])
    });
    IFC4X3_RC4_IfcPropertyTemplate_type->set_inverse_attributes({
            new inverse_attribute(strings[3874], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcComplexPropertyTemplate_type, IFC4X3_RC4_IfcComplexPropertyTemplate_type->attributes()[2]),
            new inverse_attribute(strings[3875], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcPropertySetTemplate_type, IFC4X3_RC4_IfcPropertySetTemplate_type->attributes()[2])
    });
    IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type->set_inverse_attributes({
            new inverse_attribute(strings[2900], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type, IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type->attributes()[0])
    });
    IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type->set_inverse_attributes({
            new inverse_attribute(strings[3876], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type, IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type->attributes()[0])
    });
    IFC4X3_RC4_IfcRepresentation_type->set_inverse_attributes({
            new inverse_attribute(strings[3877], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRepresentationMap_type, IFC4X3_RC4_IfcRepresentationMap_type->attributes()[1]),
            new inverse_attribute(strings[3878], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcPresentationLayerAssignment_type, IFC4X3_RC4_IfcPresentationLayerAssignment_type->attributes()[2]),
            new inverse_attribute(strings[3879], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcProductRepresentation_type, IFC4X3_RC4_IfcProductRepresentation_type->attributes()[2])
    });
    IFC4X3_RC4_IfcRepresentationContext_type->set_inverse_attributes({
            new inverse_attribute(strings[3880], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRepresentation_type, IFC4X3_RC4_IfcRepresentation_type->attributes()[0])
    });
    IFC4X3_RC4_IfcRepresentationItem_type->set_inverse_attributes({
            new inverse_attribute(strings[3881], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcPresentationLayerAssignment_type, IFC4X3_RC4_IfcPresentationLayerAssignment_type->attributes()[2]),
            new inverse_attribute(strings[3882], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcStyledItem_type, IFC4X3_RC4_IfcStyledItem_type->attributes()[0])
    });
    IFC4X3_RC4_IfcRepresentationMap_type->set_inverse_attributes({
            new inverse_attribute(strings[3865], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcShapeAspect_type, IFC4X3_RC4_IfcShapeAspect_type->attributes()[4]),
            new inverse_attribute(strings[3883], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcMappedItem_type, IFC4X3_RC4_IfcMappedItem_type->attributes()[0])
    });
    IFC4X3_RC4_IfcResource_type->set_inverse_attributes({
            new inverse_attribute(strings[3884], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToResource_type, IFC4X3_RC4_IfcRelAssignsToResource_type->attributes()[0])
    });
    IFC4X3_RC4_IfcSegment_type->set_inverse_attributes({
            new inverse_attribute(strings[3885], inverse_attribute::set_type, 1, -1, IFC4X3_RC4_IfcCompositeCurve_type, IFC4X3_RC4_IfcCompositeCurve_type->attributes()[0])
    });
    IFC4X3_RC4_IfcShapeAspect_type->set_inverse_attributes({
            new inverse_attribute(strings[3786], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_RC4_IfcShapeModel_type->set_inverse_attributes({
            new inverse_attribute(strings[3886], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcShapeAspect_type, IFC4X3_RC4_IfcShapeAspect_type->attributes()[0])
    });
    IFC4X3_RC4_IfcSpace_type->set_inverse_attributes({
            new inverse_attribute(strings[3818], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelCoversSpaces_type, IFC4X3_RC4_IfcRelCoversSpaces_type->attributes()[0]),
            new inverse_attribute(strings[3821], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelSpaceBoundary_type, IFC4X3_RC4_IfcRelSpaceBoundary_type->attributes()[0])
    });
    IFC4X3_RC4_IfcSpatialElement_type->set_inverse_attributes({
            new inverse_attribute(strings[3887], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelContainedInSpatialStructure_type, IFC4X3_RC4_IfcRelContainedInSpatialStructure_type->attributes()[1]),
            new inverse_attribute(strings[3888], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelServicesBuildings_type, IFC4X3_RC4_IfcRelServicesBuildings_type->attributes()[1]),
            new inverse_attribute(strings[3889], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type, IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type->attributes()[1])
    });
    IFC4X3_RC4_IfcStructuralActivity_type->set_inverse_attributes({
            new inverse_attribute(strings[3890], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelConnectsStructuralActivity_type, IFC4X3_RC4_IfcRelConnectsStructuralActivity_type->attributes()[1])
    });
    IFC4X3_RC4_IfcStructuralConnection_type->set_inverse_attributes({
            new inverse_attribute(strings[3891], inverse_attribute::set_type, 1, -1, IFC4X3_RC4_IfcRelConnectsStructuralMember_type, IFC4X3_RC4_IfcRelConnectsStructuralMember_type->attributes()[1])
    });
    IFC4X3_RC4_IfcStructuralItem_type->set_inverse_attributes({
            new inverse_attribute(strings[3892], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelConnectsStructuralActivity_type, IFC4X3_RC4_IfcRelConnectsStructuralActivity_type->attributes()[0])
    });
    IFC4X3_RC4_IfcStructuralLoadGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3893], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcStructuralResultGroup_type, IFC4X3_RC4_IfcStructuralResultGroup_type->attributes()[1]),
            new inverse_attribute(strings[3894], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcStructuralAnalysisModel_type, IFC4X3_RC4_IfcStructuralAnalysisModel_type->attributes()[2])
    });
    IFC4X3_RC4_IfcStructuralMember_type->set_inverse_attributes({
            new inverse_attribute(strings[3895], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelConnectsStructuralMember_type, IFC4X3_RC4_IfcRelConnectsStructuralMember_type->attributes()[0])
    });
    IFC4X3_RC4_IfcStructuralResultGroup_type->set_inverse_attributes({
            new inverse_attribute(strings[3896], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcStructuralAnalysisModel_type, IFC4X3_RC4_IfcStructuralAnalysisModel_type->attributes()[3])
    });
    IFC4X3_RC4_IfcSurfaceFeature_type->set_inverse_attributes({
            new inverse_attribute(strings[3897], inverse_attribute::unspecified_type, -1, -1, IFC4X3_RC4_IfcRelAdheresToElement_type, IFC4X3_RC4_IfcRelAdheresToElement_type->attributes()[1])
    });
    IFC4X3_RC4_IfcSurfaceTexture_type->set_inverse_attributes({
            new inverse_attribute(strings[3898], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcTextureCoordinate_type, IFC4X3_RC4_IfcTextureCoordinate_type->attributes()[0]),
            new inverse_attribute(strings[3899], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcSurfaceStyleWithTextures_type, IFC4X3_RC4_IfcSurfaceStyleWithTextures_type->attributes()[0])
    });
    IFC4X3_RC4_IfcSystem_type->set_inverse_attributes({
            new inverse_attribute(strings[3900], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelServicesBuildings_type, IFC4X3_RC4_IfcRelServicesBuildings_type->attributes()[0]),
            new inverse_attribute(strings[3901], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type, IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type->attributes()[0])
    });
    IFC4X3_RC4_IfcTessellatedFaceSet_type->set_inverse_attributes({
            new inverse_attribute(strings[3902], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcIndexedColourMap_type, IFC4X3_RC4_IfcIndexedColourMap_type->attributes()[0]),
            new inverse_attribute(strings[3903], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcIndexedTextureMap_type, IFC4X3_RC4_IfcIndexedTextureMap_type->attributes()[0])
    });
    IFC4X3_RC4_IfcTimeSeries_type->set_inverse_attributes({
            new inverse_attribute(strings[3782], inverse_attribute::set_type, 1, -1, IFC4X3_RC4_IfcExternalReferenceRelationship_type, IFC4X3_RC4_IfcExternalReferenceRelationship_type->attributes()[1])
    });
    IFC4X3_RC4_IfcTypeObject_type->set_inverse_attributes({
            new inverse_attribute(strings[3904], inverse_attribute::set_type, 0, 1, IFC4X3_RC4_IfcRelDefinesByType_type, IFC4X3_RC4_IfcRelDefinesByType_type->attributes()[1])
    });
    IFC4X3_RC4_IfcTypeProcess_type->set_inverse_attributes({
            new inverse_attribute(strings[3860], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToProcess_type, IFC4X3_RC4_IfcRelAssignsToProcess_type->attributes()[0])
    });
    IFC4X3_RC4_IfcTypeProduct_type->set_inverse_attributes({
            new inverse_attribute(strings[3861], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToProduct_type, IFC4X3_RC4_IfcRelAssignsToProduct_type->attributes()[0])
    });
    IFC4X3_RC4_IfcTypeResource_type->set_inverse_attributes({
            new inverse_attribute(strings[3884], inverse_attribute::set_type, 0, -1, IFC4X3_RC4_IfcRelAssignsToResource_type, IFC4X3_RC4_IfcRelAssignsToResource_type->attributes()[0])
    });
    IFC4X3_RC4_IfcControl_type->set_subtypes({
        IFC4X3_RC4_IfcActionRequest_type,IFC4X3_RC4_IfcCostItem_type,IFC4X3_RC4_IfcCostSchedule_type,IFC4X3_RC4_IfcPerformanceHistory_type,IFC4X3_RC4_IfcPermit_type,IFC4X3_RC4_IfcProjectOrder_type,IFC4X3_RC4_IfcWorkCalendar_type,IFC4X3_RC4_IfcWorkControl_type
    });
    IFC4X3_RC4_IfcObject_type->set_subtypes({
        IFC4X3_RC4_IfcActor_type,IFC4X3_RC4_IfcControl_type,IFC4X3_RC4_IfcGroup_type,IFC4X3_RC4_IfcProcess_type,IFC4X3_RC4_IfcProduct_type,IFC4X3_RC4_IfcResource_type
    });
    IFC4X3_RC4_IfcDistributionControlElement_type->set_subtypes({
        IFC4X3_RC4_IfcActuator_type,IFC4X3_RC4_IfcAlarm_type,IFC4X3_RC4_IfcController_type,IFC4X3_RC4_IfcFlowInstrument_type,IFC4X3_RC4_IfcProtectiveDeviceTrippingUnit_type,IFC4X3_RC4_IfcSensor_type,IFC4X3_RC4_IfcUnitaryControlElement_type
    });
    IFC4X3_RC4_IfcDistributionControlElementType_type->set_subtypes({
        IFC4X3_RC4_IfcActuatorType_type,IFC4X3_RC4_IfcAlarmType_type,IFC4X3_RC4_IfcControllerType_type,IFC4X3_RC4_IfcFlowInstrumentType_type,IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitType_type,IFC4X3_RC4_IfcSensorType_type,IFC4X3_RC4_IfcUnitaryControlElementType_type
    });
    IFC4X3_RC4_IfcManifoldSolidBrep_type->set_subtypes({
        IFC4X3_RC4_IfcAdvancedBrep_type,IFC4X3_RC4_IfcFacetedBrep_type
    });
    IFC4X3_RC4_IfcAdvancedBrep_type->set_subtypes({
        IFC4X3_RC4_IfcAdvancedBrepWithVoids_type
    });
    IFC4X3_RC4_IfcFaceSurface_type->set_subtypes({
        IFC4X3_RC4_IfcAdvancedFace_type
    });
    IFC4X3_RC4_IfcFlowTerminal_type->set_subtypes({
        IFC4X3_RC4_IfcAirTerminal_type,IFC4X3_RC4_IfcAudioVisualAppliance_type,IFC4X3_RC4_IfcCommunicationsAppliance_type,IFC4X3_RC4_IfcElectricAppliance_type,IFC4X3_RC4_IfcFireSuppressionTerminal_type,IFC4X3_RC4_IfcLamp_type,IFC4X3_RC4_IfcLightFixture_type,IFC4X3_RC4_IfcLiquidTerminal_type,IFC4X3_RC4_IfcMedicalDevice_type,IFC4X3_RC4_IfcMobileTelecommunicationsAppliance_type,IFC4X3_RC4_IfcOutlet_type,IFC4X3_RC4_IfcSanitaryTerminal_type,IFC4X3_RC4_IfcSignal_type,IFC4X3_RC4_IfcSpaceHeater_type,IFC4X3_RC4_IfcStackTerminal_type,IFC4X3_RC4_IfcWasteTerminal_type
    });
    IFC4X3_RC4_IfcFlowController_type->set_subtypes({
        IFC4X3_RC4_IfcAirTerminalBox_type,IFC4X3_RC4_IfcDamper_type,IFC4X3_RC4_IfcDistributionBoard_type,IFC4X3_RC4_IfcElectricDistributionBoard_type,IFC4X3_RC4_IfcElectricTimeControl_type,IFC4X3_RC4_IfcFlowMeter_type,IFC4X3_RC4_IfcProtectiveDevice_type,IFC4X3_RC4_IfcSwitchingDevice_type,IFC4X3_RC4_IfcValve_type
    });
    IFC4X3_RC4_IfcFlowControllerType_type->set_subtypes({
        IFC4X3_RC4_IfcAirTerminalBoxType_type,IFC4X3_RC4_IfcDamperType_type,IFC4X3_RC4_IfcDistributionBoardType_type,IFC4X3_RC4_IfcElectricDistributionBoardType_type,IFC4X3_RC4_IfcElectricTimeControlType_type,IFC4X3_RC4_IfcFlowMeterType_type,IFC4X3_RC4_IfcProtectiveDeviceType_type,IFC4X3_RC4_IfcSwitchingDeviceType_type,IFC4X3_RC4_IfcValveType_type
    });
    IFC4X3_RC4_IfcFlowTerminalType_type->set_subtypes({
        IFC4X3_RC4_IfcAirTerminalType_type,IFC4X3_RC4_IfcAudioVisualApplianceType_type,IFC4X3_RC4_IfcCommunicationsApplianceType_type,IFC4X3_RC4_IfcElectricApplianceType_type,IFC4X3_RC4_IfcFireSuppressionTerminalType_type,IFC4X3_RC4_IfcLampType_type,IFC4X3_RC4_IfcLightFixtureType_type,IFC4X3_RC4_IfcLiquidTerminalType_type,IFC4X3_RC4_IfcMedicalDeviceType_type,IFC4X3_RC4_IfcMobileTelecommunicationsApplianceType_type,IFC4X3_RC4_IfcOutletType_type,IFC4X3_RC4_IfcSanitaryTerminalType_type,IFC4X3_RC4_IfcSignalType_type,IFC4X3_RC4_IfcSpaceHeaterType_type,IFC4X3_RC4_IfcStackTerminalType_type,IFC4X3_RC4_IfcWasteTerminalType_type
    });
    IFC4X3_RC4_IfcEnergyConversionDevice_type->set_subtypes({
        IFC4X3_RC4_IfcAirToAirHeatRecovery_type,IFC4X3_RC4_IfcBoiler_type,IFC4X3_RC4_IfcBurner_type,IFC4X3_RC4_IfcChiller_type,IFC4X3_RC4_IfcCoil_type,IFC4X3_RC4_IfcCondenser_type,IFC4X3_RC4_IfcCooledBeam_type,IFC4X3_RC4_IfcCoolingTower_type,IFC4X3_RC4_IfcElectricGenerator_type,IFC4X3_RC4_IfcElectricMotor_type,IFC4X3_RC4_IfcEngine_type,IFC4X3_RC4_IfcEvaporativeCooler_type,IFC4X3_RC4_IfcEvaporator_type,IFC4X3_RC4_IfcHeatExchanger_type,IFC4X3_RC4_IfcHumidifier_type,IFC4X3_RC4_IfcMotorConnection_type,IFC4X3_RC4_IfcSolarDevice_type,IFC4X3_RC4_IfcTransformer_type,IFC4X3_RC4_IfcTubeBundle_type,IFC4X3_RC4_IfcUnitaryEquipment_type
    });
    IFC4X3_RC4_IfcEnergyConversionDeviceType_type->set_subtypes({
        IFC4X3_RC4_IfcAirToAirHeatRecoveryType_type,IFC4X3_RC4_IfcBoilerType_type,IFC4X3_RC4_IfcBurnerType_type,IFC4X3_RC4_IfcChillerType_type,IFC4X3_RC4_IfcCoilType_type,IFC4X3_RC4_IfcCondenserType_type,IFC4X3_RC4_IfcCooledBeamType_type,IFC4X3_RC4_IfcCoolingTowerType_type,IFC4X3_RC4_IfcElectricGeneratorType_type,IFC4X3_RC4_IfcElectricMotorType_type,IFC4X3_RC4_IfcEngineType_type,IFC4X3_RC4_IfcEvaporativeCoolerType_type,IFC4X3_RC4_IfcEvaporatorType_type,IFC4X3_RC4_IfcHeatExchangerType_type,IFC4X3_RC4_IfcHumidifierType_type,IFC4X3_RC4_IfcMotorConnectionType_type,IFC4X3_RC4_IfcSolarDeviceType_type,IFC4X3_RC4_IfcTransformerType_type,IFC4X3_RC4_IfcTubeBundleType_type,IFC4X3_RC4_IfcUnitaryEquipmentType_type
    });
    IFC4X3_RC4_IfcLinearPositioningElement_type->set_subtypes({
        IFC4X3_RC4_IfcAlignment_type
    });
    IFC4X3_RC4_IfcLinearElement_type->set_subtypes({
        IFC4X3_RC4_IfcAlignmentCant_type,IFC4X3_RC4_IfcAlignmentHorizontal_type,IFC4X3_RC4_IfcAlignmentSegment_type,IFC4X3_RC4_IfcAlignmentVertical_type
    });
    IFC4X3_RC4_IfcAlignmentParameterSegment_type->set_subtypes({
        IFC4X3_RC4_IfcAlignmentCantSegment_type,IFC4X3_RC4_IfcAlignmentHorizontalSegment_type,IFC4X3_RC4_IfcAlignmentVerticalSegment_type
    });
    IFC4X3_RC4_IfcProduct_type->set_subtypes({
        IFC4X3_RC4_IfcAnnotation_type,IFC4X3_RC4_IfcElement_type,IFC4X3_RC4_IfcLinearElement_type,IFC4X3_RC4_IfcPort_type,IFC4X3_RC4_IfcPositioningElement_type,IFC4X3_RC4_IfcProxy_type,IFC4X3_RC4_IfcSpatialElement_type,IFC4X3_RC4_IfcStructuralActivity_type,IFC4X3_RC4_IfcStructuralItem_type
    });
    IFC4X3_RC4_IfcGeometricRepresentationItem_type->set_subtypes({
        IFC4X3_RC4_IfcAnnotationFillArea_type,IFC4X3_RC4_IfcBooleanResult_type,IFC4X3_RC4_IfcBoundingBox_type,IFC4X3_RC4_IfcCartesianPointList_type,IFC4X3_RC4_IfcCartesianTransformationOperator_type,IFC4X3_RC4_IfcCsgPrimitive3D_type,IFC4X3_RC4_IfcCurve_type,IFC4X3_RC4_IfcDirection_type,IFC4X3_RC4_IfcFaceBasedSurfaceModel_type,IFC4X3_RC4_IfcFillAreaStyleHatching_type,IFC4X3_RC4_IfcFillAreaStyleTiles_type,IFC4X3_RC4_IfcGeometricSet_type,IFC4X3_RC4_IfcHalfSpaceSolid_type,IFC4X3_RC4_IfcLightSource_type,IFC4X3_RC4_IfcPlacement_type,IFC4X3_RC4_IfcPlanarExtent_type,IFC4X3_RC4_IfcPoint_type,IFC4X3_RC4_IfcSectionedSpine_type,IFC4X3_RC4_IfcSegment_type,IFC4X3_RC4_IfcShellBasedSurfaceModel_type,IFC4X3_RC4_IfcSolidModel_type,IFC4X3_RC4_IfcSurface_type,IFC4X3_RC4_IfcTessellatedItem_type,IFC4X3_RC4_IfcTextLiteral_type,IFC4X3_RC4_IfcVector_type
    });
    IFC4X3_RC4_IfcResourceLevelRelationship_type->set_subtypes({
        IFC4X3_RC4_IfcApprovalRelationship_type,IFC4X3_RC4_IfcCurrencyRelationship_type,IFC4X3_RC4_IfcDocumentInformationRelationship_type,IFC4X3_RC4_IfcExternalReferenceRelationship_type,IFC4X3_RC4_IfcMaterialRelationship_type,IFC4X3_RC4_IfcOrganizationRelationship_type,IFC4X3_RC4_IfcPropertyDependencyRelationship_type,IFC4X3_RC4_IfcResourceApprovalRelationship_type,IFC4X3_RC4_IfcResourceConstraintRelationship_type
    });
    IFC4X3_RC4_IfcProfileDef_type->set_subtypes({
        IFC4X3_RC4_IfcArbitraryClosedProfileDef_type,IFC4X3_RC4_IfcArbitraryOpenProfileDef_type,IFC4X3_RC4_IfcCompositeProfileDef_type,IFC4X3_RC4_IfcDerivedProfileDef_type,IFC4X3_RC4_IfcOpenCrossProfileDef_type,IFC4X3_RC4_IfcParameterizedProfileDef_type
    });
    IFC4X3_RC4_IfcArbitraryClosedProfileDef_type->set_subtypes({
        IFC4X3_RC4_IfcArbitraryProfileDefWithVoids_type
    });
    IFC4X3_RC4_IfcGroup_type->set_subtypes({
        IFC4X3_RC4_IfcAsset_type,IFC4X3_RC4_IfcInventory_type,IFC4X3_RC4_IfcStructuralLoadGroup_type,IFC4X3_RC4_IfcStructuralResultGroup_type,IFC4X3_RC4_IfcSystem_type
    });
    IFC4X3_RC4_IfcParameterizedProfileDef_type->set_subtypes({
        IFC4X3_RC4_IfcAsymmetricIShapeProfileDef_type,IFC4X3_RC4_IfcCShapeProfileDef_type,IFC4X3_RC4_IfcCircleProfileDef_type,IFC4X3_RC4_IfcEllipseProfileDef_type,IFC4X3_RC4_IfcIShapeProfileDef_type,IFC4X3_RC4_IfcLShapeProfileDef_type,IFC4X3_RC4_IfcRectangleProfileDef_type,IFC4X3_RC4_IfcTShapeProfileDef_type,IFC4X3_RC4_IfcTrapeziumProfileDef_type,IFC4X3_RC4_IfcUShapeProfileDef_type,IFC4X3_RC4_IfcZShapeProfileDef_type
    });
    IFC4X3_RC4_IfcPlacement_type->set_subtypes({
        IFC4X3_RC4_IfcAxis1Placement_type,IFC4X3_RC4_IfcAxis2Placement2D_type,IFC4X3_RC4_IfcAxis2Placement3D_type,IFC4X3_RC4_IfcAxis2PlacementLinear_type
    });
    IFC4X3_RC4_IfcBoundedCurve_type->set_subtypes({
        IFC4X3_RC4_IfcBSplineCurve_type,IFC4X3_RC4_IfcCompositeCurve_type,IFC4X3_RC4_IfcIndexedPolyCurve_type,IFC4X3_RC4_IfcPolyline_type,IFC4X3_RC4_IfcTrimmedCurve_type
    });
    IFC4X3_RC4_IfcBSplineCurve_type->set_subtypes({
        IFC4X3_RC4_IfcBSplineCurveWithKnots_type
    });
    IFC4X3_RC4_IfcBoundedSurface_type->set_subtypes({
        IFC4X3_RC4_IfcBSplineSurface_type,IFC4X3_RC4_IfcCurveBoundedPlane_type,IFC4X3_RC4_IfcCurveBoundedSurface_type,IFC4X3_RC4_IfcRectangularTrimmedSurface_type
    });
    IFC4X3_RC4_IfcBSplineSurface_type->set_subtypes({
        IFC4X3_RC4_IfcBSplineSurfaceWithKnots_type
    });
    IFC4X3_RC4_IfcBuiltElement_type->set_subtypes({
        IFC4X3_RC4_IfcBeam_type,IFC4X3_RC4_IfcBearing_type,IFC4X3_RC4_IfcBuildingElementProxy_type,IFC4X3_RC4_IfcChimney_type,IFC4X3_RC4_IfcColumn_type,IFC4X3_RC4_IfcCourse_type,IFC4X3_RC4_IfcCovering_type,IFC4X3_RC4_IfcCurtainWall_type,IFC4X3_RC4_IfcDeepFoundation_type,IFC4X3_RC4_IfcDoor_type,IFC4X3_RC4_IfcEarthworksElement_type,IFC4X3_RC4_IfcFooting_type,IFC4X3_RC4_IfcKerb_type,IFC4X3_RC4_IfcMember_type,IFC4X3_RC4_IfcMooringDevice_type,IFC4X3_RC4_IfcNavigationElement_type,IFC4X3_RC4_IfcPavement_type,IFC4X3_RC4_IfcPlate_type,IFC4X3_RC4_IfcRail_type,IFC4X3_RC4_IfcRailing_type,IFC4X3_RC4_IfcRamp_type,IFC4X3_RC4_IfcRampFlight_type,IFC4X3_RC4_IfcRoof_type,IFC4X3_RC4_IfcShadingDevice_type,IFC4X3_RC4_IfcSlab_type,IFC4X3_RC4_IfcStair_type,IFC4X3_RC4_IfcStairFlight_type,IFC4X3_RC4_IfcTrackElement_type,IFC4X3_RC4_IfcWall_type,IFC4X3_RC4_IfcWindow_type
    });
    IFC4X3_RC4_IfcBeam_type->set_subtypes({
        IFC4X3_RC4_IfcBeamStandardCase_type
    });
    IFC4X3_RC4_IfcBuiltElementType_type->set_subtypes({
        IFC4X3_RC4_IfcBeamType_type,IFC4X3_RC4_IfcBearingType_type,IFC4X3_RC4_IfcBuildingElementProxyType_type,IFC4X3_RC4_IfcChimneyType_type,IFC4X3_RC4_IfcColumnType_type,IFC4X3_RC4_IfcCourseType_type,IFC4X3_RC4_IfcCoveringType_type,IFC4X3_RC4_IfcCurtainWallType_type,IFC4X3_RC4_IfcDeepFoundationType_type,IFC4X3_RC4_IfcDoorType_type,IFC4X3_RC4_IfcFootingType_type,IFC4X3_RC4_IfcKerbType_type,IFC4X3_RC4_IfcMemberType_type,IFC4X3_RC4_IfcMooringDeviceType_type,IFC4X3_RC4_IfcNavigationElementType_type,IFC4X3_RC4_IfcPavementType_type,IFC4X3_RC4_IfcPlateType_type,IFC4X3_RC4_IfcRailType_type,IFC4X3_RC4_IfcRailingType_type,IFC4X3_RC4_IfcRampFlightType_type,IFC4X3_RC4_IfcRampType_type,IFC4X3_RC4_IfcRoofType_type,IFC4X3_RC4_IfcShadingDeviceType_type,IFC4X3_RC4_IfcSlabType_type,IFC4X3_RC4_IfcStairFlightType_type,IFC4X3_RC4_IfcStairType_type,IFC4X3_RC4_IfcTrackElementType_type,IFC4X3_RC4_IfcWallType_type,IFC4X3_RC4_IfcWindowType_type
    });
    IFC4X3_RC4_IfcSurfaceTexture_type->set_subtypes({
        IFC4X3_RC4_IfcBlobTexture_type,IFC4X3_RC4_IfcImageTexture_type,IFC4X3_RC4_IfcPixelTexture_type
    });
    IFC4X3_RC4_IfcCsgPrimitive3D_type->set_subtypes({
        IFC4X3_RC4_IfcBlock_type,IFC4X3_RC4_IfcRectangularPyramid_type,IFC4X3_RC4_IfcRightCircularCone_type,IFC4X3_RC4_IfcRightCircularCylinder_type,IFC4X3_RC4_IfcSphere_type
    });
    IFC4X3_RC4_IfcBooleanResult_type->set_subtypes({
        IFC4X3_RC4_IfcBooleanClippingResult_type
    });
    IFC4X3_RC4_IfcGeotechnicalAssembly_type->set_subtypes({
        IFC4X3_RC4_IfcBorehole_type,IFC4X3_RC4_IfcGeomodel_type,IFC4X3_RC4_IfcGeoslice_type
    });
    IFC4X3_RC4_IfcCompositeCurveOnSurface_type->set_subtypes({
        IFC4X3_RC4_IfcBoundaryCurve_type
    });
    IFC4X3_RC4_IfcBoundaryCondition_type->set_subtypes({
        IFC4X3_RC4_IfcBoundaryEdgeCondition_type,IFC4X3_RC4_IfcBoundaryFaceCondition_type,IFC4X3_RC4_IfcBoundaryNodeCondition_type
    });
    IFC4X3_RC4_IfcBoundaryNodeCondition_type->set_subtypes({
        IFC4X3_RC4_IfcBoundaryNodeConditionWarping_type
    });
    IFC4X3_RC4_IfcCurve_type->set_subtypes({
        IFC4X3_RC4_IfcBoundedCurve_type,IFC4X3_RC4_IfcConic_type,IFC4X3_RC4_IfcLine_type,IFC4X3_RC4_IfcOffsetCurve_type,IFC4X3_RC4_IfcPcurve_type,IFC4X3_RC4_IfcPolynomialCurve_type,IFC4X3_RC4_IfcSpiral_type,IFC4X3_RC4_IfcSurfaceCurve_type
    });
    IFC4X3_RC4_IfcSurface_type->set_subtypes({
        IFC4X3_RC4_IfcBoundedSurface_type,IFC4X3_RC4_IfcElementarySurface_type,IFC4X3_RC4_IfcSectionedSurface_type,IFC4X3_RC4_IfcSweptSurface_type
    });
    IFC4X3_RC4_IfcHalfSpaceSolid_type->set_subtypes({
        IFC4X3_RC4_IfcBoxedHalfSpace_type,IFC4X3_RC4_IfcPolygonalBoundedHalfSpace_type
    });
    IFC4X3_RC4_IfcFacility_type->set_subtypes({
        IFC4X3_RC4_IfcBridge_type,IFC4X3_RC4_IfcBuilding_type,IFC4X3_RC4_IfcMarineFacility_type,IFC4X3_RC4_IfcRailway_type,IFC4X3_RC4_IfcRoad_type
    });
    IFC4X3_RC4_IfcElementComponent_type->set_subtypes({
        IFC4X3_RC4_IfcBuildingElementPart_type,IFC4X3_RC4_IfcDiscreteAccessory_type,IFC4X3_RC4_IfcFastener_type,IFC4X3_RC4_IfcImpactProtectionDevice_type,IFC4X3_RC4_IfcMechanicalFastener_type,IFC4X3_RC4_IfcReinforcingElement_type,IFC4X3_RC4_IfcSign_type,IFC4X3_RC4_IfcVibrationDamper_type,IFC4X3_RC4_IfcVibrationIsolator_type
    });
    IFC4X3_RC4_IfcElementComponentType_type->set_subtypes({
        IFC4X3_RC4_IfcBuildingElementPartType_type,IFC4X3_RC4_IfcDiscreteAccessoryType_type,IFC4X3_RC4_IfcFastenerType_type,IFC4X3_RC4_IfcImpactProtectionDeviceType_type,IFC4X3_RC4_IfcMechanicalFastenerType_type,IFC4X3_RC4_IfcReinforcingElementType_type,IFC4X3_RC4_IfcSignType_type,IFC4X3_RC4_IfcVibrationDamperType_type,IFC4X3_RC4_IfcVibrationIsolatorType_type
    });
    IFC4X3_RC4_IfcSpatialStructureElement_type->set_subtypes({
        IFC4X3_RC4_IfcBuildingStorey_type,IFC4X3_RC4_IfcFacility_type,IFC4X3_RC4_IfcFacilityPart_type,IFC4X3_RC4_IfcSite_type,IFC4X3_RC4_IfcSpace_type
    });
    IFC4X3_RC4_IfcSystem_type->set_subtypes({
        IFC4X3_RC4_IfcBuildingSystem_type,IFC4X3_RC4_IfcBuiltSystem_type,IFC4X3_RC4_IfcDistributionSystem_type,IFC4X3_RC4_IfcStructuralAnalysisModel_type,IFC4X3_RC4_IfcZone_type
    });
    IFC4X3_RC4_IfcElement_type->set_subtypes({
        IFC4X3_RC4_IfcBuiltElement_type,IFC4X3_RC4_IfcCivilElement_type,IFC4X3_RC4_IfcDistributionElement_type,IFC4X3_RC4_IfcElementAssembly_type,IFC4X3_RC4_IfcElementComponent_type,IFC4X3_RC4_IfcFeatureElement_type,IFC4X3_RC4_IfcFurnishingElement_type,IFC4X3_RC4_IfcGeographicElement_type,IFC4X3_RC4_IfcGeotechnicalElement_type,IFC4X3_RC4_IfcTransportElement_type,IFC4X3_RC4_IfcVirtualElement_type
    });
    IFC4X3_RC4_IfcElementType_type->set_subtypes({
        IFC4X3_RC4_IfcBuiltElementType_type,IFC4X3_RC4_IfcCivilElementType_type,IFC4X3_RC4_IfcDistributionElementType_type,IFC4X3_RC4_IfcElementAssemblyType_type,IFC4X3_RC4_IfcElementComponentType_type,IFC4X3_RC4_IfcFurnishingElementType_type,IFC4X3_RC4_IfcGeographicElementType_type,IFC4X3_RC4_IfcTransportElementType_type
    });
    IFC4X3_RC4_IfcFlowFitting_type->set_subtypes({
        IFC4X3_RC4_IfcCableCarrierFitting_type,IFC4X3_RC4_IfcCableFitting_type,IFC4X3_RC4_IfcDuctFitting_type,IFC4X3_RC4_IfcJunctionBox_type,IFC4X3_RC4_IfcPipeFitting_type
    });
    IFC4X3_RC4_IfcFlowFittingType_type->set_subtypes({
        IFC4X3_RC4_IfcCableCarrierFittingType_type,IFC4X3_RC4_IfcCableFittingType_type,IFC4X3_RC4_IfcDuctFittingType_type,IFC4X3_RC4_IfcJunctionBoxType_type,IFC4X3_RC4_IfcPipeFittingType_type
    });
    IFC4X3_RC4_IfcFlowSegment_type->set_subtypes({
        IFC4X3_RC4_IfcCableCarrierSegment_type,IFC4X3_RC4_IfcCableSegment_type,IFC4X3_RC4_IfcConveyorSegment_type,IFC4X3_RC4_IfcDuctSegment_type,IFC4X3_RC4_IfcPipeSegment_type
    });
    IFC4X3_RC4_IfcFlowSegmentType_type->set_subtypes({
        IFC4X3_RC4_IfcCableCarrierSegmentType_type,IFC4X3_RC4_IfcCableSegmentType_type,IFC4X3_RC4_IfcConveyorSegmentType_type,IFC4X3_RC4_IfcDuctSegmentType_type,IFC4X3_RC4_IfcPipeSegmentType_type
    });
    IFC4X3_RC4_IfcDeepFoundation_type->set_subtypes({
        IFC4X3_RC4_IfcCaissonFoundation_type,IFC4X3_RC4_IfcPile_type
    });
    IFC4X3_RC4_IfcDeepFoundationType_type->set_subtypes({
        IFC4X3_RC4_IfcCaissonFoundationType_type,IFC4X3_RC4_IfcPileType_type
    });
    IFC4X3_RC4_IfcPoint_type->set_subtypes({
        IFC4X3_RC4_IfcCartesianPoint_type,IFC4X3_RC4_IfcPointByDistanceExpression_type,IFC4X3_RC4_IfcPointOnCurve_type,IFC4X3_RC4_IfcPointOnSurface_type
    });
    IFC4X3_RC4_IfcCartesianPointList_type->set_subtypes({
        IFC4X3_RC4_IfcCartesianPointList2D_type,IFC4X3_RC4_IfcCartesianPointList3D_type
    });
    IFC4X3_RC4_IfcCartesianTransformationOperator_type->set_subtypes({
        IFC4X3_RC4_IfcCartesianTransformationOperator2D_type,IFC4X3_RC4_IfcCartesianTransformationOperator3D_type
    });
    IFC4X3_RC4_IfcCartesianTransformationOperator2D_type->set_subtypes({
        IFC4X3_RC4_IfcCartesianTransformationOperator2DnonUniform_type
    });
    IFC4X3_RC4_IfcCartesianTransformationOperator3D_type->set_subtypes({
        IFC4X3_RC4_IfcCartesianTransformationOperator3DnonUniform_type
    });
    IFC4X3_RC4_IfcArbitraryOpenProfileDef_type->set_subtypes({
        IFC4X3_RC4_IfcCenterLineProfileDef_type
    });
    IFC4X3_RC4_IfcConic_type->set_subtypes({
        IFC4X3_RC4_IfcCircle_type,IFC4X3_RC4_IfcEllipse_type
    });
    IFC4X3_RC4_IfcCircleProfileDef_type->set_subtypes({
        IFC4X3_RC4_IfcCircleHollowProfileDef_type
    });
    IFC4X3_RC4_IfcExternalInformation_type->set_subtypes({
        IFC4X3_RC4_IfcClassification_type,IFC4X3_RC4_IfcDocumentInformation_type,IFC4X3_RC4_IfcLibraryInformation_type
    });
    IFC4X3_RC4_IfcExternalReference_type->set_subtypes({
        IFC4X3_RC4_IfcClassificationReference_type,IFC4X3_RC4_IfcDocumentReference_type,IFC4X3_RC4_IfcExternallyDefinedHatchStyle_type,IFC4X3_RC4_IfcExternallyDefinedSurfaceStyle_type,IFC4X3_RC4_IfcExternallyDefinedTextFont_type,IFC4X3_RC4_IfcLibraryReference_type
    });
    IFC4X3_RC4_IfcConnectedFaceSet_type->set_subtypes({
        IFC4X3_RC4_IfcClosedShell_type,IFC4X3_RC4_IfcOpenShell_type
    });
    IFC4X3_RC4_IfcSpiral_type->set_subtypes({
        IFC4X3_RC4_IfcClothoid_type,IFC4X3_RC4_IfcCosine_type,IFC4X3_RC4_IfcSecondOrderPolynomialSpiral_type,IFC4X3_RC4_IfcSeventhOrderPolynomialSpiral_type,IFC4X3_RC4_IfcSine_type,IFC4X3_RC4_IfcThirdOrderPolynomialSpiral_type
    });
    IFC4X3_RC4_IfcColourSpecification_type->set_subtypes({
        IFC4X3_RC4_IfcColourRgb_type
    });
    IFC4X3_RC4_IfcPresentationItem_type->set_subtypes({
        IFC4X3_RC4_IfcColourRgbList_type,IFC4X3_RC4_IfcColourSpecification_type,IFC4X3_RC4_IfcCurveStyleFont_type,IFC4X3_RC4_IfcCurveStyleFontAndScaling_type,IFC4X3_RC4_IfcCurveStyleFontPattern_type,IFC4X3_RC4_IfcIndexedColourMap_type,IFC4X3_RC4_IfcPreDefinedItem_type,IFC4X3_RC4_IfcSurfaceStyleLighting_type,IFC4X3_RC4_IfcSurfaceStyleRefraction_type,IFC4X3_RC4_IfcSurfaceStyleShading_type,IFC4X3_RC4_IfcSurfaceStyleWithTextures_type,IFC4X3_RC4_IfcSurfaceTexture_type,IFC4X3_RC4_IfcTextStyleForDefinedFont_type,IFC4X3_RC4_IfcTextStyleTextModel_type,IFC4X3_RC4_IfcTextureCoordinate_type,IFC4X3_RC4_IfcTextureVertex_type,IFC4X3_RC4_IfcTextureVertexList_type
    });
    IFC4X3_RC4_IfcColumn_type->set_subtypes({
        IFC4X3_RC4_IfcColumnStandardCase_type
    });
    IFC4X3_RC4_IfcProperty_type->set_subtypes({
        IFC4X3_RC4_IfcComplexProperty_type,IFC4X3_RC4_IfcSimpleProperty_type
    });
    IFC4X3_RC4_IfcPropertyTemplate_type->set_subtypes({
        IFC4X3_RC4_IfcComplexPropertyTemplate_type,IFC4X3_RC4_IfcSimplePropertyTemplate_type
    });
    IFC4X3_RC4_IfcCompositeCurve_type->set_subtypes({
        IFC4X3_RC4_IfcCompositeCurveOnSurface_type,IFC4X3_RC4_IfcGradientCurve_type,IFC4X3_RC4_IfcSegmentedReferenceCurve_type
    });
    IFC4X3_RC4_IfcSegment_type->set_subtypes({
        IFC4X3_RC4_IfcCompositeCurveSegment_type,IFC4X3_RC4_IfcCurveSegment_type
    });
    IFC4X3_RC4_IfcFlowMovingDevice_type->set_subtypes({
        IFC4X3_RC4_IfcCompressor_type,IFC4X3_RC4_IfcFan_type,IFC4X3_RC4_IfcPump_type
    });
    IFC4X3_RC4_IfcFlowMovingDeviceType_type->set_subtypes({
        IFC4X3_RC4_IfcCompressorType_type,IFC4X3_RC4_IfcFanType_type,IFC4X3_RC4_IfcPumpType_type
    });
    IFC4X3_RC4_IfcTopologicalRepresentationItem_type->set_subtypes({
        IFC4X3_RC4_IfcConnectedFaceSet_type,IFC4X3_RC4_IfcEdge_type,IFC4X3_RC4_IfcFace_type,IFC4X3_RC4_IfcFaceBound_type,IFC4X3_RC4_IfcLoop_type,IFC4X3_RC4_IfcPath_type,IFC4X3_RC4_IfcVertex_type
    });
    IFC4X3_RC4_IfcConnectionGeometry_type->set_subtypes({
        IFC4X3_RC4_IfcConnectionCurveGeometry_type,IFC4X3_RC4_IfcConnectionPointGeometry_type,IFC4X3_RC4_IfcConnectionSurfaceGeometry_type,IFC4X3_RC4_IfcConnectionVolumeGeometry_type
    });
    IFC4X3_RC4_IfcConnectionPointGeometry_type->set_subtypes({
        IFC4X3_RC4_IfcConnectionPointEccentricity_type
    });
    IFC4X3_RC4_IfcConstructionResource_type->set_subtypes({
        IFC4X3_RC4_IfcConstructionEquipmentResource_type,IFC4X3_RC4_IfcConstructionMaterialResource_type,IFC4X3_RC4_IfcConstructionProductResource_type,IFC4X3_RC4_IfcCrewResource_type,IFC4X3_RC4_IfcLaborResource_type,IFC4X3_RC4_IfcSubContractResource_type
    });
    IFC4X3_RC4_IfcConstructionResourceType_type->set_subtypes({
        IFC4X3_RC4_IfcConstructionEquipmentResourceType_type,IFC4X3_RC4_IfcConstructionMaterialResourceType_type,IFC4X3_RC4_IfcConstructionProductResourceType_type,IFC4X3_RC4_IfcCrewResourceType_type,IFC4X3_RC4_IfcLaborResourceType_type,IFC4X3_RC4_IfcSubContractResourceType_type
    });
    IFC4X3_RC4_IfcResource_type->set_subtypes({
        IFC4X3_RC4_IfcConstructionResource_type
    });
    IFC4X3_RC4_IfcTypeResource_type->set_subtypes({
        IFC4X3_RC4_IfcConstructionResourceType_type
    });
    IFC4X3_RC4_IfcObjectDefinition_type->set_subtypes({
        IFC4X3_RC4_IfcContext_type,IFC4X3_RC4_IfcObject_type,IFC4X3_RC4_IfcTypeObject_type
    });
    IFC4X3_RC4_IfcNamedUnit_type->set_subtypes({
        IFC4X3_RC4_IfcContextDependentUnit_type,IFC4X3_RC4_IfcConversionBasedUnit_type,IFC4X3_RC4_IfcSIUnit_type
    });
    IFC4X3_RC4_IfcConversionBasedUnit_type->set_subtypes({
        IFC4X3_RC4_IfcConversionBasedUnitWithOffset_type
    });
    IFC4X3_RC4_IfcAppliedValue_type->set_subtypes({
        IFC4X3_RC4_IfcCostValue_type
    });
    IFC4X3_RC4_IfcSolidModel_type->set_subtypes({
        IFC4X3_RC4_IfcCsgSolid_type,IFC4X3_RC4_IfcManifoldSolidBrep_type,IFC4X3_RC4_IfcSectionedSolid_type,IFC4X3_RC4_IfcSweptAreaSolid_type,IFC4X3_RC4_IfcSweptDiskSolid_type
    });
    IFC4X3_RC4_IfcPresentationStyle_type->set_subtypes({
        IFC4X3_RC4_IfcCurveStyle_type,IFC4X3_RC4_IfcFillAreaStyle_type,IFC4X3_RC4_IfcSurfaceStyle_type,IFC4X3_RC4_IfcTextStyle_type
    });
    IFC4X3_RC4_IfcElementarySurface_type->set_subtypes({
        IFC4X3_RC4_IfcCylindricalSurface_type,IFC4X3_RC4_IfcPlane_type,IFC4X3_RC4_IfcSphericalSurface_type,IFC4X3_RC4_IfcToroidalSurface_type
    });
    IFC4X3_RC4_IfcSweptAreaSolid_type->set_subtypes({
        IFC4X3_RC4_IfcDirectrixCurveSweptAreaSolid_type,IFC4X3_RC4_IfcExtrudedAreaSolid_type,IFC4X3_RC4_IfcRevolvedAreaSolid_type
    });
    IFC4X3_RC4_IfcFixedReferenceSweptAreaSolid_type->set_subtypes({
        IFC4X3_RC4_IfcDirectrixDerivedReferenceSweptAreaSolid_type
    });
    IFC4X3_RC4_IfcDistributionFlowElement_type->set_subtypes({
        IFC4X3_RC4_IfcDistributionChamberElement_type,IFC4X3_RC4_IfcEnergyConversionDevice_type,IFC4X3_RC4_IfcFlowController_type,IFC4X3_RC4_IfcFlowFitting_type,IFC4X3_RC4_IfcFlowMovingDevice_type,IFC4X3_RC4_IfcFlowSegment_type,IFC4X3_RC4_IfcFlowStorageDevice_type,IFC4X3_RC4_IfcFlowTerminal_type,IFC4X3_RC4_IfcFlowTreatmentDevice_type
    });
    IFC4X3_RC4_IfcDistributionFlowElementType_type->set_subtypes({
        IFC4X3_RC4_IfcDistributionChamberElementType_type,IFC4X3_RC4_IfcEnergyConversionDeviceType_type,IFC4X3_RC4_IfcFlowControllerType_type,IFC4X3_RC4_IfcFlowFittingType_type,IFC4X3_RC4_IfcFlowMovingDeviceType_type,IFC4X3_RC4_IfcFlowSegmentType_type,IFC4X3_RC4_IfcFlowStorageDeviceType_type,IFC4X3_RC4_IfcFlowTerminalType_type,IFC4X3_RC4_IfcFlowTreatmentDeviceType_type
    });
    IFC4X3_RC4_IfcDistributionSystem_type->set_subtypes({
        IFC4X3_RC4_IfcDistributionCircuit_type
    });
    IFC4X3_RC4_IfcDistributionElement_type->set_subtypes({
        IFC4X3_RC4_IfcDistributionControlElement_type,IFC4X3_RC4_IfcDistributionFlowElement_type
    });
    IFC4X3_RC4_IfcDistributionElementType_type->set_subtypes({
        IFC4X3_RC4_IfcDistributionControlElementType_type,IFC4X3_RC4_IfcDistributionFlowElementType_type
    });
    IFC4X3_RC4_IfcPort_type->set_subtypes({
        IFC4X3_RC4_IfcDistributionPort_type
    });
    IFC4X3_RC4_IfcPreDefinedPropertySet_type->set_subtypes({
        IFC4X3_RC4_IfcDoorLiningProperties_type,IFC4X3_RC4_IfcDoorPanelProperties_type,IFC4X3_RC4_IfcPermeableCoveringProperties_type,IFC4X3_RC4_IfcReinforcementDefinitionProperties_type,IFC4X3_RC4_IfcWindowLiningProperties_type,IFC4X3_RC4_IfcWindowPanelProperties_type
    });
    IFC4X3_RC4_IfcDoor_type->set_subtypes({
        IFC4X3_RC4_IfcDoorStandardCase_type
    });
    IFC4X3_RC4_IfcTypeProduct_type->set_subtypes({
        IFC4X3_RC4_IfcDoorStyle_type,IFC4X3_RC4_IfcElementType_type,IFC4X3_RC4_IfcSpatialElementType_type,IFC4X3_RC4_IfcWindowStyle_type
    });
    IFC4X3_RC4_IfcPreDefinedColour_type->set_subtypes({
        IFC4X3_RC4_IfcDraughtingPreDefinedColour_type
    });
    IFC4X3_RC4_IfcPreDefinedCurveFont_type->set_subtypes({
        IFC4X3_RC4_IfcDraughtingPreDefinedCurveFont_type
    });
    IFC4X3_RC4_IfcFlowTreatmentDevice_type->set_subtypes({
        IFC4X3_RC4_IfcDuctSilencer_type,IFC4X3_RC4_IfcElectricFlowTreatmentDevice_type,IFC4X3_RC4_IfcFilter_type,IFC4X3_RC4_IfcInterceptor_type
    });
    IFC4X3_RC4_IfcFlowTreatmentDeviceType_type->set_subtypes({
        IFC4X3_RC4_IfcDuctSilencerType_type,IFC4X3_RC4_IfcElectricFlowTreatmentDeviceType_type,IFC4X3_RC4_IfcFilterType_type,IFC4X3_RC4_IfcInterceptorType_type
    });
    IFC4X3_RC4_IfcFeatureElementSubtraction_type->set_subtypes({
        IFC4X3_RC4_IfcEarthworksCut_type,IFC4X3_RC4_IfcOpeningElement_type,IFC4X3_RC4_IfcVoidingFeature_type
    });
    IFC4X3_RC4_IfcEarthworksElement_type->set_subtypes({
        IFC4X3_RC4_IfcEarthworksFill_type,IFC4X3_RC4_IfcReinforcedSoil_type
    });
    IFC4X3_RC4_IfcEdge_type->set_subtypes({
        IFC4X3_RC4_IfcEdgeCurve_type,IFC4X3_RC4_IfcOrientedEdge_type,IFC4X3_RC4_IfcSubedge_type
    });
    IFC4X3_RC4_IfcLoop_type->set_subtypes({
        IFC4X3_RC4_IfcEdgeLoop_type,IFC4X3_RC4_IfcPolyLoop_type,IFC4X3_RC4_IfcVertexLoop_type
    });
    IFC4X3_RC4_IfcFlowStorageDevice_type->set_subtypes({
        IFC4X3_RC4_IfcElectricFlowStorageDevice_type,IFC4X3_RC4_IfcTank_type
    });
    IFC4X3_RC4_IfcFlowStorageDeviceType_type->set_subtypes({
        IFC4X3_RC4_IfcElectricFlowStorageDeviceType_type,IFC4X3_RC4_IfcTankType_type
    });
    IFC4X3_RC4_IfcQuantitySet_type->set_subtypes({
        IFC4X3_RC4_IfcElementQuantity_type
    });
    IFC4X3_RC4_IfcProcess_type->set_subtypes({
        IFC4X3_RC4_IfcEvent_type,IFC4X3_RC4_IfcProcedure_type,IFC4X3_RC4_IfcTask_type
    });
    IFC4X3_RC4_IfcSchedulingTime_type->set_subtypes({
        IFC4X3_RC4_IfcEventTime_type,IFC4X3_RC4_IfcLagTime_type,IFC4X3_RC4_IfcResourceTime_type,IFC4X3_RC4_IfcTaskTime_type,IFC4X3_RC4_IfcWorkTime_type
    });
    IFC4X3_RC4_IfcTypeProcess_type->set_subtypes({
        IFC4X3_RC4_IfcEventType_type,IFC4X3_RC4_IfcProcedureType_type,IFC4X3_RC4_IfcTaskType_type
    });
    IFC4X3_RC4_IfcPropertyAbstraction_type->set_subtypes({
        IFC4X3_RC4_IfcExtendedProperties_type,IFC4X3_RC4_IfcPreDefinedProperties_type,IFC4X3_RC4_IfcProperty_type,IFC4X3_RC4_IfcPropertyEnumeration_type
    });
    IFC4X3_RC4_IfcExternalSpatialStructureElement_type->set_subtypes({
        IFC4X3_RC4_IfcExternalSpatialElement_type
    });
    IFC4X3_RC4_IfcSpatialElement_type->set_subtypes({
        IFC4X3_RC4_IfcExternalSpatialStructureElement_type,IFC4X3_RC4_IfcSpatialStructureElement_type,IFC4X3_RC4_IfcSpatialZone_type
    });
    IFC4X3_RC4_IfcExtrudedAreaSolid_type->set_subtypes({
        IFC4X3_RC4_IfcExtrudedAreaSolidTapered_type
    });
    IFC4X3_RC4_IfcFaceBound_type->set_subtypes({
        IFC4X3_RC4_IfcFaceOuterBound_type
    });
    IFC4X3_RC4_IfcFace_type->set_subtypes({
        IFC4X3_RC4_IfcFaceSurface_type
    });
    IFC4X3_RC4_IfcFacetedBrep_type->set_subtypes({
        IFC4X3_RC4_IfcFacetedBrepWithVoids_type
    });
    IFC4X3_RC4_IfcStructuralConnectionCondition_type->set_subtypes({
        IFC4X3_RC4_IfcFailureConnectionCondition_type,IFC4X3_RC4_IfcSlippageConnectionCondition_type
    });
    IFC4X3_RC4_IfcFeatureElement_type->set_subtypes({
        IFC4X3_RC4_IfcFeatureElementAddition_type,IFC4X3_RC4_IfcFeatureElementSubtraction_type,IFC4X3_RC4_IfcSurfaceFeature_type
    });
    IFC4X3_RC4_IfcDirectrixCurveSweptAreaSolid_type->set_subtypes({
        IFC4X3_RC4_IfcFixedReferenceSweptAreaSolid_type,IFC4X3_RC4_IfcSurfaceCurveSweptAreaSolid_type
    });
    IFC4X3_RC4_IfcFurnishingElement_type->set_subtypes({
        IFC4X3_RC4_IfcFurniture_type,IFC4X3_RC4_IfcSystemFurnitureElement_type
    });
    IFC4X3_RC4_IfcFurnishingElementType_type->set_subtypes({
        IFC4X3_RC4_IfcFurnitureType_type,IFC4X3_RC4_IfcSystemFurnitureElementType_type
    });
    IFC4X3_RC4_IfcGeometricSet_type->set_subtypes({
        IFC4X3_RC4_IfcGeometricCurveSet_type
    });
    IFC4X3_RC4_IfcRepresentationContext_type->set_subtypes({
        IFC4X3_RC4_IfcGeometricRepresentationContext_type
    });
    IFC4X3_RC4_IfcRepresentationItem_type->set_subtypes({
        IFC4X3_RC4_IfcGeometricRepresentationItem_type,IFC4X3_RC4_IfcMappedItem_type,IFC4X3_RC4_IfcStyledItem_type,IFC4X3_RC4_IfcTopologicalRepresentationItem_type
    });
    IFC4X3_RC4_IfcGeometricRepresentationContext_type->set_subtypes({
        IFC4X3_RC4_IfcGeometricRepresentationSubContext_type
    });
    IFC4X3_RC4_IfcGeotechnicalElement_type->set_subtypes({
        IFC4X3_RC4_IfcGeotechnicalAssembly_type,IFC4X3_RC4_IfcGeotechnicalStratum_type
    });
    IFC4X3_RC4_IfcPositioningElement_type->set_subtypes({
        IFC4X3_RC4_IfcGrid_type,IFC4X3_RC4_IfcLinearPositioningElement_type,IFC4X3_RC4_IfcReferent_type
    });
    IFC4X3_RC4_IfcObjectPlacement_type->set_subtypes({
        IFC4X3_RC4_IfcGridPlacement_type,IFC4X3_RC4_IfcLinearPlacement_type,IFC4X3_RC4_IfcLocalPlacement_type
    });
    IFC4X3_RC4_IfcTessellatedItem_type->set_subtypes({
        IFC4X3_RC4_IfcIndexedPolygonalFace_type,IFC4X3_RC4_IfcTessellatedFaceSet_type
    });
    IFC4X3_RC4_IfcIndexedPolygonalFace_type->set_subtypes({
        IFC4X3_RC4_IfcIndexedPolygonalFaceWithVoids_type
    });
    IFC4X3_RC4_IfcTextureCoordinate_type->set_subtypes({
        IFC4X3_RC4_IfcIndexedTextureMap_type,IFC4X3_RC4_IfcTextureCoordinateGenerator_type,IFC4X3_RC4_IfcTextureMap_type
    });
    IFC4X3_RC4_IfcIndexedTextureMap_type->set_subtypes({
        IFC4X3_RC4_IfcIndexedTriangleTextureMap_type
    });
    IFC4X3_RC4_IfcSurfaceCurve_type->set_subtypes({
        IFC4X3_RC4_IfcIntersectionCurve_type,IFC4X3_RC4_IfcSeamCurve_type
    });
    IFC4X3_RC4_IfcTimeSeries_type->set_subtypes({
        IFC4X3_RC4_IfcIrregularTimeSeries_type,IFC4X3_RC4_IfcRegularTimeSeries_type
    });
    IFC4X3_RC4_IfcLightSource_type->set_subtypes({
        IFC4X3_RC4_IfcLightSourceAmbient_type,IFC4X3_RC4_IfcLightSourceDirectional_type,IFC4X3_RC4_IfcLightSourceGoniometric_type,IFC4X3_RC4_IfcLightSourcePositional_type
    });
    IFC4X3_RC4_IfcLightSourcePositional_type->set_subtypes({
        IFC4X3_RC4_IfcLightSourceSpot_type
    });
    IFC4X3_RC4_IfcCoordinateOperation_type->set_subtypes({
        IFC4X3_RC4_IfcMapConversion_type
    });
    IFC4X3_RC4_IfcMaterialDefinition_type->set_subtypes({
        IFC4X3_RC4_IfcMaterial_type,IFC4X3_RC4_IfcMaterialConstituent_type,IFC4X3_RC4_IfcMaterialConstituentSet_type,IFC4X3_RC4_IfcMaterialLayer_type,IFC4X3_RC4_IfcMaterialLayerSet_type,IFC4X3_RC4_IfcMaterialProfile_type,IFC4X3_RC4_IfcMaterialProfileSet_type
    });
    IFC4X3_RC4_IfcProductRepresentation_type->set_subtypes({
        IFC4X3_RC4_IfcMaterialDefinitionRepresentation_type,IFC4X3_RC4_IfcProductDefinitionShape_type
    });
    IFC4X3_RC4_IfcMaterialUsageDefinition_type->set_subtypes({
        IFC4X3_RC4_IfcMaterialLayerSetUsage_type,IFC4X3_RC4_IfcMaterialProfileSetUsage_type
    });
    IFC4X3_RC4_IfcMaterialLayer_type->set_subtypes({
        IFC4X3_RC4_IfcMaterialLayerWithOffsets_type
    });
    IFC4X3_RC4_IfcMaterialProfileSetUsage_type->set_subtypes({
        IFC4X3_RC4_IfcMaterialProfileSetUsageTapering_type
    });
    IFC4X3_RC4_IfcMaterialProfile_type->set_subtypes({
        IFC4X3_RC4_IfcMaterialProfileWithOffsets_type
    });
    IFC4X3_RC4_IfcExtendedProperties_type->set_subtypes({
        IFC4X3_RC4_IfcMaterialProperties_type,IFC4X3_RC4_IfcProfileProperties_type
    });
    IFC4X3_RC4_IfcMember_type->set_subtypes({
        IFC4X3_RC4_IfcMemberStandardCase_type
    });
    IFC4X3_RC4_IfcConstraint_type->set_subtypes({
        IFC4X3_RC4_IfcMetric_type,IFC4X3_RC4_IfcObjective_type
    });
    IFC4X3_RC4_IfcDerivedProfileDef_type->set_subtypes({
        IFC4X3_RC4_IfcMirroredProfileDef_type
    });
    IFC4X3_RC4_IfcRoot_type->set_subtypes({
        IFC4X3_RC4_IfcObjectDefinition_type,IFC4X3_RC4_IfcPropertyDefinition_type,IFC4X3_RC4_IfcRelationship_type
    });
    IFC4X3_RC4_IfcActor_type->set_subtypes({
        IFC4X3_RC4_IfcOccupant_type
    });
    IFC4X3_RC4_IfcOffsetCurve_type->set_subtypes({
        IFC4X3_RC4_IfcOffsetCurve2D_type,IFC4X3_RC4_IfcOffsetCurve3D_type,IFC4X3_RC4_IfcOffsetCurveByDistances_type
    });
    IFC4X3_RC4_IfcOpeningElement_type->set_subtypes({
        IFC4X3_RC4_IfcOpeningStandardCase_type
    });
    IFC4X3_RC4_IfcBoundaryCurve_type->set_subtypes({
        IFC4X3_RC4_IfcOuterBoundaryCurve_type
    });
    IFC4X3_RC4_IfcPhysicalQuantity_type->set_subtypes({
        IFC4X3_RC4_IfcPhysicalComplexQuantity_type,IFC4X3_RC4_IfcPhysicalSimpleQuantity_type
    });
    IFC4X3_RC4_IfcPlanarExtent_type->set_subtypes({
        IFC4X3_RC4_IfcPlanarBox_type
    });
    IFC4X3_RC4_IfcGeographicElement_type->set_subtypes({
        IFC4X3_RC4_IfcPlant_type
    });
    IFC4X3_RC4_IfcPlate_type->set_subtypes({
        IFC4X3_RC4_IfcPlateStandardCase_type
    });
    IFC4X3_RC4_IfcTessellatedFaceSet_type->set_subtypes({
        IFC4X3_RC4_IfcPolygonalFaceSet_type,IFC4X3_RC4_IfcTriangulatedFaceSet_type
    });
    IFC4X3_RC4_IfcAddress_type->set_subtypes({
        IFC4X3_RC4_IfcPostalAddress_type,IFC4X3_RC4_IfcTelecomAddress_type
    });
    IFC4X3_RC4_IfcPreDefinedItem_type->set_subtypes({
        IFC4X3_RC4_IfcPreDefinedColour_type,IFC4X3_RC4_IfcPreDefinedCurveFont_type,IFC4X3_RC4_IfcPreDefinedTextFont_type
    });
    IFC4X3_RC4_IfcPropertySetDefinition_type->set_subtypes({
        IFC4X3_RC4_IfcPreDefinedPropertySet_type,IFC4X3_RC4_IfcPropertySet_type,IFC4X3_RC4_IfcQuantitySet_type
    });
    IFC4X3_RC4_IfcPresentationLayerAssignment_type->set_subtypes({
        IFC4X3_RC4_IfcPresentationLayerWithStyle_type
    });
    IFC4X3_RC4_IfcContext_type->set_subtypes({
        IFC4X3_RC4_IfcProject_type,IFC4X3_RC4_IfcProjectLibrary_type
    });
    IFC4X3_RC4_IfcCoordinateReferenceSystem_type->set_subtypes({
        IFC4X3_RC4_IfcProjectedCRS_type
    });
    IFC4X3_RC4_IfcFeatureElementAddition_type->set_subtypes({
        IFC4X3_RC4_IfcProjectionElement_type
    });
    IFC4X3_RC4_IfcSimpleProperty_type->set_subtypes({
        IFC4X3_RC4_IfcPropertyBoundedValue_type,IFC4X3_RC4_IfcPropertyEnumeratedValue_type,IFC4X3_RC4_IfcPropertyListValue_type,IFC4X3_RC4_IfcPropertyReferenceValue_type,IFC4X3_RC4_IfcPropertySingleValue_type,IFC4X3_RC4_IfcPropertyTableValue_type
    });
    IFC4X3_RC4_IfcPropertyDefinition_type->set_subtypes({
        IFC4X3_RC4_IfcPropertySetDefinition_type,IFC4X3_RC4_IfcPropertyTemplateDefinition_type
    });
    IFC4X3_RC4_IfcPropertyTemplateDefinition_type->set_subtypes({
        IFC4X3_RC4_IfcPropertySetTemplate_type,IFC4X3_RC4_IfcPropertyTemplate_type
    });
    IFC4X3_RC4_IfcPhysicalSimpleQuantity_type->set_subtypes({
        IFC4X3_RC4_IfcQuantityArea_type,IFC4X3_RC4_IfcQuantityCount_type,IFC4X3_RC4_IfcQuantityLength_type,IFC4X3_RC4_IfcQuantityTime_type,IFC4X3_RC4_IfcQuantityVolume_type,IFC4X3_RC4_IfcQuantityWeight_type
    });
    IFC4X3_RC4_IfcBSplineCurveWithKnots_type->set_subtypes({
        IFC4X3_RC4_IfcRationalBSplineCurveWithKnots_type
    });
    IFC4X3_RC4_IfcBSplineSurfaceWithKnots_type->set_subtypes({
        IFC4X3_RC4_IfcRationalBSplineSurfaceWithKnots_type
    });
    IFC4X3_RC4_IfcRectangleProfileDef_type->set_subtypes({
        IFC4X3_RC4_IfcRectangleHollowProfileDef_type,IFC4X3_RC4_IfcRoundedRectangleProfileDef_type
    });
    IFC4X3_RC4_IfcPreDefinedProperties_type->set_subtypes({
        IFC4X3_RC4_IfcReinforcementBarProperties_type,IFC4X3_RC4_IfcSectionProperties_type,IFC4X3_RC4_IfcSectionReinforcementProperties_type
    });
    IFC4X3_RC4_IfcReinforcingElement_type->set_subtypes({
        IFC4X3_RC4_IfcReinforcingBar_type,IFC4X3_RC4_IfcReinforcingMesh_type,IFC4X3_RC4_IfcTendon_type,IFC4X3_RC4_IfcTendonAnchor_type,IFC4X3_RC4_IfcTendonConduit_type
    });
    IFC4X3_RC4_IfcReinforcingElementType_type->set_subtypes({
        IFC4X3_RC4_IfcReinforcingBarType_type,IFC4X3_RC4_IfcReinforcingMeshType_type,IFC4X3_RC4_IfcTendonAnchorType_type,IFC4X3_RC4_IfcTendonConduitType_type,IFC4X3_RC4_IfcTendonType_type
    });
    IFC4X3_RC4_IfcRelDecomposes_type->set_subtypes({
        IFC4X3_RC4_IfcRelAdheresToElement_type,IFC4X3_RC4_IfcRelAggregates_type,IFC4X3_RC4_IfcRelNests_type,IFC4X3_RC4_IfcRelProjectsElement_type,IFC4X3_RC4_IfcRelVoidsElement_type
    });
    IFC4X3_RC4_IfcRelationship_type->set_subtypes({
        IFC4X3_RC4_IfcRelAssigns_type,IFC4X3_RC4_IfcRelAssociates_type,IFC4X3_RC4_IfcRelConnects_type,IFC4X3_RC4_IfcRelDeclares_type,IFC4X3_RC4_IfcRelDecomposes_type,IFC4X3_RC4_IfcRelDefines_type
    });
    IFC4X3_RC4_IfcRelAssigns_type->set_subtypes({
        IFC4X3_RC4_IfcRelAssignsToActor_type,IFC4X3_RC4_IfcRelAssignsToControl_type,IFC4X3_RC4_IfcRelAssignsToGroup_type,IFC4X3_RC4_IfcRelAssignsToProcess_type,IFC4X3_RC4_IfcRelAssignsToProduct_type,IFC4X3_RC4_IfcRelAssignsToResource_type
    });
    IFC4X3_RC4_IfcRelAssignsToGroup_type->set_subtypes({
        IFC4X3_RC4_IfcRelAssignsToGroupByFactor_type
    });
    IFC4X3_RC4_IfcRelAssociates_type->set_subtypes({
        IFC4X3_RC4_IfcRelAssociatesApproval_type,IFC4X3_RC4_IfcRelAssociatesClassification_type,IFC4X3_RC4_IfcRelAssociatesConstraint_type,IFC4X3_RC4_IfcRelAssociatesDocument_type,IFC4X3_RC4_IfcRelAssociatesLibrary_type,IFC4X3_RC4_IfcRelAssociatesMaterial_type,IFC4X3_RC4_IfcRelAssociatesProfileDef_type
    });
    IFC4X3_RC4_IfcRelConnects_type->set_subtypes({
        IFC4X3_RC4_IfcRelConnectsElements_type,IFC4X3_RC4_IfcRelConnectsPortToElement_type,IFC4X3_RC4_IfcRelConnectsPorts_type,IFC4X3_RC4_IfcRelConnectsStructuralActivity_type,IFC4X3_RC4_IfcRelConnectsStructuralMember_type,IFC4X3_RC4_IfcRelContainedInSpatialStructure_type,IFC4X3_RC4_IfcRelCoversBldgElements_type,IFC4X3_RC4_IfcRelCoversSpaces_type,IFC4X3_RC4_IfcRelFillsElement_type,IFC4X3_RC4_IfcRelFlowControlElements_type,IFC4X3_RC4_IfcRelInterferesElements_type,IFC4X3_RC4_IfcRelPositions_type,IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type,IFC4X3_RC4_IfcRelSequence_type,IFC4X3_RC4_IfcRelServicesBuildings_type,IFC4X3_RC4_IfcRelSpaceBoundary_type
    });
    IFC4X3_RC4_IfcRelConnectsElements_type->set_subtypes({
        IFC4X3_RC4_IfcRelConnectsPathElements_type,IFC4X3_RC4_IfcRelConnectsWithRealizingElements_type
    });
    IFC4X3_RC4_IfcRelConnectsStructuralMember_type->set_subtypes({
        IFC4X3_RC4_IfcRelConnectsWithEccentricity_type
    });
    IFC4X3_RC4_IfcRelDefines_type->set_subtypes({
        IFC4X3_RC4_IfcRelDefinesByObject_type,IFC4X3_RC4_IfcRelDefinesByProperties_type,IFC4X3_RC4_IfcRelDefinesByTemplate_type,IFC4X3_RC4_IfcRelDefinesByType_type
    });
    IFC4X3_RC4_IfcRelSpaceBoundary_type->set_subtypes({
        IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type
    });
    IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type->set_subtypes({
        IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type
    });
    IFC4X3_RC4_IfcCompositeCurveSegment_type->set_subtypes({
        IFC4X3_RC4_IfcReparametrisedCompositeCurveSegment_type
    });
    IFC4X3_RC4_IfcRevolvedAreaSolid_type->set_subtypes({
        IFC4X3_RC4_IfcRevolvedAreaSolidTapered_type
    });
    IFC4X3_RC4_IfcSectionedSolid_type->set_subtypes({
        IFC4X3_RC4_IfcSectionedSolidHorizontal_type
    });
    IFC4X3_RC4_IfcRepresentation_type->set_subtypes({
        IFC4X3_RC4_IfcShapeModel_type,IFC4X3_RC4_IfcStyleModel_type
    });
    IFC4X3_RC4_IfcShapeModel_type->set_subtypes({
        IFC4X3_RC4_IfcShapeRepresentation_type,IFC4X3_RC4_IfcTopologyRepresentation_type
    });
    IFC4X3_RC4_IfcSlab_type->set_subtypes({
        IFC4X3_RC4_IfcSlabElementedCase_type,IFC4X3_RC4_IfcSlabStandardCase_type
    });
    IFC4X3_RC4_IfcGeotechnicalStratum_type->set_subtypes({
        IFC4X3_RC4_IfcSolidStratum_type,IFC4X3_RC4_IfcVoidStratum_type,IFC4X3_RC4_IfcWaterStratum_type
    });
    IFC4X3_RC4_IfcSpatialStructureElementType_type->set_subtypes({
        IFC4X3_RC4_IfcSpaceType_type
    });
    IFC4X3_RC4_IfcSpatialElementType_type->set_subtypes({
        IFC4X3_RC4_IfcSpatialStructureElementType_type,IFC4X3_RC4_IfcSpatialZoneType_type
    });
    IFC4X3_RC4_IfcStructuralActivity_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralAction_type,IFC4X3_RC4_IfcStructuralReaction_type
    });
    IFC4X3_RC4_IfcStructuralItem_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralConnection_type,IFC4X3_RC4_IfcStructuralMember_type
    });
    IFC4X3_RC4_IfcStructuralAction_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralCurveAction_type,IFC4X3_RC4_IfcStructuralPointAction_type,IFC4X3_RC4_IfcStructuralSurfaceAction_type
    });
    IFC4X3_RC4_IfcStructuralConnection_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralCurveConnection_type,IFC4X3_RC4_IfcStructuralPointConnection_type,IFC4X3_RC4_IfcStructuralSurfaceConnection_type
    });
    IFC4X3_RC4_IfcStructuralMember_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralCurveMember_type,IFC4X3_RC4_IfcStructuralSurfaceMember_type
    });
    IFC4X3_RC4_IfcStructuralCurveMember_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralCurveMemberVarying_type
    });
    IFC4X3_RC4_IfcStructuralReaction_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralCurveReaction_type,IFC4X3_RC4_IfcStructuralPointReaction_type,IFC4X3_RC4_IfcStructuralSurfaceReaction_type
    });
    IFC4X3_RC4_IfcStructuralCurveAction_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralLinearAction_type
    });
    IFC4X3_RC4_IfcStructuralLoadGroup_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralLoadCase_type
    });
    IFC4X3_RC4_IfcStructuralLoad_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralLoadConfiguration_type,IFC4X3_RC4_IfcStructuralLoadOrResult_type
    });
    IFC4X3_RC4_IfcStructuralLoadStatic_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralLoadLinearForce_type,IFC4X3_RC4_IfcStructuralLoadPlanarForce_type,IFC4X3_RC4_IfcStructuralLoadSingleDisplacement_type,IFC4X3_RC4_IfcStructuralLoadSingleForce_type,IFC4X3_RC4_IfcStructuralLoadTemperature_type
    });
    IFC4X3_RC4_IfcStructuralLoadSingleDisplacement_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralLoadSingleDisplacementDistortion_type
    });
    IFC4X3_RC4_IfcStructuralLoadSingleForce_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralLoadSingleForceWarping_type
    });
    IFC4X3_RC4_IfcStructuralLoadOrResult_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralLoadStatic_type,IFC4X3_RC4_IfcSurfaceReinforcementArea_type
    });
    IFC4X3_RC4_IfcStructuralSurfaceAction_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralPlanarAction_type
    });
    IFC4X3_RC4_IfcStructuralSurfaceMember_type->set_subtypes({
        IFC4X3_RC4_IfcStructuralSurfaceMemberVarying_type
    });
    IFC4X3_RC4_IfcStyleModel_type->set_subtypes({
        IFC4X3_RC4_IfcStyledRepresentation_type
    });
    IFC4X3_RC4_IfcSweptSurface_type->set_subtypes({
        IFC4X3_RC4_IfcSurfaceOfLinearExtrusion_type,IFC4X3_RC4_IfcSurfaceOfRevolution_type
    });
    IFC4X3_RC4_IfcSurfaceStyleShading_type->set_subtypes({
        IFC4X3_RC4_IfcSurfaceStyleRendering_type
    });
    IFC4X3_RC4_IfcSweptDiskSolid_type->set_subtypes({
        IFC4X3_RC4_IfcSweptDiskSolidPolygonal_type
    });
    IFC4X3_RC4_IfcTaskTime_type->set_subtypes({
        IFC4X3_RC4_IfcTaskTimeRecurring_type
    });
    IFC4X3_RC4_IfcTextLiteral_type->set_subtypes({
        IFC4X3_RC4_IfcTextLiteralWithExtent_type
    });
    IFC4X3_RC4_IfcPreDefinedTextFont_type->set_subtypes({
        IFC4X3_RC4_IfcTextStyleFontModel_type
    });
    IFC4X3_RC4_IfcTriangulatedFaceSet_type->set_subtypes({
        IFC4X3_RC4_IfcTriangulatedIrregularNetwork_type
    });
    IFC4X3_RC4_IfcTypeObject_type->set_subtypes({
        IFC4X3_RC4_IfcTypeProcess_type,IFC4X3_RC4_IfcTypeProduct_type,IFC4X3_RC4_IfcTypeResource_type
    });
    IFC4X3_RC4_IfcVertex_type->set_subtypes({
        IFC4X3_RC4_IfcVertexPoint_type
    });
    IFC4X3_RC4_IfcWall_type->set_subtypes({
        IFC4X3_RC4_IfcWallElementedCase_type,IFC4X3_RC4_IfcWallStandardCase_type
    });
    IFC4X3_RC4_IfcWindow_type->set_subtypes({
        IFC4X3_RC4_IfcWindowStandardCase_type
    });
    IFC4X3_RC4_IfcWorkControl_type->set_subtypes({
        IFC4X3_RC4_IfcWorkPlan_type,IFC4X3_RC4_IfcWorkSchedule_type
    });

    std::vector<const declaration*> declarations= {
    IFC4X3_RC4_IfcAbsorbedDoseMeasure_type,
    IFC4X3_RC4_IfcAccelerationMeasure_type,
    IFC4X3_RC4_IfcActionRequest_type,
    IFC4X3_RC4_IfcActionRequestTypeEnum_type,
    IFC4X3_RC4_IfcActionSourceTypeEnum_type,
    IFC4X3_RC4_IfcActionTypeEnum_type,
    IFC4X3_RC4_IfcActor_type,
    IFC4X3_RC4_IfcActorRole_type,
    IFC4X3_RC4_IfcActorSelect_type,
    IFC4X3_RC4_IfcActuator_type,
    IFC4X3_RC4_IfcActuatorType_type,
    IFC4X3_RC4_IfcActuatorTypeEnum_type,
    IFC4X3_RC4_IfcAddress_type,
    IFC4X3_RC4_IfcAddressTypeEnum_type,
    IFC4X3_RC4_IfcAdvancedBrep_type,
    IFC4X3_RC4_IfcAdvancedBrepWithVoids_type,
    IFC4X3_RC4_IfcAdvancedFace_type,
    IFC4X3_RC4_IfcAirTerminal_type,
    IFC4X3_RC4_IfcAirTerminalBox_type,
    IFC4X3_RC4_IfcAirTerminalBoxType_type,
    IFC4X3_RC4_IfcAirTerminalBoxTypeEnum_type,
    IFC4X3_RC4_IfcAirTerminalType_type,
    IFC4X3_RC4_IfcAirTerminalTypeEnum_type,
    IFC4X3_RC4_IfcAirToAirHeatRecovery_type,
    IFC4X3_RC4_IfcAirToAirHeatRecoveryType_type,
    IFC4X3_RC4_IfcAirToAirHeatRecoveryTypeEnum_type,
    IFC4X3_RC4_IfcAlarm_type,
    IFC4X3_RC4_IfcAlarmType_type,
    IFC4X3_RC4_IfcAlarmTypeEnum_type,
    IFC4X3_RC4_IfcAlignment_type,
    IFC4X3_RC4_IfcAlignmentCant_type,
    IFC4X3_RC4_IfcAlignmentCantSegment_type,
    IFC4X3_RC4_IfcAlignmentCantSegmentTypeEnum_type,
    IFC4X3_RC4_IfcAlignmentHorizontal_type,
    IFC4X3_RC4_IfcAlignmentHorizontalSegment_type,
    IFC4X3_RC4_IfcAlignmentHorizontalSegmentTypeEnum_type,
    IFC4X3_RC4_IfcAlignmentParameterSegment_type,
    IFC4X3_RC4_IfcAlignmentSegment_type,
    IFC4X3_RC4_IfcAlignmentTypeEnum_type,
    IFC4X3_RC4_IfcAlignmentVertical_type,
    IFC4X3_RC4_IfcAlignmentVerticalSegment_type,
    IFC4X3_RC4_IfcAlignmentVerticalSegmentTypeEnum_type,
    IFC4X3_RC4_IfcAmountOfSubstanceMeasure_type,
    IFC4X3_RC4_IfcAnalysisModelTypeEnum_type,
    IFC4X3_RC4_IfcAnalysisTheoryTypeEnum_type,
    IFC4X3_RC4_IfcAngularVelocityMeasure_type,
    IFC4X3_RC4_IfcAnnotation_type,
    IFC4X3_RC4_IfcAnnotationFillArea_type,
    IFC4X3_RC4_IfcAnnotationTypeEnum_type,
    IFC4X3_RC4_IfcApplication_type,
    IFC4X3_RC4_IfcAppliedValue_type,
    IFC4X3_RC4_IfcAppliedValueSelect_type,
    IFC4X3_RC4_IfcApproval_type,
    IFC4X3_RC4_IfcApprovalRelationship_type,
    IFC4X3_RC4_IfcArbitraryClosedProfileDef_type,
    IFC4X3_RC4_IfcArbitraryOpenProfileDef_type,
    IFC4X3_RC4_IfcArbitraryProfileDefWithVoids_type,
    IFC4X3_RC4_IfcArcIndex_type,
    IFC4X3_RC4_IfcAreaDensityMeasure_type,
    IFC4X3_RC4_IfcAreaMeasure_type,
    IFC4X3_RC4_IfcArithmeticOperatorEnum_type,
    IFC4X3_RC4_IfcAssemblyPlaceEnum_type,
    IFC4X3_RC4_IfcAsset_type,
    IFC4X3_RC4_IfcAsymmetricIShapeProfileDef_type,
    IFC4X3_RC4_IfcAudioVisualAppliance_type,
    IFC4X3_RC4_IfcAudioVisualApplianceType_type,
    IFC4X3_RC4_IfcAudioVisualApplianceTypeEnum_type,
    IFC4X3_RC4_IfcAxis1Placement_type,
    IFC4X3_RC4_IfcAxis2Placement_type,
    IFC4X3_RC4_IfcAxis2Placement2D_type,
    IFC4X3_RC4_IfcAxis2Placement3D_type,
    IFC4X3_RC4_IfcAxis2PlacementLinear_type,
    IFC4X3_RC4_IfcBeam_type,
    IFC4X3_RC4_IfcBeamStandardCase_type,
    IFC4X3_RC4_IfcBeamType_type,
    IFC4X3_RC4_IfcBeamTypeEnum_type,
    IFC4X3_RC4_IfcBearing_type,
    IFC4X3_RC4_IfcBearingType_type,
    IFC4X3_RC4_IfcBearingTypeDisplacementEnum_type,
    IFC4X3_RC4_IfcBearingTypeEnum_type,
    IFC4X3_RC4_IfcBenchmarkEnum_type,
    IFC4X3_RC4_IfcBendingParameterSelect_type,
    IFC4X3_RC4_IfcBinary_type,
    IFC4X3_RC4_IfcBlobTexture_type,
    IFC4X3_RC4_IfcBlock_type,
    IFC4X3_RC4_IfcBoiler_type,
    IFC4X3_RC4_IfcBoilerType_type,
    IFC4X3_RC4_IfcBoilerTypeEnum_type,
    IFC4X3_RC4_IfcBoolean_type,
    IFC4X3_RC4_IfcBooleanClippingResult_type,
    IFC4X3_RC4_IfcBooleanOperand_type,
    IFC4X3_RC4_IfcBooleanOperator_type,
    IFC4X3_RC4_IfcBooleanResult_type,
    IFC4X3_RC4_IfcBorehole_type,
    IFC4X3_RC4_IfcBoundaryCondition_type,
    IFC4X3_RC4_IfcBoundaryCurve_type,
    IFC4X3_RC4_IfcBoundaryEdgeCondition_type,
    IFC4X3_RC4_IfcBoundaryFaceCondition_type,
    IFC4X3_RC4_IfcBoundaryNodeCondition_type,
    IFC4X3_RC4_IfcBoundaryNodeConditionWarping_type,
    IFC4X3_RC4_IfcBoundedCurve_type,
    IFC4X3_RC4_IfcBoundedSurface_type,
    IFC4X3_RC4_IfcBoundingBox_type,
    IFC4X3_RC4_IfcBoxAlignment_type,
    IFC4X3_RC4_IfcBoxedHalfSpace_type,
    IFC4X3_RC4_IfcBridge_type,
    IFC4X3_RC4_IfcBridgePartTypeEnum_type,
    IFC4X3_RC4_IfcBridgeTypeEnum_type,
    IFC4X3_RC4_IfcBSplineCurve_type,
    IFC4X3_RC4_IfcBSplineCurveForm_type,
    IFC4X3_RC4_IfcBSplineCurveWithKnots_type,
    IFC4X3_RC4_IfcBSplineSurface_type,
    IFC4X3_RC4_IfcBSplineSurfaceForm_type,
    IFC4X3_RC4_IfcBSplineSurfaceWithKnots_type,
    IFC4X3_RC4_IfcBuilding_type,
    IFC4X3_RC4_IfcBuildingElementPart_type,
    IFC4X3_RC4_IfcBuildingElementPartType_type,
    IFC4X3_RC4_IfcBuildingElementPartTypeEnum_type,
    IFC4X3_RC4_IfcBuildingElementProxy_type,
    IFC4X3_RC4_IfcBuildingElementProxyType_type,
    IFC4X3_RC4_IfcBuildingElementProxyTypeEnum_type,
    IFC4X3_RC4_IfcBuildingStorey_type,
    IFC4X3_RC4_IfcBuildingSystem_type,
    IFC4X3_RC4_IfcBuildingSystemTypeEnum_type,
    IFC4X3_RC4_IfcBuiltElement_type,
    IFC4X3_RC4_IfcBuiltElementType_type,
    IFC4X3_RC4_IfcBuiltSystem_type,
    IFC4X3_RC4_IfcBuiltSystemTypeEnum_type,
    IFC4X3_RC4_IfcBurner_type,
    IFC4X3_RC4_IfcBurnerType_type,
    IFC4X3_RC4_IfcBurnerTypeEnum_type,
    IFC4X3_RC4_IfcCableCarrierFitting_type,
    IFC4X3_RC4_IfcCableCarrierFittingType_type,
    IFC4X3_RC4_IfcCableCarrierFittingTypeEnum_type,
    IFC4X3_RC4_IfcCableCarrierSegment_type,
    IFC4X3_RC4_IfcCableCarrierSegmentType_type,
    IFC4X3_RC4_IfcCableCarrierSegmentTypeEnum_type,
    IFC4X3_RC4_IfcCableFitting_type,
    IFC4X3_RC4_IfcCableFittingType_type,
    IFC4X3_RC4_IfcCableFittingTypeEnum_type,
    IFC4X3_RC4_IfcCableSegment_type,
    IFC4X3_RC4_IfcCableSegmentType_type,
    IFC4X3_RC4_IfcCableSegmentTypeEnum_type,
    IFC4X3_RC4_IfcCaissonFoundation_type,
    IFC4X3_RC4_IfcCaissonFoundationType_type,
    IFC4X3_RC4_IfcCaissonFoundationTypeEnum_type,
    IFC4X3_RC4_IfcCardinalPointReference_type,
    IFC4X3_RC4_IfcCartesianPoint_type,
    IFC4X3_RC4_IfcCartesianPointList_type,
    IFC4X3_RC4_IfcCartesianPointList2D_type,
    IFC4X3_RC4_IfcCartesianPointList3D_type,
    IFC4X3_RC4_IfcCartesianTransformationOperator_type,
    IFC4X3_RC4_IfcCartesianTransformationOperator2D_type,
    IFC4X3_RC4_IfcCartesianTransformationOperator2DnonUniform_type,
    IFC4X3_RC4_IfcCartesianTransformationOperator3D_type,
    IFC4X3_RC4_IfcCartesianTransformationOperator3DnonUniform_type,
    IFC4X3_RC4_IfcCenterLineProfileDef_type,
    IFC4X3_RC4_IfcChangeActionEnum_type,
    IFC4X3_RC4_IfcChiller_type,
    IFC4X3_RC4_IfcChillerType_type,
    IFC4X3_RC4_IfcChillerTypeEnum_type,
    IFC4X3_RC4_IfcChimney_type,
    IFC4X3_RC4_IfcChimneyType_type,
    IFC4X3_RC4_IfcChimneyTypeEnum_type,
    IFC4X3_RC4_IfcCircle_type,
    IFC4X3_RC4_IfcCircleHollowProfileDef_type,
    IFC4X3_RC4_IfcCircleProfileDef_type,
    IFC4X3_RC4_IfcCivilElement_type,
    IFC4X3_RC4_IfcCivilElementType_type,
    IFC4X3_RC4_IfcClassification_type,
    IFC4X3_RC4_IfcClassificationReference_type,
    IFC4X3_RC4_IfcClassificationReferenceSelect_type,
    IFC4X3_RC4_IfcClassificationSelect_type,
    IFC4X3_RC4_IfcClosedShell_type,
    IFC4X3_RC4_IfcClothoid_type,
    IFC4X3_RC4_IfcCoil_type,
    IFC4X3_RC4_IfcCoilType_type,
    IFC4X3_RC4_IfcCoilTypeEnum_type,
    IFC4X3_RC4_IfcColour_type,
    IFC4X3_RC4_IfcColourOrFactor_type,
    IFC4X3_RC4_IfcColourRgb_type,
    IFC4X3_RC4_IfcColourRgbList_type,
    IFC4X3_RC4_IfcColourSpecification_type,
    IFC4X3_RC4_IfcColumn_type,
    IFC4X3_RC4_IfcColumnStandardCase_type,
    IFC4X3_RC4_IfcColumnType_type,
    IFC4X3_RC4_IfcColumnTypeEnum_type,
    IFC4X3_RC4_IfcCommunicationsAppliance_type,
    IFC4X3_RC4_IfcCommunicationsApplianceType_type,
    IFC4X3_RC4_IfcCommunicationsApplianceTypeEnum_type,
    IFC4X3_RC4_IfcComplexNumber_type,
    IFC4X3_RC4_IfcComplexProperty_type,
    IFC4X3_RC4_IfcComplexPropertyTemplate_type,
    IFC4X3_RC4_IfcComplexPropertyTemplateTypeEnum_type,
    IFC4X3_RC4_IfcCompositeCurve_type,
    IFC4X3_RC4_IfcCompositeCurveOnSurface_type,
    IFC4X3_RC4_IfcCompositeCurveSegment_type,
    IFC4X3_RC4_IfcCompositeProfileDef_type,
    IFC4X3_RC4_IfcCompoundPlaneAngleMeasure_type,
    IFC4X3_RC4_IfcCompressor_type,
    IFC4X3_RC4_IfcCompressorType_type,
    IFC4X3_RC4_IfcCompressorTypeEnum_type,
    IFC4X3_RC4_IfcCondenser_type,
    IFC4X3_RC4_IfcCondenserType_type,
    IFC4X3_RC4_IfcCondenserTypeEnum_type,
    IFC4X3_RC4_IfcConic_type,
    IFC4X3_RC4_IfcConnectedFaceSet_type,
    IFC4X3_RC4_IfcConnectionCurveGeometry_type,
    IFC4X3_RC4_IfcConnectionGeometry_type,
    IFC4X3_RC4_IfcConnectionPointEccentricity_type,
    IFC4X3_RC4_IfcConnectionPointGeometry_type,
    IFC4X3_RC4_IfcConnectionSurfaceGeometry_type,
    IFC4X3_RC4_IfcConnectionTypeEnum_type,
    IFC4X3_RC4_IfcConnectionVolumeGeometry_type,
    IFC4X3_RC4_IfcConstraint_type,
    IFC4X3_RC4_IfcConstraintEnum_type,
    IFC4X3_RC4_IfcConstructionEquipmentResource_type,
    IFC4X3_RC4_IfcConstructionEquipmentResourceType_type,
    IFC4X3_RC4_IfcConstructionEquipmentResourceTypeEnum_type,
    IFC4X3_RC4_IfcConstructionMaterialResource_type,
    IFC4X3_RC4_IfcConstructionMaterialResourceType_type,
    IFC4X3_RC4_IfcConstructionMaterialResourceTypeEnum_type,
    IFC4X3_RC4_IfcConstructionProductResource_type,
    IFC4X3_RC4_IfcConstructionProductResourceType_type,
    IFC4X3_RC4_IfcConstructionProductResourceTypeEnum_type,
    IFC4X3_RC4_IfcConstructionResource_type,
    IFC4X3_RC4_IfcConstructionResourceType_type,
    IFC4X3_RC4_IfcContext_type,
    IFC4X3_RC4_IfcContextDependentMeasure_type,
    IFC4X3_RC4_IfcContextDependentUnit_type,
    IFC4X3_RC4_IfcControl_type,
    IFC4X3_RC4_IfcController_type,
    IFC4X3_RC4_IfcControllerType_type,
    IFC4X3_RC4_IfcControllerTypeEnum_type,
    IFC4X3_RC4_IfcConversionBasedUnit_type,
    IFC4X3_RC4_IfcConversionBasedUnitWithOffset_type,
    IFC4X3_RC4_IfcConveyorSegment_type,
    IFC4X3_RC4_IfcConveyorSegmentType_type,
    IFC4X3_RC4_IfcConveyorSegmentTypeEnum_type,
    IFC4X3_RC4_IfcCooledBeam_type,
    IFC4X3_RC4_IfcCooledBeamType_type,
    IFC4X3_RC4_IfcCooledBeamTypeEnum_type,
    IFC4X3_RC4_IfcCoolingTower_type,
    IFC4X3_RC4_IfcCoolingTowerType_type,
    IFC4X3_RC4_IfcCoolingTowerTypeEnum_type,
    IFC4X3_RC4_IfcCoordinateOperation_type,
    IFC4X3_RC4_IfcCoordinateReferenceSystem_type,
    IFC4X3_RC4_IfcCoordinateReferenceSystemSelect_type,
    IFC4X3_RC4_IfcCosine_type,
    IFC4X3_RC4_IfcCostItem_type,
    IFC4X3_RC4_IfcCostItemTypeEnum_type,
    IFC4X3_RC4_IfcCostSchedule_type,
    IFC4X3_RC4_IfcCostScheduleTypeEnum_type,
    IFC4X3_RC4_IfcCostValue_type,
    IFC4X3_RC4_IfcCountMeasure_type,
    IFC4X3_RC4_IfcCourse_type,
    IFC4X3_RC4_IfcCourseType_type,
    IFC4X3_RC4_IfcCourseTypeEnum_type,
    IFC4X3_RC4_IfcCovering_type,
    IFC4X3_RC4_IfcCoveringType_type,
    IFC4X3_RC4_IfcCoveringTypeEnum_type,
    IFC4X3_RC4_IfcCrewResource_type,
    IFC4X3_RC4_IfcCrewResourceType_type,
    IFC4X3_RC4_IfcCrewResourceTypeEnum_type,
    IFC4X3_RC4_IfcCsgPrimitive3D_type,
    IFC4X3_RC4_IfcCsgSelect_type,
    IFC4X3_RC4_IfcCsgSolid_type,
    IFC4X3_RC4_IfcCShapeProfileDef_type,
    IFC4X3_RC4_IfcCurrencyRelationship_type,
    IFC4X3_RC4_IfcCurtainWall_type,
    IFC4X3_RC4_IfcCurtainWallType_type,
    IFC4X3_RC4_IfcCurtainWallTypeEnum_type,
    IFC4X3_RC4_IfcCurvatureMeasure_type,
    IFC4X3_RC4_IfcCurve_type,
    IFC4X3_RC4_IfcCurveBoundedPlane_type,
    IFC4X3_RC4_IfcCurveBoundedSurface_type,
    IFC4X3_RC4_IfcCurveFontOrScaledCurveFontSelect_type,
    IFC4X3_RC4_IfcCurveInterpolationEnum_type,
    IFC4X3_RC4_IfcCurveMeasureSelect_type,
    IFC4X3_RC4_IfcCurveOnSurface_type,
    IFC4X3_RC4_IfcCurveOrEdgeCurve_type,
    IFC4X3_RC4_IfcCurveSegment_type,
    IFC4X3_RC4_IfcCurveStyle_type,
    IFC4X3_RC4_IfcCurveStyleFont_type,
    IFC4X3_RC4_IfcCurveStyleFontAndScaling_type,
    IFC4X3_RC4_IfcCurveStyleFontPattern_type,
    IFC4X3_RC4_IfcCurveStyleFontSelect_type,
    IFC4X3_RC4_IfcCylindricalSurface_type,
    IFC4X3_RC4_IfcDamper_type,
    IFC4X3_RC4_IfcDamperType_type,
    IFC4X3_RC4_IfcDamperTypeEnum_type,
    IFC4X3_RC4_IfcDataOriginEnum_type,
    IFC4X3_RC4_IfcDate_type,
    IFC4X3_RC4_IfcDateTime_type,
    IFC4X3_RC4_IfcDayInMonthNumber_type,
    IFC4X3_RC4_IfcDayInWeekNumber_type,
    IFC4X3_RC4_IfcDeepFoundation_type,
    IFC4X3_RC4_IfcDeepFoundationType_type,
    IFC4X3_RC4_IfcDefinitionSelect_type,
    IFC4X3_RC4_IfcDerivedMeasureValue_type,
    IFC4X3_RC4_IfcDerivedProfileDef_type,
    IFC4X3_RC4_IfcDerivedUnit_type,
    IFC4X3_RC4_IfcDerivedUnitElement_type,
    IFC4X3_RC4_IfcDerivedUnitEnum_type,
    IFC4X3_RC4_IfcDescriptiveMeasure_type,
    IFC4X3_RC4_IfcDimensionalExponents_type,
    IFC4X3_RC4_IfcDimensionCount_type,
    IFC4X3_RC4_IfcDirection_type,
    IFC4X3_RC4_IfcDirectionSenseEnum_type,
    IFC4X3_RC4_IfcDirectrixCurveSweptAreaSolid_type,
    IFC4X3_RC4_IfcDirectrixDerivedReferenceSweptAreaSolid_type,
    IFC4X3_RC4_IfcDiscreteAccessory_type,
    IFC4X3_RC4_IfcDiscreteAccessoryType_type,
    IFC4X3_RC4_IfcDiscreteAccessoryTypeEnum_type,
    IFC4X3_RC4_IfcDistributionBoard_type,
    IFC4X3_RC4_IfcDistributionBoardType_type,
    IFC4X3_RC4_IfcDistributionBoardTypeEnum_type,
    IFC4X3_RC4_IfcDistributionChamberElement_type,
    IFC4X3_RC4_IfcDistributionChamberElementType_type,
    IFC4X3_RC4_IfcDistributionChamberElementTypeEnum_type,
    IFC4X3_RC4_IfcDistributionCircuit_type,
    IFC4X3_RC4_IfcDistributionControlElement_type,
    IFC4X3_RC4_IfcDistributionControlElementType_type,
    IFC4X3_RC4_IfcDistributionElement_type,
    IFC4X3_RC4_IfcDistributionElementType_type,
    IFC4X3_RC4_IfcDistributionFlowElement_type,
    IFC4X3_RC4_IfcDistributionFlowElementType_type,
    IFC4X3_RC4_IfcDistributionPort_type,
    IFC4X3_RC4_IfcDistributionPortTypeEnum_type,
    IFC4X3_RC4_IfcDistributionSystem_type,
    IFC4X3_RC4_IfcDistributionSystemEnum_type,
    IFC4X3_RC4_IfcDocumentConfidentialityEnum_type,
    IFC4X3_RC4_IfcDocumentInformation_type,
    IFC4X3_RC4_IfcDocumentInformationRelationship_type,
    IFC4X3_RC4_IfcDocumentReference_type,
    IFC4X3_RC4_IfcDocumentSelect_type,
    IFC4X3_RC4_IfcDocumentStatusEnum_type,
    IFC4X3_RC4_IfcDoor_type,
    IFC4X3_RC4_IfcDoorLiningProperties_type,
    IFC4X3_RC4_IfcDoorPanelOperationEnum_type,
    IFC4X3_RC4_IfcDoorPanelPositionEnum_type,
    IFC4X3_RC4_IfcDoorPanelProperties_type,
    IFC4X3_RC4_IfcDoorStandardCase_type,
    IFC4X3_RC4_IfcDoorStyle_type,
    IFC4X3_RC4_IfcDoorStyleConstructionEnum_type,
    IFC4X3_RC4_IfcDoorStyleOperationEnum_type,
    IFC4X3_RC4_IfcDoorType_type,
    IFC4X3_RC4_IfcDoorTypeEnum_type,
    IFC4X3_RC4_IfcDoorTypeOperationEnum_type,
    IFC4X3_RC4_IfcDoseEquivalentMeasure_type,
    IFC4X3_RC4_IfcDraughtingPreDefinedColour_type,
    IFC4X3_RC4_IfcDraughtingPreDefinedCurveFont_type,
    IFC4X3_RC4_IfcDuctFitting_type,
    IFC4X3_RC4_IfcDuctFittingType_type,
    IFC4X3_RC4_IfcDuctFittingTypeEnum_type,
    IFC4X3_RC4_IfcDuctSegment_type,
    IFC4X3_RC4_IfcDuctSegmentType_type,
    IFC4X3_RC4_IfcDuctSegmentTypeEnum_type,
    IFC4X3_RC4_IfcDuctSilencer_type,
    IFC4X3_RC4_IfcDuctSilencerType_type,
    IFC4X3_RC4_IfcDuctSilencerTypeEnum_type,
    IFC4X3_RC4_IfcDuration_type,
    IFC4X3_RC4_IfcDynamicViscosityMeasure_type,
    IFC4X3_RC4_IfcEarthworksCut_type,
    IFC4X3_RC4_IfcEarthworksCutTypeEnum_type,
    IFC4X3_RC4_IfcEarthworksElement_type,
    IFC4X3_RC4_IfcEarthworksFill_type,
    IFC4X3_RC4_IfcEarthworksFillTypeEnum_type,
    IFC4X3_RC4_IfcEdge_type,
    IFC4X3_RC4_IfcEdgeCurve_type,
    IFC4X3_RC4_IfcEdgeLoop_type,
    IFC4X3_RC4_IfcElectricAppliance_type,
    IFC4X3_RC4_IfcElectricApplianceType_type,
    IFC4X3_RC4_IfcElectricApplianceTypeEnum_type,
    IFC4X3_RC4_IfcElectricCapacitanceMeasure_type,
    IFC4X3_RC4_IfcElectricChargeMeasure_type,
    IFC4X3_RC4_IfcElectricConductanceMeasure_type,
    IFC4X3_RC4_IfcElectricCurrentMeasure_type,
    IFC4X3_RC4_IfcElectricDistributionBoard_type,
    IFC4X3_RC4_IfcElectricDistributionBoardType_type,
    IFC4X3_RC4_IfcElectricDistributionBoardTypeEnum_type,
    IFC4X3_RC4_IfcElectricFlowStorageDevice_type,
    IFC4X3_RC4_IfcElectricFlowStorageDeviceType_type,
    IFC4X3_RC4_IfcElectricFlowStorageDeviceTypeEnum_type,
    IFC4X3_RC4_IfcElectricFlowTreatmentDevice_type,
    IFC4X3_RC4_IfcElectricFlowTreatmentDeviceType_type,
    IFC4X3_RC4_IfcElectricFlowTreatmentDeviceTypeEnum_type,
    IFC4X3_RC4_IfcElectricGenerator_type,
    IFC4X3_RC4_IfcElectricGeneratorType_type,
    IFC4X3_RC4_IfcElectricGeneratorTypeEnum_type,
    IFC4X3_RC4_IfcElectricMotor_type,
    IFC4X3_RC4_IfcElectricMotorType_type,
    IFC4X3_RC4_IfcElectricMotorTypeEnum_type,
    IFC4X3_RC4_IfcElectricResistanceMeasure_type,
    IFC4X3_RC4_IfcElectricTimeControl_type,
    IFC4X3_RC4_IfcElectricTimeControlType_type,
    IFC4X3_RC4_IfcElectricTimeControlTypeEnum_type,
    IFC4X3_RC4_IfcElectricVoltageMeasure_type,
    IFC4X3_RC4_IfcElement_type,
    IFC4X3_RC4_IfcElementarySurface_type,
    IFC4X3_RC4_IfcElementAssembly_type,
    IFC4X3_RC4_IfcElementAssemblyType_type,
    IFC4X3_RC4_IfcElementAssemblyTypeEnum_type,
    IFC4X3_RC4_IfcElementComponent_type,
    IFC4X3_RC4_IfcElementComponentType_type,
    IFC4X3_RC4_IfcElementCompositionEnum_type,
    IFC4X3_RC4_IfcElementQuantity_type,
    IFC4X3_RC4_IfcElementType_type,
    IFC4X3_RC4_IfcEllipse_type,
    IFC4X3_RC4_IfcEllipseProfileDef_type,
    IFC4X3_RC4_IfcEnergyConversionDevice_type,
    IFC4X3_RC4_IfcEnergyConversionDeviceType_type,
    IFC4X3_RC4_IfcEnergyMeasure_type,
    IFC4X3_RC4_IfcEngine_type,
    IFC4X3_RC4_IfcEngineType_type,
    IFC4X3_RC4_IfcEngineTypeEnum_type,
    IFC4X3_RC4_IfcEvaporativeCooler_type,
    IFC4X3_RC4_IfcEvaporativeCoolerType_type,
    IFC4X3_RC4_IfcEvaporativeCoolerTypeEnum_type,
    IFC4X3_RC4_IfcEvaporator_type,
    IFC4X3_RC4_IfcEvaporatorType_type,
    IFC4X3_RC4_IfcEvaporatorTypeEnum_type,
    IFC4X3_RC4_IfcEvent_type,
    IFC4X3_RC4_IfcEventTime_type,
    IFC4X3_RC4_IfcEventTriggerTypeEnum_type,
    IFC4X3_RC4_IfcEventType_type,
    IFC4X3_RC4_IfcEventTypeEnum_type,
    IFC4X3_RC4_IfcExtendedProperties_type,
    IFC4X3_RC4_IfcExternalInformation_type,
    IFC4X3_RC4_IfcExternallyDefinedHatchStyle_type,
    IFC4X3_RC4_IfcExternallyDefinedSurfaceStyle_type,
    IFC4X3_RC4_IfcExternallyDefinedTextFont_type,
    IFC4X3_RC4_IfcExternalReference_type,
    IFC4X3_RC4_IfcExternalReferenceRelationship_type,
    IFC4X3_RC4_IfcExternalSpatialElement_type,
    IFC4X3_RC4_IfcExternalSpatialElementTypeEnum_type,
    IFC4X3_RC4_IfcExternalSpatialStructureElement_type,
    IFC4X3_RC4_IfcExtrudedAreaSolid_type,
    IFC4X3_RC4_IfcExtrudedAreaSolidTapered_type,
    IFC4X3_RC4_IfcFace_type,
    IFC4X3_RC4_IfcFaceBasedSurfaceModel_type,
    IFC4X3_RC4_IfcFaceBound_type,
    IFC4X3_RC4_IfcFaceOuterBound_type,
    IFC4X3_RC4_IfcFaceSurface_type,
    IFC4X3_RC4_IfcFacetedBrep_type,
    IFC4X3_RC4_IfcFacetedBrepWithVoids_type,
    IFC4X3_RC4_IfcFacility_type,
    IFC4X3_RC4_IfcFacilityPart_type,
    IFC4X3_RC4_IfcFacilityPartCommonTypeEnum_type,
    IFC4X3_RC4_IfcFacilityPartTypeSelect_type,
    IFC4X3_RC4_IfcFacilityUsageEnum_type,
    IFC4X3_RC4_IfcFailureConnectionCondition_type,
    IFC4X3_RC4_IfcFan_type,
    IFC4X3_RC4_IfcFanType_type,
    IFC4X3_RC4_IfcFanTypeEnum_type,
    IFC4X3_RC4_IfcFastener_type,
    IFC4X3_RC4_IfcFastenerType_type,
    IFC4X3_RC4_IfcFastenerTypeEnum_type,
    IFC4X3_RC4_IfcFeatureElement_type,
    IFC4X3_RC4_IfcFeatureElementAddition_type,
    IFC4X3_RC4_IfcFeatureElementSubtraction_type,
    IFC4X3_RC4_IfcFillAreaStyle_type,
    IFC4X3_RC4_IfcFillAreaStyleHatching_type,
    IFC4X3_RC4_IfcFillAreaStyleTiles_type,
    IFC4X3_RC4_IfcFillStyleSelect_type,
    IFC4X3_RC4_IfcFilter_type,
    IFC4X3_RC4_IfcFilterType_type,
    IFC4X3_RC4_IfcFilterTypeEnum_type,
    IFC4X3_RC4_IfcFireSuppressionTerminal_type,
    IFC4X3_RC4_IfcFireSuppressionTerminalType_type,
    IFC4X3_RC4_IfcFireSuppressionTerminalTypeEnum_type,
    IFC4X3_RC4_IfcFixedReferenceSweptAreaSolid_type,
    IFC4X3_RC4_IfcFlowController_type,
    IFC4X3_RC4_IfcFlowControllerType_type,
    IFC4X3_RC4_IfcFlowDirectionEnum_type,
    IFC4X3_RC4_IfcFlowFitting_type,
    IFC4X3_RC4_IfcFlowFittingType_type,
    IFC4X3_RC4_IfcFlowInstrument_type,
    IFC4X3_RC4_IfcFlowInstrumentType_type,
    IFC4X3_RC4_IfcFlowInstrumentTypeEnum_type,
    IFC4X3_RC4_IfcFlowMeter_type,
    IFC4X3_RC4_IfcFlowMeterType_type,
    IFC4X3_RC4_IfcFlowMeterTypeEnum_type,
    IFC4X3_RC4_IfcFlowMovingDevice_type,
    IFC4X3_RC4_IfcFlowMovingDeviceType_type,
    IFC4X3_RC4_IfcFlowSegment_type,
    IFC4X3_RC4_IfcFlowSegmentType_type,
    IFC4X3_RC4_IfcFlowStorageDevice_type,
    IFC4X3_RC4_IfcFlowStorageDeviceType_type,
    IFC4X3_RC4_IfcFlowTerminal_type,
    IFC4X3_RC4_IfcFlowTerminalType_type,
    IFC4X3_RC4_IfcFlowTreatmentDevice_type,
    IFC4X3_RC4_IfcFlowTreatmentDeviceType_type,
    IFC4X3_RC4_IfcFontStyle_type,
    IFC4X3_RC4_IfcFontVariant_type,
    IFC4X3_RC4_IfcFontWeight_type,
    IFC4X3_RC4_IfcFooting_type,
    IFC4X3_RC4_IfcFootingType_type,
    IFC4X3_RC4_IfcFootingTypeEnum_type,
    IFC4X3_RC4_IfcForceMeasure_type,
    IFC4X3_RC4_IfcFrequencyMeasure_type,
    IFC4X3_RC4_IfcFurnishingElement_type,
    IFC4X3_RC4_IfcFurnishingElementType_type,
    IFC4X3_RC4_IfcFurniture_type,
    IFC4X3_RC4_IfcFurnitureType_type,
    IFC4X3_RC4_IfcFurnitureTypeEnum_type,
    IFC4X3_RC4_IfcGeographicElement_type,
    IFC4X3_RC4_IfcGeographicElementType_type,
    IFC4X3_RC4_IfcGeographicElementTypeEnum_type,
    IFC4X3_RC4_IfcGeometricCurveSet_type,
    IFC4X3_RC4_IfcGeometricProjectionEnum_type,
    IFC4X3_RC4_IfcGeometricRepresentationContext_type,
    IFC4X3_RC4_IfcGeometricRepresentationItem_type,
    IFC4X3_RC4_IfcGeometricRepresentationSubContext_type,
    IFC4X3_RC4_IfcGeometricSet_type,
    IFC4X3_RC4_IfcGeometricSetSelect_type,
    IFC4X3_RC4_IfcGeomodel_type,
    IFC4X3_RC4_IfcGeoslice_type,
    IFC4X3_RC4_IfcGeotechnicalAssembly_type,
    IFC4X3_RC4_IfcGeotechnicalElement_type,
    IFC4X3_RC4_IfcGeotechnicalStratum_type,
    IFC4X3_RC4_IfcGloballyUniqueId_type,
    IFC4X3_RC4_IfcGlobalOrLocalEnum_type,
    IFC4X3_RC4_IfcGradientCurve_type,
    IFC4X3_RC4_IfcGrid_type,
    IFC4X3_RC4_IfcGridAxis_type,
    IFC4X3_RC4_IfcGridPlacement_type,
    IFC4X3_RC4_IfcGridPlacementDirectionSelect_type,
    IFC4X3_RC4_IfcGridTypeEnum_type,
    IFC4X3_RC4_IfcGroup_type,
    IFC4X3_RC4_IfcHalfSpaceSolid_type,
    IFC4X3_RC4_IfcHatchLineDistanceSelect_type,
    IFC4X3_RC4_IfcHeatExchanger_type,
    IFC4X3_RC4_IfcHeatExchangerType_type,
    IFC4X3_RC4_IfcHeatExchangerTypeEnum_type,
    IFC4X3_RC4_IfcHeatFluxDensityMeasure_type,
    IFC4X3_RC4_IfcHeatingValueMeasure_type,
    IFC4X3_RC4_IfcHumidifier_type,
    IFC4X3_RC4_IfcHumidifierType_type,
    IFC4X3_RC4_IfcHumidifierTypeEnum_type,
    IFC4X3_RC4_IfcIdentifier_type,
    IFC4X3_RC4_IfcIlluminanceMeasure_type,
    IFC4X3_RC4_IfcImageTexture_type,
    IFC4X3_RC4_IfcImpactProtectionDevice_type,
    IFC4X3_RC4_IfcImpactProtectionDeviceType_type,
    IFC4X3_RC4_IfcImpactProtectionDeviceTypeEnum_type,
    IFC4X3_RC4_IfcImpactProtectionDeviceTypeSelect_type,
    IFC4X3_RC4_IfcIndexedColourMap_type,
    IFC4X3_RC4_IfcIndexedPolyCurve_type,
    IFC4X3_RC4_IfcIndexedPolygonalFace_type,
    IFC4X3_RC4_IfcIndexedPolygonalFaceWithVoids_type,
    IFC4X3_RC4_IfcIndexedTextureMap_type,
    IFC4X3_RC4_IfcIndexedTriangleTextureMap_type,
    IFC4X3_RC4_IfcInductanceMeasure_type,
    IFC4X3_RC4_IfcInteger_type,
    IFC4X3_RC4_IfcIntegerCountRateMeasure_type,
    IFC4X3_RC4_IfcInterceptor_type,
    IFC4X3_RC4_IfcInterceptorType_type,
    IFC4X3_RC4_IfcInterceptorTypeEnum_type,
    IFC4X3_RC4_IfcInterferenceSelect_type,
    IFC4X3_RC4_IfcInternalOrExternalEnum_type,
    IFC4X3_RC4_IfcIntersectionCurve_type,
    IFC4X3_RC4_IfcInventory_type,
    IFC4X3_RC4_IfcInventoryTypeEnum_type,
    IFC4X3_RC4_IfcIonConcentrationMeasure_type,
    IFC4X3_RC4_IfcIrregularTimeSeries_type,
    IFC4X3_RC4_IfcIrregularTimeSeriesValue_type,
    IFC4X3_RC4_IfcIShapeProfileDef_type,
    IFC4X3_RC4_IfcIsothermalMoistureCapacityMeasure_type,
    IFC4X3_RC4_IfcJunctionBox_type,
    IFC4X3_RC4_IfcJunctionBoxType_type,
    IFC4X3_RC4_IfcJunctionBoxTypeEnum_type,
    IFC4X3_RC4_IfcKerb_type,
    IFC4X3_RC4_IfcKerbType_type,
    IFC4X3_RC4_IfcKinematicViscosityMeasure_type,
    IFC4X3_RC4_IfcKnotType_type,
    IFC4X3_RC4_IfcLabel_type,
    IFC4X3_RC4_IfcLaborResource_type,
    IFC4X3_RC4_IfcLaborResourceType_type,
    IFC4X3_RC4_IfcLaborResourceTypeEnum_type,
    IFC4X3_RC4_IfcLagTime_type,
    IFC4X3_RC4_IfcLamp_type,
    IFC4X3_RC4_IfcLampType_type,
    IFC4X3_RC4_IfcLampTypeEnum_type,
    IFC4X3_RC4_IfcLanguageId_type,
    IFC4X3_RC4_IfcLayeredItem_type,
    IFC4X3_RC4_IfcLayerSetDirectionEnum_type,
    IFC4X3_RC4_IfcLengthMeasure_type,
    IFC4X3_RC4_IfcLibraryInformation_type,
    IFC4X3_RC4_IfcLibraryReference_type,
    IFC4X3_RC4_IfcLibrarySelect_type,
    IFC4X3_RC4_IfcLightDistributionCurveEnum_type,
    IFC4X3_RC4_IfcLightDistributionData_type,
    IFC4X3_RC4_IfcLightDistributionDataSourceSelect_type,
    IFC4X3_RC4_IfcLightEmissionSourceEnum_type,
    IFC4X3_RC4_IfcLightFixture_type,
    IFC4X3_RC4_IfcLightFixtureType_type,
    IFC4X3_RC4_IfcLightFixtureTypeEnum_type,
    IFC4X3_RC4_IfcLightIntensityDistribution_type,
    IFC4X3_RC4_IfcLightSource_type,
    IFC4X3_RC4_IfcLightSourceAmbient_type,
    IFC4X3_RC4_IfcLightSourceDirectional_type,
    IFC4X3_RC4_IfcLightSourceGoniometric_type,
    IFC4X3_RC4_IfcLightSourcePositional_type,
    IFC4X3_RC4_IfcLightSourceSpot_type,
    IFC4X3_RC4_IfcLine_type,
    IFC4X3_RC4_IfcLinearElement_type,
    IFC4X3_RC4_IfcLinearForceMeasure_type,
    IFC4X3_RC4_IfcLinearMomentMeasure_type,
    IFC4X3_RC4_IfcLinearPlacement_type,
    IFC4X3_RC4_IfcLinearPositioningElement_type,
    IFC4X3_RC4_IfcLinearStiffnessMeasure_type,
    IFC4X3_RC4_IfcLinearVelocityMeasure_type,
    IFC4X3_RC4_IfcLineIndex_type,
    IFC4X3_RC4_IfcLiquidTerminal_type,
    IFC4X3_RC4_IfcLiquidTerminalType_type,
    IFC4X3_RC4_IfcLiquidTerminalTypeEnum_type,
    IFC4X3_RC4_IfcLoadGroupTypeEnum_type,
    IFC4X3_RC4_IfcLocalPlacement_type,
    IFC4X3_RC4_IfcLogical_type,
    IFC4X3_RC4_IfcLogicalOperatorEnum_type,
    IFC4X3_RC4_IfcLoop_type,
    IFC4X3_RC4_IfcLShapeProfileDef_type,
    IFC4X3_RC4_IfcLuminousFluxMeasure_type,
    IFC4X3_RC4_IfcLuminousIntensityDistributionMeasure_type,
    IFC4X3_RC4_IfcLuminousIntensityMeasure_type,
    IFC4X3_RC4_IfcMagneticFluxDensityMeasure_type,
    IFC4X3_RC4_IfcMagneticFluxMeasure_type,
    IFC4X3_RC4_IfcManifoldSolidBrep_type,
    IFC4X3_RC4_IfcMapConversion_type,
    IFC4X3_RC4_IfcMappedItem_type,
    IFC4X3_RC4_IfcMarineFacility_type,
    IFC4X3_RC4_IfcMarineFacilityTypeEnum_type,
    IFC4X3_RC4_IfcMarinePartTypeEnum_type,
    IFC4X3_RC4_IfcMassDensityMeasure_type,
    IFC4X3_RC4_IfcMassFlowRateMeasure_type,
    IFC4X3_RC4_IfcMassMeasure_type,
    IFC4X3_RC4_IfcMassPerLengthMeasure_type,
    IFC4X3_RC4_IfcMaterial_type,
    IFC4X3_RC4_IfcMaterialClassificationRelationship_type,
    IFC4X3_RC4_IfcMaterialConstituent_type,
    IFC4X3_RC4_IfcMaterialConstituentSet_type,
    IFC4X3_RC4_IfcMaterialDefinition_type,
    IFC4X3_RC4_IfcMaterialDefinitionRepresentation_type,
    IFC4X3_RC4_IfcMaterialLayer_type,
    IFC4X3_RC4_IfcMaterialLayerSet_type,
    IFC4X3_RC4_IfcMaterialLayerSetUsage_type,
    IFC4X3_RC4_IfcMaterialLayerWithOffsets_type,
    IFC4X3_RC4_IfcMaterialList_type,
    IFC4X3_RC4_IfcMaterialProfile_type,
    IFC4X3_RC4_IfcMaterialProfileSet_type,
    IFC4X3_RC4_IfcMaterialProfileSetUsage_type,
    IFC4X3_RC4_IfcMaterialProfileSetUsageTapering_type,
    IFC4X3_RC4_IfcMaterialProfileWithOffsets_type,
    IFC4X3_RC4_IfcMaterialProperties_type,
    IFC4X3_RC4_IfcMaterialRelationship_type,
    IFC4X3_RC4_IfcMaterialSelect_type,
    IFC4X3_RC4_IfcMaterialUsageDefinition_type,
    IFC4X3_RC4_IfcMeasureValue_type,
    IFC4X3_RC4_IfcMeasureWithUnit_type,
    IFC4X3_RC4_IfcMechanicalFastener_type,
    IFC4X3_RC4_IfcMechanicalFastenerType_type,
    IFC4X3_RC4_IfcMechanicalFastenerTypeEnum_type,
    IFC4X3_RC4_IfcMedicalDevice_type,
    IFC4X3_RC4_IfcMedicalDeviceType_type,
    IFC4X3_RC4_IfcMedicalDeviceTypeEnum_type,
    IFC4X3_RC4_IfcMember_type,
    IFC4X3_RC4_IfcMemberStandardCase_type,
    IFC4X3_RC4_IfcMemberType_type,
    IFC4X3_RC4_IfcMemberTypeEnum_type,
    IFC4X3_RC4_IfcMetric_type,
    IFC4X3_RC4_IfcMetricValueSelect_type,
    IFC4X3_RC4_IfcMirroredProfileDef_type,
    IFC4X3_RC4_IfcMobileTelecommunicationsAppliance_type,
    IFC4X3_RC4_IfcMobileTelecommunicationsApplianceType_type,
    IFC4X3_RC4_IfcMobileTelecommunicationsApplianceTypeEnum_type,
    IFC4X3_RC4_IfcModulusOfElasticityMeasure_type,
    IFC4X3_RC4_IfcModulusOfLinearSubgradeReactionMeasure_type,
    IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionMeasure_type,
    IFC4X3_RC4_IfcModulusOfRotationalSubgradeReactionSelect_type,
    IFC4X3_RC4_IfcModulusOfSubgradeReactionMeasure_type,
    IFC4X3_RC4_IfcModulusOfSubgradeReactionSelect_type,
    IFC4X3_RC4_IfcModulusOfTranslationalSubgradeReactionSelect_type,
    IFC4X3_RC4_IfcMoistureDiffusivityMeasure_type,
    IFC4X3_RC4_IfcMolecularWeightMeasure_type,
    IFC4X3_RC4_IfcMomentOfInertiaMeasure_type,
    IFC4X3_RC4_IfcMonetaryMeasure_type,
    IFC4X3_RC4_IfcMonetaryUnit_type,
    IFC4X3_RC4_IfcMonthInYearNumber_type,
    IFC4X3_RC4_IfcMooringDevice_type,
    IFC4X3_RC4_IfcMooringDeviceType_type,
    IFC4X3_RC4_IfcMooringDeviceTypeEnum_type,
    IFC4X3_RC4_IfcMotorConnection_type,
    IFC4X3_RC4_IfcMotorConnectionType_type,
    IFC4X3_RC4_IfcMotorConnectionTypeEnum_type,
    IFC4X3_RC4_IfcNamedUnit_type,
    IFC4X3_RC4_IfcNavigationElement_type,
    IFC4X3_RC4_IfcNavigationElementType_type,
    IFC4X3_RC4_IfcNavigationElementTypeEnum_type,
    IFC4X3_RC4_IfcNonNegativeLengthMeasure_type,
    IFC4X3_RC4_IfcNormalisedRatioMeasure_type,
    IFC4X3_RC4_IfcNumericMeasure_type,
    IFC4X3_RC4_IfcObject_type,
    IFC4X3_RC4_IfcObjectDefinition_type,
    IFC4X3_RC4_IfcObjective_type,
    IFC4X3_RC4_IfcObjectiveEnum_type,
    IFC4X3_RC4_IfcObjectPlacement_type,
    IFC4X3_RC4_IfcObjectReferenceSelect_type,
    IFC4X3_RC4_IfcObjectTypeEnum_type,
    IFC4X3_RC4_IfcOccupant_type,
    IFC4X3_RC4_IfcOccupantTypeEnum_type,
    IFC4X3_RC4_IfcOffsetCurve_type,
    IFC4X3_RC4_IfcOffsetCurve2D_type,
    IFC4X3_RC4_IfcOffsetCurve3D_type,
    IFC4X3_RC4_IfcOffsetCurveByDistances_type,
    IFC4X3_RC4_IfcOpenCrossProfileDef_type,
    IFC4X3_RC4_IfcOpeningElement_type,
    IFC4X3_RC4_IfcOpeningElementTypeEnum_type,
    IFC4X3_RC4_IfcOpeningStandardCase_type,
    IFC4X3_RC4_IfcOpenShell_type,
    IFC4X3_RC4_IfcOrganization_type,
    IFC4X3_RC4_IfcOrganizationRelationship_type,
    IFC4X3_RC4_IfcOrientedEdge_type,
    IFC4X3_RC4_IfcOuterBoundaryCurve_type,
    IFC4X3_RC4_IfcOutlet_type,
    IFC4X3_RC4_IfcOutletType_type,
    IFC4X3_RC4_IfcOutletTypeEnum_type,
    IFC4X3_RC4_IfcOwnerHistory_type,
    IFC4X3_RC4_IfcParameterizedProfileDef_type,
    IFC4X3_RC4_IfcParameterValue_type,
    IFC4X3_RC4_IfcPath_type,
    IFC4X3_RC4_IfcPavement_type,
    IFC4X3_RC4_IfcPavementType_type,
    IFC4X3_RC4_IfcPavementTypeEnum_type,
    IFC4X3_RC4_IfcPcurve_type,
    IFC4X3_RC4_IfcPerformanceHistory_type,
    IFC4X3_RC4_IfcPerformanceHistoryTypeEnum_type,
    IFC4X3_RC4_IfcPermeableCoveringOperationEnum_type,
    IFC4X3_RC4_IfcPermeableCoveringProperties_type,
    IFC4X3_RC4_IfcPermit_type,
    IFC4X3_RC4_IfcPermitTypeEnum_type,
    IFC4X3_RC4_IfcPerson_type,
    IFC4X3_RC4_IfcPersonAndOrganization_type,
    IFC4X3_RC4_IfcPHMeasure_type,
    IFC4X3_RC4_IfcPhysicalComplexQuantity_type,
    IFC4X3_RC4_IfcPhysicalOrVirtualEnum_type,
    IFC4X3_RC4_IfcPhysicalQuantity_type,
    IFC4X3_RC4_IfcPhysicalSimpleQuantity_type,
    IFC4X3_RC4_IfcPile_type,
    IFC4X3_RC4_IfcPileConstructionEnum_type,
    IFC4X3_RC4_IfcPileType_type,
    IFC4X3_RC4_IfcPileTypeEnum_type,
    IFC4X3_RC4_IfcPipeFitting_type,
    IFC4X3_RC4_IfcPipeFittingType_type,
    IFC4X3_RC4_IfcPipeFittingTypeEnum_type,
    IFC4X3_RC4_IfcPipeSegment_type,
    IFC4X3_RC4_IfcPipeSegmentType_type,
    IFC4X3_RC4_IfcPipeSegmentTypeEnum_type,
    IFC4X3_RC4_IfcPixelTexture_type,
    IFC4X3_RC4_IfcPlacement_type,
    IFC4X3_RC4_IfcPlanarBox_type,
    IFC4X3_RC4_IfcPlanarExtent_type,
    IFC4X3_RC4_IfcPlanarForceMeasure_type,
    IFC4X3_RC4_IfcPlane_type,
    IFC4X3_RC4_IfcPlaneAngleMeasure_type,
    IFC4X3_RC4_IfcPlant_type,
    IFC4X3_RC4_IfcPlate_type,
    IFC4X3_RC4_IfcPlateStandardCase_type,
    IFC4X3_RC4_IfcPlateType_type,
    IFC4X3_RC4_IfcPlateTypeEnum_type,
    IFC4X3_RC4_IfcPoint_type,
    IFC4X3_RC4_IfcPointByDistanceExpression_type,
    IFC4X3_RC4_IfcPointOnCurve_type,
    IFC4X3_RC4_IfcPointOnSurface_type,
    IFC4X3_RC4_IfcPointOrVertexPoint_type,
    IFC4X3_RC4_IfcPolygonalBoundedHalfSpace_type,
    IFC4X3_RC4_IfcPolygonalFaceSet_type,
    IFC4X3_RC4_IfcPolyline_type,
    IFC4X3_RC4_IfcPolyLoop_type,
    IFC4X3_RC4_IfcPolynomialCurve_type,
    IFC4X3_RC4_IfcPort_type,
    IFC4X3_RC4_IfcPositioningElement_type,
    IFC4X3_RC4_IfcPositiveInteger_type,
    IFC4X3_RC4_IfcPositiveLengthMeasure_type,
    IFC4X3_RC4_IfcPositivePlaneAngleMeasure_type,
    IFC4X3_RC4_IfcPositiveRatioMeasure_type,
    IFC4X3_RC4_IfcPostalAddress_type,
    IFC4X3_RC4_IfcPowerMeasure_type,
    IFC4X3_RC4_IfcPreDefinedColour_type,
    IFC4X3_RC4_IfcPreDefinedCurveFont_type,
    IFC4X3_RC4_IfcPreDefinedItem_type,
    IFC4X3_RC4_IfcPreDefinedProperties_type,
    IFC4X3_RC4_IfcPreDefinedPropertySet_type,
    IFC4X3_RC4_IfcPreDefinedTextFont_type,
    IFC4X3_RC4_IfcPreferredSurfaceCurveRepresentation_type,
    IFC4X3_RC4_IfcPresentableText_type,
    IFC4X3_RC4_IfcPresentationItem_type,
    IFC4X3_RC4_IfcPresentationLayerAssignment_type,
    IFC4X3_RC4_IfcPresentationLayerWithStyle_type,
    IFC4X3_RC4_IfcPresentationStyle_type,
    IFC4X3_RC4_IfcPressureMeasure_type,
    IFC4X3_RC4_IfcProcedure_type,
    IFC4X3_RC4_IfcProcedureType_type,
    IFC4X3_RC4_IfcProcedureTypeEnum_type,
    IFC4X3_RC4_IfcProcess_type,
    IFC4X3_RC4_IfcProcessSelect_type,
    IFC4X3_RC4_IfcProduct_type,
    IFC4X3_RC4_IfcProductDefinitionShape_type,
    IFC4X3_RC4_IfcProductRepresentation_type,
    IFC4X3_RC4_IfcProductRepresentationSelect_type,
    IFC4X3_RC4_IfcProductSelect_type,
    IFC4X3_RC4_IfcProfileDef_type,
    IFC4X3_RC4_IfcProfileProperties_type,
    IFC4X3_RC4_IfcProfileTypeEnum_type,
    IFC4X3_RC4_IfcProject_type,
    IFC4X3_RC4_IfcProjectedCRS_type,
    IFC4X3_RC4_IfcProjectedOrTrueLengthEnum_type,
    IFC4X3_RC4_IfcProjectionElement_type,
    IFC4X3_RC4_IfcProjectionElementTypeEnum_type,
    IFC4X3_RC4_IfcProjectLibrary_type,
    IFC4X3_RC4_IfcProjectOrder_type,
    IFC4X3_RC4_IfcProjectOrderTypeEnum_type,
    IFC4X3_RC4_IfcProperty_type,
    IFC4X3_RC4_IfcPropertyAbstraction_type,
    IFC4X3_RC4_IfcPropertyBoundedValue_type,
    IFC4X3_RC4_IfcPropertyDefinition_type,
    IFC4X3_RC4_IfcPropertyDependencyRelationship_type,
    IFC4X3_RC4_IfcPropertyEnumeratedValue_type,
    IFC4X3_RC4_IfcPropertyEnumeration_type,
    IFC4X3_RC4_IfcPropertyListValue_type,
    IFC4X3_RC4_IfcPropertyReferenceValue_type,
    IFC4X3_RC4_IfcPropertySet_type,
    IFC4X3_RC4_IfcPropertySetDefinition_type,
    IFC4X3_RC4_IfcPropertySetDefinitionSelect_type,
    IFC4X3_RC4_IfcPropertySetDefinitionSet_type,
    IFC4X3_RC4_IfcPropertySetTemplate_type,
    IFC4X3_RC4_IfcPropertySetTemplateTypeEnum_type,
    IFC4X3_RC4_IfcPropertySingleValue_type,
    IFC4X3_RC4_IfcPropertyTableValue_type,
    IFC4X3_RC4_IfcPropertyTemplate_type,
    IFC4X3_RC4_IfcPropertyTemplateDefinition_type,
    IFC4X3_RC4_IfcProtectiveDevice_type,
    IFC4X3_RC4_IfcProtectiveDeviceTrippingUnit_type,
    IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitType_type,
    IFC4X3_RC4_IfcProtectiveDeviceTrippingUnitTypeEnum_type,
    IFC4X3_RC4_IfcProtectiveDeviceType_type,
    IFC4X3_RC4_IfcProtectiveDeviceTypeEnum_type,
    IFC4X3_RC4_IfcProxy_type,
    IFC4X3_RC4_IfcPump_type,
    IFC4X3_RC4_IfcPumpType_type,
    IFC4X3_RC4_IfcPumpTypeEnum_type,
    IFC4X3_RC4_IfcQuantityArea_type,
    IFC4X3_RC4_IfcQuantityCount_type,
    IFC4X3_RC4_IfcQuantityLength_type,
    IFC4X3_RC4_IfcQuantitySet_type,
    IFC4X3_RC4_IfcQuantityTime_type,
    IFC4X3_RC4_IfcQuantityVolume_type,
    IFC4X3_RC4_IfcQuantityWeight_type,
    IFC4X3_RC4_IfcRadioActivityMeasure_type,
    IFC4X3_RC4_IfcRail_type,
    IFC4X3_RC4_IfcRailing_type,
    IFC4X3_RC4_IfcRailingType_type,
    IFC4X3_RC4_IfcRailingTypeEnum_type,
    IFC4X3_RC4_IfcRailType_type,
    IFC4X3_RC4_IfcRailTypeEnum_type,
    IFC4X3_RC4_IfcRailway_type,
    IFC4X3_RC4_IfcRailwayPartTypeEnum_type,
    IFC4X3_RC4_IfcRailwayTypeEnum_type,
    IFC4X3_RC4_IfcRamp_type,
    IFC4X3_RC4_IfcRampFlight_type,
    IFC4X3_RC4_IfcRampFlightType_type,
    IFC4X3_RC4_IfcRampFlightTypeEnum_type,
    IFC4X3_RC4_IfcRampType_type,
    IFC4X3_RC4_IfcRampTypeEnum_type,
    IFC4X3_RC4_IfcRatioMeasure_type,
    IFC4X3_RC4_IfcRationalBSplineCurveWithKnots_type,
    IFC4X3_RC4_IfcRationalBSplineSurfaceWithKnots_type,
    IFC4X3_RC4_IfcReal_type,
    IFC4X3_RC4_IfcRectangleHollowProfileDef_type,
    IFC4X3_RC4_IfcRectangleProfileDef_type,
    IFC4X3_RC4_IfcRectangularPyramid_type,
    IFC4X3_RC4_IfcRectangularTrimmedSurface_type,
    IFC4X3_RC4_IfcRecurrencePattern_type,
    IFC4X3_RC4_IfcRecurrenceTypeEnum_type,
    IFC4X3_RC4_IfcReference_type,
    IFC4X3_RC4_IfcReferent_type,
    IFC4X3_RC4_IfcReferentTypeEnum_type,
    IFC4X3_RC4_IfcReflectanceMethodEnum_type,
    IFC4X3_RC4_IfcRegularTimeSeries_type,
    IFC4X3_RC4_IfcReinforcedSoil_type,
    IFC4X3_RC4_IfcReinforcedSoilTypeEnum_type,
    IFC4X3_RC4_IfcReinforcementBarProperties_type,
    IFC4X3_RC4_IfcReinforcementDefinitionProperties_type,
    IFC4X3_RC4_IfcReinforcingBar_type,
    IFC4X3_RC4_IfcReinforcingBarRoleEnum_type,
    IFC4X3_RC4_IfcReinforcingBarSurfaceEnum_type,
    IFC4X3_RC4_IfcReinforcingBarType_type,
    IFC4X3_RC4_IfcReinforcingBarTypeEnum_type,
    IFC4X3_RC4_IfcReinforcingElement_type,
    IFC4X3_RC4_IfcReinforcingElementType_type,
    IFC4X3_RC4_IfcReinforcingMesh_type,
    IFC4X3_RC4_IfcReinforcingMeshType_type,
    IFC4X3_RC4_IfcReinforcingMeshTypeEnum_type,
    IFC4X3_RC4_IfcRelAdheresToElement_type,
    IFC4X3_RC4_IfcRelAggregates_type,
    IFC4X3_RC4_IfcRelAssigns_type,
    IFC4X3_RC4_IfcRelAssignsToActor_type,
    IFC4X3_RC4_IfcRelAssignsToControl_type,
    IFC4X3_RC4_IfcRelAssignsToGroup_type,
    IFC4X3_RC4_IfcRelAssignsToGroupByFactor_type,
    IFC4X3_RC4_IfcRelAssignsToProcess_type,
    IFC4X3_RC4_IfcRelAssignsToProduct_type,
    IFC4X3_RC4_IfcRelAssignsToResource_type,
    IFC4X3_RC4_IfcRelAssociates_type,
    IFC4X3_RC4_IfcRelAssociatesApproval_type,
    IFC4X3_RC4_IfcRelAssociatesClassification_type,
    IFC4X3_RC4_IfcRelAssociatesConstraint_type,
    IFC4X3_RC4_IfcRelAssociatesDocument_type,
    IFC4X3_RC4_IfcRelAssociatesLibrary_type,
    IFC4X3_RC4_IfcRelAssociatesMaterial_type,
    IFC4X3_RC4_IfcRelAssociatesProfileDef_type,
    IFC4X3_RC4_IfcRelationship_type,
    IFC4X3_RC4_IfcRelConnects_type,
    IFC4X3_RC4_IfcRelConnectsElements_type,
    IFC4X3_RC4_IfcRelConnectsPathElements_type,
    IFC4X3_RC4_IfcRelConnectsPorts_type,
    IFC4X3_RC4_IfcRelConnectsPortToElement_type,
    IFC4X3_RC4_IfcRelConnectsStructuralActivity_type,
    IFC4X3_RC4_IfcRelConnectsStructuralMember_type,
    IFC4X3_RC4_IfcRelConnectsWithEccentricity_type,
    IFC4X3_RC4_IfcRelConnectsWithRealizingElements_type,
    IFC4X3_RC4_IfcRelContainedInSpatialStructure_type,
    IFC4X3_RC4_IfcRelCoversBldgElements_type,
    IFC4X3_RC4_IfcRelCoversSpaces_type,
    IFC4X3_RC4_IfcRelDeclares_type,
    IFC4X3_RC4_IfcRelDecomposes_type,
    IFC4X3_RC4_IfcRelDefines_type,
    IFC4X3_RC4_IfcRelDefinesByObject_type,
    IFC4X3_RC4_IfcRelDefinesByProperties_type,
    IFC4X3_RC4_IfcRelDefinesByTemplate_type,
    IFC4X3_RC4_IfcRelDefinesByType_type,
    IFC4X3_RC4_IfcRelFillsElement_type,
    IFC4X3_RC4_IfcRelFlowControlElements_type,
    IFC4X3_RC4_IfcRelInterferesElements_type,
    IFC4X3_RC4_IfcRelNests_type,
    IFC4X3_RC4_IfcRelPositions_type,
    IFC4X3_RC4_IfcRelProjectsElement_type,
    IFC4X3_RC4_IfcRelReferencedInSpatialStructure_type,
    IFC4X3_RC4_IfcRelSequence_type,
    IFC4X3_RC4_IfcRelServicesBuildings_type,
    IFC4X3_RC4_IfcRelSpaceBoundary_type,
    IFC4X3_RC4_IfcRelSpaceBoundary1stLevel_type,
    IFC4X3_RC4_IfcRelSpaceBoundary2ndLevel_type,
    IFC4X3_RC4_IfcRelVoidsElement_type,
    IFC4X3_RC4_IfcReparametrisedCompositeCurveSegment_type,
    IFC4X3_RC4_IfcRepresentation_type,
    IFC4X3_RC4_IfcRepresentationContext_type,
    IFC4X3_RC4_IfcRepresentationItem_type,
    IFC4X3_RC4_IfcRepresentationMap_type,
    IFC4X3_RC4_IfcResource_type,
    IFC4X3_RC4_IfcResourceApprovalRelationship_type,
    IFC4X3_RC4_IfcResourceConstraintRelationship_type,
    IFC4X3_RC4_IfcResourceLevelRelationship_type,
    IFC4X3_RC4_IfcResourceObjectSelect_type,
    IFC4X3_RC4_IfcResourceSelect_type,
    IFC4X3_RC4_IfcResourceTime_type,
    IFC4X3_RC4_IfcRevolvedAreaSolid_type,
    IFC4X3_RC4_IfcRevolvedAreaSolidTapered_type,
    IFC4X3_RC4_IfcRightCircularCone_type,
    IFC4X3_RC4_IfcRightCircularCylinder_type,
    IFC4X3_RC4_IfcRoad_type,
    IFC4X3_RC4_IfcRoadPartTypeEnum_type,
    IFC4X3_RC4_IfcRoadTypeEnum_type,
    IFC4X3_RC4_IfcRoleEnum_type,
    IFC4X3_RC4_IfcRoof_type,
    IFC4X3_RC4_IfcRoofType_type,
    IFC4X3_RC4_IfcRoofTypeEnum_type,
    IFC4X3_RC4_IfcRoot_type,
    IFC4X3_RC4_IfcRotationalFrequencyMeasure_type,
    IFC4X3_RC4_IfcRotationalMassMeasure_type,
    IFC4X3_RC4_IfcRotationalStiffnessMeasure_type,
    IFC4X3_RC4_IfcRotationalStiffnessSelect_type,
    IFC4X3_RC4_IfcRoundedRectangleProfileDef_type,
    IFC4X3_RC4_IfcSanitaryTerminal_type,
    IFC4X3_RC4_IfcSanitaryTerminalType_type,
    IFC4X3_RC4_IfcSanitaryTerminalTypeEnum_type,
    IFC4X3_RC4_IfcSchedulingTime_type,
    IFC4X3_RC4_IfcSeamCurve_type,
    IFC4X3_RC4_IfcSecondOrderPolynomialSpiral_type,
    IFC4X3_RC4_IfcSectionalAreaIntegralMeasure_type,
    IFC4X3_RC4_IfcSectionedSolid_type,
    IFC4X3_RC4_IfcSectionedSolidHorizontal_type,
    IFC4X3_RC4_IfcSectionedSpine_type,
    IFC4X3_RC4_IfcSectionedSurface_type,
    IFC4X3_RC4_IfcSectionModulusMeasure_type,
    IFC4X3_RC4_IfcSectionProperties_type,
    IFC4X3_RC4_IfcSectionReinforcementProperties_type,
    IFC4X3_RC4_IfcSectionTypeEnum_type,
    IFC4X3_RC4_IfcSegment_type,
    IFC4X3_RC4_IfcSegmentedReferenceCurve_type,
    IFC4X3_RC4_IfcSegmentIndexSelect_type,
    IFC4X3_RC4_IfcSensor_type,
    IFC4X3_RC4_IfcSensorType_type,
    IFC4X3_RC4_IfcSensorTypeEnum_type,
    IFC4X3_RC4_IfcSequenceEnum_type,
    IFC4X3_RC4_IfcSeventhOrderPolynomialSpiral_type,
    IFC4X3_RC4_IfcShadingDevice_type,
    IFC4X3_RC4_IfcShadingDeviceType_type,
    IFC4X3_RC4_IfcShadingDeviceTypeEnum_type,
    IFC4X3_RC4_IfcShapeAspect_type,
    IFC4X3_RC4_IfcShapeModel_type,
    IFC4X3_RC4_IfcShapeRepresentation_type,
    IFC4X3_RC4_IfcShearModulusMeasure_type,
    IFC4X3_RC4_IfcShell_type,
    IFC4X3_RC4_IfcShellBasedSurfaceModel_type,
    IFC4X3_RC4_IfcSign_type,
    IFC4X3_RC4_IfcSignal_type,
    IFC4X3_RC4_IfcSignalType_type,
    IFC4X3_RC4_IfcSignalTypeEnum_type,
    IFC4X3_RC4_IfcSignType_type,
    IFC4X3_RC4_IfcSignTypeEnum_type,
    IFC4X3_RC4_IfcSimpleProperty_type,
    IFC4X3_RC4_IfcSimplePropertyTemplate_type,
    IFC4X3_RC4_IfcSimplePropertyTemplateTypeEnum_type,
    IFC4X3_RC4_IfcSimpleValue_type,
    IFC4X3_RC4_IfcSine_type,
    IFC4X3_RC4_IfcSIPrefix_type,
    IFC4X3_RC4_IfcSite_type,
    IFC4X3_RC4_IfcSIUnit_type,
    IFC4X3_RC4_IfcSIUnitName_type,
    IFC4X3_RC4_IfcSizeSelect_type,
    IFC4X3_RC4_IfcSlab_type,
    IFC4X3_RC4_IfcSlabElementedCase_type,
    IFC4X3_RC4_IfcSlabStandardCase_type,
    IFC4X3_RC4_IfcSlabType_type,
    IFC4X3_RC4_IfcSlabTypeEnum_type,
    IFC4X3_RC4_IfcSlippageConnectionCondition_type,
    IFC4X3_RC4_IfcSolarDevice_type,
    IFC4X3_RC4_IfcSolarDeviceType_type,
    IFC4X3_RC4_IfcSolarDeviceTypeEnum_type,
    IFC4X3_RC4_IfcSolidAngleMeasure_type,
    IFC4X3_RC4_IfcSolidModel_type,
    IFC4X3_RC4_IfcSolidOrShell_type,
    IFC4X3_RC4_IfcSolidStratum_type,
    IFC4X3_RC4_IfcSoundPowerLevelMeasure_type,
    IFC4X3_RC4_IfcSoundPowerMeasure_type,
    IFC4X3_RC4_IfcSoundPressureLevelMeasure_type,
    IFC4X3_RC4_IfcSoundPressureMeasure_type,
    IFC4X3_RC4_IfcSpace_type,
    IFC4X3_RC4_IfcSpaceBoundarySelect_type,
    IFC4X3_RC4_IfcSpaceHeater_type,
    IFC4X3_RC4_IfcSpaceHeaterType_type,
    IFC4X3_RC4_IfcSpaceHeaterTypeEnum_type,
    IFC4X3_RC4_IfcSpaceType_type,
    IFC4X3_RC4_IfcSpaceTypeEnum_type,
    IFC4X3_RC4_IfcSpatialElement_type,
    IFC4X3_RC4_IfcSpatialElementType_type,
    IFC4X3_RC4_IfcSpatialReferenceSelect_type,
    IFC4X3_RC4_IfcSpatialStructureElement_type,
    IFC4X3_RC4_IfcSpatialStructureElementType_type,
    IFC4X3_RC4_IfcSpatialZone_type,
    IFC4X3_RC4_IfcSpatialZoneType_type,
    IFC4X3_RC4_IfcSpatialZoneTypeEnum_type,
    IFC4X3_RC4_IfcSpecificHeatCapacityMeasure_type,
    IFC4X3_RC4_IfcSpecularExponent_type,
    IFC4X3_RC4_IfcSpecularHighlightSelect_type,
    IFC4X3_RC4_IfcSpecularRoughness_type,
    IFC4X3_RC4_IfcSphere_type,
    IFC4X3_RC4_IfcSphericalSurface_type,
    IFC4X3_RC4_IfcSpiral_type,
    IFC4X3_RC4_IfcStackTerminal_type,
    IFC4X3_RC4_IfcStackTerminalType_type,
    IFC4X3_RC4_IfcStackTerminalTypeEnum_type,
    IFC4X3_RC4_IfcStair_type,
    IFC4X3_RC4_IfcStairFlight_type,
    IFC4X3_RC4_IfcStairFlightType_type,
    IFC4X3_RC4_IfcStairFlightTypeEnum_type,
    IFC4X3_RC4_IfcStairType_type,
    IFC4X3_RC4_IfcStairTypeEnum_type,
    IFC4X3_RC4_IfcStateEnum_type,
    IFC4X3_RC4_IfcStructuralAction_type,
    IFC4X3_RC4_IfcStructuralActivity_type,
    IFC4X3_RC4_IfcStructuralActivityAssignmentSelect_type,
    IFC4X3_RC4_IfcStructuralAnalysisModel_type,
    IFC4X3_RC4_IfcStructuralConnection_type,
    IFC4X3_RC4_IfcStructuralConnectionCondition_type,
    IFC4X3_RC4_IfcStructuralCurveAction_type,
    IFC4X3_RC4_IfcStructuralCurveActivityTypeEnum_type,
    IFC4X3_RC4_IfcStructuralCurveConnection_type,
    IFC4X3_RC4_IfcStructuralCurveMember_type,
    IFC4X3_RC4_IfcStructuralCurveMemberTypeEnum_type,
    IFC4X3_RC4_IfcStructuralCurveMemberVarying_type,
    IFC4X3_RC4_IfcStructuralCurveReaction_type,
    IFC4X3_RC4_IfcStructuralItem_type,
    IFC4X3_RC4_IfcStructuralLinearAction_type,
    IFC4X3_RC4_IfcStructuralLoad_type,
    IFC4X3_RC4_IfcStructuralLoadCase_type,
    IFC4X3_RC4_IfcStructuralLoadConfiguration_type,
    IFC4X3_RC4_IfcStructuralLoadGroup_type,
    IFC4X3_RC4_IfcStructuralLoadLinearForce_type,
    IFC4X3_RC4_IfcStructuralLoadOrResult_type,
    IFC4X3_RC4_IfcStructuralLoadPlanarForce_type,
    IFC4X3_RC4_IfcStructuralLoadSingleDisplacement_type,
    IFC4X3_RC4_IfcStructuralLoadSingleDisplacementDistortion_type,
    IFC4X3_RC4_IfcStructuralLoadSingleForce_type,
    IFC4X3_RC4_IfcStructuralLoadSingleForceWarping_type,
    IFC4X3_RC4_IfcStructuralLoadStatic_type,
    IFC4X3_RC4_IfcStructuralLoadTemperature_type,
    IFC4X3_RC4_IfcStructuralMember_type,
    IFC4X3_RC4_IfcStructuralPlanarAction_type,
    IFC4X3_RC4_IfcStructuralPointAction_type,
    IFC4X3_RC4_IfcStructuralPointConnection_type,
    IFC4X3_RC4_IfcStructuralPointReaction_type,
    IFC4X3_RC4_IfcStructuralReaction_type,
    IFC4X3_RC4_IfcStructuralResultGroup_type,
    IFC4X3_RC4_IfcStructuralSurfaceAction_type,
    IFC4X3_RC4_IfcStructuralSurfaceActivityTypeEnum_type,
    IFC4X3_RC4_IfcStructuralSurfaceConnection_type,
    IFC4X3_RC4_IfcStructuralSurfaceMember_type,
    IFC4X3_RC4_IfcStructuralSurfaceMemberTypeEnum_type,
    IFC4X3_RC4_IfcStructuralSurfaceMemberVarying_type,
    IFC4X3_RC4_IfcStructuralSurfaceReaction_type,
    IFC4X3_RC4_IfcStyledItem_type,
    IFC4X3_RC4_IfcStyledRepresentation_type,
    IFC4X3_RC4_IfcStyleModel_type,
    IFC4X3_RC4_IfcSubContractResource_type,
    IFC4X3_RC4_IfcSubContractResourceType_type,
    IFC4X3_RC4_IfcSubContractResourceTypeEnum_type,
    IFC4X3_RC4_IfcSubedge_type,
    IFC4X3_RC4_IfcSurface_type,
    IFC4X3_RC4_IfcSurfaceCurve_type,
    IFC4X3_RC4_IfcSurfaceCurveSweptAreaSolid_type,
    IFC4X3_RC4_IfcSurfaceFeature_type,
    IFC4X3_RC4_IfcSurfaceFeatureTypeEnum_type,
    IFC4X3_RC4_IfcSurfaceOfLinearExtrusion_type,
    IFC4X3_RC4_IfcSurfaceOfRevolution_type,
    IFC4X3_RC4_IfcSurfaceOrFaceSurface_type,
    IFC4X3_RC4_IfcSurfaceReinforcementArea_type,
    IFC4X3_RC4_IfcSurfaceSide_type,
    IFC4X3_RC4_IfcSurfaceStyle_type,
    IFC4X3_RC4_IfcSurfaceStyleElementSelect_type,
    IFC4X3_RC4_IfcSurfaceStyleLighting_type,
    IFC4X3_RC4_IfcSurfaceStyleRefraction_type,
    IFC4X3_RC4_IfcSurfaceStyleRendering_type,
    IFC4X3_RC4_IfcSurfaceStyleShading_type,
    IFC4X3_RC4_IfcSurfaceStyleWithTextures_type,
    IFC4X3_RC4_IfcSurfaceTexture_type,
    IFC4X3_RC4_IfcSweptAreaSolid_type,
    IFC4X3_RC4_IfcSweptDiskSolid_type,
    IFC4X3_RC4_IfcSweptDiskSolidPolygonal_type,
    IFC4X3_RC4_IfcSweptSurface_type,
    IFC4X3_RC4_IfcSwitchingDevice_type,
    IFC4X3_RC4_IfcSwitchingDeviceType_type,
    IFC4X3_RC4_IfcSwitchingDeviceTypeEnum_type,
    IFC4X3_RC4_IfcSystem_type,
    IFC4X3_RC4_IfcSystemFurnitureElement_type,
    IFC4X3_RC4_IfcSystemFurnitureElementType_type,
    IFC4X3_RC4_IfcSystemFurnitureElementTypeEnum_type,
    IFC4X3_RC4_IfcTable_type,
    IFC4X3_RC4_IfcTableColumn_type,
    IFC4X3_RC4_IfcTableRow_type,
    IFC4X3_RC4_IfcTank_type,
    IFC4X3_RC4_IfcTankType_type,
    IFC4X3_RC4_IfcTankTypeEnum_type,
    IFC4X3_RC4_IfcTask_type,
    IFC4X3_RC4_IfcTaskDurationEnum_type,
    IFC4X3_RC4_IfcTaskTime_type,
    IFC4X3_RC4_IfcTaskTimeRecurring_type,
    IFC4X3_RC4_IfcTaskType_type,
    IFC4X3_RC4_IfcTaskTypeEnum_type,
    IFC4X3_RC4_IfcTelecomAddress_type,
    IFC4X3_RC4_IfcTemperatureGradientMeasure_type,
    IFC4X3_RC4_IfcTemperatureRateOfChangeMeasure_type,
    IFC4X3_RC4_IfcTendon_type,
    IFC4X3_RC4_IfcTendonAnchor_type,
    IFC4X3_RC4_IfcTendonAnchorType_type,
    IFC4X3_RC4_IfcTendonAnchorTypeEnum_type,
    IFC4X3_RC4_IfcTendonConduit_type,
    IFC4X3_RC4_IfcTendonConduitType_type,
    IFC4X3_RC4_IfcTendonConduitTypeEnum_type,
    IFC4X3_RC4_IfcTendonType_type,
    IFC4X3_RC4_IfcTendonTypeEnum_type,
    IFC4X3_RC4_IfcTessellatedFaceSet_type,
    IFC4X3_RC4_IfcTessellatedItem_type,
    IFC4X3_RC4_IfcText_type,
    IFC4X3_RC4_IfcTextAlignment_type,
    IFC4X3_RC4_IfcTextDecoration_type,
    IFC4X3_RC4_IfcTextFontName_type,
    IFC4X3_RC4_IfcTextFontSelect_type,
    IFC4X3_RC4_IfcTextLiteral_type,
    IFC4X3_RC4_IfcTextLiteralWithExtent_type,
    IFC4X3_RC4_IfcTextPath_type,
    IFC4X3_RC4_IfcTextStyle_type,
    IFC4X3_RC4_IfcTextStyleFontModel_type,
    IFC4X3_RC4_IfcTextStyleForDefinedFont_type,
    IFC4X3_RC4_IfcTextStyleTextModel_type,
    IFC4X3_RC4_IfcTextTransformation_type,
    IFC4X3_RC4_IfcTextureCoordinate_type,
    IFC4X3_RC4_IfcTextureCoordinateGenerator_type,
    IFC4X3_RC4_IfcTextureMap_type,
    IFC4X3_RC4_IfcTextureVertex_type,
    IFC4X3_RC4_IfcTextureVertexList_type,
    IFC4X3_RC4_IfcThermalAdmittanceMeasure_type,
    IFC4X3_RC4_IfcThermalConductivityMeasure_type,
    IFC4X3_RC4_IfcThermalExpansionCoefficientMeasure_type,
    IFC4X3_RC4_IfcThermalResistanceMeasure_type,
    IFC4X3_RC4_IfcThermalTransmittanceMeasure_type,
    IFC4X3_RC4_IfcThermodynamicTemperatureMeasure_type,
    IFC4X3_RC4_IfcThirdOrderPolynomialSpiral_type,
    IFC4X3_RC4_IfcTime_type,
    IFC4X3_RC4_IfcTimeMeasure_type,
    IFC4X3_RC4_IfcTimeOrRatioSelect_type,
    IFC4X3_RC4_IfcTimePeriod_type,
    IFC4X3_RC4_IfcTimeSeries_type,
    IFC4X3_RC4_IfcTimeSeriesDataTypeEnum_type,
    IFC4X3_RC4_IfcTimeSeriesValue_type,
    IFC4X3_RC4_IfcTimeStamp_type,
    IFC4X3_RC4_IfcTopologicalRepresentationItem_type,
    IFC4X3_RC4_IfcTopologyRepresentation_type,
    IFC4X3_RC4_IfcToroidalSurface_type,
    IFC4X3_RC4_IfcTorqueMeasure_type,
    IFC4X3_RC4_IfcTrackElement_type,
    IFC4X3_RC4_IfcTrackElementType_type,
    IFC4X3_RC4_IfcTrackElementTypeEnum_type,
    IFC4X3_RC4_IfcTransformer_type,
    IFC4X3_RC4_IfcTransformerType_type,
    IFC4X3_RC4_IfcTransformerTypeEnum_type,
    IFC4X3_RC4_IfcTransitionCode_type,
    IFC4X3_RC4_IfcTranslationalStiffnessSelect_type,
    IFC4X3_RC4_IfcTransportElement_type,
    IFC4X3_RC4_IfcTransportElementFixedTypeEnum_type,
    IFC4X3_RC4_IfcTransportElementNonFixedTypeEnum_type,
    IFC4X3_RC4_IfcTransportElementType_type,
    IFC4X3_RC4_IfcTransportElementTypeSelect_type,
    IFC4X3_RC4_IfcTrapeziumProfileDef_type,
    IFC4X3_RC4_IfcTriangulatedFaceSet_type,
    IFC4X3_RC4_IfcTriangulatedIrregularNetwork_type,
    IFC4X3_RC4_IfcTrimmedCurve_type,
    IFC4X3_RC4_IfcTrimmingPreference_type,
    IFC4X3_RC4_IfcTrimmingSelect_type,
    IFC4X3_RC4_IfcTShapeProfileDef_type,
    IFC4X3_RC4_IfcTubeBundle_type,
    IFC4X3_RC4_IfcTubeBundleType_type,
    IFC4X3_RC4_IfcTubeBundleTypeEnum_type,
    IFC4X3_RC4_IfcTypeObject_type,
    IFC4X3_RC4_IfcTypeProcess_type,
    IFC4X3_RC4_IfcTypeProduct_type,
    IFC4X3_RC4_IfcTypeResource_type,
    IFC4X3_RC4_IfcUnit_type,
    IFC4X3_RC4_IfcUnitaryControlElement_type,
    IFC4X3_RC4_IfcUnitaryControlElementType_type,
    IFC4X3_RC4_IfcUnitaryControlElementTypeEnum_type,
    IFC4X3_RC4_IfcUnitaryEquipment_type,
    IFC4X3_RC4_IfcUnitaryEquipmentType_type,
    IFC4X3_RC4_IfcUnitaryEquipmentTypeEnum_type,
    IFC4X3_RC4_IfcUnitAssignment_type,
    IFC4X3_RC4_IfcUnitEnum_type,
    IFC4X3_RC4_IfcURIReference_type,
    IFC4X3_RC4_IfcUShapeProfileDef_type,
    IFC4X3_RC4_IfcValue_type,
    IFC4X3_RC4_IfcValve_type,
    IFC4X3_RC4_IfcValveType_type,
    IFC4X3_RC4_IfcValveTypeEnum_type,
    IFC4X3_RC4_IfcVaporPermeabilityMeasure_type,
    IFC4X3_RC4_IfcVector_type,
    IFC4X3_RC4_IfcVectorOrDirection_type,
    IFC4X3_RC4_IfcVertex_type,
    IFC4X3_RC4_IfcVertexLoop_type,
    IFC4X3_RC4_IfcVertexPoint_type,
    IFC4X3_RC4_IfcVibrationDamper_type,
    IFC4X3_RC4_IfcVibrationDamperType_type,
    IFC4X3_RC4_IfcVibrationDamperTypeEnum_type,
    IFC4X3_RC4_IfcVibrationIsolator_type,
    IFC4X3_RC4_IfcVibrationIsolatorType_type,
    IFC4X3_RC4_IfcVibrationIsolatorTypeEnum_type,
    IFC4X3_RC4_IfcVirtualElement_type,
    IFC4X3_RC4_IfcVirtualGridIntersection_type,
    IFC4X3_RC4_IfcVoidingFeature_type,
    IFC4X3_RC4_IfcVoidingFeatureTypeEnum_type,
    IFC4X3_RC4_IfcVoidStratum_type,
    IFC4X3_RC4_IfcVolumeMeasure_type,
    IFC4X3_RC4_IfcVolumetricFlowRateMeasure_type,
    IFC4X3_RC4_IfcWall_type,
    IFC4X3_RC4_IfcWallElementedCase_type,
    IFC4X3_RC4_IfcWallStandardCase_type,
    IFC4X3_RC4_IfcWallType_type,
    IFC4X3_RC4_IfcWallTypeEnum_type,
    IFC4X3_RC4_IfcWarpingConstantMeasure_type,
    IFC4X3_RC4_IfcWarpingMomentMeasure_type,
    IFC4X3_RC4_IfcWarpingStiffnessSelect_type,
    IFC4X3_RC4_IfcWasteTerminal_type,
    IFC4X3_RC4_IfcWasteTerminalType_type,
    IFC4X3_RC4_IfcWasteTerminalTypeEnum_type,
    IFC4X3_RC4_IfcWaterStratum_type,
    IFC4X3_RC4_IfcWindow_type,
    IFC4X3_RC4_IfcWindowLiningProperties_type,
    IFC4X3_RC4_IfcWindowPanelOperationEnum_type,
    IFC4X3_RC4_IfcWindowPanelPositionEnum_type,
    IFC4X3_RC4_IfcWindowPanelProperties_type,
    IFC4X3_RC4_IfcWindowStandardCase_type,
    IFC4X3_RC4_IfcWindowStyle_type,
    IFC4X3_RC4_IfcWindowStyleConstructionEnum_type,
    IFC4X3_RC4_IfcWindowStyleOperationEnum_type,
    IFC4X3_RC4_IfcWindowType_type,
    IFC4X3_RC4_IfcWindowTypeEnum_type,
    IFC4X3_RC4_IfcWindowTypePartitioningEnum_type,
    IFC4X3_RC4_IfcWorkCalendar_type,
    IFC4X3_RC4_IfcWorkCalendarTypeEnum_type,
    IFC4X3_RC4_IfcWorkControl_type,
    IFC4X3_RC4_IfcWorkPlan_type,
    IFC4X3_RC4_IfcWorkPlanTypeEnum_type,
    IFC4X3_RC4_IfcWorkSchedule_type,
    IFC4X3_RC4_IfcWorkScheduleTypeEnum_type,
    IFC4X3_RC4_IfcWorkTime_type,
    IFC4X3_RC4_IfcZone_type,
    IFC4X3_RC4_IfcZShapeProfileDef_type
        };
    return new schema_definition(strings[3905], declarations, new IFC4X3_RC4_instance_factory());
}


#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC pop_options
#elif defined(_MSC_VER)
#pragma optimize("", on)
#endif
        
static std::unique_ptr<schema_definition> schema;

void Ifc4x3_rc4::clear_schema() {
    schema.reset();
}

const schema_definition& Ifc4x3_rc4::get_schema() {
    if (!schema) {
        schema.reset(IFC4X3_RC4_populate_schema());
    }
    return *schema;
}

